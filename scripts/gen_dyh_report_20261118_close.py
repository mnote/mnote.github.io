"""都业华 2026-11-18 收评（高级班）· 纪要 HTML（白底 · 收盘版）

⛔ 用户 2026-11-11 禁令：只用日线 + 收盘快照，不调用分钟级 K 线、不调用 czsc。
📏 篇幅硬约束：正文 ≤2000 中文字、表格 ≤4 张；K 线图保留、不计字数。

输出：html/duyiehua-20261118.html
"""
import json
import sys
from pathlib import Path

REPO = Path("/Users/maoling/workspace/mnote.github.io")
RPT = REPO / "reports/duyiehua-20261118"
D = json.loads((RPT / "data_20261118_close.json").read_text(encoding="utf-8"))
BR = json.loads((RPT / "breadth_20261118_close.json").read_text(encoding="utf-8"))
CM = json.loads((RPT / "em_concepts_close.json").read_text(encoding="utf-8"))
IX, ST, BK = D["index"], D["stocks"], D["baskets"]
POOL = D["pools"]
SUF = "20261118C"

TITLE = "DYH 收评 - 2026-11-18（周三 高开阴线创新低，3623未破）"

CSS = """<style>
  :root{--bg:#fff;--panel:#f8f9fb;--border:#e5e7eb;--text:#1f2937;--muted:#6b7280;
    --bull:#16a34a;--bullbg:#dcfce7;--up:#e0392e;--down:#26a69a;--bear:#dc2626;--bearbg:#fee2e2;
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


def sp(n):
    return ST[n]["snap"]


def px(n):
    s = sp(n)
    return f'<span class="{cls(s["pct"])}">{s["close"]:.2f} ({s["pct"]:+.2f}%)</span>'


def cfind(name):
    for c in CM:
        if c["name"] == name:
            return c
    return None


sh, cy, kc, sz, hs = (IX["上证指数_snap"], IX["创业板指_snap"], IX["科创50_snap"],
                      IX["深证成指_snap"], IX["沪深300_snap"])
amt = D["amount"]
prev_amt = (D["prev_day"]["上证指数"]["20261117"]["amt_yi"]
            + D["prev_day"]["深证成指"]["20261117"]["amt_yi"])
amt_g = (amt["total_yi"] / prev_amt - 1) * 100
tx = D["tx_amount"]
amt_1130 = (tx["sh"]["20261118"]["amt_1130"] + tx["sz"]["20261118"]["amt_1130"]) / 1e8
amt_1130_prev = (tx["sh"]["20261117"]["amt_1130"] + tx["sz"]["20261117"]["amt_1130"]) / 1e8
amt_1130_g = (amt_1130 / amt_1130_prev - 1) * 100

s_sh = sp("药明康德")
s_csg = sp("中国船舶")
s_rxw = sp("瑞芯微")
s_yl = sp("伊利股份")
s_htr = sp("海天瑞声")
s_zy = sp("兆易创新")
s_mt = sp("模塑科技")
s_cyp = sp("长盈精密")

BANKS = BK["银行"]["members"]
DRINKS = BK["饮料制造"]["members"]
CPO = BK["算力/CPO"]["members"]
ROBO = BK["人形机器人"]["members"]
MEDIA = BK["AI视频/传媒"]["members"]
SEMI = BK["半导体"]["members"]

HS = cfind("华为概念")
HS_RISE = cfind("华为昇腾")
SLC = cfind("算力概念")
DXS = cfind("东数西算")
CPO_C = cfind("CPO概念")

# ---------- 板块表 ----------
BKROWS = [
    ("国产算力（华为链）", "老师：二类热点 · 国产算力",
     f'算力概念 <b>{SLC["pct"]:+.2f}%</b>（主力 {SLC["main_net"]/1e8:+.0f} 亿，涨 {SLC["up"]}/跌 {SLC["down"]}）、'
     f'东数西算 <b>{DXS["pct"]:+.2f}%</b>（板块涨幅第一）、CPO 概念 {CPO_C["pct"]:+.2f}%、'
     f'华为昇腾 {HS_RISE["pct"]:+.2f}%；但<b>华为概念整体 {HS["pct"]:+.2f}%</b>（涨 {HS["up"]}/跌 {HS["down"]}）'),
    ("算力租赁 / IDC", "老师：算力租赁也有些表现",
     f'涨停池 IT服务Ⅱ {POOL["zt"]["pool"][0].get("hybk", "") and ""}7 家 + 通信服务 5 + 计算机设备 3，'
     f'美利云、城地香江、华胜天成、真视通、常山北明、卡莱特涨停 —— 集中在 IDC 与算力租赁'),
    ("高股息 / 红利", "老师：内部出现分化",
     f'公路 {BK["公路"]["avg_pct"]:+.2f}%、电力/高股息 {BK["电力/高股息"]["avg_pct"]:+.2f}%、'
     f'家电 {BK["家电"]["avg_pct"]:+.2f}%、煤炭/石油 {BK["煤炭/石油"]["avg_pct"]:+.2f}% 全线红；'
     f'<b>银行 {BK["银行"]["avg_pct"]:+.2f}%</b>（涨 {BK["银行"]["up"]}/跌 {BK["银行"]["down"]}）掉队'),
    ("饮料制造 / 白酒", "老师：走势不太对劲，防范短线高点",
     f'<b>{BK["饮料制造"]["avg_pct"]:+.2f}%</b>（0 涨 5 跌）：欢乐家 {DRINKS[2]["pct"]:+.2f}%、'
     f'李子园 {DRINKS[4]["pct"]:+.2f}%、东鹏饮料 {DRINKS[0]["pct"]:+.2f}%；'
     f'白酒概念 -1.56%（涨 5/跌 36）、酿酒行业 -0.89%'),
    ("前期强势补跌", "老师：算力若延续向下不一定顶得住",
     f'AI视频/传媒 {BK["AI视频/传媒"]["avg_pct"]:+.2f}%（0 涨 7 跌，华策影视 {MEDIA[1]["pct"]:+.2f}%）、'
     f'人形机器人 {BK["人形机器人"]["avg_pct"]:+.2f}%（1 涨 8 跌，兆威机电 {ROBO[5]["pct"]:+.2f}%）'),
]

# ---------- 标的表 ----------
ROWS = [
    ("药明康德 603259", "大医药", "不操作 · 等突破 157.8 出 15 分钟底分型三买；或止跌后出日线有力度底分型 + 收盘站住 148",
     "157.8 / 148",
     f'收 {s_sh["close"]:.2f} <b>{s_sh["pct"]:+.2f}%</b>，最高 {s_sh["high"]:.2f} 未触 157.8（差 {157.8-s_sh["high"]:.2f}）、'
     f'<b>收盘未站住 148</b>；最低 {s_sh["low"]:.2f} 破 11/17 低 142.20，跌破 MA5/MA10', "等"),
    ("中国船舶 600150", "船舶", "不操作 · 等突破 36.75 出 15 分钟底分型回抽确认",
     "36.75",
     f'收 {s_csg["close"]:.2f} <b>{s_csg["pct"]:+.2f}%</b>，收在全天最高，量比 129%（池内最强）；'
     f'距 36.75 差 {36.75-s_csg["high"]:.2f} 元', "等"),
    ("瑞芯微 603893", "端侧AI", "不操作 · 等日线有力度底分型（激进）；等共振或突破上沿出三买（稳健）",
     "220.7 / 208",
     f'收 {s_rxw["close"]:.2f} <b>{s_rxw["pct"]:+.2f}%</b>，最低 {s_rxw["low"]:.2f} <b>再破 208 与 220.7</b>，'
     f'跌破 MA20 205.45，底分型未出', "等"),
    ("伊利股份 600887", "大消费", "不操作 · 不追涨，设好止损；有效击穿 31.96 = 顶背驰大概率成立",
     "31.96",
     f'最高 {s_yl["high"]:.2f} 创 60 日新高，收 {s_yl["close"]:.2f} <b>{s_yl["pct"]:+.2f}%</b> 贴平、量比 100%；'
     f'<b>最低 {s_yl["low"]:.2f}，距 31.96 仅差 {31.96-s_yl["low"]:.2f} 元未击穿</b>', "不追"),
    ("海天瑞声 688787", "机器人", "不操作 · 先观察调整能否止跌，辅助 15 分钟二买",
     "141",
     f'收 {s_htr["close"]:.2f} <b>{s_htr["pct"]:+.2f}%</b>，最低 {s_htr["low"]:.2f} <b>破 11/17 低 91.99</b>；'
     f'量比 66% 缩量下跌，距 60 日低 76.54 还有 {76.54/s_htr["low"]*100-100:.0f}%', "等"),
    ("兆易创新 603986", "存储芯片", "不操作 · 等日线有力度底分型出现、收复 233 后的回抽三买",
     "233",
     f'收 {s_zy["close"]:.2f} <b>{s_zy["pct"]:+.2f}%</b> 反弹，量比 78% 缩量；'
     f'最高 {s_zy["high"]:.2f} <b>差 {233-s_zy["high"]:.2f} 元未收复 233</b>', "等"),
    ("模塑科技 000700", "人形机器人", "不操作 · 结构跌破支撑向下延续转弱，<b>短线剔除跟踪</b>",
     "14.95",
     f'收 {s_mt["close"]:.2f} <b>{s_mt["pct"]:+.2f}%</b>，最低 {s_mt["low"]:.2f} <b>远低于 14.95 支撑</b>，'
     f'量比 62%', "剔除"),
    ("长盈精密 300115", "人形机器人", "不操作 · 延续下跌破位、类二买结构不再，<b>短线剔除跟踪</b>",
     "23.86",
     f'收 {s_cyp["close"]:.2f} <b>{s_cyp["pct"]:+.2f}%</b>，最低 {s_cyp["low"]:.2f} <b>破 11/17 低 23.86</b>，'
     f'量比 95%', "剔除"),
]

DEVS = [
    ("老师：「二类热点：国产算力（华为概念）」",
     f'算力概念 {SLC["pct"]:+.2f}%、东数西算 {DXS["pct"]:+.2f}%、华为昇腾 {HS_RISE["pct"]:+.2f}%；'
     f'但<b>华为概念整体 {HS["pct"]:+.2f}%</b>（涨 {HS["up"]}/跌 {HS["down"]}）',
     "方向对 · 口径窄"),
    ("老师：「高股息内部出现分化，银行有些品种走不出去」",
     f'银行 {BK["银行"]["avg_pct"]:+.2f}%（招商 {BANKS[0]["pct"]:+.2f}%、兴业 {BANKS[4]["pct"]:+.2f}%）；'
     f'而电力 {BK["电力/高股息"]["avg_pct"]:+.2f}%、公路 {BK["公路"]["avg_pct"]:+.2f}% 仍全红',
     "分化成立 · 更强"),
    ("老师：「兆易创新内部有做 1 分钟下跌中枢迹象」",
     f'今日实测反弹 {s_zy["pct"]:+.2f}%、量比 78%，未收复 233',
     "无法核验"),
    ("老师：「伊利今日顶背驰没出现，但力度放不出来」",
     f'最低 {s_yl["low"]:.2f} <b>距 31.96 仅 {31.96-s_yl["low"]:.2f} 元</b>，收盘贴平、量比 100%',
     "精确命中"),
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
  <div class="meta"><a href="/" style="color:#2563eb;text-decoration:none">← 返回首页</a><span style="color:#9ca3af"> · </span>收盘版 · 数据截至 2026-11-18 15:00</div>
  <p class="stance"><b>结论：高开阴线、盘中创 60 日新低；3623 未破 → 仍是下跌中枢震荡，总仓 ≤4 成、少动多看。</b>
  上证开 3596.55 既是最高也是开盘价，盘中最低 <b>3560.45 创 60 日新低</b>，收 3587.83 <b>收在开盘价下方 = 阴线</b>，
  距压力 3623 差 26.45 点。跌家数 {BR['down']}（{BR['down']/BR['n']*100:.0f}%）、涨停 {POOL['zt']['tc']} vs 跌停 {POOL['dt']['tc']}。
  池内 <b>8 只全部无方法买点</b>，模塑科技、长盈精密被剔除跟踪。</p>
</div>

<div class="grid4">
  <div class="kpi"><div class="label">上证指数 · 收阴创新低</div><div class="val down">{sh['pct']:+.2f}%</div><div class="sub">{sh['close']:.2f} · 低 {sh['low']:.2f} 创 60 日新低</div></div>
  <div class="kpi"><div class="label">成长端 / 权重</div><div class="val up">{kc['pct']:+.2f}% / <span class="down">{cy['pct']:+.2f}%</span></div><div class="sub">科创50 / 创业板指 · 沪深300 {hs['pct']:+.2f}% · 深成 {sz['pct']:+.2f}%</div></div>
  <div class="kpi"><div class="label">两市成交额（全天）</div><div class="val vol">{amt['total_yi']:,.0f} 亿</div><div class="sub vol">环比 {amt_g:+.2f}%（昨 {prev_amt:,.0f} 亿）</div></div>
  <div class="kpi"><div class="label">涨 / 跌家数</div><div class="val"><span class="up">{BR['up']}</span> / <span class="down">{BR['down']}</span></div><div class="sub">涨停 {POOL['zt']['tc']} · 跌停 {POOL['dt']['tc']} · 炸板 {POOL['zb']['tc']}</div></div>
</div>

<h2>一、指数：高开阴线、盘中创新低，3623 未破</h2>
<p>老师三个判据逐条对上：① <b>「高开后走势运行沉闷，盘中创出新低，收盘收出一根阴线」</b> —— 上证开 {sh['open']:.2f}（高开 +0.33%）<b>同时就是全天最高</b>，开盘后没再冲高；盘中最低 <b>{sh['low']:.2f}</b>，破 11/17 的 3565.59，是 60 日新低；收盘 {sh['close']:.2f} <b>收在开盘价下方 0.24% = 阴线</b>。② <b>「突破压力 3623 点后出分型回抽确认」</b> —— 今日最高 {sh['high']:.2f}，<b>差 26.45 点没触及</b>，向上路径未打开。③ <b>「没有日线有力度底分型即没有止跌」</b> —— 收盘仍在 MA5 {3613.03:.0f} / MA10 {3640.94:.0f} / MA20 {3648.40:.0f} 三线下方。</p>
<p>结构上是<b>指数收阴、宽度更差</b>：跌 {BR['down']} 家占 {BR['down']/BR['n']*100:.0f}%，跌超 5% {BR['down_5']} 家、涨停仅 {POOL['zt']['tc']} 家、炸板 {POOL['zb']['tc']} 家；两市成交 {amt['total_yi']:,.0f} 亿环比 <span class="vol">{amt_g:+.2f}%</span>，11:30 同时点同比 <span class="vol">{amt_1130_g:+.2f}%</span> —— <b>缩量阴跌、赚钱效应差</b>，对应老师「市场弱时做好风控，少动多看」。创业板是唯一例外：{cy['pct']:+.2f}% 收 {cy['close']:.2f}，<b>最低 {cy['low']:.2f} 未破 60 日低 2263.74</b>，仍在压力下方横住。</p>
<img class="chart" src="../charts/000001_SH_DY_{SUF}.png">
<img class="chart" src="../charts/399006_SZ_DY_{SUF}.png">

<h2>二、板块：国产算力上二类热点，银行掉队</h2>
<table>
  <tr><th>方向</th><th>老师口径</th><th>实测（东财概念 + 自建篮子）</th></tr>
  {''.join(f'<tr><td><b>{n}</b></td><td>{t}</td><td>{v}</td></tr>' for n, t, v in BKROWS)}
</table>
<p><b>两条要记的：</b>① <b>二类热点是国产算力，但「华为概念」这个口径本身没走出来</b> —— 算力概念 {SLC['pct']:+.2f}%、东数西算 {DXS['pct']:+.2f}%（板块涨幅第一）、华为昇腾 {HS_RISE['pct']:+.2f}%，可<b>华为概念整体 {HS['pct']:+.2f}%</b>、涨 {HS['up']} 跌 {HS['down']} —— 真正强的是昇腾+算力租赁，不是「华为概念」这个大盘。算力租赁确有表现：涨停池里美利云、城地香江、华胜天成、真视通、常山北明集中在 IDC 与算力租赁，<b>但老师明确「不要着急去追涨」</b>。② <b>高股息分化比老师说的更明显</b> —— 银行 {BK['银行']['avg_pct']:+.2f}%（招商 {BANKS[0]['pct']:+.2f}%、兴业 {BANKS[4]['pct']:+.2f}%）掉队，而公路 {BK['公路']['avg_pct']:+.2f}%、电力 {BK['电力/高股息']['avg_pct']:+.2f}% 仍全线红 —— <b>红利内部不是普跌，是银行被单独抽走</b>。饮料制造 {BK['饮料制造']['avg_pct']:+.2f}%（0 涨 5 跌）、白酒概念 -1.56%，老师「防范短线高点」当天就兑现。</p>

<h2>三、8 只标的：全部无方法买点</h2>
<table>
  <tr><th>标的 / 题材</th><th>现价</th><th>老师定性（老师口径）</th><th>关键位</th><th>实测印证（日线触达）</th><th>动作</th></tr>
  {''.join(f'<tr><td><b>{n}</b><br><span class="meta">{t}</span></td><td class="num">{px(n.split()[0])}</td><td>{d}</td><td class="kn">{k}</td><td>{e}</td><td><span class="tag {"tag-bear" if a=="不追" else ("tag-none" if a=="剔除" else "tag-neutral")}">{a}</span></td></tr>' for n, t, d, k, e, a in ROWS)}
</table>
<img class="chart" src="../charts/603259_SH_DY_{SUF}.png">
<img class="chart" src="../charts/600150_SH_DY_{SUF}.png">
<img class="chart" src="../charts/603893_SH_DY_{SUF}.png">
<img class="chart" src="../charts/600887_SH_DY_{SUF}.png">
<img class="chart" src="../charts/688787_SH_DY_{SUF}.png">
<img class="chart" src="../charts/603986_SH_DY_{SUF}.png">
<img class="chart" src="../charts/000700_SZ_DY_{SUF}.png">
<img class="chart" src="../charts/300115_SZ_DY_{SUF}.png">

<h2>四、明日关注（可验证条件）</h2>
<div class="box box-a">
① <b>上证 3560.45（今日创的 60 日新低）</b>：明日破了 = 老师说的「震荡向下创新低」，进入底背驰观察窗口；守住且收复 <b>3623</b>（差 26.45 点）才转为向上回抽确认。<br>
② <b>创业板 2263.74（60 日低）</b>：今日最低 2265.76 只差 2.02 点没破，破了说明它也跟着选向下。<br>
③ <b>国产算力能否延续</b>：算力概念 {SLC['pct']:+.2f}%、东数西算 {DXS['pct']:+.2f}% 是今日主线，但<b>华为概念整体 {HS['pct']:+.2f}%</b> —— 明日看能否从细分扩散到整体，扩散不了就是一日游，不追。<br>
④ <b>高股息会不会在指数企稳后先跌</b>：银行今日已 {BK['银行']['avg_pct']:+.2f}%，公路/电力仍红 —— 老师提醒「防范指数止跌后高股息出现下跌」，红利补跌即为验证。<br>
⑤ <b>两个最近的触发位</b>：伊利 <b>31.96</b>（今日最低 {s_yl['low']:.2f}，差 {31.96-s_yl['low']:.2f} 元，有效击穿=顶背驰）、兆易创新 <b>233</b>（今日最高 {s_zy['high']:.2f}，差 {233-s_zy['high']:.2f} 元）。
</div>
<div class="box box-r">
<b>纪律（原文明写）：</b>① <b>总仓位上限 4 成</b>，轻仓控制出手频率，不追涨、不放大仓位抢低点；② <b>不要默认底背驰一定会出现</b>，遵循方法买点信号；③ 防范走势转成阴跌；④ <b>被套处理</b>：仓位轻的可结合反弹用部分仓位高抛低吸倒差价，仓位重的<b>不硬顶也不额外加仓</b>，心态压力大可酌情降部分仓位；⑤ 今日<b>潜在强势教学案例：无</b>；港股<b>暂无符合中枢方法的教学案例</b>。
</div>

<h2>五、偏差记录</h2>
<table>
  <tr><th>老师原文</th><th>实测</th><th>判定</th></tr>
  {''.join(f'<tr><td>{a}</td><td>{b}</td><td><span class="tag {"tag-bear" if "窄" in c else ("tag-bull" if c=="精确命中" else "tag-none")}">{c}</span></td></tr>' for a, b, c in DEVS)}
</table>
<p class="meta">「高开阴线创新低」「3623 未破」「无日线有力度底分型」「算力租赁有表现」「高股息分化」「饮料白酒防短线高点」「8 只全部无买点」「模塑、长盈剔除跟踪」「总仓 4 成」等其余判据与实测一致；缠论定性按老师口径引用。</p>

<div class="foot">
  <p>来源：都业华《高级班》2026-11-18 收评，执业编号 A0400626100004。<b>仅供参考，不作为买卖依据，据此操作风险自担。投资有风险，入市需谨慎！历史案例不代表未来收益。</b></p>
  <p><b>口径：</b>同花顺日线 141 根（今日那根用收盘快照补齐）+ 新浪收盘快照；成交额＝上证指数额＋深证成指额，环比取 11/17 同口径；涨跌家数取新浪全 A {BR['n']} 只 15:00 快照；涨停/跌停/炸板用东财池；板块为东财概念板块 + 自建篮子均值。关键位一律用<b>日线触达判据</b>（当日最高/最低 vs 关键位）。</p>
</div>

</div>
</body>
</html>
"""

out = REPO / "html/duyiehua-20261118.html"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from fix_mobile_tables import patch_html
out.write_text(patch_html(html), encoding="utf-8")
print("saved", out, len(html))
