"""审计：文章页与栏目页到底渲染了哪些区块，以及这些区块的现有样式。"""
import io
import re

out = []
def W(*a): out.append(' '.join(str(x) for x in a))

# ---------- 1) 文章页的区块顺序 ----------
W('=' * 94)
W('文章页 /reviews/laifen/ 的区块顺序（按 DOM 出现顺序）')
W('=' * 94)
h = io.open('site/dist/reviews/laifen/index.html', encoding='utf-8').read()
# 取 <main> 范围
i = h.find('<main')
j = h.find('</main>')
main = h[i:j] if i >= 0 else h

blocks = [
    ('breadcrumbs', r'class="breadcrumbs"'),
    ('h1', r'<h1[ >]'),
    ('lede', r'class="lede"'),
    ('badge', r'class="badge badge--'),
    ('disclosure', r'class="disclosure"'),
    ('meta-line', r'class="meta-line"'),
    ('product-hero', r'class="product-hero"'),
    ('verdict-split', r'class="verdict-split"'),
    ('lab-test', r'class="lab-test"'),
    ('ratings', r'class="ratings"'),
    ('picks-grid', r'class="picks-grid"'),
    ('pick-card', r'class="pick-card"'),
    ('toc', r'class="toc"'),
    ('proscons', r'class="proscons"'),
    ('table-scroll', r'class="table-scroll"'),
    ('method-box', r'class="method-box"'),
    ('where-to-buy', r'class="where-to-buy"'),
    ('pick(id)', r'class="pick" id='),
    ('price-box', r'class="price-box"'),
    ('related', r'class="related"'),
    ('authorbox', r'class="authorbox"'),
]
seq = []
for name, pat in blocks:
    for m in re.finditer(pat, main):
        seq.append((m.start(), name))
seq.sort()
W('   ' + ' → '.join(n for _, n in seq))

# ---------- 2) 现有组件样式 ----------
W('')
W('=' * 94)
W('现有组件样式（global.css）—— 注意与首页新语言是否一致')
W('=' * 94)
css = io.open('site/src/styles/global.css', encoding='utf-8').read()

GROUPS = {
    '文章顶选卡片（旧）': ['.picks', '.picks-grid', '.pick-card', '.pick-card-body', '.pick-card-media'],
    'Where to buy 卡片': ['.pick', '.pick-media', '.pick-body', '.pick-meta'],
    'Lab Test Card': ['.lab-test'],
    'Best for/Skip if': ['.verdict-split'],
    '分类结论': ['.ratings'],
    'Pros/Cons': ['.proscons'],
    '方法论框': ['.method-box'],
    '相关阅读': ['.related'],
    '作者框': ['.authorbox'],
    'Price Box': ['.price-box'],
    '对比表': ['.cmp-table'],
    '证据标签': ['.ev'],
    '披露': ['.disclosure'],
}
for gname, sels in GROUPS.items():
    W('')
    W(f'--- {gname}')
    found = False
    for b in re.findall(r'(?s)([^{}]*\{[^{}]*\})', css):
        sel = b.split('{')[0]
        if any(re.search(re.escape(s) + r'(?![\w-])', sel) for s in sels):
            W('   ' + re.sub(r'\s+', ' ', b.strip())[:170])
            found = True
    if not found:
        W('   （global.css 里没有对应规则）')

io.open('analysis/_consistency_audit.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written analysis/_consistency_audit.txt')
