"""Add Levanta commission-research target sheets (21, 22)."""
import io
import pandas as pd, numpy as np
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.formatting.rule import ColorScaleRule

WB = 'deliverables/Laifen-Canada-关键词与可行性分析.xlsx'
WBF = load_workbook(WB)
for s in ['21_单笔佣金矩阵', '22_Levanta调研清单']:
    if s in WBF.sheetnames:
        del WBF[s]

H_FILL = PatternFill('solid', fgColor='1F3864')
H_FONT = Font(color='FFFFFF', bold=True, size=10)
THIN = Side(style='thin', color='BFBFBF')
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


def add(name, d, widths, fmts=None, cscale=None):
    ws = WBF.create_sheet(name[:31])
    ws.append(list(d.columns))
    for c in range(1, len(d.columns) + 1):
        cell = ws.cell(1, c); cell.fill = H_FILL; cell.font = H_FONT
        cell.alignment = Alignment(wrap_text=True, vertical='center', horizontal='center')
        cell.border = BORDER
    for _, r in d.iterrows():
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
            Lc = get_column_letter(col)
            ws.conditional_formatting.add(f'{Lc}2:{Lc}{ws.max_row}',
                ColorScaleRule(start_type='min', start_color='F8696B',
                               mid_type='percentile', mid_value=50, mid_color='FFEB84',
                               end_type='max', end_color='63BE7B'))
    return ws


# ---------------- 21: per-sale commission matrix ----------------
bg = pd.read_pickle('analysis/brand_commission.pkl')
bg = bg[bg['月销量'] > 0].copy()
CUR = {'Laifen': 0.15, 'slopehill': 0.20, 'dreame': 0.10}
rows = []
for _, r in bg.iterrows():
    pr = r['加权均价']
    rows.append({
        '品牌': r['品牌'], '加权均价(C$)': round(pr, 2), '月销量': int(r['月销量']),
        '月销售额(C$)': int(r['月销售额']),
        '当前佣金率': CUR.get(r['品牌'], 0.04),
        '单笔@当前': round(pr * CUR.get(r['品牌'], 0.04), 2),
        '单笔@4%': round(pr * .04, 2), '单笔@8%': round(pr * .08, 2),
        '单笔@10%': round(pr * .10, 2), '单笔@15%': round(pr * .15, 2),
        '单笔@20%': round(pr * .20, 2),
        '每+1%佣金月增(C$)': int(r['月销售额'] * 0.01),
    })
M = pd.DataFrame(rows).sort_values('加权均价(C$)', ascending=False)
ws21 = add('21_单笔佣金矩阵', M,
           [18, 13, 10, 14, 11, 12, 10, 10, 10, 10, 10, 17],
           fmts={2: '$#,##0.00', 3: '#,##0', 4: '#,##0', 5: '0%', 6: '$#,##0.00',
                 7: '$#,##0.00', 8: '$#,##0.00', 9: '$#,##0.00', 10: '$#,##0.00',
                 11: '$#,##0.00', 12: '#,##0'},
           cscale=[11])
r0 = ws21.max_row + 3
ws21.cell(r0, 1, '★ 核心结论：真正的杠杆是客单价，不是佣金率').font = Font(bold=True, size=11, color='C00000')
for i, t in enumerate([
    'slopehill @20% = 单笔 C$9.84（你目前佣金率最高的产品）',
    'Shark @10% = 单笔 C$20.00 —— 只要 10%，单笔就翻倍',
    'dreame @10% = 单笔 C$16.00 —— 已拿到，比 slopehill 高 63%',
    '与其纠结 slopehill 从 20% 提到 25%（+C$2.5/笔），不如找一个 C$150-250 价位带给 10-15% 的品牌',
    '去 Levanta 的目标：高客单价 + 中等佣金率，而不是高佣金率',
], 1):
    ws21.cell(r0 + i, 1, f'{i}. {t}')

