"""最终验证（直接从 dist 产物核验，不依赖预览服务器）。"""
import glob
import io
import re
from collections import Counter

D = 'site/dist'
STYLE = re.compile(r'(?s)<style[^>]*>.*?</style>')
out = []
def W(*a): out.append(' '.join(str(x) for x in a))

pages = glob.glob(f'{D}/**/*.html', recursive=True)
def dom(p):
    return STYLE.sub(' ', io.open(p, encoding='utf-8').read())

W('=' * 96)
W('§55 组件库最终落地（24 项，已用正确的 class 口径）')
W('=' * 96)
SPEC = [
    ('1  Header', r'class="site-header"'),
    ('2  Footer', r'class="site-footer"'),
    ('3  Breadcrumb', r'class="breadcrumbs"'),
    ('4  Product Hero', None),
    ('5  Lab Test Card', r'class="lab-test"'),
    ('6  Best For / Skip If', r'class="verdict-split"'),
    ('7  Quick Verdict', r'class="lede"'),
    ('8  Pros / Cons', r'class="proscons"'),
    ('9  Comparison Table', None),
    ('10 Product Card', r'class="pick"'),
    ('11 Affiliate CTA', r'class="cta"'),
    ('12 Price Box', r'class="price-box"'),
    ('13 Disclosure Box', r'class="disclosure"'),
    ('14 Methodology Box', None),
    ('15 Tested Badge', r'class="badge badge--'),
    ('16 Hair-Type Card', None),
    ('17 Feature Card', None),
    ('18 Related Content', None),
    ('19 Author Box', None),
    ('20 Update Date', r'badge--updated'),
    ('21 FAQ（markdown 渲染，Faq.astro 未用）', r'id="[^"]*faq"'),
    ('22 Newsletter', None),
    ('23 Image caption', None),
    ('24 Evidence / source note', r'class="ev '),
]
used = miss = 0
for name, pat in SPEC:
    if pat is None:
        W(f'   ✗ 未建    {name}')
        miss += 1
        continue
    n = sum(len(re.findall(pat, dom(p), re.I)) for p in pages)
    if n:
        W(f'   ✓ 已上线  {name:<38} {n:>5} 处')
        used += 1
    else:
        W(f'   ⚠ 未渲染  {name}')
        miss += 1
W('')
W(f'   已上线 {used} / 未建或未渲染 {miss}   （品牌规范要求 24 项）')

W('')
W('=' * 96)
W('抽查：/reviews/laifen/ 页面上的组件')
W('=' * 96)
h = dom(f'{D}/reviews/laifen/index.html')
for label, pat in [
    ('Lab Test Card', r'class="lab-test"'), ('Best for / Skip if', r'class="verdict-split"'),
    ('CategoryRatings', r'class="ratings"'), ('Pros / Cons', r'class="proscons"'),
    ('Price Box', r'class="price-box"'), ('Affiliate CTA', r'class="cta"'),
    ('Evidence label', r'class="ev '), ('Tested Badge', r'class="badge badge--'),
]:
    n = len(re.findall(pat, h))
    W(f'   {label:<20} {n:>3} 处  {"✓" if n else "✗"}')

W('')
W('=' * 96)
W('交付质量（全站）')
W('=' * 96)
leak = sum(len(re.findall(r'%7B%7B|\{\{affiliate', dom(p))) for p in pages)
dead = sum(len(set(re.findall(r'href="#([A-Z0-9]{10})"', dom(p))) -
               set(re.findall(r'id="([A-Z0-9]{10})"', dom(p)))) for p in pages)
exact = sum(len(re.findall(r'C\$\d+\.\d{2}', dom(p))) for p in pages)
approx = sum(len(re.findall(r'about C\$\d+', dom(p))) for p in pages)
spon = sum(len(re.findall(r'rel="[^"]*sponsored', dom(p))) for p in pages)
nodisc = 0
for p in pages:
    x = dom(p)
    if re.search(r'rel="[^"]*sponsored', x) and not re.search(
            r'may earn a commission when you buy through our links', x, re.I):
        nodisc += 1
mangle = sum(len(re.findall(r'â€|Ã[\x80-\xbf]|鑱|鍑', dom(p))) for p in pages)
lit = sum(len(re.findall(r'\*\*[A-Za-z]', dom(p))) for p in pages)

W(f'   占位符泄漏                  {leak:>5}   （应 0）')
W(f'   断裂锚点                    {dead:>5}   （应 0）')
W(f'   精确价格 C$XX.XX            {exact:>5}   （应 0，方案 B）')
W(f'   约数价格 about C$X          {approx:>5}')
W(f'   联盟外链（rel=sponsored）   {spon:>5}')
W(f'   有外链但缺披露的页面        {nodisc:>5}   （应 0）')
W(f'   产物乱码特征                {mangle:>5}   （应 0）')
W(f'   字面 markdown 残留 **       {lit:>5}   （应 0）')

io.open('analysis/_round_final2.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written analysis/_round_final2.txt')
