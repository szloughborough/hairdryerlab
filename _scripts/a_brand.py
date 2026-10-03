import pandas as pd, numpy as np, re, os

pd.set_option('display.width', 320)
pd.set_option('display.max_columns', 60)
pd.set_option('display.max_colwidth', 55)

m = pd.read_pickle('analysis/master.pkl')
m['kw'] = m['Keyword'].astype(str).str.lower().str.strip()

BRANDS = {
    'laifen': r'\blaifen\b|laifen',
    'dyson': r'\bdyson\b',
    'shark': r'\bshark\b',
    'ghd': r'\bghd\b',
    't3': r'\bt3\b',
    'babyliss': r'babyliss|babylisspro',
    'revlon': r'\brevlon\b',
    'conair': r'\bconair\b',
    'drybar': r'drybar|dry bar',
    'zuvi': r'\bzuvi\b',
    'lange': r'\blange\b',
    'dyson_dupe': r'dupe|alternative|like dyson|similar to dyson',
}

print("=" * 110)
print("A. BRAND DEMAND IN CANADA  (unique keywords, volume>0)")
print("=" * 110)
rows = []
for name, pat in BRANDS.items():
    sub = m[m['kw'].str.contains(pat, regex=True, na=False) & (m['Volume'] > 0)]
    rows.append({
        'brand/theme': name,
        'keywords': len(sub),
        'total_volume': int(sub['Volume'].sum()),
        'avg_vol': round(sub['Volume'].mean(), 1) if len(sub) else 0,
        'max_vol': int(sub['Volume'].max()) if len(sub) else 0,
        'med_KD': sub['KD'].median(),
        'avg_CPC': round(sub['CPC'].mean(), 2) if len(sub) else 0,
    })
bdf = pd.DataFrame(rows).sort_values('total_volume', ascending=False)
print(bdf.to_string(index=False))

print("\n" + "=" * 110)
print("B. TOP 40 LAIFEN KEYWORDS BY VOLUME (CA)")
print("=" * 110)
la = m[m['kw'].str.contains('laifen', na=False) & (m['Volume'] > 0)].copy()
print(f"total laifen keywords w/ volume: {len(la)},  total volume: {int(la['Volume'].sum()):,}")
cols = ['Keyword', 'Volume', 'KD', 'CPC', 'Intent', 'Relevance', 'best_seed']
print(la.nlargest(40, 'Volume')[cols].to_string(index=False))

print("\n" + "=" * 110)
print("C. LAIFEN vs DYSON vs SHARK -- head-to-head core terms")
print("=" * 110)
cores = ['laifen hair dryer', 'laifen', 'laifen canada', 'laifen hair dryer review',
         'laifen swift', 'laifen se', 'laifen swift special', 'laifen hair dryer canada',
         'dyson hair dryer', 'dyson supersonic', 'shark hair dryer', 'shark speedstyle',
         'shark flexstyle', 'ghd helios', 't3 hair dryer', 'hair dryer', 'blow dryer',
         'best hair dryer', 'laifen alternative', 'dyson dupe hair dryer']
cd = m[m['kw'].isin(cores)][['Keyword', 'Volume', 'KD', 'CPC', 'Intent', 'CompDensity', 'SERP', 'n_seeds']]
print(cd.sort_values('Volume', ascending=False).to_string(index=False))

print("\n" + "=" * 110)
print("D. LAIFEN SHARE OF HAIR-DRYER CATEGORY DEMAND")
print("=" * 110)
# core category demand = keywords that plausibly belong to the hair dryer category
cat = m[(m['Volume'] > 0) & (m['Relevance'] >= 40)].copy()
print(f"keywords with Relevance>=40 and vol>0: {len(cat):,}, volume={int(cat['Volume'].sum()):,}")
la_cat = cat[cat['kw'].str.contains('laifen', na=False)]
print(f"  of which laifen-branded: {len(la_cat):,}, volume={int(la_cat['Volume'].sum()):,} "
      f"({100*la_cat['Volume'].sum()/cat['Volume'].sum():.2f}% of category demand)")
dy_cat = cat[cat['kw'].str.contains('dyson', na=False)]
print(f"  of which dyson-branded : {len(dy_cat):,}, volume={int(dy_cat['Volume'].sum()):,} "
      f"({100*dy_cat['Volume'].sum()/cat['Volume'].sum():.2f}% of category demand)")

print("\n" + "=" * 110)
print("E. TOP 60 NON-BRANDED CATEGORY KEYWORDS (the real traffic pool)")
print("=" * 110)
nonbrand = cat[~cat['kw'].str.contains('laifen|dyson|shark|ghd|t3 |babyliss|revlon|conair|drybar|zuvi', regex=True, na=False)]
print(f"non-branded kws: {len(nonbrand):,}, volume={int(nonbrand['Volume'].sum()):,}")
print(nonbrand.nlargest(60, 'Volume')[['Keyword', 'Volume', 'KD', 'CPC', 'Intent', 'Relevance', 'best_seed']].to_string(index=False))
