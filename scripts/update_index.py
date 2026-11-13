#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""首页插卡（纯静态 index.html 通用版）。

站点已去掉 Jekyll：index.html 是**纯静态**页面 —— 没有 YAML front matter，没有 Liquid。

**卡片不放徽标、不放 emoji 图标**（用户 2026-11-13 明确要求）：
    <div class="featured"><h2><a href="/html/xxx.html">标题</a></h2></div>

插卡位置：
- `latest`（wu2198 日报）：插在第一张 wu2198 卡片之前（保持最新在前）
- `dyh`（都业华收评/午评）：插在第一张 DYH 卡片之前

用法：
  python3 scripts/update_index.py latest --url /html/wu2198-20261113.html \
      --title "wu2198 - 2026-11-13（周五 ……）"
  python3 scripts/update_index.py dyh --url /html/duyiehua-20261113.html \
      --title "DYH 收评 - 2026-11-13（周五 ……）"

幂等：URL 已存在则跳过，不会重复插卡。
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IDX = ROOT / "index.html"

DYH_STYLE = ("background: linear-gradient(135deg, #f5f0ff 0%, #eef9ff 100%); "
             "border-color: #d6c4f7; border-left-color: #7e57c2;")


def card(url, title, style=None):
    s = f' style="{style}"' if style else ""
    return f'<div class="featured"{s}><h2><a href="{url}">{title}</a></h2></div>'


def _insert_before(html, url, title, first_of, style=None):
    if f'href="{url}"' in html:
        return html, "[skip] 首页已有该链接"
    m = re.search(rf'<div class="featured"[^>]*><h2><a href="{first_of}', html)
    if not m:
        return html, f"[ERR] 找不到以 {first_of} 开头的卡片锚点"
    idx = m.start()
    return html[:idx] + card(url, title, style) + "\n" + html[idx:], "[ok] 已插入新卡（无徽标、无图标）"


def insert_latest(html, url, title):
    return _insert_before(html, url, title, r"/html/wu2198-")


def insert_dyh(html, url, title):
    return _insert_before(html, url, title, r"/html/duyiehua-", DYH_STYLE)


def main():
    ap = argparse.ArgumentParser(description="首页插卡（静态版，无徽标/图标）")
    ap.add_argument("mode", choices=["latest", "dyh"], help="latest=wu2198 日报；dyh=都业华收评/午评")
    ap.add_argument("--url", required=True, help="卡片链接，以 / 开头（报告页在 /html/ 下）")
    ap.add_argument("--title", required=True, help="卡片标题（与报告页 <title>/<h1> 同一字符串）")
    args = ap.parse_args()

    if not args.url.startswith("/"):
        print("[ERR] --url 必须以 / 开头")
        return 1
    if not args.url.endswith(".html"):
        print("[ERR] --url 必须是 .html")
        return 1

    s = IDX.read_text(encoding="utf-8")
    if not s.lstrip().startswith("<!DOCTYPE html>"):
        print("[ERR] index.html 不是静态首页（首行应为 <!DOCTYPE html>），停止")
        return 1

    s, msg = (insert_latest if args.mode == "latest" else insert_dyh)(s, args.url, args.title)
    if msg.startswith("[ERR]"):
        print(msg)
        return 1
    IDX.write_text(s, encoding="utf-8")

    body = IDX.read_text(encoding="utf-8")
    print(msg)
    print("[卡片数]", body.count('class="featured"'))
    print("[徽标残留]", body.count('class="badge"'))
    return 0


if __name__ == "__main__":
    sys.exit(main())
