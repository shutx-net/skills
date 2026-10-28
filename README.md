# shutx skills

Claude Code / Codex などで使うスキル・プラグイン置き場。このリポジトリは以下の3通りの方法で配布されます:

1. **Claude Code プラグインマーケットプレイス** — `/plugin` でインストールする形式
2. **Codex プラグインマーケットプレイス** — Codex CLIで配布元を登録し、プラグイン単位でインストールする形式
3. **[APM (Agent Package Manager)](https://microsoft.github.io/apm/) パッケージ** — Copilot / Cursor / Codex 等でも使える形式

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

### Codex（プラグイン）

ターミナルで、マーケットプレイスを登録して必要なスキルをインストールします。APMは不要です:

```bash
codex plugin marketplace add shutx-net/skills
codex plugin add <スキル名>@shutx-skills
```

例えば、コミットメッセージのスキルだけを使う場合:

```bash
codex plugin add writing-commit-messages@shutx-skills
```

インストール後は新しいCodexセッションを開始してください。登録内容とインストール済みプラグインは次のコマンドで確認できます:

```bash
codex plugin marketplace list
codex plugin list
```

配布元を更新し、使っているプラグインを再取得するには:

```bash
codex plugin marketplace upgrade shutx-skills
codex plugin add <スキル名>@shutx-skills
```

配布形式はOpenAI公式の [Package your plugin](https://developers.openai.com/plugins/build/plugins)、コマンドは [Developer commands](https://learn.chatgpt.com/docs/developer-commands#codex-plugin) に準拠しています。CIではCodex CLI `0.163.0` で、各プラグインのインストールと全同梱ファイルの一致を検証します。

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
plugins/<name>/skills/<name>/     # 生成物: Claude Code / Codexプラグイン共用

evals/<name>/evals.json           # スキルの評価（配布物には含めない）

apm.yml                           # APMパッケージマニフェスト
.claude-plugin/marketplace.json   # Claude Code マーケットプレイス定義
plugins/<name>/.claude-plugin/plugin.json
.agents/plugins/marketplace.json # Codex マーケットプレイス定義
plugins/<name>/plugin.json       # Codex用のAgent Plugins形式マニフェスト
plugins/<name>/assets/           # Codexの表示用アイコン
scripts/
├── sync-skills.sh                # SSoT → 生成先の同期 / --check で乖離検出
├── lint-skills.sh                # マニフェスト・スキル規約の検証
└── check-codex-plugins.mjs        # Codex配布定義の整合性 / --install でインストール検証
```

SKILL.mdは**自己完結**で、すべてのチャネルで完全に同一の内容です。Claude CodeとCodexは同じプラグインディレクトリの `skills/` を使います。専用サブエージェントは同梱せず、実行環境にあるサブエージェント機構（あれば）を使い、無ければ自力実行にフォールバックします。これによりチャネル間で挙動が分岐しません。

Codex用マニフェストは、新規パッケージ向けの推奨形式であるプラグイン直下の `plugin.json` を使い、Agent Pluginsのスキーマを宣言します。スキルは直下の `skills/` から検出されるため、マニフェストに `skills` フィールドは不要です。表示名やアイコンは `extensions.com.openai.interface` に置きます。マーケットプレイスの `source.path` は、リポジトリルートからの `./plugins/<name>` とし、各登録に `policy.installation` / `policy.authentication` / `category` を指定します。

同じ理由で、frontmatter には Agent Skills 仕様にある項目（`name` / `description` / `license` / `compatibility` / `metadata` / `allowed-tools`）だけを使います。Claude Code 独自の項目（`argument-hint` / `when_to_use` 等）は、Claude Code の外では働かず、claude.ai へのアップロードではエラーになります。CI の skills-ref の検証で検出されます。

### スキルを編集するとき

1. `skills/<name>/` を編集する（生成先を直接編集しない）
2. `plugins/<name>/.claude-plugin/plugin.json` と `plugins/<name>/plugin.json` の `version` を同じ値に上げる（修正はパッチ、機能の追加やふるまいの変更はマイナーを上げる）。Claude Code は `version` が変わるまで、インストール済みの利用者に更新を配りません。両マニフェストの `name` / `version` / `description` / `author` / `keywords` の一致はCIで検証します
3. 同期する:

```bash
./scripts/sync-skills.sh
```

4. 生成物も含めてコミットする（配布時に取得されるのは生成先のファイルのため、リポジトリにコミットが必要です）

CIは `./scripts/sync-skills.sh --check` を実行し、生成先がSSoTと乖離していればビルドを落とします。

同期スクリプトと `lint-skills.sh` はPOSIX shと標準的なコマンド（cp / diff / grep / sed / awk / wc）だけで動くため、追加のランタイムやパッケージのインストールは不要です。ローカル検証も同じコマンドで実行できます:

```bash
./scripts/lint-skills.sh          # マニフェスト・スキル規約の検証
./scripts/sync-skills.sh --check  # 生成先の乖離チェック
```

Codex用のJSON・配布登録・共通メタデータ・アイコン参照は、Node.js 22以上で検証できます（npm依存はありません）:

```bash
node scripts/check-codex-plugins.mjs
```

Codex CLIもインストール済みなら、実際のインストールも検証できます。一時的な `CODEX_HOME` を使うため、普段の設定やインストール済みプラグインには影響しません:

```bash
node scripts/check-codex-plugins.mjs --install
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
2. `plugins/<name>/.claude-plugin/plugin.json` と `plugins/<name>/plugin.json` を作成（`name` / `version` / `description` / `author` / `keywords` は両者でそろえる）。Codex用には既存プラグインにならい、`extensions.com.openai.interface` と、`logo` / `composerIcon` が参照する `assets/` 内の画像も用意する
3. 両マーケットプレイスに登録する。`.claude-plugin/marketplace.json` の `plugins` に `{"name": "<name>", "source": "./plugins/<name>"}` を追加し、`.agents/plugins/marketplace.json` にも既存の登録と同じ形式で `source` / `policy` / `category` を追加する
4. `apm.yml` の `description` がスキル集全体の説明になっているか見直し、`keywords` にそのプラグインの `keywords` を足す
5. `./scripts/sync-skills.sh` を実行してコミット
6. このREADMEの「収録スキル」の表に1行追加する

2と3の漏れは `lint-skills.sh` と `check-codex-plugins.mjs` が検出します。CodexのCIでは、同梱するテンプレート・参照資料・アイコンを含むプラグイン全体がインストールされることも確認します。

スキルを削除・改名したときは、`sync-skills.sh` が対応するSSoTを失った生成先を検出して削除します（`--check` では取り残しとして報告）。プラグインの両マニフェスト・アイコンと、両マーケットプレイスの登録は手動で消し、`apm.yml` の `description` と `keywords` も見直してください。

あわせて、Claude Code用の `.claude-plugin/marketplace.json` の `renames` に旧名を足します（改名なら `"旧名": "新しい名前"`、削除なら `"旧名": null`）。Claude Codeでインストール済みの利用者の設定が、新しい名前へ自動で移ります。`renames` は履歴なので、移行が済んでも消しません。Codexでは旧名を `codex plugin remove <旧名>@shutx-skills` で削除し、新名をインストールします。
