"""修正 EvidenceLabel 检查口径，并抽查 ProsCons 渲染是否保住了 markdown。"""
import glob
import io
import re

D = 'site/dist'
STYLE = re.compile(r'(?s)<style[^>]*>.*?</style>')
out = []
def W(*a): out.append(' '.join(str(x) for x in a))

pages = glob.glob(f'{D}/**/*.html', recursive=True)

W('=' * 90)
W('EvidenceLabel 真实渲染（class="ev …"）')
W('=' * 90)
total = 0
bykind = {}
for p in pages:
    h = STYLE.sub(' ', io.open(p, encoding='utf-8').read())
    for m in re.findall(r'class="ev (ev-[a-z]+)"', h):
        total += 1
        bykind[m] = bykind.get(m, 0) + 1
W(f'  合计 {total} 处')
for k, v in sorted(bykind.items(), key=lambda x: -x[1]):
    W(f'     {k:<14} {v}')
W('')
W(f'  残留的斜体证据标注 <em>(review analysis)</em>: '
  f'{sum(len(re.findall(r"<em>\(review analysis\)</em>|<em>\(Amazon.ca data\)</em>|<em>\(manufacturer claim\)</em>|<em>\(buyer feedback\)</em>", STYLE.sub(" ", io.open(p,encoding="utf-8").read()))) for p in pages)} 处')

W('')
W('=' * 90)
W('ProsCons 渲染抽查（是否保住了 **粗体** 与链接，是否出现字面星号）')
W('=' * 90)
h = io.open(f'{D}/reviews/laifen/index.html', encoding='utf-8').read()
i = h.find('class="proscons"')
if i < 0:
    W('   未找到 proscons')
else:
    seg = h[i:i + 1400]
    seg = re.sub(r'\s+', ' ', seg)
    W('   ' + seg[:1100])
W('')
literal = sum(len(re.findall(r'\*\*[A-Za-z]', STYLE.sub(' ', io.open(p, encoding='utf-8').read()))) for p in pages)
W(f'  全站字面 ** 残留（应为 0）: {literal} 处')
W(f'  全站字面 *(...)  残留: '
  f'{sum(len(re.findall(r"\\*\\((?:review analysis|Amazon\\.ca data|manufacturer claim|buyer feedback)\\)", STYLE.sub(" ", io.open(p,encoding="utf-8").read()))) for p in pages)} 处')

io.open('analysis/_evidence_proscons.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written analysis/_evidence_proscons.txt')
