"""
修复旧 URL 分类法残留（品牌规范 §54 改版前的写法）。

只替换链接上下文里的路径，不做全文盲替换。
映射依据：site/src/data/site.ts 的 COLLECTION_PREFIX。
"""
import io
import os
import re

# 旧的 → 新的（顺序重要：长的先替换）
URL_MAP = [
    ('/best-hair-dryer/', '/best-hair-dryers/'),
    ('/compare/', '/comparisons/'),
    ('/learn/', '/guides/'),
    ('/for/', '/hair-types/'),
    ('/ca/where-to-buy-laifen-canada/', '/best-hair-dryers/best-hair-dryer-canada/'),
    ('/ca/hair-dryer-sale-canada/', '/best-hair-dryers/best-hair-dryer-canada/'),
    ('/ca/', '/best-hair-dryers/'),
    ('(/laifen/)', '(/reviews/laifen/)'),
    ('- /laifen/', '- /reviews/laifen/'),
]

ROOTS = ['deliverables/drafts', 'site/src/content']
TARGETS = []
for root in ROOTS:
    for dp, dn, fn in os.walk(root):
        for f in fn:
            if f.endswith('.mdx'):
                TARGETS.append(os.path.join(dp, f))

out = []
def W(*a): out.append(' '.join(str(x) for x in a))

W('=' * 92)
W('修复前的旧 URL 出现情况')
W('=' * 92)
PAT = re.compile(r'(?<![\w/])/(?:compare|learn|for|ca|best-hair-dryer)/')
for p in sorted(TARGETS):
    t = io.open(p, encoding='utf-8').read()
    hits = list(PAT.finditer(t))
    if hits:
        W(f'   {p}  —  {len(hits)} 处')
        for m in hits:
            W(f'        {t[max(0,m.start()-50):m.end()+40].strip()[:100]}')

W('')
W('=' * 92)
W('执行替换')
W('=' * 92)
changed = 0
for p in sorted(TARGETS):
    t = io.open(p, encoding='utf-8').read()
    orig = t
    for old, new in URL_MAP:
        t = t.replace(old, new)
    # /laifen/ 这类裸路径只在 related 列表或行内链接里出现
    t = re.sub(r'(?<![\w/])/laifen/(?![\w])', '/reviews/laifen/', t)
    if t != orig:
        io.open(p, 'w', encoding='utf-8').write(t)
        changed += 1
        W(f'   {p}')

W('')
W(f'   共修改 {changed} 个文件')

W('')
W('=' * 92)
W('修复后复查')
W('=' * 92)
left = 0
for p in sorted(TARGETS):
    t = io.open(p, encoding='utf-8').read()
    for m in PAT.finditer(t):
        W(f'   {p}: {t[max(0,m.start()-50):m.end()+40].strip()[:100]}')
        left += 1
if not left:
    W('   旧 URL 已清零')

io.open('analysis/_url_migration.txt', 'w', encoding='utf-8').write('\n'.join(out))
print(f'changed files: {changed}, remaining: {left}')
print('written analysis/_url_migration.txt')
