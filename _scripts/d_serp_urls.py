import pandas as pd, numpy as np, re, os, glob

pd.set_option('display.width', 330)
pd.set_option('display.max_columns', 60)
pd.set_option('display.max_colwidth', 75)

print("=" * 110)
print("N. SERP REALITY CHECK -- who actually ranks for the money terms?")
print("=" * 110)
for f in sorted(glob.glob('semrush数据/*_serp_urls_*.xlsx')):
    df = pd.read_excel(f)
    name = os.path.basename(f).split('_serp_urls')[0]
    print(f"\n### {name}   (rows={len(df)})")
    org = df[df['Type'] == 'Organic'].copy()
    print(f"organic results: {len(org)}")
    # domain frequency
    print("\n-- domains appearing most in organic top50:")
    print(org['Domain'].value_counts().head(15).to_string())
    print("\n-- best-ranking position per domain:")
    best = org.groupby('Domain')['Position'].min().sort_values().head(20)
    print(best.to_string())
    print("\n-- Page Authority of ranking pages (organic):")
    print(org['Page AS'].describe(percentiles=[.25, .5, .75, .9]).round(1).to_string())
    print("\n-- how many ranking pages are LOW authority (Page AS <= 5)? -> winnable signal")
    low = org[org['Page AS'] <= 5]
    print(f"   {len(low)} / {len(org)} pages  ({100*len(low)/len(org):.0f}%)")
    print("\n-- Page AS <= 10 pages that rank top 30 (realistic competitor set):")
    easy = org[(org['Page AS'] <= 10) & (org['Position'] <= 30)][['Position', 'Domain', 'Page AS', 'Ref.Domains']]
    print(easy.to_string(index=False))
    print("\n-- result types present:")
    print(df['Type'].value_counts().to_string())
    print("\n" + "#" * 110)
