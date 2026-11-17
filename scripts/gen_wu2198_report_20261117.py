"""wu2198 投资日报 2026-11-17（周二 · 收盘版）— 线上产物生成器

用法： python3 scripts/gen_wu2198_report_20261117.py
产物： html/wu2198-20261117.html（覆盖盘中版）
篇幅： 正文 ≤ 2000 中文字 / 表格 ≤ 4 张
"""
import json
import sys
from pathlib import Path

ROOT = Path("/Users/maoling/workspace/mnote.github.io")
CH = ROOT / "charts"

KPI = json.loads((CH / "_kpic_20261117.json").read_text(encoding="utf-8"))
KPI_FULL = json.loads((CH / "_kpi_20261117.json").read_text(encoding="utf-8"))
SEC = json.loads((CH / "_pools_20261117.json").read_text(encoding="utf-8"))
CLOSE = json.loads((CH / "_close_20261117.json").read_text(encoding="utf-8"))
SER = CLOSE["series"]
ALL = CLOSE["all"]
EM = CLOSE["em_pools"]

SH, CY = KPI_FULL["000001.SH"], KPI_FULL["399006.SZ"]
KC, HS, KH = KPI_FULL["000300.SH"], KPI_FULL["000688.SH"], KPI_FULL["399001.SZ"]
ZH, MT, HX = KPI_FULL["002179.SZ"], KPI_FULL["600519.SH"], KPI_FULL["688256.SH"]
RZ = KPI_FULL["300442.SZ"]

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
CY_LO60 = 2263.74          # 11/17 最低 = 60 日新低

TITLE = "wu2198 - 2026-11-17（周二 2263点触达，等吃肉）"

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
    <span>🕘 截稿 2026-11-17 15:25（<b>收盘版</b>）</span>
    <span>📡 weibo skill（三轮补采，<b>22 条</b>，06:07–14:56）</span>
    <span>💹 东方财富日 K（前复权，11/17 收盘）</span>
  </div>
  <p class="stance">
    <b>🟢 连续两天第一次出现明确方向 —— 但方向是「位置」不是「板块」。</b>
    10:07「<b>C 不一定是机会，但 C5 绝对是机会</b>」→ 10:31「<b>没有什么思考的余地，要么继续被干，要么干</b>」→
    14:56「<b>本周 2263 点可以了，接下来等吃肉了</b>」—— <b>她给的 2263 点当天就被创业板指最低 {CY_LO60:.2f} 触达</b>。
    她 13:38 也说清「<b>抵抗力量有，但未出现可扭转局面的力量</b>」——
    <b>位置到位、方向未定</b>：只做银行 + 白酒 + 军工，科技只留高成长龙头。
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

<h2>一、博主说了什么（8 条）</h2>
<table>
<thead><tr><th>时间</th><th>信号</th><th>原文</th><th>判读 / 日线实测</th></tr></thead>
<tbody>
<tr><td><b>06:07</b></td><td>⚪ 外盘</td><td class="text">昨晚美股下跌：道指跌739点、纳指跌626点、标普跌145点</td>
  <td class="text"><b>三个数字分毫不差</b>：11/16 实测 −739.38 / −626.51 / −145.08（纳指 −2.49% 最重）。</td></tr>
<tr><td><b>09:39</b></td><td>🟢 板块点名</td><td class="text">GPU，半导体等目前局部走红！</td>
  <td class="text"><b>「局部」成立、「等」不成立</b>：科创50 <b class="up">{KC['pct']:+.2f}%</b> 是五大指数唯一上涨，
  寒武纪 {HX['pct']:+.2f}%、有研新材涨停；但存储池均值 <b class="down">{p_st['avg_pct']:+.2f}%</b>、澜起 {p_st['members'][-1]['pct']:+.2f}% → <b>只有龙头在红</b>。</td></tr>
<tr><td><b>10:07</b></td><td>🟢🟢 位置定性</td><td class="text">以前给大家分析过 C 不一定是机会，但是 C5 绝对是机会。</td>
  <td class="text"><b>本期最重要的一条</b>：把「等」具体化成 <b>C5</b>。11:14 再次点名「有技术的 C3 开始布局，稳健的 C5 完成之后干」——<b>比 11/13 的「分批承接」更明确</b>。</td></tr>
