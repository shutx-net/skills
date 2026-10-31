# Codex CLI

[READMEに戻る](README.md)

Codex CLIのプラグインマーケットプレイスから、必要なスキルをインストールできます。

## インストール

ターミナルで、マーケットプレイスを登録して必要なスキルをインストールします。

```bash
codex plugin marketplace add shutx-net/skills
codex plugin add <スキル名>@shutx-skills
```

`<スキル名>` は [収録スキル](README.md#収録スキル) の名前に置き換えてください。

## 更新

配布元を更新し、使っているプラグインを再取得します。

```bash
codex plugin marketplace upgrade shutx-skills
codex plugin add <スキル名>@shutx-skills
```

コマンドの仕様は、OpenAI公式の [Developer commands](https://learn.chatgpt.com/docs/developer-commands#codex-plugin) を参照してください。

## 配布形式

| パス | 用途 |
| --- | --- |
| `.agents/plugins/marketplace.json` | マーケットプレイス定義 |
| `plugins/<name>/plugin.json` | Agent Plugins形式のマニフェスト |
| `plugins/<name>/skills/<name>/` | `skills/<name>/` から生成するスキル（Claude Codeと共用） |
| `plugins/<name>/assets/` | 表示用アイコン |

マニフェストはプラグイン直下の `plugin.json` に置き、Agent Pluginsのスキーマを宣言します。スキルは直下の `skills/` から検出されるため、マニフェストに `skills` フィールドは不要です。表示名やアイコンは `extensions.com.openai.interface` に置き、`logo` / `composerIcon` が参照する画像を `assets/` 内に用意します。

マーケットプレイスの `source.path` は、リポジトリルートからの `./plugins/<name>` とし、各登録に `policy.installation` / `policy.authentication` / `category` を指定します。既存の登録では、それぞれ `AVAILABLE` / `ON_INSTALL` / `Productivity` を使っています。

配布形式は、OpenAI公式の [Package your plugin](https://developers.openai.com/plugins/build/plugins) に準拠しています。

## 改名と削除

改名されたスキルは、旧名のプラグインを削除してから新名でインストールします。削除だけの場合は1つ目のコマンドを実行します。

```bash
codex plugin remove <旧名>@shutx-skills
codex plugin add <新しい名前>@shutx-skills
```

スキル編集・追加、同期、検証の手順は、[CONTRIBUTING.md](CONTRIBUTING.md) を参照してください。
