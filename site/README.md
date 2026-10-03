# Hair Dryer Lab — Astro 站点

加拿大吹风机决策站。基于 Astro 5 静态构建，内容以 MDX 管理，SEO 与 AI 可抽取性按
`../deliverables/技术SEO与信息架构规划.md` 与 `../deliverables/内容上线检查表.md` 落地。

---

## 1. 环境要求

- **Node.js ≥ 18**（本项目在 Node 24 上验证通过）
- **pnpm**（推荐；用 npm 也可，但需自行处理第 3 节的构建脚本授权）

## 2. 安装

```bash
cd site
pnpm install
```

`.npmrc` 已配置两项：

| 配置 | 原因 |
|---|---|
| `node-linker=hoisted` | 使用扁平 node_modules，避免 pnpm 默认符号链接结构在受限环境/Windows 上的问题；与 `astro.config.mjs` 中的 `preserveSymlinks` 设置一致 |
| `enable-pre-post-scripts=true` | 允许安装脚本运行 |

## 3. 如果安装提示 `Ignored build scripts: esbuild`

pnpm 10+ 默认拦截依赖的构建脚本。**esbuild 必须放行**，否则构建会失败（它需要准备原生二进制）：

```bash
pnpm approve-builds      # 交互式勾选 esbuild（以及 sharp）
pnpm install
```

> `package.json` 里已声明 `pnpm.onlyBuiltDependencies: ["esbuild","sharp"]`，
> 但不同 pnpm 版本对该字段的支持不一致，所以上面这条命令是最可靠的兜底。

## 4. 开发与构建

```bash
pnpm dev        # 本地开发服务器，默认 http://localhost:4321
pnpm build      # 构建到 dist/
pnpm preview    # 预览 dist/ 构建产物
```

---

## 5. 目录结构

```
site/
├── astro.config.mjs          # Astro 配置（标题锚点、sitemap、preserveSymlinks）
├── .npmrc                    # pnpm 安装策略
├── public/
│   ├── robots.txt            # 明确允许 5 个 AI 爬虫（GPTBot/PerplexityBot/ClaudeBot/Google-Extended/CCBot）
│   ├── llms.txt              # 给大模型的站点索引
│   ├── favicon.svg
│   └── og-default.svg
└── src/
    ├── content/
    │   ├── config.ts         # 6 个内容集合的统一 Zod schema
    │   ├── best/             # 榜单页
    │   ├── review/           # 评测页
    │   ├── compare/          # 对比页
    │   ├── for/              # 需求指南
    │   ├── learn/            # 科普 / 信任页
    │   └── ca/               # 加拿大本地化
    ├── data/
    │   ├── site.ts           # 站点配置 + Header 导航 + Footer 五列 + Pillar 映射
    │   └── products.ts       # ★ 产品数据（含图片 URL）—— 单一数据源
    ├── layouts/
    │   ├── Base.astro        # HTML 骨架 + head + Header/Footer
    │   └── Article.astro     # 文章布局：H1、披露、TOC、产品图卡、JSON-LD、署名
    ├── components/
    │   ├── Seo.astro         # title/description/canonical/OG/Twitter
    │   ├── JsonLd.astro      # 结构化数据（不输出 Offer / aggregateRating）
    │   ├── Header.astro / Footer.astro / Breadcrumbs.astro
    │   ├── Toc.astro         # 由 H2 自动生成目录
    │   ├── ProductPicks.astro# 榜首横排（含产品图）
    │   ├── ProductPick.astro # 单个产品卡
    │   ├── Faq.astro         # 可选：<details> 折叠，内容仍在 DOM
    │   ├── EvidenceLabel.astro # 证据等级标签
    │   └── AffiliateDisclosure.astro
    ├── pages/
    │   ├── index.astro       # 首页（含 Organization/WebSite JSON-LD）
    │   ├── [...slug].astro   # 内容集合动态路由
    │   └── 404.astro
    └── styles/global.css
```

---

## 6. 写文章的工作流

### 6.1 在 `../deliverables/drafts/` 里写 MDX

frontmatter 遵循 `src/content/config.ts` 的 schema。**正文不要写 `# H1`** —— H1 由
`Article.astro` 从 frontmatter 的 `h1` 字段渲染，保证全站恰好一个 H1。

### 6.2 同步到站点内容目录

```bash
python ../_scripts/sync_content.py
```

该脚本自动完成三件事：

