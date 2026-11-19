"""都业华 2026-11-19 午评（高级班·午盘）纪要 HTML（白底 · 盘中版）

⛔ 用户 2026-11-11 禁令：只用日线 + 实时快照，不调用分钟级 K 线、不调用 czsc。
📏 篇幅硬约束：正文 ≤2000 中文字、表格 ≤4 张；K 线图保留、不计字数。

输出：html/duyiehua-20261119-noon.html
"""
import json
import sys
from pathlib import Path

REPO = Path("/Users/maoling/workspace/mnote.github.io")
RPT = REPO / "reports/duyiehua-20261119"
D = json.loads((RPT / "data_20261119.json").read_text(encoding="utf-8"))
BR = json.loads((RPT / "breadth_20261119.json").read_text(encoding="utf-8"))
IX, ST, BK = D["index"], D["stocks"], D["baskets"]
POOL = D["pools"]
SUF = "20261119N"

TITLE = "DYH 午评 - 2026-11-19（周四 探低回升创新低，半导体未领涨）"

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
amt_1130 = (tx["sh"]["20261119"]["amt_1130"] + tx["sz"]["20261119"]["amt_1130"]) / 1e8
amt_1130_prev = (tx["sh"]["20261118"]["amt_1130"] + tx["sz"]["20261118"]["amt_1130"]) / 1e8
amt_chg = (amt_1130 / amt_1130_prev - 1) * 100
SNAP = D["snapshot_time"]

# ---------- 板块表 ----------
BKROWS = [
    ("半导体", "老师：今天领涨，按弱势看待",
     f'<b>{BK["半导体"]["avg_pct"]:+.2f}%</b>（2 涨 4 跌），<b>内部撕裂</b>：中芯国际 +5.47%、北方华创 +2.25%；'
     f'<b>海光信息 -13.03%</b>、瑞芯微 -1.92%、寒武纪 -1.63%、兆易 -0.94%'),
    ("AI视频/传媒", "老师：跌破支撑，大概率不行",
     f'<b>{BK["AI视频/传媒"]["avg_pct"]:+.2f}%</b>，<b>0 涨 7 跌</b>；掌阅科技 -4.24%、上海电影 -4.25%、'
     f'捷成股份 -2.79%、昆仑万维 -2.57%、中文在线 -1.98%、华策影视 -1.84%'),
    ("人形机器人", "老师：机器人已走弱",
     f'{BK["人形机器人"]["avg_pct"]:+.2f}%（4 涨 5 跌），<b>内部反而有分化</b>：拓普集团 +4.26%、兆威机电 +2.13%、'
     f'三花智控 +1.49%；模塑科技 -3.32%、鸣志电器 -1.30%、长盈精密 -1.66%'),
    ("算力/CPO", "老师：强势股仍在洗牌",
     f'{BK["算力/CPO"]["avg_pct"]:+.2f}%（3 涨 2 跌）；新易盛 +2.19%、沪电 +0.90%、中际旭创 +0.87%，'
     f'工业富联 -1.21%、胜宏科技 -1.22%'),
    ("银行", "老师：防御品种温和上扬",
     f'{BK["银行"]["avg_pct"]:+.2f}%（2 涨 3 跌）；招商银行 +0.07%、兴业银行 +0.15%，'
     f'农业银行 -0.92%、建设银行 -0.32%'),
    ("电力/高股息", "同上",
     f'{BK["电力/高股息"]["avg_pct"]:+.2f}%（2 涨 3 跌）；华能水电 +0.89%、国投电力 +0.25%，中国核电 -0.81%'),
    ("饮料制造", "同上",
     f'<b>{BK["饮料制造"]["avg_pct"]:+.2f}%</b>（4 涨 1 跌）；东鹏饮料 +1.58%、欢乐家 +1.44%、养元饮品 +1.11%'),
    ("家电", "同上",
     f'<b>{BK["家电"]["avg_pct"]:+.2f}%</b>（4 涨 0 跌）；海尔智家 +1.24%、海信视像 +1.10%、美的 +0.53%、格力 +0.37%'),
    ("煤炭/石油", "同上",
     f'{BK["煤炭/石油"]["avg_pct"]:+.2f}%（<b>0 涨 5 跌</b>）；中国石化 -1.34%、中国石油 -1.27%、'
     f'中国海油 -1.60%、中国神华 -0.41%'),
]

