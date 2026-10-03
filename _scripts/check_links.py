"""全站死链扫描：检查 dist 里所有 HTML 的站内链接是否有对应产物。"""
import io, os, re, glob, collections

DIST = 'site/dist'
out = []
def P(*a): out.append(' '.join(str(x) for x in a))

# 收集所有存在的路由
exists = set()
for p in glob.glob(os.path.join(DIST, '**', '*.html'), recursive=True):
    rel = os.path.relpath(p, DIST).replace('\\', '/')
    if rel.endswith('index.html'):
        route = '/' + rel[:-len('index.html')]
    else:
        route = '/' + rel
    exists.add(route)
# 静态文件
statics = set()
for p in glob.glob(os.path.join(DIST, '**', '*'), recursive=True):
    if os.path.isfile(p):
        statics.add('/' + os.path.relpath(p, DIST).replace('\\', '/'))

P(f'产物中的路由（{len(exists)} 个）:')
for r in sorted(exists):
    P(f'  {r}')

# 扫描所有 HTML 的站内链接
link_src = collections.defaultdict(set)   # target -> {source pages}
for p in glob.glob(os.path.join(DIST, '**', '*.html'), recursive=True):
    rel = os.path.relpath(p, DIST).replace('\\', '/')
    src = '/' + (rel[:-len('index.html')] if rel.endswith('index.html') else rel)
    h = io.open(p, encoding='utf-8').read()
    for href in re.findall(r'href="(/[^"#?]*)"', h):
        if href.startswith('/_astro/') or href.endswith(('.css', '.js', '.png', '.jpg', '.svg', '.ico', '.xml', '.txt', '.webmanifest')):
            continue
        link_src[href].add(src)

# 判定
dead = {}
for target, srcs in link_src.items():
    t = target if target.endswith('/') else target + '/'
    if t in exists or target in exists or target in statics:
        continue
    dead[target] = srcs

P('')
P('=' * 78)
if dead:
    P(f'死链 {len(dead)} 个：')
    for t, srcs in sorted(dead.items(), key=lambda x: -len(x[1])):
        P(f'  {t}')
        P(f'      被引用自: {", ".join(sorted(srcs))}')
else:
    P('没有死链 —— 所有站内链接都有对应产物')
P('=' * 78)

io.open('analysis/_deadlinks.txt', 'w', encoding='utf-8').write('\n'.join(out))
print(f'dead links: {len(dead)}')
print('written analysis/_deadlinks.txt')
