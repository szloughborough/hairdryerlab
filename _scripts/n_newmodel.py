import io
import pandas as pd, numpy as np

pd.set_option('display.width', 300); pd.set_option('display.max_columns', 40)
out = []
def P(*a): out.append(' '.join(str(x) for x in a))

# ---------- real Laifen economics from BSR ----------
LAIFEN = pd.DataFrame([
    ('B0FKBFZNHK', 'SE Lite',            448, 109.99, 4.5,  22, 408),
    ('B0GWHGTBDY', 'Air Diffuser',       377,  99.99, 4.6,  85, 122),
    ('B0FPMBBG2J', 'SE2',                319, 143.98, 4.5,  14, 348),
    ('B0GWHF4SHD', 'Air',                534,  99.99, 4.5,  36, 126),
    ('B0D141Q8ZF', 'Swift (gen1)',       113, 149.98, 4.1,   0, 703),
    ('B0D13MYLJC', 'Swift + Diffuser',   179, 219.99, 4.5,   4, 905),
], columns=['ASIN','型号','月销量','价格','评分','月新增评分','上架天数'])

LAIFEN['月销售额'] = LAIFEN['月销量'] * LAIFEN['价格']
tot_u = LAIFEN['月销量'].sum(); tot_r = LAIFEN['月销售额'].sum()
aov = tot_r / tot_u
P("=" * 100)
P("LAIFEN 真实产品与单笔佣金价值 (Amazon.ca, SellerSprite 2026-10-02)")
P("=" * 100)
LAIFEN['单笔佣金@15%'] = (LAIFEN['价格'] * 0.15).round(2)
LAIFEN['月佣金池'] = (LAIFEN['月销售额'] * 0.15).round(0)
P(LAIFEN.to_string(index=False))
P(f"\nLaifen 合计: 月销量 {tot_u:,.0f} 台 | 月销售额 C${tot_r:,.0f} | 实际客单价 AOV = C${aov:.2f}")
P(f"→ Laifen 单笔 15% 佣金 = C${aov*0.15:.2f}")
P(f"→ Laifen 全系月佣金池 = C${tot_r*0.15:,.0f}/月")

P("\n" + "=" * 100)
P("★ 核心洞察：为什么必须主推 Laifen 而不是其他品牌")
P("=" * 100)
OTHER_AOV_MEDIAN = 49.39      # 类目中位价
P(f"类目中位价           : C${OTHER_AOV_MEDIAN:.2f}")
P(f"Laifen 实际客单价     : C${aov:.2f}   ({aov/OTHER_AOV_MEDIAN:.1f}倍)")
P(f"")
P(f"其他品牌单笔佣金 @4%  : C${OTHER_AOV_MEDIAN*0.04:.2f}")
P(f"Laifen   单笔佣金 @15%: C${aov*0.15:.2f}   ({(aov*0.15)/(OTHER_AOV_MEDIAN*0.04):.1f}倍)")
P(f"")
P("→ 卖一台 Laifen = 卖 {:.0f} 台普通吹风机（佣金口径）".format((aov*0.15)/(OTHER_AOV_MEDIAN*0.04)))
P("→ 15%佣金 + C$137客单价，把 Laifen 从'低价值联盟品'变成'高价值联盟品'")

# ---------- market structure ----------
P("\n" + "=" * 100)
P("Amazon.ca 吹风机类目结构 (Top50 BSR)")
P("=" * 100)
P(f"类目 Top50 月销量: 33,507 台 | 月销售额: C$1,809,118")
P(f"Laifen 月销量: {tot_u:,.0f} 台 = 类目Top50的 {100*tot_u/33507:.1f}%")
P(f"Laifen 月销售额: C${tot_r:,.0f} = 类目Top50的 {100*tot_r/1809118:.1f}%")
P(f"→ Laifen 用 5.9% 的销量拿到 13.4% 的销售额（高价定位成立）")

# ---------- corrected revenue model ----------
P("\n" + "=" * 100)
P("修正后的收入模型 —— 用真实客单价与真实佣金率")
P("=" * 100)
P("已替换的假设：AOV C$200(假设) → C$%.2f(实测)；佣金 6%%(假设) → 15%%(实测)" % aov)

# session estimates from Semrush model (base case)
SESS = {'悲观(第1年)': 1433, '基准(第1-2年)': 4503, '乐观(第2-3年)': 8734}
CLICK_RATES = [0.10, 0.15, 0.18, 0.25]   # outbound click rate
CONV = [0.03, 0.05, 0.08, 0.10]          # outbound click -> sale

P("\n--- A. 联盟收入 (只算 Laifen 15%%) ---")
rows = []
for sname, s in SESS.items():
    for cr in CLICK_RATES:
        for cv in CONV:
            rev = s * cr * cv * aov * 0.15
            rows.append({'情景': sname, '月访问': s, '出站点击率': cr, '成交率': cv,
                         '单笔佣金': round(aov*0.15, 2), '月收入': round(rev)})
A = pd.DataFrame(rows)
piv = A.pivot_table(index=['出站点击率', '成交率'], columns='情景', values='月收入')
P(piv.to_string())

P("\n--- B. 混入其他品牌(4%%佣金)后的加权收益 ---")
P("假设 60%% 出站点击去 Laifen(15%%), 40%% 去其他品牌(4%%, 客单价C$49)")
blend_cpc = 0.60 * aov * 0.15 + 0.40 * OTHER_AOV_MEDIAN * 0.04
P(f"加权单笔佣金 = C${blend_cpc:.2f}    (纯Laifen C${aov*0.15:.2f})")
for sname, s in SESS.items():
    for cv in [0.05, 0.08, 0.10]:
        rev = s * 0.18 * cv * blend_cpc
        P(f"  {sname:<14} 月访问{s:>6,}  成交率{cv:.0%}  →  C${rev:>8,.0f}/月  (C${rev/s:.3f}/访问)")

P("\n--- C. 达成收入目标所需月访问量 (18%%出站点击, 8%%成交) ---")
for target in [500, 1000, 2000, 3000, 5000]:
    need_pure = target / (0.18 * 0.08 * aov * 0.15)
    need_blend = target / (0.18 * 0.08 * blend_cpc)
    P(f"  C${target:>5,}/月  →  纯Laifen需 {need_pure:>8,.0f} 访问/月  |  混合需 {need_blend:>8,.0f} 访问/月")

P("\n--- D. 对比：修正前 vs 修正后 ---")
old_rps = 0.054
new_rps = 0.18 * 0.08 * aov * 0.15
P(f"  修正前每访问收入: C${old_rps:.3f}  (AOV200 x 6%%)")
P(f"  修正后每访问收入: C${new_rps:.3f}  (AOV{aov:.0f} x 15%%, 8%%成交)  → 提升 {new_rps/old_rps:.1f}倍")
P(f"  基准情景(4,503访问)月收入: C${4503*old_rps:,.0f}  →  C${4503*new_rps:,.0f}")

with io.open('analysis/_newmodel.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print("written analysis/_newmodel.txt")

A.to_pickle('analysis/model_a.pkl')
LAIFEN.to_pickle('analysis/laifen_asin.pkl')
