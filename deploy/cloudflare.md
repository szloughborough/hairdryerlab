# Cloudflare Pages 部署说明

本站是**纯静态站点**（`astro build` 产出 `dist/`，63 个文件 / 2.2 MB，无服务端逻辑）。
决定使用 **Cloudflare Pages**。

> 曾经尝试过 **Workers** 路径并连续失败两次，原因见文末「为什么不用 Workers」。
> Workers 所需的 `wrangler.jsonc` 已删除，避免被 Pages 误读为 Pages Functions 配置。

---

## 项目设置

**Workers & Pages → Create application → Pages 标签 → Connect to Git** → 选仓库。

| 字段 | 值 |
|---|---|
| Production branch | `main` |
| Framework preset | `Astro` |
| **Root directory** | **`site`** |
| **Build command** | **`pnpm build`** |
| **Build output directory** | **`dist`** |

> ⚠️ **Root directory 必须填 `site`。** 仓库根目录没有 `package.json`（它在 `site/`），
> 留空会导致 Cloudflare 检测不到 Node/pnpm，构建直接失败。这是 Workers 那两次
> 失败的根因之一。

---

## 环境变量

**Settings → Environment variables**（Pages 的环境变量就是这一处；Workers 才把构建
变量单独放在 Settings → Build 里）。

| 变量 | 值 | 必要性 |
|---|---|---|
| `PNPM_VERSION` | `11.7.0` | **必须。** 见下方说明 |
| `NODE_VERSION` | `22` | 可选（`site/.nvmrc` 已写 `22`，双保险） |

### 为什么 `PNPM_VERSION` 是必需的

Cloudflare Pages **v3 构建镜像的已知限制**（官方文档原文）：

> - Detecting pnpm version detection based `pnpm-lock.yaml` file version.
> - Detecting Node.js and package managers from `package.json` -> `"engines"`.

也就是说 Pages **不会**从 `pnpm-lock.yaml` 或 `package.json` 推断 pnpm 版本，会用镜像
自带的默认版本（较旧）。而本项目的 `site/pnpm-workspace.yaml` 使用的是 **pnpm 11 的
配置语法**：

```yaml
nodeLinker: hoisted
allowBuilds: { esbuild: true, sharp: true }
verifyDepsBeforeRun: false
```

pnpm 10 不认识 `allowBuilds` / `verifyDepsBeforeRun`。**版本不匹配会导致依赖布局
不正确，进而构建报 `Cannot find module 'html-escaper'`** —— 这个错误本项目已经踩过
一次（见 `site/pnpm-workspace.yaml` 顶部说明）。

**所以务必显式设置 `PNPM_VERSION=11.7.0`。**

---

## 不需要任何密钥

联盟链接由 `pnpm affiliate:sync` **在本地**拉取，结果写入
`site/src/data/affiliate-links.mjs` **并已入库**。因此 Pages 的构建环境
**不需要配置任何 API 密钥** —— 这是刻意设计，避免凭据进入 CI。

改动联盟链接后：本地重跑 `pnpm affiliate:sync`，提交生成的文件即可。

---

## 成功标志

构建日志里应出现：

```
Detected the following tools from environment: nodejs@22.x, pnpm@11.7.0
...
45 page(s) built
Complete!
```

产物应有 63 个文件，包含 `index.html`、`404.html`、`robots.txt`、`sitemap-index.xml`、
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

1. 域名 `hairdryerlab.ca` 的 DNS 必须托管在 Cloudflare（先在 Cloudflare 添加站点、
   把 nameserver 改过去）
2. Pages 项目 → **Custom domains** → 添加 `hairdryerlab.ca` 与 `www.hairdryerlab.ca`
3. `www` 建议用 **Redirect Rule 301** 指到裸域，避免两个 host 各自被 Google 索引

---

## 排查顺序

1. **日志里 `Detected the following tools from environment:` 是否非空**
   —— 空 = Root directory 没设成 `site`
2. **日志里有没有 `pnpm build` 这一步** —— 没有 = Build command 没填
3. **`PNPM_VERSION` 是否为 `11.7.0`** —— 不设会用旧版 pnpm，报模块找不到
4. **Build output directory 是否为 `dist`**

---

## 为什么不用 Workers

两次 Workers 部署均失败，日志：

```
Cloning repository...
No build output detected to cache. Skipping.
No dependencies detected to cache. Skipping.
Detected the following tools from environment:        ← 空的
Executing user deploy command: npx wrangler deploy
✘ Could not detect a directory containing static files
```

三个原因：

| # | 原因 | 说明 |
|---|---|---|
| 1 | Root directory 未指向 `site` | 工具检测为空即为证据 |
| 2 | Build command 为空 | 从未执行 `pnpm build`，不存在 `dist/` |
| 3 | 缺 Wrangler 配置 | `wrangler deploy` 默认找 Worker 脚本，纯静态站必须声明 `assets.directory` |

第 3 项的配置为（若日后要回到 Workers，把这段存成 `site/wrangler.jsonc`）：

```jsonc
{
  "$schema": "node_modules/wrangler/config-schema.json",
  "name": "hairdryerlab",
  "compatibility_date": "2026-10-03",
  "assets": {
    "directory": "./dist",
    "not_found_handling": "404-page",
    "html_handling": "auto-trailing-slash"
  }
}
```

另有两条 Workers 特有的坑，Pages 不存在：

- **Worker 名称必须与 `wrangler.jsonc` 的 `name` 一致**，否则构建失败（官方原文：
  "the Worker name in the Cloudflare dashboard must match the `name` in the Wrangler
  configuration file in the specified root directory, or the build will fail."）
- Workers 的构建变量在 **Settings → Build → Build Variables and Secrets**，
  而不是 **Settings → Variables & Secrets**（后者是运行时变量，构建阶段读不到）

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
