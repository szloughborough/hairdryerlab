"""验证生成的 llms.txt：所有 URL 是否都有对应产物；并统计分组。"""
import io
import os
import re

D = 'site/dist'
t = io.open(f'{D}/llms.txt', encoding='utf-8').read()
out = []
def W(*a): out.append(' '.join(str(x) for x in a))

urls = re.findall(r'\((https://hairdryerlab\.ca/[^)]*)\)', t)
W(f'llms.txt 里的链接总数: {len(urls)}')
W('')

missing = []
for u in urls:
    path = u.replace('https://hairdryerlab.ca', '').strip('/')
    target = os.path.join(D, path, 'index.html') if path else os.path.join(D, 'index.html')
    if not os.path.isfile(target):
        missing.append(u)

if missing:
    W(f'!! 有 {len(missing)} 个链接没有对应产物：')
    for u in missing:
        W(f'   {u}')
else:
    W('全部链接都有对应产物 OK')

W('')
W('=== 分组统计 ===')
for m in re.finditer(r'(?m)^## (.+)$', t):
    title = m.group(1)
    rest = t[m.end():]
    nxt = re.search(r'(?m)^## ', rest)
    seg = rest[:nxt.start()] if nxt else rest
    n = len(re.findall(r'^- \[', seg, re.M))
    W(f'   {title:<34} {n:>3} 项')

W('')
W('=== 是否还有旧分类法残留 ===')
old = re.findall(r'/(?:best-hair-dryer|laifen-vs|shark-vs|learn|for|ca)/', t)
W(f'   旧 URL 出现: {len(old)} 处 {"OK" if not old else old[:6]}')

io.open('analysis/_llms_verify.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written analysis/_llms_verify.txt')
