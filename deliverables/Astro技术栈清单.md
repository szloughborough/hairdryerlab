# Astro 技术栈清单

> 站点：加拿大吹风机决策站（内容型 SEO 联盟站）。技术目标：**静态优先、极致性能、结构化数据可控、内容以 Markdown 管理**。

## 核心选型

| 层 | 选型 | 理由 |
|---|---|---|
| 框架 | **Astro 5.x**（`output: 'static'` SSG） | 内容站零 JS 开销，Core Web Vitals 天然优秀 |
| 内容 | **Content Collections v2 + Zod** | frontmatter 强校验（标题/关键词/类型/schema），防内容质量漂移 |
| 格式 | **MDX** | 能在文章里放对比表、评分卡等组件 |
| 样式 | Tailwind CSS | 快速出设计系统 |
| 部署 | Cloudflare Pages（或 Vercel） | 边缘分发 + 免费额度 + 自动 CI/CD |
| 图片 | Astro Assets + sharp → WebP/AVIF | 评测图多，必须懒加载 + 现代格式 |
| 分析 | GA4 + Google Search Console + Bing Webmaster + Microsoft Clarity | GA4 流量、GSC 排名、Microsoft Clarity 隐私友好 |

## 必须装的 Astro 集成

```bash
npm install @astrojs/sitemap @astrojs/mdx @astrojs/rss
```

- `@astrojs/sitemap` —— 自动生成 sitemap.xml，提交 GSC
- `@astrojs/mdx` —— 文章用 MDX 写对比表/评分组件
- `@astrojs/rss` ——（可选）给 Google Discover/订阅

## 目录结构

```
src/
  content/
    best/            # 榜单页 → 集合 'best'
    reviews/         # 评测页 → 集合 'reviews'
    compare/         # 对比页 → 集合 'compare'
    for/             # 需求指南 → 集合 'for'
    learn/           # 科普 → 集合 'learn'
    ca/              # 加拿大本地化 → 集合 'ca'
  components/
    Schema.astro     # JSON-LD 统一输出
    ProductCard.astro
    CompareTable.astro
    RatingBadge.astro
    AffiliateCTA.astro
    FAQ.astro
  layouts/
    Article.astro    # 文章布局（含 SEO head + 内链）
  pages/
    [...slug].astro  # 集合路由
```

## Content Collection 统一 frontmatter（Zod schema）

```ts
// src/content/config.ts 核心字段
{
  type: 'best' | 'review' | 'compare' | 'for' | 'learn' | 'ca',
  title: string,            // 页面 Title
  h1: string,               // 页面 H1
  description: string,      // meta description (150-160 字符)
  slug: string,             // URL
  primaryKeyword: string,   // 首要关键词
  secondaryKeywords: string[],  // 次关键词（来自内容计划映射）
  intent: 'commercial'|'informational'|'transactional'|'comparison',
  priority: 1|2|3,          // T1/T2/T3
  schema: 'ItemList'|'Product'|'Review'|'Article'|'FAQPage'|'HowTo',
  author: string,
  published: string,        // ISO 日期（首版）
  updated: string,          // 更新日期（常青更新，显示给用户+Google）
  canonical: string,
  draft: boolean,
  // 评测/榜单专属：
  products?: { name, brand, priceCAD, rating, asin, affiliateUrl }[],
  faq?: { q, a }[],
}
```

## SEO 关键实现

1. **Head/SEO 组件**：`title` / `meta description` / `canonical` / `og:` / `twitter:` / `hreflang`（法语版预留）
2. **标题锚点（必须）**：配置 `rehype-slug` + `rehype-autolink-headings`，让每个 H2/H3 自动生成稳定 `id`。
   —— AI 引用我们的内容时会带锚点定位到具体段落，无名锚点会丢失引用精度。
   ```js
   // astro.config.mjs
   import rehypeSlug from 'rehype-slug';
   import rehypeAutolink from 'rehype-autolink-headings';
   export default defineConfig({
     markdown: { rehypePlugins: [rehypeSlug, [rehypeAutolink, { behavior: 'wrap' }]] },
   });
   ```
3. **目录（TOC）**：从 H2 自动生成，长文必备（榜单/指南页）
4. **JSON-LD**：`Schema.astro` 按 frontmatter 的 `schema` 字段输出
   - 榜单/对比/品牌枢纽 → `ItemList` + `Article` + `FAQPage`
   - 单型号评测 → `Product` + `Review`（**仅当评分来自我们自己实测**）
   - 需求/科普 → `Article` + `FAQPage`
   - 数据报告 → `Article` + `Dataset`
   - 全站 → `Organization` / `Person`(作者) + `BreadcrumbList`
   - ⚠️ **不输出 `Offer`、不输出 `aggregateRating`**
5. **robots.txt** + 自动 sitemap + GSC 提交；**明确允许 AI 爬虫**（GPTBot / PerplexityBot / ClaudeBot / Google-Extended / CCBot）
6. **`llms.txt`**：根目录提供站点结构与关键内容索引
7. **canonical 唯一**、无重复参数页
8. **内链**：面包屑 + `相关阅读` 模块（由 frontmatter 指定 `related` 字段）
9. **FAQ 必须在 DOM**：折叠组件要服务端渲染内容，禁止点击后才 fetch
10. **性能红线**：LCP < 2.5s、CLS < 0.1（图片懒加载 + 显式宽高 + font-display: swap）

## 内容生产工作流

```
内容计划(xlsx) → 按《内容结构标准.md》写 MDX(frontmatter) → 构建 → 上线 → GSC 提交 → 追踪排名
```

> 以后每篇文章都按《内容结构标准.md》的固定骨架写，frontmatter 按上面 schema 填，类型与结构一一对应。
