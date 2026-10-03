import io, zipfile, re
import pandas as pd, numpy as np

BSR = r"C:\Users\Mloong\Downloads\BSR(Hair-Dryers(Current))-50-CA-20261002.xlsx"
z = zipfile.ZipFile(BSR)
S = [''.join(re.findall(r'<t[^>]*>(.*?)</t>', s, re.S)).replace('&amp;', '&').replace('&apos;', "'")
     for s in re.findall(r'<si>(.*?)</si>', z.read('xl/sharedStrings.xml').decode('utf-8'), re.S)]
df = pd.read_excel(BSR, sheet_name='CA', header=0); df.columns = S[:71]
for c in ['月销量', '月销售额(C$)', '价格(C$)']:
    df[c] = pd.to_numeric(df[c], errors='coerce')

# ---- brand aggregate (各品牌全部 ASIN 汇总)
bg = df.groupby('品牌').agg(ASIN数=('ASIN', 'size'), 月销量=('月销量', 'sum'),
                            月销售额=('月销售额(C$)', 'sum')).reset_index()
bg['加权均价'] = (bg['月销售额'] / bg['月销量']).round(2)

# ---- 用户确认的佣金率
RATE = {'Laifen': 0.15, 'slopehill': 0.20, 'dreame': 0.10}
DEFAULT = 0.04
bg['佣金率'] = bg['品牌'].map(RATE).fillna(DEFAULT)
bg['单笔佣金'] = (bg['加权均价'] * bg['佣金率']).round(2)
bg['月佣金池'] = (bg['月销售额'] * bg['佣金率']).round(0)
bg = bg.sort_values('月佣金池', ascending=False)

out = []
def P(*a): out.append(' '.join(str(x) for x in a))

P("=" * 108)
P("各品牌佣金池排名 (Amazon.ca 吹风机类目 Top50)")
P("=" * 108)
P(f"{'品牌':<18}{'ASIN':>5}{'月销量':>9}{'月销售额':>13}{'加权均价':>10}{'佣金率':>8}{'单笔佣金':>10}{'月佣金池':>13}")
P("-" * 108)
for _, r in bg.iterrows():
    tag = '  ★自定义' if r['品牌'] in RATE else ''
    P(f"{r['品牌']:<18}{r['ASIN数']:>5.0f}{r['月销量']:>9,.0f}{r['月销售额']:>13,.0f}"
      f"{r['加权均价']:>10.2f}{r['佣金率']:>8.0%}{r['单笔佣金']:>10.2f}{r['月佣金池']:>13,.0f}{tag}")
P("-" * 108)
P(f"{'合计':<18}{bg['ASIN数'].sum():>5.0f}{bg['月销量'].sum():>9,.0f}"
  f"{bg['月销售额'].sum():>13,.0f}{'':>10}{'':>8}{'':>10}{bg['月佣金池'].sum():>13,.0f}")

P("\n" + "=" * 108)
P("★ 三个自定义佣金品牌的直接对比")
P("=" * 108)
three = bg[bg['品牌'].isin(RATE)].copy()
three['占佣金池%'] = (100 * three['月佣金池'] / bg['月佣金池'].sum()).round(1)
P(three[['品牌', 'ASIN数', '月销量', '月销售额', '加权均价', '佣金率', '单笔佣金',
         '月佣金池', '占佣金池%']].to_string(index=False))
P(f"\n三品牌佣金池合计: C${three['月佣金池'].sum():,.0f}/月  "
  f"= 类目Top50总佣金池的 {100*three['月佣金池'].sum()/bg['月佣金池'].sum():.1f}%")

P("\n" + "=" * 108)
P("单笔佣金 vs 走量能力 —— 两种不同的生意")
P("=" * 108)
for _, r in three.iterrows():
    P(f"  {r['品牌']:<12} 单笔 C${r['单笔佣金']:>6.2f}   月销量 {r['月销量']:>7,.0f} 台   "
      f"月销售额 C${r['月销售额']:>10,.0f}   佣金池 C${r['月佣金池']:>9,.0f}")
P("")
P("  读法：Laifen 单笔最值钱(C$18.47)，但 slopehill 走量是 Laifen 的 5.1 倍，")
P("        两者佣金池分别是 C$36,393 与 C$149,420 —— slopehill 的池子是 Laifen 的 4.1 倍。")
P("        → 只做 Laifen = 放弃 80% 的可赚佣金。必须以 Laifen 为高端锚点，slopehill 为走量引擎。")

# ---- per-session value by product mix
P("\n" + "=" * 108)
P("不同内容策略下的「单笔加权佣金」")
P("=" * 108)
L, SL, DR = 18.47, 14.86, 12.00
mixes = {
    '只推 Laifen (当前方案)':        (1.00, 0.00, 0.00),
    'Laifen 高端为主':               (0.60, 0.35, 0.05),
    '高端+走量均衡 (推荐)':           (0.35, 0.55, 0.10),
    '走量为主 slopehill':            (0.15, 0.75, 0.10),
    '只推 slopehill':                (0.00, 1.00, 0.00),
}
rows = []
for name, (a, b, c) in mixes.items():
    w = a * L + b * SL + c * DR
    rows.append({'内容策略': name, 'Laifen占比': f'{a:.0%}', 'slopehill占比': f'{b:.0%}',
                 'dreame占比': f'{c:.0%}', '加权单笔佣金(C$)': round(w, 2),
                 '相对纯Laifen': f'{w/L:.0%}'})
mx = pd.DataFrame(rows)
P(mx.to_string(index=False))

P("\n" + "=" * 108)
P("修正收入模型 —— 采用「高端+走量均衡」加权佣金 C$%.2f" %
  (0.35 * L + 0.55 * SL + 0.10 * DR))
P("=" * 108)
W = 0.35 * L + 0.55 * SL + 0.10 * DR
SESS = {'悲观(第1年)': 1433, '基准(第1-2年)': 4503, '乐观(第2-3年)': 8734}
rows = []
for sname, s in SESS.items():
    for cr in [0.10, 0.15, 0.18, 0.25]:
        for cv in [0.03, 0.05, 0.08, 0.10]:
            rev = s * cr * cv * W
            rows.append({'情景': sname, '月访问': s, '出站点击率': f'{cr:.0%}',
                         '成交率': f'{cv:.0%}', '月收入(C$)': round(rev),
                         '每访问(C$)': round(rev / s, 3)})
R = pd.DataFrame(rows)
P("--- 基准情景(4,503访问) 各转化组合 ---")
P(R[R['情景'] == '基准(第1-2年)'].pivot_table(
    index='成交率', columns='出站点击率', values='月收入(C$)').to_string())
P("\n--- 达成收入目标所需月访问量 (18%出站, 8%成交) ---")
for t in [500, 1000, 2000, 3000, 5000]:
    P(f"  C${t:>5,}/月  →  {t/(0.18*0.08*W):>8,.0f} 访问/月")
P(f"\n  对比：纯Laifen需 {1000/(0.18*0.08*L):,.0f} 访问  →  均衡组合需 {1000/(0.18*0.08*W):,.0f} 访问  "
  f"(省 {1000/(0.18*0.08*W) - 1000/(0.18*0.08*L):,.0f})")

with io.open('analysis/_brandmix.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
bg.to_pickle('analysis/brand_commission.pkl')
mx.to_pickle('analysis/mix.pkl')
print("written analysis/_brandmix.txt")
