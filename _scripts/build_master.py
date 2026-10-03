"""
Build a deduplicated master keyword dataset from the 34 Semrush CA broad-match exports.

Each export is a Semrush "Broad Match" keyword list seeded on one phrase.
- Relevance: similarity of the keyword to that seed (0-100)
- Volume: CA monthly search volume
- The lists overlap heavily, so we keep per (keyword) the BEST evidence:
  max volume, max relevance, and the seed that gave max relevance.

Duplicate files (byte-identical) are detected via md5 and skipped.
"""
import glob, os, hashlib, re
import pandas as pd

SRC = 'semrush数据'
OUT = 'analysis'

os.makedirs(OUT, exist_ok=True)


def md5(path):
    h = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


files = sorted(glob.glob(os.path.join(SRC, '*_all-keywords_ca_*.xlsx')))
seen, uniq_files = {}, []
for f in files:
    d = md5(f)
    if d in seen:
        print(f"SKIP duplicate: {os.path.basename(f)}  == {os.path.basename(seen[d])}")
        continue
    seen[d] = f
    uniq_files.append(f)

print(f"\nunique keyword files: {len(uniq_files)} (from {len(files)})\n")

COLS = ['Keyword', 'Intent', 'Relevance', 'Volume', 'Trend',
        'Keyword Difficulty', 'CPC (USD)', 'Competitive Density',
        'SERP Features', 'Number of Results']

frames = []
for f in uniq_files:
    base = os.path.basename(f)
    seed = re.sub(r'_all-keywords_ca_.*$', '', base)
    df = pd.read_excel(f, usecols=COLS)
    df['seed'] = seed
    # only keep rows with any volume to cut noise; keep 0-volume for later gap analysis? -> keep >=1
    frames.append(df)
    print(f"  {seed:<42} rows={len(df):>7}")

allk = pd.concat(frames, ignore_index=True)
print(f"\ncombined rows: {len(allk):,}")

# --- one row per keyword, keeping the strongest/most-relevant seed evidence
allk = allk.sort_values(['Keyword', 'Relevance', 'Volume'], ascending=[True, False, False])
grp = allk.groupby('Keyword', as_index=False)

master = grp.agg(
    Volume=('Volume', 'max'),
    Relevance=('Relevance', 'max'),
    CPC=('CPC (USD)', 'max'),
    KD=('Keyword Difficulty', 'max'),
    CompDensity=('Competitive Density', 'max'),
    NumResults=('Number of Results', 'max'),
    Intent=('Intent', lambda s: next((v for v in s if isinstance(v, str) and v.strip()), None)),
    Trend=('Trend', 'first'),
    SERP=('SERP Features', lambda s: next((v for v in s if isinstance(v, str) and v.strip()), None)),
    best_seed=('seed', 'first'),
    n_seeds=('seed', 'nunique'),
    # which seeds this keyword appeared under, in relevance order -> seed list
    seed_list=('seed', lambda s: list(dict.fromkeys(s))),
)

print(f"master unique keywords: {len(master):,}")
print(f"  with volume > 0: {(master['Volume'] > 0).sum():,}")
master.to_pickle(os.path.join(OUT, 'master.pkl'))
print("\nsaved", os.path.join(OUT, 'master.pkl'))

print("\n--- Volume distribution (unique kw, vol>0)")
v = master.loc[master['Volume'] > 0, 'Volume']
print(v.describe(percentiles=[.5, .75, .9, .95, .99]).to_string())
print("\nvolume buckets:")
bins = [0, 10, 50, 100, 500, 1000, 5000, 100000]
print(pd.cut(v, bins).value_counts().sort_index().to_string())
