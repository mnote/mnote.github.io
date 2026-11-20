"""都业华 2026-11-20 午评（高级班·午盘）纪要 HTML（白底 · 上午版）

⛔ 用户 2026-11-11 禁令：只用日线 + 实时快照，不调用分钟级 K 线接口、不调用 czsc。
📏 篇幅硬约束：正文 ≤2000 中文字、表格 ≤4 张；K 线图保留、不计字数。

上午口径（11:30）来自腾讯 5 日分时点位 + 同花顺日线；13:15 新浪快照交叉校验。
输出：html/duyiehua-20261120-noon.html
"""
import json
import sys
from pathlib import Path

REPO = Path("/Users/maoling/workspace/mnote.github.io")
RPT = REPO / "reports/duyiehua-20261120"
D = json.loads((RPT / "data_20261120.json").read_text(encoding="utf-8"))
BR = json.loads((RPT / "breadth_20261120.json").read_text(encoding="utf-8"))
MK = json.loads((RPT / "morning_20261120.json").read_text(encoding="utf-8"))
IX, ST = D["index"], D["stocks"]
POOL = D["pools"]
SUF = "20261120N"

TITLE = "DYH 午评 - 2026-11-20（周五 低开下探创新低，3620未到）"

CSS = """<style>
    :root{--bg:#fff;--panel:#f8f9fb;--border:#e5e7eb;--text:#1f2937;--muted:#6b7280;
    --bull:#16a34a;--bullbg:#dcfce7;--up:#e63946;--down:#2a9d8f;--bear:#dc2626;--bearbg:#fee2e2;
    --neutral:#d97706;--neutbg:#fef3c7;--none:#6b7280;--nonebg:#f3f4f6;--accent:#2563eb;--accentbg:#dbeafe;--key:#7c3aed;}
    *{box-sizing:border-box}
    body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei","Segoe UI",sans-serif;
    background:var(--bg);color:var(--text);line-height:1.6;font-size:14.5px}
    .wrap{max-width:1200px;margin:0 auto;padding:26px 24px 60px}
    h1{font-size:24px;margin:0 0 5px}h2{font-size:18px;margin:26px 0 10px;padding-bottom:6px;border-bottom:2px solid var(--border)}
    p{margin:6px 0}a{color:var(--accent);text-decoration:none}
    .meta{color:var(--muted);font-size:12px}
    .hero{background:linear-gradient(135deg,#fff7ed,#fffdf7);border:1px solid #fdba74;border-radius:12px;padding:18px 22px;margin-bottom:14px}
    .hero h1{color:#9a3412}.hero .stance{font-size:14.5px;margin:7px 0 0}
    .grid4{display:grid;grid-template-columns:repeat(4,1fr);gap:11px}
    @media(max-width:900px){.grid4{grid-template-columns:1fr 1fr}}@media(max-width:700px){.grid4{grid-template-columns:1fr}}
    .kpi{background:#fff;border:1px solid var(--border);border-radius:8px;padding:10px 12px;text-align:center}
    .kpi .label{font-size:11.5px;color:var(--muted)}.kpi .val{font-size:18px;font-weight:600;margin:2px 0}
    .kpi .sub{font-size:11px;color:var(--muted)}
    table{width:100%;border-collapse:collapse;margin:9px 0;font-size:13px}
    th,td{padding:6px 8px;text-align:left;border-bottom:1px solid var(--border);vertical-align:top}
    th{background:var(--panel);font-weight:600;white-space:nowrap}
    .up{color:var(--up)}.down{color:var(--down)}.vol{color:var(--neutral);font-weight:600}
    .num{font-variant-numeric:tabular-nums;white-space:nowrap}
    .kn{color:var(--key);font-weight:600}
    .tag{display:inline-block;padding:1px 7px;border-radius:10px;font-size:11.5px;white-space:nowrap}
    .tag-bear{background:var(--bearbg);color:var(--bear)}
    .tag-bull{background:var(--bullbg);color:var(--bull)}
    .tag-neutral{background:var(--neutbg);color:var(--neutral)}
    .tag-none{background:var(--nonebg);color:var(--none)}
    .box{background:var(--panel);border-left:4px solid var(--accent);border-radius:6px;padding:11px 14px;margin:9px 0}
    .box-g{background:var(--bullbg);border-left-color:var(--bull)}
    .box-r{background:var(--bearbg);border-left-color:var(--bear)}
    .box-a{background:var(--accentbg);border-left-color:var(--accent)}
    img.chart{width:100%;max-width:100%;display:block;margin:10px 0 4px;border:1px solid var(--border);border-radius:8px;background:#fff}
    .cap{color:var(--muted);font-size:12px;margin:0 0 14px}
    .foot{margin-top:30px;padding-top:12px;border-top:1px solid var(--border);font-size:11.5px;color:var(--muted)}
</style>"""


