"""都业华 2026-11-18 午评（高级班·午盘）纪要 HTML（白底 · 盘中版）

⛔ 用户 2026-11-11 禁令：只用日线 + 实时快照，不调用分钟级 K 线、不调用 czsc。
📏 篇幅硬约束：正文 ≤2000 中文字、表格 ≤4 张；K 线图保留、不计字数。

输出：html/duyiehua-20261118-noon.html
"""
import json
import sys
from pathlib import Path

REPO = Path("/Users/maoling/workspace/mnote.github.io")
RPT = REPO / "reports/duyiehua-20261118"
D = json.loads((RPT / "data_20261118.json").read_text(encoding="utf-8"))
BR = json.loads((RPT / "breadth_20261118.json").read_text(encoding="utf-8"))
IX, ST, BK = D["index"], D["stocks"], D["baskets"]
POOL = D["pools"]
SUF = "20261118N"

TITLE = "DYH 午评 - 2026-11-18（周三 窄幅震荡，3623未破，池内无买点）"

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
amt_1130 = (tx["sh"]["20261118"]["amt_1130"] + tx["sz"]["20261118"]["amt_1130"]) / 1e8
amt_1130_prev = (tx["sh"]["20261117"]["amt_1130"] + tx["sz"]["20261117"]["amt_1130"]) / 1e8
amt_chg = (amt_1130 / amt_1130_prev - 1) * 100
SNAP = D["snapshot_time"]

# ---------- 板块表 ----------
BKROWS = [
    ("公路", "老师：高股息里表现较好",
     f'<b>{BK["公路"]["avg_pct"]:+.2f}%</b>，<b>5 涨 0 跌</b>；皖通高速 +4.11%、山东高速 +2.47%、深高速 +1.59%'),
    ("家电", "同上",
     f'<b>{BK["家电"]["avg_pct"]:+.2f}%</b>，5 涨 0 跌；海信视像 +1.96%、海尔智家 +1.52%、老板电器 +0.98%'),
    ("饮料制造", "老师：出现回调",
     f'<b>{BK["饮料制造"]["avg_pct"]:+.2f}%</b>，<b>0 涨 5 跌</b>；欢乐家 -4.57%、李子园 -2.47%、东鹏饮料 -1.22%'),
    ("银行", "老师：高股息未全面抱团",
     f'{BK["银行"]["avg_pct"]:+.2f}%，2 涨 2 跌 1 平；农业银行 +0.53%、建设银行 +0.08%，兴业银行 -0.89%'),
    ("半导体", "老师：走势不好，空间不多",
     f'{BK["半导体"]["avg_pct"]:+.2f}%（4 涨 2 跌），内部撕裂：寒武纪 +3.23%、海光 +0.84%，'
     f'瑞芯微 <b>-4.85%</b>、北方华创 -1.11%'),
    ("算力/CPO", "老师：国产算力有动作，CPO 弱",
     f'{BK["算力/CPO"]["avg_pct"]:+.2f}%（3 涨 2 跌）：沪电 +6.45%、工业富联 +3.93%、胜宏 +3.92%；'
     f'CPO 双龙头 中际旭创 -0.51%、新易盛 -1.59%'),
    ("人形机器人", "老师：前期强势股补跌未结束",
     f'<b>{BK["人形机器人"]["avg_pct"]:+.2f}%</b>，<b>0 涨 9 跌</b>；兆威机电 -6.27%、鸣志电器 -5.40%、长盈精密 -4.09%'),
    ("AI视频/传媒", "同上",
     f'<b>{BK["AI视频/传媒"]["avg_pct"]:+.2f}%</b>，<b>0 涨 7 跌</b>；华策影视 -5.41%、掌阅科技 -5.33%、捷成股份 -4.58%'),
]

