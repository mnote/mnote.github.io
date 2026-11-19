"""11/19 午评 · 东财行业/概念板块快照（盘中口径，免登录）

⛔ 只用实时快照，不调用分钟级 K 线 / czsc。
输出：reports/duyiehua-20261119/sectors_20261119.json
"""
import json
import subprocess
import time
from pathlib import Path

REPO = Path("/Users/maoling/workspace/mnote.github.io")
RPT = REPO / "reports/duyiehua-20261119"
RPT.mkdir(parents=True, exist_ok=True)
UA = ["User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"]


def boards(fs):
    out = []
    for pn in range(1, 8):
        url = (f"https://push2.eastmoney.com/api/qt/clist/get?pn={pn}&pz=100&po=1&np=1&fltt=2&invt=2"
               f"fid=f3&fs={fs}&fields=f12,f14,f3,f104,f105,f128,f136,f62")
        for i in range(3):
            r = subprocess.run(["curl", "-s", "--max-time", "20", "-H", UA[0], url],
                               capture_output=True, text=True)
            try:
                js = json.loads(r.stdout)
                diff = (js.get("data") or {}).get("diff") or []
            except Exception:
                diff = []
                time.sleep(1.0 + i)
                continue
            if not diff:
                break
            out += diff
            break
        time.sleep(0.5)
    return out


def norm(rows):
    return {b["f14"]: {"code": b["f12"], "pct": b["f3"], "up": b["f104"], "down": b["f105"],
                       "leader": b["f128"], "leader_pct": b["f136"],
                       "main_net_yi": round((b.get("f62") or 0) / 1e8, 2)} for b in rows}


ind = norm(boards("m:90+t:2"))
con = norm(boards("m:90+t:3"))
(RPT / "sectors_20261119.json").write_text(
    json.dumps({"行业": ind, "概念": con}, ensure_ascii=False, indent=1), encoding="utf-8")

print("=== 行业板块涨幅 TOP12 ===")
for k, v in sorted(ind.items(), key=lambda x: -(x[1]["pct"] or -99))[:12]:
    print(f"  {k:<14} {v['pct']:+.2f}%  {v['up']}涨/{v['down']}跌  领涨 {v['leader']} {v['leader_pct']:+.2f}%  主力{v['main_net_yi']}亿")
print("=== 行业板块跌幅 TOP8 ===")
for k, v in sorted(ind.items(), key=lambda x: (x[1]["pct"] or 0))[:8]:
    print(f"  {k:<14} {v['pct']:+.2f}%  {v['up']}涨/{v['down']}跌")

print("\n=== 关注概念 ===")
KEY = ["半导体", "芯片", "国产芯片", "算力概念", "CPO概念", "东数西算", "华为昇腾",
       "AI视频", "短剧互动游戏", "传媒", "文化传媒", "游戏", "人形机器人", "机器人概念",
       "光刻机", "AI眼镜", "消费电子", "光伏设备", "光伏概念", "液冷服务器", "数据要素"]
for k in KEY:
    for src, d in (("概念", con), ("行业", ind)):
        if k in d:
            v = d[k]
            print(f"  [{src}] {k:<12} {v['pct']:+.2f}%  {v['up']}涨/{v['down']}跌  主力{v['main_net_yi']}亿")
