"""wu2198 投资日报 2026-11-13（周五 · 收盘版 · 精简版）— 线上产物生成器

用法： python3 scripts/gen_wu2198_report_20261113.py
产物： html/wu2198-20261113.html
篇幅： 正文 ≤ 1500 中文字 / 表格 ≤ 4 张（cron 任务硬约束）
"""
import json
from pathlib import Path

ROOT = Path("/Users/maoling/workspace/mnote.github.io")
CH = ROOT / "charts"

KPI = json.loads((CH / "_kpi_20261113.json").read_text(encoding="utf-8"))
SEC = json.loads((CH / "_sectors_20261113.json").read_text(encoding="utf-8"))
BR = json.loads((CH / "_breadth_20261113.json").read_text(encoding="utf-8"))

SH = KPI["000001.SH"]
CY = KPI["399006.SZ"]
b13, b12 = BR["20261113"], BR["20261112"]
p_st, p_cpo, p_rob = SEC["pools"]["存储/半导体/GPU"], SEC["pools"]["CPO/光通信"], SEC["pools"]["人形机器人/端侧"]
p_wine = SEC["pools"]["白酒/大消费"]

TITLE = "wu2198 - 2026-11-13（周五 C杀尾段，分批承接）"

# 关键位距门槛（统一按门槛为分母）
SH_GAP = 3706 - SH["close"]          # 71.65
SH_GAP_HI = 3706 - SH["high"]        # 36.56
CY_GAP = 2626 - CY["close"]          # 199.92
CY_GAP_HI = 2626 - CY["high"]        # 97.01
AMT_DIFF = b12["amount_yi"] - b13["amount_yi"]

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
    <span>🕘 截稿 2026-11-13 23:10（收盘版）</span>
    <span>📡 weibo skill（两轮补采，17 条）</span>
    <span>💹 Tushare Pro 11/13 收盘</span>
  </div>
  <p class="stance">
    <b>🟡 双门槛仍未果，操作口径从「等」改成「分批承接」。</b>
    15:12 定性「<b>ABC 结构调整重的 C 杀尾段</b>……<b>分批承接或坚持为主</b>」；12:24 点名 <b>端侧、机器人、GPU</b>；
    16:12 补「3706 / 2626 <b>收复才有用，才有空间</b>」。
    <b>方向转防守、门槛没松</b> —— 门槛不动前只分批低吸。
  </p>
</div>

<div class="grid-4" style="margin-bottom:8px">
  <div class="kpi"><div class="label">上证指数</div><div class="val">{SH['close']:.2f}</div>
    <div class="sub"><span class="down">{SH['pct']:+.2f}%</span> · 距 <b>3706</b> 差 {SH_GAP:.2f} 点</div></div>
  <div class="kpi"><div class="label">创业板指</div><div class="val">{CY['close']:.2f}</div>
    <div class="sub"><span class="down">{CY['pct']:+.2f}%</span> · 距 <b>2626</b> 差 {CY_GAP:.2f} 点</div></div>
  <div class="kpi"><div class="label">全 A 成交额</div><div class="val">{b13['amount_yi']:,.0f} 亿</div>
    <div class="sub"><span class="vol">缩量 {AMT_DIFF:,.0f} 亿（−14.3%）</span></div></div>
  <div class="kpi"><div class="label">涨跌家数</div><div class="val">{b13['up']} / {b13['down']}</div>
    <div class="sub">涨停 {b13['limit_up']}（昨 {b12['limit_up']}）· <span class="down">跌停 {b13['limit_down']}（昨 {b12['limit_down']}）</span></div></div>
</div>

<h2>一、博主说了什么（8 条）</h2>
<table>
<thead><tr><th>时间</th><th>信号</th><th>原文</th><th>判读 / 日线实测</th></tr></thead>
<tbody>
<tr><td><b>07:03</b></td><td>⚪ 外盘</td><td class="text">道指跌189点、纳指跌100点、标普跌27点</td>
  <td class="text"><b>三个数字分毫不差</b>：11/12 实测 −189.39 / −100.10 / −26.98。</td></tr>
<tr><td><b>10:38</b></td><td>🟢 板块点名</td><td class="text">端侧板块再度拉起，行业+技术趋势完美无缺！</td>
  <td class="text"><b>收盘未兑现</b>：端侧池 8 跌、均值 <b>−1.31%</b>。</td></tr>
<tr><td><b>10:45</b></td><td>🟢 纪律</td><td class="text">只适合低位分批布局，不要去追。能做到这点，起码赢80%的投资者</td>
  <td class="text"><b>最可执行一条</b>：只给方向不给买点，规则先行。</td></tr>
