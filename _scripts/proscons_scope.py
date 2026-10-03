"""1) 查内容结构标准.md 里 5 处旧 URL 的上下文；2) 看 ProsCons 在正文里的实际模式。"""
import io
import re

out = []
def W(*a): out.append(' '.join(str(x) for x in a))

W('=' * 92)
W('内容结构标准.md 中的旧 URL 残留上下文')
W('=' * 92)
t = io.open('deliverables/内容结构标准.md', encoding='utf-8').read()
for m in re.finditer(r'/compare/|/for/|/learn/|/ca/', t):
    s = max(0, m.start() - 130)
    e = min(len(t), m.end() + 130)
    W(f'[{m.group(0)}]  …{t[s:e].replace(chr(10), " ").strip()}…')
    W('')

W('=' * 92)
W('ProsCons 在正文里的实际模式（取 laifen.mdx 一段）')
W('=' * 92)
d = io.open('deliverables/drafts/laifen.mdx', encoding='utf-8').read()
lines = d.splitlines()
# 找 "What we liked"
idx = [i for i, l in enumerate(lines) if l.strip().startswith('**What we liked')]
W(f'  laifen.mdx 中 "**What we liked" 出现 {len(idx)} 次')
if idx:
    i = idx[0]
    for l in lines[i:i + 22]:
        W('   | ' + l)
W('')

W('=' * 92)
W('全站统计：这些模式各自出现多少次（评估转换规模）')
W('=' * 92)
import os
D = 'deliverables/drafts'
tot = {}
for fn in sorted(os.listdir(D)):
    if not fn.endswith('.mdx'):
        continue
    x = io.open(os.path.join(D, fn), encoding='utf-8').read()
    for key, pat in [
        ('What we liked', r'(?m)^\*\*What we liked'),
        ("What we didn't", r"(?m)^\*\*What we didn't"),
        ('Skip if:', r'(?m)\*\*Skip if:\*\*'),
        ('Check price 链接', r'\[Check price'),
        ('证据标注 *(…)*', r'\*\((?:review analysis|Amazon\.ca data|manufacturer claim|buyer feedback|Measured)\)\*'),
        ('价格元信息行 about C$… ·', r'\*\*about C\$[\d,]+ · '),
    ]:
        tot[key] = tot.get(key, 0) + len(re.findall(pat, x))
for k, v in tot.items():
    W(f'   {k:<28} {v:>5} 处')

io.open('analysis/_proscons_scope.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written analysis/_proscons_scope.txt')
