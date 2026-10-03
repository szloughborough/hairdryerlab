"""修方案 B 引入的别扭表述（把裸的 "about C$X is" 改为 "At about C$X it is" 等）。"""
import io
import os
import re

D = 'deliverables/drafts'

# 通用正则：裸的 "**about C$N is/are" → "**At about C$N it is/they are"
GENERIC = [
    (r'\*\*about (C\$\d+) is\b', r'**At \1 it is'),
    (r'\*\*about (C\$\d+) are\b', r'**At \1 they are'),
    (r'\bmoving to the about (C\$\d+) band\b', r'moving to the band around \1'),
    (r'\bfrom a about (C\$\d+) volume leader to a about (C\$\d+) brushless model\b',
     r'from a volume leader at about \1 to a brushless model at about \2'),
    (r'\ba about (C\$\d+) Laifen Air Diffuser\b', r'a Laifen Air Diffuser at about \1'),
    (r'\bunlike the about (C\$\d+) Slopehill sibling\b', r'unlike the Slopehill model at about \1'),
    (r'\bunlike the about (C\$\d+) sibling\b', r'unlike the sibling at about \1'),
]

# 精确替换
EXACT = [
    ('**about C$61 is the most expensive Conair here',
     '**The InfinitiPro FloMotion at about C$61 is the most expensive Conair here'),
]

total = 0
per = {}
for fn in sorted(os.listdir(D)):
    if not fn.endswith('.mdx'):
        continue
    p = os.path.join(D, fn)
    t = io.open(p, encoding='utf-8').read()
    orig = t
    n = 0
    for old, new in EXACT:
        if old in t:
            t = t.replace(old, new)
            n += 1
    for pat, rep in GENERIC:
        t, k = re.subn(pat, rep, t)
        n += k
    if t != orig:
        io.open(p, 'w', encoding='utf-8').write(t)
        per[fn] = n
        total += n

print(f'修复 {total} 处，涉及 {len(per)} 个文件')
for fn, n in sorted(per.items(), key=lambda x: -x[1]):
    print(f'   {fn:<42} {n} 处')
