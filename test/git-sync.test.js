import test from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { mkdtempSync, readFileSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { commitAndPush } from '../src/git-sync.js';

function git(cwd, ...args) {
  return execFileSync('git', args, {
    cwd,
    encoding: 'utf8',
    stdio: ['ignore', 'pipe', 'pipe'],
  }).trim();
}

function configure(cwd) {
  git(cwd, 'config', 'user.name', 'Test User');
  git(cwd, 'config', 'user.email', 'test@example.com');
}

function createRepositories() {
  const root = mkdtempSync(path.join(tmpdir(), 'readme-git-sync-'));
  const remote = path.join(root, 'remote.git');
  const seed = path.join(root, 'seed');
  const worker = path.join(root, 'worker');
  const competitor = path.join(root, 'competitor');

  git(root, 'init', '--bare', remote);
  git(root, 'init', seed);
  configure(seed);
  git(seed, 'checkout', '-b', 'main');
  writeFileSync(path.join(seed, 'README.md'), '# Original\n');
  writeFileSync(path.join(seed, 'notes.txt'), 'original\n');
  git(seed, 'add', '.');
  git(seed, 'commit', '-m', 'initial');
  git(seed, 'remote', 'add', 'origin', remote);
  git(seed, 'push', '-u', 'origin', 'main');
  git(root, '--git-dir', remote, 'symbolic-ref', 'HEAD', 'refs/heads/main');
  git(root, 'clone', remote, worker);
  git(root, 'clone', remote, competitor);
  configure(worker);
  configure(competitor);

  return { remote, worker, competitor };
}

test('rebases and pushes when only unrelated remote files changed', () => {
  const { worker, competitor } = createRepositories();
  const baseSha = git(worker, 'rev-parse', 'HEAD');

  writeFileSync(path.join(worker, 'README.ko.md'), '# 번역\n');
  writeFileSync(path.join(competitor, 'notes.txt'), 'changed remotely\n');
  git(competitor, 'add', 'notes.txt');
  git(competitor, 'commit', '-m', 'update notes');
  git(competitor, 'push', 'origin', 'main');

  const result = commitAndPush({
    files: ['README.md', 'README.ko.md'],
    baseSha,
    branch: 'main',
    cwd: worker,
    log: () => {},
  });

  assert.equal(result.status, 'pushed');
  assert.equal(git(worker, 'rev-list', '--count', 'HEAD'), '3');
  assert.equal(
    readFileSync(path.join(worker, 'notes.txt'), 'utf8').replace(/\r\n/g, '\n'),
    'changed remotely\n',
  );
});

test('skips a stale translation when the remote README changed', () => {
  const { worker, competitor } = createRepositories();
  const baseSha = git(worker, 'rev-parse', 'HEAD');

  writeFileSync(path.join(worker, 'README.ko.md'), '# 오래된 번역\n');
  writeFileSync(path.join(competitor, 'README.md'), '# New source\n');
  git(competitor, 'add', 'README.md');
  git(competitor, 'commit', '-m', 'update source README');
  git(competitor, 'push', 'origin', 'main');

  const result = commitAndPush({
    files: ['README.md', 'README.ko.md'],
    baseSha,
    branch: 'main',
    cwd: worker,
    log: () => {},
  });

  assert.equal(result.status, 'stale');
  assert.equal(git(worker, 'rev-parse', 'origin/main'), git(competitor, 'rev-parse', 'HEAD'));
});

test('does not create a commit when translation changed no files', () => {
  const { worker } = createRepositories();
  const baseSha = git(worker, 'rev-parse', 'HEAD');

  const result = commitAndPush({
    files: ['README.md'],
    baseSha,
    branch: 'main',
    cwd: worker,
    log: () => {},
  });

  assert.equal(result.status, 'no-changes');
  assert.equal(git(worker, 'rev-parse', 'HEAD'), baseSha);
});
