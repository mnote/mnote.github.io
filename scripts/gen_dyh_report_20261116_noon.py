"""都业华 2026-11-16 午评（高级班·午盘）纪要 HTML（白底 · 盘中版）

⛔ 用户 2026-11-11 禁令：只用日线 + 实时快照，不调用分钟级 K 线、不调用 czsc。
📏 篇幅硬约束：正文 ≤2000 中文字、表格 ≤4 张；K 线图保留、不计字数。

输出：html/duyiehua-20261116-noon.html
"""
import json
import sys
from pathlib import Path

REPO = Path("/Users/maoling/workspace/mnote.github.io")
RPT = REPO / "reports/duyiehua-20261116"
D = json.loads((RPT / "data_20261116.json").read_text(encoding="utf-8"))
BR = json.loads((RPT / "breadth_20261116.json").read_text(encoding="utf-8"))
IX, ST, BK = D["index"], D["stocks"], D["baskets"]
POOL = D["pools"]
SUF = "20261116N"

TITLE = "DYH 午评 - 2026-11-16（周一 探底回升仍弱，红利独强）"

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
    return f'<span class="{cls(s["pct"])}">{s["price"]:.2f} ({s["pct"]:+.2f}%)</span>'


sh = IX["上证指数_snap"]
cy = IX["创业板指_snap"]
kc = IX["科创50_snap"]
hs300 = IX["沪深300_snap"]
amt_now = D["amount"]["total_yi"]
amt_prev_am = 9793.8          # 11/13 同时点（沪 4490.0 + 深 5303.8）
amt_chg = (amt_now / amt_prev_am - 1) * 100

# ---------- 板块表 ----------
BKROWS = [
    ("银行", "红利防御", f'{BK["银行"]["avg_pct"]:+.2f}%，{BK["银行"]["up"]}/{BK["银行"]["down"]} 全红；'
     f'农行 +1.90%、建行 +1.49%、工行 +1.47%'),
    ("电力/高股息", "红利防御", f'{BK["电力/高股息"]["avg_pct"]:+.2f}%，5/5 全红；川投 +2.19%、长电 +1.24%'),
    ("煤炭/石油", "红利防御", f'{BK["煤炭/石油"]["avg_pct"]:+.2f}%，4 涨 1 跌；神华 +1.22%、石化 +0.87%'),
    ("AI视频/传媒", "老师：上午略微强些",
     f'<b>{BK["AI视频/传媒"]["avg_pct"]:+.2f}%，仅 {BK["AI视频/传媒"]["up"]}/{BK["AI视频/传媒"]["down"]}</b>；'
     f'掌阅 +1.45%、华策 -0.59%，中文在线 -3.35%、上海电影 -5.61%'),
    ("半导体", "老师：上午下跌比较厉害",
     f'{BK["半导体"]["avg_pct"]:+.2f}%，{BK["半导体"]["up"]}/{BK["半导体"]["down"]}；'
     f'兆易 -5.58%、寒武纪 -4.98%、海光 -4.74%，仅北方华创 +1.23%'),
    ("算力/CPO", "老师：前期强势股补跌",
     f'<b>{BK["算力/CPO"]["avg_pct"]:+.2f}%，0/{BK["算力/CPO"]["down"]}</b>；'
     f'中际旭创 -7.70%、新易盛 -6.97%、工业富联 -6.71%、沪电 -5.64%'),
    ("人形机器人", "老师：三个机器人股都没止跌",
     f'{BK["人形机器人"]["avg_pct"]:+.2f}%，{BK["人形机器人"]["up"]}/{BK["人形机器人"]["down"]}；'
     f'模塑 -5.42%、长盈 -3.74%，仅拓普 +0.16%'),
]

# ---------- 标的表 ----------
def snap(n):
    return ST[n]["snap"]