# ---------- 标的表 ----------
ROWS = [
    ("药明康德", "大医药", "不操作 · 需向上突破 157.8 出三买；市场止跌后出日线有力度底分型才考虑",
     "157.8", f'最低 <b>{snap("药明康德")["low"]:.2f} 创短线新低</b>（破 11/17 低 142.20），'
     f'距 157.8 差 {157.8-snap("药明康德")["high"]:.2f} 元', "等"),
    ("中国船舶", "船舶", "不操作 · 上涨但本质仍是下跌中枢震荡，结构未止跌",
     "36.75", f'收 34.39 <b>+1.21%</b>（池内唯一红盘），最高 34.58，距 36.75 差 2.17 元', "等"),
    ("瑞芯微", "半导体", "不操作 · 短线已破位，等日线有力度底分型或重新形成共振结构",
     "220.7 / 208", f'收 195.01 <b>-4.85%</b>，<b>跌破 208 与 220.7</b>，最低 194.70，底分型未出', "等"),
    ("伊利股份", "大消费", "不操作 · 不建议追涨，持仓者观察是否形成顶背驰",
     "—", f'最高 32.59 <b>创 60 日新高</b>，收 32.40 平；顶背驰尚未成立（老师口径）', "不追"),
    ("海天瑞声", "机器人", "等回调到下沿附近找止跌机会 + 日线有力度底分型 + 小级别 2-3 日共振",
     "141", f'收 91.27 -2.23%，最低 90.00 <b>再破前低</b>（11/17 低 91.99），距 60 日低 76.54 还有 17%', "等"),
    ("兆易创新", "存储芯片", "不操作 · ①日线有力度底分型 ②收复 233，防演变成下跌中枢震荡",
     "233", f'最高 218.00，<b>差 {233-snap("兆易创新")["high"]:.2f} 元</b>；收 215.00 微红，未止跌', "等"),
    ("模塑科技", "机器人", "不操作 · 底分型没形成、短线破位，可不用关注",
     "14.95", f'最低 <b>{snap("模塑科技")["low"]:.2f} 创新低并破 14.95</b>，收 14.39 -3.42%', "等"),
    ("长盈精密", "机器人", "不操作 · 未止跌 + 短线破位；<b>老师已提出今晚剔除跟踪</b>",
     "—", f'收 23.19 <b>-4.09%</b>，最低 22.91 破 11/17 低 23.86，创 20 日新低', "等"),
]

