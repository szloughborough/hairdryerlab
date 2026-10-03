"""核实 how-we-test.mdx 的两处疑点：疑似实测数值的上下文；价格表述。"""
import io
import re

t = io.open('deliverables/drafts/how-we-test.mdx', encoding='utf-8').read()
out = []
def W(*a): out.append(' '.join(str(x) for x in a))

W('=' * 94)
W('疑点一：疑似实测数值的上下文（判断是「方法规格」还是「编造结果」）')
W('=' * 94)
for pat in [r'0\.1\s*g', r'2\s*dB', r'400\s*g', r'550\s*g']:
    for m in re.finditer(pat, t):
        s = max(0, m.start() - 150)
        e = min(len(t), m.end() + 120)
        W(f'[{m.group(0)}]')
        W(f'   …{t[s:e].replace(chr(10), " ").strip()}…')
        W('')

W('=' * 94)
W('疑点二：价格表述（subagent 声称用了 about C$X，但扫描为 0）')
W('=' * 94)
any_price = re.findall(r'about C\$[\d,]+|C\$[\d,]+|\$\d+(?:\.\d+)?\b', t)
W(f'  任何 $ 形式的价格出现: {len(any_price)} 处 -> {any_price[:20]}')
W('')
W('  含 price / cost / $ 的行:')
n = 0
for i, line in enumerate(t.splitlines(), 1):
    if re.search(r'price|cost|\$', line, re.I):
        W(f'   L{i}: {line.strip()[:150]}')
        n += 1
        if n > 25:
            break
if n == 0:
    W('   （无）')

io.open('analysis/_howwetest_doubts.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written analysis/_howwetest_doubts.txt')