<tr><td><b>10:31</b></td><td>🟢🟢 立场表态</td><td class="text">现在的位置，没有什么思考的余地。要么继续被干，要么干！</td>
  <td class="text"><b>从观望切到主动</b>。当日沪指最低 {SH_LO60:.2f}、创业板最低 {CY_LO60:.2f}，<b>双指数创 60 日新低</b> → 她在最低位喊「干」。</td></tr>
<tr><td><b>10:47</b></td><td>🟢 方向</td><td class="text">科技类股杀估值去杠杆，清洗干净之后，高成长+行业向好的科技股会走出局部行情。</td>
  <td class="text">把 11/16 科技崩盘定性为<b>杀估值</b>而非逻辑破坏。涨停池有研新材、卡莱特等兑现，但<b>算力池 {p_calc['avg_pct']:+.2f}%、存储池 {p_st['avg_pct']:+.2f}%</b> → <b>清洗尚未结束</b>。</td></tr>
<tr><td><b>13:38</b></td><td>🟡 收盘前定性</td><td class="text">市场上抵抗力量是有的，但还未见出现可扭转局面的力量。</td>
  <td class="text"><b>当日最准的一句</b>：涨 {ALL['up']} / 跌 {ALL['down']}，<b>尾盘跌停从盘中 40 家增到 {ALL['limit_down']} 家</b>，创业板收 {CY['close']:.2f}（<b>仍低于 11/16 新低 2308.90</b>）→ <b>有抵抗、无反转</b>。</td></tr>
<tr><td><b>14:54</b></td><td>🟡 盘面反应</td><td class="text">下砸拉起，好事！</td>
  <td class="text">尾盘从低位回拉，创业板自 {CY_LO60:.2f} 拉回 <b>{CY['close']-CY_LO60:.2f} 点</b>，但<b>收盘仍跌 {CY['pct']:+.2f}%</b>。</td></tr>
<tr><td><b>14:56</b></td><td>🟢🟢 关键位</td><td class="text">本周 2263 点可以了，接下来等吃肉了！</td>
  <td class="text"><b>本期最硬的核验</b>：创业板指最低 <b>{CY_LO60:.2f}</b>，<b>与 2263 点分毫不差</b>；这是她第一次在 C 杀期间给出<b>可执行点位</b>。「等吃肉」= 位置到了，买点在 C5 之后。</td></tr>
</tbody>
</table>

<h2>二、大盘关键点位</h2>
<p class="meta" style="margin-bottom:6px">K 线<b>红涨绿跌</b>；关键位在图<b>左侧虚线</b>。全部为 11/17 <b>完整收盘 K 线</b>。</p>

<h3>上证指数 · {SH['close']:.2f}（{SH['pct']:+.2f}%）</h3>
<img class="chart" src="../charts/000001_SH_20261117.png" alt="上证指数 2026-11-17 K线">
<p class="chart-caption">开 {SH['open']:.2f} / 高 {SH['high']:.2f} / 低 <b>{SH['low']:.2f}</b> / 收 {SH['close']:.2f}。
<b>最低 {SH_LO60:.2f} 是新的 60 日低点</b>（前低 3574.27 被跌破）；
<b>3706 差 {SH_GAP:.2f} 点（{SH_GAP/3706*100:.2f}%）</b>，MA20 {SH['ma20']:.2f} 失守，量能 5 日均 {SH['vol_ratio']:.0f}%。</p>

<h3>创业板指 · {CY['close']:.2f}（{CY['pct']:+.2f}%）</h3>
<img class="chart" src="../charts/399006_SZ_20261117.png" alt="创业板指 2026-11-17 K线">
<p class="chart-caption">开 {CY['open']:.2f} / 高 {CY['high']:.2f} / 低 <b>{CY['low']:.2f}</b> / 收 {CY['close']:.2f}。
<b>最低 {CY_LO60:.2f} = 她的 2263 点，也是新的 60 日低点</b>；收盘较日低拉回 {CY['close']-CY['low']:.2f} 点，
但<b>仍低于 11/16 新低 2308.90</b>；<b>2626 差 {CY_GAP:.2f} 点（{CY_GAP/2626*100:.2f}%）</b>，MA20 {CY['ma20']:.2f} 远在头顶。</p>

