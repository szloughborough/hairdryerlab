"""
把指向「尚未撰写页面」的站内链接重映射到已存在的最近页面，消除死链。
幂等：可重复执行。

背景：文章里为将来内容预留了链接，但这些页面还没写。上线前不能留死链。
将来页面写好后再把具体链接换回来即可（映射表在下方，反向替换即可）。
"""
import io, os, re

DRAFTS = 'deliverables/drafts'

# 未写页面 → 已存在的最近页面
REMAP = [
    # 品牌/型号评测 → 品牌枢纽或评测栏目
    (r'/reviews/laifen/air/', '/reviews/laifen/'),
    (r'/reviews/laifen/se2/', '/reviews/laifen/'),
    (r'/reviews/dreame/', '/reviews/'),
    (r'/reviews/slopehill/', '/reviews/'),
    (r'/reviews/wavytalk/', '/reviews/'),
    (r'/reviews/conair/', '/reviews/'),
    # 发质页 → 发质栏目
    (r'/hair-types/curly-hair/', '/hair-types/'),
    (r'/hair-types/fine-hair/', '/hair-types/'),
    (r'/hair-types/thick-hair/', '/hair-types/'),
    (r'/hair-types/frizzy-hair/', '/hair-types/'),
    (r'/hair-types/travel-hair-dryer/', '/hair-types/'),
    (r'/hair-types/quiet-hair-dryer/', '/hair-types/'),
    (r'/hair-types/diffuser/', '/hair-types/'),
    # 指南页 → 指南栏目
    (r'/guides/how-long-does-a-hair-dryer-last/', '/guides/'),
    (r'/guides/hair-dryer-care/', '/guides/'),
    # 加拿大购买类 → 已有的加拿大购买指南
    (r'/best-hair-dryers/where-to-buy-laifen-canada/', '/best-hair-dryers/best-hair-dryer-canada/'),
    (r'/best-hair-dryers/hair-dryer-sale-canada/', '/best-hair-dryers/best-hair-dryer-canada/'),
    # 需求类榜单 → 榜单支柱
    (r'/best-hair-dryers/fast-drying/', '/best-hair-dryers/'),
    (r'/best-hair-dryers/best-lightweight-hair-dryer/', '/best-hair-dryers/'),
    (r'/best-hair-dryers/best-travel-hair-dryer/', '/best-hair-dryers/'),
    (r'/best-hair-dryers/under-150/', '/best-hair-dryers/'),
    (r'/best-hair-dryers/premium/', '/best-hair-dryers/'),
    # 旧 URL（仅出现在 404 页）
    (r'/best-dyson-alternatives/', '/best-hair-dryers/dyson-alternatives/'),
]

changed = {}
for fn in sorted(os.listdir(DRAFTS)):
    if not fn.endswith('.mdx'):
        continue
    p = os.path.join(DRAFTS, fn)
    t = io.open(p, encoding='utf-8').read()
    orig = t
    n = 0
    for pat, rep in REMAP:
        t, k = re.subn(pat, rep, t)
        n += k
    if t != orig:
        io.open(p, 'w', encoding='utf-8').write(t)
        changed[fn] = n

print('重映射的草稿：')
for fn, n in changed.items():
    print(f'  {fn:<36} {n} 处')
print(f'合计 {sum(changed.values())} 处')