ROWS = [
    ("药明康德", "大医药", "无买点 · 等突破前高后回抽确认三买",
     "157.8", f'最高 {snap("药明康德")["high"]:.2f}，差 {157.8-snap("药明康德")["high"]:.2f}', "等"),
    ("中国船舶", "防御", "无买点 · 走势没有止跌",
     "11/13 低 33.80", f'最低 {snap("中国船舶")["low"]:.2f}，破前低 0.25 元', "等"),
    ("瑞芯微", "端侧AI", "无买点 · 等回调到 208 或跌穿下沿拉回",
     "208", f'最低 {snap("瑞芯微")["low"]:.2f}，距 208 差 {snap("瑞芯微")["low"]-208:.2f} 元，两条件均未触发', "等"),
    ("伊利股份", "大消费", "无买点 · 上周五向上延续，不建议追涨",
     "30.46", f'最高 {snap("伊利股份")["high"]:.2f} 续创 60 日新高，位置偏高', "不追"),
    ("中文在线", "AI视频", "无买点 · 等突破 30.38 出 15 分钟底分型三买",
     "30.38", f'最高 {snap("中文在线")["high"]:.2f}，差 {30.38-snap("中文在线")["high"]:.2f}', "等"),
    ("海天瑞声", "机器人", "无买点 · 有下影线，等日线有力度底分型",
     "—", f'最低 {snap("海天瑞声")["low"]:.2f} 破前低 6.63 元，收 {snap("海天瑞声")["price"]:.2f}', "等"),
    ("奥普特", "机器视觉", "无买点 · 有下影线，等日线有力度底分型",
     "140", f'最低 {snap("奥普特")["low"]:.2f}，距下沿 140 差 1.00 元', "等"),
    ("柯力传感", "六维传感器", "无买点 · 有下影线，等日线有力度底分型",
     "53", f'最低 {snap("柯力传感")["low"]:.2f}，<b>已跌破 53 支撑 1.90 元</b>', "等"),
    ("兆易创新", "存储芯片", "无买点 · 创出新低，耐心等底背驰",
     "237.28", f'最低 {snap("兆易创新")["low"]:.2f}，<b>深跌破 7.78 元</b>（老师：破得深一点更好）', "等"),
    ("模塑科技", "人形机器人", "无买点 · 创短期新低，等 14.95 出止跌信号",
     "14.95", f'最低 {snap("模塑科技")["low"]:.2f}，距支撑仅 {snap("模塑科技")["low"]-14.95:.2f} 元', "等"),
    ("长盈精密", "人形机器人", "无买点 · 走势没有止跌",
     "32.08", f'最低 {snap("长盈精密")["low"]:.2f}，距三买门槛差 3.82 元', "等"),
]

DEVS = [
    ("老师：传媒/AI视频「看起来略微强些」",
     f'板块均值 {BK["AI视频/传媒"]["avg_pct"]:+.2f}%（{BK["AI视频/传媒"]["up"]}涨/{BK["AI视频/传媒"]["down"]}跌），'
     f'中文在线 -3.35%、光线 -4.20%、上海电影 -5.61%',
     "相对强于算力，绝对仍跌"),
    ("老师：算力硬件「出现补跌动作」",
     f'算力/CPO 均值 {BK["算力/CPO"]["avg_pct"]:+.2f}%，0/{BK["算力/CPO"]["down"]}，'
     f'中际旭创 -7.70%、工业富联 -6.71%',
     "<b>完全成立</b>"),
    ("老师：半导体与 CPO「下跌比较厉害」",
     f'半导体 {BK["半导体"]["avg_pct"]:+.2f}%、CPO {BK["算力/CPO"]["avg_pct"]:+.2f}%',
     "<b>完全成立</b>"),
    ("老师：涨幅榜靠前「除传媒外基本都带防御属性」",
     "新浪行业涨幅前 12：开发区 +3.17%、公路桥梁 +1.67%、家电 +1.57%、物资外贸 +0.94%、"
     "金融 +0.66%、酿酒 +0.41%、食品 +0.38%、煤炭 +0.32%",
     "<b>成立</b>（全防御）"),
    ("老师：三个机器人股「都没出止跌，虽然有下影线」",
     "海天瑞声低 105.61 收 109.78；奥普特低 141.00 收 146.42；柯力传感低 51.10 收 53.40",
     "<b>成立</b>（三只都有下影线）"),
]

