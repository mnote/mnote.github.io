"""wu2198 投资日报 2026-11-17（周二 · 盘中版）— 线上产物生成器

用法： python3 scripts/gen_wu2198_report_20261117.py
产物： html/wu2198-20261117.html
篇幅： 正文 ≤ 2000 中文字 / 表格 ≤ 4 张
"""
import json
import sys
from pathlib import Path

ROOT = Path("/Users/maoling/workspace/mnote.github.io")
CH = ROOT / "charts"

KPI = json.loads((CH / "_kpic_20261117.json").read_text(encoding="utf-8"))
SEC = json.loads((CH / "_pools_20261117.json").read_text(encoding="utf-8"))
INTRA = json.loads((CH / "_intraday_20261117.json").read_text(encoding="utf-8"))
ALL = INTRA["all"]
B16 = json.loads((CH / "_breadth_20261116.json").read_text(encoding="utf-8"))["20261116"]
AMT = INTRA["amount_by_day"]
CUT = INTRA["amount_cutoff"]
EM = INTRA["em_pools"]

SH, CY = KPI["000001.SH"], KPI["399006.SZ"]
RZ, HX, ZH = KPI["300442.SZ"], KPI["688256.SH"], KPI["002179.SZ"]
P = SEC
p_calc, p_st, p_mil = P["算力租赁/IDC"], P["存储/半导体/GPU"], P["军工"]
p_bank, p_cpo, p_rob = P["银行/红利"], P["CPO/光通信"], P["人形机器人/端侧"]


def mem(pool, n_top=2, n_bot=1):
    """池内领涨 n 只 + 领跌 n 只，动态拼接。"""
    ms = pool["members"]
    top = ms[:n_top]
    bot = ms[-n_bot:] if n_bot else []
    def f(m):
        cls = "up" if m["pct"] >= 0 else "down"
        return f'<b class="{cls}">{m["pct"]:+.2f}%</b>' if m["pct"] >= 0 \
            else f'<b class="{cls}">{m["pct"]:+.2f}%</b>'
    a = "、".join(f'{m["name"]} {f(m)}' for m in top)
    if bot:
        a += " / " + "、".join(f'{m["name"]} {f(m)}' for m in bot)
    return a

# 同时点成交额同比（沪深两市，截到同一时点）
_today = AMT.get("2026-11-17", 0)
_yest = AMT.get("2026-11-16", 0)
AMT_DIFF = _today - _yest
AMT_PCT = AMT_DIFF / _yest * 100 if _yest else 0

SH_GAP = 3706 - SH["close"]
CY_GAP = 2626 - CY["close"]
SH_LO60 = 3574.27
SH_LO60_GAP = SH["close"] - SH_LO60
CY_LO_GAP = CY["close"] - 2308.90

STAMP = INTRA["stamp"]

TITLE = "wu2198 - 2026-11-17（周二 探低回升，主线未成）"

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
</head>
<body>
<div class="wrap">

<div class="hero">
  <h1>📈 {TITLE}</h1>
  <div class="meta">
    <span><a href="/">← 返回首页</a></span>
    <span>🕘 <b>盘中版 · 数据截至 {STAMP}</b></span>
    <span>📡 weibo skill（三轮补采，11 条，06:07–13:13）</span>
    <span>💹 Tushare Pro 日线 + 东财实时快照</span>
  </div>
  <p class="stance">
    <b>🟡 「探低之后的抵抗」成立，但「没有大的力量」也是真的 —— 情绪修复，主线没成。</b>
    10:47 定性「科技类股<b>杀估值去杠杆</b>，洗干净之后，高成长+行业向好的科技股会走出局部行情」；
    11:14 重申「有技术的可以 <b>C3 开始布局</b>，稳健的是 <b>C5 完成之后干</b>」；
    11:15「早盘还只是探低之后的抵抗」；13:02/13:13「还没有明朗的热点效应」「暂时没有出现大的力量」。
    <b>可做的只有一条：算力租赁（她 11/16 唯一催化方向）8/8 全涨兑现；银行昨天一日游，今天退潮。</b>
  </p>
