# shutx skills

Claude Code 用のスキル・プラグイン置き場。このリポジトリは以下の2通りの方法で配布されます:

1. **Claude Code プラグインマーケットプレイス** — `/plugin` でインストールする形式
2. **[APM (Agent Package Manager)](https://microsoft.github.io/apm/) パッケージ** — Copilot / Cursor / Codex 等でも使える形式

## 収録スキル

| スキル | 概要 |
| --- | --- |
| [`implementing-in-phases`](skills/implementing-in-phases/SKILL.md) | 実装タスクをフェーズ分割し、フェーズごとの計画JSONを書き出してから段階的に実装する |
| [`writing-commit-messages`](skills/writing-commit-messages/SKILL.md) | git commitのメッセージを Conventional Commits 形式（`feat:` / `fix:` 等のプレフィックス）で書く |
| [`creating-job-application-docs`](skills/creating-job-application-docs/SKILL.md) | 履歴書・職務経歴書・エントリーシートを、印刷・PDF化を前提とした HTML/CSS で作成する |

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

### 旧名から移行する

次のスキルは名前を変えました。

| 旧名 | 新しい名前 |
| --- | --- |
| `impl` | `implementing-in-phases` |
| `commit-message` | `writing-commit-messages` |

- **Claude Code（プラグイン）**: マーケットプレイスを更新すると、旧名で有効にしていた設定は、`marketplace.json` の `renames` によって新しい名前に書き換わります。そのあと、新しい名前で一度インストールしてください（旧名の削除は不要です）:

  ```
  /plugin marketplace update shutx-skills
  /plugin install <新しい名前>@shutx-skills
  ```

- **APM**: `apm update` で依存を更新すると、新しい名前のスキルが配備され、旧名のスキルは削除されます。

## リポジトリ構成とスキル定義の同期

スキル定義の**唯一の正（SSoT）は `skills/`** です。各配布チャネル向けのディレクトリは、そこから同期スクリプトで生成されます。

```
skills/<name>/                    # ★ SSoT — 編集するのはここだけ
├── SKILL.md                      #   スキル本体（自己完結）
└── references/                   #   本文からLOADする補助ドキュメント

.apm/skills/<name>/               # 生成物: APMパッケージ用
plugins/<name>/skills/<name>/     # 生成物: Claude Codeプラグイン用

evals/<name>/evals.json           # スキルの評価（配布物には含めない）

apm.yml                           # APMパッケージマニフェスト
.claude-plugin/marketplace.json   # Claude Code マーケットプレイス定義
plugins/<name>/.claude-plugin/plugin.json
scripts/
├── sync-skills.sh                # SSoT → 生成先の同期 / --check で乖離検出
└── lint-skills.sh                # マニフェスト・スキル規約の検証
```

SKILL.mdは**自己完結**で、どちらのチャネル経由でも完全に同一の内容です。専用サブエージェントは同梱せず、実行環境にあるサブエージェント機構（あれば）を使い、無ければ自力実行にフォールバックします。これによりチャネル間で挙動が分岐しません。

同じ理由で、frontmatter には Agent Skills 仕様にある項目（`name` / `description` / `license` / `compatibility` / `metadata` / `allowed-tools`）だけを使います。Claude Code 独自の項目（`argument-hint` / `when_to_use` 等）は、Claude Code の外では働かず、claude.ai へのアップロードではエラーになります。CI の skills-ref の検証で検出されます。

### スキルを編集するとき

1. `skills/<name>/` を編集する（生成先を直接編集しない）
2. `plugins/<name>/.claude-plugin/plugin.json` の `version` を上げる（修正はパッチ、機能の追加やふるまいの変更はマイナーを上げる）。Claude Code は `version` が変わるまで、インストール済みの利用者に更新を配りません
3. 同期する:

```bash
./scripts/sync-skills.sh
```

4. 生成物も含めてコミットする（配布時に取得されるのは生成先のファイルのため、リポジトリにコミットが必要です）

CIは `./scripts/sync-skills.sh --check` を実行し、生成先がSSoTと乖離していればビルドを落とします。

スクリプトはPOSIX shと標準的なコマンド（cp / diff / grep / sed / awk / wc）だけで動くため、追加のランタイムやパッケージのインストールは不要です。ローカル検証も同じコマンドで実行できます:

```bash
./scripts/lint-skills.sh          # マニフェスト・スキル規約の検証
./scripts/sync-skills.sh --check  # 生成先の乖離チェック
```

CIは、Agent Skills 仕様の検証ツール [skills-ref](https://github.com/agentskills/agentskills/tree/main/skills-ref) でも各スキルを検証します。手元で実行するには Python 3.11 以上が必要です:

```bash
pip install skills-ref==0.1.1
agentskills validate skills/<name>   # コマンド名は agentskills
```

### 評価（evals）

スキルが期待どおりに動くかを確かめる評価は `evals/<name>/evals.json` に置きます。形式は Anthropic の skill-creator スキルの `evals.json` に合わせており、評価ごとにユーザーの依頼（`prompt`）と、結果が満たすべき条件（`expectations`）を持ちます。`skills/` の外に置くため、配布物には含まれません。

スキルを変更したら、変更前のスキルと同じ評価を実行して結果を比べます。skill-creator を使えば、実行・採点・比較までをまとめて進められます。

### 新しいスキルを追加する

`skills/<name>/SKILL.md` を作れば、同期スクリプトが自動で検出して各生成先に配ります（スクリプトの編集は不要です）。ただし配布するには、そのスキルのプラグインをマニフェストに登録する必要があります:

1. `skills/<name>/SKILL.md` を作成（`name` はディレクトリ名と一致させる。名前は、ほかのスキルと同じ動名詞形（`writing-commit-messages` のような形）にする）
2. `plugins/<name>/.claude-plugin/plugin.json` を作成（`name` / `version` / `description` / `author`。`author` は `--strict` 検証で必須）
3. `.claude-plugin/marketplace.json` の `plugins` に `{"name": "<name>", "source": "./plugins/<name>"}` を追加
4. `apm.yml` の `description` がスキル集全体の説明になっているか見直し、`keywords` にそのプラグインの `keywords` を足す
5. `./scripts/sync-skills.sh` を実行してコミット
6. このREADMEの「収録スキル」の表に1行追加する

2と3を忘れた場合は `lint-skills.sh` が具体的に何が足りないかを指摘して落ちるので、「配布したつもりで何も配られていない」状態にはなりません。

スキルを削除・改名したときは、`sync-skills.sh` が対応するSSoTを失った生成先を検出して削除します（`--check` では取り残しとして報告）。プラグインのマニフェストとマーケットプレイスの登録は手動で消し、`apm.yml` の `description` と `keywords` も見直してください。

あわせて、`marketplace.json` の `renames` に旧名を足します（改名なら `"旧名": "新しい名前"`、削除なら `"旧名": null`）。インストール済みの利用者の設定が、新しい名前へ自動で移ります。`renames` は履歴なので、移行が済んでも消しません。
