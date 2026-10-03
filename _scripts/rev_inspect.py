import pandas as pd, openpyxl, glob, os
pd.set_option('display.width', 340); pd.set_option('display.max_columns', 60)
pd.set_option('display.max_colwidth', 70)

f = 'asin数据/B0C3M9WBQF-CA-Reviews-20261002.xlsx'   # slopehill #1
wb = openpyxl.load_workbook(f, read_only=True)
print("sheets:", wb.sheetnames)
ws = wb[wb.sheetnames[0]]
print(f"rows={ws.max_row} cols={ws.max_column}")
print("\n--- first 6 rows ---")
for i, row in enumerate(ws.iter_rows(min_row=1, max_row=6, values_only=True)):
    print(i+1, [str(v)[:60] if v is not None else None for v in row])
wb.close()

print("\n--- pandas view ---")
df = pd.read_excel(f)
print("shape:", df.shape)
print("columns:", list(df.columns))
print(df.head(3).to_string())
print("\ndtypes:\n", df.dtypes)
