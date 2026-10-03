#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ArtemisAds Open API 的本地 mock —— 按官方 OpenAPI 3.0.1 规范实现，
用来在拿到真实 API key 前验证 ASIN → productId → 建链 两步流程。

规范来源: https://artemisads-api-doc.apifox.cn/llms.txt 下各页 .md 镜像

实现的端点（基址 /openapi/publisher/v1）:
    GET  /products?asins=B0..,B0..&marketplace=&limit=&cursor=
         -> {"cursor": null, "products":[{productId, asin, marketplace, ...}]}
    POST /links   body {"productId": "aa_xxx"}
         -> {"linkId","productId","asin","trackingLink","shortTrackingLink",...}
    GET  /sources -> {"sources":[{id,name}], "cursor": null}

认证: x-aa-authorization: Bearer <key>，缺失或非法返回 401 {"code":401,...}
限流: POST /links 20/min —— mock 会统计并在超过 20 次/分钟时返回 429

用法:
    1) python _scripts/dev/mock_artemis_api.py --port 8803
    2) $env:ARTEMIS_API_KEY='test'
       $env:ARTEMIS_BASE_URL='http://127.0.0.1:8803/openapi/publisher/v1'
       python _scripts/sync_affiliate_links.py --provider artemis
    3) 测完还原: python _scripts/sync_affiliate_links.py --reset
"""

import argparse
import json
import os
import sys
import time
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from sync_affiliate_links import parse_registry
except Exception:
    parse_registry = None

# 模拟「不在 ArtemisAds 商品库」的品牌
NOT_IN_CATALOG = {'Revlon', 'Aina', 'Conair'}

BRAND_HINTS = [
    ('laifen', 'Laifen'), ('dyson', 'Dyson'), ('shark', 'Shark'),
    ('dreame', 'dreame'), ('slopehill', 'slopehill'), ('wavytalk', 'wavytalk'),
    ('conair', 'Conair'), ('revlon', 'Revlon'), ('aina', 'Aina'),
]


def guess_brand(token, label):
    low = (token + ' ' + label).lower()
    for key, brand in BRAND_HINTS:
        if key in low:
            return brand
    return 'Unknown'


def build_catalog():
    if parse_registry is None:
        return []
    out = []
    for p in parse_registry():
        brand = guess_brand(p['token'], p.get('label', ''))
        if brand in NOT_IN_CATALOG:
            continue
        out.append({
            'productId': 'aa_%s' % p['asin'],
            'asin': p['asin'],
            'brandId': 'aab_%s' % brand.lower(),
            'category': 'Hair Dryers',
            'commission': {'rate': 0.15},
            'imageUrl': 'https://example.invalid/img/%s.jpg' % p['asin'],
            'marketplace': 'amazon.ca',
            'status': 'active',
            'title': p.get('label') or p['asin'],
            'pricing': {'currency': 'CAD', 'value': '99.99'},
            'deals': [],
            'aboutProduct': {},
        })
    return out


CATALOG = build_catalog()
BY_ID = {p['productId']: p for p in CATALOG}
POST_TIMES = deque()  # POST /links 调用时间戳
LINK_LIMIT_PER_MIN = 20


class Handler(BaseHTTPRequestHandler):
    def _send(self, payload, status=200):
        body = json.dumps(payload).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _authed(self):
        return (self.headers.get('x-aa-authorization') or '').startswith('Bearer ')

    def do_GET(self):
        path, _, qs = self.path.partition('?')
        params = {}
        for kv in qs.split('&'):
            if '=' in kv:
                k, v = kv.split('=', 1)
                params[k] = v

        if not self._authed():
            return self._send({'code': 401, 'message': 'Unauthorized'}, 401)

        p = path.rstrip('/')
        if p.endswith('/products'):
            want = set(a for a in (params.get('asins') or '').split(',') if a)
            mp = params.get('marketplace')
            items = [x for x in CATALOG if (not want or x['asin'] in want)]
            if mp:
                items = [x for x in items if x['marketplace'] == mp]
            return self._send({'cursor': None, 'products': items})

        if p.endswith('/sources'):
            return self._send({'cursor': None, 'sources': [
                {'id': 'aa_src_default', 'name': 'Default Source'},
                {'id': 'aa_src_blog', 'name': 'Blog'},
            ]})

        return self._send({'code': 404, 'message': 'Not Found'}, 404)

    def do_POST(self):
        length = int(self.headers.get('Content-Length') or 0)
        raw = self.rfile.read(length) if length else b'{}'
        try:
            body = json.loads(raw or b'{}')
        except ValueError:
            return self._send({'code': 422, 'message': 'Input Validation Failed'}, 422)

        if not self._authed():
            return self._send({'code': 401, 'message': 'Unauthorized'}, 401)

        if not self.path.rstrip('/').endswith('/links'):
            return self._send({'code': 404, 'message': 'Not Found'}, 404)

        # 限流：60 秒滑动窗口
        now = time.time()
        while POST_TIMES and now - POST_TIMES[0] > 60:
            POST_TIMES.popleft()
        if len(POST_TIMES) >= LINK_LIMIT_PER_MIN:
            return self._send({'code': 429, 'message': 'Too Many Requests'}, 429)
        POST_TIMES.append(now)

        pid = body.get('productId')
        if not pid:
            return self._send({'code': 422, 'message': 'Input Validation Failed'}, 422)

        hit = BY_ID.get(pid)
        if not hit:
            return self._send({'code': 422, 'message': 'Input Validation Failed'}, 422)

        asin = hit['asin']
        return self._send({
            'linkId': 'aal_%s' % asin,
            'productId': pid,
            'asin': asin,
            'sourceId': body.get('sourceId') or 'aa_src_default',
            'sourceName': 'Default Source',
            'marketplace': hit['marketplace'],
            'productStatus': 'active',
            'trackingLink': 'https://example.invalid/artemis/%s?tid=test' % asin,
            'shortTrackingLink': 'https://example.invalid/artemis/s/%s' % asin,
        })

    def log_message(self, fmt, *args):
        if os.environ.get('AFFILIATE_DEBUG') == '1':
            sys.stderr.write('[mock-artemis] %s\n' % (fmt % args))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--port', type=int, default=8803)
    args = ap.parse_args()
    srv = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
    sys.stderr.write(
        '[mock-artemis] http://127.0.0.1:%d/openapi/publisher/v1\n'
        '  商品库 %d 个（%s 不在库中）\n'
        '  限流: POST /links %d/min\n'
        % (args.port, len(CATALOG), ','.join(sorted(NOT_IN_CATALOG)), LINK_LIMIT_PER_MIN))
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        sys.stderr.write('\n[mock-artemis] stopped\n')


if __name__ == '__main__':
    main()
