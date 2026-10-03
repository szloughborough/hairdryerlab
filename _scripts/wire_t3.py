"""T3 本批收尾：修 H2 实体 + 更新栏目页把新页面标为已发布。"""
import io

EDITS = {
    # H2 补实体
    'deliverables/drafts/remington.mdx': [
        ('## Why 48,228 ratings with only 319 units a month',
         '## Why Remington has 48,228 ratings but only 319 units a month'),
    ],
    # reviews 栏目页：补 3 个品牌
    'deliverables/drafts/reviews.mdx': [
        ('| **wavytalk** | 1875W | [Full review](/reviews/wavytalk/) — the second-largest review base in Canada at 32,950 ratings |',
         '| **wavytalk** | 1875W | [Full review](/reviews/wavytalk/) — the second-largest review base in Canada at 32,950 ratings |\n'
         '| **Revlon** | RVDR5034F | [Full review](/reviews/revlon/) — ~12% of Canadian units, at C$18.99 |\n'
         '| **Aina** | Diffuser Dryer | [Full review](/reviews/aina/) — BSR #2, and a brand-operated listing at C$25.99 |\n'
         '| **Remington** | 2 models | [Full review](/reviews/remington/) — 48,228 ratings, the largest review base we track |'),
        ('**Every brand in our dataset now has a dedicated review.** If a model you are considering is missing — Revlon, Remington and Aina all appear in our category analysis without their own pages yet — email editorial@hairdryerlab.ca.',
         '**Every brand in our dataset now has a dedicated review.** Ten brands are covered: Laifen, Dyson, Slopehill, Conair, Dreame, Shark, wavytalk, Revlon, Aina and Remington. If a model you are considering is missing, email editorial@hairdryerlab.ca — but note that our dataset covers the Amazon.ca **Hair Dryers** category only, so hot air brush stylers are outside it entirely.'),
    ],
    # hair-types 栏目页：补 damaged-hair
    'deliverables/drafts/hair-types.mdx': [
        ('| **[Quiet hair dryer](/hair-types/quiet-hair-dryer/)** | **Published** | Why no brand publishes a measured decibel figure, and how to compare yourself |',
         '| **[Quiet hair dryer](/hair-types/quiet-hair-dryer/)** | **Published** | Why no brand publishes a measured decibel figure, and how to compare yourself |\n'
         '| **[Damaged or colour-treated hair](/hair-types/damaged-hair/)** | **Published** | Heat control, and the repair claims we will not make |'),
    ],
    # guides 栏目页：补 dual-voltage
    'deliverables/drafts/guides.mdx': [
        ('| **Dual voltage and travel** | Which dryers work abroad, and what an adapter cannot fix | Covered in our [travel guide](/hair-types/travel-hair-dryer/) |',
         '| **[Dual voltage hair dryer](/guides/dual-voltage/)** | What dual voltage means, and why an adapter is not a converter | **Published** |'),
    ],
}

for path, edits in EDITS.items():
    t = io.open(path, encoding='utf-8').read()
    n = 0
    for old, new in edits:
        if old in t:
            t = t.replace(old, new, 1)
            n += 1
        else:
            print(f'  !! 未找到于 {path.split("/")[-1]}: {old[:60]}')
    if n:
        io.open(path, 'w', encoding='utf-8').write(t)
    print(f'{path.split("/")[-1]:<26} 改了 {n} 处')
