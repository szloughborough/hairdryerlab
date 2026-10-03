"""
Build the SEO content-plan workbook: sitemap + per-page keyword mapping + 90-day roadmap.
"""
import io, re
import pandas as pd, numpy as np
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.formatting.rule import ColorScaleRule

SITEMAP = pd.read_pickle('analysis/sitemap.pkl')
ont = pd.read_pickle('analysis/ontopic.pkl')
ont['kw'] = ont['Keyword'].astype(str).str.lower().str.strip()
pool = ont[ont['Volume'] >= 10].copy()

# same page definitions (re-import for keyword detail)
PAGES = [
    ('/best/', 'best-hair-dryer', r'\bbest hair dryer|\bbest blow dryer|\bbest hairdryer'),
    ('/best/', 'best-dyson-alternatives', r'dyson (dupe|alternative|alternatives|similar|like)|dupe hair dryer|hair dryer like dyson|alternatives? to dyson'),
    ('/best/', 'best-hair-dryer-canada', r'best .*canada|canada.*best hair|best hair dryer canada'),
    ('/best/', 'best-curly-hair', r'best .*curly|curly.*best|best hair dryer for curls'),
    ('/best/', 'best-fine-hair', r'best .*fine hair|fine hair.*best|best hair dryer thin hair'),
    ('/best/', 'best-thick-hair', r'best .*thick hair|thick hair.*best|best hair dryer coarse'),
    ('/best/', 'best-frizzy-hair', r'best .*frizz|frizz.*best|best hair dryer frizzy'),
    ('/best/', 'best-travel', r'best .*travel|travel.*best|best portable hair dryer|best compact hair dryer'),
    ('/best/', 'best-quiet', r'best .*quiet|quiet.*best|best silent hair dryer|best low noise'),
    ('/best/', 'best-diffuser', r'best .*diffus|diffuser.*best|best hair dryer with diffuser'),
    ('/best/', 'best-professional', r'best .*professional|professional.*best|best salon hair dryer'),
    ('/compare/', 'laifen-vs-dyson', r'laifen vs dyson|dyson vs laifen|laifen or dyson|laifen compared to dyson'),
    ('/compare/', 'shark-vs-dyson', r'shark vs dyson|dyson vs shark|shark or dyson'),
    ('/compare/', 'laifen-vs-shark', r'laifen vs shark|shark vs laifen|shark hair dryer vs laifen'),
    ('/compare/', 'laifen-swift-vs-se', r'laifen swift vs|laifen se vs|laifen swift se|swift vs se|laifen swift special'),
    ('/compare/', 'shark-flexstyle-vs-speedstyle', r'flexstyle vs speedstyle|speedstyle vs flexstyle|flex style vs speed style'),
    ('/compare/', 'laifen-vs-slopehill', r'laifen vs slopehill|slopehill vs laifen'),
    ('/compare/', 'dyson-vs-airwrap-dupes', r'airwrap vs|vs airwrap|airwrap dupe|airwrap alternative'),
    ('/reviews/', 'laifen', r'\blaifen\b'),
    ('/reviews/', 'laifen-air', r'laifen air'),
    ('/reviews/', 'laifen-se-lite', r'laifen se lite'),
    ('/reviews/', 'laifen-se2', r'laifen se2|\blaifen se\b'),
    ('/reviews/', 'laifen-swift', r'laifen swift'),
    ('/reviews/', 'shark-flexstyle', r'shark flexstyle|shark flex style'),
    ('/reviews/', 'shark-speedstyle', r'shark speedstyle|shark speed style'),
    ('/reviews/', 'dreame', r'\bdreame\b'),
    ('/reviews/', 'slopehill', r'\bslopehill\b'),
    ('/for/', 'hair-dryer-for-curly-hair', r'for curly hair|curly hair dryer|curly hair blow dryer'),
    ('/for/', 'hair-dryer-for-fine-hair', r'for fine hair|fine hair dryer|for thin hair|thin hair dryer'),
    ('/for/', 'hair-dryer-for-thick-hair', r'for thick hair|thick hair dryer|for coarse hair'),
    ('/for/', 'hair-dryer-for-frizzy-hair', r'for frizzy hair|frizzy hair dryer|anti frizz hair dryer'),
    ('/for/', 'travel-hair-dryer', r'travel hair dryer|portable hair dryer|compact hair dryer|dual voltage hair dryer'),
    ('/for/', 'quiet-hair-dryer', r'quiet hair dryer|silent hair dryer|low noise hair dryer'),
    ('/for/', 'lightweight-hair-dryer', r'lightweight hair dryer|light weight hair dryer'),
    ('/for/', 'hair-dryer-with-diffuser', r'with diffuser|hair diffuser|diffuser hair dryer'),
    ('/learn/', 'ionic-vs-ceramic', r'ionic vs ceramic|ionic or ceramic|what is ionic hair dryer|ionic hair dryer'),
    ('/learn/', 'how-many-watts', r'how many watts|watt hair dryer|1800w|1875w|2000w hair dryer'),
    ('/learn/', 'how-to-use-diffuser', r'how to use diffuser|how to diffuse|diffuser for wavy'),
    ('/learn/', 'is-dyson-worth-it', r'dyson worth it|is dyson worth|worth the money'),
    ('/learn/', 'high-speed-dryer', r'high speed hair dryer|high-speed|fastest hair dryer|fast drying'),
    ('/ca/', 'where-to-buy-laifen-canada', r'laifen canada|laifen hair dryer canada|buy laifen|laifen costco|laifen walmart|laifen amazon'),
    ('/ca/', 'best-hair-dryer-costco-canada', r'costco hair dryer|hair dryer costco|costco laifen'),
    ('/ca/', 'hair-dryer-sale-canada', r'hair dryer sale|hair dryer deal|hair dryer discount|black friday hair dryer'),
]
PRIORITY = dict(zip([p[1] for p in PAGES], SITEMAP['优先级(T1最高)']))
TITLE = dict(zip(SITEMAP['URL'].str.strip('/'), SITEMAP['页面标题']))