</div>

<div class="grid-4" style="margin-bottom:8px">
  <div class="kpi"><div class="label">上证指数</div><div class="val">{SH['close']:.2f}</div>
    <div class="sub"><span class="down">{SH['pct']:+.2f}%</span> · 早盘破 60 日低后拉回</div></div>
  <div class="kpi"><div class="label">创业板指</div><div class="val">{CY['close']:.2f}</div>
    <div class="sub"><span class="down">{CY['pct']:+.2f}%</span> · 早盘破 {2308.90:.2f} 新低后拉回</div></div>
  <div class="kpi"><div class="label">跌停 / 涨停</div><div class="val">{ALL['limit_down']} / {ALL['limit_up']}</div>
    <div class="sub">昨跌停 <b>{B16['limit_down']}</b> 家 → 情绪修复；涨 {ALL['up']} / 跌 {ALL['down']}</div></div>
  <div class="kpi"><div class="label">沪深成交额（至 {CUT}）</div><div class="val">{_today:,.0f} 亿</div>
    <div class="sub"><span class="vol">同时点同比 {AMT_DIFF:+,.0f} 亿（{AMT_PCT:+.1f}%）</span></div></div>
</div>

<h2>一、博主说了什么（8 条）</h2>
<table>
<thead><tr><th>时间</th><th>信号</th><th>原文</th><th>判读 / 日线实测</th></tr></thead>
<tbody>
<tr><td><b>06:07</b></td><td>⚪ 外盘</td><td class="text">昨晚美股下跌：道指跌739点、纳指跌626点、标普跌145点</td>
  <td class="text"><b>三个数字分毫不差</b>：11/16 实测 −739.38 / −626.51 / −145.08（纳指 −2.49% 最重）。</td></tr>
<tr><td><b>09:31</b></td><td>⚪ 情绪</td><td class="text">我不投降！</td>
  <td class="text">隔夜纳指 −2.49% 之后的情绪表态，<b>无操作信息</b>。</td></tr>
<tr><td><b>10:47 / 11:05</b></td><td>🟢🟢 方向</td><td class="text">科技类股杀估值去杠杆，清洗干净之后，高成长+行业向好的科技股会走出局部行情。明白666</td>
  <td class="text"><b>本期核心定性</b>：把 11/16 科技崩盘解释成「杀估值去杠杆」，不是「逻辑破坏」。
  实测涨停池集中在电子化学 3 / 光学光电 3 / IT服务 3，大涨榜伟测科技 +20%、华虹宏力 +11.33%、影石创新 +14.96% → <b>「局部行情」成立</b>。</td></tr>
<tr><td><b>11:14</b></td><td>🟡 操作框架</td><td class="text">有技术的可以 C3 开始布局，稳健的是 C5 完成之后干</td>
  <td class="text"><b>重申 11/13 口径，门槛一个字没松</b>：双门槛 3706 / 2626 仍未提（沪指今差 {SH_GAP:.2f} 点、创业板差 {CY_GAP:.2f} 点）。</td></tr>
<tr><td><b>11:15</b></td><td>🟡 盘面定性</td><td class="text">暂时看，早盘还只是探低之后的抵抗！</td>
  <td class="text"><b>实测成立</b>：早盘创业板破 11/16 新低至 <b>{CY["low"]:.2f}</b>、上证破 60 日低 {SH_LO60:.2f} 至 <b>{SH["low"]:.2f}</b>，午后双双拉回至基本平盘。</td></tr>
<tr><td><b>11:27 / 11:31</b></td><td>⚪ 情绪</td><td class="text">我不会鼓动大家，接下来聊风月吧！／早盘不用点评，中午加菜，吃肉！</td>
  <td class="text">11:31 互动 <b>1.03 万</b>为当日第一，但<b>是情绪帖不是操作帖</b>；「不会鼓动大家」= 今天不给方向。</td></tr>
