"""都业华 2026-11-20 高级班收评 · 补充采集（板块榜 + ETF 份额）

核验老师三条关键判据：
  1.「涨幅榜靠前的主要是银行和保险」→ 东财行业板块涨幅榜
  2.「元件板块有点动作」→ 元件板块（BK0459/BK1036）当日走势
  3.「中证500以及中证1000ETF资金进入但走势没什么起色」/「上证50ETF尾盘量能异动放大翻红」
     → Tushare fund_share（ETF 份额变化 = 申赎）

输出：reports/duyiehua-20261120/extra_close_20261120.json
"""
import json
import subprocess
import time
from pathlib import Path

import tushare as ts
import os

REPO = Path("/Users/maoling/workspace/mnote.github.io")
RPT = REPO / "reports/duyiehua-20261120"
TD = "20261120"

pro = ts.pro_api(os.environ.get("TUSHARE_TOKEN")
                 or "a4d50511c45b1f214ca32edbde1ba21241d5bb37c9f66f66a91025b3")

UA = ["User-Agent: Mozilla/5.0", "Referer: https://quote.eastmoney.com/"]


def curl_json(url, tries=4):
    cmd = ["curl", "-s", "--max-time", "25"]
    for h in UA:
        cmd += ["-H", h]
    cmd.append(url)
    for i in range(tries):
        r = subprocess.run(cmd, capture_output=True)
        if r.stdout and r.stdout.strip():
            try:
                return json.loads(r.stdout.decode("utf-8", "ignore"))
            except Exception:
                pass
        time.sleep(1.2 + i)
    return None


def em_board(fs, fid="f3", pz=100, pages=3):
    """东财板块列表（m:90+t:2 行业 / m:90+t:3 概念），按 fid 排序"""
    out = []
    for pn in range(1, pages + 1):
        url = (f"https://push2.eastmoney.com/api/qt/clist/get?pn={pn}&pz={pz}&po=1&np=1"
               f"&fltt=2&invt=2&fid={fid}&fs={fs}"
               "&fields=f12,f14,f3,f62,f104,f105,f128,f136")
        j = curl_json(url)
        if not j or not j.get("data"):
            break
        diff = j["data"].get("diff") or []
        for d in diff:
            out.append({"code": d.get("f12"), "name": d.get("f14"), "pct": d.get("f3"),
                        "main_net": d.get("f62"), "up": d.get("f104"), "down": d.get("f105"),
                        "leader": d.get("f128"), "leader_pct": d.get("f136")})
        time.sleep(0.5)
    return out


res = {}

log_lines = []


def log(*a):
    print(*a, flush=True)


log("== 行业板块涨幅榜（m:90+t:2，按 f3 降序）==")
ind = em_board("m:90+t:2", "f3", 100, 3)
res["industry_by_pct"] = ind
log(f"  总 {len(ind)} 条，前 15：")
for b in ind[:15]:
    log(f"   {b['name']:14s} {b['pct']:+7.2f}%  涨{b['up']}/跌{b['down']}  "
        f"主力 {(b['main_net'] or 0)/1e8:+8.2f}亿  领涨 {b['leader']}")

log("== 行业板块跌幅榜（fid=f3 升序 -> po=0）==")
ind_bad = em_board("m:90+t:2", "f3", 30, 1)
log("  （改用 pz=100 全量排序，取末尾）")
ind_all = em_board("m:90+t:2", "f3", 100, 3)
tail = sorted(ind_all, key=lambda x: x["pct"])[:15]
res["industry_worst"] = tail
for b in tail:
    log(f"   {b['name']:14s} {b['pct']:+7.2f}%  涨{b['up']}/跌{b['down']}  "
        f"主力 {(b['main_net'] or 0)/1e8:+8.2f}亿")

log("== 概念板块涨幅榜（m:90+t:3）==")
con = em_board("m:90+t:3", "f3", 100, 3)
res["concept_by_pct"] = con
for b in con[:15]:
    log(f"   {b['name']:16s} {b['pct']:+7.2f}%  涨{b['up']}/跌{b['down']}  "
        f"主力 {(b['main_net'] or 0)/1e8:+8.2f}亿  领涨 {b['leader']}")

# 元件板块
log("== 元件相关板块 ==")
keys = ["元件", "PCB", "印制", "电子元件"]
res["yuanjian"] = [b for b in ind_all + con
                   if any(k in (b["name"] or "") for k in keys)]
for b in res["yuanjian"]:
    log(f"   {b['name']:16s} {b['pct']:+7.2f}%  涨{b['up']}/跌{b['down']}  "
        f"主力 {(b['main_net'] or 0)/1e8:+8.2f}亿  领涨 {b['leader']}")

# 银行/保险
log("== 银行/保险/红利板块 ==")
keys2 = ["银行", "保险", "煤炭", "石油", "电力"]
res["dividend"] = [b for b in ind_all + con
                   if any(k in (b["name"] or "") for k in keys2)]
for b in sorted(res["dividend"], key=lambda x: -x["pct"])[:20]:
    log(f"   {b['name']:18s} {b['pct']:+7.2f}%  涨{b['up']}/跌{b['down']}  "
        f"主力 {(b['main_net'] or 0)/1e8:+8.2f}亿  领涨 {b['leader']}")

log("== ETF 份额变化（fund_share）==")
FUNDS = {
    "510050.SH": "上证50ETF",
    "510500.SH": "中证500ETF",
    "512100.SH": "中证1000ETF",
    "159915.SZ": "创业板ETF易方达",
    "588000.SH": "科创50ETF",
    "510300.SH": "沪深300ETF",
}
res["etf_share"] = {}
for code, name in FUNDS.items():
    try:
        df = pro.fund_share(ts_code=code, start_date="20261110", end_date=TD)
    except Exception as e:
        log(f"  {name} ERR {str(e)[:80]}")
        continue
    if df is None or len(df) == 0:
        log(f"  {name} 无数据")
        continue
    df = df.sort_values("trade_date")
    d = df.to_dict("records")
    last, prev = d[-1], d[-2] if len(d) > 1 else d[-1]
    res["etf_share"][name] = {
        "code": code,
        "series": [{"d": r["trade_date"], "share": r["fd_share"]} for r in d],
        "last_share": last["fd_share"], "prev_share": prev["fd_share"],
        "delta_share": round(last["fd_share"] - prev["fd_share"], 2),
        "delta_pct": round((last["fd_share"] / prev["fd_share"] - 1) * 100, 2),
    }
    log(f"  {name:14s} 份额 {prev['fd_share']:.2f} → {last['fd_share']:.2f} "
        f"({res['etf_share'][name]['delta_pct']:+.2f}%)")

(RPT / "extra_close_20261120.json").write_text(
    json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
log("saved", RPT / "extra_close_20261120.json")
