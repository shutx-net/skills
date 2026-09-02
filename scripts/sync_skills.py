#!/usr/bin/env python3
"""スキル定義をSSoT（skills/）から各配布チャネルへ同期する。

SSoT: skills/<name>/            — スキル定義の唯一の正
生成先:
  .apm/skills/<name>/           — APMパッケージ用
  plugins/<name>/skills/<name>/ — Claude Codeプラグイン用

使い方:
  python3 scripts/sync_skills.py           # 生成先を同期（書き込み）
  python3 scripts/sync_skills.py --check   # 差分があれば非ゼロ終了（CI用）
"""
import argparse
import filecmp
import pathlib
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SOURCE_DIR = ROOT / "skills"

#: SSoTのスキル名 -> 同期先ディレクトリのリスト
TARGETS = {
    "impl": [
        ROOT / ".apm" / "skills" / "impl",
        ROOT / "plugins" / "impl" / "skills" / "impl",
    ],
}

GENERATED_NOTE = (
    "このディレクトリは skills/{name}/ から生成されています。"
    "直接編集せず、skills/{name}/ を編集して "
    "`python3 scripts/sync_skills.py` を実行してください。"
)


def iter_files(base: pathlib.Path):
    """ディレクトリ配下のファイルを相対パスで列挙する（同期メモは除く）。"""
    for path in sorted(base.rglob("*")):
        if path.is_file() and path.name != "GENERATED.md":
            yield path.relative_to(base)


def diff_dirs(src: pathlib.Path, dst: pathlib.Path) -> list[str]:
    """srcとdstの差分を人間可読な文字列のリストで返す。"""
    diffs = []
    src_files = set(iter_files(src))
    dst_files = set(iter_files(dst)) if dst.is_dir() else set()

    for rel in sorted(src_files - dst_files):
        diffs.append(f"{dst.relative_to(ROOT)}/{rel}: 生成先にありません")
    for rel in sorted(dst_files - src_files):
        diffs.append(f"{dst.relative_to(ROOT)}/{rel}: SSoTにない余分なファイルです")
    for rel in sorted(src_files & dst_files):
        if not filecmp.cmp(src / rel, dst / rel, shallow=False):
            diffs.append(f"{dst.relative_to(ROOT)}/{rel}: 内容がSSoTと異なります")
    return diffs


def sync(src: pathlib.Path, dst: pathlib.Path) -> None:
    """dstをsrcの内容で置き換え、生成物であることを示すメモを添える。"""
    if dst.is_dir():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    note = GENERATED_NOTE.format(name=src.name)
    (dst / "GENERATED.md").write_text(f"<!-- {note} -->\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="同期せず、差分があれば非ゼロ終了する（CI用）",
    )
    args = parser.parse_args()

    all_diffs: list[str] = []
    for name, targets in TARGETS.items():
        src = SOURCE_DIR / name
        if not src.is_dir():
            print(f"エラー: SSoT '{src.relative_to(ROOT)}' がありません", file=sys.stderr)
            return 1
        for dst in targets:
            if args.check:
                all_diffs.extend(diff_dirs(src, dst))
            else:
                sync(src, dst)
                print(f"同期: {src.relative_to(ROOT)} -> {dst.relative_to(ROOT)}")

    if args.check:
        if all_diffs:
            print(f"NG: 生成先がSSoTと同期されていません（{len(all_diffs)}件）\n", file=sys.stderr)
            for d in all_diffs:
                print(f"  - {d}", file=sys.stderr)
            print(
                "\n修正: skills/ を編集したうえで "
                "`python3 scripts/sync_skills.py` を実行してコミットしてください。",
                file=sys.stderr,
            )
            return 1
        print("OK: すべての生成先がSSoTと同期されています")
    return 0


if __name__ == "__main__":
    sys.exit(main())