<tr><td><b>13:02</b></td><td>🟡 热点</td><td class="text">暂时还没有明朗的热点效应！</td>
  <td class="text">实测涨停 {ALL['limit_up']} 只分散在 6 个以上行业、<b>无连板主线</b>（东财涨停池 {EM.get('zt',{}).get('tc','—')} 只、炸板 {EM.get('zb',{}).get('tc','—')} 只）→ <b>口径自洽</b>。</td></tr>
<tr><td><b>13:13</b></td><td>🟡 资金</td><td class="text">暂时没有出现大的力量！</td>
  <td class="text">成交额同时点同比 {AMT_PCT:+.1f}%（{AMT_DIFF:+,.0f} 亿）→ <b>放量有限</b>，没有增量资金。</td></tr>
</tbody>
</table>

<h2>二、大盘关键点位</h2>
<p class="meta" style="margin-bottom:6px">K 线<b>红涨绿跌</b>；关键位在图<b>左侧虚线</b>。
<b>最右一根为 {STAMP} 盘中未完成 K 线</b>，成交量为<b>盘中累计值</b>（橙色边框标记），收盘形态待验证。</p>

<h3>上证指数 · {SH['close']:.2f}（{SH['pct']:+.2f}%）</h3>
<img class="chart" src="../charts/000001_SH_20261117.png" alt="上证指数 2026-11-17 盘中 K线">
<p class="chart-caption">开 {SH['open']:.2f} / 高 {SH['high']:.2f} / 低 <b>{SH['low']:.2f}</b> / 现 {SH['close']:.2f}。
早盘跌破 60 日低 {SH_LO60:.2f} 后拉回，现价距 60 日低仅 {SH_LO60_GAP:.2f} 点（{SH_LO60_GAP/SH_LO60*100:.2f}%）；
<b>3706 差 {SH_GAP:.2f} 点（{SH_GAP/3706*100:.2f}%）</b>，MA20 {SH['ma20']:.2f} 仍失守。</p>

<h3>创业板指 · {CY['close']:.2f}（{CY['pct']:+.2f}%）</h3>
<img class="chart" src="../charts/399006_SZ_20261117.png" alt="创业板指 2026-11-17 盘中 K线">
<p class="chart-caption">开 {CY['open']:.2f} / 高 {CY['high']:.2f} / 低 <b>{CY['low']:.2f}</b> / 现 {CY['close']:.2f}。
早盘跌穿 11/16 新低 2308.90 至 {CY['low']:.2f}，午后较日低拉回 {CY['close']-CY['low']:.2f} 点，<b>但仍低于 11/16 新低 {abs(CY_LO_GAP):.2f} 点、尚未收复</b>；
<b>2626 差 {CY_GAP:.2f} 点（{CY_GAP/2626*100:.2f}%）</b>，MA20 {CY['ma20']:.2f} 远在头顶。</p>

<div class="risk">
  <b>⚠️ 今天最该看的不是指数，是跌停家数。</b>跌停从 11/16 的 <b>{B16['limit_down']} 家降到 {ALL['limit_down']} 家</b>，
  涨停从 {B16['limit_up']} 家增到 <b>{ALL['limit_up']} 家</b>；但涨跌家数仍是 <b>涨 {ALL['up']} / 跌 {ALL['down']}</b>（昨日收盘 {B16['up']} / {B16['down']}）→ <b>跌停冰点在退潮，但市场仍跌多涨少</b>。
  但沪深成交额同时点 {AMT_PCT:+.1f}%（{AMT_DIFF:+,.0f} 亿）<b>没有增量</b> → <b>缩量修复，不是反转</b>。
</div>

<h2>三、最值得关注的 3 个板块</h2>
<table>
<thead><tr><th>板块</th><th>11/17 盘中实测（{STAMP}）</th><th>博主口径 / 打法</th></tr></thead>
<tbody>
<tr><td><b>① 算力租赁 / IDC</b><br><span class="tag tag-bull">首选 · 催化兑现</span></td>
    <td>池 8 只 <b class="up">{p_calc['up']} 涨 {p_calc['down']} 跌</b>，均值 <b class="up">+{p_calc['avg_pct']:.2f}%</b>，额 {p_calc['amount_yi']:,.0f} 亿<br>
      {mem(p_calc, 3, 0)}</td>
    <td>11/16 12:53 唯一催化（#DeepSeek因算力不足限额#）—— <b>今天 8/8 全涨，兑现</b>。
    但龙头润泽 {RZ['close']:.2f} <b>仍在 MA20 {RZ['ma20']:.2f} 之下</b>（差 {(RZ['ma20']-RZ['close'])/RZ['close']*100:.1f}%）→ <b>等站回 MA20，不追反抽</b>。</td></tr>
