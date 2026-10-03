"""
Build the deliverable workbook: Laifen Canada affiliate-site feasibility analysis.
"""
import pandas as pd, numpy as np, re, os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.formatting.rule import ColorScaleRule

os.makedirs('deliverables', exist_ok=True)
OUT = 'deliverables/Laifen-Canada-关键词与可行性分析.xlsx'

m = pd.read_pickle('analysis/master.pkl')
scored = pd.read_pickle('analysis/scored.pkl')
ont = pd.read_pickle('analysis/ontopic.pkl')
rev = pd.read_pickle('analysis/revenue_model.pkl')

for d in (m, scored, ont):
    d['kw'] = d['Keyword'].astype(str).str.lower().str.strip()

BRAND = r'laifen|dyson|shark|\bghd\b|\bt3\b|babyliss|revlon|conair|drybar|zuvi'

# ---------------------------------------------------------------- styles
H_FILL = PatternFill('solid', fgColor='1F3864')
H_FONT = Font(color='FFFFFF', bold=True, size=10)
TITLE_FONT = Font(bold=True, size=13, color='1F3864')
SUB_FONT = Font(italic=True, size=9, color='595959')
THIN = Side(style='thin', color='BFBFBF')
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
WRAP = Alignment(wrap_text=True, vertical='top')

wb = Workbook()
wb.remove(wb.active)


def add_sheet(name, df, colwidths=None, number_formats=None, freeze='A2', color_scale_cols=None):
    ws = wb.create_sheet(name[:31])
    ws.append(list(df.columns))
    for c in range(1, len(df.columns) + 1):
        cell = ws.cell(row=1, column=c)
        cell.fill = H_FILL
        cell.font = H_FONT
        cell.alignment = Alignment(wrap_text=True, vertical='center', horizontal='center')
        cell.border = BORDER
    for _, r in df.iterrows():
        ws.append(['' if (isinstance(v, float) and pd.isna(v)) else v for v in r.tolist()])
    if colwidths:
        for i, w in enumerate(colwidths, start=1):
            ws.column_dimensions[get_column_letter(i)].width = w
    if number_formats:
        for col, fmt in number_formats.items():
            for row in range(2, ws.max_row + 1):
                ws.cell(row=row, column=col).number_format = fmt
    ws.freeze_panes = freeze
    ws.auto_filter.ref = ws.dimensions
    if color_scale_cols:
        for col in color_scale_cols:
            L = get_column_letter(col)
            ws.conditional_formatting.add(
                f'{L}2:{L}{ws.max_row}',
                ColorScaleRule(start_type='min', start_color='F8696B',
                               mid_type='percentile', mid_value=50, mid_color='FFEB84',
                               end_type='max', end_color='63BE7B'))
    return ws


# ================================================================ 1. DASHBOARD
ws = wb.create_sheet('01_结论与评分')
ws.column_dimensions['A'].width = 42
ws.column_dimensions['B'].width = 22
ws.column_dimensions['C'].width = 78
ws['A1'] = 'Laifen 加拿大联盟站 — 可行性分析结论'
ws['A1'].font = TITLE_FONT
ws['A2'] = '数据源: Semrush CA 数据库, 34个 broad-match 关键词库 + 2个 SERP 页面库 (导出日 2026-10-02)'
ws['A2'].font = SUB_FONT

