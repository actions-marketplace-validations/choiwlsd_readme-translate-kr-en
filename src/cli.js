import {
  getAutomaticSourcePath,
  getAutomaticTargetPath,
  readUtf8,
  stripLanguageNav,
  withLanguageNav,
  writeUtf8,
} from './core.js';

import { execFileSync } from 'node:child_process';
import { translateMarkdownLocal } from './local.js';

const args = process.argv.slice(2);
const command = args[0] ?? 'help';
const flags = parseFlags(args.slice(1));

if (command === 'help' || flags.help) {
  printHelp();
  process.exit(0);
}

if (command === 'init') {
  await init(flags);
  process.exit(0);
}

if (command === 'sync') {
  await sync(flags);
  process.exit(0);
}

console.error(`Unknown command: ${command}`);
printHelp();
process.exit(1);

async function init(flags) {
  const sourcePath = flags.source ?? 'README.md';

  const markdown = await readUtf8(sourcePath).catch(() => '# Project\n');
  const cleanMarkdown = stripLanguageNav(markdown);

  const language = flags.from ?? detectContentLanguage(cleanMarkdown);
  validateLanguage(language);

  const targetPath =
    flags.target ?? getAutomaticTargetPath(sourcePath, language);

  const englishPath =
    language === 'en'
      ? sourcePath
      : targetPath;

  const koreanPath =
    language === 'ko'
      ? sourcePath
      : targetPath;

  await writeUtf8(
    sourcePath,
    withLanguageNav(
      cleanMarkdown,
      sourcePath,
      englishPath,
      koreanPath,
    ),
  );

  try {
    const target = await readUtf8(targetPath);

    await writeUtf8(
      targetPath,
      withLanguageNav(
        stripLanguageNav(target),
        targetPath,
        englishPath,
        koreanPath,
      ),
    );
  } catch {
    const placeholder =
      language === 'en'
        ? '# 프로젝트\n'
        : '# Project\n';

    await writeUtf8(
      targetPath,
      withLanguageNav(
        placeholder,
        targetPath,
        englishPath,
        koreanPath,
      ),
    );
  }

  console.log(`Initialized ${sourcePath} and ${targetPath}.`);
}

async function sync(flags) {
  const source = resolveSourcePath(flags);

  const sourceMarkdown =
    stripLanguageNav(await readUtf8(source));

  const from = flags.from ?? detectContentLanguage(sourceMarkdown);

  validateLanguage(from);

  const direction =
    from === 'en'
      ? 'en-to-ko'
      : 'ko-to-en';

  const target =
    flags.target ?? getAutomaticTargetPath(source, from);

  const englishPath =
    from === 'en'
      ? source
      : target;

  const koreanPath =
    from === 'ko'
      ? source
      : target;

  const sourceLanguage =
    from === 'en'
      ? 'English'
      : 'Korean';

  const targetLanguage =
    from === 'en'
      ? 'Korean'
      : 'English';

  console.log(`Source: ${source}`);
  console.log(`Detected language: ${from}`);
  console.log(`Target: ${target}`);
  console.log(
    `Translating locally (${sourceLanguage} -> ${targetLanguage})...`,
  );

  const translated = await translateMarkdownLocal({
    markdown: sourceMarkdown,
    direction,
  });

  await writeUtf8(
    source,
    withLanguageNav(
      sourceMarkdown,
      source,
      englishPath,
      koreanPath,
    ),
  );

  await writeUtf8(
    target,
    withLanguageNav(
      translated,
      target,
      englishPath,
      koreanPath,
    ),
  );

  console.log(`Updated ${target}.`);
}

function resolveSourcePath(flags) {
  if (flags.source || flags.from) {
    return flags.source ?? 'README.md';
  }

  return getAutomaticSourcePath(latestChangedFiles());
}

function latestChangedFiles() {
  try {
    return execFileSync(
      'git',
      ['diff', '--name-only', 'HEAD^', 'HEAD'],
      { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] },
    )
      .split(/\r?\n/)
      .filter(Boolean);
  } catch {
    return [];
  }
}

function detectContentLanguage(markdown) {
  const text = stripNonLanguageContent(markdown);

  const koreanChars =
    (text.match(/[가-힣]/g) ?? []).length;

  const englishChars =
    (text.match(/[A-Za-z]/g) ?? []).length;

  if (koreanChars === 0 && englishChars === 0) {
    throw new Error(
      'Could not detect README language. Use --from en or --from ko.',
    );
  }

  return koreanChars > englishChars
    ? 'ko'
    : 'en';
}

function stripNonLanguageContent(markdown) {
  return markdown
    .replace(/```[\s\S]*?```/g, ' ')
    .replace(/~~~[\s\S]*?~~~/g, ' ')
    .replace(/`[^`]*`/g, ' ')
    .replace(/https?:\/\/\S+/g, ' ')
    .replace(/<[^>]+>/g, ' ')
    .replace(/!\[[^\]]*\]\([^)]+\)/g, ' ')
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1');
}

function validateLanguage(from) {
  if (from !== 'en' && from !== 'ko') {
    throw new Error('--from must be en or ko.');
  }
}

function parseFlags(items) {
  const out = {};

  for (let i = 0; i < items.length; i++) {
    const item = items[i];

    if (item === '--help' || item === '-h') {
      out.help = true;
      continue;
    }

    if (item.startsWith('--')) {
      const [key, inline] =
        item.slice(2).split('=', 2);

      if (inline !== undefined) {
        out[key] = inline;
      } else {
        out[key] = items[++i];
      }
    }
  }

  return out;
}

function printHelp() {
  console.log(`
readme-translate-kr-en

Usage:
  readme-translate-kr-en init [options]
  readme-translate-kr-en sync [options]

Options:
  --from en|ko       Force source language.
  --source <file>    Source Markdown file. Default: README.md.
                     When --source and --from are omitted, use one
                     standard README changed in the latest commit.
  --target <file>    Target Markdown file.
                     If omitted, generated automatically:
                       en -> *.ko.md
                       ko -> *.en.md
  --help, -h         Show help.

Examples:
  readme-translate-kr-en sync
  readme-translate-kr-en sync --from en
  readme-translate-kr-en sync --from ko
  readme-translate-kr-en sync --source README.md
  readme-translate-kr-en sync --source docs/README.md
  readme-translate-kr-en sync --from ko --source README.md --target README.en.md

Requirements:
  Python 3 + dependencies from requirements.txt
`);
}
