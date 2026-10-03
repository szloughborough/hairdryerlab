#!/usr/bin/env node
/**
 * 一条命令完成「同步草稿 → 构建 → 暂存产物」。
 *
 * 为什么需要它
 *   Cloudflare 在零构建配置下直接部署**已提交的** site/dist（见根目录
 *   wrangler.jsonc 顶部说明）。每次改内容后必须重新构建并提交，否则线上是旧内容。
 *
 * 用法
 *     node _scripts/deploy_prepare.mjs
 *     git commit -m "content: ..." && git push
 *
 * ── 为什么调用 sync_content.py 而不是在 JS 里重写 ─────────────────────────
 * 曾经在 JS 里重新实现过一遍同步逻辑，结果漏掉了原脚本的 5 条规则
 * （跳过 draft:true、按 slug 命名、删除正文 H1、把 HTML 注释转成 MDX 注释写法、
 * 先清空旧文件），直接把一篇含 HTML 注释的草稿同步进站点，构建报
 *   [@mdx-js/rollup] Unexpected character `!` ...
 * 同步规则只有一处真源：_scripts/sync_content.py。找不到 Python 时**大声失败**，
 * 绝不静默降级 —— 静默降级正是上次出错的根因。
 */
import { execFileSync, execSync } from 'node:child_process';
import { existsSync } from 'node:fs';
import path from 'node:path';

const root = path.resolve(import.meta.dirname, '..');
const site = path.join(root, 'site');

function run(cmd, args, cwd) {
  process.stdout.write(`\n$ ${cmd} ${args.join(' ')}\n`);
  execFileSync(cmd, args, { cwd, stdio: 'inherit' });
}

/** 找可用的 Python。支持 HDL_PYTHON 覆盖（受限环境里 Python 可能不在 PATH 上）。 */
function findPython() {
  const candidates = [process.env.HDL_PYTHON, 'python', 'python3', 'py'].filter(Boolean);
  for (const c of candidates) {
    try {
      execSync(`"${c}" --version`, { stdio: 'ignore' });
      return c;
    } catch {
      /* 试下一个 */
    }
  }
  return null;
}

/** pnpm 可能不在 PATH 上；按可靠性依次回退。 */
function buildWith(cmd, args) {
  try {
    execSync(`"${cmd}" --version`, { stdio: 'ignore' });
  } catch {
    return false;
  }
  run(cmd, args, site);
  return true;
}

// ---------- 1) 草稿 → 内容集合 ----------
const py = findPython();
if (!py) {
  console.error(
    '\n✗ 找不到 Python。\n' +
      '  同步草稿的唯一真源是 _scripts/sync_content.py，本脚本不再自带实现\n' +
      '  （曾经自带过，漏了 5 条规则并导致构建失败）。\n' +
      '  请安装 Python，或用 HDL_PYTHON 指定解释器路径，例如：\n' +
      '      HDL_PYTHON=/path/to/python node _scripts/deploy_prepare.mjs\n',
  );
  process.exit(1);
}
run(py, [path.join(root, '_scripts', 'sync_content.py')], root);

// 校验同步确实产出了内容（防止「静默什么都没做」）
const contentDir = path.join(site, 'src', 'content');
if (!existsSync(contentDir)) {
  console.error('\n✗ 同步后 site/src/content 不存在，中止。\n');
  process.exit(1);
}

// ---------- 2) 构建 ----------
let built = buildWith('pnpm', ['build']);
if (!built) {
  console.warn('  (pnpm 不可用，尝试 npx)');
  built = buildWith('npx', ['--yes', 'pnpm@11.7.0', 'build']);
}
if (!built) {
  console.warn('  (pnpm / npx 都不可用，直接用 astro 兜底)');
  run(process.execPath, [path.join(site, 'node_modules', 'astro', 'astro.js'), 'build'], site);
}

// 校验构建产出
if (!existsSync(path.join(site, 'dist', 'index.html'))) {
  console.error('\n✗ 构建后 site/dist/index.html 不存在，中止（不要提交空产物）。\n');
  process.exit(1);
}

// ---------- 3) 暂存产物 ----------
// -f 是必需的：site/dist 曾被 .gitignore 排除，需要强制加入
run('git', ['add', '-f', 'site/dist'], root);
run('git', ['add', '-A'], root);

console.log('\n完成。site/dist 已暂存 —— 提交并推送即部署。');