<tr><td><b>② 存储 / 半导体 / GPU</b><br><span class="tag tag-neutral">次选 · 内部分化极大</span></td>
    <td>池 8 只均值 <b class="{'up' if p_st['avg_pct'] >= 0 else 'down'}">{p_st['avg_pct']:+.2f}%</b>（{p_st['up']} 涨 {p_st['down']} 跌），额 {p_st['amount_yi']:,.0f} 亿<br>
      {mem(p_st, 2, 2)}</td>
    <td>正对应她 10:47 的「高成长+行业向好的科技股走出局部行情」。<b>只做龙头</b>：寒武纪站上 MA5/MA10/MA20（{HX['ma20']:.2f}），回踩不破可分；<b>不碰分化掉的跟风股</b>。</td></tr>
<tr><td><b>③ 军工</b><br><span class="tag tag-neutral">观察 · 补涨</span></td>
    <td>池 12 只均值 <b class="{'up' if p_mil['avg_pct'] >= 0 else 'down'}">{p_mil['avg_pct']:+.2f}%</b>（{p_mil['up']} 涨 {p_mil['down']} 跌），额 {p_mil['amount_yi']:,.0f} 亿<br>
      {mem(p_mil, 2, 1)}</td>
    <td>她 11/16 13:55「军工有五六只冲板」收盘没兑现，<b>今天补上</b>。<b>只做池内领涨</b>：中航光电 {ZH['close']:.2f} 站上 MA5/MA10/MA20（{ZH['ma10']:.2f} / {ZH['ma20']:.2f}），回踩 MA10 可分。</td></tr>
</tbody>
</table>
<p class="meta" style="margin-bottom:0">
  <b>回避两个</b>：银行/红利 <b class="down">{p_bank['avg_pct']:+.2f}%</b>（<b>9 跌 1 涨</b>）—— 昨天唯一避险方向，今天一日游退潮；
  人形机器人/端侧 <b class="down">{p_rob['avg_pct']:+.2f}%</b>（宇树 <b class="down">{p_rob['members'][-1]['pct']:+.2f}%</b>）；CPO/光通信 <b class="down">{p_cpo['avg_pct']:+.2f}%</b>。
  口径：核心标的池 + 东财实时快照（{STAMP}），与 11/16 收盘口径可比。
</p>

<h2>四、3 支个股</h2>
<table>
<thead><tr><th>代码 名称</th><th class="score">现价</th><th class="score">涨跌</th>
<th class="score">成交额</th><th>关键位</th><th>实测印证 / 动作</th></tr></thead>
<tbody>
<tr><td><b>300442</b> 润泽科技</td><td class="score">{RZ['close']:.2f}</td><td class="score"><span class="up">{RZ['pct']:+.2f}%</span></td>
    <td class="score">{RZ["amount_yi"]:.1f} 亿</td><td>MA20 <b>{RZ['ma20']:.2f}</b> · 60 日低 <b>{RZ['lo60']:.2f}</b></td>
    <td class="text">11/16 跌停后反抽 <b class="up">{RZ['pct']:+.2f}%</b>，算力租赁池 {p_calc['up']}/{p_calc['up']+p_calc['down']} 全涨 —— <b>她唯一催化方向的兑现标志</b>。
    但 <b>MA20 {RZ['ma20']:.2f} 未收复</b>，60 日低 {RZ['lo60']:.2f} 只差 {(RZ['close']-RZ['lo60'])/RZ['close']*100:.1f}%。<b>站回 MA20 才买，不追反抽。</b></td></tr>
