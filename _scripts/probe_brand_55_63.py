"""查品牌文档里 §63（How We Test 页）与 §55（组件）的原文要求。"""
import io
import re

t = io.open('deliverables/品牌规范-HairDryerLab-v1.0.md', encoding='utf-8').read()
out = []
def P(*a): out.append(' '.join(str(x) for x in a))

P(f'品牌文档总长: {len(t):,} 字符')
P('')

# 找所有章节标题
heads = re.findall(r'(?m)^#{1,4}\s*(?:§)?(\d{1,3})[.、\s]+(.{0,60})$', t)
P(f'=== 章节标题（共 {len(heads)} 个），含 55 / 63 的：')
for num, title in heads:
    if num in ('55', '63', '38', '39', '62', '64', '67', '71', '79'):
        P(f'   §{num}  {title.strip()}')
P('')

for target in ('55', '63'):
    # 定位该节并截取
    m = re.search(r'(?m)^#{1,4}\s*§?' + target + r'[.、\s]', t)
    if not m:
        P(f'§{target}: 未定位到')
        continue
    start = m.start()
    nxt = re.search(r'(?m)^#{1,4}\s*§?\d{1,3}[.、\s]', t[m.end():])
    end = m.end() + nxt.start() if nxt else min(len(t), start + 3000)
    P('=' * 96)
    P(f'§{target} 原文（{end-start} 字符）')
    P('=' * 96)
    P(t[start:end].strip()[:2600])
    P('')

io.open('analysis/_brand_55_63.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written analysis/_brand_55_63.txt')
