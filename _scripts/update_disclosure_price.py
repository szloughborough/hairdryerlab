"""更新联盟披露页中关于价格的表述（方案 B 后已不再展示精确价）。"""
import io

P = 'deliverables/drafts/affiliate-disclosure.mdx'
t = io.open(P, encoding='utf-8').read()

FIXES = [
    ('- **We do not claim a price is permanent.** Every price carries the date we verified it',
     '- **We do not display current prices.** Prices on this site are approximate figures from '
     'our own research, not live retailer pricing — the price that applies is the one on the '
     'retailer page when you buy'),
    ('prices carry the **date we verified them**, because a price without a date is not information',
     'prices are shown as **approximations**, because a figure presented as current is a claim '
     'we cannot keep accurate'),
]

n = 0
for old, new in FIXES:
    if old in t:
        t = t.replace(old, new, 1)
        n += 1
    else:
        print(f'  !! 未找到: {old[:70]}')

# 追加一节，说明价格展示政策
SECTION = """
---

## Why we show approximate prices

**Amazon Associates requires that any Amazon price you display must be current.** They publish that rule because a stale price misleads buyers, and we agree with the reasoning.

**We do not have a live price feed.** The prices in our guides come from our own research at a stated check date, so presenting them as exact current prices would be a claim we cannot keep accurate. Instead:

- **Prices are shown as approximations** — "about C$100" rather than a figure to the cent
- **The exact figure still drives our analysis internally**, which is why we can still tell you a dryer costs roughly four times another
- **The price that applies is the one on the retailer page** when you buy, and that is where our links take you
- **We do not run a price-tracking feed**, and we will not imply we do

**What this changes for you.** If you are comparing two dryers where the price difference matters to your decision, check both on the retailer page — our approximations are good enough for judging which price band a product sits in, and not precise enough to be a quote.
"""

if '## Why we show approximate prices' not in t:
    t = t.rstrip() + '\n' + SECTION
    n += 1

io.open(P, 'w', encoding='utf-8').write(t)
print(f'affiliate-disclosure.mdx: {n} 处更新')
