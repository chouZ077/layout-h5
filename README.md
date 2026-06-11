# layout-h5

`layout-h5` is a single-case interactive H5 card renderer. It turns one structured case JSON into a dark 16:9 web experience with three switchable panes:

- before: pain points and broken links before the change
- after: the rebuilt value chain or operating loop
- evidence: proof chain, screenshots, videos, metrics, or a custom raw pane

The renderer is intentionally simple: `template.html` owns the visual shell and runtime, while each case lives in a JSON file.

## What Is Inside

```text
layout-h5/
  build.py                      injects JSON into template.html
  validate.py                   checks schema, copy budget, assets, and raw panes
  template.html                 standalone renderer and interaction shell
  schema/case-card.schema.json  JSON contract
  examples/                     anonymized reference cases
```

## Quick Start

Build one example:

```bash
cd layout-h5
python build.py examples/raw-pane-demo.json out/index.html
```

Open `out/index.html` in a browser.

Validate before building:

```bash
python validate.py examples/raw-pane-demo.json --assets out
```

If the case references images or videos, put those assets next to the output HTML using the same relative paths written in the JSON:

```text
out/
  index.html
  assets/source/demo-01.png
  assets/videos/demo.mp4
```

For structure-only validation:

```bash
python validate.py examples/gac-toyota.json --skip-assets
```

## JSON Model

Every case has:

```json
{
  "header": {
    "title": "Case point of view",
    "sub": "Short context"
  },
  "panes": {
    "before": {},
    "after": {},
    "evidence": {}
  }
}
```

Supported built-in layouts:

- `before`: `swimlane`, `column-network`
- `after`: `hub-3col`, `journey`
- `evidence`: `evidence`
- any pane: `raw`

Use built-in layouts when the case fits the pattern. Use `raw` when the page needs its own visual metaphor, such as an organization tree, logistics network, dashboard, or custom proof map.

## Raw Panes

A raw pane lets one pane define its own HTML and CSS while still using the layout-h5 shell.

```json
{
  "layout": "raw",
  "label": "案例实证",
  "html": "<div class='demo-proof'>...</div>",
  "css": ".demo-proof{height:100%;display:grid;}",
  "js": "/* optional; receives pane and CaseCard */"
}
```

Notes:

- Do not put `<script>` tags inside `html`; use the `js` field.
- Prefer CSS variables from the shell when possible.
- Keep asset paths relative to the output HTML.

## Integrating Into feishu-deck-h5

The stable way to combine `layout-h5` with `feishu-deck-h5` is a full-screen iframe.

Why iframe:

- layout-h5 has its own CSS, JavaScript, scaling, hash navigation, and lightbox.
- feishu-deck-h5 also has its own slide shell, scaling, keyboard navigation, and hash routing.
- iframe keeps those two runtimes isolated, so styles and scripts do not collide.

### Recommended Directory Shape

Put the generated layout-h5 case beside the deck output:

```text
deck-output/
  index.html                 feishu-deck-h5 deck
  cases/customer-a/index.html layout-h5 case
  cases/customer-a/assets/...
```

Then iframe it from a full-screen deck slide.

### Full-Screen iframe Slide

In a `feishu-deck-h5` raw slide, use a full-canvas iframe:

```json
{
  "key": "customer-case",
  "layout": "raw",
  "data": {
    "html": "<style>.slide[data-slide-key='customer-case']{position:absolute;inset:0;overflow:hidden;background:#030611}.slide[data-slide-key='customer-case'] .wordmark,.slide[data-slide-key='customer-case'] .header{display:none}.slide[data-slide-key='customer-case'] iframe{position:absolute;inset:0;width:100%;height:100%;border:0;display:block;background:#030611}</style><iframe src='cases/customer-a/index.html' title='客户案例 H5' loading='lazy'></iframe>"
  }
}
```

This preserves the complete layout-h5 interaction: `before / after / evidence` switching, animations, zoom behavior, and lightbox.

### Framed iframe Alternative

`feishu-deck-h5` also has an `iframe-embed` layout for framed embeds with a deck title bar. Use it for demos or reports that should sit inside a deck frame.

For layout-h5 cases, full-screen iframe is usually better because layout-h5 already has its own 16:9 shell and navigation.

## Caveats

- Keyboard focus can stay inside the iframe after clicking the embedded case. If deck-level arrow navigation stops responding, click outside the iframe or add a small postMessage bridge.
- URL hashes are independent. The outer deck can use `#3`, while the layout-h5 iframe can use `#before`, `#after`, or `#evidence` internally.
- Direct DOM splicing is not recommended. It can cause CSS, JavaScript, scaling, and hash-routing conflicts.

## Publishing Checklist

Before sharing a built case:

```bash
python validate.py <case>.json --assets <output-dir>
python build.py <case>.json <output-dir>/index.html
```

For a deck integration, validate the deck after adding the iframe page as well.
