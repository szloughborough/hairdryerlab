"""给 how-we-test.mdx 打开 Newsletter 区块（§55(22)）。"""
import io
import re

P = 'deliverables/drafts/how-we-test.mdx'
t = io.open(P, encoding='utf-8').read()

if re.search(r'(?m)^newsletter:', t):
    print('已有 newsletter 字段，跳过')
else:
    # 插到 frontmatter 结束的 --- 之前
    m = re.search(r'(?m)^---\s*$', t)
    m2 = re.search(r'(?m)^---\s*$', t[m.end():])
    close = m.end() + m2.start()
    t2 = t[:close] + 'newsletter: true\n' + t[close:]
    io.open(P, 'w', encoding='utf-8').write(t2)
    print('已给 how-we-test.mdx 加上 newsletter: true')
