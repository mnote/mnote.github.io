"""wu2198 投资日报 2026-11-17（周二 · 收盘后增补版）— 线上产物生成器

用法： python3 scripts/gen_wu2198_report_20261117_close.py
产物： html/wu2198-20261117.html（覆盖 15:25 收盘版，补 15:08 后 4 条新帖）
增量：09:54 / 10:28 / 21:46 / 22:02 四条新帖
      10:28「CPO 龙头 1416.88→385，跌 1031.88 元，-72.82%」= 精确核验
      22:02「我既然能够在 5 月份高位撤离，这次重新杀进来」= 首次明确建仓表态
行情口径：Tushare Pro 日线（pro.daily / pro.index_daily + adj_factor 前复权）
篇幅： 正文 ≤ 2000 中文字 / 表格 ≤ 4 张
"""
import json
import sys
from pathlib import Path

ROOT = Path("/Users/maoling/workspace/mnote.github.io")
CH = ROOT / "charts"

KPI = json.loads((CH / "_kpic_20261117c.json").read_text(encoding="utf-8"))
SEC = json.loads((CH / "_pools_20261117.json").read_text(encoding="utf-8"))
CLOSE = json.loads((CH / "_close_20261117.json").read_text(encoding="utf-8"))
TS = json.loads((CH / "_ts_20261117.json").read_text(encoding="utf-8"))
SER = CLOSE["series"]
ALL = CLOSE["all"]
EM = CLOSE["em_pools"]

SH, CY = KPI["000001.SH"], KPI["399006.SZ"]
ZH, MT, HX = KPI["002179.SZ"], KPI["600519.SH"], KPI["688256.SH"]
YB = KPI["600036.SH"]
CPO = KPI["300308.SZ"]

P = SEC
p_wine, p_bank, p_mil = P["白酒/大消费"], P["银行/红利"], P["军工"]
p_calc, p_st, p_cpo, p_rob = (P["算力租赁/IDC"], P["存储/半导体/GPU"],
                               P["CPO/光通信"], P["人形机器人/端侧"])


def mem(pool, n_top=2, n_bot=1):
    ms = pool["members"]
    top, bot = ms[:n_top], (ms[-n_bot:] if n_bot else [])
    fmt = lambda m: f'<b class="{"up" if m["pct"] >= 0 else "down"}">{m["pct"]:+.2f}%</b>'
    a = "、".join(f'{m["name"]} {fmt(m)}' for m in top)
    if bot:
        a += " / " + "、".join(f'{m["name"]} {fmt(m)}' for m in bot)
    return a


def amt_on(code, date):
    for r in SER.get(code, []):
        if r["Date"] == date:
            return r["Amount"] / 1e8
    return None


AMT_17 = amt_on("000001.SH", "2026-11-17") + amt_on("399001.SZ", "2026-11-17")
AMT_16 = amt_on("000001.SH", "2026-11-16") + amt_on("399001.SZ", "2026-11-16")
AMT_DIFF = AMT_17 - AMT_16
AMT_PCT = AMT_DIFF / AMT_16 * 100

SH_GAP = 3706 - SH["close"]
CY_GAP = 2626 - CY["close"]
SH_LO60 = 3565.59          # 11/17 最低 = 60 日新低
CY_LO60 = 2263.74          # 11/17 最低 = 她的 2263 点 = 60 日新低
CPO_PEAK = 1416.88         # 她 10:28 给的 CPO 龙头前高
CPO_NOW = 385.00           # 她 10:28 给的现价
CPO_DROP = 1031.88         # 1416.88 - 385
CPO_PCT = CPO_DROP / CPO_PEAK * 100   # 72.82%

TITLE = "wu2198 - 2026-11-17（周二 2263点触达，重新杀进来）"

