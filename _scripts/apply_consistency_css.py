"""
把首页确立的设计语言下沉到全站共享组件层。

只做精确替换，每一条都打印命中情况；任何未命中都会报出来，不会静默跳过。
仅使用品牌规范既有 token，不新增色值。
"""
import io

P = 'site/src/styles/global.css'
css = io.open(P, encoding='utf-8').read()

EDITS = [
    # ---- 1) §17 违规：H3 应为 24px ----
    (
        '.proscons h3 { margin-top: 0; font-size: 18px; }',
        "/* §17 H3 = 24px。原本 18px，低于规范。 */\n"
        ".proscons h3 { margin-top: 0; font-size: 24px; }",
        'proscons h3 → 24px',
    ),
    (
        '.pick-body h3 { margin: 0 0 var(--s1); font-size: 20px; }',
        "/* §17 H3 = 24px。原本 20px，低于规范。 */\n"
        ".pick-body h3 { margin: 0 0 var(--s1); font-size: 24px; }",
        'pick-body h3 → 24px',
    ),

    # ---- 2) 层级塌陷：真正的 <h2> 被渲染成 13px 小标签 ----
    (
        ".picks > h2 {\n"
        "  font-size: 13px; text-transform: uppercase; letter-spacing: 0.1em;\n"
        "  color: var(--hdl-text-secondary); margin: 0 0 var(--s4); font-weight: 700;\n"
        "}",
        "/* §17 H2 = 34px。这里曾是 13px 大写标签 —— 一个真正的 <h2> 被渲染成\n"
        "   小标签，与首页改版前同一类层级塌陷问题。 */\n"
        ".picks > h2 {\n"
        "  font-size: 34px; line-height: 1.2; letter-spacing: -0.015em;\n"
        "  color: var(--hdl-navy); margin: 0 0 var(--s5); font-weight: 700;\n"
        "}",
        'picks > h2 → 34px 真标题',
    ),

    # ---- 3) 卡片网格：5 列太挤，与首页 3 列卡片语言不一致 ----
    (
        '.picks-grid { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: var(--s4); }',
        "/* 与首页 .models 一致改为 3 列。5 列时每张卡仅约 227px，标题只能压到 14px，\n"
        "   且 6 个产品的页面会在第二行留下孤卡。 */\n"
        ".picks-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: var(--s4); }",
        'picks-grid 5 → 3 列',
    ),
    (
        '@media (max-width: 900px) { .picks-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); } }',
        '@media (max-width: 900px) { .picks-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }',
        '@900px picks-grid 3 → 2 列',
    ),
    (
        '@media (max-width: 560px) { .picks-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }',
        '@media (max-width: 560px) { .picks-grid { grid-template-columns: 1fr; } }',
        '@560px picks-grid 2 → 1 列',
    ),

    # ---- 4) 卡片标题字号：3 列后不再需要压到 14px ----
    (
        ".pick-card-body strong { font-family: 'Manrope', sans-serif; font-size: 14px; line-height: 1.3; color: var(--hdl-navy); }",
        "/* 3 列布局后卡片标题有空间了；14px 在 227px 卡里勉强，在 390px 卡里过小。 */\n"
        ".pick-card-body strong { font-family: 'Manrope', sans-serif; font-size: 20px; line-height: 1.25; color: var(--hdl-navy); }",
        'pick-card 标题 14 → 20px',
    ),

    # ---- 5) 作者框：与首页「How We Work」统一为 2px navy 顶线 ----
    (
        ".authorbox {\n"
        "  border: 1px solid var(--hdl-border); border-radius: var(--hdl-radius-md);\n"
        "  background: var(--hdl-white); padding: var(--s5);\n"
        "  margin: var(--s7) 0 0; font-size: 15px;\n"
        "}",
        "/* 与首页「How We Work」三栏统一：讲我们自己的内容用 2px navy 顶线，\n"
        "   卡片边框留给产品与数据，避免整页都是同一种盒子。 */\n"
        ".authorbox {\n"
        "  border-top: 2px solid var(--hdl-navy);\n"
        "  padding: var(--s5) 0 0;\n"
        "  margin: var(--s7) 0 0; font-size: 15px;\n"
        "}",
        'authorbox → 2px navy 顶线',
    ),

    # ---- 6) 新增数据核对徽章（替代虚假的「Tested」） ----
    (
        '.badge--updated { background: var(--hdl-white); }',
        '.badge--updated { background: var(--hdl-white); }\n'
        '/* 数据核对日期徽章。替代此前全站 43 个页面上的「Tested」徽章 ——\n'
        '   本站尚未完成任何台架实测，那个徽章是虚假声称。 */\n'
        '.badge--data { background: var(--hdl-white); color: var(--hdl-navy); border-color: var(--hdl-border); }',
        'badge--data 新增',
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

if not missing:
    io.open(P, 'w', encoding='utf-8', newline='\n').write(css)

print(f'编辑 {len(EDITS)} 条，命中 {len(EDITS) - len(missing)}，未命中 {len(missing)}')
print('\n'.join(report))
if missing:
    print('\n未命中项（未写入文件）：')
    for m in missing:
        print(f'   {m}')
else:
    print('\n文件已写入')
    raw = io.open(P, 'rb').read()
    try:
        raw.decode('utf-8')
        print('编码校验: 合法 UTF-8')
    except UnicodeDecodeError as e:
        print(f'编码校验: **非法字节 @ {e.start}**')

io.open('analysis/_css_consistency.txt', 'w', encoding='utf-8').write(
    f'edits={len(EDITS)} hit={len(EDITS)-len(missing)} miss={len(missing)}\n' + '\n'.join(report))
