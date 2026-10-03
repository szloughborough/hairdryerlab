"""
Opportunity scoring + realistic traffic/revenue model.

Scoring logic (affiliate-site oriented, Canadian market):
  OpportunityScore = f(Volume, KD, Relevance, Intent commercial-ness, SERP defensibility)
  - KD penalty: harder to rank
  - SERP penalty: AI Overview / Popular products steal clicks
  - commercial bonus: buyer intent converts to affiliate clicks
"""
import pandas as pd, numpy as np, re

pd.set_option('display.width', 340)
pd.set_option('display.max_columns', 60)
pd.set_option('display.max_colwidth', 70)

m = pd.read_pickle('analysis/master.pkl')
m['kw'] = m['Keyword'].astype(str).str.lower().str.strip()
core = m[(m['Volume'] > 0) & (m['Relevance'] >= 70)].copy()   # research pool
print(f"research pool (rel>=70, vol>0): {len(core):,} kws, {int(core['Volume'].sum()):,} vol")

# ---- intent scoring
def intent_score(s):
    if not isinstance(s, str):
        return 0.5
    s = s.lower()
    if 'transactional' in s:
        return 1.0
    if 'commercial' in s:
        return 0.9
    if 'informational' in s:
        return 0.45
    if 'navigational' in s:
        return 0.3
    return 0.5

core['intent_score'] = core['Intent'].apply(intent_score)

# ---- SERP defensibility: what share of clicks survive?
#    AI Overview = -35%, Popular products = -30%, Short videos = -10%, Reviews = +8% (affiliate-friendly)
core['SERP'] = core['SERP'].fillna('')
core['serp_risk'] = (
    core['SERP'].str.contains('AI Overview', na=False).astype(int) * 0.35
    + core['SERP'].str.contains('Popular products', na=False).astype(int) * 0.30
    + core['SERP'].str.contains('Short videos', na=False).astype(int) * 0.10
    + core['SERP'].str.contains('Image pack', na=False).astype(int) * 0.08
)
core['serp_boost'] = core['SERP'].str.contains('Reviews', na=False).astype(int) * 0.08
core['click_retention'] = (1 - core['serp_risk'] + core['serp_boost']).clip(0.15, 1.0)

# ---- KD handling: only 4% have KD. Impute with a model-free heuristic:
#      branded long-tails are easier; short head terms are harder.
core['nwords'] = core['kw'].str.split().str.len()
core['is_branded'] = core['kw'].str.contains(
    'laifen|dyson|shark|ghd|babyliss|revlon|conair|drybar', na=False)

kd_med_by_words = core[core['KD'].notna()].groupby('nwords')['KD'].median()
def impute_kd(r):
    if pd.notna(r['KD']):
        return r['KD']
    base = kd_med_by_words.get(r['nwords'], 30)
    return float(base) + (5 if r['Volume'] >= 500 else 0)

core['KD_eff'] = core.apply(impute_kd, axis=1)
core['KD_is_real'] = core['KD'].notna()

# ---- difficulty penalty (0..1, higher = easier)
core['ease'] = ((100 - core['KD_eff']) / 100).clip(0.05, 1.0) ** 1.5

# ---- final opportunity score
core['Opportunity'] = (
    np.log1p(core['Volume']) * 0.35
    + core['Relevance'] / 100 * 0.20
    + core['intent_score'] * 0.20
    + core['ease'] * 0.15
    + core['click_retention'] * 0.10
)
core['Opportunity'] = (core['Opportunity'] / core['Opportunity'].max() * 100).round(1)

# ---- expected clicks if we rank (CTR by position, CA, blended with SERP leakage)
CTR = {1: 0.26, 2: 0.15, 3: 0.10, 4: 0.07, 5: 0.05, 6: 0.04, 7: 0.03, 8: 0.025, 9: 0.02, 10: 0.018}
def exp_clicks(vol, pos, retain):
    return vol * CTR.get(pos, 0.01) * retain

out = core.sort_values('Opportunity', ascending=False)
out.to_pickle('analysis/scored.pkl')

