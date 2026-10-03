# Cloudflare 部署说明

本站是**纯静态站点**（`astro build` 产出 `dist/`，63 个文件 / 2.2 MB，无 Worker 脚本）。
Cloudflare 上有两条路径，下面都写了。

---

## 当前遇到的问题（2026-10-03）

```
Cloning repository...
No build output detected to cache. Skipping.
No dependencies detected to cache. Skipping.
Detected the following tools from environment:        ← 空的
Executing user deploy command: npx wrangler deploy
✘ Could not detect a directory containing static files
Failed: error occurred while running deploy command
```

### 诊断

**「Detected the following tools from environment」为空是关键线索。**
如果 Root directory 正确指向 `site`，Cloudflare 会从 `site/package.json` 检测到
Node 与 pnpm，并在这里列出来。空着说明**它在仓库根目录找，那里没有 `package.json`**。

三个原因叠加：

| # | 原因 | 后果 |
|---|---|---|
| 1 | **Root directory 未设为 `site`** | 在仓库根找不到 package.json，工具检测为空 |
| 2 | **Build command 为空** | 完全没有执行 `pnpm build`，不存在 `dist/` |
| 3 | **缺少 Wrangler 配置** | `wrangler deploy` 默认找 Worker 脚本，纯静态站必须声明 `assets.directory` |

第 3 项已在仓库侧修好（`site/wrangler.jsonc`）。第 1、2 项需在 Dashboard 改。

---

## 路径 A：改用 Cloudflare Pages（推荐）

**Pages 是专为静态站点设计的**，不需要 Wrangler 配置，也**没有 Worker 名称必须
匹配的坑**（见下方路径 B 的警告）。对本站这种纯静态产物，这是最省事的一条路。

**Workers & Pages → Create application → Pages 标签 → Connect to Git** → 选仓库：

| 配置项 | 值 |
|---|---|
| Production branch | `main` |
| Framework preset | `Astro` |
| **Root directory** | **`site`** |
| **Build command** | **`pnpm build`** |
| **Build output directory** | **`dist`** |
| 环境变量 | `NODE_VERSION` = `22` |

**不需要任何密钥** —— 联盟链接在本地生成好并已入库（`site/src/data/affiliate-links.mjs`），
这是刻意设计，避免凭据进入 CI。

---

## 路径 B：继续用 Workers

你现在的项目已是 Workers 且 Git 已连好。需要在 **两个地方** 各改几项。

### B1. Dashboard：Settings → Build

> ⚠️ 注意菜单是 **Settings → Build**（不是「Builds」）。构建相关字段都在这里。

| 字段 | 设为 | 说明 |
|---|---|---|
| **Root directory** | `site` | **当前缺失项 1**。官方定义：「defines where the build command will be run」 |
| **Build command** | `pnpm build` | **当前缺失项 2**。官方标注为 Optional，但静态站必需 |
| **Deploy command** | `npx wrangler deploy` | 保持默认，不用改 |
| Git branch | `main` | 应已是 |

### B2. Dashboard：Settings → Build → Build Variables and Secrets

> ⚠️ 是 **Settings → Build** 里的「Build Variables and Secrets」，
> 不是 **Settings → Variables & Secrets**（后者是运行时变量，构建阶段读不到）。

| 变量名 | 值 | 为什么 |
|---|---|---|
| `NODE_VERSION` | `22` | Astro 5 要求 `>=20.3.0`；镜像默认可能是 24，显式指定更稳 |
| `PNPM_VERSION` | `11.7.0` | **必须设。** 镜像默认 pnpm 是 **10.11.1**，而本项目的 `pnpm-workspace.yaml` 用的是 **pnpm 11 的语法**（`allowBuilds` / `verifyDepsBeforeRun`）。pnpm 10 不认识这些键，可能报错或静默忽略后构建失败 |

### B3. ⚠️ Worker 名称必须与 Wrangler 配置一致

官方原文（[Workers Builds 文档](https://developers.cloudflare.com/workers/ci-cd/builds/)）：

> When connecting a repository to a Workers project, **the Worker name in the
> Cloudflare dashboard must match the `name` in the Wrangler configuration file
> in the specified root directory, or the build will fail.**

`site/wrangler.jsonc` 里写的是 `"name": "hairdryerlab"`。

- 若你 Dashboard 上的 Worker 名**就是** `hairdryerlab` → 无需处理
- 若**不是**（比如 `hairdryer-lab`、`hairdryerlab-site`）→ 二选一：
  - 在 Dashboard 把 Worker 改名（Settings → 名称字段）
  - 或告诉维护者实际名称，改 `wrangler.jsonc` 里那一行

### B4. Retry deployment

**成功标志**（构建日志里应出现）：

```
Detected the following tools from environment: nodejs@22, pnpm@11.7.0
...
45 page(s) built
Complete!
```

---

## 两条路径对比

| | 路径 A（Pages） | 路径 B（Workers） |
|---|---|---|
| 新建项目 | 需要 | 不用 |
| 需要 `wrangler.jsonc` | 否 | 是（已加好） |
| **Worker 名称必须匹配** | **否** | **是，否则构建失败** |
| 环境变量位置 | 常规环境变量 | **Settings → Build → Build Variables** |
| 静态站点适配 | **专为此设计** | 支持 |

**建议走路径 A。** 本站是纯静态、无服务端逻辑，Pages 的字段少一项、
且避开了名称匹配这个容易踩的坑。

---

## 部署后必须验证的三个文件

```
https://hairdryerlab.ca/robots.txt
https://hairdryerlab.ca/sitemap-index.xml
https://hairdryerlab.ca/llms.txt
```

`llms.txt` 由 `site/src/pages/llms.txt.ts` 在构建时从内容集合生成，列出 46 个真实
页面链接供 AI 爬虫使用。**它原本是手写文件、URL 停留在旧分类法**，上线后会让
爬虫拿到一整页 404，现已改为生成式。

---

## 绑定域名

1. 域名 `hairdryerlab.ca` 的 DNS 必须托管在 Cloudflare（先添加站点、改 nameserver）
2. Pages 项目 / Worker → **Custom domains** → 添加 `hairdryerlab.ca` 与 `www.hairdryerlab.ca`
3. `www` 建议用 **Redirect Rule 301** 指到裸域，避免两个 host 各自被 Google 索引

---

## 排查顺序

1. **日志里 `Detected the following tools from environment:` 是否非空**
   —— 空 = Root directory 没设成 `site`
2. **日志里有没有 `pnpm build` 这一步** —— 没有 = Build command 没填
3. **`NODE_VERSION` 是否 22**，`PNPM_VERSION` 是否 `11.7.0`
4. **Workers 路径下 Worker 名称是否等于 `wrangler.jsonc` 的 `name`**

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
> 一直没暴露。修复见 `site/pnpm-workspace.yaml` 顶部说明。
>
> 教训：**验证必须用干净克隆，不能用开发中的本地目录。**
