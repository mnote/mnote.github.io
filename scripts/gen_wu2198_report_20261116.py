"""wu2198 投资日报 2026-11-16（周一 · 收盘版）— 线上产物生成器

用法： python3 scripts/gen_wu2198_report_20261116.py
产物： html/wu2198-20261116.html
篇幅： 正文 ≤ 2000 中文字 / 表格 ≤ 4 张（cron 任务硬约束）
"""
import json
import sys
from pathlib import Path

ROOT = Path("/Users/maoling/workspace/mnote.github.io")
CH = ROOT / "charts"

KPI = json.loads((CH / "_kpi_20261116.json").read_text(encoding="utf-8"))
SEC = json.loads((CH / "_sectors_20261116.json").read_text(encoding="utf-8"))
BR = json.loads((CH / "_breadth_20261116.json").read_text(encoding="utf-8"))

SH, CY = KPI["000001.SH"], KPI["399006.SZ"]
BK, MB, RB, CYB = KPI["600036.SH"], KPI["600519.SH"], KPI["300442.SZ"], KPI["399006.SZ"]
b16, b13 = BR["20261116"], BR["20261113"]

P = SEC["pools"]
p_bank, p_wine, p_calc = P["银行/红利"], P["白酒/大消费"], P["算力租赁/IDC"]
p_cpo, p_st, p_rob = P["CPO/光通信"], P["存储/半导体/GPU"], P["人形机器人/端侧"]
p_mil = P["军工"]

TITLE = "wu2198 - 2026-11-16（周一 跌停潮起，只点名银行）"

SH_GAP = 3706 - SH["close"]            # 103.43
CY_GAP = 2626 - CY["close"]            # 305.98
SH_GAP_P = SH_GAP / 3706 * 100
CY_GAP_P = CY_GAP / 2626 * 100
AMT_DIFF = b13["amount_yi"] - b16["amount_yi"]
AMT_PCT = AMT_DIFF / b13["amount_yi"] * 100
SH_LO60 = 3574.27
SH_GAP_LO60 = SH["close"] - SH_LO60

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
    <span>🕘 截稿 2026-11-16 22:45（收盘版）</span>
    <span>📡 weibo skill（三轮词表补采，13 条）</span>
    <span>💹 Tushare Pro 11/16 收盘</span>
  </div>
  <p class="stance">
    <b>🟡 全天没有新买点 —— 13 条帖子里只有 2 条点名板块，其余是情绪安抚与事后归因。</b>
    10:31 回顾旧账（4256 撤离 / 4380 三川顶 / 第四大浪 ABC），12:53 唯一催化（DeepSeek 限额 → 算力租赁），
    14:39 唯一避险点名（银行股「唯一没有受这轮调整影响」），21:03 把跌停潮归为「泡沫破灭之后的事情」。
    <b>双门槛 3706 / 2626 全天未提</b>（沪指已差 {SH_GAP:.2f} 点、创业板差 {CY_GAP:.2f} 点）——
    门槛不是被突破，是<b>被搁置</b>。<b>只做银行 + 白酒，算力租赁先看不接。</b>
  </p>
</div>

<div class="grid-4" style="margin-bottom:8px">
  <div class="kpi"><div class="label">上证指数</div><div class="val">{SH['close']:.2f}</div>
    <div class="sub"><span class="down">{SH['pct']:+.2f}%</span> · 距 <b>3706</b> 差 {SH_GAP:.2f} 点</div></div>
  <div class="kpi"><div class="label">创业板指</div><div class="val">{CY['close']:.2f}</div>
    <div class="sub"><span class="down">{CY['pct']:+.2f}%</span> · 距 <b>2626</b> 差 {CY_GAP:.2f} 点</div></div>
  <div class="kpi"><div class="label">全 A 成交额</div><div class="val">{b16['amount_yi']:,.0f} 亿</div>
    <div class="sub"><span class="vol">缩量 {AMT_DIFF:,.0f} 亿（−{AMT_PCT:.1f}%）</span></div></div>
  <div class="kpi"><div class="label">涨跌家数</div><div class="val">{b16['up']} / {b16['down']}</div>
    <div class="sub">涨停 {b16['limit_up']}（昨 {b13['limit_up']}）· <span class="down">跌停 {b16['limit_down']}（昨 {b13['limit_down']}）</span></div></div>
</div>