rows = [
    ('', '', ''),
    ('【最终结论】', '有条件可行 — 不建议做"纯 Laifen 单品站"', ''),
    ('总体评分', '5.7 / 10', '需求真实但盘子小、佣金薄；必须做成"吹风机决策站"而非"Laifen 站"，并引入非联盟收入'),
    ('', '', ''),
    ('【核心数据】', '', ''),
    ('全网去重关键词总数', '438,477', '34个导出文件互相大量重叠，去重后真实词量'),
    ('有搜索量的关键词', '181,512', '59% 的关键词在加拿大月搜索量=0'),
    ('同主题核心盘 (相关性≥80)', '247,180 /月', '真正的"吹风机意图"搜索量'),
    ('放宽口径主题盘 (相关性≥70)', '661,030 /月', '含大量边缘词'),
    ('Laifen 品牌词量', '16,900 /月', '457个含 laifen 的词'),
    ('Laifen 占主题盘份额', '2.8%', '288词/12,730月搜索 (相关性口径)'),
    ('Dyson 品牌词量', '1,311,160 /月', 'Dyson 在美发工具品类是绝对主导'),
    ('Dyson 占主题盘份额', '41.2%', ''),
    ('Shark 占主题盘份额', '12.5%', ''),
    ('非品牌开放市场', '185,880 /月 (41.1%)', '4,888个词 — 这是新站唯一能抢的地方'),
    ('', '', ''),
    ('【5个决定性发现】', '', ''),
    ('1. 品牌认知已形成，但很浅', '利好', '"laifen hair dryer" 3,600/月 + "laifen" 1,900/月，说明加拿大已有真实品牌搜索需求'),
    ('2. Laifen 在"平替"流量里完全缺席', '重大机会', 'SERP数据显示 Laifen 在 "hair dryer like dyson"(61条) 和 "dyson dupe hair dryer"(48条) 中排名数为 0'),
    ('3. 但平替词本身搜索量极小', '风险', '"dupe/alternative/like dyson" 全库仅 650/月 — 流量天花板极低，不能作为唯一支柱'),
    ('4. 联盟佣金结构性地薄', '重大风险', 'CPC中位数仅 $0.41；AOV约CAD200、佣金3-6% → Amazon纯佣金仅 $0.041/访问'),
    ('5. 新站有真实排名机会', '利好', 'SERP中 41-50% 的排名页面 Page AS ≤5，DR0 新站可竞争'),
    ('', '', ''),
    ('【建议打法】', '', ''),
    ('站点定位', '吹风机决策站', '覆盖 "best hair dryer / dupe / vs / 按发质" — Laifen 作为核心推荐而非唯一内容'),
    ('第一优先内容', '平替与对比', '"hair dryer like dyson" / "laifen vs dyson" — 竞品位空缺、意图最热'),
    ('第二优先内容', 'Best/榜单页', '33,160/月，但中位KD 41（最难），需外链投入'),
    ('第三优先内容', '按发质细分', 'curly/fine/frizzy/thick — 长尾多、KD 低、转化好'),
    ('第四优先内容', '加拿大本地化', '10,100/月，CPC $0.37（品类最高）— 含 Costco/BestBuy/Sephora 渠道'),
    ('必须做的收入结构', '联盟 + 展示广告 + 品牌赞助', '纯Amazon联盟在乐观流量下也只有 $361/月'),
    ('', '', ''),
    ('【收入模型】', 'base 情景 (第1-2年)', ''),
    ('可排名词库', '508词 / 223,330月搜索', 'vol≥50 且 可排名难度≤45'),
    ('预计月访问量', '4,503', '假设占词库60%进入前30、混合CTR 5.5%、点击留存61%'),
    ('纯 Amazon 联盟', '$186 /月', '$0.041 /访问 — 不可行'),
    ('Amazon + Laifen 直连', '$243 /月', '$0.054 /访问'),
    ('+ 展示广告', '$297 /月', '$0.066 /访问'),
    ('+ 品牌赞助 (月$1,500)', '$1,797 /月', '$0.399 /访问 — 只有加上这层才成立'),
    ('', '', ''),
    ('【Go / No-Go 判据】', '', ''),
    ('继续投入的条件', '', '能在6个月内拿到 Laifen 直连联盟或 $1,000+/月 的赞助位'),
    ('建议止损点', '', '18个月后月访问 <8,000 且月收入 <$500，则应停止投入'),
    ('最大不确定性', '', 'SEMrush 显示 "dupe/alternative" 仅650/月，但竞品却专门做这类内容并获流量 — 说明该词簇被低估，需用 GSC/GA 实测验证'),
]
r = 4
for a, b, c in rows:
    ws.cell(row=r, column=1, value=a)
    ws.cell(row=r, column=2, value=b)
    ws.cell(row=r, column=3, value=c)
    if a.startswith('【'):
        for col in range(1, 4):
            ws.cell(row=r, column=col).fill = PatternFill('solid', fgColor='D9E2F3')
            ws.cell(row=r, column=col).font = Font(bold=True, size=10, color='1F3864')
    ws.cell(row=r, column=1).alignment = WRAP
    ws.cell(row=r, column=2).alignment = WRAP
    ws.cell(row=r, column=3).alignment = WRAP
    r += 1
# highlight the verdict (content starts at row 4: blank spacer is the first tuple)
ws['A5'].font = Font(bold=True, size=11, color='C00000')
ws['B5'].font = Font(bold=True, size=11, color='C00000')
ws['A6'].font = Font(bold=True, size=14, color='C00000')
ws['B6'].font = Font(bold=True, size=14, color='C00000')

