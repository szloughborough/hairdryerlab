"""独立核验 how-we-test.mdx：章节覆盖 §63 的 13 项 + 是否编造实测值。"""
import io
import re

P = 'deliverables/drafts/how-we-test.mdx'
t = io.open(P, encoding='utf-8').read()
out = []
def W(*a): out.append(' '.join(str(x) for x in a))

W(f'行数 {len(t.splitlines())}   字符 {len(t):,}')
W('')

W('=== H2 清单 ===')
h2 = re.findall(r'(?m)^## (.+)$', t)
for i, h in enumerate(h2, 1):
    W(f'  {i:>2}. {h}')
W('')

W('=== §63 的 13 个主题覆盖检查 ===')
THEMES = {
    '1 Why we test': r'why we test',
    '2 Products we test': r'products we test',
    '3 How sourced': r'how we source|sourced',
    '4 Test environment': r'test environment',
    '5 Drying-speed test': r'drying.speed test|dry time',
    '6 Noise test': r'noise test',
    '7 Weight test': r'weight test',
    '8 Heat test': r'heat test',
    '9 Real-world use': r'real.world use',
    '10 Hair-type feedback': r'hair.type feedback',
    '11 Price/value methodology': r'price and value|value methodology',
    '12 Affiliate independence': r'affiliate independence',
    '13 Update policy': r'update policy',
}
missing = []
for label, pat in THEMES.items():
    n = len(re.findall(pat, t, re.I))
    W(f'  {"✓" if n else "✗"} {label:<30} 命中 {n}')
    if not n:
        missing.append(label)
W('')

W('=== 是否编造实测值 ===')
W(f'  *(Measured)* 标注出现: {len(re.findall(r"\\(\\s*Measured\\s*\\)", t))} 处（应为 0）')
W(f'  final 中 "Not yet tested" / "not measured": '
  f'{len(re.findall(r"not yet test|not measured|not weighed|have not measure", t, re.I))} 处')
W(f'  出现疑似具体实测数值（如 XX.X dB / XXX g / XX:XX）:')
suspect = re.findall(r'\b\d+(?:\.\d+)?\s*(?:dB|g\b|°C)\b', t)
W(f'     {suspect if suspect else "无"}')
W('')

W('=== 合规硬项 ===')
W(f'  数字总分 / WINNER / #1: '
  f'{len(re.findall(r"\\b\\d+(\\.\\d+)?/10\\b|\\bWINNER\\b|#1\\b|Best Overall", t))} 处（应为 0）')
W(f'  精确价格 C$XX.XX: {len(re.findall(r"C\\$\\d+\\.\\d{2}", t))} 处（应为 0）')
W(f'  约数价格 about C$X: {len(re.findall(r"about C\\$\\d+", t))} 处')
W(f'  单位 min:sec / dB @ 1 m / g / °C / m / W 出现: '
  f'{len(re.findall(r"min:sec|dB @ 1 m|\\b°C\\b|\\bg\\b|\\bW\\b", t))} 处')
W(f'  无虚构资质检查: {"PASS" if not re.search(r"licensed (stylist|hairstylist)|certified trichologist|\\d+ years of experience", t) else "FAIL"}')

if missing:
    W('')
    W(f'⚠ 未覆盖的主题: {missing}')
else:
    W('')
    W('✓ §63 的 13 个主题全部覆盖')

io.open('analysis/_howwetest_verify.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written analysis/_howwetest_verify.txt')
