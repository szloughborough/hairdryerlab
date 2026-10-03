"""把注入的 GA4 与 Clarity 脚本原文打出来，确认功能完好。"""
import io
import re

h = io.open('site/dist/index.html', encoding='utf-8').read()
head = h[:h.find('</head>')]

out = []
def W(*a): out.append(' '.join(str(x) for x in a))

W('=' * 88)
W('首页 <head> 里第三方脚本的完整原文')
W('=' * 88)
for m in re.finditer(r'<script[^>]*>(.*?)</script>', head, re.S):
    body = m.group(1)
    if 'googletagmanager' in m.group(0) or 'clarity' in body or 'dataLayer' in body:
        W(m.group(0)[:900])
        W('')

W('=' * 88)
W('功能完好性检查（容忍空白）')
W('=' * 88)

CHECKS = [
    ('Clarity 队列初始化 c[a].q=c[a].q', r'c\[a\]\s*\.\s*q\s*=\s*c\[a\]\s*\.\s*q'),
    ('Clarity 动态创建 script 标签', r'createElement\s*\(\s*r\s*\)'),
    ('Clarity 走 clarity.ms/tag/', r'clarity\.ms/tag/'),
    ('GA4 dataLayer 初始化', r'dataLayer'),
    ('GA4 gtag 调用 js + new Date', r"gtag\s*\(\s*'js'"),
    ('GA4 config 使用注入的 gaId', r"gtag\s*\(\s*'config'\s*,\s*gaId"),
    ('define:vars 注入 gaId 常量', r'const gaId\s*='),
    ('define:vars 注入 clarityId 常量', r'const clarityId\s*='),
]
for label, pat in CHECKS:
    ok = bool(re.search(pat, head))
    W(f'   {"OK      " if ok else "**缺失**"} {label}')

W('')
W('=' * 88)
W('规模')
W('=' * 88)
W(f'   <head> 内联脚本数: {len(re.findall(chr(60) + "script", head))}')
W(f'   <head> 字节数    : {len(head):,}')

io.open('analysis/_analytics_snippets.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written analysis/_analytics_snippets.txt')
