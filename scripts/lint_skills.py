#!/usr/bin/env python3
"""リポジトリ内のマニフェストとスキルの整合性チェック。

- JSONマニフェスト（marketplace.json / plugin.json）がパースできること
- apm.yml に必須フィールド（name / version）があること
- APM版スキルが公式規約を満たすこと
  （name がディレクトリ名と一致、description が1024文字以内、本文500行以内）
- プラグイン版スキル・エージェント定義の frontmatter がパースできること
- マーケットプレイスの source が指すプラグインディレクトリが存在すること
"""
import json
import pathlib
import re
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
errors: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def load_frontmatter(path: pathlib.Path) -> dict:
    text = path.read_text(encoding="utf-8")
    m = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        err(f"{path}: frontmatter がありません")
        return {}
    try:
        meta = yaml.safe_load(m.group(1))
    except yaml.YAMLError as e:
        err(f"{path}: frontmatter のYAMLが不正です: {e}")
        return {}
    if not isinstance(meta, dict):
        err(f"{path}: frontmatter がマッピングではありません")
        return {}
    return meta


# --- JSONマニフェスト ---
marketplace = {}
for rel in [".claude-plugin/marketplace.json", "plugins/impl/.claude-plugin/plugin.json"]:
    path = ROOT / rel
    if not path.is_file():
        err(f"{rel}: ファイルがありません")
        continue
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        err(f"{rel}: JSONが不正です: {e}")
        continue
    if rel.endswith("marketplace.json"):
        marketplace = data

# marketplace の source が存在するか
for plugin in marketplace.get("plugins", []):
    source = plugin.get("source")
    if isinstance(source, str) and source.startswith("./"):
        if not (ROOT / source).is_dir():
            err(f"marketplace.json: source '{source}' が存在しません")

# --- apm.yml ---
apm_path = ROOT / "apm.yml"
if not apm_path.is_file():
    err("apm.yml がありません")
else:
    try:
        apm = yaml.safe_load(apm_path.read_text(encoding="utf-8"))
        for field in ("name", "version"):
            if not apm.get(field):
                err(f"apm.yml: 必須フィールド '{field}' がありません")
    except yaml.YAMLError as e:
        err(f"apm.yml: YAMLが不正です: {e}")

# --- APM版スキル（公式規約） ---
for skill_dir in sorted((ROOT / ".apm" / "skills").iterdir()):
    if not skill_dir.is_dir():
        continue
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        err(f"{skill_dir}: SKILL.md がありません")
        continue
    meta = load_frontmatter(skill_md)
    name = meta.get("name", "")
    desc = meta.get("description", "")
    if name != skill_dir.name:
        err(f"{skill_md}: name '{name}' がディレクトリ名 '{skill_dir.name}' と一致しません")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name or ""):
        err(f"{skill_md}: name '{name}' は小文字英数字とハイフンのみ（連続ハイフン不可）")
    if len(name or "") > 64:
        err(f"{skill_md}: name が64文字を超えています")
    if not desc:
        err(f"{skill_md}: description がありません")
    elif len(desc) > 1024:
        err(f"{skill_md}: description が1024文字を超えています ({len(desc)}文字)")
    lines = skill_md.read_text(encoding="utf-8").count("\n") + 1
    if lines > 500:
        err(f"{skill_md}: 本文が500行を超えています ({lines}行)")
    # LOAD で参照している references ファイルの存在確認
    for ref in re.findall(r"LOAD (references/[\w./-]+)", skill_md.read_text(encoding="utf-8")):
        ref = ref.rstrip(".")
        if not (skill_dir / ref).is_file():
            err(f"{skill_md}: 参照先 '{ref}' が存在しません")

# --- プラグイン版スキルとエージェント ---
plugin_skill = ROOT / "plugins/impl/skills/impl/SKILL.md"
if not plugin_skill.is_file():
    err("plugins/impl/skills/impl/SKILL.md がありません")
else:
    meta = load_frontmatter(plugin_skill)
    if not meta.get("description"):
        err(f"{plugin_skill}: description がありません")

for agent_md in sorted((ROOT / "plugins/impl/agents").glob("*.md")):
    meta = load_frontmatter(agent_md)
    for field in ("name", "description"):
        if not meta.get(field):
            err(f"{agent_md}: 必須フィールド '{field}' がありません")

# --- 結果 ---
if errors:
    print(f"NG: {len(errors)}件の問題が見つかりました\n")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
print("OK: すべてのチェックを通過しました")