<tr><td><b>10:48</b></td><td>⚪ 外盘</td><td class="text">日股上涨997点，韩国上涨1.1%</td>
  <td class="text">盘中口径：日经收 61142.35（<b>+0.53%</b>），韩国收 5290.53（<b>−0.98%</b>）。</td></tr>
<tr><td><b>11:24</b></td><td>🔴 拖累定性</td><td class="text">CPO，存储芯片，继续拖累指数！</td>
  <td class="text"><b>当天兑现</b>：CPO 池 <b>8/8 全跌、均值 −7.87%</b>（源杰 −11.76%）；存储池 −3.75%。</td></tr>
<tr><td><b>12:24</b></td><td>🟢🟢 结构+主线</td><td class="text">C3低点会有一批股提前见底。如端侧、人形机器人、GPU等……C3之后分批布局</td>
  <td class="text"><b>本期核心</b>：点名 <b>端侧 / 机器人 / GPU</b>，但三者 11/13 全收跌。</td></tr>
<tr><td><b>12:37</b></td><td>🟢 催化+目标位</td><td class="text">借利空扫货英伟达（试了148.8美元，收在166.19美元）……等待反弹到200美元</td>
  <td class="text"><b>核实通过</b>：11/12 NVDA 收 <b>166.19</b> 一致；11/13 11:31 报 160.35（−3.52%），距目标位差 24.8%。</td></tr>
<tr><td><b>15:12 / 16:12</b></td><td>🟡 收盘定调</td><td class="text">市场属于ABC结构调整重的C杀尾段，策略偏向分批承接 / 3706、2626 点收复才有用才有空间，不要断章取义！</td>
  <td class="text"><b>两句必须连读</b>：15:12 给方向，16:12 收回买点 → <b>方向转防守、门槛不松</b>，不是「现在可以买」。</td></tr>
</tbody>
</table>

<h2>二、大盘关键点位</h2>
<p class="meta" style="margin-bottom:6px">K 线<b>红涨绿跌</b>（按收 vs 开着色）；关键位在图<b>左侧虚线</b>。</p>

<h3>上证指数 · {SH['close']:.2f}（{SH['pct']:+.2f}%）</h3>
<img class="chart" src="../charts/000001_SH_20261113.png" alt="上证指数 2026-11-13 K线">
<p class="chart-caption">开 {SH['open']:.2f} / 高 <b>{SH['high']:.2f}</b> / 低 {SH['low']:.2f} / 收 {SH['close']:.2f}，高开低走。
<b>3706 差 {SH_GAP:.2f} 点（{SH_GAP/3706*100:.2f}%）</b>，日内最高也只差 {SH_GAP_HI:.2f} 点；
收盘失守 MA20 {SH['ma20']:.2f}，MACD 柱 <b>+{SH['macd_bar']:.2f}</b>（仍在零轴下）。</p>

<h3>创业板指 · {CY['close']:.2f}（{CY['pct']:+.2f}%）</h3>
<img class="chart" src="../charts/399006_SZ_20261113.png" alt="创业板指 2026-11-13 K线">
<p class="chart-caption">开 {CY['open']:.2f} / 高 <b>{CY['high']:.2f}</b> / 低 {CY['low']:.2f} / 收 {CY['close']:.2f}。
<b>2626 差 {CY_GAP:.2f} 点（{CY_GAP/2626*100:.2f}%）</b>，收盘距 60 日低 2376.28 仅 2.1%；MA20 {CY['ma20']:.2f} 失守。</p>

<div class="risk">
  <b>⚠️ 今天最该看的是跌停家数，不是成交额。</b>成交额缩到 <b>{b13['amount_yi']:,.0f} 亿</b>（−14.3%），
  但<b>跌停从 19 家增到 {b13['limit_down']} 家（4.3 倍）</b>，跌家数 4748 家（85%）。
  缩量 + 跌停激增 = <b>动能衰减但流动性枯竭</b> → <b>反弹要放量才确认</b>。
</div>

<h2>三、最值得关注的 3 个板块</h2>
<table>
<thead><tr><th>板块</th><th>11/13 收盘实测</th><th>博主口径 / 打法</th></tr></thead>
<tbody>
<tr><td><b>① GPU / 国产算力</b><br><span class="tag tag-bull">首选 · 唯一逆势</span></td>
    <td>池 8 只均值 <b>−3.75%</b>，但<b>寒武纪 +0.60%、海光 +0.46% 唯二上涨</b></td>
    <td>12:24 点名 + 12:37 英伟达催化（<b>等反弹到 200 美元</b>）。<b>只做龙头</b>：寒武纪站上 MA20 893.98，PE 147.65 偏高，回踩不破才加。</td></tr>
