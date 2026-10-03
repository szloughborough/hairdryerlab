# 联盟链接接入说明 —— Levanta / PartnerBoost / ArtemisAds

> **结论：三家 API 都已按官方文档实现，生产环境连通性已实测，只差有效凭据。**
> 把 key/token 填进 `site/.env`，跑一条命令即可生成真实推广链接。

---

## 1. 现在的状态

### 已实测通过的部分

**生产 API 连通性**（2026-10-02，无有效凭据，返回业务级错误而非网络错误）：

| 主机 | 结果 | 含义 |
|---|---|---|
| `app.levanta.io` | `401` "You must provide an 'Authorization' header with a valid bearer token" | 可达，鉴权就位 |
| `app.partnerboost.com` | `{"status":{"code":1000,"msg":"Publisher does not exist"}}` | 可达，token 生效路径就位 |
| `api.artemisads.com` | `{"code":401,"message":"Unauthorized"}` | 可达，鉴权就位 |

**三家 provider 全链路**（对着按官方规范写的本地 mock 跑）：17 个商品 →
Levanta 成功 12 个、其余 5 个自动回退 PartnerBoost、再回退 ArtemisAds →
写入链接表 → Astro 构建把占位符替换成真实 URL，**0 处泄漏**。

**构建期防护**：干净状态构建，20 个页面的占位符全部渲染成不可点击的
`#affiliate-pending-*` 锚点，产物里 `{{affiliate_url_*}}` 与其百分号编码形式
均为 **0** 处。`AFFILIATE_STRICT=1` 时未解析会直接构建失败。

### 未完成的部分

**没有有效凭据**，所以 `site/src/data/affiliate-links.mjs` 目前是空的，
线上仍是 pending 锚点（不可点击，不是坏链）。

---

## 2. 三家接口的真实规格（已从官方文档核实）

### Levanta —— Creator API v2 ✅

```
POST https://app.levanta.io/api/creator/v2/links
Authorization: Bearer {api_key}
{"product": {"primary_id": "<Levanta 内部 primaryId>", "marketplace": "amazon.ca"}}
→ {"id","type","marketplace","url","mobileOptimizedUrl"}
```

**关键点：建链接口吃的是 Levanta 内部 `primaryId`，不是 ASIN。** 所以要两步：

1. `GET /products?marketplace=amazon.ca&limit=500`（cursor 翻页）
   响应 `products[]` 每项含 `primaryId` 和 `ids[]`，**ASIN 在
   `ids[]` 里 `label == "ASIN"` 的那一项**。
2. 只有 `access == true` 的商品才能建链，否则返回
   `400 "You do not have permission to create a link for this product"`。
   脚本会据此跳过无权限品牌。

无批量接口，一个商品一次请求。脚本已内置 0.15s 间隔限速。

### PartnerBoost —— Partner API ✅

```
POST https://app.partnerboost.com/api/datafeed/get_amazon_link_by_asin
Content-Type: application/json
{"token": "<渠道 token>", "asins": "B0...,B0...", "country_code": "CA"}
→ {"status":{"code":0},"data":{"link":"<Amazon Attribution 深链>","link_id":...},
   "error_list":[{"asin":...,"message":"Product not found or no relationship"}]}
```

**关键点：**

- Amazon 系列走 `/api/datafeed/*` REST 路径，**不是** authentication 页那种
  `/api.php?mod={module}&op={action}` 形态。
- 认证只用请求体里的 `token`（来自 Partner 后台 → Token manage，**按推广渠道区分**），
  没有鉴权 header。
- **支持批量**：`asins` 逗号分隔，单次上限 50 —— 17 个商品一次请求搞定。
- `country_code` 必填，加拿大用 `CA`。
- 前提是已与该品牌建立 partnership，否则进 `error_list`。
- 状态码 `1002` = 调用频率过高，脚本已做指数退避重试。
- ⚠ 批量时 `data` 是单对象还是 `data.list[]` 数组，**文档未写明**。脚本对
  `data` 单对象 / `data.list[]` / `data` 直接是数组 三种形态都做了兼容，
  首次真实调用后建议核对一次。

