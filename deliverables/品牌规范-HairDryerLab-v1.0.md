# Hair Dryer Lab — Brand Guidelines

> **本文件是全站唯一的品牌规范源（Source of Truth）。**
> 所有网站搭建、页面设计、组件开发、内容呈现都必须遵循本文件。
> 与其它文档冲突时，以本文件为准。

| 项 | 值 |
|---|---|
| Domain | hairdryerlab.ca |
| Market | Canada |
| Brand Type | Independent Hair Dryer Review & Buying Guide Media Site |
| Primary Monetization | Affiliate Marketing |
| Primary Brands | Laifen, Dreame, Slopehill |
| Secondary / Traffic Brands | Dyson, Shark, T3, GHD, Conair, BaByliss, Revlon |
| Version | 1.0 |
| Last Updated | October 2026 |

---

## 1. Brand Overview

### 1.1 Brand Name
**Hair Dryer Lab** — primary domain `hairdryerlab.ca`

The main logo should display: **HAIR DRYER LAB**
- Do **not** include `.ca` in the primary logo.
- `.ca` may be used in: favicon-related branding, footer, social bios, browser title, trust statements, Canada-specific page messaging.

## 2. Brand Positioning

Hair Dryer Lab is an independent hair dryer testing, comparison and buying-guide website for Canadian consumers.

The site should help users answer practical purchase questions such as:
- Which hair dryer is right for my hair type?
- Is a premium high-speed dryer worth the extra money?
- Is Laifen a good alternative to Dyson?
- Is Dreame better for travel?
- Which dryer works best for curly, fine, thick or frizzy hair?
- Which models offer the best value in Canada?
- What is actually different between two similar dryers?
- Which dryer is lighter, quieter, faster or easier to use?

The site **must not** feel like a brand-owned ecommerce store.
It must **not** feel like a generic affiliate site.

Desired user perception:
> "I'm buying a hair dryer in Canada. I should check Hair Dryer Lab before deciding."

## 3. Core Brand Promise

**Primary Brand Statement**
Independent hair dryer reviews, comparisons and real-world testing for Canadian shoppers.

**Short Brand Line**
Tested. Compared. Explained.

**Homepage Positioning Line**
Find the right hair dryer. Based on testing, not hype.

## 4. Brand Mission

Hair Dryer Lab exists to reduce the amount of guesswork involved in buying a hair dryer.

The site should turn technical specifications, marketing claims, model differences, real-world usability, price differences and hair-type suitability into practical buying guidance.

The role of the brand is **not** to tell users what they must buy. The role is to:
1. test products where possible
2. compare them under consistent criteria
3. explain important differences
4. identify who each model is suitable for
5. identify who should skip each model
6. show current Canadian purchase options
7. make monetization transparent

## 5. Brand Personality

Should feel: Measured · Independent · Modern · Helpful · Evidence-led · Calm · Premium · Accessible · Practical · Human

Should never feel: Overly feminine · Overly technical · Medical · Futuristic · Luxury-fashion oriented · Cheap affiliate marketing · Aggressive ecommerce · SaaS-like · AI-generated · Hype-driven

## 6. Brand Voice

### 6.1 Writing Principles

**Direct**
- Prefer: "The Swift is light, fast and easy to use."
- Avoid: "The Laifen Swift delivers a truly revolutionary and transformative hair-drying experience."

**Evidence-led**
- Prefer: "It weighed 407 g on our scale."
- Avoid: "It feels incredibly lightweight."

**Specific**
- Prefer: "It dried our test section 42 seconds faster than the comparison model."
- Avoid: "It dries hair much faster."

**Balanced** — every review should clearly explain strengths, weaknesses, suitable users, unsuitable users.

**Consumer-first** — explain *why* a feature matters. Do not simply repeat manufacturer specifications.

## 7. Editorial Tone Examples

**Good**
- "The Swift dried our test hair quickly and weighs less than most premium dryers we tested. Its biggest limitation is styling versatility."
- "If you mainly want fast drying under CAD $200, this is one of the more interesting options we tested."

**Bad**
- "The Swift absolutely blew us away with its stunning performance and incredible power."
- "This is hands-down the best hair dryer you can buy."

## 8. Visual Design Philosophy