<h2>一、博主说了什么（8 条）</h2>
<table>
<thead><tr><th>时间</th><th>信号</th><th>原文</th><th>判读 / 日线实测</th></tr></thead>
<tbody>
<tr><td><b>10:31</b></td><td>⚪ 旧账重宣</td><td class="text">4256 撤离本金和一半盈利、4380 后构筑三川顶、提示科技股泡沫、第四大浪 ABC 调整</td>
  <td class="text"><b>全是 6-7 月旧结论，本期无新增仓位/买点信息</b>。互动 1.46 万，是全日第一热帖。</td></tr>
<tr><td><b>12:53</b></td><td>🟢 板块点名 + 催化</td><td class="text">#DeepSeek因算力不足限额# 利好算力，算力租赁！</td>
  <td class="text"><b>全天唯一具名机会帖</b>。实测算力租赁池 <b>8/8 全跌、均值 −4.34%</b>，龙头润泽科技 <b>−9.87% 跌停</b> → <b>当日未兑现</b>。</td></tr>
<tr><td><b>14:28</b></td><td>🟡 幅度统计</td><td class="text">创业板自 4380 到今天 2314，跌 2066 点，跌幅 47.16%</td>
  <td class="text"><b>数字分毫不差</b>：(4380−2314)/4380 = 47.17%。2314 为 14:28 盘中值。</td></tr>
<tr><td><b>14:39</b></td><td>🟢🟢 板块点名</td><td class="text">以四大行和优质城商行为代表的银行股板块，是唯一没有受这轮大盘调整影响的板块</td>
  <td class="text"><b>核验通过且是全市场最强方向</b>：银行池 <b>10/10 全涨、均值 +1.97%</b>（浦发 +3.65%、农行 +2.99%）。</td></tr>
<tr><td><b>14:47</b></td><td>🟡 底部反问</td><td class="text">创业板自 4380 到今天 2308，跌 2072 点，跌幅 47.30%。股市不是跌出机会吗？</td>
  <td class="text">数字对：(4380−2308)/4380 = 47.31%。<b>是反问不是断言</b>，不等于「买」。当日创业板最低 2308.90 正是 <b>60 日新低</b>。</td></tr>
<tr><td><b>14:51</b></td><td>🟡 计数</td><td class="text">这次时间跨度比之前的大些，今天已经第 9 个交易了</td>
  <td class="text"><b>核验通过</b>：自 11/04 创业板见低 2376.28 起算，11/04-06、07、10、11、12、13、16 = <b>9 个交易日</b>。</td></tr>
<tr><td><b>14:58</b></td><td>⚪ 情绪</td><td class="text">今天不用评论，能互相安慰的都是好老铁！</td>
  <td class="text"><b>当日互动第一（2.05 万）</b>，纯情绪帖，<b>无操作信息</b>。</td></tr>
<tr><td><b>21:03</b></td><td>🟡 事后归因</td><td class="text">#科技股现跌停潮不少股民爆仓# 这是泡沫破灭之后的事情！</td>
  <td class="text"><b>核验通过</b>：收盘跌停 <b>{b16['limit_down']} 家</b>（11/13 是 {b13['limit_down']}、11/12 是 19），三日 <b>9 倍</b>。定性=事后解释，<b>不含前瞻信号</b>。</td></tr>
</tbody>
</table>

<h2>二、大盘关键点位</h2>
<p class="meta" style="margin-bottom:6px">K 线<b>红涨绿跌</b>（按收 vs 开着色）；关键位在图<b>左侧虚线</b>。</p>

<h3>上证指数 · {SH['close']:.2f}（{SH['pct']:+.2f}%）</h3>
<img class="chart" src="../charts/000001_SH_20261116.png" alt="上证指数 2026-11-16 K线">
<p class="chart-caption">开 {SH['open']:.2f} / 高 <b>{SH['high']:.2f}</b> / 低 {SH['low']:.2f} / 收 {SH['close']:.2f}，低开低走。
<b>3706 差 {SH_GAP:.2f} 点（{SH_GAP_P:.2f}%）</b>，连日内最高也差 {3706-SH['high']:.2f} 点；
距 60 日低 {SH_LO60:.2f} 只剩 <b>{SH_GAP_LO60:.2f} 点（{SH_GAP_LO60/SH_LO60*100:.2f}%）</b>，MA20 {SH['ma20']:.2f} 失守。</p>

