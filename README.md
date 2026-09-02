# shutx skills

Claude Code 用のスキル・プラグイン置き場。このリポジトリはプラグインマーケットプレイスとして機能します。

## インストール

Claude Code 上で:

```
/plugin marketplace add shutx-net/skills
/plugin install phased-implementation@shutx-skills
```

## 収録プラグイン

### phased-implementation

実装タスクをフェーズ分割して段階的に進めるワークフロー。

1. **effort選択** — ユーザープロンプトにeffort指定（low / medium / high）がなければ、選択肢を提示して選ばせる
2. **計画立案** — `phase-planner` サブエージェントがコードベースを探索し、フェーズごとの計画JSON（`phase-01.json`, `phase-02.json`, ... と `plan-index.json`）を一時ディレクトリに書き出す。計画JSONはgitリポジトリには含めず、1ファイルを大きくしすぎない
3. **実装** — フェーズごとに `phase-implementer` サブエージェントを起動し、計画JSONを読み込ませて実装・検証させる

使い方の例:

```
/phased-implementation ユーザー認証にパスキー対応を追加して
```

またはスキルの説明に合致する依頼（「フェーズ分割で実装して」「計画を立ててから実装して」等）で自動的に発動します。

構成:

```
plugins/phased-implementation/
├── .claude-plugin/plugin.json
├── skills/phased-implementation/SKILL.md   # ワークフロー本体
└── agents/
    ├── phase-planner.md                    # 計画立案エージェント（読み取り + 計画JSON書き出しのみ）
    └── phase-implementer.md                # 実装エージェント（1フェーズ = 1エージェント）
```