The visual system should combine: consumer testing credibility · beauty-category polish · editorial readability · restrained technology cues.

Overall visual concept: **Editorial beauty + measurable product testing**

The word "Lab" means: **We test products.**
It does **not** mean: We are a scientific or medical laboratory.

## 9. Design Keywords

Prioritize: Clean · Measured · Editorial · Human · Premium · Neutral
Avoid: Futuristic · Cyberpunk · Neon · Girly pink · Medical lab · Luxury black-and-gold · Amazon-affiliate style · SaaS-dashboard style

## 10. Logo System

### 10.1 Primary Logo
Typography-led logo: **HAIR DRYER LAB**. The word LAB may receive subtle visual emphasis.
Possible structure: `HAIR DRYER [ LAB ]` — the bracket treatment should remain subtle.
**Do not** turn LAB into a large button or badge.

## 11. Logo Symbol

Preferred symbol should be **abstract rather than literal**. Recommended concept: **Airflow + Measurement Point**

```
─────●
 ────
  ───
```

Meaning: airflow · drying speed · measurement · comparison · testing

The mark may also be combined with **HDL** for compact applications.

## 12. Logo Avoid List

Do **not** use: female face silhouettes · long-hair illustrations · lips · beauty icons · a literal pink hair dryer · maple leaf as the primary symbol · Canadian flag · scientific flask icons · microscope icons · lightning bolts · flames · glossy 3D logo effects · gradient-heavy logos.

The brand should not look like a salon. It should not look like a manufacturer.

## 13. Primary Color Palette

| Token | Hex | Use | Purpose |
|---|---|---|---|
| **Lab Navy** | `#183153` | logo, main navigation, headings, strong text, important UI labels, comparison headers | trust, authority, editorial credibility |
| **Ice Blue** | `#EAF3F7` | testing modules, methodology sections, light information backgrounds, comparison highlights, educational modules | testing, clarity, calm, subtle Canadian feeling |
| **Warm White** | `#FAFAF8` | primary page background (avoid pure white across the entire page) | less clinical appearance, better long-form readability, stronger product photography contrast |
| **Body Text** | `#202427` | body copy | — |
| **Secondary Text** | `#66727A` | secondary copy | — |
| **Accent Coral** | `#E85D4A` | primary CTA, Editor's Pick, key highlight, active indicators — **sparingly** | — |
| **Positive Green** | `#27745B` | Pros, positive test result, passed criteria, availability confirmation | — |
| **Border** | `#DDE3E6` | dividers, card borders | — |

Coral should occupy no more than roughly **5%** of a normal page.

## 14. CSS Design Tokens

```css
:root {
  --hdl-navy: #183153;
  --hdl-ice: #EAF3F7;
  --hdl-background: #FAFAF8;
  --hdl-text: #202427;
  --hdl-text-secondary: #66727A;
  --hdl-accent: #E85D4A;
  --hdl-positive: #27745B;
  --hdl-border: #DDE3E6;
  --hdl-white: #FFFFFF;

  --hdl-radius-sm: 8px;
  --hdl-radius-md: 12px;
  --hdl-radius-pill: 999px;

  --hdl-content-width: 1200px;
  --hdl-article-width: 780px;
  --hdl-comparison-width: 1080px;
}
```

## 15. Color Usage Ratio

Recommended ratio: **80%** neutral / warm white / white · **15%** navy + ice blue · **5%** coral accent.

Do not create large coral backgrounds. Do not make coral the navigation color. Products should provide much of the page's natural visual colour.

## 16. Typography

**Heading Font — Manrope**
Use for: H1, H2, H3, numbers, testing metrics, product model names, comparison highlights.

**Body Font — Inter**
Use for: body text, navigation, tables, buttons, labels, forms, captions.

Both fonts must support English **and French** characters (important for future Québec content).

## 17. Typography Scale

**Desktop**
| Element | Font | Weight | Size |
|---|---|---|---|
| H1 | Manrope | 700 | 48px, line-height 1.1–1.2 |
| H2 | Manrope | 700 | 34px |
| H3 | Manrope | 650–700 | 24px |
| Body | Inter | 400 | 17px, line-height 1.7 |
| Small | Inter | — | 14–15px |

