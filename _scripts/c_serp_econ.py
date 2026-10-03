import pandas as pd, numpy as np, re

pd.set_option('display.width', 330)
pd.set_option('display.max_columns', 60)
pd.set_option('display.max_colwidth', 62)

m = pd.read_pickle('analysis/master.pkl')
m['kw'] = m['Keyword'].astype(str).str.lower().str.strip()
cat = m[(m['Volume'] > 0) & (m['Relevance'] >= 40)].copy()

# ---------------------------------------------------------------- relevance control
print("=" * 110)
print("I. RELEVANCE CONTROL -- how much of the 'category' pool is actually on-topic?")
print("=" * 110)
cat['rel_bucket'] = pd.cut(cat['Relevance'], [0, 50, 65, 80, 90, 101],
                           labels=['40-50', '51-65', '66-80', '81-90', '91-100'])
g = cat.groupby('rel_bucket', observed=True).agg(
    kws=('Volume', 'size'), volume=('Volume', 'sum'),
    med_KD=('KD', 'median'), avg_cpc=('CPC', 'mean')).round(2)
g['vol_%'] = (100 * g['volume'] / g['volume'].sum()).round(1)
print(g.to_string())
print("\n--> Relevance>=80 is the on-topic core; use that as the honest TAM.")

core = cat[cat['Relevance'] >= 80].copy()
print(f"\nON-TOPIC CORE (rel>=80): {len(core):,} kws, {int(core['Volume'].sum()):,} monthly searches (CA)")

print("\n" + "=" * 110)
print("J. ON-TOPIC CORE -- brand split")
print("=" * 110)
def seg(df, name, pat):
    s = df[df['kw'].str.contains(pat, na=False)]
    return {'segment': name, 'kws': len(s), 'volume': int(s['Volume'].sum()),
            'med_KD': s['KD'].median(), 'avg_cpc': round(s['CPC'].mean(), 2) if len(s) else 0}
segs = [
    seg(core, 'LAIFEN branded', 'laifen'),
    seg(core, 'dyson branded', 'dyson'),
    seg(core, 'shark branded', 'shark'),
    seg(core, 'other brands (ghd/t3/babyliss/revlon/conair/drybar)', r'\bghd\b|\bt3\b|babyliss|revlon|conair|drybar'),
    seg(core, 'dupe/alternative', r'dupe|alternative|similar to|like dyson|knock ?off'),
    seg(core, 'vs / comparison', r'\bvs\b|\bversus\b|compare'),
    seg(core, 'best / roundup', r'\bbest\b'),
    seg(core, 'review', r'review'),
    seg(core, 'buy / price / where', r'\bbuy\b|price|cost|where to|for sale|deal|coupon|discount'),
    seg(core, 'how to / guide', r'how to|tutorial|guide|tips'),
]
sd = pd.DataFrame(segs)
sd['vol_%'] = (100 * sd['volume'] / core['Volume'].sum()).round(2)
print(sd.sort_values('volume', ascending=False).to_string(index=False))
nb = core[~core['kw'].str.contains('laifen|dyson|shark|ghd|t3|babyliss|revlon|conair|drybar', na=False)]
print(f"\nNON-BRANDED core: {len(nb):,} kws, {int(nb['Volume'].sum()):,} vol "
      f"({100*nb['Volume'].sum()/core['Volume'].sum():.1f}%)")

# ---------------------------------------------------------------- SERP features
print("\n" + "=" * 110)
print("K. SERP FEATURE RISK -- what eats the clicks on the core terms?")
print("=" * 110)
FEATS = ['AI Overview', 'Popular products', 'People also ask', 'Video carousel', 'Short videos',
         'Image pack', 'Reviews', 'Sitelinks', 'Ads top', 'Ads bottom', 'Knowledge panel',
         'Discussions and forums', 'Related searches', 'Video', 'Image']
core['SERP'] = core['SERP'].fillna('')
rows = []
for f in FEATS:
    s = core[core['SERP'].str.contains(re.escape(f), na=False)]
    rows.append({'feature': f, 'kws': len(s), 'volume': int(s['Volume'].sum()),
                 'vol_%': round(100 * s['Volume'].sum() / core['Volume'].sum(), 1)})
fd = pd.DataFrame(rows).sort_values('volume', ascending=False)
print(fd.to_string(index=False))

print("\n--- Overlap: how many core searches face BOTH AI Overview and Popular products?")
both = core[core['SERP'].str.contains('AI Overview', na=False) & core['SERP'].str.contains('Popular products', na=False)]
print(f"{len(both):,} kws / {int(both['Volume'].sum()):,} vol "
      f"({100*both['Volume'].sum()/core['Volume'].sum():.1f}% of core demand)")
print("\n--- Commercial-intent core terms with AI Overview:")
comm = core[core['Intent'].fillna('').str.contains('Commercial|Transactional', na=False)]
comm_ai = comm[comm['SERP'].str.contains('AI Overview', na=False)]
print(f"commercial kws: {len(comm):,} (vol {int(comm['Volume'].sum()):,})")
print(f"  with AI Overview: {len(comm_ai):,} (vol {int(comm_ai['Volume'].sum()):,}) "
      f"= {100*comm_ai['Volume'].sum()/comm['Volume'].sum():.1f}% of commercial demand")

# ---------------------------------------------------------------- CPA / CPC economics
print("\n" + "=" * 110)
print("L. CPC ECONOMICS -- affiliate revenue proxy")
print("=" * 110)
cc = comm[(comm['CPC'] > 0)]
print(f"commercial core kws with CPC>0: {len(cc):,}")
print(cc['CPC'].describe(percentiles=[.25, .5, .75, .9, .95]).round(2).to_string())
print("\nCPC buckets (commercial core):")
cb = pd.cut(cc['CPC'], [0, .1, .25, .5, 1, 2, 5, 100],
            labels=['0-.10', '.10-.25', '.25-.50', '.50-1', '1-2', '2-5', '5+'])
print(cc.groupby(cb, observed=True).agg(kws=('CPC', 'size'), vol=('Volume', 'sum'),
                                        medvol=('Volume', 'median')).to_string())
print("\nHigh-CPC core terms (monetization quality check):")
print(cc.nlargest(25, 'CPC')[['Keyword', 'Volume', 'CPC', 'KD', 'Intent']].to_string(index=False))

print("\n" + "=" * 110)
print("M. LAIFEN-BRANDED DEMAND QUALITY (the affiliate's warmest traffic)")
print("=" * 110)
la = core[core['kw'].str.contains('laifen', na=False)]
print(f"laifen core kws: {len(la)}, volume {int(la['Volume'].sum()):,}, "
      f"median KD {la['KD'].median()}, avg CPC ${la['CPC'].mean():.2f}")
print("\nlaifen intent split:")
print(la['Intent'].fillna('(none)').value_counts().to_string())
print("\nlaifen KD distribution (known only):")
print(la['KD'].dropna().describe().round(1).to_string())
