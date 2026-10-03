"""核验方案 B 在构建产物中的落地：精确价格应为 0，约数价格应大量存在。"""
import glob
import io
import re
from collections import Counter

D = 'site/dist'
out = []
def P(*a): out.append(' '.join(str(x) for x in a))

EXACT = re.compile(r'C\$\d+\.\d{2}')
APPROX = re.compile(r'about C\$\d+')

exact = Counter()
exact_pages = set()
approx = 0
approx_pages = set()
allp = glob.glob(f'{D}/**/*.html', recursive=True)

for p in allp:
    h = io.open(p, encoding='utf-8').read()
    for m in EXACT.findall(h):
        exact[m] += 1
        exact_pages.add(p)
    n = len(APPROX.findall(h))
    if n:
        approx += n
        approx_pages.add(p)

P('=' * 80)
P('方案 B 落地核验')
P('=' * 80)
P(f'  页面总数: {len(allp)}')
P(f'  仍含精确价格 (C$XX.XX): {sum(exact.values())} 处，涉及 {len(exact_pages)} 个页面')
if exact:
    P('  残留明细（前 15）:')
    for k, v in exact.most_common(15):
        P(f'     {k:<12} x{v}')
    P('  涉及的页面:')
    for p in sorted(exact_pages)[:15]:
        P(f'     {p}')
P(f'  约数价格 (about C$X): {approx} 处，涉及 {len(approx_pages)} 个页面')

# 抽样确认
P('')
P('=' * 80)
P('抽样：/best-hair-dryers/under-150/ 的价格呈现')
P('=' * 80)
try:
    h = io.open(f'{D}/best-hair-dryers/under-150/index.html', encoding='utf-8').read()
    for m in re.findall(r'about C\$\d+[^<]{0,30}', h)[:8]:
        P('   ' + m)
    P('')
    P('  价格说明句:')
    for m in re.findall(r'[^<>]{0,40}approximate figures[^<>]{0,80}', h)[:3]:
        P('   ' + m.strip())
except Exception as e:
    P(f'   读取失败: {e}')

io.open('analysis/_planb_build_check.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written analysis/_planb_build_check.txt')
