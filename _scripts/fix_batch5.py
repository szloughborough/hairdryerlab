"""本批 5 篇的收尾修正：H2 补核心实体 + 补内链。"""
import io

EDITS = {
    'deliverables/drafts/under-150.mdx': [
        ('## Under C$150 comparison table',
         '## Hair dryer comparison table under C$150'),
        ('## Why the C$120 line matters more than the C$150 line',
         '## Why the C$120 line matters more than the C$150 line for hair dryers'),
        ('## What to check on arrival, whichever you buy',
         '## What to check on arrival, whichever hair dryer you buy'),
        ('## Frequently asked questions',
         '## Best hair dryer under C$150: FAQ'),
    ],
    'deliverables/drafts/fast-drying.mdx': [
        ('## Fast drying comparison table',
         '## Fast-drying hair dryer comparison table'),
        ('## Why airflow beats wattage for drying speed',
         '## Why airflow beats wattage for hair dryer speed'),
        ('## Does a fast dryer damage hair?',
         '## Does a fast-drying hair dryer damage hair?'),
        ('## How to dry faster without buying anything',
         '## How to dry hair faster without buying a hair dryer'),
        ('## Frequently asked questions',
         '## Fast-drying hair dryer: FAQ'),
    ],
    'deliverables/drafts/hair-dryer-care.mdx': [
        ('**The full failure-mode analysis',
         '**If you are choosing a replacement rather than maintaining one**, our '
         '[best hair dryers guide](/best-hair-dryers/) ranks models on the price-band '
         'complaint rate this page keeps referring to. **The full failure-mode analysis'),
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
            print(f'  !! 未找到: {old[:60]}')
    io.open(path, 'w', encoding='utf-8').write(t)
    print(f'{path.split("/")[-1]:<26} 改了 {n} 处')