<tr><td><b>② 人形机器人</b><br><span class="tag tag-neutral">次选 · 跌幅最小</span></td>
    <td>池 8 跌、均值 <b>−1.31%</b>（科技方向里跌幅最小）；汇川 +0.64%；宇树 −0.70%，量缩至 5 日均 63%</td>
    <td>12:24 点名。<b>缩量回调</b>，宇树 MA20 645.83 是分批位，距 60 日高 1100 已 −36.7%。</td></tr>
<tr><td><b>③ 端侧 AI</b><br><span class="tag tag-neutral">观察 · 未兑现</span></td>
    <td>瑞芯微 <b>−1.32%</b>（曾冲 228.00 后回落）、芯原 −3.64%</td>
    <td>10:38 唯一盘中点名板块。<b>收盘未兑现，等次日验证</b>；PE 57.90 不低，MA20 202.94 之下不接。</td></tr>
</tbody>
</table>
<p class="meta" style="margin-bottom:0">
  <b>回避两个</b>：CPO/光通信 8 只<b>全跌</b>、均值 <b>−7.87%</b>（他 11:24 已定性拖累）；存储芯片 −3.75%。
  <b>另需注意</b>：唯一逆势的是<b>白酒/大消费 5/5 全涨、均值 +3.16%</b>（古井 +5.86%），
  与他 11/08「白酒+大消费泡沫」警示相反 —— 避险轮动，<b>本期不列入前三</b>。
  口径：核心标的池 + 东财涨停池行业分布（push2 限流），与 11/12 可比。
</p>

<h2>四、3 支个股</h2>
<table>
<thead><tr><th>代码 名称</th><th class="score">收盘</th><th class="score">涨跌</th>
<th class="score">成交额</th><th>关键位</th><th>实测印证 / 动作</th></tr></thead>
<tbody>
<tr><td><b>688256</b> 寒武纪</td><td class="score">978.88</td><td class="score"><span class="up">+0.60%</span></td>
    <td class="score">160.4 亿</td><td>MA20 <b>893.98</b> · 60 日高 <b>1170</b></td>
    <td class="text">大盘 −0.59% 下逆势收红，MACD 柱 <b>+34.86</b>、量能 115%；距 60 日低 750.01 已 +30.5%。<b>PE 147.65 偏高</b>，回踩 MA20 不破才加。</td></tr>
<tr><td><b>688836</b> 宇树科技</td><td class="score">696.00</td><td class="score"><span class="down">−0.70%</span></td>
    <td class="score">28.7 亿</td><td>MA20 <b>645.83</b> · 60 日高 <b>1100</b></td>
    <td class="text">机器人池跌幅小、<b>缩量</b>（5 日均 63%），MACD 柱 +12.64 仍正；距 60 日低 404.03 已 +72%。<b>MA20 645.83 分批，不追。</b></td></tr>
<tr><td><b>603893</b> 瑞芯微</td><td class="score">217.80</td><td class="score"><span class="down">−1.32%</span></td>
    <td class="score">36.1 亿</td><td>MA20 <b>202.94</b> · 60 日高 <b>237.37</b></td>
    <td class="text">10:38 冲 228.00 后回落，<b>收盘未兑现他的「趋势完美无缺」</b>；量能仅 5 日均 92%。<b>破 MA20 202.94 不接。</b></td></tr>
</tbody>
</table>

<h3>寒武纪（688256）· 978.88（+0.60%）</h3>
<img class="chart" src="../charts/688256_SH_20261113.png" alt="寒武纪 2026-11-13 K线">
<p class="chart-caption">高 1033.18 / 低 968.01 / 收 978.88，站上 MA20 893.98；60 日低 750.01 在左下、60 日高 1170 在左上（距今 −16.3%）。</p>

<h3>宇树科技（688836）· 696.00（−0.70%）</h3>
<img class="chart" src="../charts/688836_SH_20261113.png" alt="宇树科技 2026-11-13 K线">
<p class="chart-caption">高 718.70 / 低 689.20 / 收 696.00，缩量小阴线；MA20 645.83 在下方，60 日高 1100 是头顶压制。</p>

