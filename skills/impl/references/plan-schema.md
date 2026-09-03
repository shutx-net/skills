# 計画JSONスキーマ

implスキルの計画立案工程が書き出すJSONファイルの形式。

## plan-index.json（全体索引）

```json
{
  "task": "タスクの1行要約",
  "effort": "決定したeffortレベル",
  "createdAt": "ISO8601",
  "phases": [
    { "id": 1, "file": "phase-01.json", "title": "フェーズ名", "dependsOn": [] },
    { "id": 2, "file": "phase-02.json", "title": "フェーズ名", "dependsOn": [1] }
  ]
}
```

## phase-NN.json（各フェーズ）

```json
{
  "id": 1,
  "title": "フェーズ名",
  "goal": "このフェーズで達成すること（1〜2文）",
  "dependsOn": [],
  "contextFiles": ["実装前に読むべきファイルパス（最小限）"],
  "steps": [
    {
      "file": "変更対象ファイルの相対パス",
      "action": "create | modify | delete",
      "detail": "何をどう変更するかの具体的な説明。必要なら短いコード断片や関数シグネチャを含める"
    }
  ],
  "verification": ["このフェーズ完了を確認するコマンドや手順（例: npm test -- path/to/test）"],
  "notes": "実装者への注意点（既存の慣習、落とし穴など）。不要なら省略"
}
```

## サイズの目安

- 1ファイルあたり最大でも約8KB / `steps` は10個以内
- 超えそうな場合はフェーズをさらに分割する
