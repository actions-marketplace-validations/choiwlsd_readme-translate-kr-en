import { execFileSync } from 'node:child_process';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));

function getPythonCommand() {
  if (process.env.PYTHON) {
    return process.env.PYTHON;
  }

  return process.platform === 'win32' ? 'python' : 'python3';
}

export async function translateMarkdownLocal({ markdown, direction }) {
  const dir = await fs.mkdtemp(
    path.join(os.tmpdir(), 'readme-bilingual-')
  );

  const input = path.join(dir, 'input.md');
  const output = path.join(dir, 'output.md');

  await fs.writeFile(input, markdown, 'utf8');

  try {
    execFileSync(getPythonCommand(), [
      path.join(here, 'local_translate.py'),
      '--direction',
      direction,
      '--input',
      input,
      '--output',
      output,
    ], {
      stdio: 'inherit',
    });

    return await fs.readFile(output, 'utf8');
  } finally {
    await fs.rm(dir, {
      recursive: true,
      force: true,
    });
  }
}