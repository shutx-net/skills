# PDF 化を見据えた安全な CSS ガイドライン

このスキルで生成する HTML は、最終的にブラウザの印刷機能等で PDF へ変換される前提である。
以下のルールに従い、PDF 出力時に崩れない CSS を書く。

## 目次

1. ページサイズの指定
2. 単位の指針
3. 改ページ制御
4. 禁止する CSS / HTML
5. フォント指針
6. 色の指針
7. 画像
8. テスト方法（ユーザー向け案内）
9. チェックリスト

## 1. ページサイズの指定

`@page` ルールでページサイズを明示し、余白は `@page` の `margin` ではなく `.page` の `padding` で取る（テンプレートと同じ方式）。`.page` が用紙1枚に当たる。

```css
@page {
  size: A4 portrait;         /* または: A4 landscape, JIS-B5 portrait, letter portrait */
  margin: 0;
}

* {
  box-sizing: border-box;
}

html, body {
  margin: 0;
  padding: 0;
}

.page {
  width: 210mm;              /* A4 縦の幅 */
  min-height: 297mm;         /* A4 縦の高さ（1枚に収める書類は height） */
  padding: 15mm;             /* 余白 */
  margin: 0 auto;
  background: #fff;
}
```

- `@page` の `margin` と `.page` の `padding` を併用しない。余白が二重になるうえ、`.page` が印刷できる範囲より広くなるため、ブラウザが内容を縮小して印刷する（Chrome で A4・両方 15mm の場合、約86%に縮小され、余白は約28mmになる）
- 日本の書類で B5 といえば JIS B5（182 × 257mm）を指す。CSS の `size: B5` は ISO B5（176 × 250mm）になるため、`size: JIS-B5` を使う

## 2. 単位の指針

| 用途 | 推奨単位 | 禁止単位 |
|------|---------|---------|
| ページ寸法・余白 | `mm` `cm` `pt` | `vh` `vw` `vmin` `vmax` |
| フォントサイズ | `pt` `mm` | `vh` `vw` |
| 行間・余白 | `mm` `em` `pt` | `vh` `vw` |

ビューポート単位（`vh` `vw` 等）は印刷時にブラウザによって解釈が異なるため、**絶対に使用しない** こと。

## 3. 改ページ制御

`.page` は用紙1枚に当たる。1枚に収まらない書類は `.page` を枚数分並べ、下の `break-after` で改ページする。1つの `.page` から次の用紙へ内容があふれると、2枚目以降は上下の余白がなくなる。

```css
.page {
  page-break-after: always;  /* 旧仕様 */
  break-after: page;         /* 新仕様 */
}

.no-break {
  page-break-inside: avoid;
  break-inside: avoid;
}

h2, h3 {
  page-break-after: avoid;
  break-after: avoid;
}
```

## 4. 禁止する CSS / HTML

### CSS
- `position: fixed`、`position: sticky`（PDF で位置がずれる）
- `transform`（一部レンダラで崩れる）
- `transition` / `animation` / `@keyframes`（PDF では無意味）
- `:hover` / `:focus` / `:active` の視覚変化
- `box-shadow` の多用（印刷時に色が変わる場合あり）
- `filter`（blur 等）
- `backdrop-filter`
- ダークモード対応の `prefers-color-scheme`
- グラデーションの多用（印刷時に階調が崩れやすい）

### HTML
- `<script>` タグ
- `<form>` `<input>` `<button>` `<select>` `<textarea>`（インタラクティブ要素）
- `<video>` `<audio>` `<canvas>` `<iframe>`
- `<a href="...">`（クリック前提のリンク。テキスト表示のみにする）
- `<details>` `<summary>`（折りたたみ要素）
- 外部 CSS 読み込み（`<link rel="stylesheet" href="...">`）
- 外部 JS 読み込み
- CDN 経由のフォント・アイコン（オフライン環境で崩れる）

## 5. フォント指針

Web フォントの参照は避け、システムフォントを使う。

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

明朝体を使う場合：

```css
font-family:
  "Hiragino Mincho ProN",
  "Yu Mincho",
  "MS Mincho",
  "Noto Serif CJK JP",
  serif;
```

## 6. 色の指針

- 黒文字基調（`#000` または `#222`）
- 装飾色は印刷でも視認できる濃度を選ぶ
- 背景に薄いグレーを使う場合は `#f5f5f5` 程度に留める
- `print-color-adjust: exact;`（必要時のみ・色付き背景を確実に出すため）

```css
* {
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}
```

## 7. 画像

- 画像を使う場合は base64 埋め込み、もしくはファイルと同階層のローカル相対パス
- `<img>` の幅・高さを `mm` で指定すると印刷ズレを防げる

## 8. テスト方法（ユーザー向け案内）

1. 出力された HTML をブラウザで開く
2. ブラウザの「印刷」→「PDFとして保存」で確認
3. 余白・改ページ・フォントを確認

## 9. チェックリスト

書類を生成したら、以下を満たしているか確認する。

- [ ] `@page size` を指定している
- [ ] `@page` の `margin` と `.page` の `padding` を併用していない
- [ ] `.page` に mm で用紙の実寸を指定している
- [ ] `<script>` タグがない
- [ ] インタラクティブ要素（form/button/input 等）がない
- [ ] 外部リソース参照（CDN/外部CSS）がない
- [ ] viewport 単位を使っていない
- [ ] `position: fixed` `sticky` を使っていない
- [ ] アニメーション関連プロパティがない
- [ ] フォントはシステムフォント指定
- [ ] CSS は `<style>` 内に同梱