**Mobile**
| Element | Size |
|---|---|
| H1 | 32–34px |
| H2 | 26–28px |
| H3 | 21–23px |
| Body | 16.5–17px, line-height 1.65–1.75 |

Do not reduce article copy to 14px.

## 18. Layout System

| Context | Width |
|---|---|
| Global max site width | 1200px |
| Editorial article width | 760–800px (recommended 780px) |
| Comparison content | 1000–1100px (recommended 1080px) |

## 19. Spacing

Scale: `4 · 8 · 12 · 16 · 24 · 32 · 48 · 64 · 96`

Use generous spacing. Avoid tight card stacking. Long-form articles should have clear visual breathing room.

## 20. Border Radius

| Context | Radius |
|---|---|
| Standard UI | 8px |
| Cards | 12px |
| Tags / badges | 999px |

Do not use excessive 20–30px rounded cards. The site should feel editorial rather than app-like.

## 21. Shadows

Use shadows very lightly — subtle, low blur, low opacity.
Cards should usually be separated by **border / whitespace / background tone** rather than heavy drop shadows.

## 22. Header

Recommended desktop structure:
```
HAIR DRYER LAB

Best Hair Dryers   Reviews   Comparisons   Hair Types   Guides

How We Test   Search
```

Do **not** include: Home · Blog · Shop · Deals · News — unless a clear future business reason emerges.

## 23. Header Behaviour

- **Desktop**: clean horizontal navigation, white or warm-white background, thin bottom border, sticky optional
- **Mobile**: brand logo, search icon, menu icon. Do not make the mobile header oversized.

## 24. Footer

**Main Navigation**: Best Hair Dryers · Reviews · Comparisons · Hair Types · Guides · How We Test

**Company**: About · Contact · Editorial Policy · Affiliate Disclosure · Privacy Policy · Terms

**Canada** — suggested line: *Independent hair dryer reviews and buying advice for Canadian shoppers.*

Footer should remain visually quiet.

## 25. Homepage Structure

### Section 1 — Hero
- **H1**: Find the right hair dryer.
- Supporting headline: Based on testing, not hype.
- Description: Independent reviews and comparisons for Canadian shoppers.
- Primary CTA: **Find Your Hair Dryer**
- Secondary CTA: **See How We Test**
- Hero image: 2–3 hair dryers, testing tools, editorial still-life composition, warm white or neutral background. **Avoid beauty-model hero imagery.**

## 26. Homepage — Tested & Compared

Section title: **Tested & Compared**

Show reviewed models. Each card may display: product image · model · test status · 2–3 key test metrics · review link.

Example:
```
TESTED
Laifen Swift
Drying time   4:18
Noise         63 dB
Weight        407 g
Read Review
```

## 27. Homepage — Start With Your Hair

Categories: Curly Hair · Fine Hair · Thick Hair · Frizzy Hair
Use **authentic texture photography**. Do not use stylized stock beauty photography with unrealistic hair.

## 28. Homepage — Start With What Matters

Feature entry points: Fast Drying · Quiet · Lightweight · Diffuser · Travel · Under CAD $150 · Premium · Dyson Alternatives
These should connect directly to SEO clusters.

## 29. Core Brand Component — Lab Test Card

This should become the most recognizable UI element on Hair Dryer Lab.

```
LAB TEST
────────────────────
Laifen Swift

Drying Speed        4:18
Noise @ 1m          63 dB
Weight              407 g
Max Temperature     87°C
Cord Length         1.8 m

Tested: Sep 2026
Unit: Review sample

See how we test →
```

Visual treatment: Ice Blue background · navy heading · highly legible numeric alignment · thin borders · minimal decoration.

## 30. Product Review Hero

A review hero should quickly answer: What is this product? · What did we think? · Who is it for? · What are the important numbers? · Where can the user buy it?

```
Laifen Swift Review
Fast, light and much cheaper than a Dyson.
[Product Image]
BEST FOR
Fast drying under CAD $200
Drying   4:18    Noise   63 dB    Weight   407 g
Check Price
```

## 31. Review Result Style

**Avoid** overall numerical scores: `9.4/10` · `94%` · `4.8/5`
**Avoid** generic star ratings unless quoting verified consumer ratings.