def cls(v):
    return "up" if v > 0 else ("down" if v < 0 else "")


M = D["morning"]


def am(nm):
    """上午 11:30 口径：开/高/低/收 + 涨跌幅"""
    t = M[nm]["2026-11-20"]
    prev = D["index"][nm + "_snap"]["prev_close"] if nm in D["index"] else None
    if prev is None:
        prev = ST[nm]["snap"]["prev_close"]
    return {"o": t["am_open"], "h": t["am_high"], "l": t["am_low"], "c": t["am_close"],
            "prev": prev, "pct": round((t["am_close"] / prev - 1) * 100, 2),
            "amt_1130": t["amt_1130"] / 1e8}


sh = am("上证指数")
sz = am("深证成指")
cy = am("创业板指")
hs300 = am("沪深300")
kc = am("科创50")
now_sh = IX["上证指数_snap"]

# 11:30 同时点成交额同比
tx = D["tx_amount"]
amt_1130 = (tx["上证指数"]["2026-11-20"]["amt_1130"] + tx["深证成指"]["2026-11-20"]["amt_1130"]) / 1e8
amt_1130_prev = (tx["上证指数"]["2026-11-19"]["amt_1130"] + tx["深证成指"]["2026-11-19"]["amt_1130"]) / 1e8
amt_chg = (amt_1130 / amt_1130_prev - 1) * 100

# 个股上午口径
def amst(nm):
    t = M[nm]["2026-11-20"]
    prev = ST[nm]["snap"]["prev_close"]
    return {"o": t["am_open"], "h": t["am_high"], "l": t["am_low"], "c": t["am_close"],
            "prev": prev, "pct": round((t["am_close"] / prev - 1) * 100, 2),
            "amt_1130": t["amt_1130"] / 1e8}


def pctcls(v):
    return f'<span class="{cls(v)}">{v:+.2f}%</span>'


def mem(b, code):
    for m in MK[b]["members"]:
        if m["code"] == code:
            return m
    return None


def mempct(b, code):
    m = mem(b, code)
    return f'{m["name"]} {m["pct"]:+.2f}%' if m else "—"


def bkrow(b, teacher, detail):
    v = MK[b]
    return (f'<tr><td><b>{b}</b></td><td>{teacher}</td>'
            f'<td><b>{v["avg_pct"]:+.2f}%</b>（{v["up"]} 涨 {v["down"]} 跌，11:30 额 {v["amt_yi"]:.0f} 亿）<br>{detail}</td></tr>')


BKROWS = [
    bkrow("国产算力", "老师：有风险，不一定全起来，只有少数细分能走强",
           f'{mempct("国产算力","688041")}、{mempct("国产算力","603019")}、{mempct("国产算力","002261")}；'
           f'仅 {mempct("国产算力","688981")}、{mempct("国产算力","000158")} 逆势'),
    bkrow("半导体", "老师：风险外溢",
           f'{mempct("半导体","688041")}、{mempct("半导体","603986")}、{mempct("半导体","002371")}；'
           f'{mempct("半导体","688981")} 逆势'),
    bkrow("算力/CPO", "老师：不追涨",
           f'{mempct("算力/CPO","300502")} 唯一红盘；{mempct("算力/CPO","300308")}、{mempct("算力/CPO","601138")}、'
           f'{mempct("算力/CPO","300476")}'),
    bkrow("元件/PCB", "老师：PCB 较好，但走势并没有转强",
           f'{mempct("元件/PCB","002815")}、{mempct("元件/PCB","603228")}、{mempct("元件/PCB","002916")} 红；'
           f'{mempct("元件/PCB","002463")}、{mempct("元件/PCB","300476")}、{mempct("元件/PCB","002384")} 跌；'
           f'涨停池元件 6 只（中京电子/东晶电子/超声电子等）'),
    bkrow("AI视频/传媒", "老师：异动更像超跌反弹，不是止跌",
           f'{mempct("AI视频/传媒","300364")}、{mempct("AI视频/传媒","603533")}、{mempct("AI视频/传媒","300133")} 红；'
           f'{mempct("AI视频/传媒","300251")}、{mempct("AI视频/传媒","601595")} 跌'),
    bkrow("人形机器人", "老师：异动更像超跌反弹",
           f'{mempct("人形机器人","003021")} 领涨（低 73.65 拉到 80.49）、海天瑞声 +3.99%；'
           f'{mempct("人形机器人","603728")}、{mempct("人形机器人","300124")} 跌'),
    bkrow("电力/高股息", "老师：未点名（防御）",
           f'{mempct("电力/高股息","600886")}、{mempct("电力/高股息","600674")} 等 5 只全线红 —— 上午唯一'),
    bkrow("饮料制造", "老师：未点名（防御）",
           f'{mempct("饮料制造","605499")}、{mempct("饮料制造","300997")}、{mempct("饮料制造","605337")}'),
]

