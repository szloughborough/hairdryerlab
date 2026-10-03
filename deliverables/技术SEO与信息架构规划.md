# 网站技术 SEO 与信息架构规划（Pillar-Cluster 蓝图）

> 本文档是全站架构的唯一权威参考。所有页面、内链、导航、结构化数据、技术配置都以本规划为准。
> 配套文档：《内容结构标准.md》（文章骨架）、《Astro技术栈清单.md》（实现）、《SEO策略-内容计划.xlsx》（关键词映射）。

---

## 1. 信息架构总览：6 个 Pillar（支柱页）+ 集群

**模型**：每个 Pillar（支柱页）是一篇覆盖一个宽主题的「基石内容」，其下挂一组 Cluster（集群页）。Pillar 链向所有集群页，集群页回链 Pillar，形成 hub-and-spoke。

### Pillar 清单（6 个基石页）

| # | Pillar | URL | 定位 | 作用 |
|---|---|---|---|---|
| P1 | 榜单支柱 | `/best-hair-dryer/` | Best Hair Dryers（全品类） | 转化引擎，吸收所有「best」流量 |
| P2 | 平替支柱 | `/best-dyson-alternatives/` | Dyson Dupes & Alternatives | **战略切口**，吃平替空白位 |
| P3 | Laifen 品牌支柱 | `/laifen/` | Laifen 全系枢纽 | 核心变现品牌 |
| P4 | Shark 品牌支柱 | `/shark/` | Shark 全系枢纽 | 高客单品牌（目标 Shark 10–15%） |
| P5 | 选购指南支柱 | `/hair-dryer-guide/` | 吹风机选购终极指南 | 信息权威基石，汇聚需求+科普集群 |
| P6 | 加拿大支柱 | `/hair-dryer-canada/` | 加拿大购买与优惠 | 本地化转化（CPC $0.37 最高） |

### 集群映射（每个页面归属一个主 Pillar，可跨 Pillar 互链）

```
P1 /best-hair-dryer/（榜单支柱）
├── /best-hair-dryer-canada/
├── /best-curly-hair/
├── /best-fine-hair/
├── /best-thick-hair/
├── /best-frizzy-hair/
├── /best-travel/
├── /best-quiet/
├── /best-diffuser/
└── /best-professional/

P2 /best-dyson-alternatives/（平替支柱）
├── /laifen-vs-dyson/
├── /shark-vs-dyson/
├── /laifen-vs-shark/
├── /laifen-vs-slopehill/
├── /dyson-vs-airwrap-dupes/
└── /is-dyson-worth-it/  ┄┄ 科普支撑页（次级归属 P5）

P3 /laifen/（Laifen 支柱）
├── /laifen-air/
├── /laifen-se-lite/
├── /laifen-se2/
├── /laifen-swift/
├── /laifen-swift-vs-se/
└── /where-to-buy-laifen-canada/  ┄┄ 次级归属 P6

P4 /shark/（Shark 支柱）
├── /shark-flexstyle/
├── /shark-speedstyle/
└── /shark-flexstyle-vs-speedstyle/

P5 /hair-dryer-guide/（选购指南支柱）
├── 需求集群（8 页）
│   ├── /hair-dryer-for-curly-hair/
│   ├── /hair-dryer-for-fine-hair/
│   ├── /hair-dryer-for-thick-hair/
│   ├── /hair-dryer-for-frizzy-hair/
│   ├── /travel-hair-dryer/
│   ├── /quiet-hair-dryer/
│   ├── /lightweight-hair-dryer/
│   └── /hair-dryer-with-diffuser/
└── 科普集群（4 页）
    ├── /ionic-vs-ceramic/
    ├── /how-many-watts/
    ├── /how-to-use-diffuser/
    └── /high-speed-dryer/

P6 /hair-dryer-canada/（加拿大支柱）
├── /where-to-buy-laifen-canada/
├── /best-hair-dryer-costco-canada/
└── /hair-dryer-sale-canada/
```

> **新增页面**（原 43 页之外补齐的 3 个基石页）：`/shark/`、`/hair-dryer-guide/`、`/hair-dryer-canada/`。补齐后共 **46 个内容页 + 1 首页 + 8 个信任页**。

---

## 2. 完整页面清单

