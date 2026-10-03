# Hair Dryer Lab

面向加拿大市场的吹风机评测站。内容建立在 **8,261 条已验证 Amazon.ca 评测的编码分析**
与 listing 数据之上，不编造实测数值。站点用 Astro 构建为纯静态产物。

- 生产域名：`https://hairdryerlab.ca`（在 `site/src/data/site.ts` 的 `SITE_URL` 配置）
- 语言：`en-CA`
- 产出：45 个页面 / 44 篇文章

---

## 目录结构

```
site/                    Astro 站点（部署单元）
  src/
    components/          28 个 §55 品牌组件
    content/             由 deliverables/drafts 同步生成的集合（已入库）
    data/                站点配置、商品数据、联盟链接
    layouts/             Base / Article
    pages/               路由（[...slug].astro 生成全部内容页）
    plugins/             rehype 插件（联盟链接、品牌组件）
    styles/              global.css（品牌 token）+ fonts.css（自托管字体）
  public/                静态资源（品牌图、字体、robots 等）
deliverables/
  drafts/                ★ 44 篇文章的**唯一真源**（编辑这里，不是 site/src/content）
  *.md                   品牌规范、内容标准、SEO 规划等
_scripts/                构建与检查脚本（Python）
```

---

## 本地开发

```bash
cd site
pnpm install
pnpm dev            # http://localhost:4321
```

### 内容工作流（重要）

**文章真源是 `deliverables/drafts/*.mdx`，不是 `site/src/content/`。**

`site/src/content/` 是 `_scripts/sync_content.py` 生成的副本。改完草稿必须同步：

```bash
python _scripts/sync_content.py      # drafts → site/src/content
cd site && pnpm build
```

> Cloudflare 构建**不会**运行这个同步（构建镜像里没有我们的 Python 环境）。
> 所以**提交前必须同步**，否则线上是旧内容。

### 常用脚本

```bash
cd site
pnpm build                 # 生产构建
pnpm build:strict          # 联盟链接未解析即中止（上线前跑）
pnpm affiliate:sync        # 重新拉取联盟链接（需要 site/.env）
python _scripts/run_compliance_all.py   # 全量文章合规检查
python _scripts/check_links.py          # 死链扫描
python _scripts/launch_audit.py         # 上线就绪审计
```

---

## 部署到 Cloudflare

> **部署步骤与排错见 [deploy/cloudflare.md](deploy/cloudflare.md)。**
> 走 Cloudflare **Workers** 路径 —— Dashboard 的 `Create application` 已不再提供
> Pages 标签（入口合并到 Workers 的 Connect to Git），因此 Workers 是唯一可用路径。

### 架构说明：构建期不需要任何密钥

联盟链接由 `pnpm affiliate:sync` **在本地**拉取，结果写入
`site/src/data/affiliate-links.mjs` 并入库。因此 **Cloudflare 的构建环境不需要
配置任何 API 密钥** —— 这是刻意的设计，避免密钥进入 CI。

改动联盟链接后需要本地重跑 `pnpm affiliate:sync` 并提交生成的文件。

### 项目设置：什么都不用填

**直接 Retry deployment 即可。** 不需要 Root directory、不需要 Build command、
不需要构建变量。

原因：仓库**根目录**放了 `wrangler.jsonc`，声明 `assets.directory = ./site/dist`，
而 **`site/dist` 已提交到仓库**。Cloudflare 的默认部署命令 `npx wrangler deploy`
在仓库根执行时会读到它，直接上传已构建好的静态文件。

> 详情、取舍与排错见 **[deploy/cloudflare.md](deploy/cloudflare.md)**。

> ⚠️ **唯一的硬性要求**：Worker 名必须等于两个 `wrangler.jsonc` 里的 `name`
> （当前 `hairdryerlab`）。Cloudflare 官方原文：the Worker name in the dashboard
> must match the `name` in the Wrangler configuration file, **or the build will fail**。

