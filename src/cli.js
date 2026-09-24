#!/usr/bin/env node

import {
  detectContentLanguage,
  getAutomaticSourcePath,
  getAutomaticTargetPath,
  readUtf8,
  stripLanguageNav,
  withLanguageNav,
  writeUtf8,
} from './core.js';

import { execFileSync } from 'node:child_process';
import { appendFileSync } from 'node:fs';
import {
  translateMarkdownIncrementalLocal,
  translateMarkdownLocal,
} from './local.js';

const DEFAULT_STATE_FILE = '.readme-translate-state.json';
const BOT_EMAIL = '41898282+github-actions[bot]@users.noreply.github.com';

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

  const statePath = flags['state-file'] ?? DEFAULT_STATE_FILE;
  const state = await readTranslationState(statePath);
  const stateKey = JSON.stringify([source, target]);
  const currentTarget = await readUtf8(target)
    .then(stripLanguageNav)
    .catch(() => null);
  const baseline = validBaseline(
    state.translations[stateKey],
    direction,
  ) ?? previousBotBaseline(source, target, direction);

  console.log(`Source: ${source}`);
  console.log(`Detected language: ${from}`);
  console.log(`Target: ${target}`);
  console.log(
    `Translating locally (${sourceLanguage} -> ${targetLanguage})...`,
  );

  let translated;
  let generated;

  if (currentTarget !== null && baseline) {
    console.log('Preserving translations for unchanged Markdown elements...');
    ({ translated, generated } = await translateMarkdownIncrementalLocal({
      markdown: sourceMarkdown,
      currentTarget,
      previousSource: baseline.sourceMarkdown,
      previousGenerated: baseline.generatedMarkdown,
      direction,
    }));
  } else {
    translated = await translateMarkdownLocal({
      markdown: sourceMarkdown,
      direction,
    });
    generated = translated;
  }

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

  state.translations[stateKey] = {
    source,
    target,
    direction,
    sourceMarkdown,
    generatedMarkdown: generated,
  };
  await writeUtf8(statePath, `${JSON.stringify(state, null, 2)}\n`);

  writeGitHubOutput('source-file', source);
  writeGitHubOutput('target-file', target);
  writeGitHubOutput('state-file', statePath);

  console.log(`Updated ${target}.`);
}

async function readTranslationState(statePath) {
  try {
    const parsed = JSON.parse(await readUtf8(statePath));

    if (parsed?.version === 1 && parsed.translations) {
      return parsed;
    }
  } catch {
    // A missing or invalid state file starts a new translation state.
  }

  return { version: 1, translations: {} };
}

function validBaseline(entry, direction) {
  if (
    entry?.direction === direction
    && typeof entry.sourceMarkdown === 'string'
    && typeof entry.generatedMarkdown === 'string'
  ) {
    return entry;
  }

  return null;
}

function previousBotBaseline(source, target, direction) {
  try {
    const history = execFileSync(
      'git',
      ['log', '--format=%H%x09%ae', '--', target],
      { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] },
    );

    for (const line of history.split(/\r?\n/)) {
      const [commit, email] = line.split('\t');

      if (!commit || email !== BOT_EMAIL) continue;

      const sourceMarkdown = stripLanguageNav(
        execFileSync(
          'git',
          ['show', `${commit}:${gitPath(source)}`],
          { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] },
        ),
      );
      const generatedMarkdown = stripLanguageNav(
        execFileSync(
          'git',
          ['show', `${commit}:${gitPath(target)}`],
          { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] },
        ),
      );

      console.log(`Recovered incremental translation state from ${commit.slice(0, 7)}.`);
      return { direction, sourceMarkdown, generatedMarkdown };
    }
  } catch {
    // Git history is only a migration fallback for pre-state releases.
  }

  return null;
}

function gitPath(file) {
  return file.replaceAll('\\', '/');
}

function writeGitHubOutput(name, value) {
  const outputFile = process.env.GITHUB_OUTPUT;

  if (!outputFile) return;

  if (value.includes('\n') || value.includes('\r')) {
    throw new Error(`Cannot write a multiline ${name} path to GITHUB_OUTPUT.`);
  }

  appendFileSync(outputFile, `${name}=${value}\n`, 'utf8');
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
  --state-file <file> Incremental translation state file.
                      Default: .readme-translate-state.json
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
