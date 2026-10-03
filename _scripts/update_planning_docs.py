"""把规划文档里「GA4 + Plausible」的旧计划更新为实际技术栈（GA4 + Clarity）。"""
import io
import os

EDITS = {
    'deliverables/Astro技术栈清单.md': [
        ('GA4 + Google Search Console + Plausible',
         'GA4 + Google Search Console + Bing Webmaster + Microsoft Clarity'),
        ('GA4 看流量，GSC 看收录，Plausible 做隐私友好兜底',
         'GA4 看流量，GSC 看收录，Bing 看必应表现，Clarity 看会话回放与热图'),
    ],
    'deliverables/技术SEO与信息架构规划.md': [
        ('`/privacy-policy/` | 隐私（GA4/Plausible）',
         '`/privacy-policy/` | 隐私（GA4 + Microsoft Clarity）'),
        ('- [ ] GA4 + GSC + Plausible 接入验证',
         '- [ ] GA4 + GSC + Bing Webmaster + Microsoft Clarity 接入验证'),
    ],
}

for path, pairs in EDITS.items():
    if not os.path.exists(path):
        print(f'  !! 不存在 {path}')
        continue
    t = io.open(path, encoding='utf-8').read()
    n = 0
    for old, new in pairs:
        if old in t:
            t = t.replace(old, new)
            n += 1
        else:
            print(f'  !! 未找到于 {os.path.basename(path)}: {old[:60]}')
    if n:
        io.open(path, 'w', encoding='utf-8').write(t)
    print(f'{os.path.basename(path)}: 改 {n} 处')

# 复查
print()
print('=== 复查：非形容词的 Plausible 残留 ===')
import re
left = []
for root in ('deliverables', 'site/src'):
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in ('node_modules', '.astro', 'dist')]
        for f in fn:
            if not f.endswith(('.md', '.mdx', '.astro', '.ts', '.mjs')):
                continue
            p = os.path.join(dp, f)
            t = io.open(p, encoding='utf-8', errors='ignore').read()
            for m in re.finditer(r'(?i)plausible', t):
                seg = t[max(0, m.start() - 60):m.end() + 60]
                # 形容词用法会出现在 is/are/as/and 等词附近
                if re.search(r'(?i)is plausible|are plausible|as plausible|plausible\.|plausible,|\*\*plausible', seg):
                    continue
                left.append((p, re.sub(r'\s+', ' ', seg)))
for p, seg in left:
    print(f'   {p}')
    print(f'      …{seg}…')
if not left:
    print('   已无工具名残留 ✓')
