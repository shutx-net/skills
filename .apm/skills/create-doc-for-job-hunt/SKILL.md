---
name: create-doc-for-job-hunt
description: |
  就職活動用書類（履歴書・職務経歴書・エントリーシート）を HTML/CSS で作成します。
  「履歴書を作って」「職務経歴書を HTML で書いて」「エントリーシートを作成して」
  「就活書類を作りたい」と言われた時に使用してください。
  作成された HTML はそのまま Live Server で確認でき、後で印刷/PDF 化することを想定しています。
when_to_use: |
  以下の場合に呼び出してください：
  - 履歴書（rirekisho）の作成依頼
  - 職務経歴書（shokumu keirekisho）の作成依頼
  - エントリーシート（entry sheet）の作成依頼
  - 就職活動・転職活動の書類を HTML で生成したい時
---

# 就活書類作成スキル

履歴書・職務経歴書・エントリーシートを HTML/CSS で生成し、`output/` ディレクトリに保存します。

## 対応書類

| 書類 | 略称 | テンプレート参照 |
|------|------|---------------|
| 履歴書 | rirekisho | [references/rirekisho-fields.md](references/rirekisho-fields.md) |
| 職務経歴書 | shokumu-keirekisho | [references/shokumu-keirekisho-fields.md](references/shokumu-keirekisho-fields.md) |
| エントリーシート | entry-sheet | [references/entry-sheet-fields.md](references/entry-sheet-fields.md) |

## 必須ヒアリング項目

書類生成前に **必ず以下を確認** してください。指示がない場合は質問します。

1. **書類の種類** （履歴書 / 職務経歴書 / エントリーシート）
2. **用紙サイズ** （A4 / B5 / US Letter など）
3. **用紙の向き** （縦 / 横）
4. **デザインスタイル** （`japanese-formal` / `modern-simple`）
5. **記載内容** （氏名・学歴・職歴・志望動機など、書類に応じた必要項目）
   - 各書類の必要項目は `references/*-fields.md` を参照

不明な項目は推測せず、ユーザーに質問してください。

## デザインスタイル

| スタイル | 特徴 | テンプレートパス |
|---------|------|----------------|
| `japanese-formal` | JIS規格寄り・罫線あり・伝統的 | `templates/japanese-formal/` |
| `modern-simple` | 罫線少なめ・余白を活かしたモダン | `templates/modern-simple/` |

## 生成ルール

### 必須遵守事項

1. **HTML/CSS のみで構成する**
   - JavaScript は一切含めない
   - `<script>` タグを書かない

2. **PDF 化を見据えた構成にする**
   - インタラクティブ要素禁止（`<form>`, `<input>`, `<button>`, `<a href="javascript:">` など）
   - `:hover` `:focus` 等の対話的な視覚変化を使わない
   - `position: fixed` / `sticky` を使わない
   - アニメーション・トランジション禁止
   - viewport 単位（`vh`/`vw`）禁止
   - 詳細は [references/pdf-safe-css.md](references/pdf-safe-css.md) を参照

3. **用紙サイズを CSS で明示する**
   - `@page { size: ... }` を必ず指定
   - body/コンテナに mm 単位で実寸を指定（例: A4 縦なら `width: 210mm; height: 297mm;`）
   - `box-sizing: border-box` で余白計算を統一

4. **CSS は 1 ファイルに同梱（`<style>` タグ内）**
   - 単一 HTML で完結させ、Live Server で開けば即確認可能にする
   - 外部 CSS ファイルや CDN を参照しない

5. **PDF 変換処理は行わない**
   - HTML ファイルのみを生成し、`.pdf` 出力やライブラリ（puppeteer 等）は使わない

## 出力先

プロジェクトルート直下の `output/` ディレクトリに保存します。

```
output/
├── rirekisho_YYYYMMDD.html
├── shokumu-keirekisho_YYYYMMDD.html
└── entry-sheet_YYYYMMDD.html
```

- `output/` が存在しない場合は作成
- ファイル名は `<書類略称>_<YYYYMMDD>.html` 形式
- 同名ファイルがある場合は `_2`, `_3` を付与

## 用紙サイズ早見表

| 規格 | 縦向き (mm) | 横向き (mm) |
|------|-----------|-----------|
| A4 | 210 × 297 | 297 × 210 |
| B5 | 182 × 257 | 257 × 182 |
| A3 | 297 × 420 | 420 × 297 |
| US Letter | 215.9 × 279.4 | 279.4 × 215.9 |

## ワークフロー

1. ユーザーから書類作成の依頼を受ける
2. **必須ヒアリング項目** をすべて確認（不明分は質問）
3. 該当する `templates/<style>/<doc>.html` をテンプレートとして読み込む
4. 該当する `references/<doc>-fields.md` でフィールド構成を確認
5. ユーザー入力でテンプレートを埋めて HTML を生成
6. `output/` ディレクトリに書き出し
7. ファイルパスをユーザーに伝え、Live Server で確認するよう案内

## テンプレート利用の注意

`templates/` 配下の HTML は **A4 縦** をデフォルトとしたサンプルです。
ユーザーが他のサイズ・向きを指定した場合は、`@page size` と body の `width`/`height` を必ず変更してください。
