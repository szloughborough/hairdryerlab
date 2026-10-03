"""补 dyson-alternatives 页的 frontmatter（真实文件名与 slug 不同）。"""
import io
import re

P = 'deliverables/drafts/best-dyson-alternatives-LAUNCH.mdx'
t = io.open(P, encoding='utf-8').read()

if re.search(r'(?m)^bestFor:', t):
    print('已有 bestFor，跳过')
else:
    block = (
        'bestFor: "Buyers who want the Supersonic\'s high-airflow approach without paying about C$400 or more."\n'
        'skipIf: "A failure at month six would be a serious financial problem, or you need universal voltage."\n'
        'ratings:\n'
        '  - label: "Value"\n'
        '    grade: "Excellent"\n'
        '  - label: "Heat control"\n'
        '    grade: "Very Good"\n'
        '  - label: "Attachments"\n'
        '    grade: "Good"\n'
        '  - label: "Durability evidence"\n'
        '    grade: "Limited"\n'
    )
    m = re.search(r'(?m)^---\s*$', t)
    m2 = re.search(r'(?m)^---\s*$', t[m.end():])
    close = m.end() + m2.start()
    io.open(P, 'w', encoding='utf-8').write(t[:close] + block + t[close:])
    print('已补入 best-dyson-alternatives-LAUNCH.mdx')
