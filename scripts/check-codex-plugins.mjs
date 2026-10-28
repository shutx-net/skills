// OpenAI公式のパッケージ形式と、このリポジトリの配布登録・メタデータを検証する。
// https://developers.openai.com/plugins/build/plugins
// --install では、一時的なCODEX_HOMEで実際にインストールし、同梱ファイルも比較する。
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { mkdirSync, mkdtempSync, readFileSync, readdirSync, rmSync, statSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, relative, resolve, sep } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const readJson = (path) => JSON.parse(readFileSync(path, "utf8"));
const nonempty = (value) => typeof value === "string" && value.trim().length > 0;

function checkManifests() {
  const marketplace = readJson(join(root, ".agents/plugins/marketplace.json"));
  const claudeMarketplace = readJson(join(root, ".claude-plugin/marketplace.json"));
  const names = readdirSync(join(root, "skills"), { withFileTypes: true })
    .filter((entry) => entry.isDirectory()).map((entry) => entry.name).sort();

  assert.equal(marketplace.name, claudeMarketplace.name, "マーケットプレイス名が一致しません");
  assert(nonempty(marketplace.interface?.displayName), "マーケットプレイスのdisplayNameがありません");
  assert.deepEqual(marketplace.plugins.map((entry) => entry.name).sort(), names,
    "Codexの配布登録がskills/と一致しません（登録漏れ・重複・取り残し）");
  assert.deepEqual(claudeMarketplace.plugins.map((entry) => entry.name).sort(), names,
    "Claude Codeの配布登録がskills/と一致しません");

  for (const entry of marketplace.plugins) {
    const name = entry.name;
    assert.deepEqual(entry.source, { source: "local", path: `./plugins/${name}` },
      `${name}: sourceはリポジトリルートからの相対パスで指定してください`);
    assert.equal(entry.policy?.installation, "AVAILABLE", `${name}: installationが不正です`);
    assert.equal(entry.policy?.authentication, "ON_INSTALL", `${name}: authenticationが不正です`);
    assert(nonempty(entry.category), `${name}: categoryがありません`);

    const pluginRoot = join(root, "plugins", name);
    const manifest = readJson(join(pluginRoot, "plugin.json"));
    const claude = readJson(join(pluginRoot, ".claude-plugin/plugin.json"));
    assert.equal(manifest.$schema, "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
      `${name}: Agent Pluginsのスキーマを指定してください`);
    assert.equal(manifest.name, name, `${name}: プラグイン名が一致しません`);
    for (const key of ["name", "version", "description", "author", "keywords"]) {
      assert.deepEqual(manifest[key], claude[key], `${name}: ${key}がClaude Code用と一致しません`);
    }
    for (const key of ["version", "description"]) {
      assert(nonempty(manifest[key]), `${name}: ${key}がありません`);
    }
    assert(nonempty(manifest.author?.name), `${name}: author.nameがありません`);
    assert(statSync(join(pluginRoot, "skills", name, "SKILL.md")).isFile(),
      `${name}: 同梱スキルがありません`);

    const ui = manifest.extensions?.["com.openai"]?.interface;
    for (const key of ["displayName", "shortDescription", "developerName"]) {
      assert(nonempty(ui?.[key]), `${name}: interface.${key}がありません`);
    }
    assert.equal(ui.category, entry.category, `${name}: categoryが一致しません`);
    for (const key of ["logo", "composerIcon"]) {
      assert(nonempty(ui[key]) && ui[key].startsWith("./"), `${name}: ${key}には./から始まるパスが必要です`);
      const asset = resolve(pluginRoot, ui[key]);
      const path = relative(pluginRoot, asset);
      assert(path !== ".." && !path.startsWith(`..${sep}`), `${name}: ${key}がプラグイン外を参照しています`);
      assert(statSync(asset).isFile(), `${name}: ${key}のファイルがありません`);
    }
  }
  return marketplace;
}

function checkInstallation(marketplace) {
  const testDir = mkdtempSync(join(tmpdir(), "shutx-skills-codex-"));
  const env = { ...process.env, CODEX_HOME: join(testDir, "codex-home") };
  const codex = (...args) => JSON.parse(execFileSync("codex", [...args, "--json"], {
    cwd: testDir, env, encoding: "utf8", stdio: ["ignore", "pipe", "inherit"],
  }));
  try {
    mkdirSync(env.CODEX_HOME);
    const added = codex("plugin", "marketplace", "add", root);
    assert.equal(added.marketplaceName, marketplace.name);
    for (const entry of marketplace.plugins) {
      const installed = codex("plugin", "add", `${entry.name}@${marketplace.name}`);
      const pluginRoot = join(root, "plugins", entry.name);
      const manifest = readJson(join(pluginRoot, "plugin.json"));
      assert.equal(installed.pluginId, `${entry.name}@${marketplace.name}`);
      assert.equal(installed.version, manifest.version);
      // テンプレート・参照資料・アイコンを含むパッケージ全体が配備されたことを確認する。
      execFileSync("diff", ["-r", pluginRoot, installed.installedPath], { stdio: "inherit" });
      console.log(`OK: ${installed.pluginId}をインストールし、全ファイルの一致を確認しました`);
    }
  } finally {
    rmSync(testDir, { recursive: true, force: true });
  }
}

try {
  assert(process.argv.slice(2).every((arg) => arg === "--install"), "使い方: node scripts/check-codex-plugins.mjs [--install]");
  const marketplace = checkManifests();
  console.log(`OK: Codexのマーケットプレイスと${marketplace.plugins.length}件のプラグイン定義が整合しています`);
  if (process.argv.includes("--install")) checkInstallation(marketplace);
} catch (error) {
  console.error(`NG: ${error.message}`);
  process.exitCode = 1;
}