### 2.1 首页 `/`
- 作用：全站权重分发枢纽，只链向 6 个 Pillar + 少量顶级商业页
- 结构：Hero（首屏结论性品牌口号）→ 6 个 Pillar 入口卡 → 「本周首选」3 款 → 最新评测/对比 → 信任信号（How We Test 摘要）

### 2.2 内容页（46 页）—— 见 §1 集群映射

### 2.3 信任页（8 页，E-E-A-T 必需，不抢关键词但必须有）
| URL | 内容 |
|---|---|
| `/about/` | 我们是谁、为什么可信 |
| `/how-we-test/` | **测试方法论（最重要）**：真机购买/借用、测试项、数据口径 |
| `/editorial-policy/` | 编辑独立性、如何选题、如何写缺点 |
| `/affiliate-disclosure/` | 联盟披露（全站 footer 也挂） |
| `/privacy-policy/` | 隐私（GA4 + Microsoft Clarity） |
| `/terms/` | 条款 |
| `/contact/` | 联系（真人可联系） |
| `/authors/{name}/` | 作者页（每个作者一篇，头像+履历+所写文章列表） |

---

## 3. URL 结构与命名规范

| 规则 | 规范 |
|---|---|
| 层级 | 全部扁平 `/slug/`，最多两级（`/authors/name/` 例外） |
| 命名 | 小写、连字符分词、无数字、无日期（常青可更新） |
| 目录语义 | `/best/` 榜单、`/reviews/`（模型页可扁平）、`/compare/` 对比、`/for/` 需求、`/learn/` 科普、`/ca/` 本地化 |
| 品牌页 | `/laifen/`、`/shark/` 直接做品牌枢纽（品牌即目录） |
| 对比页 | 固定 `{a}-vs-{b}/` 格式，一页一对比 |
| 法语 | `/fr/` 前缀（预留），hreflang 对应 |
| 禁止 | 参数化 URL、重复路径、`?utm=` 内链、大小写混合 |

---

## 4. 内链模型（权重流 + 转化流）

### 4.1 三种内链类型

| 类型 | 形式 | 规则 |
|---|---|---|
| **结构内链** | Header 导航 + Footer + 面包屑 | 全站一致，Pillar 可达 |
| **语境内链** | 正文自然锚文本 | 按「转化流」规则，锚文本用目标词 |
| **模块内链** | 「相关阅读」区块（3–5 条） | 由 frontmatter `related` 字段指定 |

### 4.2 权重流（Link Equity 设计）

```
Homepage ──→ 6 个 Pillar（每个首页都链）
   │
   Pillar ──→ 本集群所有页面（Pillar 正文/模块链出）
   │
   集群页 ──→ 回链所属 Pillar（面包屑 + 语境）
   │
   对比页 ══ 桥梁 ══ 连接多个 Pillar（跨支柱互链）
```

### 4.3 转化流（信息 → 商业的导流）

```
信息页(/for/ /learn/) ──内链──→ 商业页(/best/ /reviews/ /compare/)
品牌枢纽(/laifen/)     ──内链──→ 单型号评测(/laifen-air/)
单型号评测            ──内链──→ 对比页(/laifen-vs-dyson/) + 榜单(/best-dyson-alternatives/)
对比页               ──内链──→ 购买页(/where-to-buy-laifen-canada/)
```

### 4.4 内链硬规则
1. **每页至少 3 条站内内链**，锚文本用目标关键词（不堆砌、自然变化）
2. **Pillar 必须链出到本集群所有页**，集群页必须回链 Pillar（面包屑兜底）
3. **对比页是跨 Pillar 桥梁**：`/laifen-vs-dyson/` 同时内链到 P2、P3，并从 P2、P3 收到回链
4. **信息页不直接链到联盟链接**，先导到商业页再由商业页转化
5. **锚文本规则**：描述性锚文本，禁止「点击这里」「了解更多」；目标关键词占比控制在自然范围
6. 首页只链 Pillar + 顶级页，不链长尾页（集中权重）

---

## 5. Header 导航结构

### 5.1 顶部导航（5 项，移动端汉堡菜单）

```
[Logo → /]
  Best Hair Dryers   → /best-hair-dryer/        (下拉：全部 /best/ 子页)
  Dyson Dupes        → /best-dyson-alternatives/ (下拉：全部对比 + /is-dyson-worth-it/)
  Brands ▾          → Laifen → /laifen/   Shark → /shark/
                      (下拉：Laifen / Shark / dreame / slopehill)
  Buying Guide       → /hair-dryer-guide/       (下拉：需求 + 科普子页)
  Canada Deals       → /hair-dryer-sale-canada/
[搜索图标]
```