# ---------- 本周两个观察点：洗牌存活率（11/11 涨停池 85 只 → 11/16 11:30） ----------
POOL_F = json.loads((RPT / "pool1111_full.json").read_text(encoding="utf-8"))
ROBO = {"汽车零部", "通用设备", "专用设备", "自动化设", "机械基件", "工业机械",
        "仪器仪表", "电网设备", "工程机械", "专用机械"}
MEDIA = {"影视院线", "游戏Ⅱ", "广告营销", "出版", "文化传媒", "数字媒体", "互联网服务", "传媒"}


def alive_stat(hybk_filter):
    rows = [(c, POOL_F["hybk"].get(c, ""), POOL_F["snap"][c]) for c in POOL_F["snap"]]
    rows = [(c, h, s) for c, h, s in rows if hybk_filter(h)]
    if not rows:
        return None
    up = [r for r in rows if r[2]["pct"] > 0]
    dn5 = [r for r in rows if r[2]["pct"] <= -5]
    return {
        "n": len(rows), "up": len(up), "rate": round(len(up) / len(rows) * 100),
        "dn5": len(dn5),
        "top": sorted(rows, key=lambda x: -x[2]["pct"])[:3],
        "bot": sorted(rows, key=lambda x: x[2]["pct"])[:2],
    }


ST_ALL = alive_stat(lambda h: True)
ST_ROBO = alive_stat(lambda h: h in ROBO)
ST_MEDIA = alive_stat(lambda h: h in MEDIA)

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
  <div class="meta"><a href="/" style="color:#2563eb;text-decoration:none">← 返回首页</a><span style="color:#9ca3af"> · </span>盘中版 · 数据截至 2026-11-16 11:30（未收盘）</div>
  <p class="stance"><b>结论：探底回升但仍是弱势震荡，仓位轻、频率降。</b>上证低开 3611.54 探至 <b>3593.45</b> 后回升至 {sh['price']:.2f}（{sh['pct']:+.2f}%），<b>最低已破 11/13 低 3623.84</b>、3750 仍差 3.5% 未触；创业板 <span class="down">{cy['pct']:+.2f}%</span>、科创50 <span class="down">{kc['pct']:+.2f}%</span>。两市上午成交 <span class="vol">{amt_now:,.0f} 亿</span>（同时点同比 <span class="down">{amt_chg:+.1f}%</span>），<span class="down">{BR['down']}</span> 家下跌、跌停 {POOL['dt']['tc']} 家。<b>热点两极：红利防御独强（银行 +1.20%、电力 +1.26%），算力硬件补跌（-6.71%）。11 只标的无一出现方法买点。</b></p>
</div>

<div class="grid4">
  <div class="kpi"><div class="label">上证指数 · 3750 未触</div><div class="val down">{sh['pct']:+.2f}%</div><div class="sub">{sh['price']:.2f} · 低 {sh['low']:.2f} 破前低</div></div>
  <div class="kpi"><div class="label">创业板指 / 科创50</div><div class="val down">{cy['pct']:+.2f}% / {kc['pct']:+.2f}%</div><div class="sub">沪深300 {hs300['pct']:+.2f}% · 成长端最弱</div></div>
  <div class="kpi"><div class="label">两市上午成交额 · 同时点同比</div><div class="val vol">{amt_now:,.0f} 亿</div><div class="sub down">{amt_chg:+.1f}%（昨同刻 {amt_prev_am:,.0f}）</div></div>
  <div class="kpi"><div class="label">涨 / 跌家数（11:30）</div><div class="val"><span class="up">{BR['up']}</span> / <span class="down">{BR['down']}</span></div><div class="sub">跌超 5% {BR['down_5']} 家 · 跌超 9% {BR['down_9']} 家</div></div>
