# shutx skills

Claude Code 用のスキル・プラグイン置き場。このリポジトリは以下の2通りの方法で配布されます:

1. **Claude Code プラグインマーケットプレイス** — `/plugin` でインストールする形式
2. **[APM (Agent Package Manager)](https://microsoft.github.io/apm/) パッケージ** — Copilot / Cursor / Codex 等でも使える形式

## 収録スキル

| スキル | 概要 |
| --- | --- |
| [`impl`](skills/impl/SKILL.md) | 実装タスクをフェーズ分割し、フェーズごとの計画JSONを書き出してから段階的に実装する |

## インストール

### Claude Code（プラグイン）

Claude Code 上で:

```
/plugin marketplace add shutx-net/skills
/plugin install <スキル名>@shutx-skills
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

## リポジトリ構成とスキル定義の同期

スキル定義の**唯一の正（SSoT）は `skills/`** です。各配布チャネル向けのディレクトリは、そこから同期スクリプトで生成されます。

```
skills/<name>/                    # ★ SSoT — 編集するのはここだけ
├── SKILL.md                      #   スキル本体（自己完結）
└── references/                   #   本文からLOADする補助ドキュメント

.apm/skills/<name>/               # 生成物: APMパッケージ用
plugins/<name>/skills/<name>/     # 生成物: Claude Codeプラグイン用

apm.yml                           # APMパッケージマニフェスト
.claude-plugin/marketplace.json   # Claude Code マーケットプレイス定義
plugins/<name>/.claude-plugin/plugin.json
scripts/
├── sync-skills.sh                # SSoT → 生成先の同期 / --check で乖離検出
└── lint-skills.sh                # マニフェスト・スキル規約の検証
```

SKILL.mdは**自己完結**で、どちらのチャネル経由でも完全に同一の内容です。専用サブエージェントは同梱せず、実行環境にあるサブエージェント機構（あれば）を使い、無ければ自力実行にフォールバックします。これによりチャネル間で挙動が分岐しません。

### スキルを編集するとき

1. `skills/<name>/` を編集する（生成先を直接編集しない）
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

### 新しいスキルを追加する

`skills/<name>/SKILL.md` を作れば、同期スクリプトが自動で検出して各生成先に配ります（スクリプトの編集は不要です）。ただし配布するには、そのスキルのプラグインをマニフェストに登録する必要があります:

1. `skills/<name>/SKILL.md` を作成（`name` はディレクトリ名と一致させる）
2. `plugins/<name>/.claude-plugin/plugin.json` を作成（`name` / `version` / `description` / `author`。`author` は `--strict` 検証で必須）
3. `.claude-plugin/marketplace.json` の `plugins` に `{"name": "<name>", "source": "./plugins/<name>"}` を追加
4. `./scripts/sync-skills.sh` を実行してコミット
5. このREADMEの「収録スキル」の表に1行追加する

2と3を忘れた場合は `lint-skills.sh` が具体的に何が足りないかを指摘して落ちるので、「配布したつもりで何も配られていない」状態にはなりません。

スキルを削除・改名したときは、`sync-skills.sh` が対応するSSoTを失った生成先を検出して削除します（`--check` では取り残しとして報告）。プラグインのマニフェストとマーケットプレイスの登録は手動で消してください。
