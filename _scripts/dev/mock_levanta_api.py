#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Levanta Creator API v2 的本地 mock —— 严格按官方 OpenAPI 规范实现，
用来在拿到真实 API key 之前验证「ASIN → primaryId → 建链」两步流程。

规范来源: https://app.levanta.io/api/creator/v2/openapi.json

实现的端点:
    GET  /products?marketplace=&access=&limit=&cursor=
         -> {"products":[{primaryId, ids:[{label,value}], brandName, marketplace, access, ...}], "cursor": ""}
    POST /links
         body {"product":{"primary_id","marketplace"}}
         -> {"id","type","marketplace","url","mobileOptimizedUrl"}
         若 primary_id 不存在 -> 404 {"status":404,"message":"Product not found"}
         若 access 为 false   -> 400 {"status":400,"message":"You do not have permission to create a link for this product"}
    GET  /brands -> {"brands":[...],"cursor":""}

用法（两个终端）:

    1) python _scripts/dev/mock_levanta_api.py --port 8801

    2) $env:LEVANTA_API_KEY='test'
       $env:LEVANTA_BASE_URL='http://127.0.0.1:8801'
       python _scripts/sync_affiliate_links.py --provider levanta

    3) 测完还原: python _scripts/sync_affiliate_links.py --reset

mock 故意让一部分商品 access=false，用来验证脚本会正确跳过无权限品牌。
"""

import argparse
import json
import os
import re
import sys
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from sync_affiliate_links import parse_registry
except Exception:
    parse_registry = None

# 这些品牌在 mock 里标记为「无推广权限」，模拟真实情况
NO_ACCESS_BRANDS = {'Dyson', 'Conair', 'Revlon'}

# 由 token 推断品牌名的简易映射（token 形如 affiliate_url_laifen_air）
BRAND_HINTS = [
    ('laifen', 'Laifen'), ('dyson', 'Dyson'), ('shark', 'Shark'),
    ('dreame', 'dreame'), ('slopehill', 'slopehill'), ('wavytalk', 'wavytalk'),
    ('conair', 'Conair'),
]


def guess_brand(token, label):
    low = (token + ' ' + label).lower()
    for key, brand in BRAND_HINTS:
        if key in low:
            return brand
    return 'Unknown'


def build_products():
    if parse_registry is None:
        return []
    out = []
    for p in parse_registry():
        brand = guess_brand(p['token'], p.get('label', ''))
        out.append({
            'primaryId': 'lev_%s' % p['asin'],
            'ids': [{'label': 'ASIN', 'value': p['asin']}],
            'title': p.get('label') or p['asin'],
            'brandId': 'brand_%s' % brand.lower(),
            'brandName': brand,
            'image': 'https://example.invalid/img/%s.jpg' % p['asin'],
            'category': 'Hair Dryers',
            'price': {'currency': 'CAD', 'value': '99.99'},
            'commission': {'rate': 0.15},
            'marketplace': 'amazon.ca',
            'access': brand not in NO_ACCESS_BRANDS,
            'availability': 'in_stock',
            'rating': 4.5,
            'ratingsTotal': 100,
            'groupId': 'grp_%s' % p['asin'],
        })
    return out


PRODUCTS = build_products()
BY_PRIMARY = {p['primaryId']: p for p in PRODUCTS}


class Handler(BaseHTTPRequestHandler):
    def _send(self, payload, status=200):
        body = json.dumps(payload).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path, _, qs = self.path.partition('?')
        params = {}
        for kv in qs.split('&'):
            if '=' in kv:
                k, v = kv.split('=', 1)
                params[k] = v

        if not self.headers.get('Authorization', '').startswith('Bearer '):
            return self._send({'message': "You must provide an 'Authorization' header "
                                         'with a valid bearer token', 'status': 401}, 401)

        if path.rstrip('/').endswith('/products'):
            items = PRODUCTS
            mp = params.get('marketplace')
            if mp:
                items = [p for p in items if p['marketplace'] == mp]
            if params.get('access') == 'true':
                items = [p for p in items if p['access']]
            limit = int(params.get('limit') or 100)
            # 故意分页，验证脚本会翻页
            page = items[:limit]
            return self._send({'products': page, 'cursor': ''})

        if path.rstrip('/').endswith('/brands'):
            brands = {}
            for p in PRODUCTS:
                brands[p['brandName']] = {
                    'id': p['brandId'], 'name': p['brandName'],
                    'marketplace': p['marketplace'], 'access': p['access'],
                }
            return self._send({'brands': list(brands.values()), 'cursor': ''})

        return self._send({'status': 404, 'message': 'Not found'}, 404)

    def do_POST(self):
        length = int(self.headers.get('Content-Length') or 0)
        raw = self.rfile.read(length) if length else b'{}'
        try:
            body = json.loads(raw or b'{}')
        except ValueError:
            return self._send({'status': 422, 'message': 'Input Validation Failed'}, 422)

        if not self.headers.get('Authorization', '').startswith('Bearer '):
            return self._send({'message': 'Unauthorized', 'status': 401}, 401)

        if not self.path.rstrip('/').endswith('/links'):
            return self._send({'status': 404, 'message': 'Not found'}, 404)

        product = body.get('product') or {}
        pid, mp = product.get('primary_id'), product.get('marketplace')
        if not pid or not mp:
            return self._send({'status': 422, 'message': 'Input Validation Failed'}, 422)

        hit = BY_PRIMARY.get(pid)
        if not hit:
            return self._send({'status': 404, 'message': 'Product not found'}, 404)
        if not hit['access']:
            return self._send({'status': 400, 'message': 'You do not have permission '
                              'to create a link for this product'}, 400)

        asin = next((i['value'] for i in hit['ids'] if i['label'] == 'ASIN'), pid)
        link_id = str(uuid.uuid4())
        # 明显的假链接，不会误当真实推广链接
        url = 'https://example.invalid/levanta/%s?lid=%s' % (asin, link_id[:8])
        return self._send({
            'id': link_id, 'type': 'product', 'marketplace': mp,
            'url': url, 'mobileOptimizedUrl': url,
        })

    def log_message(self, fmt, *args):
        if os.environ.get('AFFILIATE_DEBUG') == '1':
            sys.stderr.write('[mock-levanta] %s\n' % (fmt % args))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--port', type=int, default=8801)
    args = ap.parse_args()
    srv = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
    n_ok = sum(1 for p in PRODUCTS if p['access'])
    sys.stderr.write(
        '[mock-levanta] http://127.0.0.1:%d\n'
        '  商品 %d 个（可建链 %d，无权限 %d）\n'
        '  用法: LEVANTA_BASE_URL=http://127.0.0.1:%d\n'
        % (args.port, len(PRODUCTS), n_ok, len(PRODUCTS) - n_ok, args.port))
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        sys.stderr.write('\n[mock-levanta] stopped\n')


if __name__ == '__main__':
    main()
