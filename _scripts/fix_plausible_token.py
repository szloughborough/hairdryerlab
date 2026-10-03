"""按 token 修复两个规划文档里的 Plausible 工具名。"""
import io
import os
import re

TARGETS = [
    'deliverables/Astro技术栈清单.md',
    'deliverables/技术SEO与信息架构规划.md',
]

for p in TARGETS:
    if not os.path.exists(p):
        print(f'  !! 不存在 {p}')
        continue
    t = io.open(p, encoding='utf-8').read()
    print(f'=== {os.path.basename(p)} 里的原始行 ===')
    for i, line in enumerate(t.splitlines(), 1):
        if 'Plausible' in line:
            print(f'   L{i}: {line.strip()[:170]}')

    # 逐条替换：工具列举与描述句
    t2 = t.replace('GA4 + GSC + Plausible', 'GA4 + GSC + Bing + Clarity')
    t2 = t2.replace('GA4 + Google Search Console + Plausible',
                    'GA4 + Google Search Console + Bing Webmaster + Microsoft Clarity')
    t2 = re.sub(r'Plausible\s*做隐私友好兜底', 'Clarity 看会话回放与热图', t2)
    t2 = re.sub(r'(?<![\w])Plausible(?![\w])', 'Microsoft Clarity', t2)

    if t2 != t:
        io.open(p, 'w', encoding='utf-8').write(t2)
        print(f'   → 已更新')
    else:
        print(f'   → 无需改动')
    print()

print('=== 复查（只列工具名用法，忽略英文形容词）===')
left = 0
for root in ('deliverables', 'site/src'):
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in ('node_modules', '.astro', 'dist')]
        for f in fn:
            if not f.endswith(('.md', '.mdx', '.astro', '.ts', '.mjs')):
                continue
            fp = os.path.join(dp, f)
            t = io.open(fp, encoding='utf-8', errors='ignore').read()
            for m in re.finditer(r'(?i)plausible', t):
                seg = t[max(0, m.start() - 70):m.end() + 70]
                if re.search(r'(?i)is plausible|are plausible|as plausible|plausible\.|plausible,|\*\*plausible|with a plausible', seg):
                    continue
                print(f'   {fp}')
                print(f'      …{re.sub(chr(92)+"s+", " ", seg)}…')
                left += 1
if not left:
    print('   已无工具名残留 ✓（文章里的均为英文形容词）')
