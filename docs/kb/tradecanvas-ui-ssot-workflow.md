# TradeCanvas UI SSOT Workflow

## Files and Naming Convention

All TradeCanvas UI SSOT files live in `config/ssot/` and use the prefix `ssot.ui`.

| Layer | File Pattern | Purpose |
|---|---|---|
| Base | `ssot.ui.yml` | Global defaults shared by every UI page. |
| Family | `ssot.ui.<family>-family.yml` | Shared configuration for a page family, e.g. `ssot.ui.compare-family.yml` for the compare family. |
| Page | `ssot.ui.<page>.yml` | Per-page overrides, e.g. `ssot.ui.compare.yml` for the stable page and `ssot.ui.compare2.yml` for the preview page. |
| Feature | `ssot.ui.feature.<name>.yml` | Optional, focused feature SSOTs. |

## Merge Order

The loader in `tradecanvas-ui/strategy-compare-new.js` deep-merges the layers in this order, with each later layer overriding the previous:

1. **Base** (`ssot.ui.yml`)
2. **Family** (`ssot.ui.compare-family.yml`)
3. **Page** (`ssot.ui.<page>.yml`)
4. **Feature** (`ssot.ui.feature.<name>.yml`)

`ref` markers are stripped during the merge.

## Feature Development and Promotion Workflow

1. Create a new feature SSOT at `config/ssot/ssot.ui.feature.<name>.yml`.
2. Enable or reference the feature on the preview page by updating `config/ssot/ssot.ui.compare2.yml`.
3. Preview the feature by loading `compare2`.
4. Validate the feature. If `scripts/validate-ui-ssot.sh` exists, run it before promoting.
5. When the feature is ready, promote the configuration into the appropriate layer:
   - General shared behavior for the compare family → `config/ssot/ssot.ui.compare-family.yml`
   - Stable compare page behavior → `config/ssot/ssot.ui.compare.yml`
6. Sync the updated files to the production directory by running `./sync-tradecanvas-ui.sh` from the project root.

### Page Roles

- `compare` is the stable page. Only fully validated, promoted features should affect it.
- `compare2` is the experimental/preview page. New feature SSOTs are added here first.
