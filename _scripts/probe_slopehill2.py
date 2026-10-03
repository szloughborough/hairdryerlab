"""从已拉取的 Levanta 目录里精确查 slopehill，并核对 ASIN。"""
import io
import json
import re
from collections import Counter

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

P('=' * 104)
P(f'Levanta 目录总计 {len(prods):,} 个商品')
P('=' * 104)
P('')

# 所有品牌名里含 "slope" 的
slope = [p for p in prods if 'slope' in brand_of(p).lower()]
P(f'=== 品牌名含 "slope" 的商品：{len(slope)} 个 ===')
bc = Counter(brand_of(p) for p in slope)
for b, n in bc.most_common():
    P(f'   {n:>4} 个   {b}')
P('')
P(f"{'ASIN':<13}{'access':<8}{'primaryId':<40}{'品牌':<24}{'标题'}")
P('-' * 104)
slope_asins = set()
for p in slope:
    a = asin_of(p) or '(无)'
    slope_asins.add(a)
    title = (p.get('title') or p.get('name') or '')[:34]
    P(f"{a:<13}{str(p.get('access')):<8}{(p.get('primaryId') or '')[:38]:<40}{brand_of(p):<24}{title}")
P('')

# 我们销量最好的 3 个 ASIN 是否在目录中（不管品牌）
OURS = {
    'B0C3M9WBQF': 'Slopehill 1902 Ionic       C$42.99  4.5*  22,195 评  8,660/月  BSR #1',
    'B08HRQG2M6': 'Slopehill Brushless       C$79.99  4.6*   6,087 评    835/月  BSR #11',
    'B0CY4QMMBH': 'Slopehill Ionic+Diffuser  C$99.99  4.6*   1,809 评    557/月  BSR #12',
}
by_asin = {}
for p in prods:
    a = asin_of(p)
    if a:
        by_asin.setdefault(a, p)

P('=' * 104)
P('=== 结论：我们销量最好的 3 个 slopehill ASIN 在 Levanta 里的状态 ===')
P('=' * 104)
for a, desc in OURS.items():
    p = by_asin.get(a)
    if p:
        P(f'  ✓ {a}  在 Levanta 目录中')
        P(f'      品牌={brand_of(p)}   access={p.get("access")}   primaryId={p.get("primaryId")}')
        P(f'      我们数据：{desc}')
    else:
        P(f'  ✗ {a}  不在 Levanta 目录中')
        P(f'      我们数据：{desc}')
    P('')

# 飞利浦式核对：Levanta 目录里有没有别的 slopehill ASIN 是我们没在卖的
P('=' * 104)
P('=== Levanta 里的 slopehill ASIN vs 我们数据集里的 slopehill ASIN ===')
P('=' * 104)
OUR_ASINS = set(OURS.keys())
P(f'  Levanta 目录中有 {len(slope_asins & OUR_ASINS)} 个与我们的 ASIN 重合')
P(f'  我们未覆盖的 slopehill ASIN：{sorted(slope_asins - OUR_ASINS)}')
P(f'  我们覆盖但 Levanta 没有的：{sorted(OUR_ASINS - slope_asins)}')
P('')

# access=True 的 slopehill 商品（即可推广的）
acc = [p for p in slope if p.get('access')]
P(f'=== 其中可推广（access=true）的：{len(acc)} 个 ===')
for p in acc[:20]:
    P(f"   {asin_of(p)}   {brand_of(p)}   {(p.get('title') or '')[:40]}")

io.open('analysis/_levanta_slopehill2.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written analysis/_levanta_slopehill2.txt')