<div class="risk">
  <b>⚠️ 她的 2263 点被触及了，但这不是反转。</b>双指数同日创 60 日新低（沪指 {SH_LO60:.2f} / 创业板 {CY_LO60:.2f}），跌停仍有 <b>{ALL['limit_down']} 家</b>（盘中一度只有 40 家，尾盘翻倍），涨 {ALL['up']} / 跌 {ALL['down']}；沪深成交额 {AMT_17:,.0f} 亿、<b>缩量 {abs(AMT_DIFF):,.0f} 亿（{AMT_PCT:+.1f}%）</b>。<b>位置到位 + 缩量 + 跌停未清 = 只能分批、不能满仓</b>。
</div>

<h2>三、最值得关注的 3 个板块</h2>
<table>
<thead><tr><th>板块</th><th>11/17 收盘实测</th><th>博主口径 / 打法</th></tr></thead>
<tbody>
<tr><td><b>① 白酒 / 大消费</b><br><span class="tag tag-bull">首选 · 唯一正收益</span></td>
    <td>池 5 只 <b class="up">{p_wine['up']} 涨 {p_wine['down']} 跌</b>，均值 <b class="up">+{p_wine['avg_pct']:.2f}%</b>，额 {p_wine['amount_yi']:,.0f} 亿<br>
      {mem(p_wine, 2, 1)}</td>
    <td><b>全市场唯一收正的池</b>。茅台收 {MT['close']:.2f}、站上 MA20 {MT['ma20']:.2f}，距 60 日高 {MT['hi60']:.2f} 仅 {MT['hi60']-MT['close']:.2f} 点。<b>只做茅台、不做扩散</b>（避险≠进攻）。</td></tr>
<tr><td><b>② 银行 / 红利</b><br><span class="tag tag-bull">次选 · 尾盘翻红</span></td>
    <td>池 10 只 <b class="up">{p_bank['up']} 涨 {p_bank['down']} 跌 1 平</b>，均值 <b class="up">{p_bank['avg_pct']:+.2f}%</b>，额 {p_bank['amount_yi']:,.0f} 亿<br>
      {mem(p_bank, 2, 1)}</td>
    <td>他 11/16 14:39 点名的方向，<b>今天没有被证伪</b>（盘中一度 9 跌 1 涨，收盘翻红 {p_bank['avg_pct']:.2f}%）。招行 43.45 站上 MA20 42.74，<b>只作底仓垫</b>。</td></tr>
<tr><td><b>③ 军工</b><br><span class="tag tag-neutral">观察 · 池内一枝独秀</span></td>
    <td>池 12 只均值 <b class="down">{p_mil['avg_pct']:+.2f}%</b>（{p_mil['up']} 涨 {p_mil['down']} 跌），额 {p_mil['amount_yi']:,.0f} 亿<br>
      {mem(p_mil, 2, 1)}</td>
    <td>他 11/16 13:55「军工五六只冲板」收盘没兑现、<b>今天补上</b>：中航光电 <b class="up">{ZH['pct']:+.2f}%</b> 放量 {ZH['vol_ratio']:.0f}%。<b>只做池内领涨，不做板块</b>。</td></tr>
</tbody>
</table>
<p class="meta" style="margin-bottom:0">
  <b>回避三个</b>：人形机器人/端侧 <b class="down">{p_rob['avg_pct']:+.2f}%</b>（0 涨 10 跌，宇树 {p_rob['members'][-1]['pct']:+.2f}%）；
  CPO/光通信 <b class="down">{p_cpo['avg_pct']:+.2f}%</b>（0 涨 8 跌）；存储/半导体/GPU <b class="down">{p_st['avg_pct']:+.2f}%</b>（1 涨 7 跌）——
  <b>「杀估值去杠杆」在科技里还没洗完</b>。
  <b>她 13:27「光刻胶表现出色」/ 13:35「超节点+交换机拉起」</b>：涨停池里电子化学 3（西陇科学、江化微、格林达）、IT服务 3、计算机设备 2 —— <b>有涨停但高度分散，未成主线</b>。
  口径：核心标的池收盘涨跌幅（东财快照），与 11/16 收盘口径可比。
</p>

