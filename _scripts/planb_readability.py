"""抽查方案 B 之后关键句子的实际可读性。"""
import glob
import io
import re

D = 'site/dist'
out = []
def P(*a): out.append(' '.join(str(x) for x in a))

P('=' * 90)
P('关键句子抽查（去掉 HTML 标签后）')
P('=' * 90)

SAMPLES = [
    ('best-hair-dryers/under-150/index.html', r'Our pick[^.]{0,140}\.'),
    ('best-hair-dryers/under-150/index.html', r'The short answer[^.]{0,200}\.'),
    ('reviews/laifen/index.html', r'The short answer[^.]{0,220}\.'),
    ('comparisons/laifen-vs-dyson/index.html', r'The short answer[^.]{0,220}\.'),
    ('index.html', r'Starts at[^.]{0,80}\.|from about[^.]{0,80}\.'),
]

for path, pat in SAMPLES:
    p = f'{D}/{path}'
    try:
        h = io.open(p, encoding='utf-8').read()
    except Exception:
        continue
    # 去标签
    txt = re.sub(r'<[^>]+>', ' ', h)
    txt = re.sub(r'&amp;', '&', txt)
    txt = re.sub(r'\s+', ' ', txt)
    ms = re.findall(pat, txt)
    if ms:
        P(f'\n--- {path}')
        for m in ms[:2]:
            P('   ' + m.strip()[:230])

# 检查所有 "a about" / "an about" / "the about" 残留
P('')
P('=' * 90)
P('全局语法残留扫描')
P('=' * 90)
bad = {'a about': 0, 'an about': 0, 'the about': 0, 'about about': 0,
       '**about C': 0, 'about C$ is': 0}
detail = []
for p in glob.glob(f'{D}/**/*.html', recursive=True):
    h = io.open(p, encoding='utf-8').read()
    txt = re.sub(r'<[^>]+>', ' ', h)
    for k in bad:
        if k == '**about C':
            continue
        n = len(re.findall(re.escape(k), txt, re.I))
        if n:
            bad[k] += n
            detail.append((p.replace(D + '\\', '').replace(D + '/', ''), k, n))
for k, v in bad.items():
    P(f'   {k!r:<16} {v} 处')
if detail:
    P('   涉及页面:')
    for p, k, n in detail[:12]:
        P(f'      {p}  [{k}] x{n}')

io.open('analysis/_planb_readability.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written analysis/_planb_readability.txt')
