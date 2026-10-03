# 借鉴分析与 AI 搜索优化标准

> 来源：`brand-website-skill-handoff-20260829.zip`（Codex/Claude Code 品牌站建设 skill 包）
> 用途：① 提取可借鉴的规则 ② 标出不能照搬的红线 ③ 补上该包的空白——**AI/大模型优化（AEO/GEO）标准**

---

## 0. 一句话结论

这个包是**为「品牌自营产品站」写的**（品牌自己卖自己的货），我们做的是**独立第三方联盟决策站**。
它的**流程纪律与页面规范值得高度借鉴**（含几条我们目前缺失的、对 AI 检索直接有效的规则）；
但它的**信息披露与来源表述规则必须反向执行**——照搬会违反加拿大法规、并摧毁我们唯一的护城河。

它**没有任何大模型优化指引**，这是第 3 节要补的部分。

---

## 1. ✅ 值得借鉴（10 条，按价值排序）

### ★1. 每个 H2 必须含核心实体或语义变体（我们目前缺失）
**原文规则**：*"Make every major h2 include the primary keyword or a clear grammatical or morphological variation"*（首页/聚合/品类/产品/品牌模板）

**为什么对我们价值最高**：这不只是传统 SEO 规则，**更是 AI 检索的关键**——大模型按标题切块（chunking）后逐块检索，标题能否自包含地表达主题，直接决定我们能否被引用。我们现在的《内容结构标准》定义了骨架顺序，但**没有这条覆盖规则**。

**采纳方式**：写进《内容结构标准》通用规范：
> 每个 H2 必须包含页面的核心实体（产品名/品类词/需求词）或其自然语义变体。禁止空标题（如「更多信息」「总结」）。
> 反例：`## Other things to consider` → 正例：`## What else matters when choosing a Dyson alternative`

### ★2. FAQ 的五条硬纪律（我们目前只写了「3–5 条」）
| 原文规则 | 采纳 |
|---|---|
| 每页**恰好 5 个**问题 | 采纳：商业页固定 5 条 |
| 答案 **≤100 词**，40–80 词最佳 | 采纳 |
| **第一句直接回答问题** | 采纳（这正是 featured snippet 与 AI Overview 的抽取点） |
| 手风琴内容**必须在 DOM 里**，不得点击后才请求 | **重点采纳**——懒加载 FAQ 对爬虫和 LLM 都等于不存在 |
| FAQPage JSON-LD 必须与可见文字**逐字一致** | 采纳 |
| **不得承诺 FAQ 富媒体结果** | 采纳（Google 2023 已对多数站点取消 FAQ 富结果；schema 现在主要服务于语义与 AI 解析，不是富结果） |

### ★3. H1 之后紧跟 90–110 词导语
**原文规则**：品类页 H1 正下方放一段 90–110 词（约 100 词最佳）的独特导语。

**价值**：这段文字是 featured snippet、AI Overview 与 LLM 摘要的**最高频抓取区**。我们目前的骨架是「H1 → 首屏结论卡」，可以合并成：H1 → 90–110 词导语（即为结论卡）→ 目录。

### ★4. 价格显示纪律（联盟站的现实痛点）
**原文规则**：
- 只有确认了**具体变体**的价格、为正数、且有合法三字母货币码时，才显示数字价格
- 无确认价格时显示 `Check current price on Amazon`，**不显示数字**
- 绝不显示独立的 `Current price` 标签
- 变体切换时不能留下过期价格

**采纳**：我们做价格对比，必须标注核对日期，且不用无法验证的价格。建议格式：
`C$99.99（2026-10-02 核对）` 或 `Check current price on Amazon`

### ★5. 禁止用「过滤子集」计算 aggregateRating / 禁止编造评论数据
**原文规则**：*"Do not calculate aggregateRating from a filtered review subset... Do not invent price, currency, availability, reviews, or aggregate ratings."*

**这条对我们尤其重要**——因为我们手上有 8,261 条 Amazon 评论，很容易顺手生成 `aggregateRating`。**绝对不能这么做**：
- Google 评论摘要指南明确：**非本站直接产出的评分（聚合自其他网站）不具备资格**
- 用 Amazon 评论生成 aggregateRating 属违规，可能触发人工处罚

**采纳**：全站**不使用** `aggregateRating`，除非是我们自己实测给出的评分。Amazon 的星级只作为**可见文字**引用并注明来源。

### ★6. 禁止「旁观者措辞」
**原文禁用词**：`the listing describes`、`the source listing`、`the product page includes`、`source-backed details`

**价值**：这类措辞会暴露内容是从别处拼凑的，削弱主体性。

