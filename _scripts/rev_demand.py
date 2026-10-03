"""Cross-reference review-derived concerns with actual search demand (Semrush CA)."""
import re, io
import pandas as pd, numpy as np

m = pd.read_pickle('analysis/master.pkl')
m['kw'] = m['Keyword'].astype(str).str.lower().str.strip()

def vol(pat, minvol=0):
    s = m[m['kw'].str.contains(pat, regex=True, na=False) & (m['Volume'] >= minvol)]
    kd = s[s['KD'].notna()]['KD']
    return len(s), int(s['Volume'].sum()), (round(kd.median(), 1) if len(kd) else np.nan), s

# review-derived concern | review mentions | keyword patterns
CONCERNS = [
    ('旅行/电压能用吗',        785,
     r'travel hair dryer|dual voltage|voltage hair dryer|220v hair dryer|hair dryer for travel'),
    ('噪音大不大',            731,
     r'quiet hair dryer|silent hair dryer|how loud|noise hair dryer|low noise'),
    ('能用多久/寿命',          433,
     r'how long.*hair dryer|hair dryer lifespan|hair dryer last|long lasting hair dryer|durable hair dryer'),
    ('适合细软/粗硬发',        244,
     r'fine hair|thin hair|thick hair|coarse hair'),
    ('和 Dyson 比',           192,
     r'dyson (dupe|alternative|vs)|like dyson|similar to dyson|dyson supersonic'),
    ('风嘴/扩散器老掉',        186,
     r'diffuser.*(attach|fit|stay)|nozzle|attachment.*(compat|fit)|magnetic'),
    ('烧焦味/冒烟',            143,
     r'burning smell|hair dryer smell|smoke|burnt smell'),
    ('太烫/烫头皮',            137,
     r'too hot|overheat|heat damage|scalp|temperature control|heat setting'),
    ('冷风按钮不管用',         124,
     r'cold shot|cool shot|cool air'),
    ('坏了怎么办/保修',        119,
     r'warranty|guarantee|hair dryer repair| hair dryer broke|return policy'),
    ('滤网能否拆洗',           102,
     r'filter|removable filter|clean hair dryer|hair dryer maintenance'),
    ('安全吗/插头认证',         98,
     r'safe hair dryer|safety|alci|csa approved|ul certified'),
    ('重量/手持累不累',        1318,
     r'lightweight hair dryer|light weight hair dryer|how much does.*weigh'),
    ('功率/干得快不快',        1585,
     r'powerful hair dryer|fast hair dryer|fastest hair dryer|high speed hair dryer|watt'),
]

out = []
def P(*a): out.append(' '.join(str(x) for x in a))

P("=" * 128)
P("★ 核心表：消费者诉求（评论）× 搜索需求（Semrush CA）")
P("=" * 128)
P("逻辑：评论提及数 = 真实痛点强度；关键词搜索量 = 该痛点的流量价值。两者都高 = 必做内容。")
P("")
P(f"{'消费者诉求':<22}{'评论提及':>8}{'相关词数':>9}{'月搜索量':>10}{'中位KD':>8}  判断")
P("-" * 128)
rows = []
for name, rev_mentions, pat in CONCERNS:
    n, v, kd, s = vol(pat)
    if not n:
        verdict = '无搜索需求'
    elif v >= 3000 and (pd.isna(kd) or kd <= 35):
        verdict = '★必做(高需求+可排名)'
    elif v >= 3000:
        verdict = '必做(高需求,但KD高)'
    elif v >= 500:
        verdict = '做(中需求)'
    else:
        verdict = '低需求/长尾'
    rows.append({'消费者诉求': name, '评论提及数': rev_mentions, '相关关键词数': n,
                 '月搜索量': v, '中位KD': kd, '判断': verdict})
    P(f"{name:<22}{rev_mentions:>8,}{n:>9,}{v:>10,}"
      f"{('' if pd.isna(kd) else f'{kd:.0f}'):>8}  {verdict}")

X = pd.DataFrame(rows)
P("\n" + "=" * 128)
P("★ 结论：评论痛点 × 搜索需求的交集 = 内容优先级")
P("=" * 128)
hi = X[(X['评论提及数'] >= 100) & (X['月搜索量'] >= 500)].sort_values('月搜索量', ascending=False)
P("\n【双重验证：痛点强 + 有搜索量】—— 这些必须写进文章核心结构")
for _, r in hi.iterrows():
    P(f"  • {r['消费者诉求']:<22} 评论{r['评论提及数']:>5,}条 | 搜索{r['月搜索量']:>7,}/月 | {r['判断']}")

P("\n【痛点极强但搜索量低】—— 用 FAQ / 正文小节承接，不做独立页")
lo = X[(X['评论提及数'] >= 100) & (X['月搜索量'] < 500)].sort_values('评论提及数', ascending=False)
for _, r in lo.iterrows():
    P(f"  • {r['消费者诉求']:<22} 评论{r['评论提及数']:>5,}条 | 搜索{r['月搜索量']:>7,}/月")

# ---------- check specific high-pain long-tails ----------
P("\n" + "=" * 128)
P("★ 高痛点长尾词核查（评论说的问题，有没有人在搜）")
P("=" * 128)
CHECK = [
    'hair dryer burning smell', 'hair dryer smell', 'hair dryer smoking',
    'how long does a hair dryer last', 'hair dryer lifespan',
    'hair dryer overheating', 'hair dryer too hot',
    'hair dryer diffuser falls off', 'hair dryer filter cleaning',
    'dual voltage hair dryer', 'travel hair dryer', 'hair dryer for europe',
    'quiet hair dryer', 'lightweight hair dryer', 'fastest hair dryer',
    'hair dryer not turning on', 'hair dryer stopped working', 'hair dryer repair',
    'best hair dryer that lasts', 'most durable hair dryer',
    'cold shot hair dryer', 'hair dryer with cool shot',
    'best hair dryer for fine hair', 'best hair dryer for thick hair',
]
found = []
for k in CHECK:
    s = m[m['kw'] == k]
    if len(s):
        r = s.iloc[0]
        found.append((k, int(r['Volume']), r['KD'], r['CPC']))
    else:
        # partial
        s2 = m[m['kw'].str.contains(re.escape(k), na=False) & (m['Volume'] > 0)]
        if len(s2):
            r = s2.sort_values('Volume', ascending=False).iloc[0]
            found.append((k + ' →(近似) ' + str(r['Keyword']), int(r['Volume']), r['KD'], r['CPC']))
        else:
            found.append((k, 0, np.nan, np.nan))
Fd = pd.DataFrame(found, columns=['查询词', '月搜索量', 'KD', 'CPC'])
P(Fd.to_string(index=False))

with io.open('analysis/_rev_demand.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
X.to_pickle('analysis/rev_demand.pkl')
print("written analysis/_rev_demand.txt")
