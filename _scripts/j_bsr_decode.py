import openpyxl, pandas as pd, numpy as np
pd.set_option('display.width', 400); pd.set_option('display.max_columns', 80)

F = r"C:\Users\Mloong\Downloads\BSR(Hair-Dryers(Current))-50-CA-20261002.xlsx"
ws = openpyxl.load_workbook(F, read_only=True)['CA']

def demojibake(s):
    if not isinstance(s, str):
        return s
    try:
        return s.encode('latin-1').decode('gbk')
    except Exception:
        try:
            return s.encode('latin-1').decode('utf-8')
        except Exception:
            return s

rows = list(ws.iter_rows(values_only=True))
hdr = [demojibake(h) for h in rows[0]]
print("=== HEADERS (decoded, with 1-based index) ===")
for i, h in enumerate(hdr, 1):
    print(f"  {i:>2} | {h}")
print(f"\ntotal columns: {len(hdr)}")
print(f"data rows: {len(rows)-1}")

df = pd.DataFrame(rows[1:], columns=hdr)
df.to_pickle('analysis/bsr_raw.pkl')

print("\n=== ROW 1 (Laifen check) ===")
r = df.iloc[0]
for i, h in enumerate(hdr):
    print(f"  {h:<28} = {str(r.iloc[i])[:60]}")