### 改内容的流程

因为产物已提交，**改完内容必须重新构建并提交**，否则线上是旧版本：

```bash
node _scripts/deploy_prepare.mjs     # 同步草稿 + 构建 + 暂存产物
git commit -m "content: ..." && git push
```
### 绑定域名

1. 在 Cloudflare 添加 `hairdryerlab.ca` 站点（若尚未添加），让 DNS 托管在 Cloudflare
2. Worker → **Settings → Domains & Routes → Add custom domain** →
   `hairdryerlab.ca`，再加 `www.hairdryerlab.ca`
3. `www` 建议用 Cloudflare 的 **Redirect Rule 301** 到裸域，避免两个 host 各自被索引

### 部署后要做的三件事

1. **验证文件可达**：`/robots.txt`、`/sitemap-index.xml`、`/llms.txt`
   （`llms.txt` 由 `site/src/pages/llms.txt.ts` 在构建时从内容集合生成）
2. **站长工具**：Google Search Console 与 Bing Webmaster 的验证 meta 已注入全站，
   在各自后台提交 `https://hairdryerlab.ca/sitemap-index.xml`
3. **分析工具**：GA4 与 Microsoft Clarity 已注入，只在生产构建加载

---

## 环境变量

`site/.env`（**不入库**，模板见 `site/.env.example`）用于本地拉取联盟链接：

| 键 | 用途 |
|---|---|
| `LEVANTA_API_KEY` | Levanta API 凭据 |
| `PARTNERBOOST_TOKEN` | PartnerBoost API 凭据 |
| `ARTEMIS_API_KEY` | ArtemisAds API 凭据 |
| `AMAZON_ASSOCIATE_TAG` | Amazon Associates tag（兜底链接用） |

> ⚠️ **这三个密钥出现在过本项目的对话记录里，建议轮换一次。**
>
> `AMAZON_ASSOCIATE_TAG` 是半公开的（它出现在每个联盟链接的 `tag=` 参数里），
> 但它同时写死在 `site/src/data/affiliate-products.mjs` 作为兜底默认值，
> 可用环境变量覆盖。

---

## 品牌规范

**所有站点改动必须遵循 `deliverables/品牌规范-HairDryerLab-v1.0.md`。**

落地情况与逐条对照见 `deliverables/品牌规范落地对照表.md`。

几条硬性规则：

- **禁止数字总分**（不得 `9.4/10`、`94%`、`4.8/5`、`WINNER`、`#1`）。用分类结论
  （Excellent / Very Good / Good / Fair / Limited）
- **字数价格一律用约数**（`about C$100`，不写 `C$99.99`）—— Amazon Associates
  要求展示的价格必须是当前价，我们持有的是历史观察值，故只展示约数
- **单位统一**：`min:sec` / `dB @ 1 m` / `g` / `°C` / `m` / `W`
- **证据标注原样使用英文**：`Measured` / `Review analysis` / `Amazon.ca data` /
  `Buyer feedback` / `Manufacturer claim`
- **未实测就写未实测**。台架测试尚未开始，凡涉及实测值的模块一律写
  `Not yet tested`，不得估算
- 每篇文章提交前跑 `python _scripts/run_compliance_all.py`

---

## 已知的上线待办

- [ ] `editorial@hairdryerlab.ca` 邮箱必须在域名邮箱服务商创建
      （出现于 12 个页面、26 个联系链接，且是 Privacy / Terms 里的法定联系方式）
- [ ] 决定 Microsoft Clarity 的同意方案（会话录制在魁北克 Law 25 下属非必要 cookie；
      `site/src/components/Analytics.astro` 已预留 `CONSENT_GATE` 开关）
- [ ] Amazon Associates 账号需在 180 天内产生首笔合格销售
- [ ] 台架实测数据（Lab Test Card 目前全部显示 `Not yet tested`）
- [ ] 自有产品摄影（当前 215 张商品图全部直链 Amazon CDN）