### 5.2 Header 设计原则
- **只放 Pillar 与顶级入口**，不放长尾页（权重集中）
- **下拉最多两层**：Pillar → 集群页，不做三层
- **移动端**：汉堡菜单，全部项折叠；Logo 始终可见
- 不放外部链接、不放联盟链接（Header 是导航不是变现位）

---

## 6. Footer 导航结构

### 6.1 Footer 布局（5 列 + 底栏）

```
┌─────────────┬─────────────┬─────────────┬─────────────┬─────────────┐
│ 热门榜单     │ 对比         │ 品牌         │ 指南         │ 关于我们     │
│ best-hair-dryer │ laifen-vs-dyson │ /laifen/    │ hair-dryer-guide │ /about/     │
│ best-dyson-dup │ shark-vs-dyson   │ /shark/     │ for-curly-hair   │ /how-we-test/ │
│ best-canada   │ laifen-vs-shark   │ /dreame/    │ for-fine-hair    │ /editorial/   │
│ best-diffuser │ airwrap-dupes     │ /slopehill/ │ ionic-vs-ceramic │ /authors/     │
│ hair-dryer-sale│                  │             │ travel-hair-dryer │ /contact/     │
└─────────────┴─────────────┴─────────────┴─────────────┴─────────────┘
底栏：© 2026 Hair Dryer Lab · /affiliate-disclosure/ · /privacy-policy/ · /terms/
      「我们可能通过本页联盟链接赚取佣金」
```

### 6.2 Footer 原则
- **链接 6 个 Pillar + 全部品牌枢纽 + 全部信任页**（全站每页 footer 一致 → Pillar 与信任页权重稳定）
- 联盟披露语句放底栏（全站合规）
- Footer 不放集群长尾页（除非是核心转化页）

---

## 7. 结构化数据（Schema）全站映射

> ⚠️ **我们是联盟站，不是卖家。** 因此**不输出 `Offer`**（价格不由我们控制，无法保证准确），
> 且**全站不输出 `aggregateRating`**（Google 评论摘要指南：聚合自其他网站的评分不具备资格）。

| 页面类型 | JSON-LD |
|---|---|
| 首页 | `Organization` + `WebSite`（+ SearchAction 可选） |
| Pillar 榜单页 | `ItemList` + `Article` + `FAQPage` + `BreadcrumbList` |
| 单型号评测 | `Product` + `Review`（**仅当评分来自我们自己的实测**）+ `FAQPage` + `BreadcrumbList` |
| 品牌枢纽 | `ItemList` + `Article` + `FAQPage` + `BreadcrumbList` |
| 对比页 | `ItemList` + `Article` + `FAQPage` + `BreadcrumbList` |
| 需求指南 | `Article` + `FAQPage` + `BreadcrumbList` |
| 科普页 | `Article` + `FAQPage`（步骤类 + `HowTo`）+ `BreadcrumbList` |
| 本地化购买页 | `Article` + `FAQPage` + `BreadcrumbList`（**不加 `Product`/`Offer`**） |
| 数据报告页 `/reports/` | `Article` + `Dataset`（独家数据，AI 引用磁石） |
| 作者页 | `Person` |
| 信任页 | `Article` / `WebPage` |

**硬规则：**
1. **不输出 `Offer`** —— 我们不是卖家，价格不由我们控制
2. **不输出 `aggregateRating`** —— 除非评分来自我们自己的实测（Amazon 星级只能作为可见文字引用，并注明来源）
3. **不编造** review / 评分 / 价格 / 可用性 / `priceValidUntil`
4. **FAQPage 必须与可见文字逐字一致** —— 不承诺富媒体结果，其价值在于语义与 AI 解析
5. Amazon 星级只作为**可见文字**呈现，并在同页注明「数据来自 Amazon.ca」

## 7.5 ★ AI / 大模型可抽取性（AEO/GEO）

> 详见《借鉴分析与AI搜索优化标准.md》。以下为技术要求。

