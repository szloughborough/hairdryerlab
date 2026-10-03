"""检查 AffiliateCTA 在产物里的实际渲染，以及是否有残留的旧 CTA 文案。"""
import glob
import io
import re
from collections import Counter

D = 'site/dist'
out = []
def W(*a): out.append(' '.join(str(x) for x in a))

W('=== 产物里的 CTA 形态统计 ===')
c = Counter()
for p in glob.glob(f'{D}/**/*.html', recursive=True):
    h = io.open(p, encoding='utf-8').read()
    c['class="cta-support"'] += len(re.findall(r'class="cta-support"', h))
    c['class="cta"'] += len(re.findall(r'class="cta"', h))
    c['Check current price on Amazon.ca（旧文案）'] += h.count('Check current price on Amazon.ca')
    c['Check price（新文案）'] += len(re.findall(r'>Check price<', h))
    c['at Amazon.ca'] += h.count('at Amazon.ca')
for k, v in c.items():
    W(f'   {k:<44} {v}')

W('')
W('=== 样例：一个 Where to buy 区块的原始 HTML 片段 ===')
h = io.open(f'{D}/reviews/laifen/index.html', encoding='utf-8').read()
i = h.find('where-to-buy')
if i < 0:
    W('   未找到 where-to-buy')
else:
    seg = h[i:i + 4000]
    # 提取 CTA 相关片段
    for m in re.findall(r'<(?:p|a|span)[^>]*(?:cta|sponsored)[^>]*>[^<]{0,60}', seg)[:6]:
        W('   ' + m[:170])

W('')
W('=== ProductPick 区块（pick-body）片段 ===')
j = h.find('class="pick"')
if j < 0:
    W('   未找到 pick')
else:
    W('   ' + re.sub(r'\s+', ' ', h[j:j + 900])[:800])
else_ = None

W('')
W('=== 旧 CTA 文案残留在哪些页面 ===')
left = []
for p in glob.glob(f'{D}/**/*.html', recursive=True):
    h = io.open(p, encoding='utf-8').read()
    n = h.count('Check current price on Amazon.ca')
    if n:
        left.append((p.replace(D + '\\', '').replace(D + '/', ''), n))
if left:
    for p, n in left[:10]:
        W(f'   {p}  x{n}')
else:
    W('   无残留 ✓')

io.open('analysis/_cta_render.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written analysis/_cta_render.txt')
