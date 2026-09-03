#!/bin/sh
# リポジトリ内のマニフェストとスキルの整合性チェック。
#
# スキル定義のSSoTは skills/ で、各配布チャネルへの同期は sync-skills.sh が担う。
# このスクリプトはSSoTと、同期対象外のファイル（マニフェスト等）を検証する。
#
#   - マニフェスト（marketplace.json / plugin.json / apm.yml）が存在し必須項目を持つこと
#   - marketplace.json の source が指すディレクトリが存在すること
#   - SSoTのスキルが公式規約を満たすこと
#     （name がディレクトリ名と一致、description が1024文字以内、本文500行以内）
#   - SSoTの `LOAD references/...` の参照先が存在すること
#   - 各スキルが配布チャネルに登録されていること（plugin.json / marketplace.json）
#   - プラグインにエージェントを同梱していないこと（自己完結の担保）
#
# 使い方: ./scripts/lint-skills.sh
#
# 依存: POSIX sh と coreutils（grep / sed / awk / wc / sort）のみ。

set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT"

# 文字数を正しく数えるため、利用できればUTF-8ロケールを使う（無ければバイト数で近似）。
if [ "${LC_ALL:-}" = "" ] && locale -a 2>/dev/null | grep -qix 'C\.utf-\{0,1\}8'; then
	LC_ALL=C.UTF-8
	export LC_ALL
fi

# 検出した問題はファイルに集約する。パイプやサブシェル内からも追記できるようにするため。
ERRFILE=$(mktemp)
trap 'rm -f "$ERRFILE"' EXIT HUP INT TERM

err() {
	printf '  - %s\n' "$1" >>"$ERRFILE"
}

# SKILL.md のfrontmatter（先頭の --- で挟まれた範囲）を出力する。
# frontmatterが無ければ非ゼロで終了する。
frontmatter() {
	awk '
		NR == 1 { if ($0 != "---") exit 1; next }
		/^---[[:space:]]*$/ { found = 1; exit }
		{ print }
		END { if (!found) exit 1 }
	' "$1"
}

# frontmatterから指定キーの値を取り出す（前後の引用符を除去）。
fm_value() {
	frontmatter "$1" | sed -n "s/^$2:[[:space:]]*//p" | head -n 1 |
		sed 's/^"\(.*\)"$/\1/; s/^'\''\(.*\)'\''$/\1/'
}

# --- マニフェスト ---
for f in .claude-plugin/marketplace.json apm.yml; do
	if [ ! -f "$f" ]; then
		err "$f: ファイルがありません"
	fi
done

# marketplace.json の source が指すディレクトリの存在確認
if [ -f .claude-plugin/marketplace.json ]; then
	sed -n 's/.*"source"[[:space:]]*:[[:space:]]*"\(\.\/[^"]*\)".*/\1/p' \
		.claude-plugin/marketplace.json |
		while IFS= read -r src; do
			if [ ! -d "$src" ]; then
				err "marketplace.json: source \"$src\" が存在しません"
			fi
		done
fi

# apm.yml の必須フィールド
if [ -f apm.yml ]; then
	for key in name version; do
		if ! grep -q "^$key:[[:space:]]*[^[:space:]]" apm.yml; then
			err "apm.yml: 必須フィールド '$key' がありません"
		fi
	done
fi

# --- SSoTのスキル（公式規約） ---
for skill_dir in skills/*/; do
	[ -d "$skill_dir" ] || continue
	skill_name=${skill_dir#skills/}
	skill_name=${skill_name%/}
	skill_md="${skill_dir}SKILL.md"

	if [ ! -f "$skill_md" ]; then
		err "$skill_dir: SKILL.md がありません"
		continue
	fi

	if ! frontmatter "$skill_md" >/dev/null 2>&1; then
		err "$skill_md: frontmatter がありません"
		continue
	fi

	name=$(fm_value "$skill_md" name)
	desc=$(fm_value "$skill_md" description)

	if [ "$name" != "$skill_name" ]; then
		err "$skill_md: name '$name' がディレクトリ名 '$skill_name' と一致しません"
	fi

	if ! printf '%s' "$name" | grep -qx '[a-z0-9]\{1,\}\(-[a-z0-9]\{1,\}\)*'; then
		err "$skill_md: name '$name' は小文字英数字とハイフンのみ（連続ハイフン不可）"
	fi

	if [ "$(printf '%s' "$name" | wc -m | tr -d ' ')" -gt 64 ]; then
		err "$skill_md: name が64文字を超えています"
	fi

	if [ -z "$desc" ]; then
		err "$skill_md: description がありません"
	else
		desc_len=$(printf '%s' "$desc" | wc -m | tr -d ' ')
		if [ "$desc_len" -gt 1024 ]; then
			err "$skill_md: description が1024文字を超えています (${desc_len}文字)"
		fi
	fi

	lines=$(wc -l <"$skill_md" | tr -d ' ')
	if [ "$lines" -gt 500 ]; then
		err "$skill_md: 本文が500行を超えています (${lines}行)"
	fi

	# LOAD で参照している references ファイルの存在確認
	sed -n 's/.*LOAD \(references\/[A-Za-z0-9_./-]*\).*/\1/p' "$skill_md" |
		sed 's/\.$//' | sort -u |
		while IFS= read -r ref; do
			if [ ! -f "${skill_dir}${ref}" ]; then
				err "$skill_md: 参照先 \"$ref\" が存在しません"
			fi
		done
done

# --- 配布登録の検査 ---
# skills/ にスキルを足しただけでは配布されない。各チャネルへの登録漏れを検出する。
for skill_dir in skills/*/; do
	[ -d "$skill_dir" ] || continue
	skill_name=${skill_dir#skills/}
	skill_name=${skill_name%/}

	manifest="plugins/$skill_name/.claude-plugin/plugin.json"
	if [ ! -f "$manifest" ]; then
		err "$manifest がありません（スキル '$skill_name' のプラグインマニフェスト未作成）"
	fi

	if [ -f .claude-plugin/marketplace.json ]; then
		if ! grep -q "\"\./plugins/$skill_name\"" .claude-plugin/marketplace.json; then
			err "marketplace.json: スキル '$skill_name' のプラグインが登録されていません（source \"./plugins/$skill_name\"）"
		fi
	fi
done

# --- 自己完結の担保 ---
# スキルはチャネル間で挙動が分岐しないよう自己完結させる方針のため、
# プラグイン固有のエージェント同梱を禁止する。
for plugin_dir in plugins/*/; do
	[ -d "$plugin_dir" ] || continue
	if [ -e "${plugin_dir}agents" ]; then
		err "${plugin_dir}agents: スキルは自己完結させる方針のため、プラグイン固有のエージェントは同梱しません"
	fi
done

# --- 結果 ---
if [ -s "$ERRFILE" ]; then
	count=$(wc -l <"$ERRFILE" | tr -d ' ')
	printf 'NG: %s件の問題が見つかりました\n\n' "$count" >&2
	cat "$ERRFILE" >&2
	exit 1
fi
printf 'OK: すべてのチェックを通過しました\n'