**Prefer** category conclusions:
```
Drying Speed     Excellent
Noise            Good
Weight           Excellent
Heat Control     Good
Attachments      Very Good
Value            Excellent
```
Also show actual measured values whenever available.

## 32. Review Conclusion

Every review should include:

**Best for** — e.g. "Fast drying under CAD $200"
**Skip if** — e.g. "You want multiple styling attachments."

This is preferred over "Overall Winner".

## 33. Comparison Table

```
Feature          Laifen    Dreame    Dyson
Canada Price     CAD $X    CAD $X    CAD $X
Weight           X g       X g       X g
Noise            X dB      X dB      X dB
Drying Test      X:XX      X:XX      X:XX
Diffuser         Yes       Yes       Yes
Best For         Value     Travel    Premium
```

Tables must: scroll horizontally on mobile · keep headers readable · avoid tiny text · use sticky first column only when needed · show actual test values where possible.

## 34. Comparison Language

**Avoid**: WINNER!!! · #1 · Best Overall Winner · Beats Everything
**Prefer**: Our pick for value · Better for travel · Better for styling · Better for lighter weight · Better if budget is the priority

## 35. CTA System

| Type | Copy |
|---|---|
| Primary CTA | **Check price** |
| Secondary supporting label | at Laifen Canada / at [Retailer] |
| Alternative CTA | See current price |
| Review CTA | See our full test |
| Comparison CTA | Compare prices |
| Methodology CTA | See how we test |

## 36. CTA Avoid List

Do not use: BUY NOW!!! · GET DEAL · MASSIVE SAVINGS · SHOP NOW · LIMITED TIME · BEST PRICE GUARANTEED · MUST BUY — unless an actual retailer promotion is being factually described.

## 37. Affiliate Disclosure

Recommended copy:
> Hair Dryer Lab may earn a commission when you buy through our links. This doesn't affect how we test or review products.

**Placement**: review/article header area · buying guides · comparison pages · footer policy link.
**Do not hide disclosures.**

## 38. Product Photography

Build a consistent proprietary photo library. Categories:
- **Product Hero** — warm white / light neutral background, product fills 65–75% of frame, soft natural shadow, clean composition
- **Test Setup** — sound meter, scale, thermometer, stopwatch, measuring tape, power meter. Practical, not clinical.
- **Real Use** — short / long / curly / fine / thick / frizzy hair. Use real people where possible.

## 39. Image Style

**Preferred**: natural light · subtle shadows · realistic textures · editorial product photography · neutral background · accurate product colour · realistic hair texture
**Avoid**: beauty glamour photography · excessive retouching · artificial glowing product effects · neon backgrounds · unrealistic AI hair · floating product renders unless provided by the manufacturer

## 40. Canada-Specific Visual Strategy

Do **not** use: maple leaves everywhere · Canadian flags · red-and-white theme · snowy mountains as generic Canada imagery.

Canada should be communicated through **useful buying information**: CAD pricing · Canadian stock · Canadian retailers · Canadian warranty · local shipping · Canadian winter concerns · static / dry indoor air · Québec French support.

Example UI:
```
Price in Canada
CAD $169.99
Price checked
Oct 2, 2026
```

## 41. Mobile-First Design

Mobile is the primary design reference. Within approximately the first **1–1.5 screens**, users should see: product name · one-line verdict · product image · best-for statement · important measured values · price CTA.

Avoid pushing important information below: oversized breadcrumbs · author biography · multiple tags · newsletters · ads · excessive disclosure copy.

## 42. Article Page Layout

1. Breadcrumb
2. H1
3. One-line verdict
4. Affiliate disclosure
5. Product hero
6. Best for / Skip if
7. Lab Test Card
8. Quick verdict
9. What we tested
10. Performance sections
11. Real-world use
12. Pros and cons
13. Competitor comparison
14. Price / value
15. Recommendation
16. FAQ
17. Related reviews / guides

## 43. Buying Guide Layout

1. H1
2. Methodology / how picks were selected
3. Quick Picks
4. Comparison Table
5. Individual recommendations
6. Best for specific users
7. How to choose
8. Test criteria
9. FAQ
10. Related reviews

## 44. Comparison Page Layout