1. 按 frontmatter 的 `type` 字段决定放入哪个集合目录（`best→best/`、`learn→learn/` …）
2. **删除正文里的 `# H1`**（改由布局渲染）
3. **把 HTML 注释 `<!-- -->` 转成 MDX 注释 `{/* */}`**（MDX 不支持 HTML 注释，否则编译报错）
4. 跳过 `draft: true` 的文件（避免与正式版同 slug 冲突）

### 6.3 发布前跑合规检查

```bash
python ../_scripts/check_article.py ../deliverables/drafts/<文章>.mdx
```

按**页面类型**应用不同规则（商业页 / 指南页 / 科普信任页），检查项见
`../deliverables/内容上线检查表.md`。

### 6.4 ★ 联盟链接：占位符 → 真实推广链接

正文里写的是字面占位符 `{{affiliate_url_xxx}}`。构建时由 rehype 插件
（`src/plugins/rehype-affiliate-links.mjs`）替换成真实链接；frontmatter 的
`affiliateUrl` 由 `ProductPick.astro` 经 `src/data/affiliate.mjs` 解析。

**三步流程：**

```bash
# 1) 填入三家网络的 API 凭据（只需一次）
#    编辑 site/.env，变量清单见 site/.env.example

# 2) 调 API 生成链接，写入 src/data/affiliate-links.mjs
python ../_scripts/sync_affiliate_links.py

# 3) 上线前用严格模式构建：仍有未解析的占位符就直接失败
pnpm build:strict
```

**为什么占位符不会泄漏到线上：**
`pnpm build` 默认把未解析的占位符渲染成不可点击的 `#affiliate-pending-*` 锚点，
并在控制台打印未解析清单；`pnpm build:strict` 则直接构建失败。两种模式都保证
HTML 里不会出现 `{{affiliate_url_*}}` 或它的百分号编码形式。

**新增产品：**
1. 在 `src/data/products.ts` 加产品记录；
2. 在 `src/data/affiliate-products.mjs` 的 `AFFILIATE_PRODUCTS` 加一行
   （`token` / `asin` / `label` / `providers`）；
3. 正文即可使用 `{{affiliate_url_<你的 token>}}`；
4. 若该产品暂时未接入任何联盟网络，加 `defer: true`，避免浪费 API 配额。

**没拿到真实凭据时如何验证链路：**
`python ../_scripts/dev/mock_affiliate_api.py` 会起一个假的联盟 API，
配合 `LEVANTA_BASE_URL=http://127.0.0.1:8799` 可完整走通
「取链接 → 落盘 → 构建替换」。**测完务必执行
`python ../_scripts/sync_affiliate_links.py --reset` 还原**，否则假链接会留在仓库里。

---

## 7. ★ 图片：现状与替换方式

### 当前状态

`src/data/products.ts` 里的 `image` 字段目前指向 **Amazon 商品主图**
（来自 SellerSprite BSR 导出，核对日期 2026-10-02），共 5 张：

| ASIN | 品牌 | 用途 |
|---|---|---|
| B0GWHF4SHD | Laifen | Laifen Air |
| B0FPMBBG2J | Laifen | Laifen SE2 |
| B0F8QH8XHV | dreame | Dreame Pocket Pro |
| B0C3M9WBQF | slopehill | Slopehill Professional Ionic |
| B09JZ18GLJ | wavytalk | Wavytalk with Diffuser |

构建产物已验证：5 张图全部渲染，alt 覆盖率 5/5。

### ⚠️ 上线前的图片合规决策

| 来源 | 风险 | 说明 |
|---|---|---|
| **Amazon 商品图**（当前） | 低–中 | Amazon Associates 对商品图有**有限授权**，但严格做法应通过 Product Advertising API 获取。直接引用图片 URL 是多数联盟站的做法 |
| **品牌官网图** | **较高** | 版权归品牌，**通常未授权第三方转载**。除非拿到品牌 press kit 或书面许可 |
| **自拍实拍图** | **零** | 长期最优解：自费购买后自拍。既是合规安全区，也是竞品无法复制的护城河 |

**建议路径**：先用 Amazon 图上线（低风险），随真实测试逐步替换为自拍图。

### 如何替换

只改一个文件 `src/data/products.ts`：把 `image` 换成新图 URL（或本地图路径
`/images/xxx.webp`，把文件放到 `public/images/`），并同步更新 `imageAlt`
（alt 必须描述画面内容，不能写 "image"）。

---

## 7.5 ★ 品牌 Logo 资产

### 源文件（不发布）

```
site/src/assets/brand-src/
  _src-mark.png      1254×1254  RGBA  符号（气流三线 + coral 测量点）
  _src-lockup.png    2172×724   RGBA  完整 lockup（符号 + HAIR DRYER LAB 字标）
```