<h3>创业板指 · {CY['close']:.2f}（{CY['pct']:+.2f}%）</h3>
<img class="chart" src="../charts/399006_SZ_20261116.png" alt="创业板指 2026-11-16 K线">
<p class="chart-caption">开 {CY['open']:.2f} / 高 <b>{CY['high']:.2f}</b> / 低 <b>{CY['low']:.2f}</b> / 收 {CY['close']:.2f}。
<b>2626 差 {CY_GAP:.2f} 点（{CY_GAP_P:.2f}%）</b>；最低 {CY['low']:.2f} <b>就是 60 日新低</b>，前低 2376.28 已破；
MACD 柱 <b>{CY['macd_bar']:.2f}</b>、DIF {CY['dif']:.1f} / DEA {CY['dea']:.1f} 双双在零轴下方。</p>

<div class="risk">
  <b>⚠️ 今天最该看的不是成交额，是跌停家数。</b>成交额缩到 <b>{b16['amount_yi']:,.0f} 亿</b>（−{AMT_PCT:.1f}%），
  但<b>跌停从 {b13['limit_down']} 家增到 {b16['limit_down']} 家</b>，跌家数 {b16['down']} 家（占 {b16['down']/(b16['up']+b16['down']+b16['flat'])*100:.0f}%），
  创业板 <b>创 60 日新低</b>。缩量 + 跌停翻倍 = <b>流动性枯竭，不是缩量调整</b>。
</div>

<h2>三、最值得关注的 3 个板块</h2>
<table>
<thead><tr><th>板块</th><th>11/16 收盘实测</th><th>博主口径 / 打法</th></tr></thead>
<tbody>
<tr><td><b>① 银行 / 红利</b><br><span class="tag tag-bull">首选 · 全市场最强</span></td>
    <td>池 10 只 <b>10 涨 0 跌</b>，均值 <b class="up">+{p_bank['avg_pct']:.2f}%</b>，额 {p_bank['amount_yi']:,.0f} 亿<br>
      浦发 +3.65%、农行 +2.99%、工行 +2.26%</td>
    <td>14:39 唯一避险点名，<b>核验通过</b>。<b>只做龙头、只做防守</b>：招行站上 MA20 {BK['ma20']:.2f}，量比 {BK['vol_ratio']:.0f}% 放量，60 日高 {BK['hi60']:.2f} 只差 {BK['hi60']-BK['close']:.2f} 点。</td></tr>
<tr><td><b>② 白酒 / 大消费</b><br><span class="tag tag-bull">次选 · 防御轮动</span></td>
    <td>池 5 只 <b>5 涨 0 跌</b>，均值 <b class="up">+{p_wine['avg_pct']:.2f}%</b>，额 {p_wine['amount_yi']:,.0f} 亿<br>
      茅台 +1.30%、汾酒 +1.20%、老窖 +1.04%</td>
    <td><b>与他 11/08「白酒+大消费泡沫」警示相反</b> —— 避险轮动，不是新主线。<b>只做茅台、不做扩散</b>：收 {MB['close']:.2f} 站上 MA20 {MB['ma20']:.2f}，距 60 日高 {MB['hi60']:.2f} 仅 {MB['hi60']-MB['close']:.2f} 点。</td></tr>
<tr><td><b>③ 算力租赁 / IDC</b><br><span class="tag tag-neutral">观察位 · 当日未兑现</span></td>
    <td>池 8 只 <b>8 跌 0 涨</b>，均值 <b class="down">{p_calc['avg_pct']:.2f}%</b>，额 {p_calc['amount_yi']:,.0f} 亿<br>
      润泽科技 <b class="down">−9.87%</b>（跌停）、首都在线 −4.96%</td>
    <td>12:53 唯一具名催化（DeepSeek 限额）—— <b>催化是真的，方向没走出来</b>。<b>不接</b>：等龙头站回 MA20 {RB['ma20']:.2f}、跌停打开再谈。</td></tr>
</tbody>
</table>
<p class="meta" style="margin-bottom:0">
  <b>回避两个</b>：CPO/光通信 8 只<b>全跌</b>、均值 <b class="down">{p_cpo['avg_pct']:.2f}%</b>；存储/半导体/GPU 8 只<b>全跌</b>、均值 <b class="down">{p_st['avg_pct']:.2f}%</b>（他 11/13 点名的方向今天继续被砍）。
  <b>军工</b> {p_mil['avg_pct']:+.2f}%、<b>人形机器人/端侧</b> {p_rob['avg_pct']:+.2f}%（宇树 +1.15% 是池里唯一上涨）。口径：核心标的池收盘涨跌幅，与 11/13 可比。
</p>

