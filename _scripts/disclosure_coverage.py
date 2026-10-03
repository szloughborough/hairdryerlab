"""核实：含联盟链接的页面是否都渲染了联盟披露。"""
import glob
import io
import os
import re

D = 'site/dist'
out = []
def P(*a): out.append(' '.join(str(x) for x in a))

DISCLOSURE = r'may earn a commission when you buy through our links'

P('=' * 96)
P('联盟披露覆盖核验（有外链 = 必须有披露）')
P('=' * 96)
P(f"{'页面':<46}{'联盟外链':>9}{'披露':>7}")
P('-' * 96)
missing = []
rows = []
for p in sorted(glob.glob(f'{D}/**/*.html', recursive=True)):
    h = io.open(p, encoding='utf-8').read()
    rel = os.path.relpath(p, D).replace(os.sep, '/').replace('/index.html', '/')
    if rel == 'index.html':
        rel = '/'
    links = len(re.findall(r'rel="[^"]*sponsored', h))
    has_disc = bool(re.search(DISCLOSURE, h, re.I))
    rows.append((rel, links, has_disc))
    if links and not has_disc:
        missing.append((rel, links))

for rel, links, disc in sorted(rows, key=lambda x: (-x[1], x[0])):
    if links or not disc:
        P(f'{rel:<46}{links:>9}{"✓" if disc else "✗ 缺失":>7}')

P('')
P('=' * 96)
if missing:
    P(f'⚠ 有联盟外链但无披露的页面：{len(missing)} 个')
    for rel, n in missing:
        P(f'   {rel}   （{n} 条外链）')
else:
    P('✓ 所有含联盟外链的页面都渲染了披露')
P('=' * 96)

io.open('analysis/_disclosure_coverage.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written analysis/_disclosure_coverage.txt')
