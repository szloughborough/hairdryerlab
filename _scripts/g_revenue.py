"""
Realistic monetization model for a CA Laifen/hair-dryer affiliate site.
Runs 3 ranking scenarios x 3 monetization stacks.
"""
import pandas as pd, numpy as np

pd.set_option('display.width', 300)
pd.set_option('display.max_columns', 40)

port = pd.read_pickle('analysis/ontopic.pkl')
port = port[(port['Volume'] >= 50) & (port['KD_eff'] <= 45)].copy()
VOL = port['Volume'].sum()
RET = port['click_retention'].mean()
print(f"rankable portfolio: {len(port):,} kws, {VOL:,.0f} monthly searches, "
      f"avg click retention {RET:.2f}")

# ---- ranking scenarios: share of portfolio volume where we sit top-30 & blended CTR
SCEN = {
    'Pessimistic (yr1, new domain)': {'share': 0.35, 'ctr': 0.030},
    'Base (yr1-2)':                  {'share': 0.60, 'ctr': 0.055},
    'Optimistic (yr2-3, strong links)': {'share': 0.80, 'ctr': 0.080},
}

# ---- monetization stacks
def stack(name, affiliate_click=0.18, conv=0.025, aov=200.0, comm=0.06,
          rpm=0.0, sponsored_mo=0.0):
    return dict(name=name, aff_click=affiliate_click, conv=conv, aov=aov,
                comm=comm, rpm=rpm, sponsored_mo=sponsored_mo)

STACKS = [
    stack('A. Amazon Associates only', comm=0.03, aov=170.0, conv=0.045, rpm=0),
    stack('B. Amazon + direct Laifen program', comm=0.06, aov=200.0, conv=0.025, rpm=0),
    stack('C. B + display/affiliate-network ads', comm=0.06, aov=200.0, conv=0.025, rpm=12.0),
    stack('D. C + sponsored placements/brand deals', comm=0.06, aov=200.0, conv=0.025,
          rpm=12.0, sponsored_mo=1500.0),
    stack('E. D + high-RPM premium ad network', comm=0.06, aov=200.0, conv=0.025,
          rpm=22.0, sponsored_mo=1500.0),
]

rows = []
for sname, s in SCEN.items():
    sessions = VOL * s['share'] * s['ctr'] * RET
    for st in STACKS:
        aff_clicks = sessions * st['aff_click']
        sales = aff_clicks * st['conv']
        aff_rev = sales * st['aov'] * st['comm']
        ad_rev = sessions / 1000 * st['rpm']
        total = aff_rev + ad_rev + st['sponsored_mo']
        rows.append({
            'scenario': sname,
            'monetization': st['name'],
            'sessions/mo': round(sessions),
            'sessions/yr': round(sessions * 12),
            'affiliate_rev/mo': round(aff_rev),
            'ads_rev/mo': round(ad_rev),
            'sponsored_rev/mo': round(st['sponsored_mo']),
            'total_rev/mo_CAD': round(total),
            'total_rev/yr_CAD': round(total * 12),
            'rev_per_session_CAD': round(total / sessions, 3) if sessions else 0,
        })

R = pd.DataFrame(rows)
print("\n" + "=" * 120)
print("REALISTIC MONETIZATION MATRIX (CAD)")
print("=" * 120)
print(R.to_string(index=False))

print("\n" + "=" * 120)
print("KEY READ: revenue per session")
print("=" * 120)
piv = R.pivot_table(index='monetization', columns='scenario', values='rev_per_session_CAD')
print(piv.to_string())
print("\nTypical CA affiliate-site benchmark: $0.04-$0.10/session for thin Amazon-only,")
print("$0.15-$0.45/session for a well-built niche site with ads + direct programs.")
print("\n--> Amazon-only on a $200 AOV at 3% = ~$0.05/session. This is the structural problem.")

R.to_pickle('analysis/revenue_model.pkl')
print("\nsaved analysis/revenue_model.pkl")

# ---- traffic needed to hit income targets, under stack C and E
print("\n" + "=" * 120)
print("INVERSE: monthly sessions needed to reach income targets")
print("=" * 120)
for target in [1000, 3000, 5000, 10000]:
    line = [f"CAD {target:>6,}/mo ->"]
    for st in STACKS:
        rps = None
        for sname, s in SCEN.items():
            sessions = VOL * s['share'] * s['ctr'] * RET
            aff = sessions * st['aff_click'] * st['conv'] * st['aov'] * st['comm']
            ads = sessions / 1000 * st['rpm']
            rps = (aff + ads + st['sponsored_mo']) / sessions
            break
        # solve sessions for target with sponsored fixed
        fixed = st['sponsored_mo']
        var = rps - (fixed / (VOL * SCEN['Base (yr1-2)']['share'] * SCEN['Base (yr1-2)']['ctr'] * RET))
        need = (target - fixed) / var if var > 0 else float('inf')
        line.append(f"{st['name'][:2]}={need:>8,.0f}")
    print("  ".join(line))
print("(sessions/mo; A=Amazon only, B=+direct, C=+ads, D=+sponsored, E=+premium ads)")
