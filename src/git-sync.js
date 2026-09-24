#!/usr/bin/env node

import { execFileSync, spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const DEFAULT_COMMIT_MESSAGE = 'docs: sync bilingual README';

export function commitAndPush({
  files,
  baseSha,
  branch,
  cwd = process.cwd(),
  remote = 'origin',
  commitMessage = DEFAULT_COMMIT_MESSAGE,
  maxPushAttempts = 3,
  log = console.log,
}) {
  const paths = [...new Set(files.filter(Boolean))];

  if (paths.length === 0) {
    throw new Error('No translated README paths were provided.');
  }

  if (!baseSha) throw new Error('The pre-translation commit SHA is required.');
  if (!branch) throw new Error('A branch name is required to push changes.');

  const status = git(['status', '--porcelain', '--', ...paths], { cwd });

  if (!status.trim()) {
    log('No README changes to commit.');
    return { status: 'no-changes' };
  }

  git(['config', 'user.name', 'github-actions[bot]'], { cwd });
  git([
    'config',
    'user.email',
    '41898282+github-actions[bot]@users.noreply.github.com',
  ], { cwd });
  git(['add', '--', ...paths], { cwd });
  git(['commit', '-m', commitMessage], { cwd, stdio: 'inherit' });

  let lastPushError = '';

  for (let attempt = 1; attempt <= maxPushAttempts; attempt += 1) {
    fetchBranch(remote, branch, cwd);
    const remoteRef = `refs/remotes/${remote}/${branch}`;
    const remoteSha = git(['rev-parse', remoteRef], { cwd }).trim();

    if (remoteSha !== baseSha) {
      const readmeChanged = gitStatus(
        ['diff', '--quiet', baseSha, remoteSha, '--', ...paths],
        cwd,
      );

      if (readmeChanged === 1) {
        log('README changed on the remote while translation was running.');
        log('Skipping this stale translation; a newer workflow run will handle it.');
        return { status: 'stale', remoteSha };
      }

      if (readmeChanged !== 0) {
        throw new Error('Could not compare the translated README with the remote branch.');
      }

      const remoteIsAncestor = gitStatus(
        ['merge-base', '--is-ancestor', remoteSha, 'HEAD'],
        cwd,
      );

      if (remoteIsAncestor === 1) {
        log(`Rebasing translated README onto ${remote}/${branch}.`);
        git(['rebase', remoteRef], { cwd, stdio: 'inherit' });
      } else if (remoteIsAncestor !== 0) {
        throw new Error('Could not determine the relationship to the remote branch.');
      }
    }

    const push = spawnSync(
      'git',
      ['push', remote, `HEAD:${branch}`],
      { cwd, encoding: 'utf8' },
    );

    if (push.status === 0) {
      if (push.stdout) process.stdout.write(push.stdout);
      if (push.stderr) process.stderr.write(push.stderr);
      return { status: 'pushed' };
    }

    lastPushError = [push.stdout, push.stderr].filter(Boolean).join('\n').trim();

    fetchBranch(remote, branch, cwd);
    const updatedRemoteSha = git(['rev-parse', remoteRef], { cwd }).trim();

    if (updatedRemoteSha === remoteSha) {
      throw new Error(
        `Git push failed without a new remote commit. Check contents: write permission and branch protection.\n${lastPushError}`,
      );
    }

    log(`Remote branch advanced during push; retrying (${attempt}/${maxPushAttempts}).`);
  }

  throw new Error(
    `Git push was rejected ${maxPushAttempts} times because the remote kept changing.\n${lastPushError}`,
  );
}

function fetchBranch(remote, branch, cwd) {
  git(
    [
      'fetch',
      '--no-tags',
      remote,
      `refs/heads/${branch}:refs/remotes/${remote}/${branch}`,
    ],
    { cwd, stdio: 'inherit' },
  );
}

function git(args, { cwd, stdio = ['ignore', 'pipe', 'pipe'] }) {
  return execFileSync('git', args, { cwd, encoding: 'utf8', stdio });
}

function gitStatus(args, cwd) {
  return spawnSync('git', args, { cwd, stdio: 'ignore' }).status;
}

function parseArgs(items) {
  const values = { files: [] };

  for (let index = 0; index < items.length; index += 1) {
    const item = items[index];

    if (item === '--file') {
      values.files.push(items[++index]);
    } else if (item.startsWith('--')) {
      values[item.slice(2)] = items[++index];
    }
  }

  return values;
}

const isMain = process.argv[1]
  && fileURLToPath(import.meta.url) === process.argv[1];

if (isMain) {
  const flags = parseArgs(process.argv.slice(2));

  try {
    commitAndPush({
      files: flags.files,
      baseSha: flags['base-sha'],
      branch: flags.branch,
      commitMessage: flags['commit-message'] ?? DEFAULT_COMMIT_MESSAGE,
    });
  } catch (error) {
    console.error(error.message);
    process.exitCode = 1;
  }
}
