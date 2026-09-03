#!/bin/sh
# スキル定義をSSoT（skills/）から各配布チャネルへ同期する。
#
# SSoT: skills/<name>/            — スキル定義の唯一の正
# 生成先（スキル名から規約で導出する）:
#   .apm/skills/<name>/           — APMパッケージ用
#   plugins/<name>/skills/<name>/ — Claude Codeプラグイン用
#
# skills/ 配下のディレクトリは自動で対象になる。スキルを増やすときに
# このスクリプトを編集する必要はない（配布に必要なマニフェストの登録は
# lint-skills.sh が検査する）。
#
# 使い方:
#   ./scripts/sync-skills.sh           # 生成先を同期（書き込み）
#   ./scripts/sync-skills.sh --check   # 差分があれば非ゼロ終了（CI用）
#
# 依存: POSIX sh と coreutils（cp / rm / diff / mkdir / sed）のみ。

set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT"

# スキル名 -> 生成先ディレクトリ（ROOTからの相対パス、1行1件）
targets_for() {
	printf '%s\n' ".apm/skills/$1" "plugins/$1/skills/$1"
}

usage() {
	printf '使い方: %s [--check]\n' "$0" >&2
	printf '  --check  同期せず、差分があれば非ゼロ終了する（CI用）\n' >&2
}

CHECK=0
case "${1:-}" in
--check) CHECK=1 ;;
"") ;;
-h | --help)
	usage
	exit 0
	;;
*)
	printf 'エラー: 不明な引数 "%s"\n' "$1" >&2
	usage
	exit 2
	;;
esac

sync_one() {
	_src=$1
	_dst=$2
	_name=$3
	rm -rf "$_dst"
	mkdir -p "$(dirname "$_dst")"
	cp -R "$_src" "$_dst"
	printf '<!-- このディレクトリは skills/%s/ から生成されています。直接編集せず、skills/%s/ を編集して `./scripts/sync-skills.sh` を実行してください。 -->\n' \
		"$_name" "$_name" >"$_dst/GENERATED.md"
}

# 生成先がSSoTと一致するか調べる。差分があれば内容を表示して1を返す。
# GENERATED.md は生成時に付与するメモなので比較から除外する。
check_one() {
	_src=$1
	_dst=$2
	if [ ! -d "$_dst" ]; then
		printf '  - %s: 生成先ディレクトリがありません\n' "$_dst" >&2
		return 1
	fi
	if _out=$(diff -r -x GENERATED.md "$_src" "$_dst" 2>&1); then
		return 0
	fi
	printf '  - %s: SSoTと一致しません\n' "$_dst" >&2
	printf '%s\n' "$_out" | sed 's|^|      |' >&2
	return 1
}

# SSoT配下のスキルを列挙する
skill_names() {
	for _dir in skills/*/; do
		[ -d "$_dir" ] || continue
		_name=${_dir#skills/}
		printf '%s\n' "${_name%/}"
	done
}

names=$(skill_names)
if [ -z "$names" ]; then
	printf 'エラー: skills/ にスキルがありません\n' >&2
	exit 1
fi

drift=0
for name in $names; do
	src="skills/$name"
	for rel in $(targets_for "$name"); do
		if [ "$CHECK" -eq 1 ]; then
			check_one "$src" "$rel" || drift=1
		else
			sync_one "$src" "$rel" "$name"
			printf '同期: %s -> %s\n' "$src" "$rel"
		fi
	done
done

# 対応するSSoTが無い生成先（スキルを削除・改名したあとの取り残し）を検出する
stale_targets() {
	for _dir in .apm/skills/*/ plugins/*/skills/*/; do
		[ -d "$_dir" ] || continue
		_name=$(basename "$_dir")
		[ -d "skills/$_name" ] || printf '%s\n' "${_dir%/}"
	done
}

for stale in $(stale_targets); do
	if [ "$CHECK" -eq 1 ]; then
		printf '  - %s: 対応する skills/ のスキルがありません（削除・改名の取り残し）\n' "$stale" >&2
		drift=1
	else
		rm -rf "$stale"
		printf '削除: %s（対応する skills/ のスキルなし）\n' "$stale"
	fi
done

if [ "$CHECK" -eq 1 ]; then
	if [ "$drift" -ne 0 ]; then
		printf '\nNG: 生成先がSSoTと同期されていません\n' >&2
		printf '修正: skills/ を編集したうえで `./scripts/sync-skills.sh` を実行してコミットしてください。\n' >&2
		exit 1
	fi
	printf 'OK: すべての生成先がSSoTと同期されています\n'
fi
