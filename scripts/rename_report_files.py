#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""报告页文件名统一为 `{来源}-yyyyMMdd.html`（幂等，可重复运行）。

2026-11-13 用户定的规则：
    wu2198 投资日报  → wu2198-yyyyMMdd.html
    都业华 收评      → duyiehua-yyyyMMdd.html
    都业华 午评      → duyiehua-yyyyMMdd-noon.html   （同日两份，午评带 -noon 后缀）

本脚本做四件事：
1. 按映射重命名报告页（git mv）
2. 删掉中文名重复副本（内容由 duyiehua-* 承载）
3. 为每个旧 URL 生成 meta refresh 跳转页，旧链接不断
4. 更新 index.html 的卡片链接与 scripts/site_posts.json 清单

用法：
    python3 scripts/rename_report_files.py          # 干跑
    python3 scripts/rename_report_files.py --apply
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "scripts" / "site_posts.json"

# 旧文件名 → 新文件名
RENAMES = {
    # wu2198 投资日报
    "2026-11-04-wu2198-investment-report.html": "wu2198-20261104.html",
    "2026-11-05-wu2198-investment-report.html": "wu2198-20261105.html",
    "2026-11-06-wu2198-investment-report.html": "wu2198-20261106.html",
    "2026-11-08-wu2198-investment-report.html": "wu2198-20261108.html",
    "2026-11-09-wu2198-investment-report.html": "wu2198-20261109.html",
    "2026-11-10-wu2198-investment-report.html": "wu2198-20261110.html",
    "2026-11-11-wu2198-investment-report.html": "wu2198-20261111.html",
    "2026-11-12-wu2198-investment-report.html": "wu2198-20261112.html",
    # 都业华收评
    "duyiehua-report-20261109.html": "duyiehua-20261109.html",
    "duyiehua-report-20261110.html": "duyiehua-20261110.html",
    "duyiehua-report-20261111.html": "duyiehua-20261111.html",
    "duyiehua-report-20261112.html": "duyiehua-20261112.html",
    # 都业华午评（同日第二份，带 -noon）
    "duyiehua-noon-20261112.html": "duyiehua-20261112-noon.html",
}

# 中文名重复副本：直接删（首页未链接，内容与 duyiehua-* 相同）
DUPLICATES = [
    "2026-11-09-都业华-高级班收评纪要.html",
    "2026-11-10-都业华-高级班收评纪要.html",
    "2026-11-11-都业华-高级班收评纪要.html",
    "2026-11-12-都业华-高级班收评纪要.html",
    "2026-11-12-都业华-高级班午评纪要.html",
]

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


def git(*args):
    subprocess.run(["git", *args], cwd=ROOT, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main():
    apply = "--apply" in sys.argv
    todo, done = [], []
    for old, new in RENAMES.items():
        if (ROOT / old).exists() and not (ROOT / new).exists():
            todo.append((old, new))
        elif (ROOT / new).exists() and (ROOT / old).exists():
            done.append((old, new, "新旧同时存在"))
        elif (ROOT / new).exists():
            done.append((old, new, "已改名"))

    print(f"[1] 重命名：待处理 {len(todo)}，已完成/异常 {len(done)}")
    for old, new, why in done:
        print(f"    [skip] {old} → {new}（{why}）")
    for old, new in todo:
        print(f"    [mv]   {old} → {new}")

    dups = [d for d in DUPLICATES if (ROOT / d).exists()]
    print(f"[2] 删除中文名重复副本：{len(dups)} 个")
    for d in dups:
        print(f"    [rm]   {d}")

    # 旧 URL 需要跳转页（改名完成后，旧名不再存在、新名存在）
    print(f"[3] 跳转页：{len(RENAMES)} 个（旧 URL → 新 URL，meta refresh）")

    if not apply:
        print("\n[干跑] 未改动任何文件；确认后加 --apply")
        return 0

    for old, new in todo:
        git("mv", old, new)
    for d in dups:
        git("rm", "-q", d)
    written = 0
    for old, new in RENAMES.items():
        if (ROOT / new).exists() and not (ROOT / old).exists():
            (ROOT / old).write_text(
                REDIRECT_TPL.format(new="/" + new), encoding="utf-8")
            written += 1
    print(f"    [ok]   生成 {written} 个跳转页")

    # 首页卡片链接
    idx = ROOT / "index.html"
    s = idx.read_text(encoding="utf-8")
    hits = 0
    for old, new in RENAMES.items():
        needle = f'href="/{old}"'
        if needle in s:
            s = s.replace(needle, f'href="/{new}"')
            hits += 1
    idx.write_text(s, encoding="utf-8")
    print(f"    [ok]   首页替换 {hits} 条链接")

    # 归档清单
    if MANIFEST.exists():
        posts = json.loads(MANIFEST.read_text(encoding="utf-8"))
        m = {"/" + o: "/" + n for o, n in RENAMES.items()}
        for p in posts:
            p["url"] = m.get(p["url"], p["url"])
        counts = {}
        for p in posts:
            counts[p["url"]] = counts.get(p["url"], 0) + 1
        posts = [p for p in posts if counts[p["url"]] == 1]
        posts.sort(key=lambda p: (p["date"], p["url"]), reverse=True)
        MANIFEST.write_text(json.dumps(posts, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"    [ok]   清单更新为 {len(posts)} 条")

    subprocess.run([sys.executable, str(ROOT / "scripts" / "migrate_off_jekyll.py")],
                   check=True)
    print("\n[完成] 重跑迁移脚本已重建首页与归档分页")
    return 0


if __name__ == "__main__":
    sys.exit(main())
