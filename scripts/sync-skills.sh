#!/bin/sh
# スキル定義をSSoT（skills/）から各配布チャネルへ同期する。
#
# SSoT: skills/<name>/            — スキル定義の唯一の正
# 生成先:
#   .apm/skills/<name>/           — APMパッケージ用
#   plugins/<name>/skills/<name>/ — Claude Codeプラグイン用
#
# 使い方:
#   ./scripts/sync-skills.sh           # 生成先を同期（書き込み）
#   ./scripts/sync-skills.sh --check   # 差分があれば非ゼロ終了（CI用）
#
# 依存: POSIX sh と coreutils（cp / rm / diff / mkdir / sed）のみ。

set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)

# 同期対象のスキル名（スペース区切り）
SKILL_NAMES="impl"

# スキル名 -> 生成先ディレクトリ（ROOTからの相対パス、1行1件）
targets_for() {
	case "$1" in
	impl)
		printf '%s\n' ".apm/skills/impl" "plugins/impl/skills/impl"
		;;
	*)
		printf 'エラー: スキル "%s" の同期先が未定義です\n' "$1" >&2
		exit 1
		;;
	esac
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
	_rel=$3
	if [ ! -d "$_dst" ]; then
		printf '  - %s: 生成先ディレクトリがありません\n' "$_rel" >&2
		return 1
	fi
	if _out=$(diff -r -x GENERATED.md "$_src" "$_dst" 2>&1); then
		return 0
	fi
	printf '  - %s: SSoTと一致しません\n' "$_rel" >&2
	printf '%s\n' "$_out" | sed 's|^|      |' >&2
	return 1
}

drift=0
for name in $SKILL_NAMES; do
	src="$ROOT/skills/$name"
	if [ ! -d "$src" ]; then
		printf 'エラー: SSoT "skills/%s" がありません\n' "$name" >&2
		exit 1
	fi
	for rel in $(targets_for "$name"); do
		if [ "$CHECK" -eq 1 ]; then
			check_one "$src" "$ROOT/$rel" "$rel" || drift=1
		else
			sync_one "$src" "$ROOT/$rel" "$name"
			printf '同期: skills/%s -> %s\n' "$name" "$rel"
		fi
	done
done

if [ "$CHECK" -eq 1 ]; then
	if [ "$drift" -ne 0 ]; then
		printf '\nNG: 生成先がSSoTと同期されていません\n' >&2
		printf '修正: skills/ を編集したうえで `./scripts/sync-skills.sh` を実行してコミットしてください。\n' >&2
		exit 1
	fi
	printf 'OK: すべての生成先がSSoTと同期されています\n'
fi
