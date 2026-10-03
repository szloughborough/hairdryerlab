"""核验方案 B 的转换质量。"""
import io
import os
import re
from collections import Counter

D = 'deliverables/drafts'
out = []
def P(*a): out.append(' '.join(str(x) for x in a))

files = [f for f in sorted(os.listdir(D)) if f.endswith('.mdx')]

# 1. 残留的带小数价格
resid = []
for fn in files:
    t = io.open(os.path.join(D, fn), encoding='utf-8').read()
    for m in re.findall(r'C\$\d+\.\d{2}', t):
        resid.append((fn, m))
P(f'1) 仍带小数的商品价格残留: {len(resid)} 处')
for fn, m in resid[:10]:
    P(f'     {fn}: {m}')

# 2. 所有 C$ 写法分布
c = Counter()
for fn in files:
    t = io.open(os.path.join(D, fn), encoding='utf-8').read()
    for m in re.findall(r'about C\$[\d,]+|C\$[\d,]+', t):
        c[m] += 1
P('')
P('2) C$ 写法分布（前 24）:')
for k, v in c.most_common(24):
    tag = '  ← 价格带阈值（保持精确）' if not k.startswith('about') and ',' not in k and int(k[2:]) in (20,25,30,40,45,50,100,120,150,200,250,300,400,500,600,700) else ''
    P(f'     {k:<16} {v:>4}{tag}')

# 3. 重复修饰词
dups = 0
for fn in files:
    t = io.open(os.path.join(D, fn), encoding='utf-8').read()
    dups += len(re.findall(r'\babout about\b|\b(roughly|approximately|around) about\b', t))
P('')
P(f'3) 重复修饰词: {dups} 处')

# 4. 表格表头
hdr = Counter()
for fn in files:
    t = io.open(os.path.join(D, fn), encoding='utf-8').read()
    hdr['**Price (approx.)**'] += t.count('**Price (approx.)**')
    hdr['**Price (CAD)**'] += t.count('**Price (CAD)**')
P('')
P(f'4) 表头: Price (approx.)={hdr["**Price (approx.)**"]}  Price (CAD)={hdr["**Price (CAD)**"]}')

# 5. 抽一段正文看可读性
t = io.open(os.path.join(D, 'under-150.mdx'), encoding='utf-8').read()
body = t.split('---', 2)[-1]
P('')
P('5) 正文抽样（under-150）:')
for line in body.splitlines():
    s = line.strip()
    if s.startswith('**Our pick') or s.startswith('| **Laifen Air Diffuser**') or 'about C$' in s and len(s) < 200:
        P('     ' + s[:170])
        if len([x for x in out if x.startswith('     5')]) > 0 and out[-1].count('about C$') > 0:
            pass

io.open('analysis/_planb_check.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written analysis/_planb_check.txt')
