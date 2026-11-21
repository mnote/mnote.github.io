"""都业华 2026-11-20 高级班收评 · 纪要 HTML（白底 · 收盘版）

⛔ 用户 2026-11-11 禁令：只用日线级别数据，不调用 1/15 分钟 K 线、不调用 czsc。
⛔ 缠论定性按「老师口径」引用，不声称我方复算过 15 分钟结构。
📏 篇幅硬约束：正文 ≤2000 中文字、表格 ≤4 张；K 线图保留、不计字数。

输出：html/duyiehua-20261120.html
"""
import json
import sys
from pathlib import Path

REPO = Path("/Users/maoling/workspace/mnote.github.io")
RPT = REPO / "reports/duyiehua-20261120"
D = json.loads((RPT / "data_close_20261120.json").read_text(encoding="utf-8"))
X = json.loads((RPT / "extra_close_20261120.json").read_text(encoding="utf-8"))
IX, ST, BK, SER = D["index"], D["stocks"], D["baskets"], D["series"]
BR, POOL = D["breadth"], D["pools"]
ETF = X["etf_share"]
IND = X["industry_by_pct"]
INDW = X["industry_worst"]

TITLE = "DYH 收评 - 2026-11-20（周五 探底回升未止跌，银行保险护盘）"

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
    return SER[name][-2]


def amt_yi(name):
    return ST[name]["amt"] / 1e5


def amt_ratio(name):
    return ST[name]["amt"] / ST[name]["amt_prev"]


sh, cy, sz = IX["上证指数"], IX["创业板指"], IX["深证成指"]
hs300, kc = IX["沪深300"], IX["科创50"]
zz500, zz1000, sz50 = IX["中证500"], IX["中证1000"], IX["上证50"]
P3623 = 3623.12
MA5_SH = sh["ma5"]

bk = BK["银行"]
ins = BK["保险"]
yj = BK["元件/PCB"]
gcsl = BK["国产算力"]
ck = BK["算力/CPO"]
hl = BK["高股息红利"]
dl = BK["电力"]
mt = BK["煤炭/石油"]
cm = BK["半导体"]
mv = BK["AI视频/传媒"]
rq = BK["人形机器人"]
hw = BK["华为概念"]

ztc = POOL["zt"]["tc"]
dtc = POOL["dt"]["tc"]
ztbc = POOL["zb"]["tc"]
follow = D["prev_zt_follow"]

# ---------- 板块表 ----------
BKROWS = [
    ("银行 / 保险", "「尾盘银行和保险等板块出现拉升」",
     f'银行 <b>{bk["avg_pct"]:+.2f}%</b>、保险 {ins["avg_pct"]:+.2f}%；'
     f'国有大型银行Ⅲ <b>{[b["pct"] for b in IND if b["name"] == "国有大型银行Ⅲ"][0]:+.2f}%</b>、'
     f'股份制银行Ⅲ {[b["pct"] for b in IND if b["name"] == "股份制银行Ⅲ"][0]:+.2f}%'),
    ("高股息红利（电力/煤炭石油）", "「高股息红利内部细分要多对比」",
     f'红利篮子 {hl["avg_pct"]:+.2f}%（{hl["up"]}涨{hl["down"]}跌）；电力 {dl["avg_pct"]:+.2f}%、'
     f'煤炭/石油 {mt["avg_pct"]:+.2f}%——内部背离'),
    ("元件 / PCB", "「元件有点动作，但本质维持1分钟下跌中枢震荡」",
     f'印制电路板 {[b["pct"] for b in X["yuanjian"] if b["name"] == "印制电路板"][0]:+.2f}%、'
     f'元件 {[b["pct"] for b in X["yuanjian"] if b["name"] == "元件"][0]:+.2f}%（仍跌）；'
     f'涨停 6 家居首、主力净流入'),
    ("国产算力 / 算力CPO", "「国产算力掉下二类热点榜，防范前期强势股补跌」",
     f'国产算力 <b>{gcsl["avg_pct"]:+.2f}%</b>、算力CPO {ck["avg_pct"]:+.2f}%；'
     f'AI视频/传媒 {mv["avg_pct"]:+.2f}%、机器人 {rq["avg_pct"]:+.2f}%'),
    ("华为概念（华丰对照）", "「对比华胜天成后，华胜天成表现更强些」",
     f'华为概念篮子 {hw["avg_pct"]:+.2f}%；华丰 <b>{ST["华丰科技"]["pct"]:+.2f}%</b> vs '
     f'华胜天成 <b>{ST["华胜天成"]["pct"]:+.2f}%</b>，差 17.04pp'),
    ("半导体", "（对照：权重逆势）",
     f'{cm["avg_pct"]:+.2f}%；中芯国际 <b>{ST["中芯国际"]["pct"]:+.2f}%</b> 逆势、'
     f'瑞芯微 {ST["瑞芯微"]["pct"]:+.2f}%'),
]

