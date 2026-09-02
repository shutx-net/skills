# shutx skills

Claude Code 用のスキル・プラグイン置き場。このリポジトリは以下の2通りの方法で配布されます:

1. **Claude Code プラグインマーケットプレイス** — サブエージェント同梱のフル機能版
2. **[APM (Agent Package Manager)](https://microsoft.github.io/apm/) パッケージ** — Copilot / Cursor / Codex 等でも使えるハーネス非依存版

## インストール

### Claude Code（プラグイン）

Claude Code 上で:

```
/plugin marketplace add shutx-net/skills
/plugin install impl@shutx-skills
```

### APM

プロジェクトの `apm.yml` に依存として追加:

```yaml
dependencies:
  apm:
    - shutx-net/skills
```

その後:

```
apm install
```

Claude Code では `.claude/skills/` に、Copilot / Cursor / OpenCode / Codex / Gemini では `.agents/skills/` にスキルが配備されます。

## 収録プラグイン

### impl

実装タスクをフェーズ分割して段階的に進めるワークフロー。

1. **effort選択** — ユーザープロンプトにeffort指定（low / medium / high）がなければ、選択肢を提示して選ばせる
2. **計画立案** — 読み取り中心のサブエージェントがコードベースを探索し、フェーズごとの計画JSON（`phase-01.json`, `phase-02.json`, ... と `plan-index.json`）を一時ディレクトリに書き出す。計画JSONはgitリポジトリには含めず、1ファイルを大きくしすぎない
3. **実装** — フェーズごとにサブエージェントを起動し、計画JSONのパスを渡して読み込ませ、実装・検証させる

サブエージェント機構が無い環境では、同じ手順をそのまま自分で順に実行します（スキルは自己完結しており、専用エージェントの同梱を前提としません）。

使い方の例:

```
/impl ユーザー認証にパスキー対応を追加して
```

またはスキルの説明に合致する依頼（「フェーズ分割で実装して」「計画を立ててから実装して」等）で自動的に発動します。

## リポジトリ構成とスキル定義の同期

スキル定義の**唯一の正（SSoT）は `skills/`** です。各配布チャネル向けのディレクトリは、そこから同期スクリプトで生成されます。

```
skills/impl/                      # ★ SSoT — 編集するのはここだけ
├── SKILL.md                      #   ワークフロー本体（自己完結）
└── references/plan-schema.md     #   計画JSONスキーマ

.apm/skills/impl/                 # 生成物: APMパッケージ用
plugins/impl/skills/impl/         # 生成物: Claude Codeプラグイン用

apm.yml                           # APMパッケージマニフェスト
.claude-plugin/marketplace.json   # Claude Code マーケットプレイス定義
plugins/impl/.claude-plugin/plugin.json
scripts/
├── sync-skills.sh                # SSoT → 生成先の同期 / --check で乖離検出
└── lint-skills.sh                # マニフェスト・スキル規約の検証
```

SKILL.mdは**自己完結**で、どちらのチャネル経由でも完全に同一の内容です。専用サブエージェントは同梱せず、実行環境にあるサブエージェント機構（あれば）を使い、無ければ自力実行にフォールバックします。これによりチャネル間で挙動が分岐しません。

### スキルを編集するとき

1. `skills/impl/` を編集する（生成先を直接編集しない）
2. 同期する:

```bash
./scripts/sync-skills.sh
```

3. 生成物も含めてコミットする（配布時に取得されるのは生成先のファイルのため、リポジトリにコミットが必要です）

CIは `./scripts/sync-skills.sh --check` を実行し、生成先がSSoTと乖離していればビルドを落とします。

スクリプトはPOSIX shと標準的なコマンド（cp / diff / grep / sed / awk / wc）だけで動くため、追加のランタイムやパッケージのインストールは不要です。ローカル検証も同じコマンドで実行できます:

```bash
./scripts/lint-skills.sh          # マニフェスト・スキル規約の検証
./scripts/sync-skills.sh --check  # 生成先の乖離チェック
```
