"""查找联盟披露页里所有关于价格的表述。"""
import io

t = io.open('deliverables/drafts/affiliate-disclosure.mdx', encoding='utf-8').read()
for i, line in enumerate(t.splitlines(), 1):
    low = line.lower()
    if 'price' in low or 'verified' in low or 'c$' in low:
        print(f'L{i}: {line.strip()[:210]}')