1. H1
2. Quick answer
3. Side-by-side product image
4. Comparison table
5. Price
6. Design / weight
7. Drying performance
8. Heat
9. Noise
10. Attachments
11. Hair-type suitability
12. Travel / storage
13. Value
14. Who should buy Product A
15. Who should buy Product B
16. Alternatives
17. FAQ

## 45. Hair-Type Page Layout

1. H1
2. Problem definition
3. What matters for this hair type
4. Recommended dryers
5. Comparison table
6. Why each product fits
7. Features to look for
8. Features that may not matter
9. Usage guidance
10. FAQ
11. Related guides

## 46. Icon System

Style: outline icons · rounded geometry · 1.5–2px stroke · visually lightweight.

Concepts: airflow · thermometer · sound · weight · clock · diffuser · suitcase · dollar · hair texture · measurement.

**Avoid emoji as permanent UI icons.**

## 47. Badge System

Permitted badges: **Tested** · **Review Sample** · **Purchased** · **Updated** · **Best for Value** · **Best for Travel** · **Best for Curly Hair**

Badge styling: subtle · small · not gamified · not oversized.

## 48. Price Presentation

Always display: currency explicitly · retailer · last checked date when feasible.

```
CAD $169.99
Laifen Canada
Price checked Oct 2, 2026
```

Do not imply price permanence.

## 49. Product Test Methodology Visuals

Each measurable criterion must use a consistent unit. This consistency is part of the Hair Dryer Lab brand.

| Criterion | Unit |
|---|---|
| Drying | minutes : seconds |
| Noise | dB at 1 metre |
| Weight | grams |
| Temperature | °C |
| Cord | metres |
| Power | watts |

## 50. Recommended Core Test Metrics

dryer-only weight · cord length · nozzle attachment weight · drying time · sound at fixed distance · maximum temperature · temperature consistency · airflow · power draw · handle comfort · button placement · filter cleaning · attachment strength · storage convenience · travel suitability

## 51. Information Gain Requirement

Every major review should aim to contribute information **unavailable from the manufacturer**: measured weight · measured noise · measured temperature · real drying time · comparison photos · nozzle usability · cord measurement · real hair-type feedback · long-term observations.

**Do not build reviews by rewriting product pages.**

## 52. Affiliate Brand Neutrality

Current commercial partners may include Laifen, Dreame, Slopehill. **Their commission rates must not dictate editorial conclusions.** A product should not be recommended solely because it pays a higher commission. If a non-affiliate product is better for a specific user type, it can still be included.

This principle is essential to the Hair Dryer Lab brand.

## 53. SEO + VI Alignment

| Cluster | Visual language |
|---|---|
| Best Hair Dryers | comparison-focused · selection cards · clear ranking rationale |
| Reviews | testing evidence · real photography · measured data |
| Comparisons | side-by-side · tables · clear differences |
| Hair Types | texture photography · user-focused · educational |
| Guides | diagrams · explainer illustrations · practical steps |

## 54. Core Navigation Taxonomy

```
/
├── best-hair-dryers/
├── reviews/
├── comparisons/
├── hair-types/
├── guides/
└── how-we-test/
```

**Suggested future subcategories:**
```
/best-hair-dryers/
    best-hair-dryer-canada/
    best-high-speed-hair-dryer/
    best-ionic-hair-dryer/
    best-lightweight-hair-dryer/
    best-travel-hair-dryer/

/reviews/
    laifen/
    dreame/
    slopehill/
    dyson/
    shark/

/comparisons/
    laifen-vs-dyson/
    laifen-vs-dreame/
    dreame-vs-dyson/

/hair-types/
    curly-hair/
    fine-hair/
    thick-hair/
    frizzy-hair/

/guides/
    ionic-hair-dryer/
    diffuser/
    travel/
    noise/
    hair-dryer-care/
```

## 55. Component Library

Required reusable components:
1. Header · 2. Footer · 3. Breadcrumb · 4. Product Hero · 5. **Lab Test Card** · 6. Best For / Skip If · 7. Quick Verdict · 8. Pros / Cons · 9. Comparison Table · 10. Product Card · 11. Affiliate CTA · 12. Price Box · 13. Disclosure Box · 14. Methodology Box · 15. Tested Badge · 16. Hair-Type Card · 17. Feature Card · 18. Related Content · 19. Author Box · 20. Update Date · 21. FAQ · 22. Newsletter / email capture · 23. Image caption · 24. Evidence / source note

