"""本批 5 篇上线收尾：更新栏目页 + 补交叉内链。"""
import io

EDITS = {
    # guides 栏目页：把 2 个新指南从未发布改为已发布
    'deliverables/drafts/guides.mdx': [
        ('| **How many watts do you need?** | Why wattage is not drying speed, and what to compare instead | In progress |',
         '| **[How many watts does a hair dryer need?](/guides/how-many-watts/)** | Why wattage is not drying speed, and what to compare instead | **Published** |'),
        ('| **Hair dryer care and maintenance** | Filter cleaning, cord strain relief, and how to make one last longer | Covered in our [durability guide](/guides/how-long-does-a-hair-dryer-last/) |',
         '| **[Hair dryer care and maintenance](/guides/hair-dryer-care/)** | Filter cleaning, cord strain relief, and how to make one last longer | **Published** |'),
    ],
    # hair-types 栏目页：补 quiet 页
    'deliverables/drafts/hair-types.mdx': [
        ('| **[Travel hair dryer](/hair-types/travel-hair-dryer/)** | **Published** | Dual voltage, what an adapter cannot fix, four models |',
         '| **[Travel hair dryer](/hair-types/travel-hair-dryer/)** | **Published** | Dual voltage, what an adapter cannot fix, four models |\n'
         '| **[Quiet hair dryer](/hair-types/quiet-hair-dryer/)** | **Published** | Why no brand publishes a measured decibel figure, and how to compare yourself |'),
    ],
    # 耐用性指南 → 保养指南（自然交叉）
    'deliverables/drafts/how-long-does-a-hair-dryer-last.mdx': [
        ('**2. Keep the rear intake clear.**',
         'Our [hair dryer care and maintenance guide](/guides/hair-dryer-care/) covers the full routine.\n\n'
         '**2. Keep the rear intake clear.**'),
    ],
    # 粗硬发质 → 快速干发 + wattage
    'deliverables/drafts/thick-hair.mdx': [
        ('See our [thick hair guide](/hair-types/thick-hair/)',
         'See our [thick hair guide](/hair-types/thick-hair/)'),
    ],
    # 细软发质 → quiet 页（细软发常关心噪音/温和）
    'deliverables/drafts/fine-hair.mdx': [
        ('**Skip if:** you want active heat sensing rather than a lower-heat design — that is the Dyson Nural below.',
         '**Skip if:** you want active heat sensing rather than a lower-heat design — that is the Dyson Nural below. '
         'If noise matters to you as well, our [quiet hair dryer guide](/hair-types/quiet-hair-dryer/) explains why no brand publishes a measured figure.'),
    ],
    # 支柱榜单 → under-150（价格带筛选意图）
    'deliverables/drafts/best-hair-dryers.mdx': [
        ('related:',
         'related:'),
    ],
}

for path, edits in EDITS.items():
    t = io.open(path, encoding='utf-8').read()
    n = 0
    for old, new in edits:
        if old == new:
            continue
        if old in t:
            t = t.replace(old, new, 1)
            n += 1
        else:
            print(f'  !! 未找到于 {path.split("/")[-1]}: {old[:55]}')
    if n:
        io.open(path, 'w', encoding='utf-8').write(t)
    print(f'{path.split("/")[-1]:<34} 改了 {n} 处')
