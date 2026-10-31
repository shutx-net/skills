# コントリビューションガイド

[READMEに戻る](README.md)

## リポジトリ構成とスキル定義の同期

スキル定義の**唯一の正（SSoT）は `skills/`** です。各配布チャネル向けのディレクトリは、そこから同期スクリプトで生成されます。

```text
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

同じ理由で、frontmatter には Agent Skills 仕様にある項目（`name` / `description` / `license` / `compatibility` / `metadata` / `allowed-tools`）だけを使います。仕様にない項目は、CI の skills-ref の検証で検出されます。

## スキルを編集するとき

1. `skills/<name>/` を編集する（生成先を直接編集しない）
2. `plugins/<name>/.claude-plugin/plugin.json` と `plugins/<name>/plugin.json` の `version` を同じ値に上げる（修正はパッチ、機能の追加やふるまいの変更はマイナーを上げる）。両マニフェストの `name` / `version` / `description` / `author` / `keywords` の一致はCIで検証します
3. 同期する:

   ```bash
   ./scripts/sync-skills.sh
   ```

4. 生成物も含めてコミットする（配布時に取得されるのは生成先のファイルのため、リポジトリにコミットが必要です）

## 検証

CIは `./scripts/sync-skills.sh --check` を実行し、生成先がSSoTと乖離していればビルドを落とします。

```bash
./scripts/lint-skills.sh          # マニフェスト・スキル規約の検証
./scripts/sync-skills.sh --check  # 生成先の乖離チェック
```

CodexのCIでは `scripts/check-codex-plugins.mjs` で配布定義・共通メタデータ・アイコン参照を検証します。`--install` では、同梱するテンプレート・参照資料・アイコンを含むプラグイン全体がインストールされることも確認します。

CIは、Agent Skills 仕様の検証ツール [skills-ref](https://github.com/agentskills/agentskills/tree/main/skills-ref) でも各スキルを検証します。手元で実行するには Python 3.11 以上が必要です:

```bash
pip install skills-ref==0.1.1
agentskills validate skills/<name>   # コマンド名は agentskills
```

## 評価（evals）

スキルが期待どおりに動くかを確かめる評価は `evals/<name>/evals.json` に置きます。形式は Anthropic の skill-creator スキルの `evals.json` に合わせており、評価ごとにユーザーの依頼（`prompt`）と、結果が満たすべき条件（`expectations`）を持ちます。`skills/` の外に置くため、配布物には含まれません。

スキルを変更したら、変更前のスキルと同じ評価を実行して結果を比べます。skill-creator を使えば、実行・採点・比較までをまとめて進められます。

## 新しいスキルを追加する

`skills/<name>/SKILL.md` を作れば、同期スクリプトが自動で検出して各生成先に配ります（スクリプトの編集は不要です）。ただし配布するには、そのスキルのプラグインをマニフェストに登録する必要があります:

1. `skills/<name>/SKILL.md` を作成（`name` はディレクトリ名と一致させる。名前は、ほかのスキルと同じ動名詞形（`writing-commit-messages` のような形）にする）
2. `plugins/<name>/.claude-plugin/plugin.json` と `plugins/<name>/plugin.json` を作成（`name` / `version` / `description` / `author` / `keywords` は両者でそろえる）。各形式の詳細は [Claude Code](CLAUDE_CODE.md#配布形式) / [Codex CLI](CODEX_CLI.md#配布形式) のガイドを参照する
3. `.claude-plugin/marketplace.json` と `.agents/plugins/marketplace.json` の `plugins` に登録する（各ガイドと既存の登録を参照）
4. `apm.yml` の `description` がスキル集全体の説明になっているか見直し、`keywords` にそのプラグインの `keywords` を足す
5. `./scripts/sync-skills.sh` を実行してコミット
6. [READMEの「収録スキル」](README.md#収録スキル)の表に1行追加する

2と3の漏れは `lint-skills.sh` と `check-codex-plugins.mjs` が検出します。

## スキルを削除・改名するとき

スキルを削除・改名したときは、`sync-skills.sh` が対応するSSoTを失った生成先を検出して削除します（`--check` では取り残しとして報告）。プラグインの両マニフェスト・アイコンと、両マーケットプレイスの登録は手動で消し、`apm.yml` の `description` と `keywords` も見直してください。

改名・削除時の設定と移行手順は、[Claude Code](CLAUDE_CODE.md#改名と削除) / [Codex CLI](CODEX_CLI.md#改名と削除) のガイドを参照してください。
