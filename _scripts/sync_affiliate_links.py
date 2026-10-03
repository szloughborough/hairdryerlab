#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
联盟链接同步 —— 调 Levanta / PartnerBoost / ArtemisAds API，把占位符 token
解析成真实推广链接，写入 site/src/data/affiliate-links.json。

用法（在 site/ 目录下）:
    python ../_scripts/sync_affiliate_links.py                 # 同步全部
    python ../_scripts/sync_affiliate_links.py --dry-run       # 只打印，不写文件
    python ../_scripts/sync_affiliate_links.py --only laifen_air
    python ../_scripts/sync_affiliate_links.py --provider levanta

设计要点
  * 只用标准库（urllib），无第三方依赖。
  * 一个网络失败不影响其他网络；token 会依次尝试 providers 列表里的每个网络，
    第一个成功的胜出，结果里记录 provider，便于日后排查佣金归属。
  * defer=True 的产品直接跳过，不浪费 API 配额。
  * 未解析的 token 保留在 _meta.pending 里，构建时会据 #affiliate-pending- 兜底。
"""

import argparse
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

# --------------------------------------------------------------------------
# 路径
# --------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SITE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..', 'site'))
REGISTRY_JS = os.path.join(SITE_DIR, 'src', 'data', 'affiliate-products.mjs')
OUT_JSON = os.path.join(SITE_DIR, 'src', 'data', 'affiliate-links.mjs')
ENV_FILE = os.path.join(SITE_DIR, '.env')

# Levanta /products 分页失控保护。实测 amazon.ca 目录约 113 页（每页 500 条），
# 所以上限必须显著高于它 —— 曾因设 40 页而静默漏掉第 100 页上的 ASIN。
MAX_PAGES = 400


# --------------------------------------------------------------------------
# .env 读取（不覆盖已存在的真实环境变量）
# --------------------------------------------------------------------------
def load_env(path=ENV_FILE):
    if not os.path.exists(path):
        return False
    with io.open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, _, v = line.partition('=')
            k, v = k.strip(), v.strip().strip('"').strip("'")
            if k and k not in os.environ:
                os.environ[k] = v
    return True


def env(key, default=''):
    return (os.environ.get(key) or '').strip() or default


def debug(msg):
    if env('AFFILIATE_DEBUG') == '1':
        sys.stderr.write('[debug] %s\n' % msg)


# --------------------------------------------------------------------------
# 解析 affiliate-products.mjs（避免为 JS 引入解释器）
# --------------------------------------------------------------------------
TOKEN_RE = re.compile(r"token:\s*'([^']+)'")
ASIN_RE = re.compile(r"asin:\s*'([^']+)'")
PROVIDERS_RE = re.compile(r"providers:\s*\[([^\]]*)\]")
DEFER_RE = re.compile(r'defer:\s*true')


def parse_registry(path=REGISTRY_JS):
    """按对象块粗切，提取 token / asin / providers / defer。"""
    if not os.path.exists(path):
        sys.exit('找不到注册表: %s' % path)
    with io.open(path, 'r', encoding='utf-8') as f:
        src = f.read()

    # 去掉注释，避免注释里的示例被误解析
    src = re.sub(r'/\*.*?\*/', '', src, flags=re.S)
    src = re.sub(r'//[^\n]*', '', src)

    products = []
    # 以 { token: ... } 为界切块
    for m in TOKEN_RE.finditer(src):
        start = src.rfind('{', 0, m.start())
        end = src.find('}', m.start())
        block = src[start:end if end != -1 else len(src)]

        token = m.group(1)
        am = ASIN_RE.search(block)
        pm = PROVIDERS_RE.search(block)
        if not am:
            sys.stderr.write('警告: token %s 缺 asin，已跳过\n' % token)
            continue
        providers = []
        if pm:
            providers = [p.strip().strip("'\"") for p in pm.group(1).split(',') if p.strip()]
        products.append({
            'token': token,
            'asin': am.group(1),
            'providers': providers or ['levanta', 'partnerboost', 'artemis'],
            'defer': bool(DEFER_RE.search(block)),
        })

    if not products:
        sys.exit('注册表解析结果为空，请检查 %s 的格式' % path)
    return products


# --------------------------------------------------------------------------
# HTTP
# --------------------------------------------------------------------------
class HttpError(Exception):
    pass


def http_json(method, url, headers=None, params=None, body=None, timeout=30):
    """返回 (status, parsed_or_text)。非 2xx 抛 HttpError。"""
    if params:
        url = url + ('&' if '?' in url else '?') + urllib.parse.urlencode(params)

    data = None
    hdrs = {'Accept': 'application/json', 'User-Agent': 'hairdryerlab-affiliate-sync/1.0'}
    if headers:
        hdrs.update(headers)
    if body is not None:
        data = json.dumps(body).encode('utf-8')
        hdrs['Content-Type'] = 'application/json'

    req = urllib.request.Request(url, data=data, headers=hdrs, method=method.upper())
    debug('%s %s' % (method.upper(), url))
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode('utf-8', 'replace')
            status = resp.status
    except urllib.error.HTTPError as e:
        detail = e.read().decode('utf-8', 'replace')[:500]
        raise HttpError('%s %s -> HTTP %s: %s' % (method.upper(), url, e.code, detail))
    except Exception as e:
        raise HttpError('%s %s -> %s' % (method.upper(), url, e))

    try:
        return status, json.loads(raw)
    except ValueError:
        return status, raw


# --------------------------------------------------------------------------
# Provider 基类
# --------------------------------------------------------------------------
class Provider(object):
    """
    每个网络实现 fetch_links(targets) -> {asin: url}

    targets 是 [{'token':..., 'asin':..., 'label':...}, ...]

    关于「一次一个」：Levanta / PartnerBoost / ArtemisAds 的建链接口都是
    单个商品一次请求，所以子类内部自行循环即可，外面不用管。
    """

    id = 'base'
    label = 'Base'

    def __init__(self):
        self.timeout = int(env('AFFILIATE_HTTP_TIMEOUT', '30') or 30)

    # --- 子类需覆盖 -------------------------------------------------------
    def credentials(self):
        """返回凭据 dict；返回 None 表示未配置，跳过该网络。"""
        raise NotImplementedError

    def fetch_links(self, targets):
        """返回 {asin: url}"""
        raise NotImplementedError

    # --- 供子类使用的工具 -------------------------------------------------
    def _http(self, method, url, headers=None, params=None, body=None):
        return http_json(method, url, headers=headers, params=params,
                         body=body, timeout=self.timeout)

    @staticmethod
    def _progress(done, total, label):
        if done == total or done % 5 == 0:
            sys.stderr.write('    %s %d/%d\n' % (label, done, total))


# --------------------------------------------------------------------------
# Levanta —— Creator API v2（已按官方 OpenAPI 规范实现）
#
#   规范: https://app.levanta.io/api/creator/v2/openapi.json
#   认证: Authorization: Bearer {api_key}
#   基址: https://app.levanta.io/api/creator/v2
#
#   两步流程（关键：建链接口吃的是 Levanta 内部 primaryId，不是 ASIN）:
#     1) GET /products?marketplace=amazon.ca&access=true
#        响应 products[] 每项含 primaryId + ids[]（label=ASIN 的那项才是 ASIN）
#        只有 access == true 的商品才能建链，否则 POST /links 返回
#        400 "You do not have permission to create a link for this product"
#     2) POST /links
#        body: {"product": {"primary_id": <primaryId>, "marketplace": "amazon.ca"}}
#        响应: {"id","type","marketplace","url","mobileOptimizedUrl"}
# --------------------------------------------------------------------------
class Levanta(Provider):
    id = 'levanta'
    label = 'Levanta'

    def credentials(self):
        key = env('LEVANTA_API_KEY')
        if not key:
            return None
        return {'key': key}

    def _base(self):
        return env('LEVANTA_BASE_URL', 'https://app.levanta.io/api/creator/v2').rstrip('/')

    def _marketplace(self):
        return env('LEVANTA_MARKETPLACE', 'amazon.ca')

    def _headers(self, creds):
        return {
            'Authorization': 'Bearer %s' % creds['key'],
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

    # --- 第一步：ASIN → primaryId ----------------------------------------
    def _asin_index(self, creds, want_asins):
        """
        遍历 /products 分页，返回 {asin: {'primaryId':..., 'access':...,
        'marketplace':..., 'brandName':...}}
        """
        base, hdrs = self._base(), self._headers(creds)
        marketplace = self._marketplace()
        index, cursor, page = {}, '', 0

        while True:
            params = {'marketplace': marketplace, 'limit': 500}
            if cursor:
                params['cursor'] = cursor
            status, payload = self._http('GET', '%s/products' % base,
                                         headers=hdrs, params=params)
            if not isinstance(payload, dict):
                raise HttpError('Levanta /products 返回非 JSON: %s' % str(payload)[:200])

            products = payload.get('products') or []
            for p in products:
                pid = p.get('primaryId')
                if not pid:
                    continue
                for ident in (p.get('ids') or []):
                    if ident.get('label') == 'ASIN' and ident.get('value') in want_asins:
                        index.setdefault(ident['value'], {
                            'primaryId': pid,
                            'access': bool(p.get('access')),
                            'marketplace': p.get('marketplace') or marketplace,
                            'brandName': p.get('brandName') or '',
                        })
            page += 1
            cursor = payload.get('cursor') or ''
            debug('Levanta /products 第 %d 页，累计命中 %d' % (page, len(index)))
            # 上限只作为失控保护。实测加拿大目录约 113 页（每页 500）。
            # 早期设 40 页导致第 40 页之后的目标 ASIN 永远查不到 ——
            # 例如 slopehill 的 B08HRQG2M6 在第 100 页，曾被静默漏掉。
            if page >= MAX_PAGES:
                sys.stderr.write(
                    '    ⚠ Levanta 目录超过 %d 页上限，可能有 ASIN 未被扫描\n' % MAX_PAGES)
                break
            if not cursor or not products:
                break
        return index

    # --- 第二步：建链接 ---------------------------------------------------
    def _create_link(self, creds, primary_id, marketplace):
        status, payload = self._http(
            'POST', '%s/links' % self._base(), headers=self._headers(creds),
            body={'product': {'primary_id': primary_id, 'marketplace': marketplace}})
        if not isinstance(payload, dict):
            raise HttpError('Levanta /links 返回非 JSON: %s' % str(payload)[:200])
        return payload

    def fetch_links(self, targets):
        creds = self.credentials()
        want = {t['asin'] for t in targets}
        index = self._asin_index(creds, want)
        sys.stderr.write('    Levanta 命中 %d/%d 个 ASIN\n' % (len(index), len(want)))

        links, skipped = {}, []
        for i, t in enumerate(targets, 1):
            asin = t['asin']
            hit = index.get(asin)
            if not hit:
                skipped.append('%s(不在 Levanta 目录)' % asin)
                continue
            if not hit['access']:
                skipped.append('%s(%s 无推广权限)' % (asin, hit['brandName'] or '该品牌'))
                continue
            try:
                resp = self._create_link(creds, hit['primaryId'], hit['marketplace'])
            except HttpError as e:
                skipped.append('%s(%s)' % (asin, str(e)[:120]))
                continue
            url = resp.get('url') or resp.get('mobileOptimizedUrl')
            if url:
                links[asin] = url
            self._progress(i, len(targets), 'Levanta')
            time.sleep(0.15)  # 温和限速，避免触发风控

        if skipped:
            sys.stderr.write('    Levanta 跳过: %s\n' % '; '.join(skipped[:12]))
        return links


# --------------------------------------------------------------------------
# PartnerBoost
#   文档: https://docs.partnerboost.com/developers/publisher-api/authentication/
# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
# PartnerBoost —— Partner API（已按官方文档实现）
#
#   文档: https://docs.partnerboost.com/developers/publisher-api/amazon/
#   端点: POST https://app.partnerboost.com/api/datafeed/get_amazon_link_by_asin
#   认证: token 放在请求体里（无鉴权 header），来自 Partner 后台 Token manage，
#         每个推广渠道一个 token
#
#   注意：Amazon 系列接口**不用** authentication 页那种
#   /api.php?mod={module}&op={action} 形态，而是 REST 路径 /api/datafeed/*。
#
#   入参:
#     token                  必填
#     asins                  必填，逗号分隔，单次上限 50
#     country_code           必填，美 US / 加 CA / 墨 MX / 德 DE / 英 UK / ...
#     uid                    可选，PartnerBoost UID，最多 5 个
#     return_partnerboost_link  可选，0=不返回短链（默认），1=返回
#
#   出参:
#     status.code(0=成功) / status.msg
#     data.link              Amazon Attribution 深链 ← 我们要的
#     data.link_id
#     data.partnerboost_link 短链（需 return_partnerboost_link=1）
#     error_list            失败项（如 "Product not found or no relationship"）
#
#   ⚠ 批量时 data 是单对象还是 data.list[] 数组，文档未写明 —— 实测确认。
#     下面的 _parse_response 对两种形态都做了兼容。
# --------------------------------------------------------------------------
class PartnerBoost(Provider):
    id = 'partnerboost'
    label = 'PartnerBoost'

    BATCH_LIMIT = 50

    def credentials(self):
        token = env('PARTNERBOOST_TOKEN')
        if not token:
            return None
        return {'token': token}

    def _base(self):
        # 真实主机是 app.partnerboost.com，不是 api.partnerboost.com
        return env('PARTNERBOOST_BASE_URL', 'https://app.partnerboost.com').rstrip('/')

    def _country(self):
        """country_code 用两位码：站点是加拿大 -> CA"""
        raw = env('PARTNERBOOST_COUNTRY', 'CA').upper()
        if len(raw) > 2:  # 容错：有人会填 amazon.ca
            raw = raw.rsplit('.', 1)[-1].upper()
        return raw

    def fetch_links(self, targets):
        creds = self.credentials()
        base, country = self._base(), self._country()
        url = '%s/api/datafeed/get_amazon_link_by_asin' % base
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

        by_asin = {t['asin']: t for t in targets}
        links, skipped = {}, []

        # 单次上限 50，按批切分
        asins = list(by_asin)
        for start in range(0, len(asins), self.BATCH_LIMIT):
            chunk = asins[start:start + self.BATCH_LIMIT]
            body = {
                'token': creds['token'],
                'asins': ','.join(chunk),
                'country_code': country,
            }
            payload = self._post_with_retry(url, headers, body)

            code = ((payload.get('status') or {}).get('code')
                    if isinstance(payload, dict) else None)
            if code not in (0, None):
                msg = (payload.get('status') or {}).get('msg') or ''
                raise HttpError('PartnerBoost status %s: %s' % (code, msg))

            found = self._parse_response(payload, set(chunk))
            links.update(found)

            # 把 error_list 的原因并进 skipped，未在 error_list 里的单独记
            reasons = {}
            for item in self._error_list(payload):
                a = item.get('asin') or ''
                msg = (item.get('message') or '').strip()
                if a and msg:
                    reasons[a] = msg
            for a in chunk:
                if a in found:
                    continue
                skipped.append('%s%s' % (a, '(%s)' % reasons[a] if a in reasons else ''))

        if skipped:
            sys.stderr.write('    PartnerBoost 跳过: %s\n' % '; '.join(skipped[:12]))
        return links

    def _post_with_retry(self, url, headers, body, attempts=3):
        """1002 = 调用频率过高，做指数退避重试"""
        for i in range(attempts):
            try:
                status, payload = self._http('POST', url, headers=headers, body=body)
            except HttpError as e:
                if i == attempts - 1:
                    raise
                time.sleep(2 ** i)
                continue
            code = ((payload.get('status') or {}).get('code')
                    if isinstance(payload, dict) else None)
            if code == 1002 and i < attempts - 1:
                wait = 2 ** (i + 1)
                sys.stderr.write('    PartnerBoost 限流(1002)，%ds 后重试\n' % wait)
                time.sleep(wait)
                continue
            return payload
        return {}

    @staticmethod
    def _error_list(payload):
        if not isinstance(payload, dict):
            return []
        raw = payload.get('error_list') or payload.get('errorList') or []
        if isinstance(raw, dict):
            raw = [raw]
        return [x for x in raw if isinstance(x, dict)]

    @staticmethod
    def _parse_response(payload, wanted):
        """
        兼容两种批量返回形态：
          A) 单条:   {"data": {"asin": "...", "link": "https://..."}}
          B) 数组:   {"data": {"list": [{"asin": ..., "link": ...}, ...]}}
        以及 data 直接就是数组的情况。
        """
        found = {}

        def take(node):
            if not isinstance(node, dict):
                return
            asin = node.get('asin') or node.get('ASIN')
            link = node.get('link') or node.get('url') or node.get('amazon_link')
            if asin in wanted and isinstance(link, str) and link.startswith('http'):
                found.setdefault(asin, link)

        data = payload.get('data') if isinstance(payload, dict) else None

        if isinstance(data, list):
            for item in data:
                take(item)
        elif isinstance(data, dict):
            take(data)
            for key in ('list', 'links', 'results', 'items', 'data'):
                arr = data.get(key)
                if isinstance(arr, list):
                    for item in arr:
                        take(item)

        # 兜底：任何地方出现 {asin, link} 都收
        if not found:
            found = extract_links_generic(payload, wanted)
        return found


# --------------------------------------------------------------------------
# ArtemisAds —— Open API（已按官方 OpenAPI 3.0.1 规范实现）
#
#   规范: https://artemisads-api-doc.apifox.cn/llms.txt 下各页 .md 镜像
#   认证: x-aa-authorization: Bearer {api_key}
#   基址: https://api.artemisads.com/openapi/publisher/v1
#
#   两步流程（建链接口吃的是 ArtemisAds 自家 productId，不是 ASIN）:
#     1) GET /products?asins=B0..,B0..&marketplace=amazon.ca
#        响应 {cursor, products:[{productId, asin, marketplace, ...}]}
#     2) POST /links
#        body {"productId": "aa_xxx"}                （仅 productId 必填）
#             可选 sourceId / primaryTrackingId / subTrackingId
#        响应 {linkId, productId, asin, trackingLink, shortTrackingLink, ...}
#
#   限制: POST /links 20 次/分钟，GET /products 60 次/分钟，超限 429。
#         无批量接口，只能单个建链。无 sandbox 环境。
# --------------------------------------------------------------------------
class Artemis(Provider):
    id = 'artemis'
    label = 'ArtemisAds'

    # POST /links 限流 20/min -> 每个请求之间至少间隔 3 秒
    LINK_MIN_INTERVAL = 3.0

    def credentials(self):
        key = env('ARTEMIS_API_KEY')
        if not key:
            return None
        return {'key': key}

    def _base(self):
        return env('ARTEMIS_BASE_URL',
                   'https://api.artemisads.com/openapi/publisher/v1').rstrip('/')

    def _marketplace(self):
        return env('ARTEMIS_MARKETPLACE', 'amazon.ca')

    def _headers(self, creds):
        # 已从文档确认: x-aa-authorization: Bearer <api_key>
        return {
            'x-aa-authorization': 'Bearer %s' % creds['key'],
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

    # --- 第一步：ASIN → productId ----------------------------------------
    def _asin_index(self, creds, want_asins):
        hdrs = self._headers(creds)
        marketplace = self._marketplace()
        index, cursor, page = {}, '', 0

        while True:
            params = {
                'asins': ','.join(sorted(want_asins)),
                'marketplace': marketplace,
                'limit': 100,
            }
            if cursor:
                params['cursor'] = cursor
            status, payload = self._http('GET', '%s/products' % self._base(),
                                         headers=hdrs, params=params)
            if not isinstance(payload, dict):
                raise HttpError('ArtemisAds /products 返回非 JSON: %s' % str(payload)[:200])

            products = payload.get('products') or []
            for p in products:
                pid, asin = p.get('productId'), p.get('asin')
                if pid and asin in want_asins:
                    index.setdefault(asin, {'productId': pid,
                                            'marketplace': p.get('marketplace') or marketplace})
            page += 1
            cursor = payload.get('cursor')
            debug('ArtemisAds /products 第 %d 页，累计命中 %d' % (page, len(index)))
            if not cursor or not products or page >= 40:
                break
        return index

    # --- 第二步：建链接 ---------------------------------------------------
    def _create_link(self, creds, product_id):
        body = {'productId': product_id}
        source_id = env('ARTEMIS_SOURCE_ID')
        if source_id:
            body['sourceId'] = source_id
        status, payload = self._http('POST', '%s/links' % self._base(),
                                     headers=self._headers(creds), body=body)
        if not isinstance(payload, dict):
            raise HttpError('ArtemisAds /links 返回非 JSON: %s' % str(payload)[:200])
        return payload

    def fetch_links(self, targets):
        creds = self.credentials()
        want = {t['asin'] for t in targets}
        index = self._asin_index(creds, want)
        sys.stderr.write('    ArtemisAds 命中 %d/%d 个 ASIN\n' % (len(index), len(want)))

        links, skipped = {}, []
        last_call = 0.0
        for i, t in enumerate(targets, 1):
            asin = t['asin']
            hit = index.get(asin)
            if not hit:
                skipped.append('%s(不在 ArtemisAds 商品库)' % asin)
                continue

            # 主动限速：POST /links 上限 20/min
            gap = time.time() - last_call
            if gap < self.LINK_MIN_INTERVAL:
                time.sleep(self.LINK_MIN_INTERVAL - gap)
            try:
                resp = self._create_link(creds, hit['productId'])
            except HttpError as e:
                skipped.append('%s(%s)' % (asin, str(e)[:110]))
                last_call = time.time()
                continue
            last_call = time.time()

            # trackingLink 不在 required 里，做空值兜底
            url = resp.get('trackingLink') or resp.get('shortTrackingLink')
            if url:
                links[asin] = url
            else:
                skipped.append('%s(响应无 trackingLink)' % asin)
            self._progress(i, len(targets), 'ArtemisAds')

        if skipped:
            sys.stderr.write('    ArtemisAds 跳过: %s\n' % '; '.join(skipped[:12]))
        return links


# --------------------------------------------------------------------------
# 通用响应解析（文档确认后按真实结构收紧）
# --------------------------------------------------------------------------
URL_KEYS = ('url', 'link', 'short_url', 'shortUrl', 'tracking_url', 'trackingUrl',
            'affiliate_url', 'affiliateUrl', 'deeplink', 'deep_link', 'target_url')
ASIN_KEYS = ('asin', 'product_id', 'productId', 'sku', 'item_id')


def _pick_url(obj):
    for k in URL_KEYS:
        v = obj.get(k)
        if isinstance(v, str) and v.startswith('http'):
            return v
    return None


def _pick_asin(obj, asins):
    for k in ASIN_KEYS:
        v = obj.get(k)
        if isinstance(v, str) and v in asins:
            return v
    return None


def extract_links_generic(payload, asins):
    """
    尽力从任意 JSON 结构里抽出 asin -> url。
    支持：顶层 dict（asin 作键 / 单条记录）、data / results / links / items 数组。
    """
    wanted = set(asins)
    found = {}

    def walk(node):
        if isinstance(node, dict):
            # 形态 A: {"B0XXXX": "https://..."} 或 {"B0XXXX": {"url": ...}}
            for k, v in node.items():
                if k in wanted:
                    if isinstance(v, str) and v.startswith('http'):
                        found.setdefault(k, v)
                    elif isinstance(v, dict):
                        u = _pick_url(v)
                        if u:
                            found.setdefault(k, u)
            # 形态 B: {"asin": "B0XXXX", "url": "https://..."}
            a, u = _pick_asin(node, wanted), _pick_url(node)
            if a and u:
                found.setdefault(a, u)
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(payload)
    return found


_provider_instances = (Levanta(), PartnerBoost(), Artemis())
PROVIDERS = {p.id: p for p in _provider_instances}


# --------------------------------------------------------------------------
# 主流程
# --------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description='同步联盟推广链接')
    ap.add_argument('--dry-run', action='store_true', help='只打印结果，不写文件')
    ap.add_argument('--only', default='', help='只处理名字包含该子串的 token')
    ap.add_argument('--provider', default='', help='只用指定网络（逗号分隔）')
    ap.add_argument('--reset', action='store_true',
                    help='清空所有已解析链接（测完 mock 后还原用）')
    args = ap.parse_args()

    if not load_env():
        sys.stderr.write('提示: 未找到 %s，将只使用已存在的环境变量\n' % ENV_FILE)

    products = parse_registry()
    if args.only:
        products = [p for p in products if args.only in p['token']]
    if not products:
        sys.exit('没有匹配的产品')

    if args.reset:
        write_out({}, products, {}, [])
        sys.stderr.write('已清空所有已解析链接。\n')
        return 0

    # 读取已有结果，保留本轮未处理的条目（正则解析生成的 .mjs）
    existing = {}
    if os.path.exists(OUT_JSON):
        try:
            with io.open(OUT_JSON, 'r', encoding='utf-8') as f:
                txt = f.read()
            for m in re.finditer(
                    r"""["']([^"']+)["']:\s*\{\s*url:\s*"((?:[^"\\]|\\.)*)",\s*asin:\s*"([^"]*)","""
                    r"""\s*provider:\s*"([^"]*)"\s*\}""", txt):
                token, url, asin, pid = m.groups()
                existing[token] = {'url': url.replace('\\"', '"'), 'asin': asin, 'provider': pid}
        except Exception as e:
            sys.stderr.write('警告: 无法解析已有 %s（%s），将重建\n' % (OUT_JSON, e))

    # 未配置任何凭据 -> 提前退出，给出可执行的指引
    configured = [pid for pid, p in PROVIDERS.items() if p.credentials() is not None]
    if not configured:
        sys.stderr.write(
            '\n✗ 没有检测到任何联盟网络凭据。\n'
            '  请编辑 %s 填入至少一家的 API key，然后重新运行。\n'
            '  需要哪些变量见 site/.env.example。\n' % ENV_FILE)
        # 仍然写出一个只含 pending 的文件，保证构建侧有据可依
        if not args.dry_run:
            write_out(existing, products, {}, configured)
        return 2

    sys.stderr.write('已配置的网络: %s\n' % ', '.join(configured))

    # 按 provider 维度批量处理，减少 API 调用次数
    resolved = {}
    errors = {}
    for pid in configured:
        if args.provider and pid not in [s.strip() for s in args.provider.split(',')]:
            continue
        provider = PROVIDERS[pid]

        targets = []
        for p in products:
            if p['defer']:
                continue
            if pid not in p['providers']:
                continue
            if p['token'] in resolved:
                continue  # 前面的网络已经解析成功
            targets.append(p)

        if not targets:
            continue

        sys.stderr.write('→ %s: 查询 %d 个商品\n' % (provider.label, len(targets)))
        try:
            links = provider.fetch_links(targets)
        except HttpError as e:
            errors[pid] = str(e)
            sys.stderr.write('  ✗ %s\n' % e)
            continue
        except NotImplementedError as e:
            errors[pid] = str(e) or 'provider 未实现'
            sys.stderr.write('  ⊘ %s: %s\n' % (provider.label, e))
            continue

        for p in targets:
            url = links.get(p['asin'])
            if url:
                resolved[p['token']] = {
                    'url': url,
                    'asin': p['asin'],
                    'provider': pid,
                }
                sys.stderr.write('  ✓ %s\n' % p['token'])
            else:
                sys.stderr.write('  · %s 未返回链接\n' % p['token'])

    for token, entry in existing.items():
        # 保留本轮没碰过、但之前已解析成功的条目
        if token not in resolved and entry.get('provider'):
            resolved.setdefault(token, entry)

    if args.dry_run:
        print(json.dumps(resolved, indent=2, ensure_ascii=False))
        return 0

    write_out(resolved, products, errors, configured)
    return 0