## 56. Astra Implementation Guidance

If built with WordPress + Astra: use Astra mainly as the lightweight layout framework · avoid default Astra styling dominating the brand · create custom global colours · create global typography tokens · build reusable Gutenberg patterns · avoid excessive third-party page-builder dependency · use blocks for repeatable review modules · make comparison tables responsive · keep DOM structure simple · keep animation minimal.

## 57. Animation

**Allowed**: subtle hover · light button transition · small accordion motion · smooth disclosure opening.
**Avoid**: parallax · heavy entrance animations · floating product effects · animated gradients · excessive scrolling effects.
Performance is more important than animation.

## 58. Accessibility

Minimum expectations: strong text contrast · keyboard navigability · visible focus states · alt text on meaningful images · descriptive link labels · tables usable on mobile · buttons at least comfortable touch size · no information communicated by colour alone.

## 59. SEO-Friendly Visual Rules

Do not hide primary content behind tabs. Avoid: excessive JavaScript rendering · text embedded only inside images · image-only navigation · unnecessary sliders · infinite-scroll-only article access. Important content should remain crawlable and readable.

## 60. Trust Elements

Recommended trust components: How We Test · Editorial Policy · Affiliate Disclosure · Author profiles · Date tested · Date updated · Product acquisition method · Real test photos · Measurement methodology.
**Trust should come from transparency rather than large "Trusted" badges.**

## 61. Editorial Metadata

Each review should display: author · tested date · updated date · acquisition method.

```
Tested by Hair Dryer Lab
Updated October 2026

Product source:
Review sample supplied by Laifen
```

Where appropriate, state: *The brand had no editorial control over this review.*

## 62. About Page Visual Direction

Show: real testing environment · products being measured · authors / testers where appropriate · testing principles.
**Avoid generic office-team stock photos.**

## 63. How We Test Page

This should be one of the strongest brand pages. Sections:
1. Why we test · 2. Products we test · 3. How products are sourced · 4. Test environment · 5. Drying-speed test · 6. Noise test · 7. Weight test · 8. Heat test · 9. Real-world use · 10. Hair-type feedback · 11. Price/value methodology · 12. Affiliate independence · 13. Update policy

## 64. Social Visual Style

Reuse warm white · navy · ice blue · coral highlights · real product photography · large metric callouts.

```
LAIFEN SWIFT
407 g
63 dB
4:18 drying test
Hair Dryer Lab
```

Do not create clickbait thumbnails.

## 65. Favicon

Preferred: **HDL monogram** or airflow measurement symbol. Use navy background or navy mark.
Do not try to fit the full hair dryer illustration into the favicon.

## 66. Open Graph Images

Recommended ratio **1200 × 630**. Structure: product image · concise page title · Hair Dryer Lab logo · one key differentiating metric if relevant.

```
LAIFEN vs DYSON
Which is better under CAD $200?
Hair Dryer Lab
```

Avoid clutter.

## 67. French Canada Readiness

The design should anticipate future French content. Do not use fixed-width labels that break with longer French text. Typography must support é è ê ç à ô. Possible future architecture: `/fr/`.

**Do not launch machine-translated French content solely for SEO.**

## 68. Content Image Ratios

| Context | Ratio |
|---|---|
| Hero images | 16:9 or 4:3 |
| Product cards | 4:5 |
| Test evidence | 4:3 |
| Hair texture | 4:5 |
| Comparison | 16:9 |
| Open Graph | 1200 × 630 |

## 69. Product Card

```
[Product Image]
Laifen Swift
Best for:
Fast drying under CAD $200
407 g    63 dB    4:18
Read Review    Check Price
```

Avoid overcrowding cards with every specification.

## 70. Pros and Cons

```
What we liked
✓ Fast drying
✓ Light body
✓ Simple magnetic nozzles

What we didn't
– Limited styling attachments
– No storage case
```

Avoid excessive green/red blocks. Keep treatment editorial.

## 71. Data Visualization

Charts should: use navy · use muted neutral tones · use coral only as highlight · show units · start from honest axis ranges · remain readable on mobile.

Recommended charts: drying time · weight comparison · noise comparison · temperature comparison.
Avoid unnecessary 3D charts.