<h2>四、3 支个股</h2>
<table>
<thead><tr><th>代码 名称</th><th class="score">收盘</th><th class="score">涨跌</th>
<th class="score">成交额</th><th>关键位</th><th>实测印证 / 动作</th></tr></thead>
<tbody>
<tr><td><b>600036</b> 招商银行</td><td class="score">{BK['close']:.2f}</td><td class="score"><span class="up">{BK['pct']:+.2f}%</span></td>
    <td class="score">37.4 亿</td><td>MA20 <b>{BK['ma20']:.2f}</b> · 60 日高 <b>{BK['hi60']:.2f}</b></td>
    <td class="text">大盘 −0.87% 下放量收红，量比 <b>{BK['vol_ratio']:.0f}%</b>；MACD <b>零轴上方死叉</b>（柱 {BK['macd_bar']:.2f}，DIF {BK['dif']:.2f} < DEA {BK['dea']:.2f}）= 强势回调。<b>可分批</b>，MA20 {BK['ma20']:.2f} 不破才加，破则走。</td></tr>
<tr><td><b>600519</b> 贵州茅台</td><td class="score">{MB['close']:.2f}</td><td class="score"><span class="up">{MB['pct']:+.2f}%</span></td>
    <td class="score">57.7 亿</td><td>MA20 <b>{MB['ma20']:.2f}</b> · 60 日高 <b>{MB['hi60']:.2f}</b></td>
    <td class="text">全市场仅此一池逆势（5/5 全涨）；量比 {MB['vol_ratio']:.0f}%，距 60 日高仅 {MB['hi60']-MB['close']:.2f} 点。<b>低吸不追高</b>，MA20 {MB['ma20']:.2f} 是防守位。</td></tr>
<tr><td><b>300442</b> 润泽科技</td><td class="score">{RB['close']:.2f}</td><td class="score"><span class="down">{RB['pct']:+.2f}%</span></td>
    <td class="score">14.8 亿</td><td>MA20 <b>{RB['ma20']:.2f}</b> · 60 日低 <b>{RB['lo60']:.2f}</b></td>
    <td class="text">博主 12:53 唯一催化方向的龙头，<b>今日跌停</b>，已破 MA20 {RB['ma20']:.2f}；60 日低 {RB['lo60']:.2f} 只差 {(RB['close']-RB['lo60'])/RB['close']*100:.1f}%。<b>观察不接</b>，站回 MA20 再看。</td></tr>
</tbody>
</table>

<h3>招商银行（600036）· {BK['close']:.2f}（{BK['pct']:+.2f}%）</h3>
<img class="chart" src="../charts/600036_SH_20261116.png" alt="招商银行 2026-11-16 K线">
<p class="chart-caption">高 {BK['high']:.2f} / 低 {BK['low']:.2f} / 收 {BK['close']:.2f}，放量小阳线站上 MA20 {BK['ma20']:.2f}；60 日高 {BK['hi60']:.2f} 是头顶第一道压制。</p>

<h3>贵州茅台（600519）· {MB['close']:.2f}（{MB['pct']:+.2f}%）</h3>
<img class="chart" src="../charts/600519_SH_20261116.png" alt="贵州茅台 2026-11-16 K线">
<p class="chart-caption">高 {MB['high']:.2f} / 低 {MB['low']:.2f} / 收 {MB['close']:.2f}，逆势收红；MA20 {MB['ma20']:.2f} 在下方支撑，60 日高 {MB['hi60']:.2f} 距今 {MB['hi60']-MB['close']:.2f} 点。</p>

<h3>润泽科技（300442）· {RB['close']:.2f}（{RB['pct']:+.2f}%）</h3>
<img class="chart" src="../charts/300442_SZ_20261116.png" alt="润泽科技 2026-11-16 K线">
<p class="chart-caption">开 {RB['open']:.2f} / 高 {RB['high']:.2f} / 低 {RB['low']:.2f} / 收 {RB['close']:.2f}，<b>跌停收盘</b>；MA5 {RB['ma5']:.2f}、MA20 {RB['ma20']:.2f} 全在头上，60 日低 {RB['lo60']:.2f} 只差 {(RB['close']-RB['lo60'])/RB['close']*100:.1f}%。</p>