</div>

<h2>一、指数：低开探底回升，但创新低</h2>
<p>老师口径「低开后探底回升、走势非常弱、下跌中枢震荡、临近左边低点」—— <b>日内形态逐条对上</b>：开 3611.54 低于昨收 3634.35，探至 3593.45 后拉回 3620.00。但<b>结构没修</b>：最低 3593.45 已破 11/13 低 3623.84，距 60 日低 3574.27 只剩 0.5%；向上 3750 差 126.88 点（3.50%）根本没摸到。下午若不能站回 3624 以上，探底回升只是反抽。</p>
<p>量能同步走弱：<b>上午 9005 亿，比 11/13 同时点 9794 亿缩 {abs(amt_chg):.1f}%</b>，全天看只有昨日全天的 54.4%；跌家数 {BR['down']} 家占 {BR['down']/BR['n']*100:.0f}%，跌超 5% {BR['down_5']} 家、跌超 9% {BR['down_9']} 家，跌停 {POOL['dt']['tc']} 家。「市场很弱」不是定性，是数字。</p>
<img class="chart" src="../charts/000001_SH_DY_{SUF}.png">
<img class="chart" src="../charts/399006_SZ_DY_{SUF}.png">

<h2>二、板块：红利与算力彻底分家</h2>
<table>
  <tr><th>方向（自建篮子）</th><th>老师口径</th><th>实测（均值 · 涨跌家数 · 个股）</th></tr>
  {''.join(f'<tr><td><b>{n}</b></td><td>{t}</td><td>{v}</td></tr>' for n, t, v in BKROWS)}
</table>
<p><b>三条要记的：</b>① 涨幅榜前列<b>全是防御</b>（开发区、公路桥梁、家电、金融、酿酒、食品、煤炭），银行 +1.20%、电力 +1.26% 全红 —— 老师「红利高股息方向走得好、与市场弱相关」成立；② <b>算力/CPO -6.71%、0 涨 5 跌</b>，前期强势股全部补跌，中际旭创 -7.70%、工业富联 -6.71%，老师定性精准；③ <b>传媒只是「相对强」不是「绝对强」</b>：均值 -2.28%，只是比算力少跌得多——老师自己那句「盘中走强不一定具有持续性」正好提醒。老师说传媒「调整的低点回到前面分析不该跌破的位置」：<b>中文在线今日最低 25.56，与 11/09 低点 25.65 几乎重合（差 0.09 元）</b>，这一句可核验。</p>

<h2>三、11 只标的：无一出现方法买点</h2>
<table>
  <tr><th>标的 / 题材</th><th>11:30</th><th>老师定性（老师口径）</th><th>关键位</th><th>实测印证（日线触达）</th><th>动作</th></tr>
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

<h2>四、老师点名的「本周两个观察点」—— 洗牌存活率</h2>
<table>
  <tr><th>观察点</th><th>实测口径</th><th>存活情况（11/11 涨停池 → 11/16 11:30）</th></tr>
  <tr><td><b>① 防御品种里哪些持续性好</b></td><td>银行 / 电力 / 煤炭 15 只篮子</td>
      <td>银行 +1.20%（5/0）、电力 +1.26%（5/0）、煤炭石油 +0.51%（4/1）——
      <b>15 只里 14 只红盘，持续性目前最好</b>；但老师提醒「一旦止跌，防御会面临回调」</td></tr>
  <tr><td><b>② 上周四（11/11）强势股重新洗牌，谁能存活</b></td><td>11/11 涨停池 {ST_ALL['n']} 只</td>
      <td>红盘仅 <b>{ST_ALL['up']}/{ST_ALL['n']}（{ST_ALL['rate']}%）</b>，跌超 5% {ST_ALL['dn5']} 只；
      <b>机器人链 {ST_ROBO['up']}/{ST_ROBO['n']}（{ST_ROBO['rate']}%）</b> vs
      <b>传媒链 {ST_MEDIA['up']}/{ST_MEDIA['n']}（{ST_MEDIA['rate']}%）</b> —— 机器人几乎全灭、传媒小半存活</td></tr>
