import fs from "node:fs/promises";
import path from "node:path";

export const NAV_START = "<!-- readme-translate-kr-en:start -->";
export const NAV_END = "<!-- readme-translate-kr-en:end -->";

export function languageNav(currentFile, englishFile, koreanFile) {
  const englishLink = relativeLink(currentFile, englishFile);
  const koreanLink = relativeLink(currentFile, koreanFile);

  return `${NAV_START}
<p align="right">
  <sub>
    🌐 Language&nbsp;&nbsp;
    <a href="${englishLink}">English</a>
    &nbsp;|&nbsp;
    <a href="${koreanLink}">한국어</a>
  </sub>
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

export function withLanguageNav(
  markdown,
  currentFile = "README.md",
  englishFile = "README.md",
  koreanFile = "README.ko.md",
) {
  return `${languageNav(
    currentFile,
    englishFile,
    koreanFile,
  )}\n\n${stripLanguageNav(markdown).trimStart()}`;
}

export function detectDirection(changedFiles = []) {
  const en = changedFiles.includes("README.md");
  const ko = changedFiles.includes("README.ko.md");

  if (en && !ko) return "en-to-ko";
  if (ko && !en) return "ko-to-en";

  return "en-to-ko";
}

export function detectContentLanguage(markdown) {
  const text = stripNonLanguageContent(markdown);

  const koreanChars =
    (text.match(/[가-힣]/g) ?? []).length;

  const englishChars =
    (text.match(/[A-Za-z]/g) ?? []).length;

  if (koreanChars === 0 && englishChars === 0) {
    throw new Error(
      "Could not detect README language. Use --from en or --from ko.",
    );
  }

  return koreanChars > englishChars
    ? "ko"
    : "en";
}

export function stripNonLanguageContent(markdown) {
  return markdown
    .replace(/<!--[\s\S]*?-->/g, " ")
    .replace(/```[\s\S]*?```/g, " ")
    .replace(/~~~[\s\S]*?~~~/g, " ")
    .replace(/`[^`]*`/g, " ")
    .replace(/https?:\/\/\S+/g, " ")
    .replace(/<[^>]+>/g, " ")
    .replace(/!\[[^\]]*\]\([^)]+\)/g, " ")
    .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1");
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

function relativeLink(fromFile, toFile) {
  const fromDir = path.dirname(fromFile);

  let relative = path.relative(fromDir, toFile).replace(/\\/g, "/");

  if (!relative.startsWith(".")) {
    relative = `./${relative}`;
  }

  return relative;
}

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

export function getAutomaticTargetPath(sourcePath, from) {
  const suffix = from === "en" ? ".ko" : ".en";
  const oppositeSuffix = from === "en" ? ".en" : ".ko";
  const parsed = path.parse(sourcePath);

  if (parsed.ext.toLowerCase() !== ".md") {
    return `${sourcePath}${suffix}`;
  }

  if (parsed.name.endsWith(oppositeSuffix)) {
    return path.join(
      parsed.dir,
      `${parsed.name.slice(0, -oppositeSuffix.length)}${parsed.ext}`,
    );
  }

  return path.join(parsed.dir, `${parsed.name}${suffix}${parsed.ext}`);
}

export function getAutomaticSourcePath(changedFiles = []) {
  const changedReadmes = changedFiles.filter((file) =>
    /(^|\/)README(?:\.(?:en|ko))?\.md$/i.test(file),
  );

  if (changedReadmes.length === 0) return "README.md";

  if (changedReadmes.length > 1) {
    throw new Error(
      "Multiple README files changed in the latest commit. Use --from and --source explicitly.",
    );
  }

  return changedReadmes[0];
}