<tr><td><b>688256</b> 寒武纪</td><td class="score">{HX['close']:.2f}</td><td class="score"><span class="up">{HX['pct']:+.2f}%</span></td>
    <td class="score">{HX["amount_yi"]:.1f} 亿</td><td>MA20 <b>{HX['ma20']:.2f}</b> · 60 日高 <b>{HX['hi60']:.2f}</b></td>
    <td class="text">存储/GPU 池领涨，站上 MA5/MA10/MA20 三线；高 {HX['high']:.2f} 回落、量能 {HX['amount_yi']:.0f} 亿为池内最大。
    符合她「高成长」口径。<b>回踩 MA20 {HX['ma20']:.2f} 不破可分批</b>；PE 偏高，不追高。</td></tr>
<tr><td><b>002179</b> 中航光电</td><td class="score">{ZH['close']:.2f}</td><td class="score"><span class="up">{ZH['pct']:+.2f}%</span></td>
    <td class="score">{ZH["amount_yi"]:.1f} 亿</td><td>MA10 <b>{ZH['ma10']:.2f}</b> · 60 日高 <b>{ZH['hi60']:.2f}</b></td>
    <td class="text">军工池领涨且<b>站上全部均线</b>（MA5 {ZH['ma5']:.2f} / MA10 {ZH['ma10']:.2f} / MA20 {ZH['ma20']:.2f}），
    60 日高 {ZH['hi60']:.2f} 距今 {ZH['hi60']-ZH['close']:.2f} 点。<b>回踩 MA10 可分，冲高不追。</b></td></tr>
</tbody>
</table>

<h3>润泽科技（300442）· {RZ['close']:.2f}（{RZ['pct']:+.2f}%）</h3>
<img class="chart" src="../charts/300442_SZ_20261117.png" alt="润泽科技 2026-11-17 盘中 K线">
<p class="chart-caption">高 {RZ['high']:.2f} / 低 {RZ['low']:.2f} / 现 {RZ['close']:.2f}，11/16 跌停后反抽；
MA5 {RZ['ma5']:.2f}、MA20 {RZ['ma20']:.2f} 压在头上，60 日低 {RZ['lo60']:.2f} 在下方。</p>

<h3>寒武纪（688256）· {HX['close']:.2f}（{HX['pct']:+.2f}%）</h3>
<img class="chart" src="../charts/688256_SH_20261117.png" alt="寒武纪 2026-11-17 盘中 K线">
<p class="chart-caption">高 {HX['high']:.2f} / 低 {HX['low']:.2f} / 现 {HX['close']:.2f}，站上 MA20 {HX['ma20']:.2f}；
60 日高 {HX['hi60']:.2f} 在左上（距今 {(HX['hi60']-HX['close'])/HX['close']*100:.1f}%）。</p>

<h3>中航光电（002179）· {ZH['close']:.2f}（{ZH['pct']:+.2f}%）</h3>
<img class="chart" src="../charts/002179_SZ_20261117.png" alt="中航光电 2026-11-17 盘中 K线">
<p class="chart-caption">高 {ZH['high']:.2f} / 低 {ZH['low']:.2f} / 现 {ZH['close']:.2f}，站上 MA10/MA20；
60 日高 {ZH['hi60']:.2f}、60 日低 {ZH['lo60']:.2f} 在两端。</p>

<h2>五、今天下午 + 明日盯什么（5 条）</h2>
<ul class="tight">
  <li><b>创业板 {CY["low"]:.2f} 不破</b> —— 今日最低已破 11/16 新低，破了则 2200 成下一目标。</li>
  <li><b>跌停家数守在 50 家以内</b> —— 已从 174 降到 {ALL['limit_down']} 家，情绪修复但没增量。</li>
  <li><b>润泽科技站回 MA20 {RZ['ma20']:.2f}</b> —— 她 11/16 唯一催化是否真兑现，就看这一根。</li>
  <li><b>银行池不能继续绿</b> —— 昨天 +1.97% 唯一避险，今天 {p_bank['avg_pct']:+.2f}；银行翻绿 = 避险逻辑破产。</li>
  <li><b>博主是否给出新门槛或买点</b> —— 11/16 全天未给、今天也没给；她不给之前只按「C3 分批、不追高、控仓」执行。</li>
