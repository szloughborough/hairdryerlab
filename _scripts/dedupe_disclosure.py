"""移除旧稿正文里与布局重复的联盟披露句（品牌规范 §37 要求披露只出现一次且位置明确）。"""
import io, re

p = 'deliverables/drafts/best-dyson-alternatives-LAUNCH.mdx'
t = io.open(p, encoding='utf-8').read()

DUP = ' This page contains affiliate links — if you buy through them we may earn a commission at no extra cost to you. It does not affect our rankings, which follow the review analysis described above.'
DUP2 = ' This page contains affiliate links — if you buy through them we may earn a commission at no extra cost to you.'

before = len(t)
for d in (DUP, DUP2):
    t = t.replace(d, '')
io.open(p, 'w', encoding='utf-8').write(t)
print(f'removed {before - len(t)} chars of duplicated disclosure')