> 源图带有 alpha 1–8 的**不可见光晕**，直接按 alpha bbox 裁切会残留大片隐形留白，
> 导致 logo 在页面上显示偏小。处理脚本已按阈值 `alpha > 8` 清除光晕后再裁切。

### 派生资产（发布到 `/brand/`）

由 `_scripts/logo_process.py` 生成，**重跑即可重新导出**：

| 文件 | 尺寸 | 用途 |
|---|---|---|
| `logo-lockup.png` | 599×64 | 页头（显示 30px 高，移动 26px）+ 页脚（24px） |
| `logo-mark.png` | 640×465 | 符号单独使用（图文/社媒） |
| `favicon.ico` | 16/32/48/64 | 兼容旧浏览器与书签 |
| `favicon-32.png` · `favicon-192.png` · `favicon-512.png` | — | 浏览器标签页 / PWA |
| `apple-touch-icon.png` | 180×180 | iOS 主屏图标 |
| `og-default.png` | 1200×630 | 社交分享图（**PNG，非 SVG**——多数平台不解析 SVG OG 图） |

### 处理原则（遵循品牌规范）

- **不改写、不重绘、不改色** —— 直接使用提供的正式 logo 文件
- **favicon 用 ice blue 圆角方底 + 原色 navy mark**：§65 允许 "navy background **or navy mark**"，
  取后者以保持 logo 原色不变；实底保证在深色浏览器标签栏下依然清晰
- 原 `favicon.svg` / `og-default.svg`（我此前手绘的占位图形）**已删除**
- 全部图片均带 `alt` + 显式 `width`/`height`（防 CLS）

### 重新导出

```bash
python ../_scripts/logo_process.py
```

---

## 8. SEO / AI 可抽取性已落地的部分

| 项 | 位置 |
|---|---|
| 每页一个 H1、一个 canonical（无 query） | `Article.astro` / `Seo.astro` |
| 标题锚点（AI 引用可定位段落） | `astro.config.mjs` 的 `rehype-slug` |
| 自动目录（H2 ≥ 3 时生成） | `Toc.astro` |
| 面包屑（可见 + BreadcrumbList） | `Breadcrumbs.astro` / `JsonLd.astro` |
| **不输出 Offer、不输出 aggregateRating** | `JsonLd.astro` 注释与实现 |
| FAQPage 与可见 FAQ 一致 | frontmatter `faq` → `JsonLd.astro` |
| 联盟披露（商业页） | `Article.astro` → `AffiliateDisclosure.astro` |
| 价格核对日期 | `products.ts` 的 `PRICE_CHECKED` |
| robots 允许 AI 爬虫 | `public/robots.txt` |
| `llms.txt` | `public/llms.txt` |
| FAQ 内容在 DOM（不依赖点击加载） | 正文 markdown 直出；`Faq.astro` 用服务端 `<details>` |
| 移动菜单 CSS 限定 header 作用域 | `global.css` 的 `.site-header nav.main-nav` |

---

## 9. 已知待办

- [ ] 首页 Pillar 卡片暂无 `id` 锚点（非内容标题，影响很小）
- [ ] 文章正文的「Quick picks」表格与布局渲染的产品图卡存在信息重复；
      后续可删掉 markdown 表格，统一由 `ProductPicks` 组件承接
- [ ] 其余 5 个 Pillar 页与 7 个信任页尚未创建（`review/compare/for/ca` 集合目前为空）
- [ ] 联盟链接仍是占位符 `{{affiliate_url_*}}`：**替换机制已就绪**，只差
      `site/.env` 里的三家网络 API 凭据。填入后运行
      `python ../_scripts/sync_affiliate_links.py` 即可。详见 §6.4
- [ ] frontmatter 的 `affiliateUrl` 目前**未被任何页面渲染**：6 篇商业页都写了
      `products[]`，但 `ProductPick.astro`（逐产品 CTA 卡）没有任何地方引用，
      只有 `ProductPicks.astro`（横排卡，不输出外链）在用。若要保留产品级
      CTA，需在 `Article.astro` 里引入 `ProductPick`
- [ ] `og-default.svg` 为占位图，正式上线建议换为 1200×630 PNG（部分平台不解析 SVG OG 图）

## 10. 部署

静态输出，可直接部署到任意静态托管（Cloudflare Pages / Vercel / Netlify）：

```
构建命令: pnpm build
输出目录: dist
```

部署后需：验证 GSC 属性 → 提交 `sitemap-index.xml` → 核对 canonical 域名与
`astro.config.mjs` 的 `SITE` 一致。