**采纳（但要与我们第 2 节的差异区分开）**：
- ❌ 不要写：*"The Amazon listing states it has a brushless motor."*
- ✅ 要写：*"It has a brushless motor."* / *"We analysed 8,261 reviews and found..."*
关键区别：**以我们为主体陈述研究结果**（合法且有力），而不是**转述别人的页面**（软弱且像拼凑）。

### ★7. 分阶段 Gate + 计数对账的流程纪律
**原文规则**：每个 Phase 有明确 Gate；*"Reconcile counts at every stage"*；未达 Gate 不进入下一阶段；*"Do not call the project complete merely because the pages were generated."*

**采纳**：写进我们的执行流程——每批内容上线前做一次对账（计划页数 vs 实际上线、H1 数、canonical 数、内链数、FAQ 覆盖、schema 与可见文字一致数）。

### ★8. 唯一性硬指标
- 每页**恰好一个 H1**
- 每页**恰好一个 canonical**，且不含 query/fragment
- Title **50–60 字符**，主关键词靠前
- Meta description **150–160 字符**
- 每张有意义图片有**非空且描述性 alt**（不写 `image`）
- OG 数据全页输出

### ★9. 移动端与视觉质量的具体项
- 移动菜单 CSS 必须**作用域限定在 header nav**——*"Fail QA when a bare `nav` selector causes breadcrumbs or another semantic navigation block to inherit fixed positioning"*（我们做面包屑时正好会踩这个坑）
- 图片容器要有**显式宽高比**，不能只靠 `width`/`height` 属性（会撑出空白面板）
- 主图主体应占画幅 ≥65% 宽、≥55% 高
- 按钮/链接在 default/hover/focus/active **四个状态**都要有足够对比度
- **所有关键文字必须在 HTML 里，不能只存在于图片中**

### ★10. 可复现构建
保留生成器、验证器、来源索引、映射表；不手工改生成后的 HTML。→ 对 Astro 项目同样适用：内容进 Content Collection，模板统一。

---

## 2. ❌ 不能照搬（照做会违规或自伤）

### 🔴 红线 1：产品页禁止联盟披露 —— **必须反向执行**
**原文规则**：*"Product detail pages must not contain an Affiliate Disclosure heading, disclosure paragraph, badge, commission statement, qualifying-purchase notice, `at no additional cost` wording..."*

**为什么不能照搬**：这条是为**品牌自营站**设的（品牌站导流到自家 Amazon 店，披露与否是品牌自己的商业选择）。
**我们是独立第三方联盟站，必须显著披露联盟关系**：
- 美国 FTC 背书指南、加拿大《竞争法》与竞争局《背书与推荐指南》都要求
- **不披露的风险远大于披露**（罚款 + 信任崩塌 + 平台账号风险）

**我们的规则**：每篇含联盟链接的页面都要有可见披露（页首或价格区附近 + 页脚全站一份）。

### 🔴 红线 2：禁止提及内容来源 —— **必须反向执行**
**原文规则**：*"never describe content... as sourced, collected, adapted, rewritten, derived, or taken from an Amazon Store, Amazon listing, marketplace page..."*

**为什么不能照搬**：对品牌站来说，承认"从 Amazon 页抄的"确实很糟。但**对我们恰恰相反**：
- **"我们分析了 8,261 条 Amazon.ca 真实评论"是我们的核心资产与差异化**，不是弱点
- E-E-A-T 要求的正是这种透明度与原创研究
- 隐瞒来源反而会被视为不可信

**我们的规则**：**主动、显著地说明研究方法与数据来源**，并标注证据等级（实测 / 评论分析 / 买家反馈 / 厂商宣称）。

> 这条与第 1 节第 6 条不冲突：**引用自己的研究是主体性表达；转述别人的页面是拼凑。** 二者要分清。

### 🟠 红线 3：Product / Offer 结构化数据 —— 需重新设计，不能照搬
**原文规则**：为精确变体输出 `Offer`（含价格、货币、可用性），`Offer.url` 指向该变体的 CTA。

**问题**：我们是**联盟站，不是卖家**。我们无法保证价格实时准确，输出 `Offer` 等于对一个我们不控制的价格做承诺——既容易过期失真，也可能不符合 Google 对商品数据结构的要求。

**我们的规则**：
| 页面类型 | Schema |
|---|---|
| 榜单/对比页 | `ItemList` + `Article` + `FAQPage` + `BreadcrumbList`；**不输出 Offer** |
| 单型号评测页 | `Product` + `Review`（**仅当评分来自我们自己的实测**）+ `FAQPage` |
| 全站 | `Organization` + `Person`(作者) |
| **全站** | **不输出 `aggregateRating`**（除我们自己的实测评分） |

### 🟠 红线 4：品牌+品类的主关键词映射 —— 不适用
**原文规则**：首页=品牌名；品类页=品牌+品类；产品页=品牌+官方型号。

