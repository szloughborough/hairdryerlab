"""
让部署在「零 Cloudflare 构建配置」下可用。

背景
    Cloudflare Workers Builds 的构件设置（Root directory / Build command）在
    Dashboard 里不容易定位，导致部署反复失败。本脚本改为把构建产物直接提交，
    让默认的 `npx wrangler deploy` 就能部署成功 —— 不需要任何 Dashboard 配置。

本脚本做三件事
    1. 调整 .gitignore：不再忽略 site/dist（删除根与 site 下的 dist/ 规则）
    2. 生成 _scripts/deploy_prepare.mjs：一条命令「构建 + 暂存产物」
    3. 校验根 wrangler.jsonc 与 site/wrangler.jsonc 的 name 一致
"""
import io
import json
import os
import re

out = []
def W(*a): out.append(' '.join(str(x) for x in a))

# ---------- 1) .gitignore ----------
W('=' * 88)
W('1) .gitignore 调整')
W('=' * 88)

root_gi = '.gitignore'
t = io.open(root_gi, encoding='utf-8').read()
if re.search(r'(?m)^dist/$', t):
    t = re.sub(r'(?m)^dist/$',
               '# dist/ 不再全局忽略：site/dist 需要提交，理由见 wrangler.jsonc 顶部说明。\n'
               '# 只忽略可能在仓库根出现的构建目录。\n/dist/',
               t)
    io.open(root_gi, 'w', encoding='utf-8', newline='\n').write(t)
    W('   根 .gitignore: dist/ → /dist/（仅根级）')
else:
    W('   根 .gitignore: 无需改动')

site_gi = 'site/.gitignore'
t2 = io.open(site_gi, encoding='utf-8').read()
if re.search(r'(?m)^dist/$', t2):
    t2 = re.sub(r'(?m)^dist/$',
                '# dist/ 刻意不忽略：Cloudflare 在零构建配置下直接部署已提交的产物。\n'
                '# 内容改动后运行 `node _scripts/deploy_prepare.mjs` 重新构建并暂存。\n'
                '# dist/',
                t2)
    io.open(site_gi, 'w', encoding='utf-8', newline='\n').write(t2)
    W('   site/.gitignore: dist/ 已注释掉')
else:
    W('   site/.gitignore: 无需改动')

# ---------- 2) deploy_prepare.mjs ----------
W('')
W('=' * 88)
W('2) 生成 _scripts/deploy_prepare.mjs')
W('=' * 88)

MJS = '''#!/usr/bin/env node
/**
 * 一条命令完成「同步草稿 → 构建 → 暂存产物」。
 *
 * 为什么需要它：Cloudflare 在零构建配置下直接部署已提交的 site/dist，
 * 所以每次改内容后都必须重新构建并提交，否则线上是旧内容。
 *
 * 用法：
 *     node _scripts/deploy_prepare.mjs
 *     git commit -m "content: ..." && git push
 */
import { execFileSync } from 'node:child_process';
import { existsSync, readdirSync } from 'node:fs';
import path from 'node:path';

const root = path.resolve(import.meta.dirname, '..');
const site = path.join(root, 'site');

function run(cmd, args, cwd) {
  process.stdout.write(`\\n$ ${cmd} ${args.join(' ')}\\n`);
  execFileSync(cmd, args, { cwd, stdio: 'inherit' });
}

// 1) 草稿 → 内容集合（纯 Node 重写 sync_content.py 的核心逻辑）
const DRAFTS = path.join(root, 'deliverables', 'drafts');
const MAP = {
  best: 'best', review: 'review', compare: 'compare',
  for: 'for', learn: 'learn', ca: 'ca',
};
// 与 _scripts/sync_content.py 保持一致：按 frontmatter type 决定目标集合
function collectionOf(text) {
  const m = /^type:\\s*["']?([a-z]+)/m.exec(text);
  const type = m ? m[1] : 'learn';
  return MAP[type] ? type : 'learn';
}

let synced = 0;
if (existsSync(DRAFTS)) {
  const { readFileSync, writeFileSync, mkdirSync } = await import('node:fs');
  for (const f of readdirSync(DRAFTS)) {
    if (!f.endsWith('.mdx')) continue;
    const text = readFileSync(path.join(DRAFTS, f), 'utf8');
    const dir = path.join(site, 'src', 'content', collectionOf(text));
    mkdirSync(dir, { recursive: true });
    writeFileSync(path.join(dir, f), text);
    synced += 1;
  }
}
console.log(`\\nsynced ${synced} draft(s) into site/src/content/`);

// 2) 构建
run('pnpm', ['build'], site);

// 3) 暂存产物
run('git', ['add', '-f', 'site/dist'], root);
run('git', ['add', '-A'], root);
console.log('\\nDone. site/dist is staged — commit and push to deploy.');
'''
io.open('_scripts/deploy_prepare.mjs', 'w', encoding='utf-8', newline='\n').write(MJS)
W('   已生成 _scripts/deploy_prepare.mjs')

# ---------- 3) 校验两个 wrangler.jsonc 的 name ----------
W('')
W('=' * 88)
W('3) 两个 wrangler.jsonc 的一致性校验')
W('=' * 88)

def load_jsonc(p):
    s = io.open(p, encoding='utf-8').read()
    s = re.sub(r'(?m)^\s*//.*$', '', s)
    s = re.sub(r',(\s*[}\]])', r'\1', s)
    return json.loads(s)

names = {}
for p in ('wrangler.jsonc', 'site/wrangler.jsonc'):
    if os.path.exists(p):
        d = load_jsonc(p)
        names[p] = d['name']
        W(f'   {p:<24} name={d["name"]:<16} assets={d["assets"]["directory"]}')
    else:
        W(f'   {p:<24} 不存在')

if len(set(names.values())) == 1:
    W('   → name 一致 OK')
else:
    W('   → **name 不一致，需修正**')

io.open('analysis/_deploy_root_setup.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written analysis/_deploy_root_setup.txt')
