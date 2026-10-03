"""
调查：Levanta 目录里 slopehill-Powerise 的商品，ASIN 是否就是我们销量最好的那几个？

用法: python _scripts/probe_levanta_slopehill.py
输出: analysis/_levanta_slopehill.txt
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sync_affiliate_links as S  # noqa: E402

# sync 脚本的 load_env() 只在 main() 里调用，import 时不会读 .env —— 必须显式调一次
S.load_env()

OUT = 'analysis/_levanta_slopehill.txt'
lines = []


def P(*a):
    lines.append(' '.join(str(x) for x in a))


# 我们数据里销量最好的 3 个 slopehill ASIN
OURS = {
    'B0C3M9WBQF': 'Slopehill 1902 Ionic      C$42.99  4.5*  22,195 评  8,660/月  BSR #1',
    'B08HRQG2M6': 'Slopehill Brushless      C$79.99  4.6*   6,087 评    835/月  BSR #11',
    'B0CY4QMMBH': 'Slopehill Ionic+Diffuser C$99.99  4.6*   1,809 评    557/月  BSR #12',
}

provider = S.Levanta()
creds = provider.credentials()
if not creds:
    P('✗ 没有 LEVANTA_API_KEY，无法查询')
    io.open(OUT, 'w', encoding='utf-8').write('\n'.join(lines))
    sys.exit(1)

base = provider._base()
hdrs = provider._headers(creds)
marketplace = provider._marketplace()

P('=' * 100)
P('Levanta 目录调查 —— slopehill / Powerise')
P('=' * 100)
P(f'  基址: {base}')
P(f'  marketplace: {marketplace}')
P('')

all_products = []
cursor = ''
page = 0
try:
    while True:
        params = {'marketplace': marketplace, 'limit': 500}
        if cursor:
            params['cursor'] = cursor
        status, payload = S.http_json('GET', '%s/products' % base, headers=hdrs, params=params)
        if not isinstance(payload, dict):
            P(f'  ✗ 第 {page+1} 页返回非 JSON: {str(payload)[:200]}')
            break
        prods = payload.get('products') or []
        all_products.extend(prods)
        page += 1
        cursor = payload.get('cursor') or ''
        if page % 10 == 0:
            print(f'  已拉取 {page} 页 / {len(all_products)} 个商品...', file=sys.stderr)
        if not cursor or not prods:
            break
        if page >= 300:
            P(f'  ⚠ 达到 300 页上限，停止（可能未拉完）')
            break
except S.HttpError as e:
    P(f'  ✗ HTTP 错误: {e}')

P(f'  目录总页数: {page}')
P(f'  目录商品总数: {len(all_products):,}')
P('')


def asin_of(p):
    for ident in (p.get('ids') or []):
        if ident.get('label') == 'ASIN':
            return ident.get('value')
    return None


def brand_of(p):
    return (p.get('brandName') or p.get('brand') or '').strip()


# 品牌分布（前 20）
from collections import Counter  # noqa: E402
bc = Counter(brand_of(p) or '(空)' for p in all_products)
P('=== 目录里的品牌分布（前 25）===')
for b, n in bc.most_common(25):
    flag = '   ← 目标' if 'slope' in b.lower() or 'power' in b.lower() else ''
    P(f'   {n:>5} 个商品   {b}{flag}')
P('')

# slopehill / powerise 相关
hits = [p for p in all_products
        if 'slope' in brand_of(p).lower() or 'power' in brand_of(p).lower()]
P('=' * 100)
P(f'=== slopehill / Powerise 相关商品：{len(hits)} 个 ===')
P('=' * 100)
P(f"{'ASIN':<13}{'可推广':<8}{'primaryId':<40}{'品牌':<26}")
P('-' * 100)
hit_asins = set()
for p in sorted(hits, key=lambda x: (asin_of(x) or '')):
    a = asin_of(p) or '(无 ASIN)'
    hit_asins.add(a)
    acc = '✓ 是' if p.get('access') else '✗ 否'
    pid = (p.get('primaryId') or '')[:38]
    P(f'{a:<13}{acc:<8}{pid:<40}{brand_of(p):<26}')
P('')

P('=' * 100)
P('=== 结论：与我们销量最好的 ASIN 对比 ===')
P('=' * 100)
for a, desc in OURS.items():
    in_lev = a in hit_asins
    P(f'  {a}  {"✓ 在 Levanta 目录中" if in_lev else "✗ 不在 Levanta 目录"}' if in_lev
      else f'  {a}  ✗ 不在上面这批里')
    P(f'      {desc}')
P('')

# 对所有匹配到的 ASIN 检查 access
P('=== 这批商品的推广权限明细 ===')
for p in hits:
    a = asin_of(p)
    P(f'  {a}  access={p.get("access")}  brand={brand_of(p)}  '
      f'marketplace={p.get("marketplace")}')
    if p.get('access') is False:
        P(f'      ⚠ 目录里有，但账号 access=False → 无法建链接')

io.open(OUT, 'w', encoding='utf-8').write('\n'.join(lines))

# 同时存原始 JSON 便于深入分析
io.open('analysis/_levanta_products_raw.json', 'w', encoding='utf-8').write(
    json.dumps(all_products, ensure_ascii=False, indent=1))
print(f'written {OUT}')
print(f'written analysis/_levanta_products_raw.json  ({len(all_products)} products)')
