"""
把之前为消除死链而临时收拢到栏目页的链接，回填到已存在的具体页面。

按「锚文本 + 目标」双重匹配，避免误改仍不存在的页面（如 slopehill / wavytalk / conair）。
幂等：可重复执行。等后续页面写好，在此加规则即可。
"""
import io, os, re

DRAFTS = 'deliverables/drafts'

# (锚文本, 原 href, 新 href)
RULES = [
    # Dreame 评测页已存在
    (r'Read our full Dreame guide',  '/reviews/',   '/reviews/dreame/'),
    (r'Read our full Dreame review', '/reviews/',   '/reviews/dreame/'),
    # Slopehill / Conair 评测页已存在
    (r'Read our full Slopehill guide',  '/reviews/', '/reviews/slopehill/'),
    (r'Read our full Slopehill review', '/reviews/', '/reviews/slopehill/'),
    (r'Read our full Conair guide',     '/reviews/', '/reviews/conair/'),
    (r'Read our full Conair review',    '/reviews/', '/reviews/conair/'),
    (r'our slopehill brand guide',      '/reviews/', '/reviews/slopehill/'),
    (r'Read our full Wavytalk guide',   '/reviews/', '/reviews/wavytalk/'),
    (r'Read our full Wavytalk review',  '/reviews/', '/reviews/wavytalk/'),
    # 耐用性指南已存在
    (r'how long hair dryers actually last', '/guides/', '/guides/how-long-does-a-hair-dryer-last/'),
    (r'cord and switch failure',            '/guides/', '/guides/how-long-does-a-hair-dryer-last/'),
    (r'durability guide',                   '/guides/', '/guides/how-long-does-a-hair-dryer-last/'),
    # 发质页已存在
    (r'travel hair dryer guide', '/hair-types/', '/hair-types/travel-hair-dryer/'),
    (r'curly hair guide',        '/hair-types/', '/hair-types/curly-hair/'),
    (r'curly hair dryer guide',  '/hair-types/', '/hair-types/curly-hair/'),
    (r'frizzy hair guide',       '/hair-types/', '/hair-types/frizzy-hair/'),
    (r'fine hair guide',         '/hair-types/', '/hair-types/fine-hair/'),
    (r'thick hair guide',        '/hair-types/', '/hair-types/thick-hair/'),
    # 卷发页里的 diffuser 指南
    (r'diffuser guide',          '/guides/',    '/guides/diffuser/'),
]

changed = {}
for fn in sorted(os.listdir(DRAFTS)):
    if not fn.endswith('.mdx'):
        continue
    p = os.path.join(DRAFTS, fn)
    t = io.open(p, encoding='utf-8').read()
    orig = t
    n = 0
    for anchor, old, new in RULES:
        pat = r'(\[' + anchor + r'\]) \(' + re.escape(old) + r'\)'
        pat = r'(\[' + anchor + r'\])' + r'\(' + re.escape(old) + r'\)'
        t, k = re.subn(pat, lambda m: f'{m.group(1)}({new})', t)
        n += k
    if t != orig:
        io.open(p, 'w', encoding='utf-8').write(t)
        changed[fn] = n

print('回填的具体链接：')
for fn, n in changed.items():
    print(f'  {fn:<40} {n} 处')
print(f'合计 {sum(changed.values())} 处')