<h3>瑞芯微（603893）· 217.80（−1.32%）</h3>
<img class="chart" src="../charts/603893_SH_20261113.png" alt="瑞芯微 2026-11-13 K线">
<p class="chart-caption">高 228.00 / 低 215.65 / 收 217.80，冲高回落收在 MA5 223.75 之下；60 日高 237.37、60 日低 159.34 在两端。</p>

<h2>五、11/16（周一）盯什么（5 条）</h2>
<ul class="tight">
  <li><b>双门槛：沪指 3706 + 创业板 2626</b> —— 还差 {SH_GAP:.2f} / {CY_GAP:.2f} 点，<b>只到沪指不算</b>（16:12 明确「收复才有用」）。</li>
  <li><b>跌停从 {b13['limit_down']} 家回落到 30 家以内</b> —— 今天 19→{b13['limit_down']}，情绪没修复不追板块。</li>
  <li><b>创业板 2417.22 低点不破</b> —— 破了则 C 杀未结束，60 日低 2376.28 成下一目标。</li>
  <li><b>成交额回到 2 万亿以上</b> —— 今天缩量 {AMT_DIFF:,.0f} 亿至 {b13['amount_yi']:,.0f} 亿，缩量反弹不算反弹。</li>
  <li><b>存储 / GPU 池均值转正 + CPO 池止跌</b> —— 他 11:24 点名的两个拖累方向不企稳，指数就上不去。</li>
</ul>

<h2>六、偏差记录</h2>
<table>
<thead><tr><th>项</th><th>博主口径</th><th>实测 / 处理</th></tr></thead>
<tbody>
<tr><td>10:38 端侧<br><span class="tag tag-bear">收盘未兑现</span></td><td class="text">端侧再度拉起，趋势完美无缺</td>
    <td class="text">收盘端侧池 <b>8/10 下跌、均值 −1.31%</b>。<b>盘中口径日线核不出，需次日验证。</b></td></tr>
<tr><td>10:48 韩国<br><span class="tag tag-bear">方向相反</span></td><td class="text">韩国股市上涨1.1%</td>
    <td class="text">KS11 收 <b>5290.53、−0.98%</b>（翻绿）；日经 +0.53%（+323 点，非 997 点）。</td></tr>
<tr><td>15:12 vs 16:12<br><span class="tag tag-neutral">自相约束</span></td><td class="text">分批承接 / 收复才有用，不要断章取义</td>
    <td class="text"><b>他给读者打的补丁</b>：方向转防守是真的，<b>买点没松</b>。门槛未收复前，分批 = 只买低位、不追高、控仓。</td></tr>
<tr><td>白酒逆势<br><span class="tag tag-neutral">与旧警示冲突</span></td><td class="text">（11/13 未提白酒）</td>
    <td class="text">白酒/大消费 <b>5/5 全涨、均值 +3.16%</b>，与其 11/08「白酒+大消费泡沫」警示相反；涨停池集中在汽车零部 6、影视院线 5。<b>不推荐</b>。</td></tr>
<tr><td>周线定性<br><span class="tag tag-neutral">需降级</span></td><td class="text">C3 低点会有一批股提前见底</td>
    <td class="text">周线 MACD 上证 DIF −86.06 / DEA −57.26、创业板 DIF −274.67 / DEA −154.51：<b>柱收窄但 DIF/DEA 双双在零轴下方下行</b> → 底部成立、<b>反转未确认</b>。</td></tr>
</tbody>
</table>
<p class="meta" style="margin-bottom:0">
  其余 <b>4 条核实通过</b>：外盘三数字、CPO+存储拖累、英伟达 166.19 美元、双门槛点位。
  采集：两轮词表补采 → 17 条（07:03–22:52）；行情：Tushare Pro 11/13 收盘。
</p>

<div class="foot">
  <p><b>免责声明</b>：本报告为公开微博内容整理与技术面统计，<b>不构成投资建议</b>；
  「3 板块 + 3 个股」是博主观点 + 实测强度的归纳，不代表推荐。股市有风险，投资需谨慎。</p>
  <p>
    报告生成：2026-11-13 收盘版 · 数据源 weibo skill + Tushare Pro + 东方财富 ·
    脚本 <code>make_wu2198_charts_20261113.py</code> / <code>gen_wu2198_report_20261113.py</code> / <code>collect_daily_20261113.py</code>。
  </p>
</div>

</div>
</body>
</html>
"""

if __name__ == "__main__":
    out = ROOT / "html" / "wu2198-20261113.html"
    out.write_text(HTML, encoding="utf-8")
    print(f"[out] {out}  ({len(HTML)} bytes)")
