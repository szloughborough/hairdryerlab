#!/usr/bin/env node
/**
 * 严格模式构建：未解析的联盟链接占位符 → 直接构建失败。
 *
 * 为什么需要单独一个入口：
 *   平时 `pnpm build` 允许占位符以不可点击的 pending 锚点渲染，方便改版预览；
 *   但上线前必须用这个入口，确保没有坏链混进去。
 *
 * 用法： node _scripts/build-strict.mjs
 */

import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const siteDir = resolve(here, '..', 'site');

const child = spawn(process.execPath, [resolve(siteDir, 'node_modules/astro/astro.js'), 'build'], {
  cwd: siteDir,
  stdio: 'inherit',
  env: { ...process.env, AFFILIATE_STRICT: '1' },
});

child.on('exit', (code) => process.exit(code ?? 1));
