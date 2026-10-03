# Cloudflare 部署说明

本站是**纯静态站点**（`astro build` 产出 `dist/`，110 个文件 / 2.2 MB，无 Worker 脚本）。

**结论：走 Cloudflare Workers 路径。**

> 原计划用 Cloudflare Pages，但 **Pages 已从创建流程中移除** —— Dashboard 里点
> `Create application` 不再有 Pages 标签，直接进入 Connect to Git（即 Workers）。
> Pages 文档仍在，入口已合并。下面的配置按 Workers 写。

---

## 一、Dashboard：项目设置

进入 Worker → **Settings → Build**（注意是 **Build**，不是「Builds」）

| 字段 | 设为 | 说明 |
|---|---|---|
| **Root directory** | `site` | 官方定义：「defines where the build command will be run」 |
| **Build command** | `pnpm build` | 官方标注 Optional，但静态站必需 |
| **Deploy command** | `npx wrangler deploy` | 保持默认 |
| Git branch | `main` | |

> ⚠️ **Root directory 是最容易漏的一项。** 仓库根目录没有 `package.json`（它在 `site/`）。
> 留空的后果：Cloudflare 检测不到 Node/pnpm，日志里这一行为空 ——
> `Detected the following tools from environment:`
> 然后直接跳到 `wrangler deploy` 并失败。**这一行是否非空，是最快的诊断依据。**

## 二、Dashboard：构建变量

**Settings → Build → Build Variables and Secrets**

> ⚠️ 是 **Settings → Build** 里的这一项，**不是** Settings → Variables & Secrets
> （后者是运行时变量，构建阶段读不到）。

| 变量 | 值 | 必要性 |
|---|---|---|
| `PNPM_VERSION` | `11.7.0` | **必须**，见下 |
| `NODE_VERSION` | `22` | 可选（`site/.nvmrc` 已写 22） |

### 为什么 `PNPM_VERSION` 必须设

Workers 构建镜像的**默认 pnpm 是 10.11.1**（官方 build image 文档列出的默认版本）。
而本项目的 `site/pnpm-workspace.yaml` 用的是 **pnpm 11 的配置语法**：

```yaml
nodeLinker: hoisted
allowBuilds: { esbuild: true, sharp: true }
verifyDepsBeforeRun: false
```

pnpm 10 不认识 `allowBuilds` / `verifyDepsBeforeRun`。版本不匹配会导致依赖布局不正确，
构建报 `Cannot find module 'html-escaper'` —— 这个错误本项目已经踩过一次，
详见 `site/pnpm-workspace.yaml` 顶部说明。

## 三、⚠️ Worker 名称必须与 wrangler 配置一致

官方原文（[Workers Builds 文档](https://developers.cloudflare.com/workers/ci-cd/builds/)）：

> When connecting a repository to a Workers project, **the Worker name in the
> Cloudflare dashboard must match the `name` in the Wrangler configuration file
> in the specified root directory, or the build will fail.**

`site/wrangler.jsonc` 里写的是 `"name": "hairdryerlab"`。

- Dashboard 上的 Worker 名**就是** `hairdryerlab` → 无需处理
- **不是**（如 `hairdryer-lab`、`hairdryerlab-site`）→ 二选一：
  - 改 `site/wrangler.jsonc` 的 `name` 那一行（**推荐**，比在 Dashboard 改名安全）
  - 或在 Dashboard 把 Worker 改名

## 四、`wrangler.jsonc` 为什么必需

`wrangler deploy` 默认要找一个 Worker 脚本（`main`）。本站是纯静态站点，没有 Worker
脚本，必须用 `assets.directory` 指明静态文件位置。缺这个文件就报：

```
✘ [ERROR] Could not detect a directory containing static files (e.g. html, css and js)
```

配置内容：

```jsonc
{
  "name": "hairdryerlab",
  "compatibility_date": "2026-10-03",
  "assets": {
    "directory": "./dist",
    "not_found_handling": "404-page",
    "html_handling": "auto-trailing-slash"
  }
}
```

`not_found_handling: "404-page"` 让未匹配路径返回我们自己的 `dist/404.html`；
`html_handling: "auto-trailing-slash"` 保证 `/foo` 与 `/foo/` 都指向 `foo/index.html`。

> 官方文档另提到可以用部署命令代替配置文件：
> `npx wrangler deploy --assets ./dist`
> 但配置文件的写法更明确，且能同时声明 404 与尾斜杠行为，故采用配置文件。

## 五、不需要任何密钥

联盟链接由 `pnpm affiliate:sync` **在本地**拉取，结果写入
`site/src/data/affiliate-links.mjs` **并已入库**。因此构建环境**不需要配置
任何 API 密钥** —— 这是刻意设计，避免凭据进入 CI。

改动联盟链接后：本地重跑 `pnpm affiliate:sync`，提交生成的文件。

---

## 成功标志

构建日志应出现：

```
Detected the following tools from environment: nodejs@22.x, pnpm@11.7.0
...
45 page(s) built
Complete!
```

产物 110 个文件，含 `index.html`、`404.html`、`robots.txt`、`sitemap-index.xml`、
`llms.txt`、`_astro/`、`fonts/`。

---

## 部署后必须验证的三个文件

```
https://hairdryerlab.ca/robots.txt
https://hairdryerlab.ca/sitemap-index.xml
https://hairdryerlab.ca/llms.txt
```

`llms.txt` 由 `site/src/pages/llms.txt.ts` 在**构建时**从内容集合生成，列出 46 个真实
页面链接供 AI 爬虫使用。它原本是手写文件、URL 停留在旧分类法，上线后会让爬虫拿到
一整页 404，现已改为生成式。

---

## 绑定域名

1. 域名 `hairdryerlab.ca` 的 DNS 必须托管在 Cloudflare（先添加站点、改 nameserver）
2. Worker → **Settings → Domains & Routes** → **Add custom domain** →
   `hairdryerlab.ca`，再加 `www.hairdryerlab.ca`
3. `www` 建议用 **Redirect Rule 301** 指到裸域，避免两个 host 各自被 Google 索引

---

## 排查顺序（按这个顺序看，别跳）

1. **日志里 `Detected the following tools from environment:` 是否非空**
   —— 空 = Root directory 没设成 `site`
2. **日志里有没有 `pnpm build` 这一步** —— 没有 = Build command 没填
3. **`PNPM_VERSION` 是否为 `11.7.0`**
4. **Worker 名是否等于 `wrangler.jsonc` 的 `name`**

---

## 本地复现 Cloudflare 构建

Cloudflare 做的是「全新克隆 → 检测工具 → 安装 → 构建」。本地可完全复现：

```bash
git clone https://github.com/szloughborough/hairdryerlab.git _clonetest
cd _clonetest/site
pnpm install
pnpm build          # 应输出 45 page(s) built / Complete!
```

> **这一步不是可选的。** 本项目踩过一个只在干净环境才暴露的坑：`pnpm 10+` 不再从
> `.npmrc` 读取项目级设置，导致全新安装的 `node_modules` 布局与本地不一致，构建报
> `Cannot find module 'html-escaper'`。本地因为 `node_modules` 是旧版 pnpm 装的，
> 一直没暴露。
>
> 教训：**验证必须用干净克隆，不能用开发中的本地目录。**
