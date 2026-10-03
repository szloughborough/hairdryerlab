"""
全站设计一致性最终核验 —— 纯 ASCII 输出，避免控制台编码干扰判断。
"""
import glob
import io
import re

css_src = io.open('site/src/styles/global.css', encoding='utf-8').read()
css_nc = re.sub(r'/\*.*?\*/', '', css_src, flags=re.S)
pages = glob.glob('site/dist/**/*.html', recursive=True)
# Windows 上 glob 返回反斜杠，键统一规范成正斜杠，否则按路径查找会全部落空
html = {p.replace('\\', '/'): io.open(p, encoding='utf-8').read() for p in pages}

lines = []
def W(*a): lines.append(' '.join(str(x) for x in a))

def chk(label, ok):
    W(f'   [{"PASS" if ok else "FAIL"}]  {label}')

W('=' * 88)
W('1. Dead / stale selectors removed')
W('=' * 88)
for sel in ('.toc h2', '.footer-cols h3', '.pillar-card', '.pillar-grid'):
    chk(f'selector removed: {sel}', sel not in css_nc)
chk('new selector .toc__title present', '.toc__title' in css_nc)
chk('new selector .footer-col__title present', '.footer-col__title' in css_nc)

W('')
W('=' * 88)
W('2. Heading scale (brand spec 17)')
W('=' * 88)
chk('h1 48px', bool(re.search(r'\bh1 \{ font-size: 48px', css_nc)))
chk('h2 34px', bool(re.search(r'\bh2 \{ font-size: 34px', css_nc)))
chk('h3 24px', bool(re.search(r'\bh3 \{ font-size: 24px', css_nc)))
BAD = []
for b in re.findall(r'(?s)([^{}]*\{[^{}]*\})', css_nc):
    sel, body = b.split('{', 1)
    m = re.search(r'font-size:\s*([\d.]+)px', body)
    if not m:
        continue
    size = float(m.group(1))
    if re.search(r'\bh2\b', sel) and size < 26:
        BAD.append((sel.strip(), size))
    if re.search(r'\bh3\b', sel) and size < 21:
        BAD.append((sel.strip(), size))
chk('no h2/h3 styled below the scale', not BAD)
for sel, size in BAD:
    W(f'          off-scale: {sel} = {size}px')

W('')
W('=' * 88)
W('3. Unified card system')
W('=' * 88)
chk('picks-grid 3 cols (matches homepage .models)',
    bool(re.search(r'\.picks-grid \{[^}]*repeat\(3, minmax\(0, 1fr\)\)', css_nc)))
chk('picks h2 = 34px (real heading)', bool(re.search(r'\.picks > h2 \{[^}]*font-size: 34px', css_nc)))
chk('pick-card title 20px', bool(re.search(r'\.pick-card-body strong \{[^}]*font-size: 20px', css_nc)))
chk('pick-body h3 = 24px', bool(re.search(r'\.pick-body h3 \{[^}]*font-size: 24px', css_nc)))
chk('proscons h3 = 24px', bool(re.search(r'\.proscons h3 \{[^}]*font-size: 24px', css_nc)))
chk('authorbox uses 2px navy rule (matches homepage trust)',
    bool(re.search(r'\.authorbox \{[^}]*border-top: 2px solid var\(--hdl-navy\)', css_nc)))

W('')
W('=' * 88)
W('4. Integrity: false "Tested" claim')
W('=' * 88)
fake = sum(1 for h in html.values() if 'badge badge--tested' in h)
data = sum(1 for h in html.values() if 'badge badge--data' in h)
contra = sum(1 for h in html.values() if 'Tested Not yet' in h)
mislbl = sum(1 for h in html.values() if 'Product source: Analysis' in h)
chk(f'no page shows a "Tested" badge (was 43/45, now {fake})', fake == 0)
chk(f'"Figures checked" badge present on {data} pages', data > 0)
chk(f'self-contradictory string gone ({contra})', contra == 0)
chk(f'mislabeled "Product source" gone ({mislbl})', mislbl == 0)

W('')
W('=' * 88)
W('5. Heading outline per page type')
W('=' * 88)
for p in ('site/dist/index.html', 'site/dist/reviews/laifen/index.html',
          'site/dist/best-hair-dryers/index.html', 'site/dist/how-we-test/index.html'):
    h = html.get(p, '')
    n1 = len(re.findall(r'<h1[ >]', h))
    n2 = len(re.findall(r'<h2[ >]', h))
    n3 = len(re.findall(r'<h3[ >]', h))
    ok = n1 == 1
    W(f'   [{"PASS" if ok else "FAIL"}]  {p.replace("site/dist","")}  h1={n1} h2={n2} h3={n3}')

W('')
W('   TOC no longer injects an h2:')
for p in ('site/dist/reviews/laifen/index.html', 'site/dist/best-hair-dryers/index.html'):
    h = html.get(p, '')
    has = 'toc__title' in h
    injected = bool(re.search(r'<h2[^>]*>On this page</h2>', h))
    W(f'      {"PASS" if has and not injected else "FAIL"}  {p.replace("site/dist","")}')
    W(f'              .toc__title present={has}  h2 "On this page" injected={injected}')

W('')
W('   Footer no longer uses h3 for link-group labels:')
for p in ('site/dist/index.html', 'site/dist/reviews/laifen/index.html'):
    h = html.get(p, '')
    bad = bool(re.search(r'<h3>(Navigation|Company|Disclosure)</h3>', h))
    good = 'footer-col__title' in h
    W(f'      {"PASS" if good and not bad else "FAIL"}  {p.replace("site/dist","")}')
    W(f'              footer-col__title={good}  h3 labels still present={bad}')

W('')
W('=' * 88)
W('6. Regression')
W('=' * 88)
W(f'   pages built: {len(pages)}')
W(f'   pages with images: {sum(1 for h in html.values() if "<img" in h)}')

io.open('analysis/_consistency_final.txt', 'w', encoding='utf-8').write('\n'.join(lines))
print('\n'.join(lines))
