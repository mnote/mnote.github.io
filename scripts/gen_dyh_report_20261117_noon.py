"""都业华 2026-11-17 午评（高级班·午盘）纪要 HTML（白底 · 盘中版）

⛔ 用户 2026-11-11 禁令：只用日线 + 实时快照，不调用分钟级 K 线、不调用 czsc。
📏 篇幅硬约束：正文 ≤2000 中文字、表格 ≤4 张；K 线图保留、不计字数。

输出：html/duyiehua-20261117-noon.html
"""
import json
import sys
from pathlib import Path

REPO = Path("/Users/maoling/workspace/mnote.github.io")
RPT = REPO / "reports/duyiehua-20261117"
D = json.loads((RPT / "data_20261117.json").read_text(encoding="utf-8"))
BR = json.loads((RPT / "breadth_20261117.json").read_text(encoding="utf-8"))
IX, ST, BK = D["index"], D["stocks"], D["baskets"]
POOL = D["pools"]
SUF = "20261117N"

TITLE = "DYH 午评 - 2026-11-17（周二 创新低后拉回，底背驰未成立）"

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
  .notice{background:#fffbeb;border:1px solid #fcd34d;border-left:4px solid #d97706;border-radius:8px;padding:12px 16px;margin-bottom:14px;font-size:13.5px}
  .notice b{color:#92400e}.notice p{margin:5px 0 0}
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
    s = ST[name]["snap"]
    return f'<span class="{cls(s["pct"])}">{s["close"]:.2f} ({s["pct"]:+.2f}%)</span>'


def snap(n):
    return ST[n]["snap"]


sh = IX["上证指数_snap"]
cy = IX["创业板指_snap"]
kc = IX["科创50_snap"]
hs300 = IX["沪深300_snap"]
sz = IX["深证成指_snap"]
amt_now = D["amount"]["total_yi"]
tx = D["tx_amount"]
amt_1130 = (tx["sh"]["20261117"]["amt_1130"] + tx["sz"]["20261117"]["amt_1130"]) / 1e8
amt_1130_prev = (tx["sh"]["20261116"]["amt_1130"] + tx["sz"]["20261116"]["amt_1130"]) / 1e8
amt_chg = (amt_1130 / amt_1130_prev - 1) * 100
SNAP = D["snapshot_time"]

# ---------- 板块表 ----------
BKROWS = [
    ("半导体", "老师：今天领涨，但先按弱势看待",
     f'<b>{BK["半导体"]["avg_pct"]:+.2f}%</b>，{BK["半导体"]["up"]}涨/{BK["半导体"]["down"]}跌；'
     f'中芯国际 +7.87%、北方华创 +4.28%、寒武纪 +3.33%，兆易 -1.58%'),
    ("算力/CPO", "老师：前期强势股仍在洗牌",
     f'{BK["算力/CPO"]["avg_pct"]:+.2f}%，{BK["算力/CPO"]["up"]}涨/{BK["算力/CPO"]["down"]}跌；'
     f'沪电 +1.04%、工业富联 +0.69%，新易盛 -3.67%、中际旭创 -2.88%'),
    ("银行", "老师：防御品种走温和震荡",
     f'{BK["银行"]["avg_pct"]:+.2f}%，<b>0 涨 {BK["银行"]["down"]} 跌</b>；'
     f'兴业 -0.15%、建行 -0.16%，招行 -0.58%'),
    ("电力/高股息", "同上",
     f'{BK["电力/高股息"]["avg_pct"]:+.2f}%，1涨/{BK["电力/高股息"]["down"]}跌；'
     f'川投 +0.55%、长电 -0.62%、中国核电 -1.21%'),
    ("煤炭/石油", "同上",
     f'{BK["煤炭/石油"]["avg_pct"]:+.2f}%，1涨/{BK["煤炭/石油"]["down"]}跌；'
     f'石化 +0.17%、神华 -1.18%、中海油 -3.79%'),
    ("人形机器人", "老师：机器人已经走弱",
     f'{BK["人形机器人"]["avg_pct"]:+.2f}%，{BK["人形机器人"]["up"]}涨/{BK["人形机器人"]["down"]}跌；'
     f'兆威机电 -5.86%、长盈精密 -5.10%，华达科技跌停'),
    ("AI视频/传媒", "老师：上午跌破支撑，大概率不行",
     f'<b>{BK["AI视频/传媒"]["avg_pct"]:+.2f}%</b>，<b>0 涨 {BK["AI视频/传媒"]["down"]} 跌</b>；'
     f'华策影视 -12.22%、中文在线 -8.03%、上海电影 -6.11%，<b>跌停池 9 只</b>'),
]

# ---------- 标的表 ----------
ROWS = [
    ("药明康德", "大医药", "不操作 · 等突破 157.8 出 15 分钟底分型三买（谨慎者等日线有力度底分型）",
     "157.8", f'最高 {snap("药明康德")["high"]:.2f}，<b>差 {157.8-snap("药明康德")["high"]:.2f} 元</b>；走势抗跌（+1.23%）', "等"),
    ("中国船舶", "船舶", "不操作 · 走势没止跌",
     "—", f'最低 {snap("中国船舶")["low"]:.2f}，破昨低 33.55，未止跌', "等"),
    ("瑞芯微", "半导体", "激进思路 · 等日线有力度底分型后过第三根 K 线高点",
     "208", f'盘中低 {snap("瑞芯微")["low"]:.2f} <b>跌破 208（-{snap("瑞芯微")["low"]-208:.2f}）</b>后拉回，'
     f'底分型未出、短期压力未过', "等"),
    ("伊利股份", "大消费", "不操作 · 前期已说不追涨；持仓者看小级别顶背驰",
     "30.46", f'最高 {snap("伊利股份")["high"]:.2f} <b>创 60 日新高</b>，位置仍高', "不追"),
    ("中文在线", "AI视频", "不操作 · 等过高点 30.38 后的三买",
     "30.38", f'最高 {snap("中文在线")["high"]:.2f}，差 {30.38-snap("中文在线")["high"]:.2f}；'
     f'最低 {snap("中文在线")["low"]:.2f} 破 11/09 低点 25.65', "等"),
    ("海天瑞声", "机器人", "不操作 · 破位迹象，先看能否修复",
     "141", f'最低 {snap("海天瑞声")["low"]:.2f}，破位；141 门槛差 {141-snap("海天瑞声")["high"]:.2f}', "等"),
    ("奥普特", "机器视觉", "不操作 · 破位迹象，先观察修复",
     "140", f'最低 {snap("奥普特")["low"]:.2f} <b>破 140 下沿 {snap("奥普特")["low"]-140:.2f} 元</b>', "等"),
    ("柯力传感", "传感器", "不操作 · 等日线有力度底分型后再评估",
     "53", f'最低 {snap("柯力传感")["low"]:.2f}，破 53 支撑 {53-snap("柯力传感")["low"]:.2f} 元', "等"),
    ("兆易创新", "存储芯片", "无操作 · ①等日线底分型 ②突破收复站稳 233",
     "233", f'最高 {snap("兆易创新")["high"]:.2f}，<b>差 {233-snap("兆易创新")["high"]:.2f} 元</b>；'
     f'探底 {snap("兆易创新")["low"]:.2f} 后回升，底背驰未成立', "等"),
    ("模塑科技", "机器人", "不操作 · 等日线有力度底分型；注意明早英伟达业绩",
     "14.95", f'最低 {snap("模塑科技")["low"]:.2f} <b>创新低并破 14.95（{snap("模塑科技")["low"]-14.95:.2f}）</b>，'
     f'现拉回 +1.38%，底分型未出', "等"),
    ("长盈精密", "机器人", "不操作 · 走势没有止跌",
     "32.08", f'最低 {snap("长盈精密")["low"]:.2f}，破昨低 26.43，未止跌', "等"),
]

DEVS = [
    ("老师：「一些防御性品种走出比较温和的震荡上扬」",
     f'银行 {BK["银行"]["avg_pct"]:+.2f}%（0涨5跌）、电力 {BK["电力/高股息"]["avg_pct"]:+.2f}%、'
     f'煤炭石油 {BK["煤炭/石油"]["avg_pct"]:+.2f}%；新浪行业涨幅榜首仅 开发区 +0.59%',
     "<b>未兑现</b>"),
    ("老师原文「如果走势无法突破 3263 点」",
     "与同段「昨日上午高点 3623」自相矛盾；实测今日最高 3602.07，3623.12 未破（差 21.05 点）",
     "疑为笔误"),
    ("老师：「上证指数盘中创出短期新低」",
     "最低 3565.59，跌破 11/16 低 3586.57 <b>并跌破 60 日低 3574.27</b>，幅度大于「短期新低」",
     "<b>比表述更弱</b>"),
    ("老师：「盘面比较弱」「防御与指数节奏相反」",
     f'全 A 涨 {BR["up"]} > 跌 {BR["down"]}（涨停 {POOL["zt"]["tc"]}、跌停 {POOL["dt"]["tc"]}），'
     f'科创50 {kc["pct"]:+.2f}%、中证500 +0.88% 逆势，指数弱但个股不弱',
     "权重拖累"),
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

<div class="notice">
  <b>📌 版本说明（2026-11-19 加注）· 本页保留，未撤回</b>
  <p>本页是 <b>2026-11-17 午评</b>的核验记录 —— 当日行情与老师口径逐条吻合，结论成立，正文未作任何修改。<br>
  2026-11-19 用户提供了一份<b>内容相同、标注为「19 号」</b>的午评原文，并要求另出 11/19 报告。核验发现该原文的 4 条事实型判据（昨日上午高点 3623、昨日二类热点＝传媒、明早英伟达业绩、半导体今天领涨）<b>全部指向 11/17 上午</b>，与 11/19 实际不符 —— 逐条对照见 11/19 午评的「偏差记录」。<br>
  因此本页<b>保留为 11/17 的历史记录</b>；另出了一份按 11/19 上午实测行情出稿的报告 →
  <a href="/html/duyiehua-20261119-noon.html">DYH 午评 - 2026-11-19（周四 探低回升创新低，半导体未领涨）</a>。</p>
</div>

<div class="hero">
  <h1>📈 {TITLE}</h1>
  <div class="meta"><a href="/" style="color:#2563eb;text-decoration:none">← 返回首页</a><span style="color:#9ca3af"> · </span>盘中版 · 数据截至 2026-11-17 {SNAP}（未收盘）</div>
  <p class="stance"><b>结论：创新低后马上被拉回 → 不算底背驰，走势只能界定为震荡，仍按弱势看待，仓位轻。</b>
  上证低开 3585.67 探至 <b>3565.59</b>（破 11/16 低与 60 日低 3574.27）后拉回 {sh['close']:.2f}（{sh['pct']:+.2f}%）；
  <b>昨日上午高点 3623.12 未翻过</b>（差 21.05 点），短线止跌未确认。半导体领涨（{BK["半导体"]["avg_pct"]:+.2f}%）但按弱势处理，
  AI视频/传媒 {BK["AI视频/传媒"]["avg_pct"]:+.2f}%（跌停 9 只）已走弱。<b>11 只标的全部无方法买点。</b></p>
</div>

<div class="grid4">
  <div class="kpi"><div class="label">上证指数 · 3623 未破</div><div class="val down">{sh['pct']:+.2f}%</div><div class="sub">{sh['close']:.2f} · 低 {sh['low']:.2f} 破 60 日低</div></div>
  <div class="kpi"><div class="label">科创50 / 创业板指</div><div class="val up">{kc['pct']:+.2f}% / <span class="down">{cy['pct']:+.2f}%</span></div><div class="sub">沪深300 {hs300['pct']:+.2f}% · 深成 {sz['pct']:+.2f}%</div></div>
  <div class="kpi"><div class="label">两市累计成交额（{SNAP}）</div><div class="val vol">{amt_now:,.0f} 亿</div><div class="sub down">11:30 同时点 {amt_chg:+.2f}%（昨同刻 {amt_1130_prev:,.0f}）</div></div>
  <div class="kpi"><div class="label">涨 / 跌家数（{BR['snapshot'][-5:]}）</div><div class="val"><span class="up">{BR['up']}</span> / <span class="down">{BR['down']}</span></div><div class="sub">涨停 {POOL['zt']['tc']} · 跌停 {POOL['dt']['tc']} · 炸板 {POOL['zb']['tc']}</div></div>
</div>

<h2>一、指数：创新低后拉回，只算震荡</h2>
<p>老师三个判据逐条对上：① <b>低开后探底回升、盘中创短期新低</b> —— 开 3585.67 低于昨收 3602.57，探至 3565.59 后拉回 {sh['close']:.2f}，<b>低点既破 11/16 的 3586.57，也破 60 日低 3574.27</b>；② <b>昨日上午高点 3623 是短线止跌的门槛</b> —— 今日最高 3602.07，<b>差 21.05 点没翻过去</b>，短线止跌不成立；③ <b>3750</b> 差 147.93 点（4.11%），远门槛。</p>
<p>按老师自己的判据推演：<b>创出新低后马上被拉回，不属于底背驰</b>，因此当前位置不能判断底背驰出现，走势<b>只能界定为震荡、先看成短期低点</b>，不给阶段低点判断 —— 今天日内形态（探低 +0.95% 拉回）正好就是这个结论的实证。风险是「在前低点附近做 2–3 天弱势震荡，这种震荡属于没有止跌的表现」。</p>
<p>结构上是<b>权重弱、成长分化</b>：科创50 <span class="up">{kc['pct']:+.2f}%</span>（中芯 +7.87%）、中证500 +0.88%，创业板 <span class="down">{cy['pct']:+.2f}%</span> 且最低 2284.56 再创 60 日新低。量能上，11:30 两市 {amt_1130:,.0f} 亿 vs 昨日同时点 {amt_1130_prev:,.0f} 亿（<span class="vol">{amt_chg:+.2f}%</span>，<b>基本持平</b>），13:2x 累计 {amt_now:,.0f} 亿。</p>
<img class="chart" src="../charts/000001_SH_DY_{SUF}.png">
<img class="chart" src="../charts/399006_SZ_DY_{SUF}.png">

<h2>二、板块：半导体领涨是超跌反弹，传媒塌方</h2>
<table>
  <tr><th>方向（自建篮子）</th><th>老师口径</th><th>实测（均值 · 涨跌家数 · 个股）</th></tr>
  {''.join(f'<tr><td><b>{n}</b></td><td>{t}</td><td>{v}</td></tr>' for n, t, v in BKROWS)}
</table>
<p><b>三条要记的：</b>① <b>「今天领涨的是半导体」成立</b>（中芯 +7.87%、北方华创 +4.28%、寒武纪 +3.33%），但老师同句提醒「半导体是近两天下跌幅度比较大的板块，阶段低点还无法确认」—— 11/16 该篮子收跌 5.53%，<b>今天这根只能当超跌反弹，不当新方向，不追</b>；② <b>「传媒大概率不行」比老师说的更严重</b>：篮子 {BK["AI视频/传媒"]["avg_pct"]:+.2f}%（0 涨 7 跌，华策 -12.22%、中文在线 -8.03%），<b>跌停池里传媒链占 9 只</b>（慈文传媒、华数传媒、湖北广电、大晟文化、电魂网络、龙版传媒、横店影视、文投控股、浙文影业），昨日二类热点直接塌方；③ <b>「全体洗牌」成立</b>：玄学链大东方、东方环宇双双跌停，机器人篮子 {BK["人形机器人"]["avg_pct"]:+.2f}%（2 涨 7 跌）配华达科技跌停 —— 旧热点全灭，涨停 44 只却分散在 14 个行业（IT服务、环保设备、光学光电…），<b>没有新主线冒头</b>。</p>

<h2>三、11 只标的：全部无方法买点</h2>
<table>
  <tr><th>标的 / 题材</th><th>现价</th><th>老师定性（老师口径）</th><th>关键位</th><th>实测印证（日线触达）</th><th>动作</th></tr>
  {''.join(f'<tr><td><b>{n}</b><br><span class="meta">{t}</span></td><td class="num">{px(n)}</td><td>{d}</td><td class="kn">{k}</td><td>{e}</td><td><span class="tag {"tag-bear" if a=="不追" else "tag-neutral"}">{a}</span></td></tr>' for n, t, d, k, e, a in ROWS)}
</table>
<img class="chart" src="../charts/603259_SH_DY_{SUF}.png">
<img class="chart" src="../charts/600150_SH_DY_{SUF}.png">
<img class="chart" src="../charts/603893_SH_DY_{SUF}.png">
<img class="chart" src="../charts/600887_SH_DY_{SUF}.png">
<img class="chart" src="../charts/300364_SZ_DY_{SUF}.png">
<img class="chart" src="../charts/688787_SH_DY_{SUF}.png">
<img class="chart" src="../charts/688686_SH_DY_{SUF}.png">
<img class="chart" src="../charts/603662_SH_DY_{SUF}.png">
<img class="chart" src="../charts/603986_SH_DY_{SUF}.png">
<img class="chart" src="../charts/000700_SZ_DY_{SUF}.png">
<img class="chart" src="../charts/300115_SZ_DY_{SUF}.png">

<h2>四、明日关注（可验证条件）</h2>
<div class="box box-a">
① <b>上证能否站上 3623.12</b>（昨日上午高点）—— 站上才有「短线止跌」的第一个确认；<b>跌破 3565.59 / 3574.27</b> 则是继续新低，底背驰更远。<br>
② <b>半导体能不能连续两日不回落</b>（中芯、北方华创）—— 只涨一天是超跌反弹，两日站稳才谈得上方向。<br>
③ <b>跌停家数能否收敛</b>（今日跌停 {POOL['dt']['tc']} 家、传媒链 9 只）—— 收敛前不接任何旧热点。<br>
④ <b>瑞芯微 208</b>：今日盘中已跌破 208（低 {snap("瑞芯微")["low"]:.2f}）后拉回，等的是<b>日线有力度底分型 + 过第三根 K 线高点</b>，不是盘中异动。<br>
⑤ <b>明早英伟达业绩</b>（外盘扰动，无法预判）—— 模塑科技、兆易创新等科技标的今日都已创新低，<b>不提前赌</b>。
</div>
<div class="box box-r">
<b>纪律（原文明写）：</b>① 总体仓位<b>保持轻仓</b>，耐心等底背驰是否出现 —— 今天创新低后立刻拉回，恰恰说明还没到；② <b>防御性品种不追涨</b>（节奏与指数相反），等回调做三买时再找机会；③ <b>震荡内部操作难度大</b>，老师对 11 只标的<b>全部不给买点</b>，没给买点就是没有，不改写成「可试探」。
</div>

<h2>五、偏差记录</h2>
<table>
  <tr><th>老师原文</th><th>实测</th><th>判定</th></tr>
  {''.join(f'<tr><td>{a}</td><td>{b}</td><td><span class="tag {"tag-bull" if c=="权重拖累" else "tag-neutral"}">{c}</span></td></tr>' for a, b, c in DEVS)}
</table>

<div class="foot">
  <p>来源：都业华《高级班》2026-11-17 午盘（高级班·午盘），执业编号 A0400626100004。<b>仅供参考，不作为买卖依据，据此操作风险自担。投资有风险，入市需谨慎！</b></p>
  <p><b>口径：</b>同花顺公开接口日线（140 根）+ {SNAP} 实时快照（最后一根 K 线未走完、成交量为盘中累计）；板块为自建篮子均值（成分逐一列出）；涨跌家数取新浪全 A {BR['n']} 只 {BR['snapshot'][-5:]} 快照；涨停/跌停用东财池；成交额同比取腾讯 5 日分时「同时点 11:30」累计。缠论定性按老师口径引用，不声称我方复算过 15 分钟结构。</p>
</div>

</div>
</body>
</html>
"""

out = REPO / "html/duyiehua-20261117-noon.html"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from fix_mobile_tables import patch_html
out.write_text(patch_html(html), encoding="utf-8")
print("saved", out, len(html))
