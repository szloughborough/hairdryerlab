"""核实披露出现的位置：正文前（强合规）还是仅页脚（弱合规）。"""
import glob
import io
import os
import re

D = 'site/dist'
out = []
def P(*a): out.append(' '.join(str(x) for x in a))

SENT = 'may earn a commission when you buy through our links'

P('=' * 92)
P('披露位置核验：正文前 vs 页脚')
P('=' * 92)
P(f"{'页面':<42}{'正文前':>7}{'页脚':>6}{'在 H1 之前':>11}")
P('-' * 92)

weak = []
for p in sorted(glob.glob(f'{D}/**/*.html', recursive=True)):
    h = io.open(p, encoding='utf-8').read()
    if SENT.lower() not in h.lower():
        continue
    rel = os.path.relpath(p, D).replace(os.sep, '/').replace('/index.html', '/')
    if rel == 'index.html':
        rel = '/'

    footer_at = h.lower().find('<footer')
    h1_at = h.find('<h1')

    # 找披露出现的位置（可能有多次）
    positions = [m.start() for m in re.finditer(SENT, h, re.I)]
    before_footer = [x for x in positions if footer_at < 0 or x < footer_at]
    in_footer = [x for x in positions if footer_at >= 0 and x > footer_at]
    before_h1 = [x for x in positions if h1_at >= 0 and x < h1_at]

    P(f'{rel:<42}{("✓ " + str(len(before_footer))) if before_footer else "✗":>7}'
      f'{("✓ " + str(len(in_footer))) if in_footer else "—":>6}'
      f'{("✓ " + str(len(before_h1))) if before_h1 else "—":>11}')

    if not before_footer:
        weak.append(rel)

P('')
P('=' * 92)
if weak:
    P(f'⚠ 披露仅出现在页脚（弱合规）：{len(weak)} 个页面')
    for r in weak:
        P(f'   {r}')
else:
    P('✓ 所有披露都在正文（页脚之前）出现，符合 §37「页首或正文前」')
P('=' * 92)

io.open('analysis/_disclosure_position.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written analysis/_disclosure_position.txt')
