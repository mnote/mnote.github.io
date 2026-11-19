"""都业华 2026-11-19 高级班收评 · 纪要 HTML（白底 · 收盘版）

⛔ 用户 2026-11-11 禁令：只用日线级别数据，不调用 1/15 分钟 K 线、不调用 czsc。
⛔ 缠论定性按「老师口径」引用，不声称我方复算过 15 分钟结构。
📏 篇幅硬约束：正文 ≤2000 中文字、表格 ≤4 张；K 线图保留、不计字数。

输出：html/duyiehua-20261119.html
"""
import json
import sys
from pathlib import Path

REPO = Path("/Users/maoling/workspace/mnote.github.io")
RPT = REPO / "reports/duyiehua-20261119"
D = json.loads((RPT / "data_close_20261119.json").read_text(encoding="utf-8"))
IX, ST, BK, SER = D["index"], D["stocks"], D["baskets"], D["series"]
BR, POOL = D["breadth"], D["pools"]

TITLE = "DYH 收评 - 2026-11-19（周四 缩量阴跌，国产算力转凉）"

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


def px(name):
    s = ST[name]
    return f'<span class="{cls(s["pct"])}">{s["close"]:.2f} ({s["pct"]:+.2f}%)</span>'


def prev_row(name):
    """上一交易日（11/18）的 OHLC"""
    r = SER[name][-2]
    return r


def amt_yi(name):
    return ST[name]["amt"] / 1e5


def amt_ratio(name):
    return amt_yi(name) / (ST[name]["amt_prev"] / 1e5)


sh, cy, sz = IX["上证指数"], IX["创业板指"], IX["深证成指"]
hs300, kc = IX["沪深300"], IX["科创50"]
P3623 = 3623.12

bk = BK["国产算力"]
ck = BK["算力租赁/IDC"]
hl = BK["高股息红利"]
cm = BK["半导体"]
mv = BK["AI视频/传媒"]
ztc = POOL["zt"]["tc"]
dtc = POOL["dt"]["tc"]
ztbc = POOL["zb"]["tc"]
follow = D["prev_zt_follow"]

# ---------- 板块表 ----------
BKROWS = [
    ("国产算力", "二类热点 ·「有点要凉的迹象」",
     f'<b>{bk["avg_pct"]:+.2f}%</b>（{bk["up"]} 涨 {bk["down"]} 跌）；'
     f'拓维信息 <b>-9.35%</b>、常山北明 +4.83%、四川长虹 +1.41%'),
    ("算力租赁/IDC", "「内部也出现分化，表现比较弱」",
     f'<b>{ck["avg_pct"]:+.2f}%</b>（{ck["up"]} 涨 {ck["down"]} 跌）；'
     f'光环新网、数据港、奥飞数据全跌'),
    ("高股息红利", "「高股息红利方向有分化」",
     f'{hl["avg_pct"]:+.2f}%（{hl["up"]} 涨 {hl["down"]} 跌）；银行 {BK["银行"]["avg_pct"]:+.2f}%、'
     f'电力 {BK["电力"]["avg_pct"]:+.2f}%、煤炭/石油 {BK["煤炭/石油"]["avg_pct"]:+.2f}%'),
    ("AI视频/传媒", "「前期强势股还在延续补跌」",
     f'<b>{mv["avg_pct"]:+.2f}%</b>（{mv["up"]} 涨 {mv["down"]} 跌）；'
     f'昨日涨停 {follow["n"]} 只今日跌 {follow["down"]} 只、跌超 5% {follow["down5"]} 只'),
    ("半导体", "（对照）",
     f'{cm["avg_pct"]:+.2f}%（{cm["up"]} 涨 {cm["down"]} 跌）；'
     f'中芯国际 +6.21%、瑞芯微 -4.12%，权重与题材反向'),
]

# ---------- 标的表 ----------
def row(name, topic, judge, key, ev, act):
    return (name, topic, judge, key, ev, act)


