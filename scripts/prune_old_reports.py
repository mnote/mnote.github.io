#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""清理过期日报：删掉 cutoff 之前的 wu2198 投资日报页面。

2026-11-13 用户要求「删掉所有 2026 年 11 月之前的 投资日报」。
本脚本做三件事：

1. 删除仓库根目录下、日期早于 cutoff 的 wu2198 投资日报 HTML
   （只删日报页面；都业华收评/午评、词典页、2018 Jekyll 页不动）
2. 清掉首页里指向这些页面的卡片（否则留一堆 404 链接）
3. 更新 scripts/site_posts.json 归档清单

删完再跑 `python3 scripts/migrate_off_jekyll.py` 重建归档分页页。

用法：
    python3 scripts/prune_old_reports.py            # 默认 cutoff = 2026-11-01
    python3 scripts/prune_old_reports.py 2026-10-01 # 指定 cutoff
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "scripts" / "site_posts.json"
KEEP_FILES = {"index.html", "2018-11-16-Jekyll.html"}
DATE_DASH = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
DATE_COMPACT = re.compile(r"(\d{8})")


def file_date(name: str):
    """从文件名取日期，取不到按最早的 07-21 处理。"""
    m = DATE_DASH.search(name)
    if m:
        return "-".join(m.groups())
    m = DATE_COMPACT.search(name)
    if m:
        d = m.group(1)
        return f"{d[:4]}-{d[4:6]}-{d[6:]}"
    return "2026-07-21"


def is_wu2198_daily(name: str) -> bool:
    return "wu2198" in name and "investment-report" in name


def main():
    cutoff = sys.argv[1] if len(sys.argv) > 1 else "2026-11-01"
    print(f"[cutoff] {cutoff} 之前的 wu2198 投资日报将删除")

    victims = []
    for f in sorted(ROOT.glob("*.html")):
        if f.name in KEEP_FILES or "duyiehua" in f.name:
            continue
        if not is_wu2198_daily(f.name):
            continue
        d = file_date(f.name)
        if d < cutoff:
            victims.append((f, d))

    if not victims:
        print("[skip] 没有要删的页面")
        return 0

    urls = set()
    for f, d in victims:
        urls.add(f"/{f.name}")
        f.unlink()
        print(f"  [rm]   {f.name}  ({d})")

    # 首页卡片：删掉指向已删页面的整张卡
    idx = ROOT / "index.html"
    lines = idx.read_text(encoding="utf-8").split("\n")
    out, removed = [], 0
    for line in lines:
        if 'class="featured"' in line and any(f'href="{u}"' in line for u in urls):
            removed += 1
            continue
        out.append(line)
    # 清理因删卡留下的连续空行
    cleaned = []
    for line in out:
        if line.strip() == "" and cleaned and cleaned[-1].strip() == "":
            continue
        cleaned.append(line)
    idx.write_text("\n".join(cleaned), encoding="utf-8")
    left = sum(line.count('class="featured"') for line in cleaned)
    print(f"  [ok]   首页移除 {removed} 张卡片（现剩 {left} 张）")

    # 归档清单
    if MANIFEST.exists():
        posts = json.loads(MANIFEST.read_text(encoding="utf-8"))
        kept = [p for p in posts if p["url"] not in urls]
        MANIFEST.write_text(json.dumps(kept, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  [ok]   清单更新：{len(posts)} → {len(kept)} 条")

    # 重建归档分页页
    subprocess.run([sys.executable, str(ROOT / "scripts" / "migrate_off_jekyll.py")], check=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
