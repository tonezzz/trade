#!/usr/bin/env python3
"""run-preset-against-dell.py

Run a PlayLive preset YAML against the playlived daemon on tony-dell.
This script is meant to execute on tony-dell so all browser/network load
(browser, Chrome, page parsing) happens there; tony-omen only needs to
send one SSH command and receive JSON.
"""
import argparse
import json
import re
import sys
import time
import urllib.request
import urllib.error

import yaml


def http_request(url, method="GET", payload=None, timeout=60):
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Content-Type": "application/json"} if data else {}
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            err = json.loads(body)
        except json.JSONDecodeError:
            err = {"error": body}
        return {"ok": False, "http_code": exc.code, **err}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def normalize(value):
    """Return a stable string representation for comparison."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


PARAM_RE = re.compile(r"\$\{(\w+)\}")


def build_params(preset, cli_overrides):
    """Collect params from preset defaults and CLI --param KEY=VALUE."""
    params = {}
    for p in preset.get("params", []):
        params[p["name"]] = p.get("default", "")
    for override in cli_overrides:
        if "=" in override:
            k, v = override.split("=", 1)
            params[k] = v
    return params


def render_step(step, params):
    """Substitute ${param} in step string fields; leave script/expected untouched."""
    rendered = {}
    for k, v in step.items():
        if k in ("script", "expected") or not isinstance(v, str):
            rendered[k] = v
        else:
            rendered[k] = PARAM_RE.sub(lambda m: str(params.get(m.group(1), "")), v)
    return rendered


def main():
    parser = argparse.ArgumentParser(
        description="Run a PlayLive preset on tony-dell"
    )
    parser.add_argument("--preset-file", required=True, help="Path to the preset YAML")
    parser.add_argument(
        "--playlive-url",
        default="http://localhost:9230",
        help="playlived URL (default: http://localhost:9230)",
    )
    parser.add_argument(
        "--cdp-url",
        default="http://127.0.0.1:9222",
        help="Chrome CDP URL (default: http://127.0.0.1:9222)",
    )
    parser.add_argument(
        "--output", "-o", default="-", help="Output file or - for stdout"
    )
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument(
        "--param",
        action="append",
        default=[],
        help="Override a preset param, e.g. --param symbol=MAJOR",
    )
    args = parser.parse_args()

    with open(args.preset_file, "r", encoding="utf-8") as f:
        preset = yaml.safe_load(f)

    params = build_params(preset, args.param)
    steps = [render_step(s, params) for s in preset.get("steps", [])]
    cleanup = [render_step(c, params) for c in preset.get("cleanup", [])]
    base = args.playlive_url.rstrip("/")
    session_id = None
    results = []

    # 1. Create a Chrome CDP session on tony-dell
    create_payload = {
        "type": "chrome-live",
        "target": "remote",
        "remote_url": args.cdp_url,
    }
    if args.verbose:
        print(f"POST {base}/sessions {create_payload}", file=sys.stderr)
    res = http_request(f"{base}/sessions", "POST", create_payload)
    if not res.get("ok") or "session_id" not in res:
        print(
            json.dumps({"ok": False, "stage": "create_session", "error": res}, indent=2),
            file=sys.stderr,
        )
        return 1
    session_id = res["session_id"]
    results.append({"step": "create_session", "ok": True, "session_id": session_id})

    failed = False
    try:
        for i, step in enumerate(steps):
            action = step["action"]
            sid = step.get("id", f"step-{i}")
            if args.verbose:
                print(f"[{sid}] {action}", file=sys.stderr)

            if action == "wait":
                duration = step.get("duration_ms", 1000)
                time.sleep(duration / 1000.0)
                results.append({"step_id": sid, "action": action, "ok": True})
                continue

            if action == "navigate":
                url = step["url"]
                r = http_request(
                    f"{base}/sessions/{session_id}/navigate", "POST", {"url": url}
                )
                results.append({"step_id": sid, "action": action, "ok": r.get("ok"), "result": r})
                if not r.get("ok"):
                    print(
                        json.dumps({"ok": False, "stage": sid, "error": r}, indent=2),
                        file=sys.stderr,
                    )
                    failed = True
                    return 1
                continue

            if action == "eval":
                script = step.get("script", "")
                r = http_request(
                    f"{base}/sessions/{session_id}/eval", "POST", {"script": script}
                )
                result = r.get("result") if r.get("ok") else r
                results.append(
                    {"step_id": sid, "action": action, "ok": r.get("ok"), "result": result}
                )
                if not r.get("ok"):
                    print(
                        json.dumps({"ok": False, "stage": sid, "error": r}, indent=2),
                        file=sys.stderr,
                    )
                    failed = True
                    return 1
                expected = step.get("expected")
                if expected is not None:
                    if normalize(result) != normalize(expected) and normalize(expected) not in normalize(result):
                        print(
                            json.dumps(
                                {
                                    "ok": False,
                                    "stage": sid,
                                    "error": f"expected {expected!r}, got {result!r}",
                                },
                                indent=2,
                            ),
                            file=sys.stderr,
                        )
                        failed = True
                        return 1
                continue

            # Generic: click, fill, select, screenshot, etc.
            payload = {
                k: v
                for k, v in step.items()
                if k not in ("id", "action", "description", "expected")
            }
            r = http_request(
                f"{base}/sessions/{session_id}/{action}", "POST", payload
            )
            results.append({"step_id": sid, "action": action, "ok": r.get("ok"), "result": r})
            if not r.get("ok"):
                print(
                    json.dumps({"ok": False, "stage": sid, "error": r}, indent=2),
                    file=sys.stderr,
                )
                failed = True
                return 1
    finally:
        # Always close the browser session on tony-dell
        for c in cleanup:
            caction = c.get("action", "close_session")
            if caction == "close_session":
                http_request(f"{base}/sessions/{session_id}", "DELETE")
            else:
                payload = {k: v for k, v in c.items() if k != "action"}
                http_request(f"{base}/sessions/{session_id}/{caction}", "POST", payload)

    output = {
        "ok": not failed,
        "preset": preset.get("title"),
        "session_id": session_id,
        "results": results,
    }
    out_str = json.dumps(output, indent=2, ensure_ascii=False)
    if args.output == "-":
        print(out_str)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out_str)
        print(f"Wrote {args.output}", file=sys.stderr)

    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
