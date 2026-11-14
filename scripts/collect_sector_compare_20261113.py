"""板块对比页数据采集（半导体 / GPU / 算力 / CPO / 存储 / 端侧 / 人形机器人）。

口径（2026-11-13 收盘）：
  半导体 = 申万二级 801081
  算力   = 申万三级 851024 通信网络设备 + 850703 其他计算机设备 + 850822 印制电路板
  机器人 = 申万三级 850781 + 人形机器人核心零部件
  GPU / CPO / 存储 / 端侧 = 手工核心池（公开常识口径，见 AGENTS.md §五）
Top8 一律按总市值。

用法： python3 scripts/collect_sector_compare_20261113.py
产物： reports/sector-compare-20261113/data_20261113.json
只用日线级别；不用分钟线、不用 czsc。
"""
import json
import os
import time
from pathlib import Path

import pandas as pd
import tushare as ts

TOKEN = os.environ.get("TUSHARE_TOKEN") or "a4d50511c45b1f214ca32edbde1ba21241d5bb37c9f66f66a91025b3"
pro = ts.pro_api(TOKEN)
REPO = Path("/Users/maoling/workspace/mnote.github.io")
OUT = REPO / "reports/sector-compare-20261113"
DATE = "20261113"

# ── 手工池（AI 芯片 / 光模块光器件 / 存储 / 端侧）──────────────────────
GPU = ["688256.SH", "688041.SH", "688801.SH", "688802.SH", "688795.SH",
       "688521.SH", "300474.SZ", "603893.SH"]
CPO = ["300308.SZ", "300502.SZ", "300394.SZ", "002281.SZ", "300570.SZ", "603083.SH",
       "300548.SZ", "301205.SZ", "688498.SH", "688313.SH", "688205.SH", "688195.SH",
       "300620.SZ", "688048.SH", "600487.SH", "600522.SH", "601869.SH", "000988.SZ",
       "300757.SZ", "000936.SZ", "002902.SZ"]
STORE = ["688825.SH", "603986.SH", "301308.SZ", "688525.SH", "001309.SZ", "300223.SZ",
         "688110.SH", "688766.SH", "688123.SH", "688008.SH", "300042.SZ", "688416.SH",
         "000021.SZ", "300475.SZ", "688233.SH"]
EDGE = ["603893.SH", "300458.SZ", "688099.SH", "688608.SH", "688018.SH", "688332.SH",
        "688049.SH", "300613.SZ", "688249.SH", "603501.SH", "002920.SZ", "002241.SZ",
        "001314.SZ", "688036.SH", "300866.SZ", "300496.SZ", "688595.SH", "688045.SH",
        "688213.SH"]
ROBOT_EXTRA = ["688017.SH", "002050.SZ", "601689.SH", "002472.SZ", "603728.SH", "003021.SZ",
               "300580.SZ", "601100.SH", "301368.SZ", "002896.SZ", "002979.SZ", "603662.SH",
               "002527.SZ", "688582.SH", "688836.SH"]
SW_L3 = {"851024.SI": "通信网络设备及器件", "850703.SI": "其他计算机设备",
         "850822.SI": "印制电路板", "850781.SI": "机器人"}


def retry(fn, n=4, **kw):
    for i in range(n):
        try:
            df = fn(**kw)
            if df is not None and not df.empty:
                return df
        except Exception as e:
            if i == n - 1:
                print(f"    [ERR] {kw} {e}", flush=True)
            time.sleep(1.2)
    return pd.DataFrame()


