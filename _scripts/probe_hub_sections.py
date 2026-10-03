"""1) 打印 dyson-alternatives 的 related 块  2) 各栏目页正文章节（为卡片找位置）"""
import io
import os
import re

out = []
def W(*a): out.append(' '.join(str(x) for x in a))

W('=' * 90)
W('related 块实际内容')
W('=' * 90)
for p in (
    'site/src/content/best/dyson-alternatives.mdx',
    'deliverables/drafts/dyson-alternatives.mdx',
    'deliverables/drafts/best-dyson-alternatives-LAUNCH.mdx',
):
    if not os.path.exists(p):
        W(f'   {p}  —  不存在')
        continue
    t = io.open(p, encoding='utf-8').read()
    m = re.search(r'(?ms)^related:\n((?:[ \t]*-[ \t]*.+\n)+)', t)
    W(f'   {p}')
    W('      ' + (m.group(1).rstrip().replace('\n', '\n      ') if m else '(无 related)'))
    W('')

W('=' * 90)
W('栏目页正文章节')
W('=' * 90)
for p in (
    'site/src/content/learn/hair-types.mdx',
    'site/src/content/best/best-hair-dryers.mdx',
    'site/src/content/learn/guides.mdx',
):
    if not os.path.exists(p):
        W(f'   {p} — 不存在')
        continue
    t = io.open(p, encoding='utf-8').read()
    body = re.sub(r'(?s)^---.*?---', '', t)
    W(f'   === {os.path.basename(p)}')
    for m in re.findall(r'(?m)^(#{1,3}) (.+)$', body):
        W(f'      {"  " * (len(m[0]) - 2)}{m[1]}')
    W('')

W('=' * 90)
W('hair-types.mdx 里「Hair-type guides」表格原文')
W('=' * 90)
t = io.open('site/src/content/learn/hair-types.mdx', encoding='utf-8').read()
i = t.find('## Hair-type guides')
W(t[i:i + 1600] if i >= 0 else '未找到')

io.open('analysis/_hub_sections.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written analysis/_hub_sections.txt')