# ================================================================ 2. brand benchmark
rows = []
for name, pat in [('Laifen', 'laifen'), ('Dyson', 'dyson'), ('Shark', 'shark'),
                  ('GHD', r'\bghd\b'), ('T3', r'\bt3\b'), ('BaByliss', 'babyliss'),
                  ('Revlon', 'revlon'), ('Conair', 'conair'), ('Drybar', 'drybar'),
                  ('Zuvi', 'zuvi')]:
    s = m[m['kw'].str.contains(pat, regex=True, na=False) & (m['Volume'] > 0)]
    rows.append({'品牌': name, '关键词数': len(s), '月搜索总量': int(s['Volume'].sum()),
                 '平均单词搜索量': round(s['Volume'].mean(), 1),
                 '最大单词搜索量': int(s['Volume'].max()),
                 '中位KD': s['KD'].median(), '平均CPC(USD)': round(s['CPC'].mean(), 2)})
s = m[m['kw'].str.contains(r'dupe|alternative|like dyson|similar to dyson', regex=True, na=False) & (m['Volume'] > 0)]
rows.append({'品牌': '平替/dupe词簇(全类目)', '关键词数': len(s), '月搜索总量': int(s['Volume'].sum()),
             '平均单词搜索量': round(s['Volume'].mean(), 1), '最大单词搜索量': int(s['Volume'].max()),
             '中位KD': s['KD'].median(), '平均CPC(USD)': round(s['CPC'].mean(), 2)})
bd = pd.DataFrame(rows).sort_values('月搜索总量', ascending=False)
add_sheet('02_品牌竞争力对比', bd, colwidths=[24, 12, 15, 16, 16, 10, 14],
          number_formats={3: '#,##0', 4: '#,##0.0', 5: '#,##0', 7: '$#,##0.00'})

# ================================================================ 3. Laifen branded
la = m[m['kw'].str.contains('laifen', na=False) & (m['Volume'] > 0)].copy()
la = la.sort_values('Volume', ascending=False)
laf = pd.DataFrame({
    '关键词': la['Keyword'], '月搜索量': la['Volume'].astype(int), 'KD': la['KD'],
    '预估CPC(USD)': la['CPC'], '搜索意图': la['Intent'], '相关性': la['Relevance'],
    '竞争密度': la['CompDensity'], 'SERP特征': la['SERP'], '来源种子词': la['best_seed'],
})
add_sheet('03_Laifen品牌词全表', laf,
          colwidths=[42, 12, 7, 13, 26, 10, 11, 52, 26],
          number_formats={2: '#,##0', 4: '$#,##0.00', 6: '0', 7: '0.00'})

# ================================================================ 4. opportunity master
nb = scored[~scored['kw'].str.contains(BRAND, na=False)].copy()
nb = nb[(nb['Volume'] >= 30)].sort_values('Opportunity', ascending=False)
op = pd.DataFrame({
    '关键词': nb['Keyword'], '月搜索量': nb['Volume'].astype(int), 'KD(Semrush)': nb['KD'],
    'KD(有效/补全)': nb['KD_eff'].round(0), '预估CPC(USD)': nb['CPC'], '搜索意图': nb['Intent'],
    '相关性': nb['Relevance'], '点击留存率': nb['click_retention'].round(2),
    '机会评分': nb['Opportunity'], 'AI概览': np.where(nb['SERP'].str.contains('AI Overview', na=False), 'Y', ''),
    '热门商品卡': np.where(nb['SERP'].str.contains('Popular products', na=False), 'Y', ''),
    '评论模块': np.where(nb['SERP'].str.contains('Reviews', na=False), 'Y', ''),
    'SERP特征': nb['SERP'], '来源种子词': nb['best_seed'],
})
add_sheet('04_非品牌机会词总表', op,
          colwidths=[44, 11, 11, 13, 13, 24, 9, 11, 10, 8, 11, 9, 50, 24],
          number_formats={2: '#,##0', 3: '0', 4: '0', 5: '$#,##0.00', 7: '0', 8: '0.00'},
          color_scale_cols=[9])

# ================================================================ 5. money list
mon = ont[(~ont['kw'].str.contains(BRAND, na=False)) & (ont['Volume'] >= 100)
          & (ont['KD_eff'] <= 45)].sort_values(['Opportunity', 'Volume'], ascending=False)
