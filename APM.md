# APM（Agent Package Manager）

[READMEに戻る](README.md)

[APM](https://microsoft.github.io/apm/) パッケージとして、Copilot / Cursor / OpenCode / Codex / Gemini / Claude Codeで利用できます。

## インストール

利用するプロジェクトの `apm.yml` に依存として追加します。

```yaml
dependencies:
  apm:
    - shutx-net/skills
```

その後、プロジェクト内で実行します。

```bash
apm install
```

Claude Codeでは `.claude/skills/` に、Copilot / Cursor / OpenCode / Codex / Geminiでは `.agents/skills/` にスキルが配備されます。

## 配布形式

リポジトリルートの `apm.yml` がパッケージマニフェストです。配布用スキルは、`skills/<name>/` から `.apm/skills/<name>/` に同期して生成します。

スキルを追加・削除・改名するときは、`apm.yml` の `description` と `keywords` も見直してください。

スキル編集・追加、同期、検証の手順は、[CONTRIBUTING.md](CONTRIBUTING.md) を参照してください。