# 个股表
def strow(nm, topic, teacher, key, detail, act):
    s = amst(nm)
    return (f'<tr><td><b>{nm}</b><br><span class="meta">{topic}</span></td>'
            f'<td class="num"><span class="{cls(s["pct"])}">{s["c"]:.2f}</span> <span class="{cls(s["pct"])}">{s["pct"]:+.2f}%</span>'
            f'<br><span class="meta">高 {s["h"]:.2f} 低 {s["l"]:.2f}</span></td>'
            f'<td>{teacher}</td><td class="kn">{key}</td><td>{detail}</td>'
            f'<td><span class="tag {"tag-bear" if act=="不追" else "tag-neutral"}">{act}</span></td></tr>')


w = amst
ROWS = [
    strow("药明康德", "大医药", "不操作 · 上方压力高点无法突破，不满足买入", "157.8",
          f'低 <b>{w("药明康德")["l"]:.2f}</b>，高 {w("药明康德")["h"]:.2f}，距 157.8 差 '
          f'<b>{157.8-w("药明康德")["h"]:.2f}</b> 元；60 日低 131.90 未破', "等"),
    strow("中国船舶", "船舶", "不操作 · 下跌中枢没翻过上方压力位", "36.75",
          f'低 <b>{w("中国船舶")["l"]:.2f}</b>，距 36.75 差 <b>{36.75-w("中国船舶")["h"]:.2f}</b> 元', "等"),
    strow("瑞芯微", "半导体", "激进 · 等日线有力度底分型 + 接阳线后 2-3 天震荡", "220.7",
          f'低 <b>{w("瑞芯微")["l"]:.2f}</b> → 收 {w("瑞芯微")["c"]:.2f}（自低 +'
          f'{(w("瑞芯微")["c"]/w("瑞芯微")["l"]-1)*100:.1f}%），<b>异动成立、底分型未出</b>；'
          f'距 220.7 差 {220.7-w("瑞芯微")["c"]:.2f}', "等"),
    strow("伊利股份", "大消费", "不操作 · 走势强但不追涨；持仓看顶背驰", "31.9",
          f'最高 <b>{w("伊利股份")["h"]:.2f}</b> 逼近 60 日高 33.10，最低 {w("伊利股份")["l"]:.2f} 距 31.9 差 '
          f'<b>{w("伊利股份")["l"]-31.9:.2f}</b> 元 → <b>「当下没跌破」成立</b>', "不追"),
    strow("海天瑞声", "机器人", "池内中线（11/19 转入）· 本次未提及", "141",
          f'低 <b>{w("海天瑞声")["l"]:.2f}</b> → 收 {w("海天瑞声")["c"]:.2f}（自低 +'
          f'{(w("海天瑞声")["c"]/w("海天瑞声")["l"]-1)*100:.1f}%），<b>超跌反弹、离 141 还差 '
          f'{141-w("海天瑞声")["h"]:.2f} 元</b>', "等"),
    strow("兆易创新", "存储芯片", "无方法买点 · 底背驰可能成立，等破 224.6 出回抽三买", "224.6 / 233",
          f'低 <b>{w("兆易创新")["l"]:.2f}</b> <b>破 60 日低 212.00</b>，距 224.6 差 '
          f'{224.6-w("兆易创新")["h"]:.2f} 元、距 233 差 {233-w("兆易创新")["h"]:.2f} 元', "等"),
    strow("华丰科技", "连接器", "无方法买点 · 大阴线未止跌，等回调到 80.6 附近出止跌信号", "80.6",
          f'开 {w("华丰科技")["o"]:.2f} 高 {w("华丰科技")["h"]:.2f} 低 <b>{w("华丰科技")["l"]:.2f}</b> 收 '
          f'{w("华丰科技")["c"]:.2f} <b>{w("华丰科技")["pct"]:+.2f}%</b>（大阴线）；距 80.6 还差 '
          f'<b>{w("华丰科技")["c"]-80.6:.2f}</b>', "等"),
    strow("中芯国际", "国产算力", "谨慎 · 抗跌但昨日没出三买，等日线顶分型回抽", "120.6",
          f'高 <b>{w("中芯国际")["h"]:.2f}</b> 已破 120.6，收 {w("中芯国际")["c"]:.2f} '
          f'<b>{w("中芯国际")["pct"]:+.2f}%</b> 逆势红于上证 <b>'
          f'{w("中芯国际")["pct"]-sh["pct"]:.2f}pp</b>；缺回抽确认', "等"),
]

