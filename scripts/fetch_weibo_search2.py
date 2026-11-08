"""
weibo 补采 v2 — 自定义查询词 + 更宽窗口

用途: fetch_weibo_search.py 只用内置 SELF_TERMS, 每词只取搜索第 1 页(feature=4 时间序),
近期帖会挤掉 11/06 傍晚的帖。本脚本允许传入自定义词表, 专门捞
「美股收盘 / 纳指 / 道指 / 反弹 / 点位 / 下周 / 明日 / 外围 / 大盘」等收盘后内容。

用法:
  python3 fetch_weibo_search2.py 1216826604 --screen-name wu2198 \
      --since "2026-11-06 12:00" --out data/x.jsonl
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from fetch_weibo_search import _parse_created_at, fetch  # noqa: E402

QUERIES = [
    "美股", "纳指", "道指", "标普", "收盘", "反弹", "低开", "高开",
    "明日", "下周", "点位", "支撑", "压力", "外围", "美股反弹",
    "科技股", "大盘", "指数", "缩量", "放量", "涨停", "跌停",
    "芯片", "存储", "CPO", "光模块", "算力", "固态", "端侧", "机器人",
    "主升", "调整", "企稳", "反抽", "反弹行情", "波段",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("uid")
    ap.add_argument("--screen-name", default=None)
    ap.add_argument("--since", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--slow", type=float, default=1.2)
    args = ap.parse_args()

    posts = fetch(args.uid, args.screen_name or str(args.uid), QUERIES, slow=args.slow)

    if args.since:
        t0 = datetime.strptime(args.since, "%Y-%m-%d %H:%M")
        posts = [p for p in posts if (_parse_created_at(p["created_at"]) or t0) >= t0]

    out = Path(args.out) if args.out else SCRIPT_DIR.parent / "data" / "weibo_custom.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for p in posts:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")

    if posts:
        print(f"[range] {posts[0]['created_at'][:25]} → {posts[-1]['created_at'][:25]}")
    print(f"[done] {len(posts)} posts → {out}")


if __name__ == "__main__":
    main()
