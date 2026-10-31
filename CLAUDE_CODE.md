# Claude Code

[READMEに戻る](README.md)

Claude Codeのプラグインマーケットプレイスから、必要なスキルをインストールできます。

## インストール

Claude Code上で、マーケットプレイスを登録して必要なスキルをインストールします。

```text
/plugin marketplace add shutx-net/skills
/plugin install <スキル名>@shutx-skills
```

`<スキル名>` は [収録スキル](README.md#収録スキル) の名前に置き換えてください。

## 配布形式

| パス | 用途 |
| --- | --- |
| `.claude-plugin/marketplace.json` | マーケットプレイス定義 |
| `plugins/<name>/.claude-plugin/plugin.json` | プラグインマニフェスト |
| `plugins/<name>/skills/<name>/` | `skills/<name>/` から生成するスキル（Codexと共用） |

マーケットプレイスの `plugins` に `{"name": "<name>", "source": "./plugins/<name>"}` を追加して登録します。

Claude Codeはマニフェストの `version` が変わるまで、インストール済みの利用者に更新を配りません。スキルを編集したら、Codex用マニフェストと同じ値に上げてください。

全チャネルで共通のSKILL.mdを使うため、Claude Code独自のfrontmatter（`argument-hint` / `when_to_use` 等）は使いません。

## 改名と削除

配布側では、`.claude-plugin/marketplace.json` の `renames` に旧名を足します。改名なら `"旧名": "新しい名前"`、削除なら `"旧名": null` を指定します。インストール済みの利用者の設定は、新しい名前へ自動で移ります。`renames` は履歴なので、移行が済んでも消しません。

スキル編集・追加、同期、検証の手順は、[CONTRIBUTING.md](CONTRIBUTING.md) を参照してください。