</table>
<p><b>存活名单（可当观察池，不是买点）：</b>传媒链留存的 {ST_MEDIA['top'][0][2]['name']} {ST_MEDIA['top'][0][2]['pct']:+.2f}%、
{ST_MEDIA['top'][1][2]['name']} {ST_MEDIA['top'][1][2]['pct']:+.2f}%、{ST_MEDIA['top'][2][2]['name']} {ST_MEDIA['top'][2][2]['pct']:+.2f}%
全在游戏/出版；机器人链只剩 {ST_ROBO['top'][0][2]['name']} {ST_ROBO['top'][0][2]['pct']:+.2f}%、
{ST_ROBO['top'][1][2]['name']} {ST_ROBO['top'][1][2]['pct']:+.2f}%。
<b>结论：老师要的两个答案，数字指向同一件事 —— 防御留住、机器人没留住，方向仍没选出来，所以只能轻仓、降低频率。</b></p>

<h2>五、下午盯什么</h2>
<div class="box box-g">
① 上证 <b>3593.45 今日低点是否被二次跌破</b>；向上站回 3624（今日高点）之上才算反抽有效，3750 是远门槛。<br>
② <b>兆易创新 229.50 是不是真底</b> —— 老师要「破得深一点」，深跌破 7.78 元已到位，但没出底背驰前不动。<br>
③ <b>模塑科技 14.95</b>：今日最低 15.12，只差 0.17 元；触到且出止跌信号才谈得上方法买点。<br>
④ <b>瑞芯微 208</b>：今日最低 210.44，差 2.44 元，两条件（回调到 208 / 跌穿下沿拉回）都没满足。<br>
⑤ <b>传媒能否真正走强</b>：老师说「盘中走强不一定有持续性」，盯中文在线（今日低 25.56 恰回 11/09 低 25.65）与传媒链红盘率能否连续维持。
</div>
<div class="box box-r">
<b>两条纪律（原文明写，别自行加戏）：</b>① <b>已经自行操作参与的同学，先把适合自己的止损点定下来</b> —— 老师对所有票都没给买点，仓位轻是唯一前提；
② 防御方向操作节奏难把握，<b>不要因为今天银行电力红盘就追</b>；市场一旦止跌，防御反而会面临回调。
</div>

<h2>六、偏差记录</h2>
<table>
  <tr><th>老师原文</th><th>实测</th><th>判定</th></tr>
  {''.join(f'<tr><td>{a}</td><td>{b}</td><td><span class="tag {"tag-bull" if "成立" in c and "相对" not in c else "tag-neutral"}">{c}</span></td></tr>' for a, b, c in DEVS)}
</table>

<div class="foot">
  <p>来源：都业华《高级班》2026-11-16 午盘（高级班·午盘），执业编号 A0400626100004。<b>仅供参考，不作为买卖依据，据此操作风险自担。投资有风险，入市需谨慎！</b></p>
  <p><b>口径：</b>同花顺公开接口日线（140 根，前复权）+ 11:30 实时快照（最后一根 K 线未走完、成交量为盘中累计）；板块为自建篮子均值（成分逐一列出）；涨跌家数取新浪全 A 5578 只 11:30 快照；涨停/跌停用东财池（不含 ST／北交所）；成交额同比取腾讯 5 日分时「同时点 11:30」累计，两市 = 沪市全市场 + 深市全市场。缠论定性按老师口径引用，不声称我方复算过 15 分钟结构。</p>
</div>

</div>
</body>
</html>
"""

out = REPO / "html/duyiehua-20261116-noon.html"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from fix_mobile_tables import patch_html
out.write_text(patch_html(html), encoding="utf-8")
print("saved", out, len(html))
