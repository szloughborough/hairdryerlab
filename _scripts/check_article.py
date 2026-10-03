"""
Pre-publish compliance checker for Hair Dryer Lab MDX articles.
Type-aware: applies commercial-page rules only to commercial page types.

Usage: python check_article.py <path-to-mdx>
"""
import re, io, sys

PATH = sys.argv[1] if len(sys.argv) > 1 else 'deliverables/drafts/best-dyson-alternatives.mdx'
c = io.open(PATH, encoding='utf-8').read()

m = re.match(r'(?s)^---\n(.*?)\n---\n(.*)$', c)
fm, body = (m.group(1), m.group(2)) if m else ('', c)

def fmval(key, default=''):
    mm = re.search(rf'(?m)^{key}:\s*"?([^"\n]+)"?\s*$', fm)
    return mm.group(1).strip() if mm else default

PTYPE = fmval('type', 'best')
ROUTE = fmval('route', '')
# 法律/信任页（about / contact / terms / privacy…）与内容页规则不同：
# 它们不需要表格、带单位数字或证据标签。判定依据是「有 route 且不以 guides/ 开头」。
IS_TRUST = (PTYPE == 'learn') and bool(ROUTE) and not ROUTE.startswith('guides/')
COMMERCIAL = {'best', 'review', 'compare', 'ca'}
GUIDE = {'for'}
LEARN = {'learn'}
IS_COMM = PTYPE in COMMERCIAL

lines = body.split('\n')
h1 = [l for l in lines if re.match(r'^# ', l)]
h2 = [l for l in lines if re.match(r'^## ', l)]
h3 = [l for l in lines if re.match(r'^### ', l)]

rep = []
def R(*a): rep.append(' '.join(str(x) for x in a))
def ok(cond): return 'PASS' if cond else '**FAIL**'

R('=' * 100)
R(f'合规检查: {PATH.split("/")[-1]}   页面类型: {PTYPE}'
  f'{"（法律/信任页规则）" if IS_TRUST else "（商业页规则）" if IS_COMM else "（指南页规则）" if PTYPE in GUIDE else "（科普页规则）"}')
R('=' * 100)

# ================= A. structure =================
R('\n## A. 页面结构')
fm_h1 = fmval('h1')
R(f'  frontmatter h1 存在: {ok(bool(fm_h1))}   ({fm_h1[:60] if fm_h1 else "缺失"})')
R(f'  正文 H1 数量 = {len(h1)}  {ok(len(h1) <= 1)}   (0=站点副本 / 1=草稿，均可；>=2 为重复)')
R(f'  H2 数量 = {len(h2)}   H3 数量 = {len(h3)}')

# 导语块 = 第一个小标题 / 分隔线 之前的连续正文段落（最多 3 段）。
# 只取首段会低估真实导语长度——排版上导语常由 2–3 段组成。
clean = re.sub(r'(?s)<!--.*?-->', '', body)
blocks = []
for blk in re.split(r'\n\s*\n', clean):
    s = blk.strip()
    if not s:
        continue
    # H1 在草稿里存在、在站点副本里被降级去掉，两种情况都跳过；
    # 遇到第一个 H2（小节标题）或分隔线则导语块结束。
    if s.startswith('#'):
        if s.startswith('##'):
            break
        continue
    if s.startswith('---'):
        break
    if s.startswith('|'):
        continue
    blocks.append(s)
    if len(blocks) >= 3:
        break
intro = ' '.join(blocks)
verdict_txt = fmval('verdict', '')
intro_full = (verdict_txt + ' ' + intro) if IS_TRUST else intro
iw = len([w for w in re.split(r'\s+', re.sub(r'[*`\[\]()]', ' ', intro_full)) if re.search(r'\w', w)])
lo = 60 if IS_TRUST else 70
R(f'  H1 后导语词数 = {iw}  {ok(lo <= iw <= 240)}   '
  f'(目标 90-110，下限 {lo}，上限 240；共 {len(blocks)} 段{"，含 verdict" if IS_TRUST else ""})')

# self-contained H2: generic blacklist for all types
GENERIC = r'(?i)^(what|why|how|when|where|which|more|other|final|summary|conclusion|verdict|faq|faqs|overview|introduction|key takeaways|the bottom line|next steps)\s*$'
gens = [re.sub(r'^##\s*', '', l).strip() for l in h2
        if re.match(GENERIC, re.sub(r'^##\s*', '', l).strip())]
R(f'  空泛标题(H2) = {len(gens)}  {ok(len(gens)==0)}')
for g in gens:
    R(f'      ⚠ 空泛: "{g}"')