</ul>

<h2>六、偏差记录</h2>
<table>
<thead><tr><th>项</th><th>博主口径 / 昨日结论</th><th>实测 / 处理</th></tr></thead>
<tbody>
<tr><td>11:15 盘面定性<br><span class="tag tag-bull">核验通过</span></td><td class="text">早盘还只是探低之后的抵抗</td>
    <td class="text">创业板破新低至 {CY["low"]:.2f}、上证破 60 日低至 {SH["low"]:.2f}，午后双双拉回至基本平盘 → <b>「探低 + 抵抗」成立</b>。</td></tr>
<tr><td>06:07 外盘<br><span class="tag tag-bull">核验通过</span></td><td class="text">道指跌739点、纳指跌626点、标普跌145点</td>
    <td class="text">11/16 实测 −739.38 / −626.51 / −145.08，<b>分毫不差</b>（外盘播报继续全中）。</td></tr>
<tr><td>11/16 结论「银行/红利首选」<br><span class="tag tag-bear">一日游被证伪</span></td><td class="text">（11/16 14:39 银行是唯一没受影响的板块，池 +1.97%）</td>
    <td class="text">今日银行池 <b class="down">{p_bank['avg_pct']:+.2f}%</b>、<b>9 跌 1 涨</b>。避险资金一日游，<b>不能当主线</b>。</td></tr>
<tr><td>11/16 结论「算力租赁=观察位」<br><span class="tag tag-neutral">提前兑现</span></td><td class="text">等龙头站回 MA20 {RZ['ma20']:.2f} 再谈</td>
    <td class="text">今日池 <b class="up">8/8 全涨 +{p_calc['avg_pct']:.2f}%</b>，但润泽 {RZ['close']:.2f} <b>仍未站回 MA20</b> → <b>提前兑现但关键位未过，继续观察</b>。</td></tr>
<tr><td>双门槛 3706 / 2626<br><span class="tag tag-neutral">继续搁置</span></td><td class="text">11/16 全天未提，11/17 也未提（11:14 只重申 C3/C5 框架）</td>
    <td class="text">沪指距 3706 差 <b>{SH_GAP:.2f} 点</b>、创业板距 2626 差 <b>{CY_GAP:.2f} 点</b>。
    <b>门槛没松</b>，她只是把表达从「等收复」换成「C3 分批 / C5 干」。</td></tr>
</tbody>
</table>
<p class="meta" style="margin-bottom:0">
  其余口径与博主一致：10:47「杀估值去杠杆 + 局部行情」与涨停池分布（电子化学 3 / 光学光电 3 / IT服务 3）吻合；
  13:02「无明朗热点」与涨停 {ALL['limit_up']} 只分散、无连板主线吻合。
  采集：weibo skill 三轮词表补采 → 11 条（06:07–13:13）；行情：Tushare Pro 日线（到 11/16）+ 东财 {STAMP} 实时快照。
</p>

<div class="foot">
  <p><b>免责声明</b>：本报告为公开微博内容整理与技术面统计，<b>不构成投资建议</b>；
  「3 板块 + 3 个股」是博主观点 + 实测强度的归纳，不代表推荐。股市有风险，投资需谨慎。</p>
  <p><b>盘中版说明</b>：本页数据截至 {STAMP}，最右一根 K 线为<b>未完成 K 线</b>、成交量为盘中累计值，
  收盘形态与最终成交额可能与本页不同；收盘后如需定稿版，以同一 URL 的更新版本为准。</p>
  <p>
    报告生成：2026-11-17 盘中版 · 数据源 weibo skill + Tushare Pro + 东方财富 ·
    脚本 <code>collect_intraday_20261117.py</code> / <code>collect_intraday_20261117b.py</code> /
    <code>fetch_idx_kline_20261117.py</code> / <code>build_intraday_20261117.py</code> /
    <code>make_wu2198_charts_20261117.py</code> / <code>gen_wu2198_report_20261117.py</code>。
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
