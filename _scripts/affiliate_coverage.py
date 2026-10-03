"""统计每个页面的联盟链接落地情况 —— 找出零变现页面。"""
import io, glob, os, re

DIST = 'site/dist'
rows = []
for p in sorted(glob.glob(os.path.join(DIST, '**', '*.html'), recursive=True)):
    rel = os.path.relpath(p, DIST).replace(os.sep, '/')
    if rel in ('index.html', '404.html'):
        continue
    route = '/' + rel.replace('/index.html', '/').replace('index.html', '')
    h = io.open(p, encoding='utf-8').read()
    links = len(re.findall(r'rel="[^"]*sponsored', h))
    pend = len(re.findall(r'<span class="affiliate-pending"', h))
    rows.append((route, links, pend))

rows.sort(key=lambda r: (r[1], r[0]))
out = []
out.append(f"{'页面':<50}{'联盟链接':>9}{'待接入':>8}")
out.append('-' * 69)
zero = []
for r, l, pe in rows:
    flag = ''
    if l == 0:
        zero.append(r)
        flag = '   ← 零变现'
    out.append(f'{r:<50}{l:>9}{pe:>8}{flag}')
out.append('-' * 69)
out.append(f'共 {len(rows)} 个内容页，其中 {len(zero)} 个没有任何联盟链接')
out.append('')
out.append('零变现页面清单：')
for z in zero:
    out.append('  ' + z)

io.open('analysis/_affiliate_coverage.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written analysis/_affiliate_coverage.txt')
