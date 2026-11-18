"""类二买共振股池 2026-11-18 · 日线数据采集

⛔ 只用日线（用户 2026-11-11 禁令：不调用 1/15 分钟 K 线、不调用 czsc）。
数据源：Tushare pro.daily（前复权，基准=最新交易日）+ daily_basic（总市值/换手/量比）
输出：reports/pool-20261118/pool.json
"""
import json
import os
from pathlib import Path

import tushare as ts

REPO = Path("/Users/maoling/workspace/mnote.github.io")
RPT = REPO / "reports/pool-20261118"
RPT.mkdir(parents=True, exist_ok=True)

DATE = "20261118"
START = "20260601"  # 覆盖最早入池日 6/18 之前

tok = os.environ.get("TUSHARE_TOKEN") or open(os.path.expanduser("~/.tushare_token")).read().strip()
pro = ts.pro_api(tok)

# (序号, 名称, ts_code, 所属行业, 备注, 入池日期)
POOL = [
    (1, "凯莱英", "002821.SZ", "医疗服务", "CDMO", "20260618"),
    (2, "北特科技", "603009.SH", "汽车零部件", "机器人", "20260701"),
    (3, "新雷能", "300593.SZ", "其他电源设备", "其他电源设备", "20260826"),
    (4, "新凤鸣", "603225.SH", "化学纤维", "化学纤维", "20260831"),
    (5, "桂冠电力", "600236.SH", "电力", "电力", "20260909"),
    (6, "四川成渝", "601107.SH", "公路铁路运输", "公路铁路运输", "20261009"),
    (7, "中国石化", "600028.SH", "石油加工贸易", "石油加工贸易", "20261102"),
    (8, "平安银行", "000001.SZ", "银行", "银行", "20261103"),
    (9, "中文在线", "300364.SZ", "文化传媒", "文化传媒", "20261104"),
    (10, "瀚蓝环境", "600323.SH", "环境治理", "环境治理", "20261109"),
    (11, "拓斯达", "300607.SZ", "自动化设备", "自动化设备", "20261111"),
    (12, "马应龙", "600993.SH", "中药", "中药", "20261113"),
    (13, "春风动力", "603129.SH", "汽车服务及其他", "汽车服务及其他", "20261117"),
]

out = []
for idx, name, code, ind, note, in_date in POOL:
    daily = pro.daily(ts_code=code, start_date=START, end_date=DATE)
    if daily.empty:
        print("!! empty", name, code)
        continue
    daily = daily.sort_values("trade_date").reset_index(drop=True)
    adj = pro.adj_factor(ts_code=code, start_date=START, end_date=DATE).sort_values("trade_date")
    adj = adj.set_index("trade_date")["adj_factor"]
    base = adj.iloc[-1]
    daily["adj"] = daily["trade_date"].map(lambda d: base / adj[d])
    for c in ("open", "high", "low", "close"):
        daily[c] = daily[c] * daily["adj"]
    bs = pro.daily_basic(ts_code=code, trade_date=DATE,
                         fields="ts_code,trade_date,total_mv,circ_mv,turnover_rate,volume_ratio,pe_ttm,pb")
    b = bs.iloc[0].to_dict() if not bs.empty else {}
    rows = [{"d": r.trade_date, "o": round(r.open, 2), "h": round(r.high, 2),
             "l": round(r.low, 2), "c": round(r.close, 2),
             "v": float(r.vol), "a": float(r.amount)} for r in daily.itertuples()]
    last = rows[-1]
    # 入池日收盘（前复权）
    entry = next((r for r in rows if r["d"] == in_date), None)
    out.append({
        "idx": idx, "name": name, "code": code, "industry": ind, "note": note,
        "in_date": in_date,
        "series": rows,
        "close": last["c"], "pct": round(float(daily["pct_chg"].iloc[-1]), 2),
        "amount_yi": round(last["a"] / 1e5, 2),          # 千元 → 亿元
        "total_mv_yi": round(float(b.get("total_mv", 0)) / 1e4, 1),  # 万元 → 亿元
        "turnover": b.get("turnover_rate"), "pe_ttm": b.get("pe_ttm"), "pb": b.get("pb"),
        "entry_close": entry["c"] if entry else None,
        "entry_pct": round((last["c"] / entry["c"] - 1) * 100, 2) if entry else None,
    })
    print(f"[ok] {name:6s} {code} 收{last['c']:.2f} {out[-1]['pct']:+.2f}% "
          f"额{out[-1]['amount_yi']:.2f}亿 市值{out[-1]['total_mv_yi']:.1f}亿 "
          f"入池{entry['c'] if entry else '-'}→{out[-1]['entry_pct']}%")

(RPT / "pool.json").write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
print("saved", RPT / "pool.json", len(out))
