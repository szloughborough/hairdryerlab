"""验证首页 5 个 ASIN 是否都在 PRODUCTS 中且有 image URL。"""
import io
import re

ts = io.open('site/src/data/products.ts', encoding='utf-8').read()
m = re.search(r'export const PRODUCTS[^=]*=\s*\{(.*?)\n\};', ts, re.S)
block = m.group(1) if m else ''
keys = set(re.findall(r'(?m)^\s{2}(B0[A-Z0-9]{8}):\s*\{', block))

out = []
def W(*a): out.append(' '.join(str(x) for x in a))

W(f'PRODUCTS 中的 ASIN 数: {len(keys)}')
W('')

HOME = [
    ('Laifen Air', 'B0GWHF4SHD'),
    ('Laifen SE2', 'B0FPMBBG2J'),
    ('Dreame Pocket Pro', 'B0F8QH8XHV'),
    ('Slopehill 1902', 'B0C3M9WBQF'),
    ('Wavytalk 1875W', 'B09JZ18GLJ'),
]
missing = []
W('首页 5 张卡片:')
for name, asin in HOME:
    if asin not in keys:
        W(f'   MISSING  {name:<20} {asin}')
        missing.append(name)
        continue
    mm = re.search(r'(?m)^\s{2}' + asin + r':\s*\{(.*?)\n\s{2}\},', block, re.S)
    img = re.search(r"image:\s*'([^']+)'", mm.group(1)) if mm else None
    alt = re.search(r"imageAlt:\s*'([^']+)'", mm.group(1)) if mm else None
    W(f'   OK       {name:<20} {asin}')
    W(f'            image: {(img.group(1)[:78] if img else "(无)")}')
    W(f'            alt  : {(alt.group(1)[:60] if alt else "(无)")}')

W('')
W(f'结论: {"全部存在，可直接渲染" if not missing else "缺失 " + str(missing)}')

W('')
W('=' * 84)
W('所有 PRODUCTS 的 image 域名分布')
W('=' * 84)
from collections import Counter
c = Counter(re.findall(r"image:\s*'https?://([^/]+)", block))
for k, v in c.most_common():
    W(f'   {k:<40} {v}')

io.open('analysis/_home_asins.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('\n'.join(out))