print("\n" + "=" * 110)
print("O. TOP 60 OPPORTUNITY KEYWORDS (affiliate-optimised score)")
print("=" * 110)
cols = ['Keyword', 'Volume', 'KD', 'KD_eff', 'CPC', 'Intent', 'Relevance',
        'click_retention', 'Opportunity', 'best_seed']
print(out.head(60)[cols].to_string(index=False))

# ---------------------------------------------------------------- realistic model
print("\n" + "=" * 110)
print("P. REALISTIC TRAFFIC & REVENUE MODEL (year 1-2, single affiliate site)")
print("=" * 110)

# Build a defensible target keyword portfolio: non-head, rankable, on-topic
port = out[(out['Volume'] >= 50) & (out['KD_eff'] <= 45) & (out['Relevance'] >= 70)].copy()
print(f"rankable portfolio (vol>=50, KD_eff<=45, rel>=70): {len(port):,} kws, "
      f"{int(port['Volume'].sum()):,} monthly searches")

# Assume a good affiliate site captures these shares of its portfolio by position
SCENARIOS = {
    'pessimistic': {'top3': 0.05, 'top10': 0.20, 'top30': 0.45, 'ctr_blend': 0.030},
    'base':        {'top3': 0.12, 'top10': 0.35, 'top30': 0.65, 'ctr_blend': 0.055},
    'optimistic':  {'top3': 0.22, 'top10': 0.50, 'top30': 0.80, 'ctr_blend': 0.085},
}
rows = []
for name, s in SCENARIOS.items():
    vol = port['Volume'].sum() * s['top30']            # volume in play at all
    clicks = vol * s['ctr_blend'] * port['click_retention'].mean()
    # affiliate economics
    aff_click_rate = 0.18      # organic visitor -> merchant click
    conv_rate = 0.025          # merchant click -> sale
    aov = 200.0                # Laifen Swift ~ CAD 200 avg order
    comm = 0.06                # affiliate commission rate
    sessions = clicks
    aff_clicks = sessions * aff_click_rate
    sales = aff_clicks * conv_rate
    rev = sales * aov * comm
    rows.append({'scenario': name, 'monthly_organic_sessions': round(sessions),
                 'annual_sessions': round(sessions * 12),
                 'affiliate_clicks/mo': round(aff_clicks),
                 'sales/mo': round(sales, 1), 'sales/yr': round(sales * 12),
                 'monthly_rev_CAD': round(rev), 'annual_rev_CAD': round(rev * 12)})
rm = pd.DataFrame(rows)
print(rm.to_string(index=False))

print("\n--- Sensitivity: the model is linear in these assumptions, so treat as scenario, not forecast.")
print("    Assumptions used: aff_click_rate=18%, conv=2.5%, AOV=CAD200, commission=6%")

# ---------------------------------------------------------------- Laifen warm pool
print("\n" + "=" * 110)
print("Q. THE 'WARM' POOL -- Laifen-branded + dupe/comparison demand (highest conversion)")
print("=" * 110)
warm = out[out['kw'].str.contains('laifen|dupe|alternative|similar to|like dyson|vs ', na=False)]
print(f"warm kws: {len(warm):,}, {int(warm['Volume'].sum()):,} monthly searches")
print(warm.nlargest(35, 'Volume')[['Keyword', 'Volume', 'KD', 'KD_eff', 'CPC', 'Opportunity']].to_string(index=False))

print("\n" + "=" * 110)
print("R. QUICK-WIN LIST -- vol>=100, KD_eff<=30, on-topic, non-Dyson-head")
print("=" * 110)
qw = out[(out['Volume'] >= 100) & (out['KD_eff'] <= 30) & (out['Relevance'] >= 70)]
qw = qw[~qw['kw'].str.match(r'^(dyson|shark) (air ?wrap|supersonic|flexstyle|speedstyle)$', na=False)]
print(f"count {len(qw):,}, volume {int(qw['Volume'].sum()):,}")
print(qw.nlargest(60, 'Volume')[['Keyword', 'Volume', 'KD', 'KD_eff', 'CPC', 'Intent', 'SERP']].to_string(index=False))
