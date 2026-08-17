# TradeCanvas Compare Family — SSOT Design Registry

## Purpose

This registry documents the SSOT-driven modularization of the TradeCanvas `compare` and `compare2` pages.

## Four-Layer Pattern

```
base          ssot.ui.yml
family        ssot.ui.compare-family.yml
page          ssot.ui.compare.yml | ssot.ui.compare2.yml
feature       ssot.ui.feature.<name>.yml
```

## Family Members

| Page | HTML File | Layout | Notes |
|------|-----------|--------|-------|
| compare | compare.html | default | Stable full-layout compare page |
| compare2 | compare2.html | compact | Compact full-viewport compare page |

## Family Components

| Component | Definition Location | Page Overrides Allowed |
|-----------|--------------------|------------------------|
| chart_loader | family (`ssot.ui.compare-family.yml`) | yes (page `chart_loader.show_volume` etc.) |
| currency_selector | family | yes (`compare` uses `mode: full`, `compare2` inherits compact) |
| strategy_panel | family | yes |
| layout | family (via compact-layout feature) | `compare` inherits; `compare2` flags `page.layout: compact` |
| navigation | base (`ssot.ui.yml#navigation`) | active_page only |

## Feature Modules

| Feature File | Promoted To | Purpose |
|--------------|-------------|---------|
| `ssot.ui.feature.chart-controls.yml` | compare-family | Volume, interactive controls, trade markers |
| `ssot.ui.feature.currency-selector-compact.yml` | compare-family | Compact currency selector widget |
| `ssot.ui.feature.strategy-panel-hindsight.yml` | compare-family | Hindsight strategy defaults and UI flags |
| `ssot.ui.feature.compact-layout.yml` | compare-family | Full-viewport compact layout settings |

## Promotion Workflow

1. Create `ssot.ui.feature.<name>.yml` with `promote_to` and `preview_target`.
2. Add the feature to the preview page `features` list for testing.
3. Run `promote-feature.sh <domain> <feature-name>` to move it to the target.
4. Update `ssot.index.yml`.
5. Sync to `chaba/stacks/web/public` and verify with PlayLive.

## Component Inheritance

- `ssot.ui.yml` defines shared navigation and base panel configuration.
- `ssot.ui.compare-family.yml` defines shared chart loader, currency selector, and strategy panel defaults.
- `ssot.ui.compare.yml` and `ssot.ui.compare2.yml` add page-specific scripts, cache busting, and page metadata.
- Feature files inject focused, toggleable behavior into the family layer.