money = pd.DataFrame({
    '优先级': range(1, len(mon) + 1),
    '关键词': mon['Keyword'], '月搜索量': mon['Volume'].astype(int), 'KD': mon['KD'],
    'KD_有效': mon['KD_eff'].round(0), 'CPC(USD)': mon['CPC'], '意图': mon['Intent'],
    '机会评分': mon['Opportunity'], '建议内容类型': [
        '榜单/best页' if re.search(r'\bbest\b|top ', k) else
        '对比页' if re.search(r'\bvs\b|versus|compare', k) else
        '购买/价格页' if re.search(r'price|buy|sale|deal|coupon|where', k) else
        '评测页' if re.search(r'review', k) else
        '按发质指南' if re.search(r'curly|fine|thin|frizz|thick|damaged', k) else
        '功能科普页' if re.search(r'ionic|quiet|light|fast|voltage|diffus', k) else
        '品类主页面'
        for k in mon['kw']],
})
add_sheet('05_可排名机会词(money list)', money,
          colwidths=[8, 44, 11, 8, 10, 11, 24, 10, 20],
          number_formats={3: '#,##0', 4: '0', 5: '0', 6: '$#,##0.00', 9: '0.0'},
          color_scale_cols=[9])

# ================================================================ 6. comparison
vs = ont[ont['kw'].str.contains(r'\bvs\b|\bversus\b|compare|comparison', na=False)] \
    .sort_values('Volume', ascending=False)
vsd = pd.DataFrame({
    '关键词': vs['Keyword'], '月搜索量': vs['Volume'].astype(int), 'KD': vs['KD'],
    'KD_有效': vs['KD_eff'].round(0), 'CPC(USD)': vs['CPC'], '相关性': vs['Relevance'],
    '机会评分': vs['Opportunity'], 'SERP特征': vs['SERP'],
})
add_sheet('06_对比类关键词(vs)', vsd,
          colwidths=[46, 11, 8, 10, 11, 9, 10, 50],
          number_formats={2: '#,##0', 4: '0', 5: '$#,##0.00'},
          color_scale_cols=[7])

# ================================================================ 7. dupe
dupe = m[m['kw'].str.contains(r'dupe|alternative|like dyson|similar to dyson|knock ?off', na=False)
         & (m['Volume'] > 0)].sort_values('Volume', ascending=False)
dd = pd.DataFrame({
    '关键词': dupe['Keyword'], '月搜索量': dupe['Volume'].astype(int), 'KD': dupe['KD'],
    'CPC(USD)': dupe['CPC'], '意图': dupe['Intent'], '相关性': dupe['Relevance'],
    'SERP特征': dupe['SERP'], '来源种子词': dupe['best_seed'],
})
add_sheet('07_平替关键词(dupe)全表', dd,
          colwidths=[44, 11, 8, 11, 24, 9, 50, 24],
          number_formats={2: '#,##0', 4: '$#,##0.00'})

# ================================================================ 8. cluster
CL = {
    'best/榜单': r'\bbest\b|\btop \d|top rated',
    'review/评测': r'review|rated|worth it|is it worth',
    'cheap/budget/平替': r'\bcheap|budget|affordable|dupe|alternative|knock ?off|cheaper',
    'vs/对比': r'\bvs\b|\bversus\b|compare|comparison',
    'curly/卷发': r'\bcurly|curls|wavy|coily|kinky',
    'fine/细软发': r'\bfine hair|thin hair|thinning',
    'thick/粗硬发': r'\bthick hair|coarse hair|dense hair',
    'frizzy/毛躁受损': r'\bfrizz|damaged|dry hair|split end',
    'diffuser/扩散风嘴': r'diffus',
    'ionic/离子技术': r'\bionic|negative ion|ceramic|tourmaline|infrared',
    'lightweight/轻量': r'light ?weight|weigh|how much does|\bgrams?\b',
    'quiet/静音': r'\bquiet|silent|noise|decibel|\bdb\b|loud',
    'fast/风速功率': r'\bfast|fastest|speed|quick|powerful|high.?speed|watt|\brpm\b|strong',
    'travel/便携': r'\btravel|portable|compact|foldable|mini',
    'professional/专业沙龙': r'professional|salon|\bpro\b|stylist|barber',
    'brush/造型梳': r'\bbrush|styler|straightener|curler|airwrap|multi.?styler',
    'heat damage/护发安全': r'heat damage|damage|\bsafe|temperature|heat setting|burnt',
    'attachments/配件': r'attachment|nozzle|concentrator|magnetic',
    'voltage/电压插头': r'voltage|\bvolt|\bplug|adapter|220|110|dual voltage',
    'buy/价格渠道': r'\bbuy|price|cost|where to|for sale|\bdeal|discount|coupon|amazon|walmart|costco|sephora|shoppers|best ?buy',
    'how to/教程': r'how to|tutorial|guide|tips|step by step',
    'canada/加拿大本地': r'canada|canadian',
    'french/法语(魁北克)': r'sechoir|seche cheveux|avis|meilleur|cheveux',
}
rows = []
tot = ont['Volume'].sum()
for name, pat in CL.items():
    s = ont[ont['kw'].str.contains(pat, regex=True, na=False)]
    nz = s[s['KD'].notna()]
    rows.append({'主题簇': name, '关键词数': len(s), '月搜索量': int(s['Volume'].sum()),
                 '占主题盘%': round(100 * s['Volume'].sum() / tot, 1),
                 '中位KD': nz['KD'].median() if len(nz) else np.nan,
                 '平均CPC(USD)': round(s['CPC'].mean(), 2) if len(s) else 0,
                 '最大单词量': int(s['Volume'].max()) if len(s) else 0})