# ---------- 标的表 ----------
ROWS = [
    ("药明康德", "大医药", "不操作 · 等突破 157.8 出 15 分钟底分型三买；或日线有力度底分型（谨慎）",
     "157.8", f'{snap("药明康德")["close"]:.2f} <b>{snap("药明康德")["pct"]:+.2f}%</b>，'
     f'低 {snap("药明康德")["low"]:.2f}，最高 {snap("药明康德")["high"]:.2f}，'
     f'距 157.8 差 {157.8-snap("药明康德")["high"]:.2f} 元；<b>「走势非常抗跌」未兑现</b>', "等"),
    ("中国船舶", "船舶", "不操作 · 走势没止跌",
     "—", f'低 {snap("中国船舶")["low"]:.2f}；<b>未止跌成立</b>', "等"),
    ("瑞芯微", "半导体", "激进思路 · 等日线有力度底分型后过第三根 K 线高点",
     "208", f'低 <b>{snap("瑞芯微")["low"]:.2f}</b> 破 11/18 低 192.76，仍远低于 208 与 220.7；'
     f'盘中异动不能判止跌，底分型未出', "等"),
    ("伊利股份", "大消费", "不操作 · 前期已说不要追涨；持仓者看小级别顶背驰",
     "—", f'最高 <b>{snap("伊利股份")["high"]:.2f} 续创 60 日新高</b>，收 '
     f'{snap("伊利股份")["close"]:.2f} <b>{snap("伊利股份")["pct"]:+.2f}%</b>；位置更高，不追仍成立', "不追"),
    ("中文在线", "AI视频", "不操作 · 等过高点 30.38 后的三买",
     "30.38", f'低 <b>{snap("中文在线")["low"]:.2f}</b> 破 11/18 低 22.85，距 30.38 差 '
     f'{30.38-snap("中文在线")["high"]:.2f} 元', "等"),
    ("海天瑞声", "机器人", "不操作 · 破位迹象，先观察能否修复",
     "141", f'低 <b>{snap("海天瑞声")["low"]:.2f} 再破前低</b>（11/18 低 89.80），破位加重；'
     f'距 60 日低 76.54 还有 11.6%', "等"),
    ("奥普特", "机器视觉", "不操作 · 破位迹象，先观察修复",
     "140", f'低 <b>{snap("奥普特")["low"]:.2f} 破前低</b>（11/18 低 127.65）；距 140 门槛差 '
     f'{140-snap("奥普特")["high"]:.2f} 元', "等"),
    ("柯力传感", "传感器", "不操作 · 等日线有力度底分型后再评估",
     "53", f'低 <b>{snap("柯力传感")["low"]:.2f} 破前低</b>（11/18 低 46.90），远低于 53 支撑；'
     f'底分型未出', "等"),
    ("兆易创新", "存储芯片", "无操作 · ①等日线底分型 ②收复站稳 233，防构建新中枢延续",
     "233", f'探低 {snap("兆易创新")["low"]:.2f} 后回升，最高 {snap("兆易创新")["high"]:.2f}，<b>距 233 差 {233-snap("兆易创新")["high"]:.2f} 元</b>；底背驰未成立', "等"),
    ("模塑科技", "机器人", "不操作 · 等日线有力度底分型；<b>提示英伟达业绩风险</b>",
     "14.95", f'低 <b>{snap("模塑科技")["low"]:.2f} 创新低并破 14.95</b>（11/18 低 14.27），收 '
     f'{snap("模塑科技")["close"]:.2f} <b>{snap("模塑科技")["pct"]:+.2f}%</b>；<b>「走势抗跌」不成立</b>', "等"),
    ("长盈精密", "机器人", "不操作 · 走势没有止跌",
     "—", f'低 <b>{snap("长盈精密")["low"]:.2f} 破 11/18 低 22.89</b>；未止跌成立', "等"),
]