# ---------- styles ----------
H_FILL = PatternFill('solid', fgColor='1F3864')
H_FONT = Font(color='FFFFFF', bold=True, size=10)
THIN = Side(style='thin', color='BFBFBF')
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
WRAP = Alignment(wrap_text=True, vertical='top')

wb = Workbook(); wb.remove(wb.active)

def add_sheet(name, df, widths, fmts=None, cscale=None):
    ws = wb.create_sheet(name[:31])
    ws.append(list(df.columns))
    for c in range(1, len(df.columns) + 1):
        cell = ws.cell(1, c); cell.fill = H_FILL; cell.font = H_FONT
        cell.alignment = Alignment(wrap_text=True, vertical='center', horizontal='center')
        cell.border = BORDER
    for _, r in df.iterrows():
        ws.append(['' if (isinstance(v, float) and pd.isna(v)) else v for v in r.tolist()])
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    if fmts:
        for col, f in fmts.items():
            for row in range(2, ws.max_row + 1):
                ws.cell(row, col).number_format = f
    ws.freeze_panes = 'A2'
    ws.auto_filter.ref = ws.dimensions
    if cscale:
        for col in cscale:
            L = get_column_letter(col)
            ws.conditional_formatting.add(f'{L}2:{L}{ws.max_row}',
                ColorScaleRule(start_type='min', start_color='F8696B',
                               mid_type='percentile', mid_value=50, mid_color='FFEB84',
                               end_type='max', end_color='63BE7B'))
    return ws

# ---------- sheet 1: sitemap ----------
sm = SITEMAP.copy()
sm['优先级'] = 'T' + sm['优先级(T1最高)'].astype(str)
sm = sm[['优先级', 'Silo', 'URL', '页面标题', '意图', '月搜索量合计', '匹配关键词数',
         'KD中位', 'top1关键词', 'top1月搜索量', '头部关键词']]
sm = sm.rename(columns={'意图': '页面意图', '月搜索量合计': '月搜索量', '匹配关键词数': '关键词数',
                        'KD中位': '中位KD', 'top1关键词': '首要关键词', 'top1月搜索量': '首要词搜索量'})