def write_out(links, products, errors, configured):
    tokens = {p['token'] for p in products}
    pending = sorted(t for t in tokens if t not in links)

    meta = {
        'syncedAt': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'providersConfigured': configured,
        'resolved': len(links),
        'pending': pending,
        'errors': errors,
    }

    lines = [
        '/**',
        ' * 联盟推广链接 —— 自动生成，请勿手工编辑。',
        ' *',
        ' * 生成命令: python _scripts/sync_affiliate_links.py',
        ' * 数据来源: Levanta / PartnerBoost / ArtemisAds 官方 API',
        ' *',
        ' * 未解析的 token 在构建时会被 Astro 拒绝（见 src/data/affiliate.mjs），',
        ' * 以免占位符泄漏到线上页面。',
        ' */',
        '',
        'export const LINKS = {',
    ]
    for token in sorted(links):
        e = links[token]
        lines.append('  "%s": { url: "%s", asin: "%s", provider: "%s" },'
                     % (token, json.dumps(e['url'])[1:-1], e['asin'], e['provider']))
    lines.append('};')
    lines.append('')
    lines.append('export const META = %s;' % json.dumps(meta, indent=2, ensure_ascii=False))
    lines.append('')

    with io.open(OUT_JSON, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    sys.stderr.write('\n已写入 %s\n' % OUT_JSON)
    sys.stderr.write('解析成功 %d 个，待补 %d 个\n' % (len(links), len(pending)))
    if pending:
        sys.stderr.write('待补: %s\n' % ', '.join(pending))
    if errors:
        sys.stderr.write('出错的网络: %s\n' % json.dumps(errors, ensure_ascii=False))


if __name__ == '__main__':
    sys.exit(main())
