"""确认首页 5 个 ASIN 在 PRODUCT_IMAGES 里都有图；并检查 .pick-card-media 的 CSS。"""
import io
import re

out = []
def W(*a): out.append(' '.join(str(x) for x in a))

# --- 1) products.ts 里的图片映射 ---
ts = io.open('site/src/data/products.ts', encoding='utf-8').read()
# PRODUCT_IMAGES 块
m = re.search(r'PRODUCT_IMAGES[^=]*=\s*\{(.*?)\n\};', ts, re.S)
block = m.group(1) if m else ''
asins_with_img = set(re.findall(r'["\']?(B0[A-Z0-9]{8})["\']?\s*:', block))
W('=' * 88)
W(f'PRODUCT_IMAGES 中的 ASIN: {len(asins_with_img)} 个')
W('=' * 88)

HOME = [
    ('Laifen Air', 'B0GWHF4SHD'),
    ('Laifen SE2', 'B0FPMBBG2J'),
    ('Dreame Pocket Pro', 'B0F8QH8XHV'),
    ('Slopehill 1902', 'B0C3M9WBQF'),
    ('Wavytalk 1875W', 'B09JZ18GLJ'),
]
W('首页 5 张卡片:')
missing = []
for name, asin in HOME:
    ok = asin in asins_with_img
    W(f'   {"OK " if ok else "缺失"}  {name:<20} {asin}')
    if not ok:
        missing.append((name, asin))

# 也看看 image 字段是否真的有 URL
W('')
W('这些 ASIN 的 image URL:')
for name, asin in HOME:
    mm = re.search(asin + r'["\']?\s*:\s*\{(.*?)\}', block, re.S)
    if mm:
        u = re.search(r'image:\s*[\'"]([^\'"]+)', mm.group(1))
        W(f'   {name:<20} {u.group(1)[:88] if u else "(无 image 字段)"}')
    else:
        W(f'   {name:<20} (不在 PRODUCT_IMAGES 中)')

# --- 2) CSS ---
css = io.open('site/src/styles/global.css', encoding='utf-8').read()
W('')
W('=' * 88)
W('.pick-card / .pick-card-media 的 CSS')
W('=' * 88)
for b in re.findall(r'(?s)([^{}]*\{[^{}]*\})', css):
    if re.search(r'\.pick-card|\.picks-grid', b):
        W('   ' + re.sub(r'\s+', ' ', b.strip()))

# --- 3) 对比：ProductPick 组件是怎么渲染图片的 ---
W('')
W('=' * 88)
W('对照：ProductPick.astro 的媒体区写法（它有图）')
W('=' * 88)
pp = io.open('site/src/components/ProductPick.astro', encoding='utf-8').read()
i = pp.find('pick-media')
W(pp[i - 40:i + 420] if i >= 0 else '(未找到)')

io.open('analysis/_home_card_images.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written analysis/_home_card_images.txt')