cl = pd.DataFrame(rows).sort_values('月搜索量', ascending=False)
cl['累计占比%'] = (100 * cl['月搜索量'].cumsum() / cl['月搜索量'].sum()).round(1)
add_sheet('08_主题簇需求分布', cl, colwidths=[24, 11, 14, 11, 9, 13, 12, 11],
          number_formats={3: '#,##0', 7: '#,##0'}, color_scale_cols=[3])

# ================================================================ 9. SERP gap
serp_rows = [
    {'查询词': 'hair dryer like dyson', '结果总数': 71, '自然结果数': 61,
     'Page AS≤5 占比': '41%', 'Laifen是否出现': '否 (0条)',
     '排名第1': 'dysoncanada.ca (品牌官网)', '排名第2': 'reddit.com',
     '排名第3': 'byrdie.com', '最佳低权重机会位': 'P2 reddit / P7 facebook / P12 youtube'},
    {'查询词': 'dyson dupe hair dryer', '结果总数': 59, '自然结果数': 48,
     'Page AS≤5 占比': '50%', 'Laifen是否出现': '否 (0条)',
     '排名第1': 'reddit.com (AI Overview在此)', '排名第2': 'mashable.com',
     '排名第3': 'wwd.com', '最佳低权重机会位': 'P1 reddit / P4 youtube / P8 tiktok'},
]
sk = pd.DataFrame(serp_rows)
add_sheet('09_SERP空缺分析', sk, colwidths=[24, 10, 12, 13, 14, 30, 18, 16, 34])

# competitor detail
for f, nm in [('semrush数据/dyson-dupe-hair-dryer_serp_urls_ca_2026-10-02_11-05-22.xlsx', '10_SERP竞争者_dyson-dupe'),
              ('semrush数据/hair-dryer-like-dyson_serp_urls_ca_2026-10-02_11-05-00.xlsx', '11_SERP竞争者_like-dyson')]:
    df = pd.read_excel(f)
    df = df.rename(columns={'Position': '排名', 'Type': '结果类型', 'Domain': '域名', 'URL': 'URL',
                            'Page AS': '页面权重AS', 'Ref.Domains': '引用域', 'Backlinks': '外链数',
                            'Search Traffic': '该页搜索流量', 'URL Keywords': '该页关键词数',
                            'SERP Features': 'SERP特征'})
    add_sheet(nm, df, colwidths=[7, 20, 22, 70, 11, 10, 10, 14, 14, 30],
              number_formats={5: '#,##0', 6: '#,##0', 7: '#,##0', 8: '#,##0', 9: '#,##0'})

# ================================================================ 12. revenue model
rv = rev.rename(columns={'scenario': '排名情景', 'monetization': '变现结构',
                         'sessions/mo': '月访问量', 'sessions/yr': '年访问量',
                         'affiliate_rev/mo': '联盟收入/月', 'ads_rev/mo': '广告收入/月',
                         'sponsored_rev/mo': '赞助收入/月', 'total_rev/mo_CAD': '总收入/月(CAD)',
                         'total_rev/yr_CAD': '总收入/年(CAD)', 'rev_per_session_CAD': '每访问收入(CAD)'})