def main():
    OUT.mkdir(parents=True, exist_ok=True)

    # ── 1. 全市场行情 + 估值（各一次全量）────────────────────────
    full = retry(pro.daily, trade_date=DATE)
    basics = retry(pro.daily_basic, trade_date=DATE)
    sb = retry(pro.stock_basic, exchange="", list_status="L",
               fields="ts_code,symbol,name,industry,list_date")
    print(f"[data] daily {len(full)} / basic {len(basics)} / sb {len(sb)}", flush=True)

    df = full.merge(basics[["ts_code", "total_mv", "circ_mv", "turnover_rate",
                             "volume_ratio", "pe_ttm", "pb", "ps_ttm"]],
                    on="ts_code", how="left")
    df = df.merge(sb[["ts_code", "name", "list_date"]], on="ts_code", how="left")
    df["amt_yi"] = df["amount"] / 1e5
    df["mv_yi"] = df["total_mv"] / 1e4
    df["code"] = df["ts_code"].str[:6]
    snap = df.set_index("ts_code", drop=False).to_dict("index")

    # ── 2. 申万成分 ───────────────────────────────────────────────
    semi = retry(pro.index_member_all, l2_code="801081.SI")["ts_code"].tolist()
    l3 = {}
    for code in SW_L3:
        l3[code] = retry(pro.index_member_all, l3_code=code)["ts_code"].tolist()
        time.sleep(0.2)
    print(f"[sw] 半导体 {len(semi)} / " +
          " / ".join(f"{v} {len(l3[k])}" for k, v in SW_L3.items()), flush=True)

    pools = {
        "半导体": semi,
        "GPU": GPU,
        "算力": l3["851024.SI"] + l3["850703.SI"] + l3["850822.SI"],
        "CPO": CPO,
        "存储": STORE,
        "端侧": EDGE,
        "机器人": l3["850781.SI"] + ROBOT_EXTRA,
    }

    # ── 3. 每池 Top8 + 池统计 ─────────────────────────────────────
    tops, stats = {}, {}
    need_hist = set()
    for name, codes in pools.items():
        uniq = sorted(set(codes))
        rows = [snap[c] for c in uniq if c in snap]
        rows.sort(key=lambda r: -(r["mv_yi"] or 0))
        top8 = rows[:8]
        tops[name] = top8
        need_hist |= {r["ts_code"] for r in top8}
        pcts = [r["pct_chg"] for r in rows if r["pct_chg"] is not None]
        stats[name] = {
            "n": len(rows), "avg_pct": round(sum(pcts) / len(pcts), 2),
            "up": sum(1 for p in pcts if p > 0), "down": sum(1 for p in pcts if p < 0),
            "amount_yi": round(sum(r["amt_yi"] for r in rows)),
            "best": [r["name"] for r in sorted(rows, key=lambda r: -r["pct_chg"])[:3]],
        }
        print(f"  {name:<6} n={len(rows):>4} 均值 {stats[name]['avg_pct']:>6.2f}%  "
              f"涨{stats[name]['up']}/跌{stats[name]['down']}  额 {stats[name]['amount_yi']:>6.0f}亿",
              flush=True)

    # ── 4. 60 日位置 / 20 日涨跌 / 量比（Top8 逐只）────────────────
    print(f"\n[hist] {len(need_hist)} 只", flush=True)
    hist = {}
    for c in sorted(need_hist):
        h = retry(pro.daily, ts_code=c, start_date="20260801", end_date=DATE)
        if h.empty:
            continue
        h = h.sort_values("trade_date").reset_index(drop=True)
        last, w = h.iloc[-1], h.tail(60)
        hist[c] = {
            "bars": int(len(h)),
            "from_hi": round((last["close"] / w["high"].max() - 1) * 100, 1),
            "from_lo": round((last["close"] / w["low"].min() - 1) * 100, 1),
            "chg20": round((last["close"] / h["close"].iloc[-21] - 1) * 100, 1) if len(h) > 21 else None,
            "hi60": round(w["high"].max(), 2), "lo60": round(w["low"].min(), 2),
            "vr20": round((last["amount"] / 1e5) / ((w["amount"].tail(20) / 1e5).mean()), 2),
            "hi_date": str(w.loc[w["high"].idxmax(), "trade_date"]),
        }
        time.sleep(0.15)
    print(f"[hist] 完成 {len(hist)} 只", flush=True)

    # ── 5. 落盘 ────────────────────────────────────────────────────
    payload = {
        "date": DATE,
        "weekday": "周五",
        "title": "板块对比 - 2026-11-13（周五 七方向 Top8 对比）",
        "pools_meta": {
            "半导体": "申万二级 801081",
            "GPU": "AI 加速卡/图形 GPU 手工池",
            "算力": "申万三级 851024+850703+850822",
            "CPO": "光模块/光器件/光纤 手工池",
            "存储": "存储设计+制造+模组 手工池",
            "端侧": "端侧 SoC/AIoT/终端 手工池",
            "机器人": "申万三级 850781 + 人形核心零部件",
        },
        "stats": stats,
        "tops": {k: [{kk: (round(vv, 2) if isinstance(vv, float) else vv)
                       for kk, vv in r.items()} for r in v] for k, v in tops.items()},
        "hist": hist,
    }
    (OUT / f"data_{DATE}.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[out] {OUT / f'data_{DATE}.json'}", flush=True)


if __name__ == "__main__":
    main()