### ArtemisAds —— Open API ✅

```
POST https://api.artemisads.com/openapi/publisher/v1/links
x-aa-authorization: Bearer {api_key}
{"productId": "aa_xxx"}
→ {"linkId","productId","asin","trackingLink","shortTrackingLink",...}
```

**关键点：**

- 认证头是自定义的 `x-aa-authorization`，不是标准 `Authorization`。
- 建链接口吃的是 ArtemisAds 自家 `productId`（形如 `aa_xxx`），不是 ASIN。
  同样两步：`GET /products?asins=B0..,B0..&marketplace=amazon.ca` 拿
  `products[].productId`。
- 只有 `productId` 是必填。`sourceId` / `primaryTrackingId` / `subTrackingId`
  都是可选，**不需要**预先创建 tracking id。
- 推广链接字段是根级的 `trackingLink`（`shortTrackingLink` 是短链）。
  注意这两个字段**不在 required 列表里**，脚本做了空值兜底。
- **限流严格**：`POST /links` 只有 **20 次/分钟**，超限 429。脚本内置
  3 秒间隔的主动限速。商品多时这一步会比较慢。
- 无批量接口，无 sandbox 环境。

---

## 3. 你需要做的（只有一步）

### 3.1 填 `site/.env`

`site/.env` 已存在且已 gitignore。只有三个变量是必须的：

```ini
# Levanta：后台 → 设置/API → Create API key
LEVANTA_API_KEY=

# PartnerBoost：Partner 后台 → Token manage → 选中渠道 → 复制该渠道 token
PARTNERBOOST_TOKEN=

# ArtemisAds：后台 → Settings → Open API → Generate
ARTEMIS_API_KEY=
```

三家不必都填——**填了哪家就跑哪家**，没填的自动跳过，不会报错。
填一家的 key 也能立刻拿到那家覆盖的商品链接。

### 3.2 跑同步

```powershell
python _scripts/sync_affiliate_links.py --dry-run   # 先看结果，不写文件
python _scripts/sync_affiliate_links.py             # 确认无误后落盘
```

### 3.3 上线前严格构建

```powershell
cd site
pnpm build:strict     # 仍有未解析占位符则直接失败
```

---

## 4. 当前待补的 7 个 token

同步后仍有 7 个拿不到链接（在 mock 环境下验证的结果）：

| token | 原因 |
|---|---|
| `affiliate_url_dyson_travel` | Levanta 无推广权限；PartnerBoost 无 relationship |
| `affiliate_url_dyson_nural` | 同上 |
| `affiliate_url_conair_318rc` | 同上（Conair 的 Buy Box 甚至是 Amazon 自营） |
| `affiliate_url_conair_330c` | 同上 |
| `affiliate_url_conair_flomotion` | 同上 |
| `affiliate_url_revlon_travel` | 注册表里已标 `defer: true` |
| `affiliate_url_aina` | 注册表里已标 `defer: true` |

`dyson` / `conair` 这几个即使填了真实 key，大概率仍然拿不到——主流联盟网络
不给这些品牌佣金。**建议**：把这几项也标 `defer: true`，或考虑改用普通
Amazon.ca 链接兜底（需自行确认符合 Amazon Associates 合规要求）。

> 注：上面这个「哪家覆盖哪个品牌」的结论来自 mock 的模拟设定，**不是真实数据**。
> 填了真实 key 跑一遍才能知道实际覆盖情况——以实际结果为准。

---

## 5. 验证方式（无需真实凭据）

三个 mock 严格按各自官方规范实现，可完整走通链路：

```powershell
# 终端 1-3：起三个 mock
python _scripts/dev/mock_levanta_api.py      --port 8801
python _scripts/dev/mock_partnerboost_api.py --port 8802 --shape list
python _scripts/dev/mock_artemis_api.py      --port 8803

# 终端 4：指向 mock 并同步
$env:LEVANTA_API_KEY='test';      $env:LEVANTA_BASE_URL='http://127.0.0.1:8801'
$env:PARTNERBOOST_TOKEN='test';   $env:PARTNERBOOST_BASE_URL='http://127.0.0.1:8802'
$env:ARTEMIS_API_KEY='test';      $env:ARTEMIS_BASE_URL='http://127.0.0.1:8803/openapi/publisher/v1'
python _scripts/sync_affiliate_links.py
```

