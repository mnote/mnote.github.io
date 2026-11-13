#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""清理孤立图表与过期数据目录（幂等）。

2026-11-13 用户要求：删掉 11 月前投资日报遗留的孤立 charts 图片和 reports 数据目录。

判定规则：
- **孤立图表**：`charts/` 下的 PNG，不被仓库根目录任何页面（`*.html`）引用。
  先把所有页面的 `src`/`href` 引用收成集合，再比 `charts/` 实际文件。
- **过期数据目录**：`reports/wu2198-YYYYMMDD`，日期早于 cutoff 的整个目录删掉。
  `duyiehua-*` / `dyh-*` / `leer-*` 一律不动（收评与选股留痕不在此次清理范围）。

用法：
    python3 scripts/prune_orphan_assets.py            # 干跑，只列清单
    python3 scripts/prune_orphan_assets.py --apply    # 真删
    python3 scripts/prune_orphan_assets.py --apply 2026-11-01   # 指定 cutoff
"""
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHARTS = ROOT / "charts"
REPORTS = ROOT / "reports"
DATE_COMPACT = re.compile(r"(\d{8})")


def referenced():
    """所有根目录页面引用到的相对路径集合。"""
    refs = set()
    for p in ROOT.glob("*.html"):
        h = p.read_text(encoding="utf-8")
        for s in re.findall(r'(?:src|href)="([^"]+)"', h):
            if s.startswith(("http://", "https://", "data:", "#", "mailto:")):
                continue
            refs.add(os.path.normpath(s.split("?")[0].split("#")[0]))
    return refs


def orphan_charts(refs):
    out = []
    for f in sorted(CHARTS.iterdir()):
        if f.is_file() and f"charts/{f.name}" not in refs:
            out.append(f)
    return out


def stale_report_dirs(cutoff):
    out = []
    for d in sorted(REPORTS.iterdir()):
        if not d.is_dir() or not d.name.startswith("wu2198-"):
            continue
        m = DATE_COMPACT.search(d.name)
        if not m:
            continue
        n = m.group(1)
        if f"{n[:4]}-{n[4:6]}-{n[6:]}" < cutoff:
            out.append(d)
    return out


def rm_tracked(paths):
    """已入库的走 git rm，未入库的用 shutil（保持 git 状态干净）。"""
    rel = [str(p.relative_to(ROOT)) for p in paths]
    tracked = set()
    if rel:
        r = subprocess.run(["git", "ls-files", "--"] + rel, cwd=ROOT,
                           capture_output=True, text=True)
        tracked = {line for line in r.stdout.splitlines() if line}
    untracked = [p for p, r in zip(paths, rel) if r not in tracked]
    to_git = [r for r in rel if r in tracked]
    if to_git:
        subprocess.run(["git", "rm", "-q", "-r", "--"] + to_git, cwd=ROOT, check=True)
    for p in untracked:
        shutil.rmtree(p) if p.is_dir() else p.unlink()


def main():
    apply = "--apply" in sys.argv
    cutoffs = [a for a in sys.argv[1:] if not a.startswith("--")]
    cutoff = cutoffs[0] if cutoffs else "2026-11-01"

    refs = referenced()
    charts = orphan_charts(refs)
    dirs = stale_report_dirs(cutoff)

    csize = sum(f.stat().st_size for f in charts)
    dsize = sum(sum(f.stat().st_size for f in d.rglob("*") if f.is_file()) for d in dirs)

    print(f"页面引用 {len(refs)} 条 | charts/ 共 {len(list(CHARTS.iterdir()))} 个文件")
    print(f"孤立图表 {len(charts)} 个（{csize / 1e6:.1f} MB）")
    print(f"过期数据目录 {len(dirs)} 个（{dsize / 1e6:.1f} MB，cutoff {cutoff}）：")
    for d in dirs:
        print(f"    {d.name}")

    if not apply:
        print("\n[干跑] 未删除任何文件；确认后加 --apply")
        return 0

    rm_tracked(charts + dirs)
    print(f"\n[ok] 已删除 {len(charts)} 个孤立图表 + {len(dirs)} 个数据目录，"
          f"释放约 {(csize + dsize) / 1e6:.1f} MB")
    print(f"[剩余] charts/ {len(list(CHARTS.iterdir()))} 个文件")
    return 0


if __name__ == "__main__":
    sys.exit(main())
