"""查同一 ASIN 在 Levanta 目录里是否有重复条目、access 值是否冲突。"""
import io
import json
from collections import defaultdict

prods = json.loads(io.open('analysis/_levanta_products_raw.json', encoding='utf-8').read())
out = []
def P(*a): out.append(' '.join(str(x) for x in a))

def asin_of(p):
    for i in (p.get('ids') or []):
        if i.get('label') == 'ASIN':
            return i.get('value')
    return None

def brand_of(p):
    return (p.get('brandName') or p.get('brand') or '').strip()

by_asin = defaultdict(list)
for p in prods:
    a = asin_of(p)
    if a:
        by_asin[a].append(p)

TARGETS = ['B0C3M9WBQF', 'B08HRQG2M6', 'B0CY4QMMBH']
P('=' * 100)
P('目标 ASIN 在 Levanta 目录中的全部条目')
P('=' * 100)
for a in TARGETS:
    entries = by_asin.get(a, [])
    P(f'\n### {a}   —— 共 {len(entries)} 条记录')
    for i, p in enumerate(entries, 1):
        P(f"   [{i}] access={p.get('access')}  brand={brand_of(p)!r}  "
          f"primaryId={p.get('primaryId')}  marketplace={p.get('marketplace')}")
        t = p.get('title') or p.get('name') or ''
        if t:
            P(f"       标题: {t[:80]}")
        # 其余字段
        extra = {k: v for k, v in p.items()
                 if k not in ('ids', 'access', 'brandName', 'primaryId', 'marketplace', 'title', 'name')}
        if extra:
            P(f"       其他字段: {json.dumps(extra, ensure_ascii=False)[:200]}")

P('')
P('=' * 100)
P('统计：目录里有多少 ASIN 出现多次且 access 冲突')
P('=' * 100)
conflict = 0
for a, entries in by_asin.items():
    accs = {e.get('access') for e in entries}
    if len(entries) > 1 and len(accs) > 1:
        conflict += 1
P(f'  重复且 access 冲突的 ASIN 数: {conflict} / {len(by_asin):,}')
P(f'  （若目标 ASIN 在其中，就解释了同步脚本为何判为无权限）')

# 检查目标 ASIN 是否在脚本 40 页上限内
P('')
P('=' * 100)
P('关键：同步脚本 _asin_index 的 40 页上限')
P('=' * 100)
P(f'  目录共 113 页（每页 500）')
P(f'  脚本在第 40 页就 break → 只看过前 ~20,000 个商品')
for a in TARGETS:
    if a in by_asin:
        idx = prods.index(by_asin[a][0])
        page = idx // 500 + 1
        P(f'  {a} 首次出现在第 {page} 页  →  {"在 40 页上限内 ✓" if page <= 40 else "超出 40 页上限 ✗ 脚本根本没见过它"}')

io.open('analysis/_levanta_dupcheck.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written analysis/_levanta_dupcheck.txt')