**问题**：这是品牌站的打法（吃自己的品牌词）。我们的流量来自**非品牌词**（`dyson dupe hair dryer`、`best hair dryer for curly hair`、`travel hair dryer`），品牌词只占需求 2.8%。

**我们的规则**：主关键词按「需求/场景/对比」维度映射，见《SEO策略-内容计划.xlsx》。

### 🟠 红线 5：`/products/` + `/{category}/{product}/` 层级 —— 不适用
我们的内容站用扁平 `/slug/` 架构，更适合内容型站点与内链权重分配。保持不变。

### ⚪ 不适用项（无需采纳，仅记录）
- Phase 1–3 的 Amazon Store 导航发现 / ASIN 抓取 / 变体归并（我们不做品牌店重建）
- ArtemisAds 精确 ASIN 链接流程（我们用 Levanta）
- Hostinger 部署 SOP（我们用 Astro + Cloudflare/Vercel）
- Ahrefs 依赖（我们用 Semrush，同理不同工具）

---

## 3. ★ 该包的空白：AI / 大模型优化标准（AEO / GEO）

我在整个包里 grep 过 `AI / LLM / ChatGPT / Perplexity / answer engine / AEO / GEO / citation / llms.txt`——**零命中**。
这是它最大的空白，也正是你问的重点。以下是我们要补的标准。

### 3.1 大模型如何"看见"我们（机制）
大模型的答案来源主要有三类，我们要分别优化：

| 路径 | 说明 | 我们的对策 |
|---|---|---|
| **实时检索**（AI Overview、Perplexity、ChatGPT 搜索） | 现查现引，直接抓页面 | §3.2 可抽取性 + §3.4 技术可达性 |
| **训练语料** | 已被抓取的公开网页 | §3.3 独家数据 + §3.5 站外被引用 |
| **用户粘贴/工具调用** | 用户主动喂给模型 | 内容结构清晰度 |

### 3.2 可抽取性（最重要，直接决定能否被引用）

**① Answer-first：每个 H2 下第一句就是答案**
```
## How long do hair dryers last?
Across the 8,261 Canadian reviews we analysed, the median reported failure was 5.5 months.   ← 第一句就是答案
[然后才是展开解释]
```
大模型抽取答案时优先取段落首句与该标题的组合。**不要用铺垫式开头。**

**② 自包含标题**
每个 H2/H3 必须能脱离上下文独立表达完整语义。
- ❌ `## Why it matters` / `## More details` / `## Conclusion`
- ✅ `## Why durability matters more than airflow in this category`

**③ 事实密度：数字 + 单位 + 条件**
- ❌ "It's very quiet."
- ✅ "Noise: 62 dB at 30 cm, background 34 dB." 
LLM 引用具体数字的意愿远高于形容词。**每个数字都要带单位和测量条件**（这也正好和我们的实测体系对齐）。

**④ 结构化数据优先于散文**
对比数据用 `<table>`，规格用 `<dl>`，步骤用 `<ol>`。LLM 与 Google 对表格/列表的抽取准确率显著高于长段落。

**⑤ 定义式句式**
写「X 是……」「X 指……」，便于抽取实体关系，服务知识图谱与实体理解。

**⑥ 每段一个主张**
一段只讲一件事，便于按块检索命中。

### 3.3 独家数据 = AI 引用的最强磁石
LLM 与 AI Overview **优先引用「独有、可验证、含具体数字」的内容**。我们已具备 / 可具备：
| 资产 | 状态 |
|---|---|
| 8,261 条 Amazon.ca 评论分析（中位故障 5.5 个月、故障模式排序、价格带差评率） | ✅ 已完成 |
| 5 台机型台架实测数据（风速/噪音/重量/干发时间） | ⏳ 待测 |
| 12 个月耐用性追踪 | ⏳ 计划中 |

→ 这些要做成**独立、可单独引用**的页面（`/reports/...`），标题即结论，数据带表。**别人引用我们 = 我们进入语料与检索源。**

### 3.4 技术可达性（让爬虫与 LLM 都能拿到内容）
| 项 | 要求 |
|---|---|
| 内容在 HTML 里 | 正文不依赖客户端 JS 渲染；**不 lazy-load 正文与 FAQ** |
| 语义化标签 | `h1–h3` 层级正确、`table`/`dl`/`ul`/`ol` 正确使用 |
| 关键文字不进图片 | 参数、结论、FAQ 必须是可选中的文字 |
| 稳定锚点 | 每个 H2 有 `id`，便于被引用时带锚点 |
| `llms.txt` | 新增（新兴约定，成本极低）：在根目录放一份站点结构与关键内容索引 |
| `robots.txt` | **明确决定**是否允许 AI 爬虫（GPTBot / PerplexityBot / ClaudeBot / Google-Extended / CCBot）。既然我们要被引用 → **允许**，并写清楚 |
| 更新时间 | 可见 `Last updated` + `dateModified`，新鲜度影响引用倾向 |
| 加载速度 | LCP<2.5s、CLS<0.1（AI 爬虫对慢站抓取优先级低） |

