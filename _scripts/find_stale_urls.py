"""定位旧 URL 残留来源；并查 /best-hair-dryers/ 与 /guides/ 栏目页的来源文件。"""
import io
import os
import re

out = []
def W(*a): out.append(' '.join(str(x) for x in a))

W('=' * 88)
W('旧 URL 分类法残留（/compare/ · /learn/ · /for/ · /ca/ · /best/）')
W('=' * 88)
pat = re.compile(r'(?<![\w/])/(?:compare|learn|for|ca|best)/')
for root in ('deliverables/drafts', 'site/src/content'):
    for dp, dn, fn in os.walk(root):
        for f in fn:
            if not f.endswith('.mdx'):
                continue
            p = os.path.join(dp, f)
            t = io.open(p, encoding='utf-8').read()
            for m in pat.finditer(t):
                line = t[:m.start()].count('\n') + 1
                W(f'   {p}:{line}  …{t[max(0,m.start()-60):m.end()+40].strip()[:110]}…')

W('')
W('=' * 88)
W('栏目页来源：/best-hair-dryers/ 与 /guides/')
W('=' * 88)
for c in ('best', 'review', 'compare', 'for', 'learn', 'ca'):
    d = f'site/src/content/{c}'
    if not os.path.isdir(d):
        continue
    for f in sorted(os.listdir(d)):
        if not f.endswith('.mdx'):
            continue
        t = io.open(f'{d}/{f}', encoding='utf-8').read()
        m = re.search(r'(?m)^route:\s*["\']?([^"\'\n]+)', t)
        r = m.group(1).strip().rstrip('/') if m else ''
        if r in ('/best-hair-dryers', '/guides', 'best-hair-dryers', 'guides'):
            W(f'   {c}/{f}  →  route "{r}"')

W('')
W('=' * 88)
W('best/best-hair-dryers.mdx 的 frontmatter 头部')
W('=' * 88)
p = 'site/src/content/best/best-hair-dryers.mdx'
if os.path.exists(p):
    t = io.open(p, encoding='utf-8').read()
    m = re.match(r'(?s)^---\n(.*?)\n---', t)
    W(m.group(1)[:700] if m else '(无 frontmatter)')

W('')
W('=' * 88)
W('learn/guides.mdx 的正文结构')
W('=' * 88)
p = 'site/src/content/learn/guides.mdx'
if os.path.exists(p):
    t = io.open(p, encoding='utf-8').read()
    body = re.sub(r'(?s)^---.*?---', '', t)
    for m in re.findall(r'(?m)^(#{1,3}) (.+)$', body):
        W(f'   {"  " * (len(m[0]) - 2)}{m[1]}')
else:
    W('   不存在')

io.open('analysis/_stale_urls.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written analysis/_stale_urls.txt')
