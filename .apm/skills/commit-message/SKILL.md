---
name: commit-message
description: git commitのメッセージを Conventional Commits 形式で書き、変更の種類を feat / fix などの type プレフィックスで示す。コミットを作成するとき、コミットメッセージを書く・見直すときや、「コミットして」「コミットメッセージを考えて」等の依頼で使用する。
---

# commit-message — Conventional Commits

コミットメッセージは [Conventional Commits 1.0.0](https://www.conventionalcommits.org/ja/v1.0.0/) に従い、1行目の先頭に変更の種類を表す **type** をプレフィックスとして付ける。type には、Conventional Commits が推奨する [@commitlint/config-conventional](https://github.com/conventional-changelog/commitlint/tree/master/%40commitlint/config-conventional)（Angular の規約に由来）の一覧を使う。

リポジトリに独自の規約（commitlint の設定、`CONTRIBUTING.md` 等）がある場合は、そちらを優先する。

## 書式

```
<type>[(<scope>)][!]: <description>

[本文]

[フッター]
```

- 必須なのは1行目（ヘッダー）だけ。本文・フッターを書くときは、それぞれの前に空行を1行入れる
- ヘッダーは72文字以内を目安に短く書き、100文字（commitlint の上限）を超えない
- 本文・フッターの各行も100文字以内にする。英文は72文字前後で折り返す

## type

type は changelog の生成やバージョンの決定（`fix` → PATCH、`feat` → MINOR、破壊的変更 → MAJOR）にも使われる。変更の内容を正しく表すものを選ぶ。

| type | 使う場面 |
| --- | --- |
| `feat` | 新しい機能の追加 |
| `fix` | バグ修正 |
| `docs` | ドキュメントのみの変更 |
| `style` | コードの意味に影響しない変更（空白、フォーマット、セミコロンの欠落など） |
| `refactor` | バグ修正でも機能追加でもないコードの変更 |
| `perf` | パフォーマンスを改善するコードの変更 |
| `test` | テストの追加・既存のテストの修正 |
| `build` | ビルドシステムや外部依存（依存パッケージ等）に影響する変更 |
| `ci` | CI の設定ファイル・スクリプトの変更 |
| `chore` | ソースコードやテストを変更しない、上記以外の変更 |
| `revert` | 以前のコミットの取り消し |

type は小文字で書く。一覧にない type は作らない（commitlint の検査で拒否され、changelog の生成などのツールにも認識されないため）。

### type の選び方

ファイルの種類ではなく、**変更の目的**で決める。

- **振る舞いを変えない変更**: 目的が性能の改善なら `perf`、空白やフォーマットなどコードの書式だけなら `style`、それ以外のコードの整理は `refactor`。`style` はコードの書式のことで、CSS や UI の見た目の変更には使わない
- **`test`**: テストだけを変更するときに使う。機能追加やバグ修正に伴うテストは、本体の変更の type（`feat` / `fix`）に含める
- **`docs`**: 人が読むドキュメント（README、コードコメント等）だけの変更。Markdown でも、プロンプトやスキル定義、設定など動作を決めるファイルの変更は `docs` にしない
- **`build` / `ci` / `chore`**: ビルド設定や依存パッケージなら `build`、CI なら `ci`、どれにも当たらない雑務（`.gitignore` の更新など）が `chore`。`chore` は最後の受け皿であり、他の type に当たる変更を `chore` にしない
- **複数の type にまたがる**: 可能な限りコミットを分ける。分けない場合は、変更の主目的を表す type を選ぶ

## scope

- 変更の範囲（コンポーネント名、モジュール名など）を表す名詞を括弧で囲み、type の直後に付ける（例: `feat(parser):`）。省略してよい
- 既存のコミットで使われている scope があれば、それに合わせる。無ければ小文字の短い名詞にする
- 変更が広範囲に及ぶ場合や、範囲をうまく名付けられない場合は省略する

## description（説明文）

- 言語は既存のコミットに合わせる。判断できない場合は英語で書く
- 英語: 命令形・現在形で書き（`added` / `adds` ではなく `add`）、先頭は小文字、末尾にピリオドを付けない
- 日本語: 「〜を追加」「〜を修正」のように簡潔に書き、句点を付けない
- 先頭を `README` や `API` のような英大文字の語にしない（commitlint で文頭が大文字と判定され、拒否される）。日本語なら「README を更新」ではなく「インストール手順を README に追記」のように語順を変える
- 何を変えたのかが分かるように書く。`fix bug` や `update` のように中身の無い説明にしない

## 本文

- 変更の理由がヘッダーから自明でない限り書く
- なぜ変更が必要かを説明し、必要なら変更前後の振る舞いを比べる。どう実装したかはコードを見れば分かるので繰り返さない

## フッター

git のトレーラーの形式（`Token: value` または `Token #value`）で書く。トークン内の空白は `-` に置き換える（`BREAKING CHANGE` のみ例外）。

- 関連する Issue: `Refs: #123`、`Closes #123`
- 環境やユーザーの指示で付けるトレーラー（`Co-Authored-By` 等）もフッターに置く

## 破壊的変更

後方互換性を壊す変更は、type に関係なく次の両方で示す:

- ヘッダーの `:` の直前に `!` を付ける（例: `feat(api)!:`、`refactor!:`）
- フッターに `BREAKING CHANGE:`（大文字）を書き、影響と移行方法を説明する

## revert

`git revert` が生成する1行目 `Revert "<元のヘッダー>"` を `revert: <元のヘッダー>` に書き換える。本文の `This reverts commit <SHA>.` は残し、取り消す理由を書き足す。

## 手順

1. リポジトリ独自の規約を確認する（commitlint の設定 `commitlint.config.*` / `.commitlintrc*` / `package.json` の `commitlint`、`CONTRIBUTING.md` 等）。あればそちらに従う
2. 既存のコミット（`git log --oneline -n 20` 等）で、説明文の言語と scope の使い方を確認する
3. コミットする差分を読み、「type の選び方」に従って type を決める
4. 上記の書式でメッセージを書く

## 例

type ごとの1行目:

```
feat(auth): add password reset via email
fix(cart): keep item quantities after a page reload
docs: describe the release process in CONTRIBUTING.md
style: apply the formatter to the whole project
refactor(cart): extract price calculation into its own module
perf(search): cache compiled query patterns
test(cart): cover discounts applied twice
build(deps): bump express from 4.18.2 to 4.19.2
ci: run tests on Node.js 22
chore: ignore editor swap files
```

日本語で書くリポジトリの場合:

```
feat(auth): メールでのパスワード再設定に対応
fix: 設定ファイルが空のときに起動できない問題を修正
docs: インストール手順を README に追記
```

本文とフッター付き:

```
fix(parser): handle consecutive spaces in array input

Splitting on a single space produced empty elements when the input
contained consecutive spaces, and those elements failed validation
later. Split on runs of whitespace instead.

Closes #123
```

破壊的変更:

```
feat(config)!: read settings from config.toml instead of config.json

BREAKING CHANGE: config.json is no longer read. Convert it to TOML and
save it as config.toml.
```

取り消し:

```
revert: feat(auth): add password reset via email

This reverts commit 676104e.

Reset emails were sent without rate limiting.
```
