"""11/11 收盘板块统计（同花顺概念口径）。

⚠️ 口径说明：东财 push2 接口本次全程 IP 级限流（21:38 起不可用），
   改用同花顺概念板块成分表（q.10jqka.com.cn/gn/detail/code/<code>/），
   成分股涨跌幅取自该页表格（与 Tushare 日线交叉验证一致）。
   口径与东财不同，**不可与 11/10 报告的东财口径直接跨期比较**。

用法： python3 scripts/collect_sectors_ths_20261111.py
"""
import json
import re
import time
import urllib.request
from pathlib import Path

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
      "Referer": "http://q.10jqka.com.cn/"}

# 同花顺概念板块 code
BOARDS = [
    ("309049", "共封装光学(CPO)"),
    ("307940", "存储芯片"),
    ("309119", "人形机器人"),
    ("300816", "机器人概念"),
    ("301085", "芯片概念"),
    ("301175", "智能穿戴"),
    ("302131", "智能音箱"),
    ("309120", "AI手机"),
    ("308384", "消费电子概念"),
    ("308828", "东数西算(算力)"),
    ("309068", "算力租赁"),
]

ROW = re.compile(
    r'<td>\d+</td>\s*<td><a href="http://stockpage\.10jqka\.com\.cn/(\d+)/"[^>]*>\1</a></td>'
    r'\s*<td><a[^>]*>([^<]+)</a></td>'
    r'\s*<td[^>]*>([\d.]+)</td>'
    r'\s*<td class="[^"]*">(-?[\d.]+)</td>',
    re.S)


def get(u):
    req = urllib.request.Request(url=u, headers=UA)
    return urllib.request.urlopen(req, timeout=25).read().decode("gbk", "ignore")


def board(code, name, max_pages=8):
    rows = {}
    for page in range(1, max_pages + 1):
        u = (f"http://q.10jqka.com.cn/gn/detail/field/199112/order/desc/"
             f"page/{page}/code/{code}/")
        try:
            html = get(u)
        except Exception as e:
            print(f"  [ERR] {name} p{page}: {e}")
            break
        got = ROW.findall(html)
        if not got:
            break
        new = 0
        for c, nm, price, pct in got:
            if c not in rows:
                rows[c] = (nm, float(pct))
                new += 1
        if new == 0:
            break
        time.sleep(0.35)
        if len(got) < 20:
            break

    if not rows:
        print(f"{name} ({code}): 空")
        return None
    pcts = [v[1] for v in rows.values()]
    avg = sum(pcts) / len(pcts)
    up = sum(1 for v in pcts if v > 0)
    top = sorted(rows.items(), key=lambda kv: -kv[1][1])[:10]
    head = ", ".join(f"{nm}{pct:+.2f}" for _, (nm, pct) in top)
    print(f"{name} ({code}): 样本{len(rows)} 均值{avg:+.2f}% 上涨{up}/{len(pcts)}")
    print(f"   {head}")
    return {"code": code, "name": name, "n": len(rows), "avg": round(avg, 2),
            "up": up, "total": len(pcts),
            "top": [{"code": c, "name": nm, "pct": pct} for c, (nm, pct) in top]}


if __name__ == "__main__":
    out_dir = Path("/Users/maoling/workspace/mnote.github.io/charts")
    out = []
    for code, name in BOARDS:
        r = board(code, name)
        if r:
            out.append(r)
        time.sleep(0.5)
    p = out_dir / "_sectors_ths_20261111.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n[out] {p}")
