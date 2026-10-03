import pandas as pd
pd.set_option('display.width', 300)
pd.set_option('display.max_columns', 50)
pd.set_option('display.max_colwidth', 70)

for t in ['semrush数据/hair-dryer-like-dyson_serp_urls_ca_2026-10-02_11-05-00.xlsx',
          'semrush数据/dyson-dupe-hair-dryer_serp_urls_ca_2026-10-02_11-05-22.xlsx']:
    print("#" * 100)
    print(t)
    df = pd.read_excel(t)
    print("shape:", df.shape)
    print(df.to_string())
    print()