if IS_COMM:
    # 核心实体不再硬编码品牌名单，改为从本页 frontmatter 推导：
    # 产品品牌 + 主关键词首词，再叠加通用类目词。避免新品牌（如 Conair）被漏判。
    brands = set(b.strip().strip('"\'') for b in re.findall(r'(?m)^\s*-?\s*brand:\s*(.+)$', fm))
    pk = fmval('primaryKeyword', '')
    if pk:
        brands.add(pk.split()[0])
    brand_alt = '|'.join(re.escape(b) for b in brands if b)
    CORE = (r'(?i)' + (brand_alt + '|' if brand_alt else '')
            + r'hair dryer|hairdryer|blow dryer|alternative|dupe|comparison|vs\b')
    miss = [re.sub(r'^##\s*', '', l).strip() for l in h2
            if not re.search(CORE, re.sub(r'^##\s*', '', l))]
    R(f'  H2 含核心实体: {len(h2)-len(miss)}/{len(h2)}  {ok(len(miss)==0)}   '
      f'[商业页规则；实体={", ".join(sorted(brands)) or "（未识别）"}]')
    for g in miss:
        R(f'      ⚠ 缺实体: "{g}"')
else:
    R(f'  H2 含核心实体: 不适用（{PTYPE} 页按主题自包含判定）')

# ================= B. AI extractability =================
R('\n## B. AI / 大模型可抽取性')
nums = re.findall(r'\d+(?:\.\d+)?\s*(?:dB|mm|cm|m/s|g\b|kg|month|months|year|years|%|C\$|\$|V\b|W\b)', body)
tables = len(re.findall(r'(?m)^\|', body))
if IS_TRUST:
    num_floor, tab_floor = 0, 0          # 法律/信任页不要求表格与带单位数字
elif IS_COMM:
    num_floor, tab_floor = 15, 20
elif PTYPE in GUIDE:
    num_floor, tab_floor = 8, 5
else:
    num_floor, tab_floor = 3, 4
R(f'  带单位数字 = {len(nums)}  {ok(len(nums) >= num_floor)}   (要求 >={num_floor})')
R(f'  表格行数 = {tables}  {ok(tables >= tab_floor)}   (要求 >={tab_floor})')
ph = len(re.findall(r'【待', body))
R(f'  【待实测/待核实】占位符 = {ph}  {"PASS 已清零" if ph==0 else "**FAIL** 未清零不得发布"}')
# 联盟披露与 Last updated 由 Article.astro 布局统一渲染（品牌规范 §37 / §61），
# 草稿正文不应重复。此处仅作提示，不作为失败项；渲染结果由 verify_build.py 校验。
_has_lu = bool(re.search(r'(?i)last updated', body))
_has_disc = bool(re.search(r'(?i)affiliate link|commission', body))
R(f'  Last updated: 由布局渲染（正文{"也含" if _has_lu else "未含"}，均可）')
R(f'  联盟披露: 由布局渲染（正文{"也含，注意避免重复" if _has_disc else "未含，正确"}）')

# ================= C. FAQ =================
R('\n## C. FAQ')
faq_anchor = None
for pat in [r'(?i)frequently asked questions', r'(?i)\bFAQ\b']:
    mm = re.search(pat, body)
    if mm:
        faq_anchor = mm.start(); break
faq_block = body[faq_anchor:] if faq_anchor is not None else ''
qs = re.findall(r'(?m)^\*\*(.+?\?)\*\*\s*$', faq_block)
R(f'  FAQ 条数 = {len(qs)}  {ok(len(qs) >= 5)}   (要求 >=5)')
fm_faq = len(re.findall(r'(?m)^\s*-\s*q:', fm))
R(f'  frontmatter faq 条数 = {fm_faq}  {ok(fm_faq == len(qs))}   (须与正文一致)')
if qs:
    lens = []
    for q in qs:
        start = faq_block.index(f'**{q}**') + len(q) + 4
        rest = faq_block[start:]
        nxt = re.search(r'(?m)^\*\*.+?\?\*\*\s*$', rest)
        stop = re.search(r'(?m)^(---|## )', rest)
        ends = [x.start() for x in (nxt, stop) if x]
        seg = rest[:min(ends)] if ends else rest
        seg = re.sub(r'\[.*?\]\(.*?\)', '', seg)
        lens.append(len([w for w in re.split(r'\s+', seg) if re.search(r'\w', w)]))
    R(f'  答案词数 max = {max(lens)}  {ok(max(lens) <= 100)}   (要求 <=100)')
    R(f'  答案词数 列表 = {lens}')

# ================= D. trust =================
R('\n## D. 信任与合规')
if IS_TRUST:
    R('  研究方法/证据标签: 不适用（法律/信任页）')