<h2>五、11/17（周二）盯什么（5 条）</h2>
<ul class="tight">
  <li><b>跌停家数从 {b16['limit_down']} 家回落到 50 家以内</b> —— 今天 {b13['limit_down']}→{b16['limit_down']} 翻倍，情绪没修复不碰科技。</li>
  <li><b>创业板 2308.90（60 日新低）不破</b> —— 破了则下看 2200；守住才有反弹结构。</li>
  <li><b>银行池继续全红</b> —— 今天 10/10 +1.97%。<b>银行若翻绿，避险逻辑破产，说明是普跌不是切换</b>。</li>
  <li><b>润泽科技站回 MA20 {RB['ma20']:.2f} + 跌停打开</b> —— 这是他 12:53 唯一催化是否兑现的标志，兑现才谈算力租赁。</li>
  <li><b>博主是否给出新门槛或买点</b> —— 11/16 全天没给；她不给之前，<b>只按 11/13 的「低位分批、不追高、控仓」执行</b>。</li>
</ul>

<h2>六、偏差记录</h2>
<table>
<thead><tr><th>项</th><th>博主口径</th><th>实测 / 处理</th></tr></thead>
<tbody>
<tr><td>双门槛 3706 / 2626<br><span class="tag tag-bear">状态变化</span></td><td class="text">全天未提（11/13 还在强调「收复才有用」）</td>
    <td class="text">沪指已差 <b>{SH_GAP:.2f} 点（{SH_GAP_P:.2f}%）</b>、创业板差 <b>{CY_GAP:.2f} 点（{CY_GAP_P:.2f}%）</b>。
    <b>门槛不是被突破，是被搁置</b> —— 别读成「他放弃了纪律」，也别读成「门槛自动作废」。</td></tr>
<tr><td>12:53 算力租赁<br><span class="tag tag-bear">当日未兑现</span></td><td class="text">#DeepSeek因算力不足限额# 利好算力，算力租赁！</td>
    <td class="text">算力租赁池 <b>8/8 全跌、均值 −4.34%</b>，润泽科技 <b class="down">−9.87%</b> 跌停。催化真实但当日被大盘压过 → <b>降级为观察位</b>。</td></tr>
<tr><td>14:39「唯一」<br><span class="tag tag-neutral">不完全成立</span></td><td class="text">银行股是唯一没有受这轮大盘调整影响的板块</td>
    <td class="text">银行 <b>+1.97%</b> 确实是第一，<b>但白酒/大消费 5/5 全涨 +0.92% 同样未受影响</b> → 「唯一」不严谨，避险面比他说得宽。</td></tr>
<tr><td>10:31 长文<br><span class="tag tag-neutral">旧账重宣</span></td><td class="text">4256 撤离 / 4380 三川顶 / 第四大浪 ABC</td>
    <td class="text">全部是 6-7 月旧结论，<b>本期无新增买点</b>。当日互动第一（1.46 万）说明关注度在「情绪」不在「操作」。</td></tr>
<tr><td>口径相比 11/13<br><span class="tag tag-neutral">明显后退</span></td><td class="text">11/13：C 杀尾段、分批承接</td>
    <td class="text">11/16 连「分批承接」都没再提，改为「互相安慰」「洗洗睡了」。<b>操作口径从「分批接」退回「等」</b>，本期不给方向。</td></tr>
</tbody>
</table>
<p class="meta" style="margin-bottom:0">
  其余 <b>4 条核实通过</b>：14:39 银行、14:28/14:47 跌幅数字、14:51 第 9 个交易日、21:03 跌停潮。
  采集：weibo skill 三轮词表补采 → 13 条（10:31–21:59）；行情：Tushare Pro 11/16 收盘。
</p>

<div class="foot">
  <p><b>免责声明</b>：本报告为公开微博内容整理与技术面统计，<b>不构成投资建议</b>；
  「3 板块 + 3 个股」是博主观点 + 实测强度的归纳，不代表推荐。股市有风险，投资需谨慎。</p>
  <p>
    报告生成：2026-11-16 收盘版 · 数据源 weibo skill + Tushare Pro + 东方财富 ·
    脚本 <code>collect_daily_20261116.py</code> / <code>collect_extra_20261116.py</code> /
    <code>make_wu2198_charts_20261116.py</code> / <code>gen_wu2198_report_20261116.py</code>。
  </p>
</div>

</div>
</body>
</html>
"""

# 表格移动端适配（横向滚动 + 溢出提示）：统一由 fix_mobile_tables 注入
sys.path.insert(0, str(Path(__file__).resolve().parent))
from fix_mobile_tables import patch_html

if __name__ == "__main__":
    out = ROOT / "html" / "wu2198-20261116.html"
    out.write_text(patch_html(HTML), encoding="utf-8")
    print(f"[out] {out}  ({len(HTML)} bytes)")
