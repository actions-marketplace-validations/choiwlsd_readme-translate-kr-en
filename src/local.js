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

export async function translateMarkdownIncrementalLocal({
  markdown,
  currentTarget,
  previousSource,
  previousGenerated,
  direction,
}) {
  const dir = await fs.mkdtemp(
    path.join(os.tmpdir(), 'readme-bilingual-incremental-')
  );
  const files = {
    input: path.join(dir, 'input.md'),
    output: path.join(dir, 'output.md'),
    currentTarget: path.join(dir, 'current-target.md'),
    previousSource: path.join(dir, 'previous-source.md'),
    previousGenerated: path.join(dir, 'previous-generated.md'),
    generatedOutput: path.join(dir, 'generated-output.md'),
  };

  await Promise.all([
    fs.writeFile(files.input, markdown, 'utf8'),
    fs.writeFile(files.currentTarget, currentTarget, 'utf8'),
    fs.writeFile(files.previousSource, previousSource, 'utf8'),
    fs.writeFile(files.previousGenerated, previousGenerated, 'utf8'),
  ]);

  try {
    execFileSync(getPythonCommand(), [
      path.join(here, 'local_translate.py'),
      '--direction', direction,
      '--input', files.input,
      '--output', files.output,
      '--current-target', files.currentTarget,
      '--previous-source', files.previousSource,
      '--previous-generated', files.previousGenerated,
      '--generated-output', files.generatedOutput,
    ], {
      stdio: 'inherit',
    });

    const [translated, generated] = await Promise.all([
      fs.readFile(files.output, 'utf8'),
      fs.readFile(files.generatedOutput, 'utf8'),
    ]);

    return { translated, generated };
  } finally {
    await fs.rm(dir, {
      recursive: true,
      force: true,
    });
  }
}
