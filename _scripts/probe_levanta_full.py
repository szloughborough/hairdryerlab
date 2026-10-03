"""
用完整目录（不设 40 页上限）核对注册表里全部 ASIN，并对 access=true 的尝试建链。
输出: analysis/_levanta_full_check.txt
"""
import io
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sync_affiliate_links as S  # noqa: E402

S.load_env()

OUT = 'analysis/_levanta_full_check.txt'
lines = []
def P(*a): lines.append(' '.join(str(x) for x in a))

# 我们的注册表
reg = S.parse_registry()
P('=' * 104)
P('Levanta 全目录核对（不设 40 页上限）')
P('=' * 104)
P(f'  注册表 token 数: {len(reg)}')
P('')

provider = S.Levanta()
creds = provider.credentials()
base, hdrs = provider._base(), provider._headers(creds)
marketplace = provider._marketplace()

want = {r['asin']: r for r in reg}

# 完整分页
index = {}
cursor, page = '', 0
while True:
    params = {'marketplace': marketplace, 'limit': 500}
    if cursor:
        params['cursor'] = cursor
    status, payload = S.http_json('GET', '%s/products' % base, headers=hdrs, params=params)
    if not isinstance(payload, dict):
        break
    prods = payload.get('products') or []
    for p in prods:
        pid = p.get('primaryId')
        if not pid:
            continue
        for ident in (p.get('ids') or []):
            if ident.get('label') == 'ASIN' and ident.get('value') in want:
                index.setdefault(ident['value'], {
                    'primaryId': pid,
                    'access': bool(p.get('access')),
                    'marketplace': p.get('marketplace') or marketplace,
                    'brandName': p.get('brandName') or '',
                    'page': page + 1,
                })
    page += 1
    cursor = payload.get('cursor') or ''
    if page % 20 == 0:
        print(f'  {page} 页 / 命中 {len(index)}', file=sys.stderr)
    if not cursor or not prods:
        break

P(f'  目录共 {page} 页')
P(f'  注册表中出现在 Levanta 目录里的 ASIN: {len(index)}/{len(want)}')
P('')
P(f"{'ASIN':<13}{'access':<8}{'页':<5}{'品牌':<24}{'token'}")
P('-' * 104)
for asin in sorted(index):
    h = index[asin]
    P(f"{asin:<13}{str(h['access']):<8}{h['page']:<5}{h['brandName'][:22]:<24}{want[asin]['token']}")
P('')

missing = sorted(set(want) - set(index))
P(f'不在 Levanta 目录的: {len(missing)} 个')
for a in missing:
    P(f'   {a}  {want[a]["token"]}')
P('')

# 对 access=true 的尝试建链
P('=' * 104)
P('尝试建链（access=true 的）')
P('=' * 104)
ok, fail = {}, []
for asin in sorted(index):
    h = index[asin]
    if not h['access']:
        fail.append((asin, 'access=false'))
        continue
    try:
        resp = provider._create_link(creds, h['primaryId'], h['marketplace'])
        url = resp.get('url') or resp.get('mobileOptimizedUrl')
        if url:
            ok[asin] = {'url': url, 'token': want[asin]['token'], 'brand': h['brandName']}
            P(f"  ✓ {asin}  {want[asin]['token']}")
            P(f"      {url[:120]}")
        else:
            fail.append((asin, 'no url in response: %s' % json.dumps(resp)[:120]))
    except S.HttpError as e:
        fail.append((asin, str(e)[:150]))

P('')
P(f'建链成功 {len(ok)} 条，失败 {len(fail)} 条')
for a, why in fail:
    P(f'  ✗ {a}  {why}')

io.open(OUT, 'w', encoding='utf-8').write('\n'.join(lines))
io.open('analysis/_levanta_new_links.json', 'w', encoding='utf-8').write(
    json.dumps(ok, ensure_ascii=False, indent=1))
print(f'written {OUT}')
print(f'written analysis/_levanta_new_links.json  ({len(ok)} links)')
