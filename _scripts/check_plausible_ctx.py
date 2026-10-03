"""确认 Plausible 命中是「工具名」还是英文形容词。"""
import io
import re

FILES = [
    'deliverables/drafts/how-long-does-a-hair-dryer-last.mdx',
    'deliverables/drafts/ionic-vs-ceramic.mdx',
    'deliverables/drafts/quiet-hair-dryer.mdx',
    'deliverables/Astro技术栈清单.md',
    'deliverables/技术SEO与信息架构规划.md',
]
for p in FILES:
    t = io.open(p, encoding='utf-8').read()
    print(f'=== {p}')
    for m in re.finditer(r'(?i)plausible', t):
        s = max(0, m.start() - 90)
        e = min(len(t), m.end() + 90)
        seg = re.sub(r'\s+', ' ', t[s:e])
        print(f'   …{seg}…')
    print()