DEVS = [
    ("老师：「昨日上午高点 3623 点」",
     f'11/18 上午高点 <b>3596.55</b>，3623 实为 <b>11/16 上午高点 3621.56</b>',
     "数值与「昨日」对不上"),
    ("老师：「昨日二类热点榜的传媒」",
     '11/18 二类热点是<b>国产算力</b>；传媒是 <b>11/16 收评</b>的二类热点',
     "指向 11/16"),
    ("老师：「明早英伟达业绩」",
     'FY27Q3 已于 <b>11/17 美股盘后</b>发布（北京时间 11/18 早间），11/19 无「明早」事件',
     "事件已过期"),
    ("老师：「今天领涨的是半导体」",
     f'半导体篮子 <b>{BK["半导体"]["avg_pct"]:+.2f}%</b>（海光 -13.03% 拖累）；行业榜榜首仅陶瓷 +0.72%',
     "未领涨"),
    ("老师：「无法突破 3263 点」",
     '与同段「昨日上午高点 3623」自相矛盾，实测今日最高 ' + f'{sh["high"]:.2f}',
     "疑为笔误"),
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
  <div class="meta"><a href="/" style="color:#2563eb;text-decoration:none">← 返回首页</a><span style="color:#9ca3af"> · </span>盘中版 · 数据截至 2026-11-19 {SNAP}（未收盘）</div>
  <p class="stance"><b>结论：探低回升但创新低，底背驰仍不能判定，轻仓等待。</b>
  上午上证低开 <b>{sh['open']:.2f}</b> 探至 <b>{sh['low']:.2f}</b>（破 11/18 低 3560.45，<b>创 60 日新低</b>）后拉回 {sh['close']:.2f}（<span class="down">{sh['pct']:+.2f}%</span>）；
  3623 门槛未到（今日最高 {sh['high']:.2f}，差 {3623.12-sh['high']:.2f} 点）→ 走势只能界定为震荡，<b>不给阶段低点判断</b>。
  跌家数 {BR['down']}（{BR['down']/BR['n']*100:.0f}%）、涨停 {POOL['zt']['tc']} 家，<b>11 只标的无方法买点</b>。
  <b>⚠ 原文日期存疑</b>：「3623」「昨日二类热点」「明早英伟达」「半导体领涨」四条对不上 11/19 实际，见偏差记录。</p>
</div>

<div class="grid4">
  <div class="kpi"><div class="label">上证指数 · 创 60 日新低</div><div class="val down">{sh['pct']:+.2f}%</div><div class="sub">{sh['close']:.2f} · 低 {sh['low']:.2f}（破 3560.45）</div></div>
  <div class="kpi"><div class="label">科创50 / 创业板指</div><div class="val up">{kc['pct']:+.2f}% / <span class="down">{cy['pct']:+.2f}%</span></div><div class="sub">沪深300 {hs300['pct']:+.2f}% · 深成 {sz['pct']:+.2f}%</div></div>
  <div class="kpi"><div class="label">两市累计成交额（11:30）</div><div class="val vol">{amt_now:,.0f} 亿</div><div class="sub vol">同比 {amt_chg:+.2f}%（昨同刻 {amt_1130_prev:,.0f}）</div></div>
  <div class="kpi"><div class="label">涨 / 跌家数</div><div class="val"><span class="up">{BR['up']}</span> / <span class="down">{BR['down']}</span></div><div class="sub">涨停 {POOL['zt']['tc']} · 跌停 {POOL['dt']['tc']} · 炸板 {POOL['zb']['tc']}</div></div>
</div>

<h2>一、指数：低开探底回升，创短期新低</h2>
<p>三个判据逐条核：① <b>「低开后探底回升、上证盘中创出短期新低」</b> —— 开 {sh['open']:.2f}（开盘即全天最高）→ 探 {sh['low']:.2f} → 收 {sh['close']:.2f}，破 11/18 的 3560.45，<b>创 60 日新低</b> ✓；② <b>「观察昨日上午高点 3623 能否翻过去」</b> —— 今日最高 {sh['high']:.2f}，差 {3623.12-sh['high']:.2f} 点，<b>未满足</b>（11/18 上午高点实为 3596.55，见偏差记录）；③ 3750 差 {3750-sh['close']:.2f} 点，更远。按老师自己的推演：<b>创新低后马上被拉回不属于底背驰</b>，走势只能界定为震荡、先看成短期低点，<b>不给阶段低点判断</b>。</p>
<p>风险点照抄：<b>「在前低点附近做 2-3 天的弱势震荡，这种震荡属于没有止跌的表现」</b>。结构上是<b>权重拖累、宽度极差</b> —— 全 A {BR['n']} 只跌 {BR['down']} 只（{BR['down']/BR['n']*100:.0f}%）、跌超 5% {BR['down_5']} 家；11:30 两市 {amt_1130:,.0f} 亿 vs 昨日同时点 {amt_1130_prev:,.0f} 亿（<span class="vol">{amt_chg:+.2f}%</span>）。科创50 <span class="up">{kc['pct']:+.2f}%</span> 逆势红只是权重集中，创业板 <span class="down">{cy['pct']:+.2f}%</span>、深成 {sz['pct']:+.2f}%、沪深300 {hs300['pct']:+.2f}% 同步走弱。</p>
<img class="chart" src="../charts/000001_SH_DY_{SUF}.png">
<img class="chart" src="../charts/399006_SZ_DY_{SUF}.png">

<h2>二、板块：半导体内部撕裂，传媒走弱、防御小幅上扬</h2>
<table>
  <tr><th>方向（自建篮子）</th><th>老师口径</th><th>实测（均值 · 涨跌家数 · 个股）</th></tr>
  {''.join(f'<tr><td><b>{n}</b></td><td>{t}</td><td>{v}</td></tr>' for n, t, v in BKROWS)}
</table>
<p><b>三条要记的：</b>① <b>「传媒大概率不行」成立</b> —— AI视频/传媒 {BK['AI视频/传媒']['avg_pct']:+.2f}%（0 涨 7 跌），昨日二类热点直接塌方；② <b>「今天领涨的是半导体」不成立</b> —— 半导体篮子 {BK['半导体']['avg_pct']:+.2f}%（2 涨 4 跌），<b>海光信息 -13.03%</b> 拖累，中芯国际 +5.47%、北方华创 +2.25% 独强，<b>是内部撕裂而非领涨</b>；新浪行业榜涨幅榜首仅陶瓷行业 +0.72%，全市场无行业涨超 1%；③ <b>「防御品种温和上扬」部分成立</b> —— 饮料制造 {BK['饮料制造']['avg_pct']:+.2f}%（4 涨 1 跌）、家电 {BK['家电']['avg_pct']:+.2f}%（4 涨 0 跌）、电力 {BK['电力/高股息']['avg_pct']:+.2f}%，但煤炭/石油 {BK['煤炭/石油']['avg_pct']:+.2f}%（0 涨 5 跌）、银行 {BK['银行']['avg_pct']:+.2f}%，<b>红利不是全面抱团</b>；人形机器人 {BK['人形机器人']['avg_pct']:+.2f}% 也谈不上「已经走弱」。</p>

<h2>三、11 只标的：全部无方法买点</h2>
<table>
  <tr><th>标的 / 题材</th><th>现价</th><th>老师定性（老师口径）</th><th>关键位</th><th>实测印证（日线触达）</th><th>动作</th></tr>
  {''.join(f'<tr><td><b>{n}</b><br><span class="meta">{t}</span></td><td class="num">{px(n)}</td><td>{d}</td><td class="kn">{k}</td><td>{e}</td><td><span class="tag {"tag-bear" if a=="不追" else "tag-neutral"}">{a}</span></td></tr>' for n, t, d, k, e, a in ROWS)}
</table>
<img class="chart" src="../charts/603259_SH_DY_{SUF}.png">
<img class="chart" src="../charts/600150_SH_DY_{SUF}.png">
<img class="chart" src="../charts/603893_SH_DY_{SUF}.png">
<img class="chart" src="../charts/600887_SH_DY_{SUF}.png">
<img class="chart" src="../charts/688787_SH_DY_{SUF}.png">
<img class="chart" src="../charts/688686_SH_DY_{SUF}.png">
<img class="chart" src="../charts/603662_SH_DY_{SUF}.png">
<img class="chart" src="../charts/300364_SZ_DY_{SUF}.png">
<img class="chart" src="../charts/603986_SH_DY_{SUF}.png">
<img class="chart" src="../charts/000700_SZ_DY_{SUF}.png">
<img class="chart" src="../charts/300115_SZ_DY_{SUF}.png">

<h2>四、下午关注（可验证条件）</h2>
<div class="box box-a">
① <b>上证 {sh['low']:.2f}（今创 60 日新低）</b>：下午破了 = 震荡向下创新低延续，进入底背驰观察窗口；守住并收复 {sh['open']:.2f}（今日开盘=最高）才算日内转强。<br>
② <b>3623 门槛</b>：今日最高 {sh['high']:.2f}，差 {3623.12-sh['high']:.2f} 点 —— 站上并站稳才有「短线止跌」第一个确认；3750 差 {3750-sh['close']:.2f} 点，更远。<br>
③ <b>半导体撕裂能否收敛</b>：海光信息 -13.03% 继续下挫 = 科技链分化加剧；中芯 +5.47% 独强不等于板块止跌。<br>
④ <b>跌停家数能否收敛</b>：东财跌停 {POOL['dt']['tc']} 家、炸板 {POOL['zb']['tc']} 家，跌超 9% {BR['down_9']} 家 —— 收敛前不接旧热点。<br>
⑤ <b>英伟达事件已过期</b>：FY27Q3 已于 11/17 美股盘后发布、11/18 夜盘已消化，原文「明早英伟达」在 11/19 无对应事件。
</div>
<div class="box box-r">
<b>纪律（原文明写）：</b>① <b>总体仓位保持轻仓</b>，耐心等底背驰出现 —— 创新低后立刻被拉回恰恰说明还没到；② <b>防御性品种不追涨</b>（节奏与指数相反），等回调做三买；③ <b>震荡内部操作难度大</b>，11 只标的<b>全部「无方法买点」= 没有</b>。
</div>

<h2>五、偏差记录</h2>
<table>
  <tr><th>老师原文</th><th>实测</th><th>判定</th></tr>
  {''.join(f'<tr><td>{a}</td><td>{b}</td><td><span class="tag tag-none">{c}</span></td></tr>' for a, b, c in DEVS)}
</table>
<p style="color:var(--muted);font-size:12.5px">说明：原文「低开探底回升创新低」「传媒走弱」「防御品种温和上扬」「模塑科技今日创新低」「11 只标的无方法买点」在 11/19 上午均<b>成立</b>；但上表 4 条可证伪的事实型判据与 11/19 不符、与 <b>11/17 上午</b>逐条吻合 —— 原文很可能是 11/17 午评的重发。本纪要按 11/19 实测行情出。</p>

<div class="foot">
  <p>来源：都业华《高级班》2026-11-19 午盘（高级班·午盘），执业编号 A0400626100004。<b>仅供参考，不作为买卖依据，据此操作风险自担。投资有风险，入市需谨慎！</b></p>
  <p><b>口径：</b>同花顺公开接口日线（140 根）+ {SNAP} 实时快照（最后一根 K 线未走完、成交量为盘中累计）；板块为自建篮子均值（成分逐一列出）；涨跌家数取新浪全 A {BR['n']} 只快照；涨停/跌停用东财池；成交额同比取腾讯 5 日分时「同时点 11:30」累计。缠论定性按老师口径引用，不声称我方复算过 15 分钟结构。</p>
</div>

</div>
</body>
</html>
"""

out = REPO / "html/duyiehua-20261119-noon.html"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from fix_mobile_tables import patch_html
out.write_text(patch_html(html), encoding="utf-8")
print("saved", out, len(html))