`mock_partnerboost_api.py --shape {single|list|flat}` 可切换批量返回形态，
用来验证脚本对文档未明确的三种形态都兼容。

**测完务必还原**，否则假链接会留在仓库：

```powershell
python _scripts/sync_affiliate_links.py --reset
```

---

## 6. Token / ASIN 对照表（20 个）

| token | 产品 | ASIN |
|---|---|---|
| `affiliate_url_laifen_air` | Laifen Air | B0GWHF4SHD |
| `affiliate_url_laifen_se_lite` | Laifen SE Lite | B0FKBFZNHK |
| `affiliate_url_laifen_air_diffuser` | Laifen Air Diffuser | B0GWHGTBDY |
| `affiliate_url_laifen_se2` | Laifen SE2 | B0FPMBBG2J |
| `affiliate_url_laifen_swift` | Laifen Swift (gen 1) | B0D141Q8ZF |
| `affiliate_url_laifen_swift_diffuser` | Laifen Swift + Diffuser | B0D13MYLJC |
| `affiliate_url_dyson_travel` | Dyson Supersonic Travel | B0GHZMFY9W |
| `affiliate_url_dyson_nural` | Dyson Supersonic Nural | B0FHJFTZ57 |
| `affiliate_url_shark_speedstyle` | Shark SpeedStyle Pro | B0DFDQ3THF |
| `affiliate_url_dreame` | Dreame Pocket Pro | B0F8QH8XHV |
| `affiliate_url_slopehill` | Slopehill 1902 Ionic | B0C3M9WBQF |
| `affiliate_url_slopehill_brushless` | Slopehill Brushless | B08HRQG2M6 |
| `affiliate_url_slopehill_diffuser` | Slopehill Ionic + Diffuser | B0CY4QMMBH |
| `affiliate_url_wavytalk` | Wavytalk 1875W | B09JZ18GLJ |
| `affiliate_url_conair_318rc` | Conair 318RC | B0852913V2 |
| `affiliate_url_conair_330c` | Conair 330C Titanium Pro | B0CFQ3R4CQ |
| `affiliate_url_conair_flomotion` | Conair InfinitiPro FloMotion Pro | B0B15P7SDS |
| `affiliate_url_revlon_travel` | Revlon RVDR5034F Travel | B07NF1CLMQ |
| `affiliate_url_aina` | AINA Diffuser Dryer | B0DMWNFZRH |

（`defer: true` 的两项不会参与同步。）

---

## 7. 相关文件

| 作用 | 路径 |
|---|---|
| 凭据模板 | `site/.env.example` |
| token 注册表（改这里加产品） | `site/src/data/affiliate-products.mjs` |
| 链接表（自动生成，勿手改） | `site/src/data/affiliate-links.mjs` |
| 同步脚本（三家 provider） | `_scripts/sync_affiliate_links.py` |
| 构建期替换 | `site/src/plugins/rehype-affiliate-links.mjs` |
| 解析 / 严格模式 | `site/src/data/affiliate.mjs` |
| 严格模式构建入口 | `_scripts/build-strict.mjs` |
| 三个 mock | `_scripts/dev/mock_*_api.py` |
| 抓下来的官方文档存档 | `_ref/api-docs/` |

---

## 8. 顺带发现的一个结构问题

6 篇商业页 frontmatter 里的 `products[].affiliateUrl` **目前没有被任何页面渲染**：
`ProductPick.astro`（逐产品 CTA 卡，输出 `Check current price on Amazon.ca` 外链）
没有被任何页面引用，只有不输出外链的 `ProductPicks.astro`（横排缩略卡）在用。
产品级联盟外链实际只来自正文里的 markdown 链接。

要么在 `Article.astro` 引入 `ProductPick` 让 frontmatter 生效，要么把
`affiliateUrl` 字段删掉避免误导。这个决定和 API 对接独立。
