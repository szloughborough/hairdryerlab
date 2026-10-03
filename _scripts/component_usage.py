"""核验 §55 组件的实际使用情况：组件代码是否进入了构建产物。"""
import glob
import io
import os
import re

out = []
def P(*a): out.append(' '.join(str(x) for x in a))

# 取各组件特有的 class 名，看产物里是否出现
COMPONENTS = {
    'LabTestCard': 'lab-test',
    'BestForSkipIf': 'skip-if',
    'ProsCons': 'pros-cons',
    'CategoryRatings': 'category-rating',
    'PriceBox': 'price-box',
    'AffiliateCTA': 'affiliate-cta',
    'EvidenceLabel': 'evidence-label',
}

P('=' * 88)
P('§55 组件是否真正进入产物（按各自专有 class 检索）')
P('=' * 88)
pages = glob.glob('site/dist/**/*.html', recursive=True)
for name, cls in COMPONENTS.items():
    hits = 0
    for p in pages:
        h = io.open(p, encoding='utf-8').read()
        hits += len(re.findall(cls, h, re.I))
    # 组件源码里的 class 定义
    src = f'site/src/components/{name}.astro'
    defined = ''
    if os.path.exists(src):
        s = io.open(src, encoding='utf-8').read()
        defined = ', '.join(sorted(set(re.findall(r'class="([^"]+)"', s))))
    P(f'  {name:<18} 产物命中 {hits:>5} 处   {("源码 class: " + defined[:60]) if defined else "(无 class)"}')

P('')
P('=' * 88)
P('对照：这些概念在正文里是怎么实现的（markdown 而非组件）')
P('=' * 88)
draft = io.open('deliverables/drafts/laifen.mdx', encoding='utf-8').read()
checks = {
    'Lab Test Card 概念': r'Measured|Not yet tested|Lab Test',
    'Best for / Skip if': r'\*\*Skip if:\*\*|Best for',
    'Pros / Cons': r"What we liked|What we didn't",
    'Price Box': r'\*\*about C\$|C\$999',
    'Affiliate CTA': r'\[Check price at Amazon\.ca\]',
}
for label, pat in checks.items():
    n = len(re.findall(pat, draft))
    P(f'  {label:<22} laifen.mdx 中 {n:>3} 处（markdown 实现）')

io.open('analysis/_component_usage.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written analysis/_component_usage.txt')
