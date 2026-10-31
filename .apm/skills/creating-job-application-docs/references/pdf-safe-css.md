# Print-safe CSS

Documents created by this skill are intended to be saved as PDF through the browser's print dialog. Follow these rules to preserve their layout when printed.

## Contents

1. Page size
2. Units
3. Page breaks
4. Disallowed CSS and HTML
5. Fonts
6. Colors
7. Images
8. Previewing the result
9. Checklist

## 1. Page size

Set the paper size explicitly with `@page`. Use `.page` padding for margins, rather than `@page margin`, as the templates do.

```css
@page {
  size: A4 portrait;         /* Alternatives: JIS-B5 portrait, letter portrait */
  margin: 0;
}

* {
  box-sizing: border-box;
}

html, body {
  margin: 0;
  padding: 0;
  background: #fff;
}

.page {
  width: 210mm;              /* A4 portrait width */
  min-height: 297mm;         /* A4 portrait height */
  padding: 15mm;             /* Page margins */
  margin: 0 auto;
  background: #fff;
  -webkit-box-decoration-break: clone;
  box-decoration-break: clone;  /* Repeat padding on every printed page; see section 3 */
}

/* Gray surrounds the paper only on screen; see section 6 */
@media screen {
  html, body { background: #ddd; }
  .page { margin-bottom: 5mm; }
}
```

- Do not combine `@page margin` with `.page padding`. This doubles the margins and makes `.page` wider than the printable area, causing the browser to shrink the content. In Chrome, using 15 mm for both on A4 reduces content to about 86% and produces margins of about 28 mm.
- For Japanese documents, B5 means JIS B5 (182 × 257 mm). CSS `size: B5` selects ISO B5 (176 × 250 mm), so use `size: JIS-B5`.
- Use landscape orientation only for a rirekisho spread, such as `A3 landscape` for two A4 sheets. See "Landscape spreads" in rirekisho-fields.md.

## 2. Units

| Purpose | Recommended | Do not use |
| --- | --- | --- |
| Paper dimensions and margins | `mm`, `cm`, `pt` | `vh`, `vw`, `vmin`, `vmax` |
| Font size | `pt`, `mm` | `vh`, `vw` |
| Line spacing and other spacing | `mm`, `em`, `pt` | `vh`, `vw` |

**Never use viewport units** such as `vh` or `vw`. Browsers interpret them inconsistently when printing.

## 3. Page breaks

When a `.page` element outgrows one sheet, the browser continues it on the next. With `box-decoration-break: clone`, each printed fragment receives the element's padding. Without it, later pages lose their top and bottom margins. Safari only partially supports this property, so later pages may still lose their margins.

- **Career histories and entry sheets:** use one `.page` element and let the browser handle pagination.
- **Rirekisho:** use two `.page` elements, one per sheet, and force a page break before the second. See the page capacity guidelines in rirekisho-fields.md.

```css
.page + .page {
  break-before: page;        /* Start each subsequent .page on a new sheet */
}

.no-break,
.company-block,
.question-block {
  break-inside: avoid;       /* Keep each block together */
}

tr {
  break-inside: avoid;       /* Keep table rows together */
}

.section-title {
  break-after: avoid;        /* Keep headings with the content that follows */
}
```

- Apply `break-inside: avoid` to blocks that can fit on one page, such as an employer block or a question. Applying it to an entire large section can push the whole section onto the next page and leave a large gap.
- Put table headings in `<thead>` so they repeat when a table spans multiple pages.

## 4. Disallowed CSS and HTML

### CSS

- `position: fixed` and `position: sticky`, which can shift when saved as PDF
- `transform`, which some renderers handle poorly
- `transition`, `animation`, and `@keyframes`, which have no useful role in a PDF
- Visual changes triggered by `:hover`, `:focus`, or `:active`
- Heavy use of `box-shadow`, which can print with different colors
- `filter`, including blur
- `backdrop-filter`
- Dark mode through `prefers-color-scheme`
- Heavy use of gradients, which can lose tonal detail when printed

### HTML

- `<script>` tags
- Interactive controls: `<form>`, `<input>`, `<button>`, `<select>`, and `<textarea>`
- `<video>`, `<audio>`, `<canvas>`, and `<iframe>`
- Clickable `<a href="...">` links; display their text instead
- Collapsible `<details>` and `<summary>` elements
- External stylesheets such as `<link rel="stylesheet" href="...">`
- External JavaScript
- Fonts or icons loaded from a CDN, which fail offline

## 5. Fonts

Use system fonts instead of web fonts.

```css
body {
  font-family:
    "Hiragino Kaku Gothic ProN",
    "Hiragino Sans",
    Meiryo,
    "Yu Gothic",
    "Noto Sans CJK JP",
    sans-serif;
  font-size: 10.5pt;
  line-height: 1.6;
  color: #000;
}
```

For a Mincho-style serif font:

```css
font-family:
  "Hiragino Mincho ProN",
  "Yu Mincho",
  "MS Mincho",
  "Noto Serif CJK JP",
  serif;
```

## 6. Colors

- Use black or near-black text, such as `#000` or `#222`.
- Choose accent colors that remain legible in print.
- Keep light gray backgrounds around `#f5f5f5`.
- Use `print-color-adjust: exact;` when needed to preserve background colors.
- Put the gray background surrounding the on-screen paper inside `@media screen`. Because the templates use `print-color-adjust: exact`, a background outside that rule can also print in unused areas, such as the end of the last page.

```css
* {
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}
```

## 7. Images

- Embed images as base64 data or use a local relative path in the same directory as the document.
- Specify `<img>` width and height in `mm` to avoid shifts in print.

## 8. Previewing the result

Ask the user to:

1. Open the generated HTML in a browser.
2. Choose Print, then Save as PDF.
3. Check margins, page breaks, and fonts.

## 9. Checklist

After generating a document, verify that:

- [ ] `@page size` is set.
- [ ] `@page margin` and `.page padding` are not combined.
- [ ] `.page` has `box-decoration-break: clone`.
- [ ] Screen-only backgrounds and spacing are inside `@media screen`.
- [ ] `.page` uses the paper's actual dimensions in mm.
- [ ] There are no `<script>` tags.
- [ ] There are no interactive elements such as forms, buttons, or inputs.
- [ ] There are no external resources such as CDNs or stylesheets.
- [ ] No viewport units are used.
- [ ] Neither `position: fixed` nor `position: sticky` is used.
- [ ] There are no animation properties.
- [ ] Fonts come from the system font stack.
- [ ] All CSS is included in a `<style>` element.