DEVS = [
    ("老师：「当前走势仍由宽基 ETF 放量所导致，可靠性不一定很高」",
     f'11:30 两市 <b>{amt_1130:,.0f} 亿</b> vs 昨同时点 {amt_1130_prev:,.0f} 亿 = <b>{amt_chg:+.2f}%</b>，'
     f'确为放量下跌；但「ETF 申购主导」本机无法拆分',
     "方向一致·无法核验"),
    ("老师：「临近中午小波拉升，使指数出现下影线」",
     f'上证 O{sh["o"]:.2f} → L{sh["l"]:.2f} → C{sh["c"]:.2f}，收在开盘价下方 '
     f'{sh["o"]-sh["c"]:.2f} 点 = 阴线带下影 ✓；<b>但创业板指 C{cy["c"]:.2f} 高于开盘 {cy["o"]:.2f}'
     f'（微阳十字星）</b>',
     "口径偏窄"),
    ("老师：「小级别下跌中枢上沿压力 3620 点或放低标准 3600 点」",
     f'上午最高 <b>{sh["h"]:.2f}</b>，差 <b>{3620-sh["h"]:.2f}</b> / {3600-sh["h"]:.2f} 点；'
     f'<b>3620 ≈ 11/16 上午收盘 3620.00</b>，较此前 3623（11/16 上午高点）微降 3 点',
     "门槛微降"),
    ("老师：「中线股，均没有出买点」",
     '中线只列 4 只（药明/船舶/瑞芯微/伊利），<b>未提 11/19 刚转中线的海天瑞声</b>；'
     '短线 3 只（兆易/华丰/中芯）',
     "池子待确认"),
    ("老师：「背驰段 / 小二买 / 顶背驰 / 日线有力度底分型」等缠论定性",
     '本机不跑分钟级与 czsc，<b>无法独立复算</b>，按老师口径引用；日线只能核前提：'
     f'上证、创业板<b>创 60 日新低</b>，兆易创新低 {w("兆易创新")["l"]:.2f} <b>破 60 日低 212.00</b>',
     "无法核验"),
]

html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{TITLE}</title>
{CSS}
</head>
<body>
<div class="wrap">

<div class="hero">
  <h1>📈 {TITLE}</h1>
  <div class="meta"><a href="/" style="color:#2563eb;text-decoration:none">← 返回首页</a><span style="color:#9ca3af"> · </span>上午版 · 数据截至 2026-11-20 11:30（13:15 快照交叉校验）</div>
  <p class="stance"><b>结论：指数进入潜在背驰段，但没见底；仓位要轻、不着急、不追涨。</b>
  上午上证低开 {sh['o']:.2f} 探 <b>{sh['l']:.2f}</b>（创 60 日新低）后回升，11:30 收 {sh['c']:.2f}
  （<span class="down">{sh['pct']:+.2f}%</span>）带下影线；<b>3620 / 3600 均未到</b>（差 {3620-sh['h']:.2f} / {3600-sh['h']:.2f} 点）。
  两市 11:30 成交 {amt_1130:,.0f} 亿、同比 <span class="vol">{amt_chg:+.2f}%</span> 放量下跌。
  <b>7 只标的无买点</b>；国产算力退潮，PCB 与传媒是超跌反弹。</p>
</div>

