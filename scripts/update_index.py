#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""首页插卡（去 Jekyll 后的通用版，替代逐日手写的 update_index_YYYYMMDD.py）。

站点已去掉 Jekyll：index.html 是**纯静态**页面 —— 没有 YAML front matter，没有 Liquid。
所以插入卡片不再受「必须锚定在 front matter 之后」的约束，但仍然用锚点插入，
避免误伤其他卡片。

用法：
  # ① wu2198 日报：新增一张「🔥 最新」卡，原「🔥 最新」自动降级为「📅 往期」
  python3 scripts/update_index.py latest \
      --url /2026-11-13-wu2198-investment-report.html \
      --title "wu2198 投资日报 - 2026-11-13（周五 ……）"

  # ② 都业华收评 / 午评：在「🧭 高级班」区块最前面插一张卡（保持最新在前）
  python3 scripts/update_index.py dyh \
      --url /duyiehua-report-20261113.html \
      --title "DYH 收评 - 2026-11-13（周五 ……）"

幂等：URL 已存在则跳过，不会重复插卡。
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IDX = ROOT / "index.html"

BADGE_LATEST = "🔥 最新"
BADGE_HISTORY = "📅 往期"
BADGE_DYH = "🧭 高级班"


def card(url, title, badge=None, style=None):
    b = f'<span class="badge">{badge}</span> ' if badge else ""
    s = f' style="{style}"' if style else ""
    return f'<div class="featured"{s}><h2>{b}<a href="{url}">{title}</a></h2></div>'


def insert_latest(html, url, title):
    if f'href="{url}"' in html:
        return html, "[skip] 首页已有该链接"
    m = re.search(r'<div class="featured"[^>]*><h2><span class="badge">🔥 最新</span>', html)
    if not m:
        return html, "[ERR] 找不到「🔥 最新」卡片锚点"
    start = m.start()
    # 找到这张卡片的结束 </h2></div>
    end = html.index("</h2></div>", start) + len("</h2></div>")
    old = html[start:end]
    old_hist = old.replace(f'<span class="badge">{BADGE_LATEST}</span>',
                            f'<span class="badge">{BADGE_HISTORY}</span>')
    new = card(url, title, badge=BADGE_LATEST)
    return html[:start] + new + "\n\n" + old_hist + html[end:], f"[ok] 已插入新卡，原「🔥 最新」降级为「{BADGE_HISTORY}」"


def insert_dyh(html, url, title):
    if f'href="{url}"' in html:
        return html, "[skip] 首页已有该链接"
    m = re.search(r'<div class="featured"[^>]*><h2>(?:<span class="badge">🧭 高级班</span> )?', html)
    idx = None
    for mm in re.finditer(r'<div class="featured"[^>]*><h2>(?:<span class="badge">🧭 高级班</span> )?<a', html):
        idx = mm.start()
        break
    if idx is None:
        return html, "[ERR] 找不到「🧭 高级班」区块锚点"
    new = card(url, title, badge=BADGE_DYH,
               style="background: linear-gradient(135deg, #f5f0ff 0%, #eef9ff 100%); border-color: #d6c4f7; border-left-color: #7e57c2;")
    return html[:idx] + new + "\n\n" + html[idx:], "[ok] 已在「🧭 高级班」区块插入新卡"


def main():
    ap = argparse.ArgumentParser(description="首页插卡（静态版）")
    ap.add_argument("mode", choices=["latest", "dyh"], help="latest=wu2198 日报；dyh=都业华收评/午评")
    ap.add_argument("--url", required=True, help="卡片链接，必须以 / 开头")
    ap.add_argument("--title", required=True, help="卡片标题（与报告页 <title>/<h1> 保持同一字符串）")
    args = ap.parse_args()

    if not args.url.startswith("/"):
        print("[ERR] --url 必须以 / 开头")
        return 1
    if args.mode == "latest" and not args.url.endswith(".html"):
        print("[ERR] --url 必须是 .html")
        return 1

    s = IDX.read_text(encoding="utf-8")
    if not s.lstrip().startswith("<!DOCTYPE html>"):
        print("[ERR] index.html 不是静态首页（首行应为 <!DOCTYPE html>），停止")
        return 1
    if "{%" in s:
        print("[ERR] index.html 含 Liquid 残留（{%），停止")
        return 1

    s, msg = (insert_latest if args.mode == "latest" else insert_dyh)(s, args.url, args.title)
    if msg.startswith("[ERR]"):
        print(msg)
        return 1
    IDX.write_text(s, encoding="utf-8")

    body = IDX.read_text(encoding="utf-8")
    print(msg)
    print("[卡片数]", body.count('class="featured"'))
    print("[Liquid 残留]", body.count("{%"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
