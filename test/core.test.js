import test from 'node:test';
import assert from 'node:assert/strict';
import {
  detectContentLanguage,
  detectDirection,
  getAutomaticSourcePath,
  getAutomaticTargetPath,
  stripLanguageNav,
  withLanguageNav,
} from '../src/core.js';

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

test('detects content language without counting HTML comments', () => {
  const markdown = `<!--
  This English example is intentionally long and must be ignored.
  Another English sentence inside the comment must also be ignored.
  -->
  ## 소개
  안녕하세요. 한국어로 작성한 프로젝트입니다.
  `;

  assert.equal(detectContentLanguage(markdown), 'ko');
});

test('uses word counts for mixed Korean technical content', () => {
  const markdown = `
  ## Experience
  - 경희대학교 소프트웨어융합대학 학생회 미디어홍보팀장
  - 경희대학교 데이터분석 AI 동아리 참여
  - 대학생 IT 연합 동아리 University MakeUs Challenge 활동
  - KIST Europe AI Convergence Internship 수료
  `;

  assert.equal(detectContentLanguage(markdown), 'ko');
});

test('keeps an English README with a Korean language link as English', () => {
  const markdown = `
  [한국어](./README.ko.md)
  # Project
  A fast command-line tool for translating project documentation.
  `;

  assert.equal(detectContentLanguage(markdown), 'en');
});

test('does not count image and badge alt text as document language', () => {
  const markdown = `
  ![Build Status Documentation Coverage](https://img.shields.io/badge/build-passing-green)
  ![Developer Tool Platform](./project-logo.svg)
  ## 소개
  한국어 프로젝트입니다.
  `;

  assert.equal(detectContentLanguage(markdown), 'ko');
});

test('uses the opposite standard README as an automatic target', () => {
  assert.equal(getAutomaticTargetPath('README.md', 'en'), 'README.ko.md');
  assert.equal(getAutomaticTargetPath('README.ko.md', 'ko'), 'README.md');
  assert.equal(getAutomaticTargetPath('README.en.md', 'en'), 'README.md');
});

test('selects one changed standard README as the automatic source', () => {
  assert.equal(getAutomaticSourcePath(['README.ko.md']), 'README.ko.md');
  assert.equal(
    getAutomaticSourcePath(['docs/README.en.md']),
    'docs/README.en.md',
  );
  assert.equal(getAutomaticSourcePath(['src/core.js']), 'README.md');
  assert.throws(
    () => getAutomaticSourcePath(['README.md', 'README.ko.md']),
    /Multiple README files changed/,
  );
});
