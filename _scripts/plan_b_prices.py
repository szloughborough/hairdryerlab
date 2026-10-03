"""
方案 B：把商品精确价格改为约数，保住论证、去掉「精确当前价」表述。

规则（关键设计）：
  · 只改**带小数点**的价格 → 那是商品零售价（C$99.99）
  · 整数价格不动 → 那是价格带阈值与分析口径（C$50 / C$120 / C$150）
  · 四舍五入：<100 取整；100–299 取 5；300+ 取 10
  · 表格表头 "Price (CAD)" → "Price (approx.)"
这样 4× 价差、9.6% vs 30.3% 按价格带划分等核心论证全部保留。
"""
import io
import os
import re

DRAFTS = 'deliverables/drafts'

PRICE_RE = re.compile(r'C\$(\d+)\.(\d{2})')


def approx(n: float) -> int:
    if n < 100:
        return int(round(n))
    if n < 300:
        return int(round(n / 5.0) * 5)
    return int(round(n / 10.0) * 10)


total = 0
per_file = {}
for fn in sorted(os.listdir(DRAFTS)):
    if not fn.endswith('.mdx'):
        continue
    p = os.path.join(DRAFTS, fn)
    t = io.open(p, encoding='utf-8').read()
    orig = t
    n = 0

    def sub(m):
        global n
        n += 1
        return 'about C$%d' % approx(float(m.group(1) + '.' + m.group(2)))

    t = PRICE_RE.sub(sub, t)
    # 表头
    t = t.replace('**Price (CAD)**', '**Price (approx.)**')
    t = t.replace('| Price (CAD) |', '| Price (approx.) |')
    t = t.replace('Price (CAD)', 'Price (approx.)')

    # 修饰词去重：避免出现 "about about" 或 "roughly about"
    t = re.sub(r'\babout about\b', 'about', t)
    t = re.sub(r'\b(roughly|approximately|around) about\b', r'\1', t)

    if t != orig:
        io.open(p, 'w', encoding='utf-8').write(t)
        per_file[fn] = n
        total += n

print(f'改为约数的价格：{total} 处，涉及 {len(per_file)} 个文件')
print()
print('改动最多的 12 个文件：')
for fn, n in sorted(per_file.items(), key=lambda x: -x[1])[:12]:
    print(f'   {fn:<46} {n:>4} 处')
print()
print('未改动的文件（无带小数价格）：')
for fn in sorted(os.listdir(DRAFTS)):
    if fn.endswith('.mdx') and fn not in per_file:
        print(f'   {fn}')
