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

構成:

```
apm.yml                           # APMパッケージマニフェスト
.apm/skills/impl/                 # APM版スキル（ハーネス非依存・自己完結）
├── SKILL.md
└── references/plan-schema.md     # 計画JSONスキーマ
.claude-plugin/marketplace.json   # Claude Code マーケットプレイス定義
plugins/impl/                     # Claude Code プラグイン版
├── .claude-plugin/plugin.json
├── skills/impl/SKILL.md          # ワークフロー本体
└── agents/
    ├── phase-planner.md          # 計画立案エージェント（読み取り + 計画JSON書き出しのみ）
    └── phase-implementer.md      # 実装エージェント（1フェーズ = 1エージェント）
```

2つのSKILL.mdは同じワークフローです。プラグイン版は同梱のサブエージェント（`phase-planner` / `phase-implementer`）を使う前提で書かれており、APM版はサブエージェント機構の有無に応じて委譲/自力実行を切り替える自己完結版です。ワークフローを変更するときは両方を更新してください。