## 72. Commercial Integrity

Separate **Editorial conclusion** from **Commercial CTA**.

- Do not write: "Because Laifen offers great value, click here to buy now."
- Prefer, first: "For users mainly concerned with drying speed and weight, Laifen performed well in our testing."
- Then separately: "Check current price"

## 73. Brand Hierarchy

Hair Dryer Lab must always remain the primary brand.

**Correct**: Hair Dryer Lab → tests → Laifen → Dreame → Slopehill → Dyson → Shark
**Incorrect**: Laifen → presented by Hair Dryer Lab

The site must never visually resemble a manufacturer microsite.

## 74. Anti-Patterns

Do not use: huge star ratings · countdown timers · fake scarcity · flashing CTA buttons · excessive sale badges · "#1 Choice" everywhere · "Winner" badges on every table · bright yellow Amazon-like buttons · giant sticky ads · auto-play video · forced popup before users read content · stock smiling beauty-model hero images · fake laboratory coats · maple-leaf overload · generic AI-generated illustrations.

## 75. Homepage Visual Priority

1. Trust · 2. Product expertise · 3. Testing · 4. Navigation by user need · 5. Commercial CTA

Commercial monetization should not dominate the first impression.

## 76. UX Principle

Every important page should quickly answer:
- Am I in the right place?
- Is this relevant to my hair or budget?
- Has this product actually been evaluated?
- What are the important differences?
- What should I do next?

## 77. Brand Success Test

Before approving a page design, ask:
> Would this still look credible if all affiliate buttons were removed?

If the answer is no, redesign it.

## 78. Final Design Standard

Hair Dryer Lab should feel like:
> A Canadian consumer testing publication that happens to earn affiliate revenue.

Not:
> An affiliate website pretending to be a testing publication.

That distinction should guide every design, content and UX decision.

## 79. Developer Handoff Summary

Developers should implement: WordPress · Astra · Manrope + Inter · global design tokens · reusable Gutenberg components · responsive comparison tables · mobile-first article layouts · custom Lab Test Card · custom Product Card · consistent affiliate CTA · transparent disclosures · simple navigation · minimal JavaScript · high performance · strong accessibility · SEO-safe page structure

> ⚠️ **平台冲突说明**：本节指定 WordPress + Astra，但本项目已确定使用 **Astro 5**（见《Astro技术栈清单.md》）。
> 品牌文档 §56 的措辞是 "If built with WordPress + Astra"（条件式），且 §81 的冲突裁决原则是
> 「信任 > 促销 / 清晰 > 设计 / 准确推荐 > 最大化点击」——均为平台无关原则。
> 因此本项目按 Astro 实现，同时完整满足 §79 的实质要求：全局设计 token、可复用组件、
> 响应式对比表、移动优先、自定义 Lab Test Card / Product Card、统一 CTA、透明披露、
> 简单导航、极少 JS、高性能、无障碍、SEO 安全结构。

## 80. Canonical Brand Token Reference

```
BRAND              Hair Dryer Lab
DOMAIN             hairdryerlab.ca
POSITIONING        Independent hair dryer testing and buying advice for Canada.
TAGLINE            Tested. Compared. Explained.

PRIMARY NAVY       #183153
ICE BLUE           #EAF3F7
BACKGROUND         #FAFAF8
TEXT               #202427
SECONDARY TEXT     #66727A
ACCENT             #E85D4A
POSITIVE           #27745B
BORDER             #DDE3E6

HEADLINE FONT      Manrope
BODY FONT          Inter

STANDARD RADIUS    8px
CARD RADIUS        12px
ARTICLE WIDTH      780px
SITE WIDTH         1200px
COMPARISON WIDTH   1080px

CORE VISUAL ASSET  Lab Test Card
CORE BRAND FEEL    Clean · Measured · Editorial · Human · Premium · Neutral
```

## 81. Final Rule

When there is a conflict between making the site look more promotional and making the site look more trustworthy — **choose trust**.

When there is a conflict between adding more design and making the information easier to understand — **choose clarity**.

When there is a conflict between maximizing affiliate clicks and giving the user a more accurate recommendation — **choose the accurate recommendation**.

That is the Hair Dryer Lab brand.
