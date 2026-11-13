#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把报告页挪到 `html/` 子目录，并同步所有引用（幂等）。

2026-11-13 用户要求：wu2198 / duyiehua 的 HTML 报告页全部放进 `html/` 文件夹。

做五件事：
1. `git mv` 13 个报告页 → `html/`
2. 页面内相对图片路径 `src="charts/…"` → `src="../charts/…"`（页面深了一层）
3. 根目录旧 URL 的跳转页目标改为 `/html/<新名>`
4. `index.html` 卡片链接 `/wu2198-…` → `/html/wu2198-…`
5. `scripts/site_posts.json` 清单 URL 同步

顺带（幂等）：给报告页副标题加「← 返回首页」链接、wu2198 标题去掉「投资日报」。

用法：
    python3 scripts/move_reports_to_html_dir.py          # 干跑
    python3 scripts/move_reports_to_html_dir.py --apply
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML_DIR = ROOT / "html"
MANIFEST = ROOT / "scripts" / "site_posts.json"

PAGES = [
    "wu2198-20261104.html", "wu2198-20261105.html", "wu2198-20261106.html",
    "wu2198-20261108.html", "wu2198-20261109.html", "wu2198-20261110.html",
    "wu2198-20261111.html", "wu2198-20261112.html",
    "duyiehua-20261109.html", "duyiehua-20261110.html", "duyiehua-20261111.html",
    "duyiehua-20261112.html", "duyiehua-20261112-noon.html",
]

# 旧 URL → 新 URL（跳转页就写在旧路径上）
OLD_URLS = {
    "2026-11-04-wu2198-investment-report.html": "/html/wu2198-20261104.html",
    "2026-11-05-wu2198-investment-report.html": "/html/wu2198-20261105.html",
    "2026-11-06-wu2198-investment-report.html": "/html/wu2198-20261106.html",
    "2026-11-08-wu2198-investment-report.html": "/html/wu2198-20261108.html",
    "2026-11-09-wu2198-investment-report.html": "/html/wu2198-20261109.html",
    "2026-11-10-wu2198-investment-report.html": "/html/wu2198-20261110.html",
    "2026-11-11-wu2198-investment-report.html": "/html/wu2198-20261111.html",
    "2026-11-12-wu2198-investment-report.html": "/html/wu2198-20261112.html",
    "duyiehua-report-20261109.html": "/html/duyiehua-20261109.html",
    "duyiehua-report-20261110.html": "/html/duyiehua-20261110.html",
    "duyiehua-report-20261111.html": "/html/duyiehua-20261111.html",
    "duyiehua-report-20261112.html": "/html/duyiehua-20261112.html",
    "duyiehua-noon-20261112.html": "/html/duyiehua-20261112-noon.html",
}

# 改名后留下的中间态 URL（/wu2198-20261112.html 这类）也要跳转
INTERMEDIATE = {
    f"wu2198-2026{lit}.html": f"/html/wu2198-2026{lit}.html"
    for lit in ("1104", "1105", "1106", "1108", "1109", "1110", "1111", "1112")
}
INTERMEDIATE.update({
    f"duyiehua-2026{lit}.html": f"/html/duyiehua-2026{lit}.html"
    for lit in ("1109", "1110", "1111", "1112")
})
INTERMEDIATE["duyiehua-20261112-noon.html"] = "/html/duyiehua-20261112-noon.html"

REDIRECT_TPL = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="robots" content="noindex">
<meta http-equiv="refresh" content="0; url={new}">
<link rel="canonical" href="https://mnote.github.io{new}">
<title>页面已迁移 · {new}</title>
<style>body{{font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;
margin:0;padding:80px 24px;text-align:center;color:#1f2937;background:#fff}}
a{{color:#1f6feb}}</style>
</head>
<body>
<p>报告页已迁移到新地址：</p>
<p><a href="{new}">https://mnote.github.io{new}</a></p>
<p style="color:#6b7280;font-size:13px">未自动跳转请点上面的链接。</p>
</body>
</html>
"""

HOME_LINK = ('<a href="/" style="color:#2563eb;text-decoration:none">← 返回首页</a>'
             '<span style="color:#9ca3af"> · </span>')


def git(*args):
    subprocess.run(["git", *args], cwd=ROOT, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main():
    apply = "--apply" in sys.argv
    HTML_DIR.mkdir(exist_ok=True)

    to_move = [p for p in PAGES if (ROOT / p).exists()]
    print(f"[1] 待移动 {len(to_move)} 个页面 → html/")

    if not apply:
        for p in to_move:
            print(f"    [mv]   {p} → html/{p}")
        print("\n[干跑] 未改动任何文件；确认后加 --apply")
        return 0

    for p in to_move:
        git("mv", p, f"html/{p}")

    for p in PAGES:
        f = HTML_DIR / p
        if not f.exists():
            continue
        s = f.read_text(encoding="utf-8")
        s = s.replace('src="charts/', 'src="../charts/')
        s = s.replace('src="reports/', 'src="../reports/')
        # wu2198 标题去掉「投资日报」
        s = s.replace("wu2198 投资日报 -", "wu2198 -")
        # 副标题加返回首页
        if '← 返回首页' not in s:
            s = re.sub(r'(<div class="meta">)', r'\1' + HOME_LINK, s, count=1)
        f.write_text(s, encoding="utf-8")
    print(f"[2] 已修正 {len(PAGES)} 个页面的图片路径 / 标题 / 返回首页链接")

    stubs = {}
    stubs.update({o: f"/html/{n.split('/')[-1]}" for o, n in OLD_URLS.items()})
    stubs.update(INTERMEDIATE)
    n = 0
    for old, new in stubs.items():
        (ROOT / old).write_text(REDIRECT_TPL.format(new=new), encoding="utf-8")
        n += 1
    print(f"[3] 已写 {n} 个跳转页（旧 URL → /html/…）")

    idx = ROOT / "index.html"
    s = idx.read_text(encoding="utf-8")
    hits = 0
    for p in PAGES:
        needle = f'href="/{p}"'
        if needle in s:
            s = s.replace(needle, f'href="/html/{p}"')
            hits += 1
    s = s.replace("wu2198 投资日报 -", "wu2198 -")
    idx.write_text(s, encoding="utf-8")
    print(f"[4] 首页：{hits} 条链接改为 /html/…，卡片标题去掉「投资日报」")

    if MANIFEST.exists():
        posts = json.loads(MANIFEST.read_text(encoding="utf-8"))
        for p in posts:
            u = p["url"]
            name = u.rsplit("/", 1)[-1]
            if name in PAGES:
                p["url"] = f"/html/{name}"
            p["title"] = p["title"].replace("wu2198 投资日报 -", "wu2198 -")
        posts.sort(key=lambda p: (p["date"], p["url"]), reverse=True)
        MANIFEST.write_text(json.dumps(posts, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[5] 清单更新：{len(posts)} 条")

    subprocess.run([sys.executable, str(ROOT / "scripts" / "migrate_off_jekyll.py")],
                   check=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