else:
    R(f'  说明研究方法/来源: {ok(bool(re.search(r"(?i)we (analysed|analyzed|code|pull|built)|our (analysis|method|dataset|review)", body)))}')
    R(f'  证据等级标注: {ok(bool(re.search(r"(?i)Measured|Review analysis|Amazon\\.ca data|Buyer feedback|Manufacturer claim", body)))}')
# 先去掉引号内内容，避免把「我们不会声称"xxx"」这类否定表述误判为虚构资质
_noquote = re.sub(r'[“"][^”"]{0,200}[”"]', '', body)
R(f'  无虚构资质: {ok(not re.search(r"(?i)licensed (stylist|hairstylist)|certified trichologist|\\d+ years of experience", _noquote))}')
if IS_COMM:
    R(f'  价格核对日期: {ok(bool(re.search(r"20\d\d-\d\d-\d\d|checked on|checked 20", body)))}   [商业页规则]')
    nprod = len(re.findall(r'(?m)^\s*-\s*name:', fm)) or 5
    # 品牌规范 §70 用 "What we liked / What we didn't"；§32/§44 用 "Skip if" / "Do not buy X if"
    cons = (body.count("does not do well") + body.count("What we didn't")
            + body.count("Skip if") + body.count("Do not buy"))
    # 对比页按 §44 结构是「Who should buy A / Who should buy B」，两侧各一节即可，不按产品数要求
    need = 2 if PTYPE == 'compare' else nprod
    R(f'  缺点/不建议节数 = {cons}  {ok(cons >= need)}   (要求 >= {need}'
      f'{"（对比页按两侧计）" if PTYPE == "compare" else f"（= 产品数 {nprod}）"})')
else:
    R(f'  价格核对日期: 不适用（{PTYPE} 页）')
    R(f'  产品缺点节: 不适用（{PTYPE} 页）')

# ================= G. prohibited (reversed red lines) =================
R('\n## G. 禁止项扫描（借鉴包红线，必须反向）')
SIDE = r'(?i)the listing describes|the product page includes|the source listing|according to amazon|the listing states|source-backed details'
hits = re.findall(SIDE, body)
R(f'  旁观者措辞命中 = {len(hits)}  {ok(len(hits)==0)}')
for h in set(hits): R(f'      ⚠ "{h}"')
R(f'  未把零售商当卖点叙述者: {ok(not re.search(r"(?i)amazon (says|states|describes)", body))}')
# 联盟披露若正文重复出现，提示（避免与布局重复）
if re.search(r'(?i)may earn a commission|affiliate disclosure', body):
    R('  ⚠ 正文出现披露文案，注意与布局渲染的披露重复')

# ================= E. schema =================
R('\n## E. Schema 提示')
R(f'  frontmatter schema = {fmval("schema", "(未设置)")}')
R(f'  未使用 aggregateRating: {ok(not re.search(r"(?i)aggregateRating", c))}')
R(f'  未使用 Offer: {ok(not re.search(r"(?i)priceValidUntil|\"Offer\"", c))}')

# ================= F. links =================
R('\n## F. 内链与联盟链接')
# markdown 链接：[文字](/path/)
md_internal = re.findall(r'\]\(/', body)
# MDX 组件 props 里的站内链接：href="/path/" 或 href: '/path/'
# （§55 组件会在产物里渲染成真实 <a>，因此必须计入内链）
comp_internal = re.findall(r"href\s*[:=]\s*[\"']/", body)
# frontmatter 的 related 列表也是真实渲染的站内链接（§55(18) Related Content）
fm_related = re.findall(r'(?m)^\s+-\s+/[^/\s]', fm)
internal = md_internal + comp_internal + fm_related
aff = re.findall(r'\{\{affiliate', body)
R(f'  站内内链 = {len(internal)}  {ok(len(internal) >= 3)}   (要求 >=3)')
R(f'     markdown 链接 {len(md_internal)} · 组件 props {len(comp_internal)} · related {len(fm_related)}')
R(f'  联盟链接占位 = {len(aff)}')

R('\n' + '=' * 100)
fails = [l for l in rep if 'FAIL' in l]
R(f'结果: {"全部通过" if not fails else str(len(fails)) + " 项未通过"}')
R('=' * 100)

# 结果文件写入后必须带一行明确的机器可读标记，避免调用方误读上一次的陈旧结果
io.open('analysis/_compliance.txt', 'w', encoding='utf-8').write('\n'.join(rep))
print(f'written analysis/_compliance.txt  ({PATH})')

# 退出码约定：0 = 通过，2 = 有 FAIL，1 = 脚本崩溃（Python 异常）。
# 调用方必须区分 2 和 1 —— 否则崩溃会被误当成「检查失败」或静默通过。
sys.exit(2 if fails else 0)
