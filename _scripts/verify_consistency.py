"""
全站设计语言一致性核验。

重点查两类反复出现的 bug：
  1. 真正的 <h2>/<h3> 被 CSS 渲染成小标签字号（层级塌陷）
  2. <h3> 偏离 §17 规定的 24px
再核对卡片系统与信任区块是否已统一。
"""
import glob
import io
import re

css = io.open('site/src/styles/global.css', encoding='utf-8').read()
pages = glob.glob('site/dist/**/*.html', recursive=True)

out = []
def W(*a): out.append(' '.join(str(x) for x in a))

# ---- 1) CSS 里所有针对 h1/h2/h3 的字号声明 ----
W('=' * 92)
W('CSS 中所有 h1/h2/h3 的字号声明')
W('=' * 92)
OFF = []
for b in re.findall(r'(?s)([^{}]*\{[^{}]*\})', css):
    sel = b.split('{')[0].strip()
    body = b.split('{', 1)[1]
    m = re.search(r'font-size:\s*([\d.]+)px', body)
    if not m:
        continue
    if not re.search(r'\bh[123]\b', sel):
        continue
    size = float(m.group(1))
    W(f'   {sel[:52]:<54} {size}px')
    # 判断是否偏离规范
    if re.search(r'\bh2\b', sel) and size < 26:
        OFF.append((sel, size, 'H2 规范 34px（移动 26–28）'))
    if re.search(r'\bh3\b', sel) and size < 21:
        OFF.append((sel, size, 'H3 规范 24px（移动 21–23）'))

W('')
W('=' * 92)
W('偏离 §17 的标题字号')
W('=' * 92)
if OFF:
    for sel, size, note in OFF:
        W(f'   VIOLATION  {sel[:56]:<58} {size}px   （{note}）')
else:
    W('   无 —— 所有 h2/h3 字号均在规范范围内')

# ---- 2) 卡片系统 ----
W('')
W('=' * 92)
W('卡片系统是否统一')
W('=' * 92)
CHECKS = [
    ('picks-grid 3 列（与首页 .models 一致）', r'\.picks-grid \{[^}]*repeat\(3, minmax\(0, 1fr\)\)'),
    ('picks 标题 34px（真 h2）', r'\.picks > h2 \{[^}]*font-size:\s*34px'),
    ('pick-card 标题 20px', r'\.pick-card-body strong \{[^}]*font-size:\s*20px'),
    ('pick-body h3 = 24px', r'\.pick-body h3 \{[^}]*font-size:\s*24px'),
    ('proscons h3 = 24px', r'\.proscons h3 \{[^}]*font-size:\s*24px'),
    ('authorbox 2px navy 顶线', r'\.authorbox \{[^}]*border-top:\s*2px solid var\(--hdl-navy\)'),
    ('badge--data 已定义', r'\.badge--data'),
    ('卡片统一 radius-md', r'\.pick-card \{[^}]*border-radius: var\(--hdl-radius-md\)'),
]
for label, pat in CHECKS:
    W(f'   {"OK      " if re.search(pat, css) else "MISSING "} {label}')

# ---- 3) 产物级核验 ----
W('')
W('=' * 92)
W('产物级核验（全部 45 个页面）')
W('=' * 92)
fake = sum(1 for p in pages if 'badge badge--tested' in io.open(p, encoding='utf-8').read())
data = sum(1 for p in pages if 'badge badge--data' in io.open(p, encoding='utf-8').read())
contra = sum(1 for p in pages if 'Tested Not yet' in io.open(p, encoding='utf-8').read())
mislbl = sum(1 for p in pages if 'Product source: Analysis' in io.open(p, encoding='utf-8').read())
W(f'   虚假「Tested」徽章       {fake} 页（改前 43）')
W(f'   「Figures checked」徽章  {data} 页')
W(f'   自相矛盾字符串           {contra} 页（应为 0）')
W(f'   错标的 Product source    {mislbl} 页（应为 0）')

# 3 列网格是否生效
import re as _re
hrefs = set()
for p in pages[:3]:
    hrefs |= set(_re.findall(r'href="(/_astro/[^"]+\.css)"', io.open(p, encoding='utf-8').read()))
allcss = ''
for h in hrefs:
    allcss += io.open('site/dist' + h, encoding='utf-8').read()
allcss = _re.sub(r'\[data-astro-cid-[a-z0-9]+\]', '', allcss)
W('')
W('   产物 CSS 中 .picks-grid 的列数声明：')
for m in _re.finditer(r'\.picks-grid\{[^}]*\}', allcss):
    W('      ' + m.group(0)[:110])

io.open('analysis/_consistency_verify.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('\n'.join(out))