<h2>四、3 支个股</h2>
<table>
<thead><tr><th>代码 名称</th><th class="score">收盘</th><th class="score">涨跌</th>
<th class="score">成交额</th><th>关键位</th><th>实测印证 / 动作</th></tr></thead>
<tbody>
<tr><td><b>002179</b> 中航光电</td><td class="score">{ZH['close']:.2f}</td><td class="score"><span class="up">{ZH['pct']:+.2f}%</span></td>
    <td class="score">{ZH['amount_yi']:.1f} 亿</td><td>MA20 <b>{ZH['ma20']:.2f}</b> · 60 日高 <b>{ZH['hi60']:.2f}</b></td>
    <td class="text"><b>全场最强个股</b>：放量 <b>{ZH['vol_ratio']:.0f}%</b>、收在当日最高 {ZH['high']:.2f} 附近，站上 MA5/MA10/MA20。<b>回踩 MA20 不破可分，冲高不追。</b></td></tr>
<tr><td><b>600519</b> 贵州茅台</td><td class="score">{MT['close']:.2f}</td><td class="score"><span class="up">{MT['pct']:+.2f}%</span></td>
    <td class="score">{MT['amount_yi']:.1f} 亿</td><td>MA20 <b>{MT['ma20']:.2f}</b> · 60 日高 <b>{MT['hi60']:.2f}</b></td>
    <td class="text">唯一正收益池的龙头，逆势收红、站上 MA20 {MT['ma20']:.2f}，量能 {MT['vol_ratio']:.0f}% 未爆量。<b>低吸不追高</b>，破 MA20 放弃。</td></tr>
<tr><td><b>688256</b> 寒武纪</td><td class="score">{HX['close']:.2f}</td><td class="score"><span class="up">{HX['pct']:+.2f}%</span></td>
    <td class="score">{HX['amount_yi']:.1f} 亿</td><td>MA20 <b>{HX['ma20']:.2f}</b> · 60 日高 <b>{HX['hi60']:.2f}</b></td>
    <td class="text">正对她 10:47「高成长+行业向好的科技股走出局部行情」—— <b>存储池 1 涨 7 跌里唯一的红</b>，收盘站上 MA20 {HX['ma20']:.2f}。<b>回踩 MA20 可分批</b>，不追高。</td></tr>
</tbody>
</table>

<h3>中航光电（002179）· {ZH['close']:.2f}（{ZH['pct']:+.2f}%）</h3>
<img class="chart" src="../charts/002179_SZ_20261117.png" alt="中航光电 2026-11-17 K线">
<p class="chart-caption">高 {ZH['high']:.2f} / 低 {ZH['low']:.2f} / 收 {ZH['close']:.2f}，放量阳线站上 MA20 {ZH['ma20']:.2f}；
60 日高 {ZH['hi60']:.2f} 是第一道压制，60 日低 {ZH['lo60']:.2f} 在下方。</p>

<h3>贵州茅台（600519）· {MT['close']:.2f}（{MT['pct']:+.2f}%）</h3>
<img class="chart" src="../charts/600519_SH_20261117.png" alt="贵州茅台 2026-11-17 K线">
<p class="chart-caption">高 {MT['high']:.2f} / 低 {MT['low']:.2f} / 收 {MT['close']:.2f}，逆势小阳；MA20 {MT['ma20']:.2f} 在下方支撑，
60 日高 {MT['hi60']:.2f} 距今 {MT['hi60']-MT['close']:.2f} 点。</p>

<h3>寒武纪（688256）· {HX['close']:.2f}（{HX['pct']:+.2f}%）</h3>
<img class="chart" src="../charts/688256_SH_20261117.png" alt="寒武纪 2026-11-17 K线">
<p class="chart-caption">高 {HX['high']:.2f} / 低 {HX['low']:.2f} / 收 {HX['close']:.2f}，收盘站上 MA20 {HX['ma20']:.2f}；
60 日高 {HX['hi60']:.2f} 在左上（距今 {(HX['hi60']-HX['close'])/HX['close']*100:.1f}%）。</p>