<div class="grid4">
  <div class="kpi"><div class="label">上证指数 · 创 60 日新低</div><div class="val down">{sh['pct']:+.2f}%</div><div class="sub">{sh['c']:.2f} · 低 {sh['l']:.2f}（破 3547.94）</div></div>
  <div class="kpi"><div class="label">成长端（11:30）</div><div class="val down">创业板 {cy['pct']:+.2f}%</div><div class="sub">科创50 {kc['pct']:+.2f}% · 深成 {sz['pct']:+.2f}% · 沪深300 {hs300['pct']:+.2f}%</div></div>
  <div class="kpi"><div class="label">两市成交额（11:30 累计）</div><div class="val vol">{amt_1130:,.0f} 亿</div><div class="sub vol">同比 {amt_chg:+.2f}%（昨同刻 {amt_1130_prev:,.0f}）</div></div>
  <div class="kpi"><div class="label">涨 / 跌家数（13:15 快照）</div><div class="val"><span class="up">{BR['up']}</span> / <span class="down">{BR['down']}</span></div><div class="sub">跌占 {BR['down']/BR['n']*100:.0f}% · 涨停 {POOL['zt']['tc']} · 跌停 {POOL['dt']['tc']} · 炸板 {POOL['zb']['tc']}</div></div>
</div>

<h2>一、指数：低开下探创新低，尾段小波拉升留出下影线</h2>
<p>四条判据逐条核：① <b>「低开下探、中午小波拉升出现下影线」</b> —— 上证开 {sh['o']:.2f}（低开 {(sh['o']/sh['prev']-1)*100:.2f}%）→ 探 {sh['l']:.2f} → 11:30 收 {sh['c']:.2f}，<b>收在开盘价下方 {sh['o']-sh['c']:.2f} 点 = 阴线带下影</b> ✓；② <b>「上午破下去，进入潜在背驰段」</b> —— 上证破 11/19 低 3547.94、深成破 10505.84、创业板破 2263.74、沪深300 破 3937.75，<b>四大指数同步创 60 日新低</b> ✓；③ <b>「3620 / 3600 突破后确认」</b> —— 上午最高 {sh['h']:.2f}，都没摸到；④ <b>「由宽基 ETF 放量所致」</b> —— 11:30 两市 {amt_1130:,.0f} 亿 vs 昨同时点 {amt_1130_prev:,.0f} 亿（<span class="vol">{amt_chg:+.2f}%</span>），<b>放量但指数创新低</b>。</p>
<p>纪律照抄：<b>「仓位要轻、不着急、控制出手次数，想尝试轻仓」</b>、<b>「下午快速拉升不追涨」</b>（离背驰段所在小级别中枢太近，空间压缩、易转震荡）、<b>「等突破 3620 或 3600 完成确认」</b>——最后一条是唯一可执行条件。</p>
<img class="chart" src="../charts/000001_SH_DY_{SUF}.png">
<img class="chart" src="../charts/399006_SZ_DY_{SUF}.png">

<h2>二、板块：超跌反弹不是止跌，国产算力在退潮</h2>
<table>
  <tr><th>方向（自建篮子 · 上午 11:30）</th><th>老师口径</th><th>实测（均值 · 涨跌家数 · 个股）</th></tr>
  {''.join(BKROWS)}
</table>
<p><b>三条要记的：</b>① <b>「异动是超跌反弹、不是止跌」成立</b> —— 传媒篮子 {MK['AI视频/传媒']['avg_pct']:+.2f}%、机器人 {MK['人形机器人']['avg_pct']:+.2f}%，靠兆威机电 {mempct('人形机器人','003021')} 等龙头单点拉升；② <b>「PCB 较好但没转强」精确成立</b> —— 崇达 {mempct('元件/PCB','002815')}、景旺 {mempct('元件/PCB','603228')} 红，沪电 {mempct('元件/PCB','002463')}、胜宏 {mempct('元件/PCB','300476')} 跌；③ <b>「国产算力有风险」成立</b> —— 篮子 {MK['国产算力']['avg_pct']:+.2f}%，海光 {mempct('国产算力','688041')}、曙光 {mempct('国产算力','603019')} 重挫，<b>仅中芯与常山北明逆势</b>；上午唯一全线红盘是电力/高股息 {MK['电力/高股息']['avg_pct']:+.2f}%（5/0）。</p>

