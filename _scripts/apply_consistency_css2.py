"""
收尾一致性修正：
  1. .toc h2 → .toc__title（Toc.astro 已把 <h2> 改成 <p>）
  2. .footer-cols h3 → .footer-col__title（Footer.astro 已改成 <p> + <nav>）
  3. 删除已无引用的 .pillar-grid / .pillar-card（死 CSS，产物 0/45 页出现）
"""
import io
import re

P = 'site/src/styles/global.css'
css = io.open(P, encoding='utf-8').read()

EDITS = [
    (
        ".toc h2 {\n"
        "  font-size: 13px; margin: 0 0 var(--s3); text-transform: uppercase;\n"
        "  letter-spacing: 0.08em; color: var(--hdl-text-secondary); font-weight: 700;\n"
        "}",
        "/* 这里曾经匹配 .toc h2，把「On this page」这个真 <h2> 渲染成 13px。\n"
        "   它已改为 <p class=\"toc__title\"> —— 是导航区块的标签，不是文档章节。 */\n"
        ".toc__title {\n"
        "  font-family: 'Manrope', sans-serif;\n"
        "  font-size: 12px; margin: 0 0 var(--s3); text-transform: uppercase;\n"
        "  letter-spacing: 0.1em; color: var(--hdl-text-secondary); font-weight: 700;\n"
        "}",
        'toc h2 → .toc__title',
    ),
    (
        ".footer-cols h3 {\n"
        "  font-size: 12px; text-transform: uppercase; letter-spacing: 0.1em;\n"
        "  color: var(--hdl-text-secondary); margin: 0 0 var(--s3); font-weight: 700;\n"
        "}",
        "/* 这里曾经匹配 .footer-cols h3，把三个页脚 <h3> 渲染成 12px。\n"
        "   它们已改为 <p class=\"footer-col__title\">，导航组用 <nav aria-labelledby>。 */\n"
        ".footer-col__title {\n"
        "  font-family: 'Manrope', sans-serif;\n"
        "  font-size: 12px; text-transform: uppercase; letter-spacing: 0.1em;\n"
        "  color: var(--hdl-text-secondary); margin: 0 0 var(--s3); font-weight: 700;\n"
        "}",
        'footer-cols h3 → .footer-col__title',
    ),
]

report = []
missing = []
for old, new, label in EDITS:
    if old in css:
        css = css.replace(old, new, 1)
        report.append(f'   OK      {label}')
    else:
        missing.append(label)
        report.append(f'   MISSED  {label}')

# ---- 删除死 CSS ----
DEAD = re.compile(
    r'\n\.pillar-grid \{[^}]*\}\n'
    r'\.pillar-card \{[^}]*\}\n'
    r'\.pillar-card:hover \{[^}]*\}\n'
    r'\.pillar-card h3 \{[^}]*\}\n'
    r'\.pillar-card p \{[^}]*\}\n'
    r'@media \(max-width: 900px\) \{ \.pillar-grid \{[^}]*\} \}\n'
    r'@media \(max-width: 560px\) \{ \.pillar-grid \{[^}]*\} \}\n'
)
if DEAD.search(css):
    css = DEAD.sub(
        "\n/* .pillar-grid / .pillar-card 已删除：首页改版后无任何页面引用，\n"
        "   实测产物中 0/45 页出现，属死 CSS。 */\n",
        css,
    )
    report.append('   OK      。pillar-* 死 CSS 已删除')
else:
    report.append('   MISSED  .pillar-* 死 CSS（正则未匹配，需手工处理）')
    missing.append('pillar dead css')

if not missing:
    io.open(P, 'w', encoding='utf-8', newline='\n').write(css)
    print('全部命中，文件已写入')
else:
    print('有未命中项，未写入文件')

print('\n'.join(report))

# 残留检查
left = [s for s in ('.toc h2', '.footer-cols h3', '.pillar-card', '.pillar-grid') if s in css]
print()
print(f'残留旧选择器: {left if left else "无"}')
if not missing:
    raw = io.open(P, 'rb').read()
    try:
        raw.decode('utf-8')
        print('编码校验: 合法 UTF-8')
    except UnicodeDecodeError as e:
        print(f'编码校验: **非法字节 @ {e.start}**')
