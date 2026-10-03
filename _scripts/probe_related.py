"""查看 related frontmatter 的实际写法（输出到文件，避免 GBK 控制台问题）。"""
import io
import os
import re

D = 'deliverables/drafts'
REL = re.compile(r'(?ms)^related:\s*\n((?:\s+-\s+.+\n)+)')
VAL = re.compile(r'^\s+-\s+[\'"]?([^\'"\n]+)', re.M)

out = []
def W(*a): out.append(' '.join(str(x) for x in a))

for f in ('laifen.mdx', 'under-150.mdx', 'ionic-vs-ceramic.mdx', 'curly-hair.mdx'):
    p = os.path.join(D, f)
    if not os.path.exists(p):
        continue
    t = io.open(p, encoding='utf-8').read()
    m = REL.search(t)
    W(f'=== {f}')
    W(m.group(1).rstrip() if m else '  (无 related)')
    W('')

forms = {'带前后斜杠': 0, '仅路径(无尾斜杠)': 0, '绝对 URL': 0, '裸 slug': 0}
vals = set()
for f in os.listdir(D):
    if not f.endswith('.mdx'):
        continue
    t = io.open(os.path.join(D, f), encoding='utf-8').read()
    m = REL.search(t)
    if not m:
        continue
    for v in VAL.findall(m.group(1)):
        v = v.strip()
        vals.add(v)
        if v.startswith('http'):
            forms['绝对 URL'] += 1
        elif v.startswith('/') and v.endswith('/'):
            forms['带前后斜杠'] += 1
        elif v.startswith('/'):
            forms['仅路径(无尾斜杠)'] += 1
        else:
            forms['裸 slug'] += 1

W('=== related 值形态统计 ===')
for k, v in forms.items():
    W(f'   {k}: {v}')
W('')
W('=== 样本值 ===')
for v in sorted(vals)[:18]:
    W('   ' + v)
W(f'   （共 {len(vals)} 个不同值）')

io.open('analysis/_related_probe.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written analysis/_related_probe.txt')