HTML = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{TITLE}</title>
<style>
  :root {{
    --bg: #ffffff; --panel: #f8f9fb; --panel-2: #f1f3f6;
    --border: #e5e7eb; --border-strong: #d1d5db;
    --text: #1f2937; --muted: #6b7280;
    --bull: #16a34a; --bull-bg: #dcfce7;--up:#e63946;--down:#2a9d8f;
    --bear: #dc2626; --bear-bg: #fee2e2;
    --neutral: #d97706; --neutral-bg: #fef3c7;
    --none: #6b7280; --none-bg: #f3f4f6;
    --accent: #2563eb; --accent-bg: #dbeafe;
    --key: #7c3aed;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", "Segoe UI", sans-serif;
    background: var(--bg); color: var(--text); line-height: 1.7; font-size: 15px;
  }}
  .wrap {{ max-width: 1180px; margin: 0 auto; padding: 32px 24px 80px; }}
  h1, h2, h3 {{ font-weight: 600; line-height: 1.3; }}
  h1 {{ font-size: 28px; margin: 0 0 8px; }}
  h2 {{ font-size: 20px; margin: 36px 0 14px; padding-bottom: 8px; border-bottom: 2px solid var(--border); }}
  h3 {{ font-size: 17px; margin: 24px 0 10px; }}
  p {{ margin: 8px 0; }}
  a {{ color: var(--accent); text-decoration: none; }}
  .meta {{ color: var(--muted); font-size: 13px; }}
  .meta span {{ margin-right: 14px; }}

  .hero {{ background: linear-gradient(135deg, #eff6ff 0%, #f7fbff 100%); border: 1px solid #93c5fd; border-radius: 12px; padding: 24px 28px; margin-bottom: 28px; }}
  .hero h1 {{ color: #1e3a8a; }}
  .hero .stance {{ font-size: 16px; margin: 8px 0 0; }}

  .panel {{ background: var(--panel); border: 1px solid var(--border); border-radius: 10px; padding: 18px 22px; margin: 16px 0; }}
  .grid-4 {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }}
  @media (max-width: 900px) {{ .grid-4 {{ grid-template-columns: 1fr 1fr; }} }}
  @media (max-width: 620px) {{ .grid-4 {{ grid-template-columns: 1fr; }} }}

  .kpi {{ background: #fff; border: 1px solid var(--border); border-radius: 8px; padding: 12px 14px; text-align: center; }}
  .kpi .label {{ font-size: 12px; color: var(--muted); letter-spacing: 0.5px; }}
  .kpi .val {{ font-size: 20px; font-weight: 600; margin: 4px 0; }}
  .kpi .sub {{ font-size: 12px; color: var(--muted); }}

  table {{ width: 100%; border-collapse: collapse; margin: 12px 0; font-size: 14px; }}
  th, td {{ padding: 8px 10px; text-align: left; border-bottom: 1px solid var(--border); vertical-align: top; }}
  th {{ background: var(--panel-2); font-weight: 600; color: var(--muted); font-size: 12px; }}
  tr:hover {{ background: var(--panel); }}
  td.text {{ max-width: 420px; }}
  td.score {{ font-variant-numeric: tabular-nums; text-align: right; }}

  .tag {{ display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: 11px; font-weight: 500; margin: 0 2px; }}
  .tag-bull {{ background: var(--bull-bg); color: var(--bull); }}
  .tag-bear {{ background: var(--bear-bg); color: var(--bear); }}
  .tag-neutral {{ background: var(--neutral-bg); color: var(--neutral); }}
  .tag-accent {{ background: var(--accent-bg); color: var(--accent); }}

  .chart {{ width: 100%; height: auto; display: block; margin: 12px 0; border: 1px solid var(--border); border-radius: 6px; background: #fff; }}
  .chart-caption {{ font-size: 12px; color: var(--muted); margin: -4px 0 16px; }}

  .quote {{ background: var(--panel-2); border-radius: 8px; padding: 10px 14px; margin: 10px 0; font-size: 14px; border-left: 3px solid var(--border-strong); }}
  .risk {{ background: var(--bear-bg); border-radius: 8px; padding: 10px 14px; margin: 10px 0; font-size: 14px; }}
  .action {{ background: var(--bull-bg); border-radius: 8px; padding: 10px 14px; margin: 10px 0; font-size: 14px; }}
  .verify {{ background: var(--accent-bg); border-radius: 8px; padding: 10px 14px; margin: 10px 0; font-size: 14px; }}
  .up {{ color: var(--up); font-weight: 600; }}
  .down {{ color: var(--down); font-weight: 600; }}
  .key-num {{ color: var(--key); font-weight: 700; font-variant-numeric: tabular-nums; }}
  .foot {{ margin-top: 48px; padding-top: 20px; border-top: 1px solid var(--border); font-size: 12px; color: var(--muted); }}
  ul.tight {{ margin: 8px 0; padding-left: 22px; }}
  ul.tight li {{ margin: 4px 0; }}
  .vol{{color:var(--neutral);font-weight:600}}
</style>
<link rel="stylesheet" href="../assets/css/report-table.css">
</head>
<body>
<div class="wrap">

<div class="hero">
  <h1>📈 {TITLE}</h1>
  <div class="meta">
    <span><a href="/">← 返回首页</a></span>
    <span>🕘 截稿 2026-11-17 22:30（<b>收盘后增补版</b>）</span>
    <span>📡 weibo skill（四轮补采，<b>26 条</b>，06:07–22:02）</span>
    <span>💹 Tushare Pro 日线（前复权，11/17 收盘）</span>
  </div>
  <p class="stance">
    <b>🟢🟢 22:02「我既然能够在 5 月份高位撤离，这次重新杀进来，肯定会信心满满……」</b>
    —— 首次明确说<b>已重新建仓</b>，不是「等」；但<b>没给标的、点位、仓位</b>。
    14:56 的「本周 2263 点」已被创业板最低 <b>{CY_LO60:.2f}</b> 分毫不差触达，10:28 的「CPO 龙头 -72.82%」也分毫不差。
    <b>位置到位、她已动手，盘面还没转</b>（13:38「未见可扭转局面的力量」）——
    <b>只做白酒、方向等回踩的科技龙头、军工只做池内领涨</b>。
  </p>
</div>

<div class="grid-4" style="margin-bottom:8px">
  <div class="kpi"><div class="label">上证指数</div><div class="val">{SH['close']:.2f}</div>
    <div class="sub"><span class="down">{SH['pct']:+.2f}%</span> · 最低 {SH_LO60:.2f}（<b>60 日新低</b>）</div></div>
  <div class="kpi"><div class="label">创业板指</div><div class="val">{CY['close']:.2f}</div>
    <div class="sub"><span class="down">{CY['pct']:+.2f}%</span> · 最低 <b>{CY_LO60:.2f}</b>（她的 2263 点）</div></div>
  <div class="kpi"><div class="label">沪深成交额</div><div class="val">{AMT_17:,.0f} 亿</div>
    <div class="sub"><span class="vol">缩量 {abs(AMT_DIFF):,.0f} 亿（{AMT_PCT:+.1f}%）</span></div></div>
  <div class="kpi"><div class="label">涨跌家数</div><div class="val">{ALL['up']} / {ALL['down']}</div>
    <div class="sub">涨停 {ALL['limit_up']}（昨 37）· <span class="down">跌停 {ALL['limit_down']}（昨 174）</span></div></div>
</div>

<h2>一、博主说了什么（10 条）</h2>
<table>
<thead><tr><th>时间</th><th>信号</th><th>原文</th><th>判读 / 日线实测</th></tr></thead>
<tbody>
<tr><td><b>06:07</b></td><td>⚪ 外盘</td><td class="text">昨晚美股下跌：道指跌739点、纳指跌626点、标普跌145点</td>
  <td class="text"><b>三个数字分毫不差</b>：11/16 实测 −739.38 / −626.51 / −145.08。</td></tr>
<tr><td><b>09:39</b></td><td>🟢 板块点名</td><td class="text">GPU，半导体等目前局部走红！</td>
  <td class="text"><b>「局部」成立、「等」不成立</b>：存储池 <b class="down">{p_st['avg_pct']:+.2f}%</b>（1 涨 7 跌），寒武纪 {HX['pct']:+.2f}% 唯一红。</td></tr>
<tr><td><b>10:07</b></td><td>🟢🟢 位置定性</td><td class="text">以前给大家分析过 C 不一定是机会，但是 C5 绝对是机会。</td>
  <td class="text"><b>把「等」具体化成 C5</b>。11:14 重申「有技术的 C3 布局，稳健的 C5 完成之后干」，比 11/13 更明确。</td></tr>
<tr><td><b>10:28</b></td><td>🟢🟢 自我验证</td><td class="text">CPO 龙头这波从 1416.88 到今天的 385 元，跌了 1031.88 元，幅度达 72.82%；疯狂的时候像赌博！</td>
  <td class="text"><b>分毫不差，标的 = 新易盛 300308</b>：前复权峰值 {CPO_PEAK:.2f}（6/22），今日盘中最低 {CPO['low']:.2f}（发帖时价约 385），(1416.88−385)/1416.88 = <b>{CPO_PCT:.2f}%</b>。</td></tr>
<tr><td><b>10:31</b></td><td>🟢🟢 立场表态</td><td class="text">现在的位置，没有什么思考的余地。要么继续被干，要么干！</td>
  <td class="text"><b>从观望切到主动</b>。当日沪指、创业板<b>双创 60 日新低</b> → 她在最低位喊「干」。</td></tr>
<tr><td><b>10:47</b></td><td>🟢 方向</td><td class="text">科技类股杀估值去杠杆，清洗干净之后，高成长+行业向好的科技股会走出局部行情。</td>
  <td class="text">把 11/16 科技崩盘定性为<b>杀估值</b>而非逻辑破坏。但算力池 {p_calc['avg_pct']:+.2f}%、存储池 {p_st['avg_pct']:+.2f}% → <b>清洗尚未结束</b>。</td></tr>
<tr><td><b>13:38</b></td><td>🟡 收盘前定性</td><td class="text">市场上抵抗力量是有的，但还未见出现可扭转局面的力量。</td>
  <td class="text"><b>当日最准的一句</b>：涨 {ALL['up']} / 跌 {ALL['down']}，<b>尾盘跌停 40→{ALL['limit_down']} 家</b>，创业板收盘仍低于 11/16 新低 → <b>有抵抗、无反转</b>。</td></tr>
<tr><td><b>14:54</b></td><td>🟡 盘面反应</td><td class="text">下砸拉起，好事！</td>
  <td class="text">尾盘从低位回拉，创业板自 {CY_LO60:.2f} 拉回 <b>{CY['close']-CY_LO60:.2f} 点</b>，但<b>收盘仍跌 {CY['pct']:+.2f}%</b>。</td></tr>
<tr><td><b>14:56</b></td><td>🟢🟢 关键位</td><td class="text">本周 2263 点可以了，接下来等吃肉了！</td>
  <td class="text"><b>本期最硬的核验</b>：创业板最低 <b>{CY_LO60:.2f}</b>，<b>与 2263 点分毫不差</b>；她第一次在 C 杀期间给出<b>可执行点位</b>。</td></tr>
<tr><td><b>22:02</b><br><span class="tag tag-bull">新增</span></td><td>🟢🟢 建仓表态</td><td class="text">我既然能够在 5 月份高位撤离，这次重新杀进来，肯定会信心满满……</td>
  <td class="text"><b>首次明确「已重新建仓」</b>，与 10:31、14:56 同一条链；但<b>只有表态，没有标的/点位/仓位</b> → <b>只拿方向，不拿买点</b>。21:46 小米那条无信号。</td></tr>
</tbody>
</table>

<h2>二、大盘关键点位</h2>
<p class="meta" style="margin-bottom:6px">K 线<b>红涨绿跌</b>；关键位在图<b>左侧虚线</b>。数据源 <b>Tushare Pro 日线</b>（前复权），11/17 <b>完整收盘 K 线</b>。</p>

<h3>上证指数 · {SH['close']:.2f}（{SH['pct']:+.2f}%）</h3>
<img class="chart" src="../charts/000001_SH_20261117.png" alt="上证指数 2026-11-17 K线">
<p class="chart-caption">开 {SH['open']:.2f} / 高 {SH['high']:.2f} / 低 <b>{SH['low']:.2f}</b> / 收 {SH['close']:.2f}。
<b>最低 {SH_LO60:.2f} = 新 60 日低</b>（前低 3574.27 已破）；<b>3706 差 {SH_GAP:.2f} 点（{SH_GAP/3706*100:.2f}%）</b>，MA20 {SH['ma20']:.2f} 失守。</p>

<h3>创业板指 · {CY['close']:.2f}（{CY['pct']:+.2f}%）</h3>
<img class="chart" src="../charts/399006_SZ_20261117.png" alt="创业板指 2026-11-17 K线">
<p class="chart-caption">开 {CY['open']:.2f} / 高 {CY['high']:.2f} / 低 <b>{CY['low']:.2f}</b> / 收 {CY['close']:.2f}。
<b>最低 {CY_LO60:.2f} = 她的 2263 点 = 新 60 日低</b>；收盘较日低拉回 {CY['close']-CY['low']:.2f} 点，仍低于 11/16 新低 2308.90；<b>2626 差 {CY_GAP:.2f} 点（{CY_GAP/2626*100:.2f}%）</b>。</p>

<div class="risk">
  <b>⚠️ 位置到位 ≠ 反转到位。</b>双指数同日创 60 日新低，跌停 <b>{ALL['limit_down']} 家</b>（盘中一度 40 家），涨 {ALL['up']} / 跌 {ALL['down']}；成交额 {AMT_17:,.0f} 亿、<b>缩量 {abs(AMT_DIFF):,.0f} 亿（{AMT_PCT:+.1f}%）</b>。
  <b>她 22:02 说「重新杀进来」，但 13:38 自己说「未见可扭转局面的力量」——她赌的是 C5 空间，不是今天的盘面。</b>
</div>

<h2>三、最值得关注的 3 个板块</h2>
<table>
<thead><tr><th>板块</th><th>11/17 收盘实测</th><th>博主口径 / 打法</th></tr></thead>
<tbody>
<tr><td><b>① 白酒 / 大消费</b><br><span class="tag tag-bull">首选 · 唯一正收益</span></td>
    <td>池 5 只 <b class="up">{p_wine['up']} 涨 {p_wine['down']} 跌</b>，均值 <b class="up">+{p_wine['avg_pct']:.2f}%</b>，额 {p_wine['amount_yi']:,.0f} 亿<br>
      {mem(p_wine, 2, 1)}</td>
    <td><b>唯一收正的池</b>。茅台收 {MT['close']:.2f}、站上 MA20 {MT['ma20']:.2f}，距 60 日高 {MT['hi60']:.2f} 仅 {MT['hi60']-MT['close']:.2f} 点。<b>只做茅台</b>。</td></tr>
<tr><td><b>② 科技龙头（GPU / 存储）</b><br><span class="tag tag-neutral">方向 · 等回踩</span></td>
    <td>存储池 <b class="down">{p_st['avg_pct']:+.2f}%</b>（1 涨 7 跌），额 {p_st['amount_yi']:,.0f} 亿<br>
      {mem(p_st, 2, 1)}</td>
    <td>她 10:47 定的方向 + <b>22:02 已动手</b>：只做高成长龙头，<b>不看板块平均</b>。寒武纪 {HX['pct']:+.2f}% 唯一红、站上 MA20 {HX['ma20']:.2f}；但 CPO 池 {p_cpo['avg_pct']:+.2f}% 说明<b>洗盘没完</b> → <b>等回踩分批，不追高</b>。</td></tr>
<tr><td><b>③ 军工</b><br><span class="tag tag-neutral">观察 · 池内一枝独秀</span></td>
    <td>池 12 只均值 <b class="down">{p_mil['avg_pct']:+.2f}%</b>（{p_mil['up']} 涨 {p_mil['down']} 跌），额 {p_mil['amount_yi']:,.0f} 亿<br>
      {mem(p_mil, 2, 1)}</td>
    <td>11/16「军工五六只冲板」收盘没兑现、<b>今天补上</b>：中航光电 <b class="up">{ZH['pct']:+.2f}%</b> 放量 {ZH['vol_ratio5']:.0f}%、收在当日最高附近。<b>只做池内领涨</b>。</td></tr>
</tbody>
</table>
<p class="meta" style="margin-bottom:0">
  <b>底仓垫</b>：银行/红利池 10 只均值 <b class="up">{p_bank['avg_pct']:+.2f}%</b>，招行 {YB['close']:.2f} 站上 MA20 {YB['ma20']:.2f}、距 60 日高 {YB['hi60']:.2f} 仅 {(YB['hi60']/YB['close']-1)*100:.2f}% → <b>只垫仓</b>。
  <b>回避三个</b>：人形机器人/端侧 <b class="down">{p_rob['avg_pct']:+.2f}%</b>（宇树 {p_rob['members'][-1]['pct']:+.2f}%）；CPO/光通信 <b class="down">{p_cpo['avg_pct']:+.2f}%</b>；算力租赁 <b class="down">{p_calc['avg_pct']:+.2f}%</b>。
  <b>13:27「光刻胶表现出色」/ 13:35「超节点+交换机拉起」</b>：涨停池分散 23 个行业、最高仅 3 板，<b>未成主线</b>。
  口径：核心标的池收盘涨跌幅（东财快照），与 11/16 可比。
</p>

<h3>新易盛（300308）· {CPO['close']:.2f}（{CPO['pct']:+.2f}%）—— 她 10:28 那笔账</h3>
<img class="chart" src="../charts/300308_SZ_20261117.png" alt="新易盛 2026-11-17 K线">
<p class="chart-caption">高 {CPO['high']:.2f} / 低 <b>{CPO['low']:.2f}</b>（<b>新 60 日低</b>）/ 收 {CPO['close']:.2f}，额 {CPO['amount_yi']:.0f} 亿。
从 {CPO_PEAK:.2f} 到今天 <b>−{CPO_PCT:.2f}%</b>，与她 10:28 口算一致；MA20 {CPO['ma20']:.2f} 远在头顶 ——<b>「洗盘没完」的实证</b>。</p>

<h2>四、3 支个股</h2>
<table>
<thead><tr><th>代码 名称</th><th class="score">收盘</th><th class="score">涨跌</th>
<th class="score">成交额</th><th>关键位</th><th>实测印证 / 动作</th></tr></thead>
<tbody>
<tr><td><b>600519</b> 贵州茅台</td><td class="score">{MT['close']:.2f}</td><td class="score"><span class="up">{MT['pct']:+.2f}%</span></td>
    <td class="score">{MT['amount_yi']:.1f} 亿</td><td>MA20 <b>{MT['ma20']:.2f}</b> · 60 日高 <b>{MT['hi60']:.2f}</b></td>
    <td class="text">唯一正收益池的龙头，逆势收红、站上 MA20 {MT['ma20']:.2f}，量能 {MT['vol_ratio5']:.0f}% 未爆量。<b>低吸不追高</b>，破 MA20 放弃。</td></tr>
<tr><td><b>688256</b> 寒武纪</td><td class="score">{HX['close']:.2f}</td><td class="score"><span class="up">{HX['pct']:+.2f}%</span></td>
    <td class="score">{HX['amount_yi']:.1f} 亿</td><td>MA20 <b>{HX['ma20']:.2f}</b> · 60 日高 <b>{HX['hi60']:.2f}</b></td>
    <td class="text">正对她 10:47「高成长+行业向好的科技股」—— <b>存储池 1 涨 7 跌里唯一的红</b>，站上 MA20 {HX['ma20']:.2f}。<b>回踩 MA20 可分批</b>，不追高。</td></tr>
<tr><td><b>002179</b> 中航光电</td><td class="score">{ZH['close']:.2f}</td><td class="score"><span class="up">{ZH['pct']:+.2f}%</span></td>
    <td class="score">{ZH['amount_yi']:.1f} 亿</td><td>MA20 <b>{ZH['ma20']:.2f}</b> · 60 日高 <b>{ZH['hi60']:.2f}</b></td>
    <td class="text"><b>全场最强个股</b>：放量 <b>{ZH['vol_ratio5']:.0f}%</b>、收在当日最高 {ZH['high']:.2f} 附近，站上 MA5/MA10/MA20。<b>回踩 MA20 不破可分，不追高。</b></td></tr>
</tbody>
</table>

<h3>贵州茅台（600519）· {MT['close']:.2f}（{MT['pct']:+.2f}%）</h3>
<img class="chart" src="../charts/600519_SH_20261117.png" alt="贵州茅台 2026-11-17 K线">
<p class="chart-caption">高 {MT['high']:.2f} / 低 {MT['low']:.2f} / 收 {MT['close']:.2f}，逆势小阳；MA20 {MT['ma20']:.2f} 在下方支撑，60 日高 {MT['hi60']:.2f} 距今 {MT['hi60']-MT['close']:.2f} 点。</p>

<h3>寒武纪（688256）· {HX['close']:.2f}（{HX['pct']:+.2f}%）</h3>
<img class="chart" src="../charts/688256_SH_20261117.png" alt="寒武纪 2026-11-17 K线">
<p class="chart-caption">高 {HX['high']:.2f} / 低 {HX['low']:.2f} / 收 {HX['close']:.2f}，站上 MA20 {HX['ma20']:.2f}；60 日高 {HX['hi60']:.2f} 在左上（距今 {(HX['hi60']-HX['close'])/HX['close']*100:.1f}%）。</p>

<h3>中航光电（002179）· {ZH['close']:.2f}（{ZH['pct']:+.2f}%）</h3>
<img class="chart" src="../charts/002179_SZ_20261117.png" alt="中航光电 2026-11-17 K线">
<p class="chart-caption">高 {ZH['high']:.2f} / 低 {ZH['low']:.2f} / 收 {ZH['close']:.2f}，放量阳线站上 MA20 {ZH['ma20']:.2f}；60 日高 {ZH['hi60']:.2f} 是第一道压制，60 日低 {ZH['lo60']:.2f} 在下方。</p>

<h2>五、11/18（周三）盯什么（5 条）</h2>
<ul class="tight">
  <li><b>她给不给建仓的落地条件</b> —— 22:02 只有表态，<b>没给标的、点位、仓位</b>；11/18 仍不给，就只是情绪信号。</li>
  <li><b>创业板 {CY_LO60:.2f}（她的 2263 点）不破</b> —— 已触达，破了下一目标 2200 整数关。</li>
  <li><b>沪指 60 日新低 {SH_LO60:.2f} 不破</b> —— 破了说明她的「位置」判断还要下修。</li>
  <li><b>跌停从 {ALL['limit_down']} 家回落 + 成交额回到 1.6 万亿以上</b> —— 今天缩量 {abs(AMT_DIFF):,.0f} 亿；<b>缩量止跌不算止跌</b>。</li>
  <li><b>CPO 龙头是否止跌</b> —— 新易盛收 {CPO['close']:.2f}、新 60 日低 {CPO['low']:.2f}；<b>它不企稳，科技的「洗完」就不成立</b>。</li>
</ul>

<h2>六、偏差记录</h2>
<table>
<thead><tr><th>项</th><th>博主口径</th><th>实测 / 处理</th></tr></thead>
<tbody>
<tr><td>14:56「本周 2263 点」<br><span class="tag tag-bull">分毫不差</span></td><td class="text">本周 2263 点可以了，接下来等吃肉了</td>
    <td class="text">创业板指最低 <b>{CY_LO60:.2f}</b>，<b>与 2263 点分毫不差</b>；收盘 {CY['close']:.2f} 较日低拉回 {CY['close']-CY['low']:.2f} 点。<b>本期最硬的核验</b>——她第一次在 C 杀期间给出可执行点位。</td></tr>
<tr><td>10:28 CPO 龙头跌幅<br><span class="tag tag-bull">分毫不差</span></td><td class="text">CPO 龙头从 1416.88 到今天的 385 元，跌了 1031.88 元，幅度达 72.82%</td>
    <td class="text">标的 = <b>新易盛 300308</b>：前复权峰值 {CPO_PEAK:.2f}（6/22），今日盘中最低 {CPO['low']:.2f}、收盘 {CPO['close']:.2f}。
    <b>(1416.88−385) = 1031.88、占比 {CPO_PCT:.2f}%</b>，<b>与她的口算完全一致</b>；再创 60 日新低。</td></tr>
<tr><td>22:02 建仓表态<br><span class="tag tag-neutral">无法核验</span></td><td class="text">我既然能够在 5 月份高位撤离，这次重新杀进来，肯定会信心满满……</td>
    <td class="text"><b>只有表态，没有标的/点位/仓位</b> → <b>只当方向信号，不当买点</b>。与 13:38 不矛盾：她赌 C5 空间，不是今天的盘面。</td></tr>
<tr><td>双门槛 3706 / 2626<br><span class="tag tag-neutral">继续搁置</span></td><td class="text">11/17 全天未提门槛，只给 2263 点与 C5 口径</td>
    <td class="text">沪指差 <b>{SH_GAP:.2f} 点</b>、创业板差 <b>{CY_GAP:.2f} 点</b>。
    <b>门槛没松、新点位出现</b>——框架从「等收复 3706/2626」换成「等 C5 完成」，<b>点位换了，纪律没换</b>。</td></tr>
</tbody>
</table>
<p class="meta" style="margin-bottom:0">
  其余 <b>3 条口径自洽</b>：11:15「探低之后的抵抗」、13:02「无明朗热点效应」、13:13「没有出现大的力量」——实测涨停 {ALL['limit_up']} 只分散、最高 3 板、缩量 {abs(AMT_PCT):.1f}%，均吻合。
  采集：weibo skill 四轮补采 → <b>26 条</b>（06:07–22:02，含 15:08 后 4 条）；行情：<b>Tushare Pro 日线</b>（pro.daily / index_daily + adj_factor 前复权）+ 东财收盘快照。
</p>

<div class="foot">
  <p><b>免责声明</b>：本报告为公开微博内容整理与技术面统计，<b>不构成投资建议</b>；
  「3 板块 + 3 个股」是博主观点 + 实测强度的归纳，股市有风险，投资需谨慎。</p>
  <p>
    报告生成：2026-11-17 收盘后增补版 · 数据源 weibo skill + Tushare Pro 日线 + 东方财富快照 ·
    脚本 <code>collect_tushare_20261117.py</code> / <code>make_wu2198_charts_20261117_close.py</code> /
    <code>gen_wu2198_report_20261117_close.py</code>。
  </p>
</div>

</div>
</body>
</html>
"""

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fix_mobile_tables import patch_html

if __name__ == "__main__":
    out = ROOT / "html" / "wu2198-20261117.html"
    out.write_text(patch_html(HTML), encoding="utf-8")
    print(f"[out] {out}  ({len(HTML)} bytes)")
