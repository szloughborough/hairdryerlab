# Cloudflare 部署说明

本站是**纯静态站点**（`astro build` 产出 `site/dist`，63 个文件）。

## 结论：不需要任何 Cloudflare 构建设置

**直接 `Retry deployment` 即可。** 不需要 Root directory，不需要 Build command，
不需要构建变量。

### 为什么可行

Cloudflare Workers Builds 的默认行为是：在仓库根目录执行 `npx wrangler deploy`。
本项目在**仓库根目录**放了一个 `wrangler.jsonc`：

```jsonc
{
  "name": "hairdryerlab",
  "compatibility_date": "2026-10-03",
  "assets": {
    "directory": "./site/dist",        // ← 已提交的构建产物
    "not_found_handling": "404-page",
    "html_handling": "auto-trailing-slash"
  }
}
```

于是默认的部署命令就能找到静态文件并上传。**构建产物 `site/dist` 已提交到仓库**
（63 个文件：45 个 HTML、1 个 CSS、4 个 woff2、7 个 png、2 个 xml、2 个 txt、
manifest、ico）。

### 为什么走这条路

Dashboard 里的构建设置（Root directory / Build command）在界面上不容易定位，
导致连续三次部署失败，日志都是：

```
No build output detected to cache. Skipping.
Detected the following tools from environment:        ← 空的
Executing user deploy command: npx wrangler deploy
✘ Could not detect a directory containing static files
```

把产物直接交给 wrangler，就把对「能不能找到那三个输入框」的依赖彻底去掉了。

---

## ⚠️ 唯一的硬性要求：Worker 名称必须匹配

Cloudflare 官方原文：

> the Worker name in the Cloudflare dashboard must match the `name` in the
> Wrangler configuration file in the specified root directory, **or the build
> will fail.**

两个 `wrangler.jsonc` 里写的都是 `"name": "hairdryerlab"`：

| 文件 | 何时生效 | assets 指向 |
|---|---|---|
| `wrangler.jsonc`（仓库根） | **未设 Root directory 时**（当前情况） | `./site/dist` |
| `site/wrangler.jsonc` | 若日后设 Root directory = `site` | `./dist` |

两者一致，所以**两种情况都能工作**。

**若你 Dashboard 上的 Worker 名不是 `hairdryerlab`** → 改这两个文件里的 `name`
（比在 Dashboard 改名安全，不会影响已有部署）。

---

## 改内容的流程（重要）

因为产物是提交进仓库的，**改完内容必须重新构建并提交**，否则线上还是旧版本。

已提供一条命令：

```bash
node _scripts/deploy_prepare.mjs
git commit -m "content: ..."
git push
```

它做三件事：
1. 调 `_scripts/sync_content.py` 把 `deliverables/drafts/` 同步到 `site/src/content/`
2. 构建（`pnpm build`，找不到 pnpm 时依次回退到 npx / 直接调 astro）
3. `git add -f site/dist` 并暂存其余改动

> **同步规则只有一处真源：`_scripts/sync_content.py`。**
> 曾经在 JS 里重新实现过一遍，漏了 5 条规则（跳过 `draft:true`、按 `slug` 命名、
> 删除正文 H1、把 HTML 注释转成 MDX 注释写法、先清空旧文件），结果把一篇含 HTML
> 注释的草稿同步进站点，构建报 `[@mdx-js/rollup] Unexpected character !`。
> 现在脚本直接调用原脚本，**找不到 Python 就大声失败，绝不静默降级**。
>
> 需要 Python。受限环境可用 `HDL_PYTHON` 指定解释器路径。

### 如果忘了重新构建

线上会停留在上一个已提交的版本。**不会白屏，也不会报错** —— 只是内容旧。
改完内容后先跑一次 `deploy_prepare.mjs` 是个好习惯。

---

## 成功标志

构建日志应出现：

```
npx wrangler deploy
Total Upload: ... KiB
Uploaded hairdryerlab (x.xx sec)
Deployed hairdryerlab triggers ...
```

注意：**这条路不依赖 `pnpm build`**，所以日志里**不会**有 `45 page(s) built`。
看到 `Uploaded hairdryerlab` 就是成功了。

---

## 部署后必须验证的三个文件

```
https://hairdryerlab.ca/robots.txt
https://hairdryerlab.ca/sitemap-index.xml
https://hairdryerlab.ca/llms.txt
```

`llms.txt` 由 `site/src/pages/llms.txt.ts` 在构建时从内容集合生成，列出 46 个真实
页面链接供 AI 爬虫使用。它原本是手写文件、URL 停留在旧分类法，上线后会让爬虫拿到
一整页 404，现已改为生成式。

---

## 绑定域名

1. 域名 `hairdryerlab.ca` 的 DNS 必须托管在 Cloudflare（先添加站点、改 nameserver）
2. Worker → **Settings → Domains & Routes** → **Add custom domain** →
   `hairdryerlab.ca`，再加 `www.hairdryerlab.ca`
3. `www` 建议用 **Redirect Rule 301** 指到裸域，避免两个 host 各自被 Google 索引

---

## 若日后想改回「Cloudflare 构建」

好处是仓库不必带产物。需要做两件事：

1. **Settings → Build**（菜单名可能是 `Build` 或 `Builds`，Cloudflare 自己的文档
   两种写法都有）
   - Root directory = `site`
   - Build command = `pnpm build`
2. **Settings → Build → Build Variables and Secrets**
   （不是 Settings → Variables & Secrets，后者是运行时变量）
   - `PNPM_VERSION` = `11.7.0` —— **必需**。构建镜像默认 pnpm 是 10.11.1，
     而本项目 `pnpm-workspace.yaml` 用的是 pnpm 11 语法（`allowBuilds`、
     `verifyDepsBeforeRun`），版本不匹配会报
     `Cannot find module 'html-escaper'`
   - `NODE_VERSION` = `22`

然后从 `.gitignore` 恢复 `dist/` 的忽略规则，并把 `site/dist` 移出版本控制。

---

## 排查顺序

1. **Worker 名是否等于两个 `wrangler.jsonc` 里的 `name`** —— 这是现在唯一的硬性要求
2. **日志里有没有 `Uploaded <worker-name>`**
3. **日志里的错误是不是 `Could not detect a directory containing static files`**
   —— 若是，检查根目录 `wrangler.jsonc` 是否存在、`assets.directory` 路径是否对
4. **页面能打开但没样式** → `site/dist/_astro/*.css` 没提交，跑一次
   `node _scripts/deploy_prepare.mjs`
5. **页面内容旧** → 忘记重新构建并提交

---

## 本地复现

```bash
node _scripts/deploy_prepare.mjs     # 同步 + 构建 + 暂存
cd site && pnpm build                # 只构建
```

> **干净环境验证不可省。** 本项目踩过一个只在干净环境暴露的坑：`pnpm 10+` 不再从
> `.npmrc` 读取项目级设置，导致全新安装的 `node_modules` 布局与本地不一致，构建报
> `Cannot find module 'html-escaper'`。本地因为 `node_modules` 是旧版 pnpm 装的，
> 一直没暴露。修复见 `site/pnpm-workspace.yaml` 顶部说明。