ROWS = [
    row("药明康德", "大医药", "不操作 · 等向上突破 157.8 出 15 分钟底分型三买", "157.8",
        f'收在全天最高 <b>144.39</b>，低 {ST["药明康德"]["low"]:.2f} 未破昨低 '
        f'{prev_row("药明康德")["l"]:.2f}；距 157.8 差 <b>{157.8-ST["药明康德"]["high"]:.2f}</b> 元；'
        f'量比 {amt_ratio("药明康德"):.0%} 缩量', "等"),
    row("中国船舶", "船舶", "不操作 · 走势相对抗跌，等突破 36.75 出 15 分钟底分型回抽确认", "36.75",
        f'全市场 87% 下跌日里几乎平盘 {ST["中国船舶"]["pct"]:+.2f}%；最高 '
        f'{ST["中国船舶"]["high"]:.2f}，距 36.75 差 <b>{36.75-ST["中国船舶"]["high"]:.2f}</b> 元；'
        f'量比 {amt_ratio("中国船舶"):.0%}', "等"),
    row("瑞芯微", "端侧AI", "不操作 · 激进等日线有力度底分型+小共振中枢；稳健等突破上沿出日线三买", "220.7",
        f'低 <b>{ST["瑞芯微"]["low"]:.2f}</b> 破昨低 {prev_row("瑞芯微")["l"]:.2f}，续创新低；'
        f'底分型未出，距 220.7 差 {220.7-ST["瑞芯微"]["close"]:.2f}', "等"),
    row("伊利股份", "大消费", "不操作 · 延续上涨不追涨，观察是否出顶背驰，自行参与者设好止损", "—",
        f'高 <b>{ST["伊利股份"]["high"]:.2f}</b> 创 60 日新高，收 '
        f'<b>{ST["伊利股份"]["close"]:.2f} {ST["伊利股份"]["pct"]:+.2f}%</b>；'
        f'量比 {amt_ratio("伊利股份"):.0%}；昨给 31.96 顶背驰位今日未触', "不追"),
    row("海天瑞声", "机器人", "不操作 · 等 15 分钟二买止跌信号", "141",
        f'低 <b>{ST["海天瑞声"]["low"]:.2f}</b> 破昨低 {prev_row("海天瑞声")["l"]:.2f}，破位延续；'
        f'距 60 日低 {ST["海天瑞声"]["lo60"]:.2f} 还有 '
        f'{(ST["海天瑞声"]["close"]/ST["海天瑞声"]["lo60"]-1)*100:.1f}%', "等"),
    row("兆易创新", "存储芯片", "不操作 · 稳健等收复 233 后回抽三买；激进等突破 224.6 出 15 分钟底分型回抽",
        "233 / 224.6",
        f'高 {ST["兆易创新"]["high"]:.2f}，距 224.6 差 <b>{224.6-ST["兆易创新"]["high"]:.2f}</b>、'
        f'距 233 差 <b>{233-ST["兆易创新"]["high"]:.2f}</b> 元；低 {ST["兆易创新"]["low"]:.2f} '
        f'逼近 60 日低 {ST["兆易创新"]["lo60"]:.2f} 未破；量比 {amt_ratio("兆易创新"):.0%}', "等"),
    row("华丰科技", "华为概念", "不操作 · 等日线出顶分型回调后的 15 分钟二买止跌", "—",
        f'低 <b>{ST["华丰科技"]["low"]:.2f}</b> 破昨低 {prev_row("华丰科技")["l"]:.2f}；'
        f'成交 {amt_yi("华丰科技"):.1f} 亿；无顶分型', "等"),
    row("中芯国际", "半导体", "不操作 · 需对 120.6 突破出回抽三买（老师口径：下午未满足）", "120.6 / 117.3",
        f'高 <b>{ST["中芯国际"]["high"]:.2f}</b>、收 <b>{ST["中芯国际"]["close"]:.2f}</b> '
        f'均站上 120.6，117.3 亦突破；量比 {amt_ratio("中芯国际"):.0%} 放量', "等回抽"),
    row("常山北明", "国产算力", "涨停次日放大量，短线容易遇阻回落", "—",
        f'额 <b>{amt_yi("常山北明"):.1f} 亿</b> = 昨 {amt_ratio("常山北明"):.2f} 倍；'
        f'高 {ST["常山北明"]["high"]:.2f} 收 {ST["常山北明"]["close"]:.2f} 冲高回落', "不追"),
    row("拓维信息", "国产算力", "今日大幅调整，走势起不来", "—",
        f'<b>{ST["拓维信息"]["pct"]:+.2f}%</b> 近跌停，缩量（{amt_ratio("拓维信息"):.2f} 倍）下跌', "回避"),
    row("四川长虹", "国产算力", "放大量，短线也不一定能起来", "—",
        f'额 <b>{amt_yi("四川长虹"):.1f} 亿</b> = 昨 {amt_ratio("四川长虹"):.2f} 倍；'
        f'涨幅由昨日涨停收窄至 {ST["四川长虹"]["pct"]:+.2f}%', "不追"),
]

