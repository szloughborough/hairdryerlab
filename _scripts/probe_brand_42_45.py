"""提取品牌文档 §42–§45 的页面结构要求，并与《内容结构标准.md》对照。"""
import io
import re

brand = io.open('deliverables/品牌规范-HairDryerLab-v1.0.md', encoding='utf-8').read()
site = io.open('site/src/data/site.ts', encoding='utf-8').read()
out = []
def P(*a): out.append(' '.join(str(x) for x in a))

for n in ('41', '42', '43', '44', '45'):
    m = re.search(r'(?m)^#{1,4}\s*§?' + n + r'[.、\s]', brand)
    if not m:
        P(f'§{n}: 未定位')
        continue
    nxt = re.search(r'(?m)^#{1,4}\s*§?\d{1,3}[.、\s]', brand[m.end():])
    end = m.end() + nxt.start() if nxt else min(len(brand), m.start() + 2000)
    P('=' * 92)
    P(brand[m.start():end].strip()[:1500])
    P('')

P('=' * 92)
P('页脚链接目标')
P('=' * 92)
for name in ('FOOTER_MAIN', 'FOOTER_COMPANY', 'NAV'):
    m = re.search(name + r'[^=]*=\s*\[(.*?)\];', site, re.S)
    if not m:
        P(f'{name}: 未找到')
        continue
    P(f'{name}:')
    for href, label in re.findall(r"href:\s*'([^']+)',\s*label:\s*'([^']+)'", m.group(1)):
        P(f'   {label:<34} {href}')
    if 'label' not in m.group(1):
        for label, href in re.findall(r"label:\s*'([^']+)',\s*href:\s*'([^']+)'", m.group(1)):
            P(f'   {label:<34} {href}')
    P('')

io.open('analysis/_brand_42_45.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written analysis/_brand_42_45.txt')
