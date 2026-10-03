#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
假的联盟 API 服务 —— 在拿到真实凭据前，用来端到端验证整条链路。

验证的是：
    同步脚本取链接 → 写入 affiliate-links.mjs → Astro 构建把占位符替换成真实链接

用法（两个终端）:

    1) 启动 mock（默认 127.0.0.1:8799）
       python _scripts/dev/mock_affiliate_api.py

    2) 指向 mock 并同步
       $env:LEVANTA_API_KEY = 'test'
       $env:LEVANTA_BASE_URL = 'http://127.0.0.1:8799'
       python _scripts/sync_affiliate_links.py --provider levanta

    3) 构建并确认替换生效
       cd site; pnpm build
       Select-String -Path dist/**/index.html -Pattern 'affiliate_url_'

    4) 测完务必还原，否则会把假链接写进仓库
       python _scripts/sync_affiliate_links.py --reset

mock 对每个 ASIN 返回一条明显是假的链接（example.invalid 域名），
不会误当成真实推广链接。
"""

import argparse
import json
import os
import re
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# 让 mock 能复用同步脚本的注册表解析
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from sync_affiliate_links import parse_registry  # noqa: E402
except Exception:  # 允许以其他方式运行时不复用
    parse_registry = None


def load_asins():
    if parse_registry is None:
        return []
    try:
        return [p['asin'] for p in parse_registry()]
    except SystemExit:
        return []


ASINS = load_asins()


class Handler(BaseHTTPRequestHandler):
    def _send(self, payload, status=200):
        body = json.dumps(payload).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _asins_from_request(self):
        qs = self.path.split('?', 1)[1] if '?' in self.path else ''
        found = set(re.findall(r'B0[A-Z0-9]{8}', self.path))
        if qs:
            from urllib.parse import parse_qs, unquote
            for v in parse_qs(qs).values():
                for item in v:
                    found.update(re.findall(r'B0[A-Z0-9]{8}', unquote(item)))
        return found

    def _handle(self, body=None):
        asins = self._asins_from_request() or set(ASINS)
        links = [
            {
                'asin': a,
                'url': 'https://example.invalid/mock-link/%s?net=%s'
                       % (a, self.server.provider),
            }
            for a in sorted(asins)
        ]
        self._send({'data': links, 'success': True})

    def do_GET(self):
        self._handle()

    def do_POST(self):
        length = int(self.headers.get('Content-Length') or 0)
        raw = self.rfile.read(length) if length else b''
        try:
            body = json.loads(raw or b'{}')
        except ValueError:
            body = {}
        for v in body.values():
            if isinstance(v, list):
                self.server.extra_asins.update(x for x in v if isinstance(x, str))
            elif isinstance(v, str):
                self.server.extra_asins.add(v)
        self._handle(body)

    def log_message(self, fmt, *args):
        sys.stderr.write('[mock:%s] %s\n' % (self.server.provider, fmt % args))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--port', type=int, default=8799)
    ap.add_argument('--provider', default='levanta')
    args = ap.parse_args()

    srv = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
    srv.provider = args.provider
    srv.extra_asins = set()
    sys.stderr.write(
        '[mock] listening on http://127.0.0.1:%d  (provider=%s)\n'
        '       提供 %d 个 ASIN 的假链接\n' % (args.port, args.provider, len(ASINS)))
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        sys.stderr.write('\n[mock] stopped\n')


if __name__ == '__main__':
    main()
