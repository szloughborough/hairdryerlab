"""
Clean, business-relevant keyword sets.
Semrush broad-match drags in whole-brand noise (dyson vacuum, dehumidifier, paklaptop).
We filter to keywords that are genuinely about a hair dryer / hair-dryer-adjacent purchase.
"""
import pandas as pd, numpy as np, re

pd.set_option('display.width', 340)
pd.set_option('display.max_columns', 60)
pd.set_option('display.max_colwidth', 70)

out = pd.read_pickle('analysis/scored.pkl')
out['kw'] = out['Keyword'].astype(str).str.lower().str.strip()

CORE_PAT = (r'hair ?dry|blow ?dry|blowdry|hair ?dryer|hairdry|sechoir|seche cheveux|'
            r'diffus|airwrap|air wrap|flexstyle|speedstyle|airstrait|supersonic|helios|'
            r'laifen|ion hair|hair ion|dryer for hair|hair.?dryer')
OFF_PAT = (r'vacuum|vaccum|purifier|humidifier|dehumidifier|fan\b|heater|air ?puri|'
           r'straightener|flat iron|curling iron|curler|toothbrush|shaver|razor|laptop|'
           r'paklaptop|filter|robot|light\b|lamp|tv\b|headphone|dryer for (clothes|paint)|'
           r'clothes dryer|paint|nail|makeup|skincare|blender|kettle|toaster')

rel = out[out['kw'].str.contains(CORE_PAT, regex=True, na=False)].copy()
print(f"on-topic (contains hair-dryer language): {len(rel):,} kws, {int(rel['Volume'].sum()):,} vol")
rel = rel[~rel['kw'].str.contains(OFF_PAT, regex=True, na=False)].copy()
print(f"minus off-category products:              {len(rel):,} kws, {int(rel['Volume'].sum()):,} vol")

rel.to_pickle('analysis/ontopic.pkl')

print("\n" + "=" * 110)
print("S. ON-TOPIC MARKET STRUCTURE -- TAM by segment (CA, monthly searches)")
print("=" * 110)
tot = rel['Volume'].sum()
def show(name, mask):
    s = rel[mask]
    nz = s[s['KD'].notna()]
    print(f"{name:<38} kws={len(s):>6,}  vol={int(s['Volume'].sum()):>9,}  "
          f"({100*s['Volume'].sum()/tot:>5.1f}%)  medKD={nz['KD'].median() if len(nz) else float('nan')}  "
          f"avgCPC=${s['CPC'].mean():.2f}")
show('ALL on-topic', rel['Volume'] > 0)
show('-- LAIFEN branded', rel['kw'].str.contains('laifen', na=False))
show('-- Dyson branded', rel['kw'].str.contains('dyson', na=False))
show('-- Shark branded', rel['kw'].str.contains('shark', na=False))
show('-- GHD / T3 / other brands', rel['kw'].str.contains(r'\bghd\b|\bt3\b|babyliss|revlon|conair|drybar|zuvi', na=False))
show('-- NON-BRANDED (the open field)', ~rel['kw'].str.contains(
    r'laifen|dyson|shark|\bghd\b|\bt3\b|babyliss|revlon|conair|drybar|zuvi', na=False))
print()
show('dupe / alternative / like-Dyson', rel['kw'].str.contains(r'dupe|alternative|similar to|like dyson|knock ?off', na=False))
show('vs / comparison', rel['kw'].str.contains(r'\bvs\b|\bversus\b|compare|comparison', na=False))
show('best / roundup', rel['kw'].str.contains(r'\bbest\b|\btop \d', na=False))
show('review / worth it', rel['kw'].str.contains(r'review|worth it|is it worth', na=False))
show('buy / price / where / deal', rel['kw'].str.contains(r'\bbuy\b|price|cost|where to|for sale|\bdeal|discount|coupon|sale\b', na=False))
show('canada-qualified', rel['kw'].str.contains(r'canada|canadian|\bca\b', na=False))
show('french (quebec)', rel['kw'].str.contains(r'sechoir|seche cheveux|avis|meilleur|cheveux', na=False))

print("\n" + "=" * 110)
print("T. THE MONEY LIST -- on-topic, non-branded, vol>=100, rankable (KD_eff<=40)")
print("=" * 110)
mon = rel[(~rel['kw'].str.contains(r'laifen|dyson|shark|\bghd\b|\bt3\b|babyliss|revlon|conair|drybar', na=False))
          & (rel['Volume'] >= 100) & (rel['KD_eff'] <= 40)].copy()
mon = mon.sort_values(['Opportunity', 'Volume'], ascending=False)
print(f"count {len(mon):,}  total volume {int(mon['Volume'].sum()):,}")
print(mon[['Keyword', 'Volume', 'KD', 'KD_eff', 'CPC', 'Intent', 'Opportunity']].head(80).to_string(index=False))

print("\n" + "=" * 110)
print("U. THE DUPE / ALTERNATIVE PLAY -- full keyword set (the affiliate wedge)")
print("=" * 110)
dupe = rel[rel['kw'].str.contains(r'dupe|alternative|similar to|like dyson|knock ?off|cheaper than', na=False)]
dupe = dupe.sort_values('Volume', ascending=False)
print(f"count {len(dupe):,}  volume {int(dupe['Volume'].sum()):,}")
print(dupe[['Keyword', 'Volume', 'KD', 'KD_eff', 'CPC', 'Intent', 'Opportunity']].head(60).to_string(index=False))

print("\n" + "=" * 110)
print("V. vs-COMPARISON PLAY -- Laifen vs Dyson etc (high intent, low competition)")
print("=" * 110)
vs = rel[rel['kw'].str.contains(r'\bvs\b|\bversus\b', na=False)].sort_values('Volume', ascending=False)
print(f"count {len(vs):,}  volume {int(vs['Volume'].sum()):,}")
print(vs[['Keyword', 'Volume', 'KD', 'KD_eff', 'CPC', 'Opportunity']].head(45).to_string(index=False))

print("\n" + "=" * 110)
print("W. CONCENTRATION -- how top-heavy is the on-topic market?")
print("=" * 110)
v = rel.loc[rel['Volume'] > 0, 'Volume'].sort_values(ascending=False)
for n in [10, 25, 50, 100, 250, 500, 1000]:
    print(f"  top {n:>5} keywords = {100*v.head(n).sum()/v.sum():>5.1f}% of on-topic demand "
          f"({int(v.head(n).sum()):,} of {int(v.sum()):,})")
print(f"\n  keywords needed to reach 80% of demand: "
      f"{int((v.cumsum()/v.sum() <= 0.8).sum())}")
print(f"  median volume of on-topic kw: {v.median()}")
print(f"  keywords with vol>=1000: {(v>=1000).sum()}   vol>=500: {(v>=500).sum()}   vol>=100: {(v>=100).sum()}")