<h2>五、11/18（周三）盯什么（5 条）</h2>
<ul class="tight">
  <li><b>创业板 {CY_LO60:.2f}（她的 2263 点）不破</b> —— 今天已触达，破了则下一目标 2200 整数关。</li>
  <li><b>沪指 60 日新低 {SH_LO60:.2f} 不破</b> —— 破了说明她的「位置」判断还要往下修。</li>
  <li><b>跌停家数从 {ALL['limit_down']} 家回落</b> —— 尾盘比盘中多 60 家，情绪没修复完之前不加仓。</li>
  <li><b>成交额回到 1.6 万亿以上</b> —— 今天 {AMT_17:,.0f} 亿、缩量 {abs(AMT_DIFF):,.0f} 亿；<b>缩量止跌不算止跌</b>。</li>
  <li><b>她给不给 C5 的具体定义</b>（时间/空间/标的）—— 10:07 只说「C5 绝对是机会」，<b>没给买点就还是不能满仓</b>。</li>
</ul>

<h2>六、偏差记录</h2>
<table>
<thead><tr><th>项</th><th>博主口径</th><th>实测 / 处理</th></tr></thead>
<tbody>
<tr><td>14:56「本周 2263 点」<br><span class="tag tag-bull">分毫不差</span></td><td class="text">本周 2263 点可以了，接下来等吃肉了</td>
    <td class="text">创业板指 11/17 最低 <b>{CY_LO60:.2f}</b>，<b>与 2263 点分毫不差</b>；收盘 {CY['close']:.2f} 较日低拉回 {CY['close']-CY['low']:.2f} 点。
    <b>本期最硬的核验</b>——她第一次在 C 杀期间给出可执行点位。</td></tr>
<tr><td>06:07 外盘<br><span class="tag tag-bull">分毫不差</span></td><td class="text">道指跌739点、纳指跌626点、标普跌145点</td>
    <td class="text">11/16 实测 −739.38 / −626.51 / −145.08，<b>分毫不差</b>（外盘播报继续全中）。</td></tr>
<tr><td>13:38 收盘前定性<br><span class="tag tag-bull">成立</span></td><td class="text">抵抗力量是有的，但还未见出现可扭转局面的力量</td>
    <td class="text">涨 {ALL['up']} / 跌 {ALL['down']}，尾盘跌停从盘中 40 家增到 <b>{ALL['limit_down']} 家</b>，
    创业板收盘仍低于 11/16 新低 → <b>有抵抗、无反转</b>，成立。</td></tr>
<tr><td>13:27 / 13:35 板块点名<br><span class="tag tag-neutral">零散未成主线</span></td><td class="text">光刻胶板块今天表现出色点／超节点+交换机，板块出现拉起</td>
    <td class="text">涨停池确有电子化学 3、IT服务 3、计算机设备 2、光学光电 2，<b>但分散在 12+ 行业、最高仅 3 板</b> →
    <b>兑现为零散涨停，不构成主线</b>（与她 13:02「还没有明朗的热点效应」自洽）。</td></tr>
<tr><td>双门槛 3706 / 2626<br><span class="tag tag-neutral">继续搁置</span></td><td class="text">11/17 全天未提门槛，只给 2263 点与 C5 口径</td>
    <td class="text">沪指距 3706 差 <b>{SH_GAP:.2f} 点</b>、创业板距 2626 差 <b>{CY_GAP:.2f} 点</b>。
    <b>门槛没松、新点位出现</b>——她的框架从「等收复 3706/2626」换成「等 C5 完成」，<b>点位体系换了，纪律没换</b>。</td></tr>
</tbody>
</table>
<p class="meta" style="margin-bottom:0">
  其余 <b>3 条口径自洽</b>：11:15「早盘还只是探低之后的抵抗」、13:02「无明朗热点效应」、13:13「没有出现大的力量」——
  实测涨停 {ALL['limit_up']} 只分散、最高 3 板、成交额缩量 {abs(AMT_PCT):.1f}%，均吻合。
  采集：weibo skill 三轮词表补采 → <b>22 条</b>（06:07–14:56）；行情：东方财富日 K（前复权，11/17 收盘）+ 收盘快照全市场宽度。
</p>

<div class="foot">
  <p><b>免责声明</b>：本报告为公开微博内容整理与技术面统计，<b>不构成投资建议</b>；
  「3 板块 + 3 个股」是博主观点 + 实测强度的归纳，不代表推荐。股市有风险，投资需谨慎。</p>
  <p>
    报告生成：2026-11-17 收盘版 · 数据源 weibo skill + 东方财富（+ Tushare Pro 日线底座）·
    脚本 <code>collect_close_20261117.py</code> / <code>build_close_20261117.py</code> /
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
