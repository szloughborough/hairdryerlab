import pandas as pd, openpyxl, os
pd.set_option('display.width', 340)
pd.set_option('display.max_columns', 60)
pd.set_option('display.max_colwidth', 60)

F = r"C:\Users\Mloong\Downloads\BSR(Hair-Dryers(Current))-50-CA-20261002.xlsx"
wb = openpyxl.load_workbook(F, read_only=True)
print("sheets:", wb.sheetnames)
for sn in wb.sheetnames:
    ws = wb[sn]
    print(f"  {sn}: rows={ws.max_row} cols={ws.max_column}")
    for i, row in enumerate(ws.iter_rows(min_row=1, max_row=6, values_only=True)):
        print("   ", i+1, [str(v)[:28] if v is not None else None for v in row])
    print()
wb.close()