sm = sm.sort_values(['优先级', 'Silo'])
ws1 = add_sheet('01_站点地图', sm,
                [7, 11, 34, 42, 13, 10, 9, 8, 30, 12, 60],
                fmts={6: '#,##0', 7: '#,##0', 8: '0', 10: '#,##0'}, cscale=[6])

# ---------- sheet 2: per-page keyword detail ----------
rows = []
for silo, slug, pat in PAGES:
    m = pool[pool['kw'].str.contains(pat, regex=True, na=False)].copy()
    m = m.sort_values(['Volume', 'Opportunity'], ascending=False)
    for _, r in m.head(20).iterrows():
        rows.append({'Silo': silo, '页面URL': f'/{slug}/', '页面标题': TITLE[slug],
                     '优先级': 'T' + str(PRIORITY[slug]), '关键词': r['Keyword'],
                     '月搜索量': int(r['Volume']), 'KD': r['KD'],
                     'CPC(USD)': r['CPC'], '意图': r['Intent'],
                     '机会评分': r['Opportunity']})
DET = pd.DataFrame(rows)
ws2 = add_sheet('02_页面关键词明细', DET,
                [10, 30, 40, 8, 34, 10, 7, 10, 24, 10],
                fmts={6: '#,##0', 7: '0', 8: '$#,##0.00', 10: '0.0'}, cscale=[6, 10])

# ---------- sheet 3: 90-day roadmap ----------
R = [
    ('W1-2', 'Phase 0 · 基建', '域名/托管/技术栈/GA4+GSC/品牌定位/Affiliate账号就绪(Levanta各品牌过审)', '站点可访问、GSC验证、schema基线', '0'),
    ('W3-4', 'Phase 1 · T1上线', '6个T1页面: /best-hair-dryer/ /best-dyson-alternatives/ /best-hair-dryer-canada/ /laifen-vs-dyson/ /shark-vs-dyson/ /laifen/', '6页已索引、含首测数据与对比表', '6'),
    ('M2', 'Phase 1 · 对比组', '补齐/compare/空白位: laifen-vs-shark / laifen-swift-vs-se / shark-flexstyle-vs-speedstyle / dyson-vs-airwrap-dupes', '12页上线、内链完成第一层', '12'),
    ('M2', 'Phase 2 · 评测组', 'Laifen各型号评测: air / se-lite / se2 / swift + shark flexstyle/speedstyle', '评测页含实测数据(风速/噪音/干发时间)', '20'),
    ('M3', 'Phase 3 · 需求组', '/for/ 8页(卷发/细软/粗硬/毛躁/旅行/静音/轻量/风嘴) + /learn/ 5页', '30页上线、站内主题集群成型', '35'),
    ('M3', 'Phase 3 · 本地化', '/ca/ 3页(Laifen加拿大购买渠道/Costco/促销)', '加拿大本地定价与渠道表', '38'),
    ('M4-6', 'Phase 4 · 权威与链接', '数字公关数据研究(加拿大吹风机实测报告)+HARO+美妆博客外联+Reddit/论坛存在感', '前20条外链、引用域>15', '43'),
    ('M6', 'Phase 4 · 转化校准', '用Amazon Associates后台实测: 出站点击率/成交率/单笔佣金, 回代模型', '收入模型从情景→实测', '43'),
    ('M7-12', 'Phase 5 · 规模化+法语', '长尾词扩张(每周2-3篇)+魁北克法语版/fr/ + 节假日促销页', '80-120页、月访>3000、月佣收入C$500+', '100+'),
]
RD = pd.DataFrame(R, columns=['时间', '阶段', '关键动作', '里程碑/交付物', '累计页面数'])
ws3 = add_sheet('03_90天执行计划', RD, [10, 22, 70, 42, 12])

wb.save('deliverables/SEO策略-内容计划.xlsx')
print('saved: deliverables/SEO策略-内容计划.xlsx')
print('sheets:', wb.sheetnames)
print(f'页面数: {len(SITEMAP)}, 覆盖月搜索量: {SITEMAP["月搜索量合计"].sum():,}')
print(f'页面-关键词映射明细: {len(DET)} 行')
