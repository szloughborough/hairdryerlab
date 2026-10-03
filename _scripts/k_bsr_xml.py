import zipfile, re

F = r"C:\Users\Mloong\Downloads\BSR(Hair-Dryers(Current))-50-CA-20261002.xlsx"
z = zipfile.ZipFile(F)
print("entries:", [n for n in z.namelist() if 'sheet' in n or 'shared' in n][:20])

# sharedStrings holds the header text
try:
    raw = z.read('xl/sharedStrings.xml')
    print("sharedStrings bytes:", len(raw))
    print("first 200 raw:", raw[:200])
except KeyError:
    print("no sharedStrings")
    raw = None

if raw:
    for enc in ['utf-8', 'gbk', 'gb18030']:
        try:
            t = raw.decode(enc)
            if 'ASIN' in t:
                print(f"\n*** decoded OK with {enc}")
                strs = re.findall(r'<si>(.*?)</si>', t, re.S)
                vals = []
                for s in strs:
                    parts = re.findall(r'<t[^>]*>(.*?)</t>', s, re.S)
                    vals.append(''.join(parts))
                print(f"total shared strings: {len(vals)}")
                print("\nfirst 75 shared strings:")
                for i, v in enumerate(vals[:75]):
                    print(f"  {i:>3} | {v}")
                break
        except Exception as e:
            print(enc, "failed:", e)
