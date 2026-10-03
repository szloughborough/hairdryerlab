"""核验 site/dist 已完整暂存：不能漏掉 _astro 下的 CSS/JS，否则线上是无样式页面。"""
import os
import subprocess
from collections import Counter

tracked = set(subprocess.run(['git', 'ls-files', 'site/dist'],
                             capture_output=True, text=True,
                             encoding='utf-8', errors='replace').stdout.splitlines())

on_disk = []
for dp, dn, fn in os.walk('site/dist'):
    for f in fn:
        on_disk.append(os.path.join(dp, f).replace('\\', '/'))

missing = sorted(set(on_disk) - tracked)
extra = sorted(tracked - set(on_disk))

print(f'磁盘上 dist 文件: {len(on_disk)}')
print(f'已暂存 dist 文件: {len(tracked)}')
print()

if missing:
    print(f'✗ 未暂存 {len(missing)} 个文件：')
    for m in missing:
        print(f'   {m}')
else:
    print('OK 磁盘上的 dist 文件已全部暂存')

if extra:
    print(f'（暂存区有 {len(extra)} 个磁盘上不存在的条目，多为删除记录）')

print()
print('=== 按类型统计（已暂存）===')
c = Counter()
for t in tracked:
    ext = os.path.splitext(t)[1] or '(无扩展名)'
    c[ext] += 1
for k, v in c.most_common():
    print(f'   {k:<14} {v}')

print()
print('=== 关键资源是否在其中 ===')
KEY = [
    'site/dist/index.html',
    'site/dist/404.html',
    'site/dist/llms.txt',
    'site/dist/robots.txt',
    'site/dist/sitemap-index.xml',
    'site/dist/site.webmanifest',
    'site/dist/fonts/manrope-variable-latin.woff2',
    'site/dist/fonts/inter-variable-latin.woff2',
]
for k in KEY:
    print(f'   {"OK " if k in tracked else "缺失"}  {k}')

css = [t for t in tracked if t.endswith('.css')]
js = [t for t in tracked if t.endswith('.js')]
print(f'   {"OK " if css else "**缺失**"}  _astro/*.css  共 {len(css)} 个')
print(f'   {"OK " if js else "（无 JS，本站不需要）"}  _astro/*.js   共 {len(js)} 个')
for f in css[:4]:
    print(f'        {f}')
