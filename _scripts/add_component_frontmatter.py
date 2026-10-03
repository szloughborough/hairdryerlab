"""
给商业页补 §55 组件所需的 frontmatter：bestFor / skipIf / ratings。
只在缺失时插入，幂等。插入位置为 frontmatter 结束的 --- 之前。

ratings 只写我们有证据支撑的维度（价值 / 热控 / 附件 / 耐用性证据）。
干发速度、噪音、重量**没有实测数据，因此不写** —— 那些归 Lab Test Card 的「Not yet tested」。
"""
import io
import os
import re

DRAFTS = 'deliverables/drafts'

DATA = {
    # ---------------- best（购买指南，§43）----------------
    'best-hair-dryers': dict(
        bestFor='Most Canadian buyers who want high-speed drying without paying premium-brand prices.',
        skipIf='You need proven long-term reliability data, or you want a dryer already confirmed as dual voltage.',
        ratings=[
            ('Value', 'Good'), ('Heat control', 'Very Good'), ('Attachments', 'Good'), ('Durability evidence', 'Limited'),
        ]),
    'under-150': dict(
        bestFor='Buyers with a firm C$150 ceiling who want to reach the band where complaint rates fall.',
        skipIf='Your budget is under C$50, where our data shows the complaint rate stays near 30%.',
        ratings=[
            ('Value', 'Excellent'), ('Heat control', 'Very Good'), ('Attachments', 'Good'), ('Durability evidence', 'Limited'),
        ]),
    'best-hair-dryer-with-diffuser': dict(
        bestFor='Curly, wavy or coily hair — anyone who needs a diffuser that stays attached.',
        skipIf='Your hair is straight; a diffuser adds drying time without changing the result.',
        ratings=[
            ('Value', 'Very Good'), ('Heat control', 'Good'), ('Attachments', 'Good'), ('Durability evidence', 'Limited'),
        ]),
    'fast-drying': dict(
        bestFor='Thick, coarse or long hair, where airflow rather than heat decides drying time.',
        skipIf='Your hair is fine; a high-airflow dryer is more power than you need and harder to control.',
        ratings=[
            ('Value', 'Very Good'), ('Heat control', 'Good'), ('Attachments', 'Good'), ('Durability evidence', 'Limited'),
        ]),
    'dyson-alternatives': dict(
        bestFor="Buyers who want the Supersonic's high-airflow approach without paying C$400 or more.",
        skipIf='A failure at month six would be a serious financial problem, or you need universal voltage.',
        ratings=[
            ('Value', 'Excellent'), ('Heat control', 'Very Good'), ('Attachments', 'Good'), ('Durability evidence', 'Limited'),
        ]),
    'best-hair-dryer-canada': dict(
        bestFor='Canadian buyers who want to check retailer stock, ALCI compliance, warranty and duty before ordering.',
        skipIf='You are shopping outside Canada; the retailer and warranty guidance here does not apply.',
        ratings=[
            ('Value', 'Very Good'), ('Heat control', 'Good'), ('Attachments', 'Good'), ('Durability evidence', 'Limited'),
        ]),
    # ---------------- review（§42）----------------
    'laifen': dict(
        bestFor='Buyers who want high-speed drying at about C$100–145 from a brand-operated Canadian listing.',
        skipIf='You want proven long-term reliability, or you travel and need dual voltage.',
        ratings=[
            ('Value', 'Excellent'), ('Heat control', 'Very Good'), ('Attachments', 'Good'), ('Durability evidence', 'Limited'),
        ]),
    'dyson': dict(
        bestFor='Buyers who value a Canadian service network, a decade-old product family and universal voltage enough to pay about 4×.',
        skipIf='You are comparing on rating or on drying experience per dollar — Dyson does not lead either.',
        ratings=[
            ('Value', 'Limited'), ('Heat control', 'Excellent'), ('Attachments', 'Good'), ('Durability evidence', 'Good'),
        ]),
    'slopehill': dict(
        bestFor='Budget buyers who want the highest-volume dryer range in Canada at about C$40–100.',
        skipIf='You want a single, stable warranty counterparty — all three listings have third-party Buy Boxes.',
        ratings=[
            ('Value', 'Excellent'), ('Heat control', 'Limited'), ('Attachments', 'Good'), ('Durability evidence', 'Limited'),
        ]),
    'conair': dict(
        bestFor='Buyers who want the lowest-risk cheap dryer, backed by decades of Canadian warranty support.',
        skipIf='Your hair is thick or long — all three Conair models are heat-first conventional designs.',
        ratings=[
            ('Value', 'Good'), ('Heat control', 'Limited'), ('Attachments', 'Good'), ('Durability evidence', 'Limited'),
        ]),
    'dreame': dict(
        bestFor='Travellers who want one dual-voltage high-speed dryer with a diffuser included.',
        skipIf='You never travel — the Laifen Air does the same job for about C$60 less.',
        ratings=[
            ('Value', 'Good'), ('Heat control', 'Very Good'), ('Attachments', 'Very Good'), ('Durability evidence', 'Limited'),
        ]),
    'shark': dict(
        bestFor='Sensitive scalps and fine hair, where Scalp Shield limits air temperature near the scalp.',
        skipIf='You travel, or you want more than 64 Canadian ratings behind the reliability claim.',
        ratings=[
            ('Value', 'Good'), ('Heat control', 'Very Good'), ('Attachments', 'Very Good'), ('Durability evidence', 'Limited'),
        ]),
    'wavytalk': dict(
        bestFor='Budget buyers under about C$45 who want a diffuser and a brand-operated listing.',
        skipIf='Your hair is thick, long or heat-sensitive — this is a heat-first conventional dryer.',
        ratings=[
            ('Value', 'Good'), ('Heat control', 'Limited'), ('Attachments', 'Good'), ('Durability evidence', 'Limited'),
        ]),
    'revlon': dict(
        bestFor='A cheap second dryer for travel or a spare bathroom, at about C$19.',
        skipIf='Your hair is thick or long, or you need confirmed dual voltage.',
        ratings=[
            ('Value', 'Excellent'), ('Heat control', 'Limited'), ('Attachments', 'Limited'), ('Durability evidence', 'Limited'),
        ]),
    'aina': dict(
        bestFor='Budget buyers under about C$30 who want a diffuser and exactly one warranty counterparty.',
        skipIf='Your hair is thick, or you can stretch to about C$100 where the complaint rate roughly thirds.',
        ratings=[
            ('Value', 'Excellent'), ('Heat control', 'Limited'), ('Attachments', 'Good'), ('Durability evidence', 'Limited'),
        ]),
    'remington': dict(
        bestFor='Sub-C$30 buyers who want a long-established brand and the largest review base we track.',
        skipIf='Your hair is thick or long, or you want a brand-operated listing.',
        ratings=[
            ('Value', 'Very Good'), ('Heat control', 'Limited'), ('Attachments', 'Good'), ('Durability evidence', 'Limited'),
        ]),
    # ---------------- compare（§44）----------------
    'laifen-vs-dyson': dict(
        bestFor='Most Canadian buyers — Laifen gives roughly the same high-airflow approach for about a quarter of the price.',
        skipIf='You need universal voltage or a Canadian service network, or you want proven reliability: buy Dyson.',
        ratings=[
            ('Value', 'Excellent'), ('Heat control', 'Very Good'), ('Attachments', 'Good'), ('Durability evidence', 'Limited'),
        ]),
    'shark-vs-dyson': dict(
        bestFor='Sensitive scalps and styling-first routines — Shark adds Scalp Shield at roughly half the price.',
        skipIf='You want the most evidence behind the decision — Dyson has about five times the Canadian review base.',
        ratings=[
            ('Value', 'Very Good'), ('Heat control', 'Very Good'), ('Attachments', 'Very Good'), ('Durability evidence', 'Limited'),
        ]),
}

changed = []
for slug, d in DATA.items():
    p = os.path.join(DRAFTS, slug + '.mdx')
    if not os.path.exists(p):
        print(f'  !! 找不到 {p}')
        continue
    t = io.open(p, encoding='utf-8').read()
    if re.search(r'(?m)^bestFor:', t):
        print(f'  {slug}: 已有 bestFor，跳过')
        continue

    lines = [f'bestFor: "{d["bestFor"]}"', f'skipIf: "{d["skipIf"]}"', 'ratings:']
    for label, grade in d['ratings']:
        lines.append(f'  - label: "{label}"')
        lines.append(f'    grade: "{grade}"')
    block = '\n'.join(lines) + '\n'

    # 插到 frontmatter 结束的 --- 之前
    m = re.search(r'(?m)^---\s*$', t)          # 开头那条
    m2 = re.search(r'(?m)^---\s*$', t[m.end():])
    close = m.end() + m2.start()
    t2 = t[:close] + block + t[close:]
    io.open(p, 'w', encoding='utf-8').write(t2)
    changed.append(slug)

print(f'\n补入 frontmatter 的页面：{len(changed)} 个')
for s in changed:
    print(f'   {s}')