| 项 | 要求 |
|---|---|
| **内容在 HTML 里** | 正文与 FAQ 不依赖客户端 JS；**不 lazy-load 正文** |
| **`llms.txt`** | 根目录提供站点结构与关键内容索引（新兴约定，成本极低） |
| **robots.txt 明确允许 AI 爬虫** | `GPTBot`、`PerplexityBot`、`ClaudeBot`、`Google-Extended`、`CCBot` 等 —— 我们要被引用，就明确允许 |
| **稳定锚点** | 每个 H2 带 `id`，便于 AI 引用时定位到具体段落 |
| **语义化标签** | `table`（对比）、`dl`（规格）、`ol`（步骤），LLM 对结构化内容抽取准确率远高于长段落 |
| **定义式句式** | 写「X 是……」，便于抽取实体关系 |
| **每段一个主张** | 便于按块检索命中 |
| **新鲜度** | 可见 `Last updated` + `dateModified` |
| **速度** | LCP<2.5s / CLS<0.1（AI 爬虫对慢站抓取优先级低） |

---

## 8. 技术 SEO 清单

| 项 | 配置 |
|---|---|
| **Sitemap.xml** | 自动生成，含全部 46 内容页 + 信任页；排除 `draft`、404、参数页；提交 GSC |
| **Robots.txt** | 允许抓取；屏蔽 `/api/`、搜索参数、管理路径；指定 sitemap 位置 |
| **Canonical** | 每页唯一，指向自身；`/laifen/` 与 `/laifen-hair-dryer/`（如有别名）用 canonical 归一 |
| **Hreflang** | 上线法语版时：`en-ca` ↔ `fr-ca` 互指 |
| **Meta** | 每页唯一 `title` + `description`（150–160 字符），禁止模板默认值 |
| **OG / Twitter** | 全页输出，用于分享（评测图做 og:image） |
| **面包屑** | 可见面包屑 + `BreadcrumbList`，路径 `Home > Pillar > 页面` |
| **Core Web Vitals** | LCP < 2.5s / INP < 200ms / CLS < 0.1（图片懒加载 + 显式宽高 + WebP/AVIF） |
| **图片 SEO** | 一手实拍图 + 压缩 WebP + 描述性 alt（含关键词）+ 显式尺寸 |
| **分页** | 榜单若超 1 屏，用分页但确保主内容在第 1 屏（尽量单页） |
| **Faceted 导航** | 不做参数化筛选页（避免重复索引） |
| **404 / 重定向** | 自定义 404；旧链接 301 到最相关页；无软 404 |
| **结构化数据验证** | 上线前用 Rich Results Test 验证每类 schema |
| **移动优先** | 全站响应式，移动端体验优先 |
| **HTTPS / 安全** | 全站 HTTPS，HSTS |

---

## 9. Title / Meta / H1 公式

| 页面 | Title 公式 | 示例 |
|---|---|---|
| Pillar 榜单 | `{主题} (2026)｜实测推荐` | `Best Hair Dryers 2026 | Tested & Ranked` |
| 单型号评测 | `{产品} Review: {钩子} (2026)` | `Laifen Air Review: 15x Ionic Dryer Tested` |
| 对比页 | `{A} vs {B}: {结论钩子} (2026)` | `Laifen vs Dyson: Which Is Worth It?` |
| 需求指南 | `{需求} Hair Dryer: 完整指南` | `Best Hair Dryer for Curly Hair (Guide)` |
| 科普页 | `{主题}: 解释 + 选购影响` | `Ionic vs Ceramic: What Actually Matters` |
| 本地化 | `{主题} (Canada)` | `Where to Buy Laifen in Canada` |

**H1 规则**：每页一个 H1，含首要关键词，与 Title 语义一致但措辞可不同（不复制粘贴）。
**Meta description**：150–160 字符，含首要关键词 + 结论性钩子，诱导点击。

---

## 10. 上线前检查清单（Launch Checklist）

