"""可靠复核：§55 组件在 DOM 中的真实渲染（剔除内联 <style> 块）+ 任务 3 文档核验。"""
import glob
import io
import os
import re
from collections import Counter

D = 'site/dist'
out = []
def W(*a): out.append(' '.join(str(x) for x in a))

STYLE_RE = re.compile(r'(?s)<style[^>]*>.*?</style>')

def dom_only(html):
    return STYLE_RE.sub(' ', html)

W('=' * 92)
W('§55 组件在 DOM 中的真实渲染（已剔除内联 CSS）')
W('=' * 92)
CLASSES = {
    'LabTestCard (§29)': r'class="lab-test"',
    'BestForSkipIf (§6/§32)': r'class="verdict-split"',
    'CategoryRatings (§31)': r'class="ratings"',
    'ProsCons (§70)': r'class="proscons"',
    'PriceBox (§48)': r'class="price-box"',
    'AffiliateCTA (§35)': r'class="cta"',
    'EvidenceLabel (§51)': r'class="evidence-label"',
}
pages = glob.glob(f'{D}/**/*.html', recursive=True)
hits = {}
for name, pat in CLASSES.items():
    n, npages = 0, set()
    for p in pages:
        h = dom_only(io.open(p, encoding='utf-8').read())
        k = len(re.findall(pat, h))
        n += k
        if k:
            npages.add(p)
    hits[name] = (n, len(npages))
    W(f'   {name:<26} {n:>5} 处   覆盖 {len(npages):>2} 个页面')

W('')
W('=== 状态判定 ===')
for name, (n, np) in hits.items():
    W(f'   {"✓ 已上线" if n else "✗ 未渲染"}  {name}')

W('')
W('=' * 92)
W('任务 3：内容结构标准.md 核验')
W('=' * 92)
P3 = 'deliverables/内容结构标准.md'
if os.path.exists(P3):
    t = io.open(P3, encoding='utf-8').read()
    W(f'   大小 {len(t):,} 字符 / {len(t.splitlines())} 行')
    checks = {
        '§42 Article 结构': r'§42|Article',
        '§43 Buying Guide': r'§43|Buying Guide',
        '§44 Comparison': r'§44|Comparison',
        '§45 Hair-Type': r'§45|Hair-Type',
        '新 URL 分类法 /best-hair-dryers/': r'/best-hair-dryers/',
        '新 URL 分类法 /comparisons/': r'/comparisons/',
        '新 URL 分类法 /hair-types/': r'/hair-types/',
        '新 URL 分类法 /guides/': r'/guides/',
        '旧 URL /compare/ 已清除': None,
        '品牌要求 vs 实际实现 对照表': r'实际实现|实现差异|\| *品牌规范',
        '方案 B 价格约数': r'约数|about C\$|方案 B',
        '禁止数字总分': r'9\.4/10|数字总分',
        '八维评测标准': r'八维',
    }
    for label, pat in checks.items():
        if pat is None:
            n = len(re.findall(r'/compare/|/for/|/learn/|/ca/', t))
            W(f'   {"✓" if n == 0 else "✗ 仍有 " + str(n) + " 处"} {label}')
        else:
            n = len(re.findall(pat, t))
            W(f'   {"✓" if n else "✗"} {label:<34} 命中 {n}')
else:
    W('   文件不存在')

io.open('analysis/_final_verify.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written analysis/_final_verify.txt')