### 3.5 站外被引用（LLM 的偏好来源）
AI 答案高频引用的来源包括 Wikipedia、Reddit、YouTube、以及被广泛引用的行业站。因此：

1. **Reddit 真实参与**——我们的 SERP 数据显示 reddit 在 `hair dryer like dyson` 排第 2、在 `dyson dupe hair dryer` 排第 1。**这是 AI 最爱的语料源。**建议以真人身份持续回答加拿大吹风机问题（不硬广）。
2. **独家报告换取外链**——《加拿大吹风机可靠性报告》是天然被引用素材。
3. **YouTube 布局**——SERP 里 youtube 出现频次第一；多模态内容同时服务 Google 与 LLM。
4. **被榜单/媒体提及**——主动联系美妆媒体提供数据。

### 3.6 AI 流量来了怎么转化
AI 引流的特点是**用户已经接近决策**（他是带着具体问题来的）。所以：
- 每个「答案」后紧跟**自然的下一步**：对比表 / 该场景的推荐 / 联盟链接
- 为高意图问题单独做**落地页**（如 `/learn/hair-dryer-burning-smell/`），并在其中给出「该不该修、该换哪款」
- 不要指望 AI 用户逛站——**在答案页直接完成转化路径**

### 3.7 怎么知道我们有没有被 AI 引用（测量）
| 方法 | 说明 |
|---|---|
| 手动抽查 | 定期在 ChatGPT / Perplexity / Gemini / Google AI Overview 提相关问题，记录是否引用我们 |
| Referrer 分析 | GA4 中关注 `chatgpt.com`、`perplexity.ai`、`gemini.google.com`、`copilot.microsoft.com` 来源 |
| 品牌搜索量 | GSC 里品牌词（`hair dryer lab`）搜索量增长 = 被提及的信号 |
| 内容引用监控 | 用 Google Alerts / 外链工具追踪谁引用了我们的数据 |

---

## 4. 落地改动清单（对照我们已有文档）

| # | 改动 | 目标文档 | 优先级 |
|---|---|---|---|
| 1 | 新增「每个 H2 必须含核心实体或语义变体」规则 | 内容结构标准 §0.1 | **高** |
| 2 | FAQ 改为固定 5 条、答案 ≤100 词、首句直答、**必须在 DOM 中**、schema 逐字一致 | 内容结构标准 §0.3 / §4 | **高** |
| 3 | H1 后加 90–110 词导语（与结论卡合并） | 内容结构标准 各类型骨架 | 高 |
| 4 | 新增「answer-first：每个 H2 下首句即答案」 | 内容结构标准 §0.1 | **高** |
| 5 | 新增价格显示纪律（核对日期 / 无验证价用 fallback） | 技术SEO规划 §8 | 中 |
| 6 | 明确**全站不输出 aggregateRating**（除自测评分） | 技术SEO规划 §7 | **高** |
| 7 | 新增 `llms.txt` + robots.txt 明确允许 AI 爬虫 | Astro技术栈 / 技术SEO规划 §8 | 中 |
| 8 | 新增「AI 可抽取性检查清单」（并入上线检查） | 技术SEO规划 §10 | 中 |
| 9 | 每页 H2 加稳定 `id` 锚点 | 技术SEO规划 | 中 |
| 10 | 移动菜单 CSS 作用域限定 header nav（面包屑坑） | Astro技术栈 | 中 |
| 11 | 新增测量方案（AI referrer / 手动抽查品牌词） | 技术SEO规划 §11 | 中 |
| 12 | 试用期后做独家报告页 `/reports/` | 内容计划 | 中 |

---

## 5. 执行优先级（如果只做 5 件事）

1. **Answer-first + 自包含标题**（§3.2 ①②）——对 AI 引用影响最大，且零成本，立刻可改
2. **FAQ 五条纪律 + 必须在 DOM**（§1.2）——同时服务 Google 与 LLM
3. **不输出 aggregateRating**（§2 红线 3）——避免一次性处罚风险
4. **每页 H1 后 90–110 词导语 + 每 H2 含核心实体**（§1.1、§1.3）
5. **独家数据报告页 + Reddit 参与**（§3.3、§3.5）——长期引用磁石

---

> **一句话总结**：这个包的**流程纪律值得学**，**披露与来源规则必须反过来做**，而它**没写的大模型优化**才是我们真正的差异化机会——因为我们的 8,261 条评论研究和实测体系，正是 AI 最爱引用的那类内容。
