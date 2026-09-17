import test from 'node:test';
import assert from 'node:assert/strict';
import { detectDirection, stripLanguageNav, withLanguageNav } from '../src/core.js';

test('adds language navigation exactly once', () => {
  const once = withLanguageNav('# Hello\n');
  const twice = withLanguageNav(once);
  assert.equal(once, twice);
  assert.match(once, /README\.ko\.md/);
});

test('strips generated language navigation', () => {
  assert.equal(stripLanguageNav(withLanguageNav('# Hello\n')), '# Hello\n');
});

test('detects changed source README', () => {
  assert.equal(detectDirection(['README.ko.md']), 'ko-to-en');
  assert.equal(detectDirection(['README.md']), 'en-to-ko');
  assert.equal(detectDirection(['README.md', 'README.ko.md']), 'en-to-ko');
});
