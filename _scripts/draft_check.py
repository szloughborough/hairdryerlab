import re, io
p = 'deliverables/drafts/best-dyson-alternatives.mdx'
c = io.open(p, encoding='utf-8').read()
body = re.sub(r'(?s)^---.*?---', '', c)
words = len([w for w in re.split(r'\s+', body) if re.search(r'\w', w)])
lines = []
lines.append(f"body words (approx): {words}")
lines.append(f"total chars: {len(c)}")
lines.append(f"H1: {len(re.findall(r'(?m)^# ', c))}  H2: {len(re.findall(r'(?m)^## ', c))}  H3: {len(re.findall(r'(?m)^### ', c))}")
lines.append(f"tables: {len(re.findall(r'(?m)^\|', c))} table rows")
lines.append(f"待实测/待核实 placeholders: {len(re.findall(r'【待', c))}")
lines.append(f"affiliate placeholders: {len(re.findall(r'\{\{affiliate', c))}")
lines.append(f"internal links: {len(re.findall(r'\]\(/', c))}")
lines.append("")
lines.append("--- H2 outline ---")
for m in re.findall(r'(?m)^## (.+)$', c):
    lines.append("  " + m)
io.open('analysis/_draft_check.txt', 'w', encoding='utf-8').write('\n'.join(lines))
print("ok")
