"""
Build the concrete SEO content plan: site architecture + keyword->page mapping.
Uses the already-scored keyword pool to attach real CA volumes to each page.
"""
import io, re
import pandas as pd, numpy as np

pd.set_option('display.width', 320)

scored = pd.read_pickle('analysis/scored.pkl')
scored['kw'] = scored['Keyword'].astype(str).str.lower().str.strip()
ont = pd.read_pickle('analysis/ontopic.pkl')
ont['kw'] = ont['Keyword'].astype(str).str.lower().str.strip()

# ---- keyword pool: on-topic, has volume, rankable-ish (drop pure navigational brand head)
pool = ont[ont['Volume'] >= 10].copy()

BRAND_RX = r'laifen|dyson|shark|ghd|babyliss|revlon|conair|drybar|zuvi|dreame|slopehill'

# ================================================================
# SITE ARCHITECTURE (strategy decision, data-validated below)
# ================================================================
# Each page: (silo, url_slug, title, primary_intent, priority, kw_pattern)
PAGES = [
    # ---------- Silo 1: /best/  roundup money pages ----------
    ('/best/', 'best-hair-dryer', 'Best Hair Dryers 2026 (Canada)', 'commercial', 1,
     r'\bbest hair dryer|\bbest blow dryer|\bbest hairdryer'),
    ('/best/', 'best-dyson-alternatives', 'Best Dyson Hair Dryer Alternatives & Dupes', 'commercial', 1,
     r'dyson (dupe|alternative|alternatives|similar|like)|dupe hair dryer|hair dryer like dyson|alternatives? to dyson'),
    ('/best/', 'best-hair-dryer-canada', 'Best Hair Dryers in Canada', 'commercial', 1,
     r'best .*canada|canada.*best hair|best hair dryer canada'),
    ('/best/', 'best-curly-hair', 'Best Hair Dryer for Curly Hair', 'commercial', 2,
     r'best .*curly|curly.*best|best hair dryer for curls'),
    ('/best/', 'best-fine-hair', 'Best Hair Dryer for Fine Hair', 'commercial', 2,
     r'best .*fine hair|fine hair.*best|best hair dryer thin hair'),
    ('/best/', 'best-thick-hair', 'Best Hair Dryer for Thick Hair', 'commercial', 2,
     r'best .*thick hair|thick hair.*best|best hair dryer coarse'),
    ('/best/', 'best-frizzy-hair', 'Best Hair Dryer for Frizzy Hair', 'commercial', 2,
     r'best .*frizz|frizz.*best|best hair dryer frizzy'),
    ('/best/', 'best-travel', 'Best Travel Hair Dryer', 'commercial', 2,
     r'best .*travel|travel.*best|best portable hair dryer|best compact hair dryer'),
    ('/best/', 'best-quiet', 'Best Quiet Hair Dryer', 'commercial', 2,
     r'best .*quiet|quiet.*best|best silent hair dryer|best low noise'),
    ('/best/', 'best-diffuser', 'Best Hair Dryer with Diffuser', 'commercial', 2,
     r'best .*diffus|diffuser.*best|best hair dryer with diffuser'),
    ('/best/', 'best-professional', 'Best Professional Hair Dryer', 'commercial', 3,
     r'best .*professional|professional.*best|best salon hair dryer'),
    # ---------- Silo 2: /compare/  comparison pages (whitespace) ----------
    ('/compare/', 'laifen-vs-dyson', 'Laifen vs Dyson Hair Dryer: 2026 Comparison', 'comparison', 1,
     r'laifen vs dyson|dyson vs laifen|laifen or dyson|laifen compared to dyson'),
    ('/compare/', 'shark-vs-dyson', 'Shark vs Dyson Hair Dryer', 'comparison', 1,
     r'shark vs dyson|dyson vs shark|shark or dyson'),
    ('/compare/', 'laifen-vs-shark', 'Laifen vs Shark Hair Dryer', 'comparison', 2,
     r'laifen vs shark|shark vs laifen|shark hair dryer vs laifen'),
    ('/compare/', 'laifen-swift-vs-se', 'Laifen Swift vs SE: Which to Buy', 'comparison', 2,
     r'laifen swift vs|laifen se vs|laifen swift se|swift vs se|laifen swift special'),
    ('/compare/', 'shark-flexstyle-vs-speedstyle', 'Shark FlexStyle vs SpeedStyle', 'comparison', 2,
     r'flexstyle vs speedstyle|speedstyle vs flexstyle|flex style vs speed style'),
    ('/compare/', 'laifen-vs-slopehill', 'Laifen vs Slopehill Hair Dryer', 'comparison', 3,
     r'laifen vs slopehill|slopehill vs laifen'),
    ('/compare/', 'dyson-vs-airwrap-dupes', 'Dyson Airwrap vs Dupes: Honest Breakdown', 'comparison', 3,
     r'airwrap vs|vs airwrap|airwrap dupe|airwrap alternative'),
    # ---------- Silo 3: /reviews/  brand + model review hubs ----------
    ('/reviews/', 'laifen', 'Laifen Hair Dryer Reviews (All Models)', 'commercial', 1,
     r'\blaifen\b(?!\s*(vs|or))'),
    ('/reviews/', 'laifen-air', 'Laifen Air Review', 'commercial', 2,
     r'laifen air(?!\s*(vs|or))'),
    ('/reviews/', 'laifen-se-lite', 'Laifen SE Lite Review', 'commercial', 2,
     r'laifen se lite'),
    ('/reviews/', 'laifen-se2', 'Laifen SE2 Review', 'commercial', 2,
     r'laifen se2|\blaifen se\b'),
    ('/reviews/', 'laifen-swift', 'Laifen Swift Review', 'commercial', 3,
     r'laifen swift(?!\s*(vs|or))'),
    ('/reviews/', 'shark-flexstyle', 'Shark FlexStyle Review', 'commercial', 2,
     r'shark flexstyle|shark flex style'),
    ('/reviews/', 'shark-speedstyle', 'Shark SpeedStyle Review', 'commercial', 2,
     r'shark speedstyle|shark speed style'),
    ('/reviews/', 'dreame', 'Dreame Hair Dryer Review', 'commercial', 3,
     r'\bdreame\b'),
    ('/reviews/', 'slopehill', 'Slopehill Hair Dryer Review', 'commercial', 3,
     r'\bslopehill\b'),
    # ---------- Silo 4: /for/  needs-based (capture + internal-link) ----------
    ('/for/', 'hair-dryer-for-curly-hair', 'Hair Dryer for Curly Hair Guide', 'informational', 2,
     r'for curly hair|curly hair dryer|curly hair blow dryer'),
    ('/for/', 'hair-dryer-for-fine-hair', 'Hair Dryer for Fine Hair Guide', 'informational', 2,
     r'for fine hair|fine hair dryer|for thin hair|thin hair dryer'),
    ('/for/', 'hair-dryer-for-thick-hair', 'Hair Dryer for Thick Hair Guide', 'informational', 3,
     r'for thick hair|thick hair dryer|for coarse hair'),
    ('/for/', 'hair-dryer-for-frizzy-hair', 'Hair Dryer for Frizzy Hair Guide', 'informational', 3,
     r'for frizzy hair|frizzy hair dryer|anti frizz hair dryer'),
    ('/for/', 'travel-hair-dryer', 'Travel Hair Dryer Guide (Dual Voltage)', 'informational', 2,
     r'travel hair dryer|portable hair dryer|compact hair dryer|dual voltage hair dryer'),
    ('/for/', 'quiet-hair-dryer', 'Quiet Hair Dryer Guide (Low Noise)', 'informational', 3,
     r'quiet hair dryer|silent hair dryer|low noise hair dryer'),
    ('/for/', 'lightweight-hair-dryer', 'Lightweight Hair Dryer Guide', 'informational', 3,
     r'lightweight hair dryer|light weight hair dryer'),
    ('/for/', 'hair-dryer-with-diffuser', 'Hair Dryer with Diffuser Guide', 'informational', 2,
     r'with diffuser|hair diffuser|diffuser hair dryer'),
    # ---------- Silo 5: /learn/  informational authority ----------
    ('/learn/', 'ionic-vs-ceramic', 'Ionic vs Ceramic Hair Dryer: Explained', 'informational', 2,
     r'ionic vs ceramic|ionic or ceramic|what is ionic hair dryer|ionic hair dryer'),
    ('/learn/', 'how-many-watts', 'How Many Watts Should a Hair Dryer Be?', 'informational', 3,
     r'how many watts|watt hair dryer|1800w|1875w|2000w hair dryer'),
    ('/learn/', 'how-to-use-diffuser', 'How to Use a Hair Dryer Diffuser', 'informational', 3,
     r'how to use diffuser|how to diffuse|diffuser for wavy'),
    ('/learn/', 'is-dyson-worth-it', 'Is a Dyson Hair Dryer Worth It?', 'informational', 2,
     r'dyson worth it|is dyson worth|worth the money'),
    ('/learn/', 'high-speed-dryer', 'What Is a High-Speed Hair Dryer?', 'informational', 3,
     r'high speed hair dryer|high-speed|fastest hair dryer|fast drying'),
    # ---------- Silo 6: /ca/  Canada localization ----------
    ('/ca/', 'where-to-buy-laifen-canada', 'Where to Buy Laifen in Canada', 'transactional', 2,
     r'laifen canada|laifen hair dryer canada|buy laifen|laifen costco|laifen walmart|laifen amazon'),
    ('/ca/', 'best-hair-dryer-costco-canada', 'Best Hair Dryer at Costco Canada', 'transactional', 3,
     r'costco hair dryer|hair dryer costco|costco laifen'),
    ('/ca/', 'hair-dryer-sale-canada', 'Hair Dryer Deals & Sales in Canada', 'transactional', 3,
     r'hair dryer sale|hair dryer deal|hair dryer discount|black friday hair dryer'),
]

