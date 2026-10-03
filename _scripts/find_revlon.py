"""定位 revlon.mdx 里 about C$19 的实际写法。"""
import io

t = io.open('deliverables/drafts/revlon.mdx', encoding='utf-8').read()
hits = 0
for i, line in enumerate(t.splitlines(), 1):
    if 'C$19' in line or 'about C$' in line and '19' in line:
        print(f'L{i}: {line!r}'[:220])
        hits += 1
print(f'--- {hits} hits')