DEVS = [
    ("「各大指数均出现下跌」",
     f'科创50 <b>+{kc["pct"]:.2f}%</b>、沪深300 {hs300["pct"]:+.2f}% 逆势红',
     "部分不成立"),
    ("「深成指向下破的幅度很浅」",
     f'深成指最低 <b>{sz["low"]:.2f}</b> = 60 日新低',
     "日线看偏深"),
    ("「二类热点：国产算力」",
     f'篮子 {bk["avg_pct"]:+.2f}%（{bk["up"]} 涨 {bk["down"]} 跌）、算力租赁 {ck["avg_pct"]:+.2f}%',
     "当日未兑现"),
    ("「药明康德 15 分钟窄幅震荡向下有破位迹象」",
     f'日线低 {ST["药明康德"]["low"]:.2f} > 昨低 {prev_row("药明康德")["l"]:.2f}，且收在全天最高',
     "日线未破位"),
    ("「中芯 120.6 突破回抽，下午也没满足」",
     f'收 {ST["中芯国际"]["close"]:.2f} 已站稳 120.6（高 {ST["中芯国际"]["high"]:.2f}）',
     "回抽待 11/20 验证"),
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
  <div class="meta"><a href="/" style="color:#2563eb;text-decoration:none">← 返回首页</a><span style="color:#9ca3af"> · </span>收盘版 · 数据截至 2026-11-19 15:00</div>
  <p class="stance"><b>结论：缩量阴跌、创新低，3623 未破 → 仍是下跌中枢震荡，总仓 ≤4 成、少动多看。</b>
  上证收 <b>{sh['close']:.2f}</b>（<span class="down">{sh['pct']:+.2f}%</span>），最低 <b>{sh['low']:.2f}</b> 创 60 日新低；
  跌家 {BR['down']}（{BR['down']/BR['n']*100:.0f}%）、两市 <b>{BR['amount_yi']:,.0f} 亿</b>（{BR['amount_delta_pct']:+.2f}%）缩量阴跌。
  二类热点国产算力当日转凉（篮子 {bk['avg_pct']:+.2f}%）。<b>池内 8 只全部无方法买点</b>；
  唯一亮点中芯国际 <span class="up">+{ST['中芯国际']['pct']:.2f}%</span> 站上 120.6，但仍缺回抽确认。</p>
</div>

<div class="grid4">
  <div class="kpi"><div class="label">上证指数 · 创 60 日新低</div><div class="val down">{sh['pct']:+.2f}%</div><div class="sub">{sh['close']:.2f} · 低 {sh['low']:.2f}</div></div>
  <div class="kpi"><div class="label">科创50 / 创业板指</div><div class="val up">{kc['pct']:+.2f}% / <span class="down">{cy['pct']:+.2f}%</span></div><div class="sub">沪深300 {hs300['pct']:+.2f}% · 深成 {sz['pct']:+.2f}%</div></div>
  <div class="kpi"><div class="label">两市成交额（全天）</div><div class="val vol">{BR['amount_yi']:,.0f} 亿</div><div class="sub vol">环比 {BR['amount_delta_pct']:+.2f}%（昨 {BR['amount_prev_yi']:,.0f} 亿）</div></div>
  <div class="kpi"><div class="label">涨 / 跌家数</div><div class="val"><span class="up">{BR['up']}</span> / <span class="down">{BR['down']}</span></div><div class="sub">涨停 {ztc} · 跌停 {dtc} · 炸板 {ztbc}</div></div>
</div>

<h2>一、指数：缩量阴跌创新低，3623 仍远</h2>
<p>老师五条判据逐条核：① <b>「各大指数均出现下跌」</b> —— 上证 {sh['pct']:+.2f}%、深成 {sz['pct']:+.2f}%、创业板 {cy['pct']:+.2f}% ✓，但科创50 {kc['pct']:+.2f}%、沪深300 {hs300['pct']:+.2f}% 逆势（见偏差记录）；② <b>「1 分钟下跌中枢延伸，走势没出底背驰」</b> —— 老师口径，日线不复算；③ <b>「深成指向下破的幅度很浅」</b> —— 深成最低 {sz['low']:.2f} 已是 60 日新低；④ <b>「创业板指数没有创新低，维持震荡，指数没见底」</b> —— 创业板最低 {cy['low']:.2f} > 11/17 低 {cy['lo60']:.2f} ✓ <b>成立</b>；⑤ <b>「等震荡向上需要突破压力 3623 点后出分型回抽确认」</b> —— 3623.12 即 11/16 高点，今日最高 {sh['high']:.2f}，差 <b>{P3623-sh['high']:.2f} 点</b>，未触及。</p>
<p>结构是<b>缩量阴跌、宽度极差</b>：跌 {BR['down']} 家占 {BR['down']/BR['n']*100:.0f}%，跌超 5% {BR['down_5']} 家、跌超 9% {BR['down_9']} 家，跌停 {dtc} 家；两市 {BR['amount_yi']:,.0f} 亿环比 {BR['amount_delta_pct']:+.2f}%。正是老师提醒的<b>「防范走势缩量向下转阴跌」</b>形态 —— 底背驰未出前不抢低点。</p>
<img class="chart" src="../charts/000001_SH_DY_20261119.png">
<img class="chart" src="../charts/399006_SZ_DY_20261119.png">

<h2>二、板块：国产算力由热点转分化，红利内部分化</h2>
<table>
  <tr><th>方向（自建篮子）</th><th>老师口径</th><th>实测（均值 · 涨跌家数 · 个股）</th></tr>
  {''.join(f'<tr><td><b>{n}</b></td><td>{t}</td><td>{v}</td></tr>' for n, t, v in BKROWS)}
</table>
<p><b>三条要记的：</b>① <b>国产算力「有点要凉」当天兑现</b> —— 篮子 {bk['avg_pct']:+.2f}%（{bk['up']} 涨 {bk['down']} 跌），内部分化极端：常山北明放量 {ST['常山北明']['pct']:+.2f}%、四川长虹放量 {ST['四川长虹']['pct']:+.2f}%、<b>拓维信息直接 -9.35%</b>；② <b>「前期强势股延续补跌」成立</b> —— 昨日涨停 {follow['n']} 只，今日跌 {follow['down']} 只、跌超 5% {follow['down5']} 只（爱仕达 -10.04%、泰嘉股份 -9.98%、双环科技 -9.90%）；③ <b>红利是分化不是普跌</b> —— 银行 {BK['银行']['avg_pct']:+.2f}%、电力 {BK['电力']['avg_pct']:+.2f}% 红，煤炭/石油 {BK['煤炭/石油']['avg_pct']:+.2f}% 绿，节奏与指数相反。</p>

<h2>三、8 只标的 + 3 只板块股：全部无方法买点</h2>
<table>
  <tr><th>标的 / 题材</th><th>收盘</th><th>老师定性（老师口径）</th><th>关键位</th><th>实测印证（日线触达）</th><th>动作</th></tr>
  {''.join(f'<tr><td><b>{n}</b><br><span class="meta">{t}</span></td><td class="num">{px(n)}</td><td>{d}</td><td class="kn">{k}</td><td>{e}</td><td><span class="tag {"tag-bear" if a in ("不追","回避") else "tag-neutral"}">{a}</span></td></tr>' for n, t, d, k, e, a in ROWS)}
</table>
<p><b>三条要记的：</b>① <b>池子变了</b> —— 海天瑞声由短线升中线，新增短线华丰科技、中芯国际，模塑科技、长盈精密维持剔除；② <b>8 只全部「无方法买点」= 没有进场信号</b>，只剩触发条件，别把「条件」读成「可以试」；③ <b>池内唯一近端触发点是中芯国际</b>：老师给的 120.6 突破位今日已具备（收 {ST['中芯国际']['close']:.2f}），差一步的是<b>回抽确认</b>。</p>
<img class="chart" src="../charts/603259_SH_DY_20261119.png">
<img class="chart" src="../charts/600150_SH_DY_20261119.png">
<img class="chart" src="../charts/603893_SH_DY_20261119.png">
<img class="chart" src="../charts/600887_SH_DY_20261119.png">
<img class="chart" src="../charts/688787_SH_DY_20261119.png">
<img class="chart" src="../charts/603986_SH_DY_20261119.png">
<img class="chart" src="../charts/688629_SH_DY_20261119.png">
<img class="chart" src="../charts/688981_SH_DY_20261119.png">
<img class="chart" src="../charts/000158_SZ_DY_20261119.png">
<img class="chart" src="../charts/002261_SZ_DY_20261119.png">
<img class="chart" src="../charts/600839_SH_DY_20261119.png">

<h2>四、明日关注（可验证条件）</h2>
<div class="box box-a">
① <b>上证 {P3623:.2f}（11/16 高点）</b>：突破并回抽确认才有短线止跌的第一个确认；今日最高 {sh['high']:.2f} 差 {P3623-sh['high']:.2f} 点。跌破今低 {sh['low']:.2f} 则阴跌延续。<br>
② <b>中芯国际 120.6</b>：突破已具备（收 {ST['中芯国际']['close']:.2f}），观察回抽不破 120.6 能否出 15 分钟回抽确认 —— 池内唯一可跟踪的近端触发点。<br>
③ <b>国产算力三只</b>：常山北明 {ST['常山北明']['high']:.2f}、四川长虹 {ST['四川长虹']['high']:.2f} 是今日高点，涨停次日放量后不新高即为遇阻；拓维信息 {ST['拓维信息']['low']:.2f} 是破位低点，不碰。<br>
④ <b>兆易创新 224.6</b>：突破才有 15 分钟底分型回抽机会（稳健门槛 233）；收 {ST['兆易创新']['close']:.2f}，差 {224.6-ST['兆易创新']['high']:.2f} 元。<br>
⑤ <b>宽度与量能</b>：跌超 5% {BR['down_5']} 家、跌超 9% {BR['down_9']} 家、跌停 {dtc} 家、成交缩量 {abs(BR['amount_delta_pct']):.2f}%。跌停收敛前不接旧热点；<b>恐慌向下动作出现</b>才是底背驰的观察窗口。
</div>
<div class="box box-r">
<b>纪律与被套处理（老师原文口径）：</b>总仓上限 <b>4 成</b>、轻仓控制出手频率、<b>不追涨</b>、不用大仓位抢低点；<b>仓位轻被套</b>可结合反弹用部分仓位高抛低吸倒差价；<b>仓位重被套</b>不硬顶、不额外加仓，心态压力大可酌情主动降部分仓位。原话：「没有一个方案和策略是鱼和熊掌兼得。」
</div>

<h2>五、偏差记录</h2>
<table>
  <tr><th>老师原文</th><th>实测</th><th>判定</th></tr>
  {''.join(f'<tr><td>{a}</td><td>{b}</td><td><span class="tag tag-none">{c}</span></td></tr>' for a, b, c in DEVS)}
</table>
<p style="color:var(--muted);font-size:12.5px">其余判据当日一致：创业板未创新低 ✓、3623 未触及 ✓、常山北明与四川长虹放大量 ✓、拓维信息大幅调整 ✓、前期强势股补跌 ✓、红利分化 ✓。</p>

<div class="foot">
  <p>来源：都业华《高级班》2026-11-19 收评，执业编号 A0400626100004。<b>仅供参考，不作为买卖依据，据此操作风险自担。投资有风险，入市需谨慎！</b></p>
  <p><b>口径：</b>Tushare 日线（前复权，个股 adj_factor 基准取最新日）+ 新浪收盘快照交叉校验（11 只标的两源收盘价全部一致）；全市场涨跌家数/成交额/涨跌停取 Tushare daily 全量 5573 只；涨停/跌停/炸板池取东财 push2ex（涨停 {ztc}、跌停 {dtc}、炸板 {ztbc}）；板块为自建篮子均值（成分逐一列出）。<b>缠论定性按老师口径引用，不声称我方复算过 15 分钟结构</b>；关键位一律用日线触达判据（当日最高/最低 vs 关键位）。</p>
</div>

</div>
</body>
</html>
"""

out = REPO / "html/duyiehua-20261119.html"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from fix_mobile_tables import patch_html
out.write_text(patch_html(html), encoding="utf-8")
print("saved", out, len(html))