rows = []
for silo, slug, title, intent, prio, pat in PAGES:
    m = pool[pool['kw'].str.contains(pat, regex=True, na=False)].copy()
    # exclude if it better belongs to a more specific page is handled by later dedupe priority
    m = m.sort_values(['Volume', 'Opportunity'], ascending=False)
    rows.append({'Silo': silo, 'URL': f'/{slug}/', '页面标题': title,
                 '意图': intent, '优先级(T1最高)': prio,
                 '匹配关键词数': len(m), '月搜索量合计': int(m['Volume'].sum()),
                 '头部关键词': ' | '.join(m.head(5)['Keyword'].astype(str)),
                 'top1关键词': m.head(1)['Keyword'].iloc[0] if len(m) else '',
                 'top1月搜索量': int(m.head(1)['Volume'].iloc[0]) if len(m) else 0,
                 'KD中位': round(m['KD'].dropna().median(), 1) if m['KD'].notna().any() else np.nan})
SITEMAP = pd.DataFrame(rows)

out = []
def P(*a): out.append(' '.join(str(x) for x in a))
P("=" * 120)
P("SEO 站点信息架构 + 关键词映射 (基于 Semrush CA 实测数据)")
P("=" * 120)
P(f"页面总数: {len(SITEMAP)}")
P(f"总覆盖月搜索量: {SITEMAP['月搜索量合计'].sum():,}")
P(f"T1(最高优先): {len(SITEMAP[SITEMAP['优先级(T1最高)']==1]):>2} 页")
P(f"T2: {len(SITEMAP[SITEMAP['优先级(T1最高)']==2]):>2} 页   T3: {len(SITEMAP[SITEMAP['优先级(T1最高)']==3]):>2} 页")
P("")
for silo in ['/best/', '/compare/', '/reviews/', '/for/', '/learn/', '/ca/']:
    sub = SITEMAP[SITEMAP['Silo'] == silo].sort_values('优先级(T1最高)')
    P(f"\n### {silo}  ({len(sub)} 页, {sub['月搜索量合计'].sum():,}/月)")
    P(f"{'优先级':<6}{'URL':<34}{'月搜索量':>9}{'KD':>6}  页面标题")
    P("-" * 110)
    for _, r in sub.iterrows():
        P(f"{'T'+str(r['优先级(T1最高)']):<6}{r['URL']:<34}{r['月搜索量合计']:>9,}"
          f"{r['KD中位']:>6}  {r['页面标题']}")

P("\n" + "=" * 120)
P("各 Silo 汇总")
P("=" * 120)
sg = SITEMAP.groupby('Silo').agg(页面数=('URL', 'size'), 月搜索量=('月搜索量合计', 'sum'),
                                T1页数=('优先级(T1最高)', lambda s: (s == 1).sum()))
sg['搜索量占比%'] = (100 * sg['月搜索量'] / SITEMAP['月搜索量合计'].sum()).round(1)
P(sg.to_string())

with io.open('analysis/_sitemap.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
SITEMAP.to_pickle('analysis/sitemap.pkl')
print("written analysis/_sitemap.txt")
