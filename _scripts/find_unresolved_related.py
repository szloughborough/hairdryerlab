"""找出 related 未解析成功的条目，并查看栏目页（hair-types 等）当前结构。"""
import glob
import io
import os
import re

out = []
def W(*a): out.append(' '.join(str(x) for x in a))

STYLE = re.compile(r'(?s)<style[^>]*>.*?</style>')
D = 'site/dist'

W('=' * 90)
W('related 未解析的条目')
W('=' * 90)
for p in sorted(glob.glob(f'{D}/**/*.html', recursive=True)):
    h = STYLE.sub(' ', io.open(p, encoding='utf-8').read())
    for m in re.finditer(r'<li class="related__item">(.*?)</li>', h, re.S):
        label = re.sub(r'<[^>]+>', '', m.group(1)).strip()
        href = re.search(r'href="([^"]+)"', m.group(1))
        head = label.split('·')[0].strip()
        if head.startswith('/') or (head and '/' in head and ' ' not in head):
            rel = os.path.relpath(p, D).replace(os.sep, '/')
            W(f'   {rel}')
            W(f'      label: {label[:90]}')
            W(f'      href : {href.group(1) if href else "?"}')

W('')
W('=' * 90)
W('路由映射里到底有哪些（看是否缺条目）')
W('=' * 90)
routes = []
for p in sorted(glob.glob(f'{D}/**/*.html', recursive=True)):
    rel = os.path.relpath(p, D).replace(os.sep, '/').replace('/index.html', '')
    if rel == 'index.html':
        rel = ''
    routes.append(rel)
for r in routes[:50]:
    W(f'   /{r}/')

W('')
W('=' * 90)
W('栏目页（learn/hair-types.mdx）的正文结构')
W('=' * 90)
p = 'deliverables/drafts/hair-types.mdx'
if os.path.exists(p):
    t = io.open(p, encoding='utf-8').read()
    body = re.sub(r'(?s)^---.*?---', '', t)
    for m in re.findall(r'(?m)^(#{1,3}) (.+)$', body):
        W(f'   {"  " * (len(m[0]) - 2)}{m[1]}')
    W('')
    W('   ---- 正文开头 1200 字符 ----')
    W(body.strip()[:1200])
else:
    W(f'   {p} 不存在')

io.open('analysis/_related_unresolved.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written analysis/_related_unresolved.txt')
