#!/usr/bin/env node
import { execFileSync } from 'node:child_process';
import { detectDirection, readUtf8, stripLanguageNav, withLanguageNav, writeUtf8 } from './core.js';
import { translateMarkdownLocal } from './local.js';

const args = process.argv.slice(2);
const command = args[0] ?? 'help';
const flags = parseFlags(args.slice(1));

if (command === 'help' || flags.help) {
  printHelp();
  process.exit(0);
}

if (command === 'init') {
  await init();
  process.exit(0);
}

if (command === 'sync') {
  await sync(flags);
  process.exit(0);
}

console.error(`Unknown command: ${command}`);
printHelp();
process.exit(1);

async function init() {
  const enPath = 'README.md';
  const koPath = 'README.ko.md';
  const en = await readUtf8(enPath).catch(() => '# Project\n');
  await writeUtf8(enPath, withLanguageNav(en));

  try {
    await readUtf8(koPath);
  } catch {
    await writeUtf8(koPath, `${withLanguageNav('# 프로젝트')}\n\n> Run \`readme-bilingual sync --from en\` to generate this translation.\n`);
  }

  console.log('Initialized README.md and README.ko.md language navigation.');
}

async function sync(flags) {
  const direction = resolveDirection(flags.from);
  const source = direction === 'en-to-ko' ? 'README.md' : 'README.ko.md';
  const target = direction === 'en-to-ko' ? 'README.ko.md' : 'README.md';
  const sourceLanguage = direction === 'en-to-ko' ? 'English' : 'Korean';
  const targetLanguage = direction === 'en-to-ko' ? 'Korean' : 'English';

  const markdown = stripLanguageNav(await readUtf8(source));
  console.log(`Translating ${source} -> ${target} locally (${sourceLanguage} -> ${targetLanguage})...`);

  const translated = await translateMarkdownLocal({ markdown, direction });

  await writeUtf8(source, withLanguageNav(markdown));
  await writeUtf8(target, withLanguageNav(translated));
  console.log(`Updated ${target}.`);
}

function resolveDirection(from) {
  if (from === 'en') return 'en-to-ko';
  if (from === 'ko') return 'ko-to-en';
  if (from) throw new Error('--from must be en or ko.');

  let changed = [];
  try {
    const output = execFileSync('git', ['diff', '--name-only', 'HEAD^', 'HEAD'], { encoding: 'utf8' });
    changed = output.split(/\r?\n/).filter(Boolean);
  } catch {
    // First commit, shallow checkout, or non-git directory: default to English source.
  }
  return detectDirection(changed);
}

function parseFlags(items) {
  const out = {};
  for (let i = 0; i < items.length; i++) {
    const item = items[i];
    if (item === '--help' || item === '-h') out.help = true;
    else if (item.startsWith('--')) {
      const [key, inline] = item.slice(2).split('=', 2);
      if (inline !== undefined) out[key] = inline;
      else out[key] = items[++i];
    }
  }
  return out;
}

function printHelp() {
  console.log(`readme-bilingual\n\nUsage:\n  readme-bilingual init\n  readme-bilingual sync [--from en|ko]\n\nRequirements:\n  Python 3 + dependencies from requirements.txt\n`);
}
