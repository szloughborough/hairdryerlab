import pandas as pd, numpy as np, re

pd.set_option('display.width', 320)
pd.set_option('display.max_columns', 60)
pd.set_option('display.max_colwidth', 60)

m = pd.read_pickle('analysis/master.pkl')
m['kw'] = m['Keyword'].astype(str).str.lower().str.strip()
cat = m[(m['Volume'] > 0) & (m['Relevance'] >= 40)].copy()

print("=" * 110)
print("F. TOPIC CLUSTER DEFINITIONS -- CA demand pool by theme")
print("=" * 110)
CLUSTERS = {
    'best / roundup':        r'\bbest\b|\btop \d|top rated|top-',
    'review / rating':       r'\breview|reviews|rated|rating|worth it|is it worth',
    'cheap / budget / dupe': r'\bcheap|budget|affordable|dupe|alternative|knock ?off|under \$|cheaper',
    'comparison vs':         r'\bvs\b|\bversus\b|compare|comparison|difference between',
    'curly / wavy hair':     r'\bcurly|curls|wavy|wave|coily|kinky|permed',
    'fine / thin hair':      r'\bfine hair|thin hair|thinning',
    'thick / coarse hair':   r'\bthick hair|coarse hair|heavy hair|dense hair',
    'frizzy / damaged':      r'\bfrizz|frizzy|damaged|dry hair|split end',
    'diffuser':              r'\bdiffus',
    'ionic / technology':    r'\bionic|negative ion|ceramic|tourmaline|infrared|nanotechnology',
    'lightweight / weight':  r'\blight ?weight|light-?weight|weigh|how much does|grams|\blbs?\b|\bkg\b',
    'quiet / noise':         r'\bquiet|silent|noise|db\b|decibel|loud',
    'fast / speed / power':  r'\bfast|fastest|speed|quick|powerful|high.?speed|watt|rpm|strong',
    'travel / portable':     r'\btravel|portable|compact|foldable|fold ?up|mini',
    'professional / salon':  r'\bprofessional|salon|pro\b|stylist|barber',
    'brush / styler / combo': r'\bbrush|styler|straightener|curler|airwrap|multi.?styler|round brush|blow ?out brush',
    'heat damage / safety':  r'\bheat damage|damage|safe|safety|temperature|heat setting|burnt|burn',
    'cold / cool shot':      r'\bcold shot|cool shot|cool air',
    'attachments / nozzle':  r'\battachment|nozzle|concentrator|magnetic',
    'voltage / plug':        r'\bvoltage|\bvolt|\bplug|adapter|220|110|dual voltage',
    'buy / where / price':   r'\bbuy|price|cost|where to|for sale|sale|deal|discount|coupon|amazon|walmart|costco|sephora|shoppers',
    'how to / tutorial':     r'\bhow to|tutorial|guide|tips|step by step',
    'hair type general':     r'\bhair type|hair texture',
    'pregnancy / safety':    r'\bpregnan',
    'men':                   r'\bmen\b|\bmens\b|\bmale\b',
    'kids / pet':            r'\bkids|children|baby|\bpet\b|\bdog\b',
}
rows = []
for name, pat in CLUSTERS.items():
    sub = cat[cat['kw'].str.contains(pat, regex=True, na=False)]
    nz = sub[sub['KD'].notna()]
    rows.append({
        'cluster': name,
        'kws': len(sub),
        'volume': int(sub['Volume'].sum()),
        'avg_vol': round(sub['Volume'].mean(), 1) if len(sub) else 0,
        'max_vol': int(sub['Volume'].max()) if len(sub) else 0,
        'med_KD': round(nz['KD'].median(), 1) if len(nz) else np.nan,
        'pct_KD_known': round(100 * len(nz) / len(sub), 1) if len(sub) else 0,
        'avg_CPC': round(sub['CPC'].mean(), 2) if len(sub) else 0,
    })
c = pd.DataFrame(rows).sort_values('volume', ascending=False)
c['cum_%'] = (100 * c['volume'].cumsum() / c['volume'].sum()).round(1)
print(c.to_string(index=False))

print("\n" + "=" * 110)
print("G. VOLUME-WEIGHTED KD -- how hard is the money?")
print("=" * 110)
nz = cat[cat['KD'].notna()]
print(f"keywords with KD data: {len(nz):,} / {len(cat):,}  ({100*len(nz)/len(cat):.1f}%)")
print("KD describe (all):")
print(nz['KD'].describe(percentiles=[.1, .25, .5, .75, .9]).to_string())
print("\nKD buckets by keyword count & volume:")
bins = [-1, 10, 20, 30, 40, 50, 60, 100]
lab = ['0-10 (easy)', '11-20', '21-30', '31-40', '41-50', '51-60', '61+ (hard)']
nz = nz.assign(kdb=pd.cut(nz['KD'], bins, labels=lab))
g = nz.groupby('kdb', observed=True).agg(kws=('KD', 'size'), volume=('Volume', 'sum'),
                                          avg_vol=('Volume', 'mean'), avg_cpc=('CPC', 'mean')).round(2)
g['vol_%'] = (100 * g['volume'] / g['volume'].sum()).round(1)
print(g.to_string())

print("\n" + "=" * 110)
print("H. HIGH-VALUE SWEET SPOT: vol>=100, KD<=35, non-branded  (rankable money terms)")
print("=" * 110)
nb = cat[~cat['kw'].str.contains('laifen', na=False)]
sweet = nb[(nb['Volume'] >= 100) & (nb['KD'].notna()) & (nb['KD'] <= 35)].copy()
sweet = sweet.sort_values('Volume', ascending=False)
print(f"count: {len(sweet)}, total volume: {int(sweet['Volume'].sum()):,}")
print(sweet.head(70)[['Keyword', 'Volume', 'KD', 'CPC', 'Intent', 'CompDensity']].to_string(index=False))
sweet.to_pickle('analysis/sweet.pkl')
