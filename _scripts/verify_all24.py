"""§55 全部 24 项组件的最终落地核验（DOM 口径，剔除内联 CSS）。"""
import glob
import io
import re

D = 'site/dist'
STYLE = re.compile(r'(?s)<style[^>]*>.*?</style>')
out = []
def W(*a): out.append(' '.join(str(x) for x in a))

pages = glob.glob(f'{D}/**/*.html', recursive=True)
def dom(p):
    return STYLE.sub(' ', io.open(p, encoding='utf-8').read())

SPEC = [
    ('1  Header', r'class="site-header"'),
    ('2  Footer', r'class="site-footer"'),
    ('3  Breadcrumb', r'class="breadcrumbs"'),
    ('4  Product Hero', r'class="product-hero"'),
    ('5  Lab Test Card', r'class="lab-test"'),
    ('6  Best For / Skip If', r'class="verdict-split"'),
    ('7  Quick Verdict', r'class="lede"'),
    ('8  Pros / Cons', r'class="proscons"'),
    ('9  Comparison Table', r'class="cmp-table"'),
    ('10 Product Card', r'class="pick"'),
    ('11 Affiliate CTA', r'class="cta"'),
    ('12 Price Box', r'class="price-box"'),
    ('13 Disclosure Box', r'class="disclosure"'),
    ('14 Methodology Box', r'class="method-box"'),
    ('15 Tested Badge', r'class="badge badge--'),
    ('16 Hair-Type Card', r'class="tile tile--hair"'),
    ('17 Feature Card', r'class="tile tile--feature"'),
    ('18 Related Content', r'class="related"'),
    ('19 Author Box', r'class="authorbox"'),
    ('20 Update Date', r'badge--updated'),
    ('21 FAQ', r'id="[^"]*faq"'),
    ('22 Newsletter', r'class="signup"'),
    ('23 Image caption', r'class="fig"'),
    ('24 Evidence / source note', r'class="ev '),
]

W('=' * 98)
W('§55 组件库（品牌规范要求 24 项）')
W('=' * 98)
used = notused = 0
for name, pat in SPEC:
    n = sum(len(re.findall(pat, dom(p), re.I)) for p in pages)
    np_ = sum(1 for p in pages if re.search(pat, dom(p), re.I))
    if n:
        tag = 'OK 已上线'
        used += 1
    else:
        tag = '-- 未渲染'
        notused += 1
    W(f'   {tag}  {name:<26} {n:>5} 处 / {np_:>2} 页')
W('')
W(f'   已上线 {used} / 未渲染 {notused}   （共 24 项）')

W('')
W('=' * 98)
W('§33 表格：移动端滚动外壳')
W('=' * 98)
ts = sum(len(re.findall(r'class="table-scroll"', dom(p))) for p in pages)
tbl = sum(len(re.findall(r'<table', dom(p))) for p in pages)
W(f'   <table> 总数 {tbl}，其中被 .table-scroll 包裹 {ts}')
W(f'   → {"全部已包裹 ✓" if tbl and ts >= tbl else ("部分未包裹" if ts else "**未包裹**")}')

W('')
W('=' * 98)
W('Related Content 抽查（/reviews/laifen/）')
W('=' * 98)
h = dom(f'{D}/reviews/laifen/index.html')
i = h.find('class="related"')
if i < 0:
    W('   未找到 .related')
else:
    seg = re.sub(r'\s+', ' ', h[i:i + 700])
    W('   ' + seg[:620])
    if h.find('class="related"') < 0:
        W('   （related 为空或未解析）')

W('')
W('=' * 98)
W('Related Content 解析质量（全站）')
W('=' * 98)
total_items = 0
fallback = 0
for p in pages:
    x = dom(p)
    for m in re.finditer(r'<li class="related__item">(.*?)</li>', x, re.S):
        total_items += 1
        label = re.sub(r'<[^>]+>', '', m.group(1)).strip()
        # 未解析成功的会退回成路径文字（含 /）
        if label.startswith('/') or '/' in label.split('·')[0]:
            fallback += 1
W(f'   related 条目总数 {total_items}')
W(f'   其中标题未解析（退回路径文字）{fallback}')
W(f'   → {"全部解析成功 ✓" if fallback == 0 else "**有 " + str(fallback) + " 条未解析**"}')

io.open('analysis/_all24_verify.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written analysis/_all24_verify.txt')
