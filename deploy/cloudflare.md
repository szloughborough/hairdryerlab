# Cloudflare 部署说明

本站是**纯静态站点**（`astro build` 产出 `dist/`）。Cloudflare 上有两条可用路径，
下面都写了。**先读「当前遇到的问题」再选。**

---

## 当前遇到的问题（2026-10-03）

Cloudflare 构建日志：

```
Cloning repository...
No build output detected to cache. Skipping.
Executing user deploy command: npx wrangler deploy
✘ [ERROR] Could not detect a directory containing static files
Failed: error occurred while running deploy command
```

**两个原因叠加：**

1. **没有配置构建命令** —— 日志里完全没有 `pnpm build` 这一步，克隆完就直接部署，
   所以根本不存在 `dist/`。
2. **项目类型是 Workers** —— `wrangler deploy` 默认要找一个 Worker 脚本（`main`）。
   本站没有 Worker 脚本，必须用 `assets.directory` 指明静态文件位置。
   缺这个配置就会报 `Could not detect a directory containing static files`。

---

## 路径 A：继续用 Workers（改动最小，推荐）

你现在的项目已经是 Workers 且 Git 已连好。补两处即可。

### 1. 仓库侧（已完成）

`site/wrangler.jsonc` 已加好，声明了静态资源目录：

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

> ⚠️ **`name` 必须与 Cloudflare 上已有的 Worker 名称一致**，否则 wrangler 会新建一个
> Worker 而不是更新现有的。若你的项目名不是 `hairdryerlab`，请改这一行。

### 2. Cloudflare 侧：在构建配置里补上「构建命令」

进入 Worker → **Settings** → **Build**，确认这三项：

| 配置项 | 值 |
|---|---|
| **Root directory** | **`site`** |
| **Build command** | **`pnpm build`** ← 这是当前缺失的一项 |
| **Deploy command** | `npx wrangler deploy`（保持默认，不用改） |

再在 **Settings → Variables and Secrets** 加一条环境变量：

| 名称 | 值 |
|---|---|
| `NODE_VERSION` | `22` |

然后 **Retry deployment**。

**成功标志**：构建日志里出现

```
45 page(s) built
Complete!
```

---

## 路径 B：改用 Cloudflare Pages（更省事，但需新建项目）

Pages 是专为静态站点设计的，**不需要 `wrangler.jsonc`**，也没有 Worker 名称要匹配。

**Workers & Pages → Create → Pages 标签 → Connect to Git** → 选仓库：

| 配置项 | 值 |
|---|---|
| Production branch | `main` |
| Framework preset | `Astro` |
| **Root directory** | **`site`** |
| Build command | `pnpm build` |
| Build output directory | `dist` |
| 环境变量 | `NODE_VERSION` = `22` |

**不需要任何密钥** —— 联盟链接是本地生成好入库的，这是刻意设计。

---

## 两条路径的取舍

| | 路径 A（Workers） | 路径 B（Pages） |
|---|---|---|
| 新建项目 | 不用 | 要 |
| 需要 `wrangler.jsonc` | 是（已加好） | 否 |
| 需匹配 Worker 名称 | **是**（容易搞错） | 否 |
| 配置项数量 | 3 + 1 环境变量 | 5 |
| 静态站点适配 | 支持 | **专为此设计** |

**建议先试路径 A**（改动最小，配置已就绪）。若 `name` 匹配或根目录仍出问题，
再走路径 B —— Pages 的界面有明确的「Build output directory」字段，更不容易填错。

---

## 部署后必须验证的三个文件

```
https://hairdryerlab.ca/robots.txt
https://hairdryerlab.ca/sitemap-index.xml
https://hairdryerlab.ca/llms.txt
```

`llms.txt` 由 `site/src/pages/llms.txt.ts` 在构建时从内容集合生成，列出全部 46 个
真实页面链接供 AI 爬虫使用。**它曾经是手写文件、URL 停留在旧分类法**，
上线后会让爬虫拿到一整页 404，现已改为生成式。

---

## 绑定域名

1. 域名 `hairdryerlab.ca` 的 DNS 必须托管在 Cloudflare（先添加站点、改 nameserver）
2. Pages 项目 / Worker → **Custom domains** → 添加 `hairdryerlab.ca` 与 `www.hairdryerlab.ca`
3. `www` 建议用 **Redirect Rule 301** 指到裸域，避免两个 host 各自被 Google 索引

---

## 构建失败的排查顺序

1. **Root directory 是不是 `site`** —— 填错会报找不到 `package.json`
2. **Build command 是否填了 `pnpm build`** —— 空着就会像 2026-10-03 那次直接跳到部署
3. **`NODE_VERSION` 是不是 22** —— Astro 5 要求 `>=20.3.0`
4. **Workers 路径下 `wrangler.jsonc` 的 `name` 是否匹配** —— 不匹配会新建 Worker

---

## 本地复现 Cloudflare 构建

Cloudflare 做的是「全新克隆 → 安装 → 构建」。本地可以完全复现：

```bash
git clone https://github.com/szloughborough/hairdryerlab.git _clonetest
cd _clonetest/site
pnpm install
pnpm build          # 应输出 45 page(s) built / Complete!
```

> **这一步不是可选的。** 本项目踩过一个只在干净环境暴露的坑：`pnpm 10+` 不再从
> `.npmrc` 读取项目级设置，导致全新安装的 `node_modules` 布局与本地不一致，
> 构建报 `Cannot find module 'html-escaper'`。本地因为 `node_modules` 是旧版 pnpm
> 装的，一直没暴露。修复见 `site/pnpm-workspace.yaml` 顶部的说明。
>
> 教训：**验证必须用干净克隆，不能用开发的本地目录。**