add_sheet('12_收入模型', rv, colwidths=[30, 36, 12, 12, 14, 14, 14, 15, 16, 15],
          number_formats={3: '#,##0', 4: '#,##0', 5: '#,##0', 6: '#,##0', 7: '#,##0',
                          8: '#,##0', 9: '#,##0', 10: '$#,##0.000'})

# ================================================================ 13. SERP risk
FEATS = ['AI Overview', 'Popular products', 'People also ask', 'Video', 'Video carousel',
         'Short videos', 'Reviews', 'Image', 'Image pack', 'Sitelinks', 'Ads top',
         'Ads bottom', 'Discussions and forums', 'Knowledge panel', 'Related searches']
core = ont.copy()
core['SERP'] = core['SERP'].fillna('')
rows = []
for f in FEATS:
    s = core[core['SERP'].str.contains(re.escape(f), na=False)]
    rows.append({'SERP特征': f, '覆盖关键词数': len(s), '覆盖月搜索量': int(s['Volume'].sum()),
                 '占主题盘%': round(100 * s['Volume'].sum() / core['Volume'].sum(), 1),
                 '对联盟站影响': '极大负面(AI直接回答)' if f == 'AI Overview' else
                                '极大负面(Google自家商品卡截流)' if f == 'Popular products' else
                                '负面(视频占据版位)' if 'video' in f.lower() else
                                '正面(用户在看评测)' if f == 'Reviews' else
                                '中性/负面(挤压自然位)' if f.startswith('Ads') or f == 'Image pack' else '中性'})
sf = pd.DataFrame(rows).sort_values('覆盖月搜索量', ascending=False)
add_sheet('13_SERP特征风险', sf, colwidths=[24, 14, 14, 11, 34],
          number_formats={2: '#,##0', 3: '#,##0'}, color_scale_cols=[3])

# ================================================================ 14. data caveats
cv = pd.DataFrame([
    {'项目': '数据来源', '说明': 'Semrush CA 数据库, 34个 broad-match 关键词导出 (2026-10-02)', '影响': '—'},
    {'项目': '导出上限', '说明': '每个文件固定 50,003 行 — 这是 Semrush 导出上限，不是完整词库', '影响': '部分长尾词可能缺失'},
    {'项目': 'Broad Match 噪声', '说明': '宽匹配会带出 dyson 吸尘器、除湿机、leivoit 加湿器等跨品类词', '影响': '分析已用 12,924 个吹风机相关词做过滤'},
    {'项目': 'KD 覆盖率', '说明': '仅 3.8% 的关键词有 Semrush KD 值', '影响': '其余用词长+搜索量启发式补全，标注为 KD_有效'},
    {'项目': 'Volume 分辨率', '说明': 'Semrush CA 最小可报告值为 10，大量词显示为 10/20', '影响': '无法区分真实微流量词'},
    {'项目': '零搜索量词', '说明': '181,512 / 438,477 (59%) 的词月搜索量为 0', '影响': '已从机会分析中剔除'},
    {'项目': '重复文件', '说明': 'laifen_all-keywords 出现2份、lightweight/quiet/ionic 各有重复导出', '影响': '已按 MD5 去重，实际独立种子词 34 个'},
    {'项目': 'CPC 为 USD', '说明': 'Semrush CPC 为美元计价', '影响': '折算 CAD 约 ×1.37'},
    {'项目': 'SERP 仅2个词', '说明': '只有 "hair dryer like dyson" 与 "dyson dupe hair dryer" 有排名数据', '影响': '竞争强度结论基于这2个词，非全站'},
    {'项目': '收入模型假设', '说明': '联盟点击率18%、成交率2.5%、客单价CAD200、佣金3-6%、展示广告RPM $12-22', '影响': '属情景推演，非预测；对假设线性敏感'},
    {'项目': 'asin数据文件夹', '说明': '该文件夹为空，未包含在本次分析中', '影响': '如需 Amazon ASIN 维度分析需补充数据'},
    {'项目': '关键词本地化', '说明': '含少量非英语词条（法语、中文及编码乱码项）', '影响': '法语词已单列为魁北克机会，乱码项建议剔除'},
])
add_sheet('14_数据口径与局限', cv, colwidths=[20, 68, 44], freeze='A2')

wb.save(OUT)
print('saved:', OUT)
print('sheets:')
for s in wb.sheetnames:
    print('  -', s, f'({wb[s].max_row-1} rows)')