# ---------------- 22: Levanta research list ----------------
T = pd.DataFrame([
    ('P0', 'Shark', 199.99, 288, 0.04, 0.10, '高均价且有量；单笔最优的现实选择。谈 10% 单笔即 C$20'),
    ('P0', 'BabylissPro', 89.89, 690, 0.04, 0.15, '专业线品牌，通常愿给内容站较高佣金；4 个 ASIN'),
    ('P0', 'Cosy Companions', 129.99, 339, 0.04, 0.10, '小众高客单，谈判空间大（小品牌更需要内容流量）'),
    ('P0', 'SUPGALIY', 69.99, 707, 0.04, 0.15, '评分 4.7 为全类目最高，客单价中高'),
    ('P1', 'dreame', 159.99, 163, 0.10, 0.20, '已拿到 10%；翻到 20% 单笔 C$32，将成全场最高之一'),
    ('P1', 'wavytalk', 42.32, 3092, 0.04, 0.15, '与 slopehill 同价位带，谈判可能性较高'),
    ('P1', 'Conair', 37.00, 5982, 0.04, 0.10, '大品牌谈判难，但月销售额 C$221k；10% 即增 C$13k/月池'),
    ('P2', 'Laifen', 123.16, 1970, 0.15, 0.20, '同品牌谈升级比谈新品牌容易；每升 5% 约增 C$12k/月池'),
    ('P2', 'Alloom', 79.99, 197, 0.04, 0.15, '客单价中高，小品牌易谈'),
    ('P2', 'MESCOMB', 62.99, 180, 0.04, 0.15, '客单价中等，长尾补充'),
    ('X', 'Dyson', 500.62, 416, 0.04, 0.10, '单笔 C$50 理论最优，但 Dyson 基本不给联盟佣金，不建议花时间'),
    ('X', 'REVLON / Aina', 23.44, 7108, 0.04, 0.20, '均价 C$21-26，即使 20% 单笔仅 C$4-5；当流量词不当收入款'),
], columns=['优先级', '品牌', '加权均价(C$)', '月销量', '当前佣金率', '目标佣金率',
            '调研理由'])
T['目标单笔佣金(C$)'] = (T['加权均价(C$)'] * T['目标佣金率']).round(2)
T['当前单笔佣金(C$)'] = (T['加权均价(C$)'] * T['当前佣金率']).round(2)
T['单笔提升(C$)'] = (T['目标单笔佣金(C$)'] - T['当前单笔佣金(C$)']).round(2)
T['月销售额(C$)'] = [int(bg.loc[bg['品牌'] == b, '月销售额'].sum()) if b in set(bg['品牌'])
                  else int(bg[bg['品牌'].isin(['REVLON', 'Aina'])]['月销售额'].sum())
                  for b in T['品牌']]
T = T[['优先级', '品牌', '加权均价(C$)', '月销量', '月销售额(C$)', '当前佣金率',
       '当前单笔佣金(C$)', '目标佣金率', '目标单笔佣金(C$)', '单笔提升(C$)', '调研理由']]
ws22 = add('22_Levanta调研清单', T,
           [8, 17, 13, 10, 14, 11, 15, 11, 16, 13, 62],
           fmts={3: '$#,##0.00', 4: '#,##0', 5: '#,##0', 6: '0%', 7: '$#,##0.00',
                 8: '0%', 9: '$#,##0.00', 10: '$#,##0.00'},
           cscale=[10])
r0 = ws22.max_row + 3
ws22.cell(r0, 1, '★ 调研清单用法').font = Font(bold=True, size=11, color='C00000')
for i, t in enumerate([
    '在 Levanta 后台逐个品牌搜索，记录：是否入驻、可用佣金率、Cookie 期限、是否支持 Amazon.ca',
    '优先级 P0 的品牌即使只谈到 10%，单笔佣金就能超过现在的 slopehill 20%',
    '注意：Shark 若走 Levanta 但只给 4%，则不值得替换现有策略；关键看是否 >=10%',
    '每提升 1% 佣金率的价值 = 该品牌月销售额 x 1%（可直接对比谈判投入产出）',
    'Dyson 虽单笔最高（@10% = C$50）但极难拿到，建议把时间花在 Shark / BabylissPro / Cosy 上',
], 1):
    ws22.cell(r0 + i, 1, f'{i}. {t}')

WBF.save(WB)
print('added 21, 22. sheets:', len(WBF.sheetnames))
