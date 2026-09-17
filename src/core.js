import fs from "node:fs/promises";
import path from "node:path";

export const NAV_START = "<!-- readme-translate-kr-en:start -->";
export const NAV_END = "<!-- readme-translate-kr-en:end -->";

export function languageNav() {
  return `${NAV_START}
<p align="right">
  <a href="./README.md">English</a> · <a href="./README.ko.md">한국어</a>
</p>
${NAV_END}`;
}

export function stripLanguageNav(markdown) {
  const pattern = new RegExp(
    `${escapeRegExp(NAV_START)}[\\s\\S]*?${escapeRegExp(NAV_END)}\\n?`,
    "g",
  );

  return markdown.replace(pattern, "").replace(/^\s+/, "");
}

export function withLanguageNav(markdown) {
  return `${languageNav()}\n\n${stripLanguageNav(markdown).trimStart()}`;
}

export function detectDirection(changedFiles = []) {
  const en = changedFiles.includes("README.md");
  const ko = changedFiles.includes("README.ko.md");

  if (en && !ko) return "en-to-ko";
  if (ko && !en) return "ko-to-en";

  return "en-to-ko";
}

export async function readUtf8(file) {
  return fs.readFile(file, "utf8");
}

export async function writeUtf8(file, contents) {
  await fs.mkdir(path.dirname(file), { recursive: true });
  await fs.writeFile(
    file,
    contents.endsWith("\n") ? contents : `${contents}\n`,
    "utf8",
  );
}

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}
