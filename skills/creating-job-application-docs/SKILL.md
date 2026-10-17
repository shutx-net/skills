---
name: creating-job-application-docs
description: 就職・転職活動の応募書類（履歴書・職務経歴書・エントリーシート）を、印刷・PDF化を前提とした単一ファイルの HTML/CSS で作成する。「履歴書を作って」「職務経歴書を HTML で書いて」「ES を作成して」「就活書類を作りたい」等の依頼や、応募書類を HTML で用意したいときに使用する。
---

# creating-job-application-docs — Job Application Documents

履歴書・職務経歴書・エントリーシートを HTML/CSS で生成し、`output/` ディレクトリに保存する。

## 対応書類

| 書類 | 略称 | 記載項目 |
|------|------|---------|
| 履歴書 | rirekisho | `LOAD references/rirekisho-fields.md` |
| 職務経歴書 | shokumu-keirekisho | `LOAD references/shokumu-keirekisho-fields.md` |
| エントリーシート | entry-sheet | `LOAD references/entry-sheet-fields.md` |

## 必須ヒアリング項目

書類を生成する前に **必ず以下を確認** する。指示がない項目は推測せず、ユーザーに質問する。

1. **書類の種類** （履歴書 / 職務経歴書 / エントリーシート）
2. **用紙サイズ** （A4 / B5 / US Letter など）
3. **用紙の向き** （縦 / 横）
4. **デザインスタイル** （`japanese-formal` / `modern-simple`）
5. **記載内容** （氏名・学歴・職歴・志望動機など、書類に応じた必要項目）
   - 書類ごとの必要項目は、「対応書類」の表にある記載項目の「必須ヒアリング項目」にある

## デザインスタイル

| スタイル | 特徴 | テンプレートパス |
|---------|------|----------------|
| `japanese-formal` | 厚生労働省の様式例寄り・罫線あり・伝統的 | `templates/japanese-formal/` |
| `modern-simple` | 罫線少なめ・余白を活かしたモダン | `templates/modern-simple/` |

## 生成ルール

1. **HTML/CSS のみで構成する。** JavaScript は一切含めない（`<script>` タグを書かない）
2. **PDF 化を見据えた構成にする。** 印刷・PDF 化で崩れる、または意味を持たない CSS / HTML は使わない
3. **用紙サイズを CSS で明示する。** `@page` の `size` を必ず指定し、`.page` に用紙の実寸を mm で指定する
4. **CSS は `<style>` タグ内に同梱し、単一の HTML で完結させる。** 外部 CSS ファイルや CDN を参照しない
5. **PDF 変換処理は行わない。** HTML ファイルのみを生成し、`.pdf` 出力やライブラリ（puppeteer 等）は使わない

使わない CSS / HTML の一覧と、ページサイズ・改ページなどの書き方は `LOAD references/pdf-safe-css.md` にある。

## 出力先

プロジェクトルート直下の `output/` ディレクトリに保存する。

```
output/
├── rirekisho_YYYYMMDD.html
├── shokumu-keirekisho_YYYYMMDD.html
└── entry-sheet_YYYYMMDD.html
```

- `output/` が存在しなければ作成する
- ファイル名は `<略称>_<YYYYMMDD>.html` 形式にする
- 同名ファイルがあれば `_2`, `_3` を付ける

## ワークフロー

1. ユーザーから書類作成の依頼を受ける
2. **必須ヒアリング項目** をすべて確認する
3. 該当する `templates/<スタイル>/<略称>.html` をテンプレートとして読み込む
4. 該当する書類の記載項目（「対応書類」の表）を確認する
5. ユーザーの入力でテンプレートを埋めて HTML を生成する
6. `output/` ディレクトリに書き出す
7. ファイルパスを伝え、ブラウザで開いて確認でき、印刷機能で PDF として保存できることを案内する

## テンプレート利用の注意

`templates/` 配下の HTML は **A4 縦** をデフォルトとしたサンプルである。
ユーザーが他のサイズ・向きを指定した場合は、`@page` の `size` と `.page` の `width` / `height`（または `min-height`）を必ず変更する。B5 の指定方法は pdf-safe-css.md の「1. ページサイズの指定」にある。