<h2>三、7 只标的：全部无方法买点</h2>
<table>
  <tr><th>标的 / 题材</th><th>11:30 收盘</th><th>老师定性（老师口径）</th><th>关键位</th><th>实测印证（日线触达）</th><th>动作</th></tr>
  {''.join(ROWS)}
</table>
<img class="chart" src="../charts/603259_SH_DY_{SUF}.png">
<img class="chart" src="../charts/600150_SH_DY_{SUF}.png">
<img class="chart" src="../charts/603893_SH_DY_{SUF}.png">
<img class="chart" src="../charts/600887_SH_DY_{SUF}.png">
<img class="chart" src="../charts/688787_SH_DY_{SUF}.png">
<img class="chart" src="../charts/603986_SH_DY_{SUF}.png">
<img class="chart" src="../charts/688629_SH_DY_{SUF}.png">
<img class="chart" src="../charts/688981_SH_DY_{SUF}.png">

<h2>四、下午关注（可验证条件）</h2>
<div class="box box-a">
① <b>上证 {sh['l']:.2f}（今创 60 日新低）</b>：下午破了 = 背驰段向下延续；守住并收复 {sh['o']:.2f}（开盘价）才算日内转强。<br>
② <b>3620 / 3600</b>：上午最高 {sh['h']:.2f}，差 {3620-sh['h']:.2f} / {3600-sh['h']:.2f} 点 —— <b>突破并站稳才是短线止跌第一个确认</b>，此前拉升都不追。<br>
③ <b>量能</b>：11:30 已 {amt_chg:+.2f}%，下午若继续放量而指数不抬头 = 放量更无效，仓位更该压住。<br>
④ <b>国产算力</b>：海光 {mempct('国产算力','688041')}、曙光 {mempct('国产算力','603019')} 若跌幅扩大，指数靠权重企稳也难。<br>
⑤ <b>宽度</b>：跌家数 {BR['down']}（{BR['down']/BR['n']*100:.0f}%）、跌停 {POOL['dt']['tc']}、炸板 {POOL['zb']['tc']} —— 收敛前不接超跌反弹票（PCB / 传媒 / 机器人）。
</div>
<div class="box box-r">
<b>纪律（原文明写）：</b>① <b>仓位要轻、不着急、控制出手次数</b>，想尝试就轻仓；② <b>下午快速拉升不追涨</b>（离背驰段中枢太近，空间压缩、易转震荡）；③ <b>被套者提前想好拉升应对</b>：判断出中期低点就高抛价看高些，没出低点则反弹到压力位主动高抛降仓；<b>信念强少抛点做差价，信念弱多抛点</b>。
</div>

<h2>五、偏差记录</h2>
<table>
  <tr><th>老师原文</th><th>实测</th><th>判定</th></tr>
  {''.join(f'<tr><td>{a}</td><td>{b}</td><td><span class="tag tag-none">{c}</span></td></tr>' for a, b, c in DEVS)}
</table>
<p style="color:var(--muted);font-size:12.5px">说明：原文「低开下探」「破下去进入潜在背驰段」「PCB 较好但没转强」「传媒与机器人异动是超跌反弹」「国产算力有风险」「伊利当下没跌破 31.9」「兆易底背驰有可能成立」「中线短线均无买点」在 11/20 上午<b>均成立</b>，伊利最低 {w('伊利股份')['l']:.2f} 距 31.9 差 {w('伊利股份')['l']-31.9:.2f} 元为精确命中。上表 5 条为口径偏窄、门槛变动、池子待确认与无法复算。</p>

<div class="foot">
  <p>来源：都业华《高级班》2026-11-20 午盘（高级班·午盘），执业编号 A0400626100004。<b>仅供参考，不作为买卖依据，据此操作风险自担。投资有风险，入市需谨慎！</b></p>
  <p><b>口径：</b>上午开/高/低/收与 11:30 累计成交额取腾讯 5 日分时点位（同花顺日线 + 新浪 13:15 快照交叉校验，最后一根 K 线未走完、量为上午累计）；板块为自建篮子均值（成分逐一列出）；涨跌家数取新浪全 A {BR['n']} 只 13:15 快照；涨停/跌停用东财池。缠论定性按老师口径引用。</p>
</div>

</div>
</body>
</html>
"""

out = REPO / "html/duyiehua-20261120-noon.html"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from fix_mobile_tables import patch_html
out.write_text(patch_html(html), encoding="utf-8")
print("saved", out, len(html))
