"""本轮三个任务的最终综合验证。"""
import glob
import io
import os
import re
from collections import Counter

D = 'site/dist'
STYLE = re.compile(r'(?s)<style[^>]*>.*?</style>')
out = []
def W(*a): out.append(' '.join(str(x) for x in a))

pages = glob.glob(f'{D}/**/*.html', recursive=True)
def dom(p):
    return STYLE.sub(' ', io.open(p, encoding='utf-8').read())

W('=' * 94)
W('任务 1：§55 组件库落地情况')
W('=' * 94)
COMPONENTS = {
    '1 Header': (r'class="site-header"', 'used'),
    '2 Footer': (r'class="site-footer"', 'used'),
    '3 Breadcrumb': (r'class="breadcrumbs"', 'used'),
    '4 Product Hero': (None, 'missing'),
    '5 Lab Test Card': (r'class="lab-test"', 'used'),
    '6 Best For / Skip If': (r'class="verdict-split"', 'used'),
    '7 Quick Verdict': (r'class="lede"', 'used'),
    '8 Pros / Cons': (r'class="proscons"', 'used'),
    '9 Comparison Table': (None, 'missing'),
    '10 Product Card': (r'class="pick"', 'used'),
    '11 Affiliate CTA': (r'class="cta"', 'used'),
    '12 Price Box': (r'class="price-box"', 'used'),
    '13 Disclosure Box': (r'class="disclosure"', 'used'),
    '14 Methodology Box': (None, 'missing'),
    '15 Tested Badge': (r'class="tested-badge"', 'used'),
    '16 Hair-Type Card': (None, 'missing'),
    '17 Feature Card': (None, 'missing'),
    '18 Related Content': (None, 'missing'),
    '19 Author Box': (None, 'missing'),
    '20 Update Date': (r'Updated 20', 'used'),
    '21 FAQ': (r'class="faq"', 'used'),
    '22 Newsletter': (None, 'missing'),
    '23 Image caption': (None, 'missing'),
    '24 Evidence / source note': (r'class="ev ', 'used'),
}
used = orphan = missing = 0
for name, (pat, state) in COMPONENTS.items():
    if state == 'missing':
        W(f'   ✗ 未建      {name}')
        missing += 1
        continue
    n = sum(len(re.findall(pat, dom(p))) for p in pages)
    if n:
        W(f'   ✓ 已上线    {name:<26} {n:>5} 处')
        used += 1
    else:
        W(f'   ⚠ 建了未用  {name}')
        orphan += 1
W('')
W(f'   合计：已上线 {used} / 建了未用 {orphan} / 未建 {missing}    （总计 {used+orphan+missing}，品牌规范要求 24）')

W('')
W('=' * 94)
W('交付质量核验')
W('=' * 94)
checks = {}
leak = sum(len(re.findall(r'%7B%7B|\{\{affiliate', dom(p))) for p in pages)
dead = sum(len(set(re.findall(r'href="#([A-Z0-9]{10})"', dom(p))) -
               set(re.findall(r'id="([A-Z0-9]{10})"', dom(p)))) for p in pages)
exact_price = sum(len(re.findall(r'C\$\d+\.\d{2}', dom(p))) for p in pages)
disc_missing = 0
for p in pages:
    h = dom(p)
    if re.search(r'rel="[^"]*sponsored', h) and not re.search(
            r'may earn a commission when you buy through our links', h, re.I):
        disc_missing += 1
charset_bad = sum(len(re.findall(r'â€|Ã[\x80-\xbf]', dom(p))) for p in pages)

W(f'   占位符泄漏                        {leak}   （应为 0）')
W(f'   断裂锚点                          {dead}   （应为 0）')
W(f'   精确价格残留 C$XX.XX              {exact_price}   （应为 0，方案 B）')
W(f'   有外链但缺披露的页面              {disc_missing}   （应为 0）')
W(f'   产物中的乱码特征                  {charset_bad}   （应为 0）')

io.open('analysis/_round_final.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written analysis/_round_final.txt')
