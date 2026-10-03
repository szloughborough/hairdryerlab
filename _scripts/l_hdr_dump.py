import zipfile, re, json, io

F = r"C:\Users\Mloong\Downloads\BSR(Hair-Dryers(Current))-50-CA-20261002.xlsx"
z = zipfile.ZipFile(F)
raw = z.read('xl/sharedStrings.xml').decode('utf-8')
strs = re.findall(r'<si>(.*?)</si>', raw, re.S)
vals = []
for s in strs:
    parts = re.findall(r'<t[^>]*>(.*?)</t>', s, re.S)
    vals.append(''.join(parts).replace('&amp;', '&').replace('&apos;', "'"))

out = []
out.append("=== 表头 (71列) ===")
for i, v in enumerate(vals[:71], 1):
    out.append(f"{i:>2} | {v}")

with io.open('analysis/_hdr.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print("written analysis/_hdr.txt")
