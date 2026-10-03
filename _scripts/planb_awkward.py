"""找出方案 B 之后语法别扭的 "about C$X" 表述，并列出待修清单。"""
import io
import os
import re

D = 'deliverables/drafts'
out = []
def P(*a): out.append(' '.join(str(x) for x in a))

PATS = [
    (r'\bthe about C\$\d+', 'THE + about（作定语）'),
    (r'\*\*about C\$\d+ (?:is|are|was|were)\b', 'about 直接作主语'),
    (r'\b[an] about C\$', '冠词 + about'),
    (r'^\s*about C\$\d+', '行首 about'),
    (r'\babout C\$\d+,? (?:well below|which sits)\b', 'about + 从句'),
    (r'\bunlike the about\b', 'unlike the about'),
    (r'\bAt about C\$\d+ the\b', 'At about ... the（可接受，列出备查）'),
]

hits = []
for fn in sorted(os.listdir(D)):
    if not fn.endswith('.mdx'):
        continue
    t = io.open(os.path.join(D, fn), encoding='utf-8').read()
    for i, line in enumerate(t.splitlines(), 1):
        for p, label in PATS:
            if re.search(p, line):
                hits.append((fn, i, label, line.strip()[:160]))
                break

P(f'待修的别扭表述：{len(hits)} 处')
P('=' * 110)
for fn, i, label, line in hits:
    P(f'{fn}:{i}   [{label}]')
    P(f'    {line}')
    P('')

io.open('analysis/_planb_awkward.txt', 'w', encoding='utf-8').write('\n'.join(out))
print(f'written analysis/_planb_awkward.txt  ({len(hits)} hits)')