# ---------- 标的表 ----------
ROWS = [
    ("药明康德", "大医药", "稳健等突破 157.8 出 15 分钟底分型三买", "157.8",
     f'收 <b>{ST["药明康德"]["close"]:.2f}</b> {ST["药明康德"]["pct"]:+.2f}%，低 '
     f'{ST["药明康德"]["low"]:.2f} 破昨低；距 157.8 差 <b>{157.8-ST["药明康德"]["close"]:.2f}</b>', "等"),
    ("中国船舶", "船舶", "等突破压力 36.75 出 15 分钟底分型三买", "36.75",
     f'低 {ST["中国船舶"]["low"]:.2f} → 收 <b>{ST["中国船舶"]["close"]:.2f}</b> '
     f'{ST["中国船舶"]["pct"]:+.2f}%（收日内高位，尾盘拉升）；距 36.75 差 '
     f'<b>{36.75-ST["中国船舶"]["close"]:.2f}</b>', "等"),
    ("瑞芯微", "端侧AI", "激进等日线底分型+小共振中枢；稳健等突破上沿高点出日线三买", "—",
     f'低 <b>{ST["瑞芯微"]["low"]:.2f}</b> 破昨低，续创新低；底分型未出，'
     f'距 MA5 {ST["瑞芯微"]["ma5"]:.2f} 还有 {ST["瑞芯微"]["ma5"]-ST["瑞芯微"]["close"]:.2f}', "等"),
    ("伊利股份", "大消费", "上涨延伸不追涨；跌破 31.9 顶背驰大概率形成", "31.9",
     f'高 <b>{ST["伊利股份"]["high"]:.2f}</b> 创 60 日新高，收 '
     f'{ST["伊利股份"]["close"]:.2f} {ST["伊利股份"]["pct"]:+.2f}%；距 31.9 还有 '
     f'{ST["伊利股份"]["close"]-31.9:.2f} 元', "不追"),
    ("海天瑞声", "机器人", "继续等 15 分钟二买止跌信号", "—",
     f'盘中 {ST["海天瑞声"]["high"]:.2f} 异动后收 {ST["海天瑞声"]["close"]:.2f} '
     f'{ST["海天瑞声"]["pct"]:+.2f}%，低 {ST["海天瑞声"]["low"]:.2f} 破昨低；'
     f'距 60 日低 {(ST["海天瑞声"]["close"]/ST["海天瑞声"]["lo60"]-1)*100:.1f}%', "等"),
    ("创业板ETF易方达", "超跌 · 新增", "跌破出止跌底背驰+日线底分型站 MA5；浅调等突破 2.28 出底分型回抽", "2.28",
     f'最高 <b>2.28</b> 恰好触及未突破，收 <b>2.23</b> {ST["创业板ETF易方达"]["pct"]:+.2f}% '
     f'创 60 日新低；未站 MA5 {ST["创业板ETF易方达"]["ma5"]:.2f}；额 {amt_yi("创业板ETF易方达"):.0f} 亿', "等"),
    ("兆易创新", "存储芯片", "稳健等收复 233 出回抽三买；激进等突破 224.6 出底分型回抽", "233 / 224.6",
     f'低 <b>{ST["兆易创新"]["low"]:.2f}</b> 创 60 日新低，收 {ST["兆易创新"]["close"]:.2f} '
     f'{ST["兆易创新"]["pct"]:+.2f}%；距 233 差 {233-ST["兆易创新"]["close"]:.2f}、'
     f'224.6 差 {224.6-ST["兆易创新"]["close"]:.2f}', "等"),
    ("华丰科技", "华为概念", "等日线有力度底分型止跌；跌破 80.6 不再关注", "80.6",
     f'<b>{ST["华丰科技"]["pct"]:+.2f}%</b> 大阴线，收 {ST["华丰科技"]["close"]:.2f}、低 '
     f'{ST["华丰科技"]["low"]:.2f}；距支撑 80.6 差 {ST["华丰科技"]["close"]-80.6:.2f}', "等"),
    ("中芯国际", "半导体", "延续向上不追涨，等日线顶分型回抽", "—",
     f'收 <b>{ST["中芯国际"]["close"]:.2f}</b> {ST["中芯国际"]["pct"]:+.2f}%，高 '
     f'{ST["中芯国际"]["high"]:.2f} 逼近 60 日高（差 {ST["中芯国际"]["hi60"]-ST["中芯国际"]["high"]:.2f}）', "不追"),
    ("中际旭创", "算力 · 焦点", "走势没见底", "—",
     f'收 {ST["中际旭创"]["close"]:.2f} {ST["中际旭创"]["pct"]:+.2f}%，低 {ST["中际旭创"]["low"]:.2f} 续创新低', "等"),
    ("长鑫科技", "存储 · 焦点", "耐心等止跌信号", "—",
     f'收 {ST["长鑫科技"]["close"]:.2f} {ST["长鑫科技"]["pct"]:+.2f}%，收全天最低、创 60 日新低', "等"),
    ("华胜天成", "华为 · 对照", "老师对照口径：表现强于华丰科技", "—",
     f'收 <b>{ST["华胜天成"]["close"]:.2f}</b> {ST["华胜天成"]["pct"]:+.2f}%，高 '
     f'{ST["华胜天成"]["high"]:.2f} 逼近 60 日高，强于华丰 17.04pp', "参照"),
]