### 10.1 基础 SEO
- [ ] 6 个 Pillar 全部上线且链出本集群所有页
- [ ] Header 5 项导航 + Footer 5 列 + 底栏披露 就位
- [ ] 面包屑（可见 + schema）全站生效；**移动菜单 CSS 限定 header nav 作用域，不影响面包屑**
- [ ] 每页**恰好一个 H1**、**恰好一个 canonical**（无 query/fragment）
- [ ] Title 50–60 字符、Meta 150–160 字符，全站唯一
- [ ] 每类页面 JSON-LD 正确；**全站无 `Offer`、无 `aggregateRating`**
- [ ] Sitemap + robots.txt 提交 GSC，canonical 无冲突
- [ ] 8 个信任页（尤其 `/how-we-test/`、`/about/`、`/affiliate-disclosure/`）上线
- [ ] CWV 达标（LCP/INP/CLS 三项）
- [ ] GA4 + GSC + Bing + Clarity 埋点验证
- [ ] 联盟披露全站可见（每页，不只页脚）
- [ ] 每页 ≥3 条内链、锚文本合规
- [ ] 图片：WebP + 描述性 alt + 显式宽高比容器（不用 width/height 属性撑版）
- [ ] 移动端导航与阅读体验验收

### 10.2 ★ AI 可抽取性（AEO/GEO）
- [ ] 每个 H2 自包含且含页面核心实体，**带稳定 `id` 锚点**
- [ ] 每个 H2 下**首句即答案**（answer-first），无铺垫式开头
- [ ] H1 后 90–110 词导语就位
- [ ] 每页**恰好 5 条 FAQ**，答案 ≤100 词、首句直答、**内容在 DOM 中**
- [ ] `FAQPage` JSON-LD 与可见文字逐字一致
- [ ] 所有数字带单位与测量条件（如 `62 dB（距 30 cm）`）
- [ ] 正文与 FAQ 不依赖 JS 渲染、不 lazy-load
- [ ] `llms.txt` 已部署
- [ ] robots.txt 明确允许 `GPTBot`/`PerplexityBot`/`ClaudeBot`/`Google-Extended`/`CCBot`
- [ ] 可见 `Last updated` + `dateModified` 就位
- [ ] 价格标注核对日期；无验证价用 `Check current price on Amazon`
- [ ] 独家数据有独立可引用页面（`/reports/`）

### 10.3 计数对账（借鉴流程纪律）
- [ ] 计划页数 = 实际上线页数
- [ ] H1 数 = canonical 数 = 页面数
- [ ] FAQ 覆盖页数、schema 与可见文字一致数已统计
- [ ] 内链数、断链数已统计（断链 = 0）
- [ ] **不因「页面已生成」就判定项目完成**

---

## 11. 测量（含 AI 引用追踪）

| 指标 | 来源 | 目标 |
|---|---|---|
| 自然点击/月 | GSC | M6 ≥ 2,000 |
| 关键词排名分布 | GSC / Semrush | M6 前10 ≥15 词 |
| **AI 来源访问** | GA4 referrer：`chatgpt.com` / `perplexity.ai` / `gemini.google.com` / `copilot.microsoft.com` | 从 0 起追踪 |
| **AI 引用抽查** | 定期在 ChatGPT/Perplexity/Gemini 提相关问题，记录是否引用我们 | 每月 1 次 |
| 品牌搜索量 | GSC 品牌词（`hair dryer lab`） | 持续增长 = 被提及信号 |
| 外链引用 | 外链工具 / Google Alerts | M6 引用域 ≥15 |
| 出站点击率 / 成交率 | Amazon Associates + Levanta 后台 | M6 实测校准模型 |
| 佣金收入 | 联盟后台 | M12 C$500–1,200 |

---

## 附：架构决策记录（为什么这么定）

1. **6 个 Pillar 而非更多**：Pillar 太多会稀释首页权重；6 个已覆盖「榜单/平替/两品牌/指南/本地化」全部战略面。
2. **对比页是桥梁**：`/laifen-vs-dyson/` 同时服务 P2 与 P3，靠它把「平替流量」和「品牌流量」互相导流——这是多品牌变现的关键结构。
3. **信息页（P5）与商业页（P1/P2）分离**：信息页承接长尾流量并导流，商业页承接转化，Google 判断「主题权威」更有利，且避免纯联盟站画像。
4. **加拿大单独成 Pillar**：本地化页 CPC 最高（$0.37）且是美国大站的差异化空白，值得一个基石页聚合。
5. **信任页独立于关键词体系**：`/how-we-test/` 是全站 E-E-A-T 的锚，所有评测页都链到它，是抗 HCU 的核心。

---

> **下一步**：本架构定稿后，即可按《内容结构标准.md》逐页产出。建议第一批先做 6 个 Pillar 页 + 8 个信任页（尤其 `/how-we-test/`），把骨架立起来，再填集群页。
