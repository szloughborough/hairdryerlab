import glob, os
import pandas as pd

pd.set_option('display.width', 300)
pd.set_option('display.max_columns', 50)
pd.set_option('display.max_colwidth', 60)

# --- sample keyword files
targets = [
    'semrush数据/laifen_all-keywords_ca_2026-10-02.xlsx',
    'semrush数据/laifen-hair-dryer_all-keywords_ca_2026-10-02.xlsx',
    'semrush数据/hair-dryer_all-keywords_ca_2026-10-02.xlsx',
    'semrush数据/dyson-hair-dryer_all-keywords_ca_2026-10-02.xlsx',
]
for t in targets:
    print("#" * 100)
    print(t)
    df = pd.read_excel(t)
    print("shape:", df.shape)
    print("dtypes:\n", df.dtypes)
    print("\nHEAD 15:")
    print(df.head(15).to_string())
    print("\nVolume describe:", df['Volume'].describe().to_dict())
    print("non-null Volume:", df['Volume'].notna().sum())
    print("Volume>0:", (df['Volume'] > 0).sum())
    print("\nIntent values:", df['Intent'].value_counts(dropna=False).to_dict())
    print("Trend sample:", df['Trend'].dropna().unique()[:10])
    print("SERP Features sample:", df['SERP Features'].dropna().unique()[:5])
    print()