DEVS = [
    ("「涨幅榜靠前的主要是银行和保险」",
     f'行业榜前两位是其他数字媒体 +15.00%、视频媒体 +3.19%（成分各 2/1 只），'
     f'国有大型银行Ⅲ +2.39% 列第三；大盘口径银行 {bk["avg_pct"]:+.2f}%、保险 {ins["avg_pct"]:+.2f}%',
     "口径差异"),
    ("「元件板块有点动作」",
     f'元件 {[b["pct"] for b in X["yuanjian"] if b["name"] == "元件"][0]:+.2f}%、'
     f'印制电路板 {[b["pct"] for b in X["yuanjian"] if b["name"] == "印制电路板"][0]:+.2f}% 仍跌；'
     f'「有动作」仅体现在 6 家涨停与主力净流入',
     "仅资金面成立"),
    ("「药明康德走势抗跌」",
     f'今日 {ST["药明康德"]["pct"]:+.2f}% 弱于上证 {sh["pct"]:+.2f}%，但强于化学制药 '
     f'{[b["pct"] for b in INDW if b["name"] == "化学制药"][0]:+.2f}%',
     "相对医药成立"),
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
  <div class="meta"><a href="/" style="color:#2563eb;text-decoration:none">← 返回首页</a><span style="color:#9ca3af"> · </span>收盘版 · 数据截至 2026-11-20 15:00</div>
  <p class="stance"><b>结论：探底回升但没止跌，仍是下跌中枢延伸，总仓 ≤4 成、少动多看。</b>
  上证收 <b>{sh['close']:.2f}</b>（<span class="down">{sh['pct']:+.2f}%</span>），最低 <b>{sh['low']:.2f}</b> 创 60 日新低、
  收盘未站上 5 日线 {MA5_SH:.2f}；尾盘银行保险拉升，上证50 <span class="up">{sz50['pct']:+.2f}%</span> 逆势。
  温度 <b>20 度</b>、一/二类热点全无，国产算力掉出二类热点榜。
  <b>池内 9 只 + 焦点 2 只全部无方法买点</b>，新增中线创业板ETF亦无买点。</p>
</div>

<div class="grid4">
  <div class="kpi"><div class="label">上证指数 · 创 60 日新低</div><div class="val down">{sh['pct']:+.2f}%</div><div class="sub">{sh['close']:.2f} · 低 {sh['low']:.2f} · 收 MA5 {MA5_SH:.0f} 下</div></div>
  <div class="kpi"><div class="label">成长端杀跌 / 权重护盘</div><div class="val"><span class="down">创 {cy['pct']:+.2f}%</span> / <span class="up">50 {sz50['pct']:+.2f}%</span></div><div class="sub">科创50 {kc['pct']:+.2f}% · 中证1000 {zz1000['pct']:+.2f}%</div></div>
  <div class="kpi"><div class="label">两市成交额（放量下跌）</div><div class="val vol">{BR['amount_yi']:,.0f} 亿</div><div class="sub vol">环比 {BR['amount_delta_pct']:+.2f}%（昨 {BR['amount_prev_yi']:,.0f} 亿）</div></div>
  <div class="kpi"><div class="label">涨 / 跌家数 · 冰点</div><div class="val"><span class="up">{BR['up']}</span> / <span class="down">{BR['down']}</span></div><div class="sub">涨停 {ztc} · 跌停 {dtc} · 炸板 {ztbc} · 跌超5% {BR['down_5']}</div></div>
</div>

<h2>一、指数：探底回升出下影线，但止跌条件未满足</h2>
<p>五条判据逐条核：① <b>「今日单边下跌」</b> —— 上证 {sh['pct']:+.2f}%、深成 {sz['pct']:+.2f}%、创业板 {cy['pct']:+.2f}%、中证1000 {zz1000['pct']:+.2f}%，<b>唯上证50 {sz50['pct']:+.2f}% 逆势</b> ✓；② <b>「尾盘银行和保险拉升」</b> —— 银行 {bk['avg_pct']:+.2f}%、保险 {ins['avg_pct']:+.2f}%，上证50 开 {sz50['open']:.0f} → 收 {sz50['close']:.0f} 低开高走 ✓；③ <b>「上证50ETF尾盘量能异动放大翻红」</b> —— 510050 收 <b>2.90 +0.59%</b>、量比 3.63、额 243 亿（前日 26 亿）、份额 <b>+{ETF['上证50ETF']['delta_pct']:.1f}%</b> ✓ 精确；④ <b>「中证500/1000ETF资金进入但没起色」</b> —— 份额 <b>+{ETF['中证500ETF']['delta_pct']:.1f}%</b> / <b>+{ETF['中证1000ETF']['delta_pct']:.1f}%</b>，但两指数 {zz500['pct']:+.2f}%/{zz1000['pct']:+.2f}% <b>收全天最低</b>，抛压重 ✓；⑤ <b>「止跌通用方法是日线出有力度底分型且收盘站住5日均线」</b> —— 上证收 {sh['close']:.2f} <b>未站上 MA5 {MA5_SH:.2f}</b>，条件<b>未满足</b>（口径：多等一根日K过底分型第三根K线高点）。</p>
<p>结构是<b>放量杀跌下的探底回升</b>：两市 {BR['amount_yi']:,.0f} 亿环比 <b>+{BR['amount_delta_pct']:.2f}%</b>，跌 {BR['down']} 家（{BR['down']/BR['n']*100:.0f}%）、跌超 5% {BR['down_5']} 家、跌停 {dtc} 家，是恐慌放量而非缩量止跌。上证距上方 3623.12 压力位仍差 {P3623-sh['close']:.0f} 点，但<b>离上方下跌中枢太近</b>，被拉回延续震荡概率高 → 「上涨空间被压缩」在日线也成立：上证50 翻红而中小盘继续杀（中证1000 {zz1000['pct']:+.2f}%），赚钱效应集中在权重。</p>
<img class="chart" src="../charts/000001_SH_DY_20261120.png">
<img class="chart" src="../charts/399006_SZ_DY_20261120.png">

<h2>二、板块：温度 20 度，冰点；红利护盘、算力补跌</h2>
<table>
  <tr><th>方向（自建篮子 / 行业榜）</th><th>老师口径</th><th>实测（均值 · 涨跌家数 · 个股）</th></tr>
  {''.join(f'<tr><td><b>{n}</b></td><td>{t}</td><td>{v}</td></tr>' for n, t, v in BKROWS)}
</table>
<p><b>四条要记的：</b>① <b>温度 20 度、热点全空</b> —— 涨 {BR['up']} vs 跌 {BR['down']}、跌停 {dtc} 家、跌超 5% {BR['down_5']} 家（{BR['down_5']/BR['n']*100:.0f}%），「临近冰点」✓；② <b>「国产算力掉下二类热点榜」当天兑现</b> —— 国产算力 {gcsl['avg_pct']:+.2f}%、华为概念 {hw['avg_pct']:+.2f}%，昨日涨停 {follow['n']} 只今日跌 {follow['down']} 只、跌超 5% {follow['down5']} 只；③ <b>红利是唯一有赚钱效应的方向</b> —— 银行 {bk['avg_pct']:+.2f}%、电力 {dl['avg_pct']:+.2f}%，但煤炭开采 {[b["pct"] for b in IND if b["name"]=="煤炭开采"][0]:+.2f}% 与煤炭/石油篮子 {mt['avg_pct']:+.2f}% 背离；④ <b>元件有资金没指数</b> —— 涨停 6 家居首、主力净流入 +18.72 亿，但板块指数仍跌，即「有动作但结构没变」。</p>

<h2>三、9 只标的 + 2 只焦点 + 1 只对照：全部无方法买点</h2>
<table>
  <tr><th>标的 / 题材</th><th>收盘</th><th>老师定性（老师口径）</th><th>关键位</th><th>实测印证（日线触达）</th><th>动作</th></tr>
  {''.join(f'<tr><td><b>{n}</b><br><span class="meta">{t}</span></td><td class="num">{px(n)}</td><td>{d}</td><td class="kn">{k}</td><td>{e}</td><td><span class="tag {"tag-bear" if a in ("不追","回避") else ("tag-bull" if a=="参照" else "tag-neutral")}">{a}</span></td></tr>' for n, t, d, k, e, a in ROWS)}
</table>
<p><b>三条要记的：</b>① <b>池子变了</b> —— 中线由 5 只增至 <b>6 只</b>（新增创业板ETF易方达），短线仍 3 只，焦点品种中际旭创、长鑫科技均无买点；② <b>全部「无方法买点」= 没有进场信号</b>，只留触发条件，别把「条件」读成「可以试」；③ <b>最接近触发的是华丰科技</b>：距支撑 80.6 差 {ST['华丰科技']['close']-80.6:.2f} 元，跌破即不再关注；<b>华胜天成 {ST['华胜天成']['pct']:+.2f}% 强于华丰 {ST['华丰科技']['pct']:+.2f}%</b>，老师「华胜天成更强」获数据确认。</p>
<img class="chart" src="../charts/603259_SH_DY_20261120.png">
<img class="chart" src="../charts/600150_SH_DY_20261120.png">
<img class="chart" src="../charts/603893_SH_DY_20261120.png">
<img class="chart" src="../charts/600887_SH_DY_20261120.png">
<img class="chart" src="../charts/688787_SH_DY_20261120.png">
<img class="chart" src="../charts/159915_SZ_DY_20261120.png">
<img class="chart" src="../charts/603986_SH_DY_20261120.png">
<img class="chart" src="../charts/688629_SH_DY_20261120.png">
<img class="chart" src="../charts/688981_SH_DY_20261120.png">
<img class="chart" src="../charts/300308_SZ_DY_20261120.png">
<img class="chart" src="../charts/688825_SH_DY_20261120.png">
<img class="chart" src="../charts/600410_SH_DY_20261120.png">

<h2>四、明日关注（可验证条件）</h2>
<div class="box box-a">
① <b>上证 MA5 {MA5_SH:.2f} + 今低 {sh['low']:.2f}</b>：日线出有力度底分型<b>且收盘站上 {MA5_SH:.2f}</b> 才是止跌第一步（口径：多等一根日K过底分型第三根K线高点）；跌破 {sh['low']:.2f} 则阴跌延续。<br>
② <b>创业板ETF易方达 2.28</b>：最高 2.28 触及未突破；站稳后回抽确认才有戏，跌破 2.23 则续创新低。<br>
③ <b>华丰科技 80.6</b>：距支撑差 {ST['华丰科技']['close']-80.6:.2f} 元，跌破不再关注；对照华胜天成强弱。<br>
④ <b>中芯 {ST['中芯国际']['hi60']:.2f} / 兆易 233、224.6</b>：需突破才有三买机会，差 {ST['中芯国际']['hi60']-ST['中芯国际']['high']:.2f} / {233-ST['兆易创新']['close']:.2f} / {224.6-ST['兆易创新']['close']:.2f} 元。<br>
⑤ <b>宽度与量能</b>：跌超 5% {BR['down_5']} 家、跌停 {dtc} 家、放量 {BR['amount_delta_pct']:+.2f}%。宽度不修复前不接旧热点；<b>恐慌向下动作</b>才是底背驰观察窗口。
</div>
<div class="box box-r">
<b>纪律与被套处理（老师原文口径）：</b>不主观假设、不打提前量；<b>不追涨</b>，可用小仓位尝试；总仓上限 <b>4 成</b>、轻仓控频率；<b>仓位轻被套</b>可结合反弹高抛低吸倒差价；<b>仓位重被套</b>不硬顶、不加仓，心态压力大可酌情降仓。潜在强势案例与港股<b>今日均无</b>。
</div>

<h2>五、偏差记录</h2>
<table>
  <tr><th>老师原文</th><th>实测</th><th>判定</th></tr>
  {''.join(f'<tr><td>{a}</td><td>{b}</td><td><span class="tag tag-none">{c}</span></td></tr>' for a, b, c in DEVS)}
</table>
<p style="color:var(--muted);font-size:12.5px">其余判据当日一致 ✓：单边下跌、银行保险尾盘拉升、上证50ETF 放量翻红、中证500/1000ETF 资金进入没起色、止跌条件未满足、温度 20 度热点全空、国产算力掉榜、强势股补跌、元件有动作。</p>
<div class="foot">
  <p>来源：都业华《高级班》2026-11-20 收评，执业编号 A0400626100004。<b>仅供参考，不作为买卖依据，据此操作风险自担。投资有风险，入市需谨慎！</b></p>  <p><b>口径：</b>Tushare 日线（前复权）+ 指数/ETF 日线；涨跌家数/成交额/涨跌停取 daily 全量 5572 只；涨停/跌停/炸板取东财 push2ex（{ztc}/{dtc}/{ztbc}）；行业板块取东财 push2 榜；<b>ETF 资金进入用 fund_share 份额核验</b>；板块为自建篮子均值。<b>缠论定性按老师口径引用，不声称复算过 15 分钟结构</b>；关键位用日线触达判据。</p>
</div>

</div>
</body>
</html>
"""

out = REPO / "html/duyiehua-20261120.html"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from fix_mobile_tables import patch_html
out.write_text(patch_html(html), encoding="utf-8")
print("saved", out, len(html))
