#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PartnerBoost Amazon 转链接口的本地 mock —— 按官方文档实现，
用来在拿到真实 token 前验证批量转链流程。

文档: https://docs.partnerboost.com/developers/publisher-api/amazon/
端点: POST /api/datafeed/get_amazon_link_by_asin
入参: token, asins(逗号分隔,≤50), country_code, return_partnerboost_link
出参: status.code/msg, data.link / data.link_id, error_list

mock 用 --shape 参数模拟两种批量返回形态，用来验证脚本对两种都兼容：
    --shape single   单条: {"data": {"asin":"...","link":"..."}}       （默认）
    --shape list     数组: {"data": {"list":[{...},{...}]}}
    --shape flat     数组: {"data": [{...},{...}]}

用法:
    1) python _scripts/dev/mock_partnerboost_api.py --port 8802 --shape list
    2) $env:PARTNERBOOST_TOKEN='test'
       $env:PARTNERBOOST_BASE_URL='http://127.0.0.1:8802'
       python _scripts/sync_affiliate_links.py --provider partnerboost
    3) 测完还原: python _scripts/sync_affiliate_links.py --reset
"""

import argparse
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from sync_affiliate_links import parse_registry
except Exception:
    parse_registry = None

# 模拟「未建立 partnership」的品牌
NO_RELATION_BRANDS = {'Dyson', 'Conair', 'Revlon'}

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


def load_asins():
    if parse_registry is None:
        return {}
    out = {}
    for p in parse_registry():
        out[p['asin']] = guess_brand(p['token'], p.get('label', ''))
    return out


ASIN_BRAND = load_asins()


class Handler(BaseHTTPRequestHandler):
    def _send(self, payload, status=200):
        body = json.dumps(payload).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        length = int(self.headers.get('Content-Length') or 0)
        raw = self.rfile.read(length) if length else b'{}'
        try:
            body = json.loads(raw or b'{}')
        except ValueError:
            return self._send({'status': {'code': 1003,
                                          'msg': 'Missing required parameters or incorrect format'}})

        if not self.path.rstrip('/').endswith('/get_amazon_link_by_asin'):
            return self._send({'status': {'code': 1003, 'msg': 'Unknown endpoint'}}, 404)

        token = body.get('token')
        if not token:
            return self._send({'status': {'code': 1003, 'msg': 'Missing token'}})
        if token == 'BAD_TOKEN':
            return self._send({'status': {'code': 1000, 'msg': 'Publisher does not exist'}})
        if token == 'RATE_LIMITED':
            return self._send({'status': {'code': 1002, 'msg': 'Call frequency too high'}})

        asins = [a.strip() for a in (body.get('asins') or '').split(',') if a.strip()]
        country = (body.get('country_code') or '').upper()
        if not asins or not country:
            return self._send({'status': {'code': 1003, 'msg': 'Missing asins or country_code'}})
        if len(asins) > 50:
            return self._send({'status': {'code': 1003, 'msg': 'Maximum of 50 asins'}})

        ok, errors = [], []
        for a in asins:
            brand = ASIN_BRAND.get(a)
            if brand is None:
                errors.append({'asin': a, 'country_code': country,
                               'message': 'Product not found or no relationship'})
                continue
            if brand in NO_RELATION_BRANDS:
                errors.append({'asin': a, 'country_code': country,
                               'message': 'Product not found or no relationship'})
                continue
            cc = country.lower()
            ok.append({
                'asin': a,
                'link': 'https://example.invalid/pb/%s?cc=%s&maas=test' % (a, cc),
                'link_id': 'pbl_%s' % a,
                'partnerboost_link': 'https://example.invalid/pb/s/%s' % a,
            })

        shape = self.server.shape
        if shape == 'list':
            data = {'list': ok}
        elif shape == 'flat':
            data = ok
        else:  # single
            data = ok[0] if ok else {}
        self._send({'status': {'code': 0, 'msg': 'Success'},
                    'data': data, 'error_list': errors})

    def log_message(self, fmt, *args):
        if os.environ.get('AFFILIATE_DEBUG') == '1':
            sys.stderr.write('[mock-pb] %s\n' % (fmt % args))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--port', type=int, default=8802)
    ap.add_argument('--shape', choices=['single', 'list', 'flat'], default='single',
                    help='模拟批量返回形态')
    args = ap.parse_args()
    srv = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
    srv.shape = args.shape
    n_ok = sum(1 for b in ASIN_BRAND.values() if b not in NO_RELATION_BRANDS)
    sys.stderr.write(
        '[mock-pb] http://127.0.0.1:%d  shape=%s\n'
        '  商品 %d 个（可转链 %d）\n'
        '  特殊 token: BAD_TOKEN(1000) RATE_LIMITED(1002)\n'
        % (args.port, args.shape, len(ASIN_BRAND), n_ok))
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        sys.stderr.write('\n[mock-pb] stopped\n')


if __name__ == '__main__':
    main()