DEVS = [
    ("老师：「半导体与 CPO 上午走势不是很好」",
     f'算力/CPO 篮子 <b>{BK["算力/CPO"]["avg_pct"]:+.2f}%</b>（沪电 +6.45%、工业富联 +3.93%、胜宏 +3.92%），'
     f'绿盘只有 CPO 双龙头（中际旭创 -0.51%、新易盛 -1.59%）',
     "方向对 · 口径偏窄"),
    ("老师：「上证结构属于清晰的弱势走势」",
     f'科创50 <span class="up">{kc["pct"]:+.2f}%</span> 逆势红、创业板 {cy["pct"]:+.2f}%；'
     f'但跌家数 {BR["down"]}（{BR["down"]/BR["n"]*100:.0f}%）、缩量 {amt_chg:.1f}%',
     "弱在权重与宽度"),
    ("老师：「高股息方向不建议追涨」",
     f'公路篮子 {BK["公路"]["avg_pct"]:+.2f}%（皖通高速 +4.11%）、家电 {BK["家电"]["avg_pct"]:+.2f}% 上午已冲高',
     "追涨风险正在兑现"),
    ("底分型 / 顶背驰 / 中枢延伸类定性",
     "本机不跑分钟级 K 线与 czsc，无法独立复算",
     "按老师口径引用"),
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
  <div class="meta"><a href="/" style="color:#2563eb;text-decoration:none">← 返回首页</a><span style="color:#9ca3af"> · </span>盘中版 · 数据截至 2026-11-18 {SNAP}（未收盘）</div>
  <p class="stance"><b>结论：前低附近窄幅震荡，弱势未改，3623 未收复 → 轻仓、少出手。</b>
  上午上证 <span class="down">{sh['pct']:+.2f}%</span> 收 {sh['close']:.2f}，区间 {sh['low']:.2f}–{sh['high']:.2f}（0.78%），低点未破 11/17 创的 60 日低 3565.59；
  <b>昨日高点 3623.12 差 26.91 点没满足</b> → 结构属清晰弱势。跌家数 {BR['down']}（82%）、成交缩量 {amt_chg:.1f}%。
  池内 8 只标的<b>全部无方法买点</b>。</p>
</div>

<div class="grid4">
  <div class="kpi"><div class="label">上证指数 · 3623 未破</div><div class="val down">{sh['pct']:+.2f}%</div><div class="sub">{sh['close']:.2f} · 低 {sh['low']:.2f} 未破 60 日低</div></div>
  <div class="kpi"><div class="label">科创50 / 创业板指</div><div class="val up">{kc['pct']:+.2f}% / <span class="down">{cy['pct']:+.2f}%</span></div><div class="sub">沪深300 {hs300['pct']:+.2f}% · 深成 {sz['pct']:+.2f}%</div></div>
  <div class="kpi"><div class="label">两市累计成交额（11:30）</div><div class="val vol">{amt_now:,.0f} 亿</div><div class="sub vol">同比 {amt_chg:+.2f}%（昨同刻 {amt_1130_prev:,.0f}）</div></div>
  <div class="kpi"><div class="label">涨 / 跌家数（{BR['snapshot'][-5:]}）</div><div class="val"><span class="up">{BR['up']}</span> / <span class="down">{BR['down']}</span></div><div class="sub">涨停 {POOL['zt']['tc']} · 跌停 {POOL['dt']['tc']} · 炸板 {POOL['zb']['tc']}</div></div>
</div>

<h2>一、指数：前低附近窄幅震荡，弱势定性成立</h2>
<p>老师两个判据逐条对上：① <b>「前低附近的窄幅震荡」</b> —— 上午区间 {sh['low']:.2f}–{sh['high']:.2f}，仅 27.7 点（0.78%），低点离 11/17 创的 60 日低 3565.59 只差 3.23 点（0.09%），全天没破前低；② <b>「昨天说向上运行就无法确认阶段低点，要先收复 3623 点且站稳，但走势没有满足」</b> —— 今日最高 {sh['high']:.2f}，<b>差 26.91 点没翻过去</b>，3750 远在 179.79 点之外。所以「结构属于清晰的弱势走势」「中期短期都没止跌」成立；向下要等的是<b>震荡后再选择方向 + 底背驰</b>，没出现之前就是耐心等。</p>
<p>结构上是<b>权重弱、成长分化</b>：科创50 <span class="up">{kc['pct']:+.2f}%</span> 逆势红（寒武纪 +3.23%），创业板 <span class="down">{cy['pct']:+.2f}%</span>、深成 {sz['pct']:+.2f}%、沪深300 {hs300['pct']:+.2f}%。但宽度比指数更差 —— 全 A {BR['n']} 只里跌 {BR['down']} 只（{BR['down']/BR['n']*100:.0f}%）、跌超 5% {BR['down_5']} 家；11:30 两市 {amt_1130:,.0f} 亿 vs 昨日同时点 {amt_1130_prev:,.0f} 亿（<span class="vol">{amt_chg:+.2f}%</span> 缩量）。<b>「活跃资金生态非常差」</b> = 涨停只有 {POOL['zt']['tc']} 家且散在 IT服务 5 / 通信服务 3 / 计算机设备 3，没有主线。</p>
<img class="chart" src="../charts/000001_SH_DY_{SUF}.png">
<img class="chart" src="../charts/399006_SZ_DY_{SUF}.png">

<h2>二、板块：高股息只有家电与公路站住，科技股分化</h2>
<table>
  <tr><th>方向（自建篮子）</th><th>老师口径</th><th>实测（均值 · 涨跌家数 · 个股）</th></tr>
  {''.join(f'<tr><td><b>{n}</b></td><td>{t}</td><td>{v}</td></tr>' for n, t, v in BKROWS)}
</table>
<p><b>三条要记的：</b>① <b>高股息内部分化看得准</b> —— 公路 {BK['公路']['avg_pct']:+.2f}%（5 涨 0 跌）、家电 {BK['家电']['avg_pct']:+.2f}%（5 涨 0 跌）走出来，饮料制造 {BK['饮料制造']['avg_pct']:+.2f}%（0 涨 5 跌）回调，银行 {BK['银行']['avg_pct']:+.2f}% 混平 —— <b>全面抱团确实没形成，只有家电、公路两条线站住</b>，这正是老师说的「不建议追涨、耐心找回调后的止跌机会」；② <b>前期强势股补跌没结束</b> —— AI视频/传媒 {BK['AI视频/传媒']['avg_pct']:+.2f}%（0 涨 7 跌）、人形机器人 {BK['人形机器人']['avg_pct']:+.2f}%（0 涨 9 跌），跌停池里影视院线 3 只、游戏 4 只；③ <b>半导体与 CPO 弱、国产算力有动作</b> —— 半导体篮子 {BK['半导体']['avg_pct']:+.2f}%（瑞芯微 -4.85%、北方华创 -1.11%），CPO 双龙头中际旭创 -0.51%、新易盛 -1.59% 绿盘；但英伟达业绩后沪电 +6.45%、工业富联 +3.93%、胜宏 +3.92% 确有动作 —— <b>动作集中在 PCB/服务器链，不是 CPO</b>，老师「科技股当下可操作空间不多」的结论成立。</p>

<h2>三、8 只标的：全部无方法买点</h2>
<table>
  <tr><th>标的 / 题材</th><th>现价</th><th>老师定性（老师口径）</th><th>关键位</th><th>实测印证（日线触达）</th><th>动作</th></tr>
  {''.join(f'<tr><td><b>{n}</b><br><span class="meta">{t}</span></td><td class="num">{px(n)}</td><td>{d}</td><td class="kn">{k}</td><td>{e}</td><td><span class="tag {"tag-bear" if a=="不追" else "tag-neutral"}">{a}</span></td></tr>' for n, t, d, k, e, a in ROWS)}
</table>
<img class="chart" src="../charts/603259_SH_DY_{SUF}.png">
<img class="chart" src="../charts/600150_SH_DY_{SUF}.png">
<img class="chart" src="../charts/603893_SH_DY_{SUF}.png">
<img class="chart" src="../charts/600887_SH_DY_{SUF}.png">
<img class="chart" src="../charts/688787_SH_DY_{SUF}.png">
<img class="chart" src="../charts/603986_SH_DY_{SUF}.png">
<img class="chart" src="../charts/000700_SZ_DY_{SUF}.png">
<img class="chart" src="../charts/300115_SZ_DY_{SUF}.png">

<h2>四、下午关注（可验证条件）</h2>
<div class="box box-a">
① <b>上证 3623.12</b>：今日最高 {sh['high']:.2f}，差 26.91 点 —— 站上并站稳才有「短线止跌」第一个确认；<b>跌破 3565.59</b> 则新低延续、底背驰更远。<br>
② <b>国产算力能否延续</b>：沪电 +6.45%、工业富联 +3.93%、胜宏 +3.92% 上午有动作 —— 看下午与明日是否放量延续，且 CPO 龙头（中际旭创、新易盛）是否止跌，否则只是反抽。<br>
③ <b>跌停家数能否收敛</b>：今日跌停 {POOL['dt']['tc']} 家（游戏 4、影视院线 3、一般零售 3）—— 收敛前不接任何旧热点。<br>
④ <b>高股息不追涨</b>：公路 {BK['公路']['avg_pct']:+.2f}%、家电 {BK['家电']['avg_pct']:+.2f}% 上午已冲高，等回调后的止跌结构（老师口径）。<br>
⑤ <b>池内 8 只今日无一触发买点</b>：兆易创新 233（今日最高 218.00，差 15.00）、模塑科技 14.95（已破，低 {snap('模塑科技')['low']:.2f}）、长盈精密破位（低 {snap('长盈精密')['low']:.2f}）。
</div>
<div class="box box-r">
<b>纪律（原文明写）：</b>① <b>轻仓应对、减少出手次数</b>，底背驰出现前耐心等；② <b>高股息方向不追涨</b>（电力、公路、银行、大消费都在其中，但要对比哪条能真正走强，全面抱团难成）；③ 池内 8 只<b>全部「无方法买点」= 没有</b>，不改写成「可试探」；④ 长盈精密老师已提出今晚收评剔除跟踪，本纪要按池内处理并标注状态变化。
</div>

<h2>五、偏差记录</h2>
<table>
  <tr><th>老师原文</th><th>实测</th><th>判定</th></tr>
  {''.join(f'<tr><td>{a}</td><td>{b}</td><td><span class="tag {"tag-neutral" if "偏窄" in c or "兑现" in c else "tag-none"}">{c}</span></td></tr>' for a, b, c in DEVS)}
</table>

<div class="foot">
  <p>来源：都业华《高级班》2026-11-18 午盘（高级班·午盘），执业编号 A0400626100004。<b>仅供参考，不作为买卖依据，据此操作风险自担。投资有风险，入市需谨慎！</b></p>
  <p><b>口径：</b>同花顺公开接口日线（140 根）+ {SNAP} 实时快照（最后一根 K 线未走完、成交量为盘中累计）；板块为自建篮子均值（成分逐一列出）；涨跌家数取新浪全 A {BR['n']} 只 {BR['snapshot'][-5:]} 快照；涨停/跌停用东财池；成交额同比取腾讯 5 日分时「同时点 11:30」累计。缠论定性按老师口径引用，不声称我方复算过 15 分钟结构。</p>
</div>

</div>
</body>
</html>
"""

out = REPO / "html/duyiehua-20261118-noon.html"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from fix_mobile_tables import patch_html
out.write_text(patch_html(html), encoding="utf-8")
print("saved", out, len(html))
