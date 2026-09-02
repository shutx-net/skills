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
2. **計画立案** — `phase-planner` サブエージェントがコードベースを探索し、フェーズごとの計画JSON（`phase-01.json`, `phase-02.json`, ... と `plan-index.json`）を一時ディレクトリに書き出す。計画JSONはgitリポジトリには含めず、1ファイルを大きくしすぎない
3. **実装** — フェーズごとに `phase-implementer` サブエージェントを起動し、計画JSONを読み込ませて実装・検証させる

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
plugins/impl/
├── .claude-plugin/plugin.json
└── agents/                       # 同期対象外（プラグイン固有）
    ├── phase-planner.md          #   計画立案エージェント（読み取り + 計画JSON書き出しのみ）
    └── phase-implementer.md      #   実装エージェント（1フェーズ = 1エージェント）
scripts/
├── sync_skills.py                # SSoT → 生成先の同期 / --check で乖離検出
└── lint_skills.py                # マニフェスト・スキル規約の検証
```

SKILL.mdは**自己完結**で、どちらのチャネル経由でも同一内容です。同梱エージェント（`phase-planner` / `phase-implementer`）は「あれば使う」任意の最適化として扱われ、無い環境ではサブエージェントの代替、それも無ければ自力実行にフォールバックします。

### スキルを編集するとき

1. `skills/impl/` を編集する（生成先を直接編集しない）
2. 同期する:

```bash
python3 scripts/sync_skills.py
```

3. 生成物も含めてコミットする（配布時に取得されるのは生成先のファイルのため、リポジトリにコミットが必要です）

CIは `python3 scripts/sync_skills.py --check` を実行し、生成先がSSoTと乖離していればビルドを落とします。
