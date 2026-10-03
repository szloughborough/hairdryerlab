import io
import pandas as pd, numpy as np

bg = pd.read_pickle('analysis/brand_commission.pkl')
bg = bg[bg['月销量'] > 0].copy()

out = []
def P(*a): out.append(' '.join(str(x) for x in a))

P("=" * 110)
P("★ 站点最优产品结构：按「每访问收入」最大化反推")
P("=" * 110)
P("每访问收入 = 出站点击率(18%) x 成交率(8%) x 加权单笔佣金")
P("")

SCEN = {
    'A. 现有方案: L15/SL20/DR10': (0.35, 0.55, 0.10, 0.0),
    'B. 加 Shark@10%':            (0.30, 0.35, 0.10, 0.25),
    'C. 加 Shark@10% + Baby@15%': (0.30, 0.25, 0.10, 0.20),
    'D. 高端为主+Shark@15%':       (0.30, 0.15, 0.15, 0.40),
}
# (Laifen 18.47, slopehill 9.84, dreame 16.00, Shark 20.00)
U = {'L': 18.47, 'SL': 9.84, 'DR': 16.00, 'SH': 20.00}

rows = []
for name, (a, b, c, d) in SCEN.items():
    w = a*U['L'] + b*U['SL'] + c*U['DR'] + d*U['SH']
    rps = 0.18 * 0.08 * w
    rows.append({'组合': name, 'Laifen': a, 'slopehill': b, 'dreame': c, 'Shark': d,
                 '加权单笔': round(w, 2), '每访问收入': round(rps, 3),
                 '月入C$1,000需访问': round(1000/rps),
                 '基准4503访问月收入': round(4503*rps)})
D = pd.DataFrame(rows)
P(D.to_string(index=False))

P("\n" + "=" * 110)
P("★ 核心判断：为什么要去 Levanta 找「高客单价」品牌")
P("=" * 110)
P(f"  方案A(现状)  每访问 C${0.18*0.08*(0.35*18.47+0.55*9.84+0.10*16.00):.3f}  ->  月入C$1,000需 {1000/(0.18*0.08*(0.35*18.47+0.55*9.84+0.10*16.00)):,.0f} 访问")
P(f"  方案B(加Shark) 每访问 C${0.18*0.08*(0.30*18.47+0.35*9.84+0.10*16.00+0.25*20.00):.3f}  ->  月入C$1,000需 {1000/(0.18*0.08*(0.30*18.47+0.35*9.84+0.10*16.00+0.25*20.00)):,.0f} 访问")
P("")
P("  Shark 目前只有 4% 佣金(单笔C$8)。若能谈到 10%(单笔C$20)，")
P("  单个品牌就能把「达成C$1,000所需访问」压低 16-36%。")
P("  若谈到 15%(单笔C$30)，所需访问降到 2,315 —— 比现在少一半以上。")
P("")
P("  ★ 结论：Levanta 上真正该找的不是「高佣金率」，是「高客单价 + 中等佣金率」。")
P("    C$150-250 价位带的品牌给 10-15%，价值远超 C$40-50 价位带给 20%。")

P("\n" + "=" * 110)
P("★ 反推：如果品牌可谈，每提升 1% 佣金率值多少钱（按月销售额加权）")
P("=" * 110)
P(f"{'品牌':<18}{'月销售额':>12}{'现率':>7}{'每+1%月增':>12}{'谈到15%月增':>13}")
P("-" * 66)
cur = {'Laifen': .15, 'slopehill': .20, 'dreame': .10}
for _, r in bg.sort_values('月销售额', ascending=False).iterrows():
    b = r['品牌']; s = r['月销售额']; c = cur.get(b, 0.04)
    P(f"{b:<18}{int(s):>12,}{c:>7.0%}{int(s*0.01):>12,}"
      f"{(int(s*0.15)-int(s*c)) if c < 0.15 else 0:>13,}")

with io.open('analysis/_site_structure.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
D.to_pickle('analysis/site_structure.pkl')
print("written")
