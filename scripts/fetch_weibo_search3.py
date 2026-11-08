"""
weibo 补采 v3 — 周末/收盘后专用词表

v2 已捞到 11/06 23:21「美国市场科技股报复性反弹，纳指涨425点」这条关键帖。
v3 换一批词，专门扫 11/06 20:12（上期截断点）→ 11/07 07:02 之间的空档，
以及周末任何带行情/外盘/板块味道的漏网帖。

用法:
  python3 fetch_weibo_search3.py 1216826604 --screen-name wu2198 \
      --since "2026-11-06 19:00" --out data/x.jsonl
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from fetch_weibo_search import _parse_created_at, fetch  # noqa: E402

QUERIES = [
    "报复性反弹", "收盘了", "收盘总结", "今天收", "明日", "周一", "本周末",
    "下周", "这周", "反弹", "企稳", "止跌", "回升", "普涨", "反弹行情",
    "外围", "隔夜", "中概", "英伟达", "特斯拉", "美股科技股", "纳指",
    "美元", "黄金", "原油", "汇率", "降息", "加息", "美联储",
    "成交量", "成交额", "增量", "缩量", "放量", "换手", "北向", "主力",
    "领涨", "领跌", "涨停", "跌停", "连板", "首板", "炸板",
    "固态", "端侧", "算力", "存储", "CPO", "光模块", "芯片", "机器人",
    "锂", "电池", "新能源", "医药", "白酒", "银行", "券商", "地产",
    "AI", "人工智能", "DeepSeek", "梁文锋", "寒门", "人口",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("uid")
    ap.add_argument("--screen-name", default=None)
    ap.add_argument("--since", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--slow", type=float, default=1.1)
    args = ap.parse_args()

    posts = fetch(args.uid, args.screen_name or str(args.uid), QUERIES, slow=args.slow)

    if args.since:
        t0 = datetime.strptime(args.since, "%Y-%m-%d %H:%M")
        posts = [p for p in posts if (_parse_created_at(p["created_at"]) or t0) >= t0]

    out = Path(args.out) if args.out else SCRIPT_DIR.parent / "data" / "weibo_v3.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for p in posts:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")

    if posts:
        print(f"[range] {posts[0]['created_at'][:25]} → {posts[-1]['created_at'][:25]}")
    print(f"[done] {len(posts)} posts → {out}")


if __name__ == "__main__":
    main()
