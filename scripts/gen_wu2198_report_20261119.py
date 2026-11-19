"""wu2198 投资日报 2026-11-19（周四 · 收盘版）— 线上产物生成器

用法： python3 scripts/gen_wu2198_report_20261119.py
产物： html/wu2198-20261119.html
行情口径：Tushare Pro 日线（pro.daily / pro.index_daily + adj_factor 前复权）
篇幅： 正文 ≤ 2000 中文字 / 表格 ≤ 4 张
"""
import json
import sys
from pathlib import Path

ROOT = Path("/Users/maoling/workspace/mnote.github.io")
CH = ROOT / "charts"

KPI = json.loads((CH / "_kpic_20261119.json").read_text(encoding="utf-8"))
TS = json.loads((CH / "_ts_20261119.json").read_text(encoding="utf-8"))
POOLS = json.loads((CH / "_pools_20261119.json").read_text(encoding="utf-8"))
MKT = json.loads((CH / "_mkt_20261119.json").read_text(encoding="utf-8"))

SH, CY = KPI["000001.SH"], KPI["399006.SZ"]
ZW, XY, HG = KPI["688012.SH"], KPI["300502.SZ"], KPI["688041.SH"]
SY = TS["stocks"]["688801.SH"]
SN = TS["stocks"]["002916.SZ"]
MT = TS["stocks"]["600519.SH"]
YB = TS["stocks"]["600036.SH"]
ZX = TS["stocks"]["688825.SH"]
P = POOLS["pools"]
B = MKT["days"]["20261119"]
B18 = MKT["days"]["20261118"]

p_eq, p_liq, p_pkg = P["半导体设备"], P["光刻胶/材料"], P["先进封装"]
p_cpo, p_sw, p_idc = P["CPO/光通信"], P["交换机"], P["算力租赁/IDC"]
p_gpu, p_wine, p_bank = P["GPU/CPU"], P["白酒/食品饮料"], P["银行/红利"]


def mem(pool, n_top=3):
    ms = sorted(pool["members"], key=lambda m: -m["pct"])[:n_top]
    fmt = lambda m: f'<b class="{"up" if m["pct"] >= 0 else "down"}">{m["pct"]:+.2f}%</b>'
    return "、".join(f'{m["name"]} {fmt(m)}' for m in ms)


AMT_19 = B["sz_amount_yi"]
AMT_18 = B18["sz_amount_yi"]
AMT_D = AMT_19 - AMT_18
AMT_P = AMT_D / AMT_18 * 100

SH_GAP = 3706 - SH["close"]
CY_GAP = 2626 - CY["close"]
CY_LO = 2263.74        # 她的 2263 点 / 11/17 最低
HG_LOW_PCT = (HG["low"] / HG["prev_close"] - 1) * 100
SY_GAP = (SY["ma20"] / SY["close"] - 1) * 100
XY_GAP = (XY["ma20"] / XY["close"] - 1) * 100

TITLE = "wu2198 - 2026-11-19（周四 燧原20cm，GPU被砸）"

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
    <span>🕘 截稿 2026-11-19 21:05（<b>收盘版</b>）</span>
    <span>📡 weibo skill（两轮补采，<b>12 条</b>，06:31–20:46）</span>
    <span>💹 Tushare Pro 日线（前复权，11/19 收盘）</span>
  </div>
  <p class="stance">
    <b>🟢 11:05「以后记住了，必须等C5完成之后才参与！」</b> —— 纪律写死。
    10:55 点名<b>封装、光刻胶、半导体设备局部走红</b>（实测设备 +{p_eq['avg']:.2f}%、光刻胶 +{p_liq['avg']:.2f}%，全兑现）；
    11:14「燧原 9 个交易日涨翻番，今天被砸了 20 厘米，GPU和CPU集体被砸」→ <b>两个数字分毫不差</b>。
    <b>但今天是最差的一天</b>：沪指再创 60 日新低 {SH['low']:.2f}、跌 {B['down']} 家、跌停 {B['dt']} 家、成交额 {AMT_19:,.0f} 亿创年内地量。
    → <b>昨天算力涨停潮一日游（8 家涨停今天 0 家）</b>；只做半导体设备 + 光刻胶 + CPO，回踩分批，总仓 ≤2 成。
  </p>
</div>

<div class="grid-4" style="margin-bottom:8px">
  <div class="kpi"><div class="label">上证指数</div><div class="val">{SH['close']:.2f}</div>
    <div class="sub"><span class="down">{SH['pct']:+.2f}%</span> · 最低 <b>{SH['low']:.2f}</b>（<b>60 日新低</b>）</div></div>
  <div class="kpi"><div class="label">创业板指</div><div class="val">{CY['close']:.2f}</div>
    <div class="sub"><span class="down">{CY['pct']:+.2f}%</span> · 最低 <b>{CY['low']:.2f}</b>（2263 未破 ✓）</div></div>
  <div class="kpi"><div class="label">沪深成交额</div><div class="val">{AMT_19:,.0f} 亿</div>
    <div class="sub"><span class="vol">缩量 {abs(AMT_D):,.0f} 亿（{AMT_P:+.1f}%）· 年内地量</span></div></div>
  <div class="kpi"><div class="label">涨跌家数</div><div class="val">{B['up']} / {B['down']}</div>
    <div class="sub">涨停 {B['zt']}（昨 {B18['zt']}）· <span class="down">跌停 {B['dt']}（昨 {B18['dt']}）</span></div></div>
</div>

<h2>一、博主说了什么（8 条）</h2>
<table>
<thead><tr><th>时间</th><th>信号</th><th>原文</th><th>判读 / 日线实测</th></tr></thead>
<tbody>
<tr><td><b>06:31</b></td><td>⚪ 外盘</td><td class="text">昨晚美国股市分化，收盘道指下跌561点，纳指上涨101点、标普下跌17点</td>
  <td class="text"><b>三个数字分毫不差</b>：11/18 实测道指 <b>−561.25</b>、纳指 <b>+101.51</b>、标普 <b>−16.89</b>。</td></tr>
<tr><td><b>10:55</b></td><td>🟢🟢 板块点名</td><td class="text">按目前看，封装，光刻胶，半导体设备等局部走红。</td>
  <td class="text"><b>全兑现</b>：设备 <b class="up">{p_eq['avg']:+.2f}%</b>（{p_eq['up']} 涨 {p_eq['down']} 跌）、光刻胶 <b class="up">{p_liq['avg']:+.2f}%</b>（江化微、格林达双涨停）、封装 <b class="up">{p_pkg['avg']:+.2f}%</b>（长电 +4.74%）。</td></tr>
<tr><td><b>11:05</b></td><td>🟢🟢 纪律固化</td><td class="text">以后记住了，必须等C5完成之后才参与！</td>
  <td class="text"><b>把 11/13 的 C5 口径写成硬纪律</b>（赞 1.3 万）。今天 C5 后第一次照做：<b>没抄被砸的 GPU，改在半导体设备找强势</b>。</td></tr>
<tr><td><b>11:14</b></td><td>🟢🟢 自我验证</td><td class="text">燧原前面只用了9个交易日差不多涨翻番，今天被砸了20厘米。整体看，今天GPU和CPU板块集体被砸！</td>
  <td class="text"><b>两个数字分毫不差</b>：燧原 688801 前复权 11/04 低 321.36 → 11/13 高 613.00 = <b>+90.8%</b>（<b>9 个交易日</b>）；今日开 430 即最高、最低=收盘 <b>364.33（−20.00%）</b>。GPU/CPU 池 <b class="down">{p_gpu['avg']:+.2f}%</b>。</td></tr>
<tr><td><b>14:49</b></td><td>🟡 盘中点位</td><td class="text">早盘曾大跌17.4%，现在是小跌3.3%.......</td>
  <td class="text"><b>标的 = 海光信息 688041</b>：最低 <b>{HG['low']:.2f} = {HG_LOW_PCT:.2f}%</b>（她说 17.4%），发帖时约 −3.3%，收盘 {HG['close']:.2f}。<b>她没说名字，靠盘面反推</b>。</td></tr>
<tr><td><b>14:51 / 14:55</b></td><td>⚪ 情绪</td><td class="text">20多年啦，我一直是大家最熟悉的陌生人…… / 截止目前看，是给了我一个小V.......感谢主力！</td>
  <td class="text">情绪转暖，对应<b>尾盘从日内低点回拉</b>（沪指 {SH['low']:.2f}→{SH['close']:.2f}）。</td></tr>
<tr><td><b>14:26</b></td><td>⚪ 外盘</td><td class="text">台湾金融监管机构：从周五开始实施新的卖空限制。</td>
  <td class="text">台股卖空新规，对 A 股无直接映射，不作方向信号。</td></tr>
<tr><td><b>20:39</b></td><td>🟢 盘后催化</td><td class="text">长鑫科技公告，回购金额增加至不低于25亿元、不超过50亿元</td>
  <td class="text"><b>盘后催化，11/20 才交易</b>。长鑫 688825 今日 {ZX['close']:.2f}（{ZX['pct_chg']:+.2f}%）、Q3 营收 <b>+738.5%</b>、ROE 84.2% → 存储链支撑，<b>但不能算她提前判断对</b>。</td></tr>
</tbody>
</table>

<h2>二、大盘关键点位</h2>
<p class="meta" style="margin-bottom:6px">K 线<b>红涨绿跌</b>；关键位在图<b>左侧虚线</b>。数据源 <b>Tushare Pro 日线</b>（前复权），11/19 <b>完整收盘 K 线</b>。</p>

<h3>上证指数 · {SH['close']:.2f}（{SH['pct']:+.2f}%）</h3>
<img class="chart" src="../charts/000001_SH_20261119.png" alt="上证指数 2026-11-19 K线">
<p class="chart-caption">开 {SH['open']:.2f} / 高 {SH['high']:.2f} / 低 <b>{SH['low']:.2f}</b> / 收 {SH['close']:.2f}。
<b>最低 {SH['low']:.2f} = 又是 60 日新低</b>（前低 3560.45 再破）；<b>3706 差 {SH_GAP:.2f} 点（{SH_GAP/3706*100:.2f}%）</b>，MA20 {SH['ma20']:.2f} 失守。</p>

<h3>创业板指 · {CY['close']:.2f}（{CY['pct']:+.2f}%）</h3>
<img class="chart" src="../charts/399006_SZ_20261119.png" alt="创业板指 2026-11-19 K线">
<p class="chart-caption">开 {CY['open']:.2f} / 高 {CY['high']:.2f} / 低 <b>{CY['low']:.2f}</b> / 收 {CY['close']:.2f}。
<b>最低 {CY['low']:.2f} &gt; 11/17 的 {CY_LO:.2f} → 她的 2263 点连续第 3 天守住</b>；<b>2626 差 {CY_GAP:.2f} 点（{CY_GAP/2626*100:.2f}%）</b>，MA20 {CY['ma20']:.2f} 远在头顶。</p>

<div class="risk">
  <b>⚠️ 今天是这一轮最差的一天。</b>跌 {B['down']} 家 vs 涨 {B['up']} 家、跌停 {B['dt']} 家（昨 {B18['dt']}）、成交额 {AMT_19:,.0f} 亿缩 {abs(AMT_D):,.0f} 亿创年内新低、沪指再破 60 日低、最高连板仅 2 板。
  <b>昨天的算力涨停潮一日游：8 家涨停 → 今天 0 家</b>，鸿博股份 −10.02%、双环科技 −9.90%、泰嘉股份 −9.98% 三只跌停。
  她 11:05 写「必须等 C5 完成之后才参与」——<b>今天 C5 到了，但力度没到，所以是「参与而不加码」。</b>
</div>

<h2>三、最值得投资的 3 个板块</h2>
<table>
<thead><tr><th>板块</th><th>11/19 收盘实测</th><th>博主口径 / 打法</th></tr></thead>
<tbody>
<tr><td><b>① 半导体设备</b><br><span class="tag tag-bull">首选 · 唯一成板块</span></td>
    <td>池 {p_eq['n']} 只 <b class="up">{p_eq['up']} 涨 {p_eq['down']} 跌</b>，均值 <b class="up">{p_eq['avg']:+.2f}%</b>，额 {p_eq['amount_yi']:,.0f} 亿<br>
      {mem(p_eq, 3)}</td>
    <td><b>她 10:55 点名，兑现</b>，<b>今天唯一形成板块的强势方向</b>。中微 +5.05%、拓荆 +4.75%、华海清科 +4.49%、北方华创 +3.13%。<b>只做龙头</b>：中微收 {ZW['close']:.2f}、<b>站上 MA20 {ZW['ma20']:.2f}</b>、放量 {ZW['vol_ratio5']:.0f}%、Q3 营收 +28.1%、资产负债 21.7% → <b>回踩 MA20 不破可分批</b>。</td></tr>
<tr><td><b>② 光刻胶 / 材料</b><br><span class="tag tag-bull">情绪主线 · 只做龙头</span></td>
    <td>池 {p_liq['n']} 只 <b class="up">{p_liq['up']} 涨 {p_liq['down']} 跌</b>，均值 <b class="up">{p_liq['avg']:+.2f}%</b>，额 {p_liq['amount_yi']:,.0f} 亿<br>
      {mem(p_liq, 3)}</td>
    <td><b>她 10:55 点名，兑现</b>：江化微、格林达双涨停（<b>均 2 连板</b>），南大光电 +4.78%、彤程新材 +3.00%。
    <b>但涨停全是连板情绪票，不符合她「业绩增速」的公式</b> → 只做有业绩的南大光电（收 43.87、<b>站上 MA20 40.17</b>、放量 159%）。</td></tr>
<tr><td><b>③ CPO / 光模块</b><br><span class="tag tag-neutral">逆势最抗跌 · 等回踩</span></td>
    <td>池 {p_cpo['n']} 只 {p_cpo['up']} 涨 {p_cpo['down']} 跌，均值 <b class="up">{p_cpo['avg']:+.2f}%</b>，额 {p_cpo['amount_yi']:,.0f} 亿<br>
      {mem(p_cpo, 3)}</td>
    <td><b>算力链里唯一没被砸的分支</b>（交换机 <b class="down">{p_sw['avg']:+.2f}%</b>、算力租赁 <b class="down">{p_idc['avg']:+.2f}%</b>）。新易盛 +5.59%、中际旭创 +3.05%，Q3 营收 <b>+93.0% / +178.1%</b>。
    <b>但都在 MA20 之下（差 {XY_GAP:.1f}%）→ 位置最低、趋势未转，等回踩不追高。</b></td></tr>
</tbody>
</table>
<p class="meta" style="margin-bottom:0">
  <b>回避</b>：GPU/CPU <b class="down">{p_gpu['avg']:+.2f}%</b>（燧原 −20.00%）、交换机 <b class="down">{p_sw['avg']:+.2f}%</b>（0 涨 8 跌）、算力租赁 <b class="down">{p_idc['avg']:+.2f}%</b>（0 涨停）、传媒 −4.86%、农林牧渔 −3.08%。
  <b>底仓垫</b>：银行/红利 <b class="up">{p_bank['avg']:+.2f}%</b>（招行 {YB['close']:.2f} {YB['pct_chg']:+.2f}%）、白酒/食品饮料 <b class="up">{p_wine['avg']:+.2f}%</b>（茅台 {MT['close']:.2f} <b class="up'{MT['pct_chg']:+.2f}%</b>）→ 今天唯一稳。
  申万一级<b>无一行业均值正收益</b>（最好的非银 −0.50%），传媒 −4.86% 领跌。
</p>

<h2>四、3 支个股</h2>
<table>
<thead><tr><th>代码 名称</th><th class="score">收盘</th><th class="score">涨跌</th>
<th class="score">成交额</th><th>关键位</th><th>实测印证 / 动作</th></tr></thead>
<tbody>
<tr><td><b>688012</b> 中微公司</td><td class="score">{ZW['close']:.2f}</td><td class="score"><span class="up">{ZW['pct']:+.2f}%</span></td>
    <td class="score">{ZW['amount_yi']:.1f} 亿</td><td>MA20 <b>{ZW['ma20']:.2f}</b> · 60 日低 <b>{ZW['lo60']:.2f}</b> · 60 日高 <b>{ZW['hi60']:.2f}</b></td>
    <td class="text"><b>首选</b>：她 10:55 点名的半导体设备龙头，收盘=当日最高、放量 {ZW['vol_ratio5']:.0f}%、Q3 营收 +28.1%、毛利率 40.4%、资产负债 21.7%。
    <b>站上 MA5 {ZW['ma5']:.2f} 与 MA20 {ZW['ma20']:.2f}、MACD 柱 {ZW['macd_bar']:+.2f} → 逆势唯一站上 MA20 的主线龙头</b>。<b>回踩 MA20 不破可分批，破位放弃。</b></td></tr>
<tr><td><b>300502</b> 新易盛</td><td class="score">{XY['close']:.2f}</td><td class="score"><span class="up">{XY['pct']:+.2f}%</span></td>
    <td class="score">{XY['amount_yi']:.1f} 亿</td><td>MA20 <b>{XY['ma20']:.2f}</b> · 60 日低 <b>{XY['lo60']:.2f}</b> · 60 日高 <b>{XY['hi60']:.2f}</b></td>
    <td class="text"><b>今天全市场最强的大票</b>，Q3 营收 <b>+93.0%</b>、ROE <b>49.6%</b>、资产负债 36.9% → 最符合她「高成长」的公式；距 60 日高仍有 {(1-XY['close']/XY['hi60'])*100:.1f}%。
    <b>但 MA20 {XY['ma20']:.2f} 仍压顶（差 {XY_GAP:.1f}%）、MACD 柱 {XY['macd_bar']:+.2f} → 不追，等回踩。</b></td></tr>
<tr><td><b>688041</b> 海光信息<br><span class="tag tag-bear">等信号 · 不接</span></td><td class="score">{HG['close']:.2f}</td><td class="score"><span class="down">{HG['pct']:+.2f}%</span></td>
    <td class="score">{HG['amount_yi']:.1f} 亿</td><td>MA20 <b>{HG['ma20']:.2f}</b> · 60 日低 <b>{HG['lo60']:.2f}</b></td>
    <td class="text"><b>她 14:49 亲自点名的那只</b>：最低 {HG['low']:.2f} = <b>{HG_LOW_PCT:.2f}%</b>（她报 17.4%），<b>放量 {HG['vol_ratio5']:.0f}% 破位下跌</b>，MA20 {HG['ma20']:.2f} 失守。昨天 21:07 的「利好国产替代」今日被证伪。<b>动作：不接，等站回 MA20 或 {HG['lo60']:.2f} 二次不破。</b></td></tr>
</tbody>
</table>

<h3>中微公司（688012）· {ZW['close']:.2f}（{ZW['pct']:+.2f}%）</h3>
<img class="chart" src="../charts/688012_SH_20261119.png" alt="中微公司 2026-11-19 K线">
<p class="chart-caption">高 {ZW['high']:.2f} = 收盘价 / 低 {ZW['low']:.2f} / 收 {ZW['close']:.2f}，额 {ZW['amount_yi']:.1f} 亿。
站上 MA5 {ZW['ma5']:.2f} / MA10 {ZW['ma10']:.2f} / MA20 {ZW['ma20']:.2f}；60 日高 {ZW['hi60']:.2f} 在左上（距今 {(1-ZW['close']/ZW['hi60'])*100:.1f}%），60 日低 {ZW['lo60']:.2f} 在下方。</p>

<h3>新易盛（300502）· {XY['close']:.2f}（{XY['pct']:+.2f}%）</h3>
<img class="chart" src="../charts/300502_SZ_20261119.png" alt="新易盛 2026-11-19 K线">
<p class="chart-caption">高 {XY['high']:.2f} / 低 {XY['low']:.2f} / 收 {XY['close']:.2f}，额 {XY['amount_yi']:.1f} 亿（全场最大）。
距 60 日低 {XY['lo60']:.2f} 仅 {XY['dist_lo60']:.1f}%，但 MA20 {XY['ma20']:.2f} 压在头顶 —— <b>底部区域，未转势</b>。</p>

<h3>海光信息（688041）· {HG['close']:.2f}（{HG['pct']:+.2f}%）—— 她 14:49 那只</h3>
<img class="chart" src="../charts/688041_SH_20261119.png" alt="海光信息 2026-11-19 K线">
<p class="chart-caption">开 {HG['open']:.2f} = 最高 / 低 <b>{HG['low']:.2f}</b>（<b>60 日新低，{HG_LOW_PCT:.2f}%</b>）/ 收 {HG['close']:.2f}，额 {HG['amount_yi']:.1f} 亿。
从 {HG['prev_close']:.2f} 一路砸到 {HG['low']:.2f} 再收复到 {HG['close']:.2f} —— <b>她发帖时的「小跌 3.3%」就在这段回拉里</b>。</p>

<h2>五、11/20（周五）盯什么（5 条）</h2>
<ul class="tight">
  <li><b>燧原、海光能否止跌</b> —— 燧原 20cm 跌停收 364.33、海光收 {HG['close']:.2f}；<b>这两只不企稳，GPU 链的「杀估值」没结束</b>。</li>
  <li><b>沪指 60 日新低 {SH['low']:.2f} 不破</b> —— 破了说明她的 C5 判断还要下修。</li>
  <li><b>创业板 {CY_LO:.2f}（她的 2263 点）不破</b> —— 今日最低 {CY['low']:.2f}，已连续 3 天守住。</li>
  <li><b>半导体设备能否连续</b> —— 今天是唯一成板块的强势方向；<b>11/20 若缩量不跟，就是一日游</b>。</li>
  <li><b>长鑫回购的兑现</b> —— 20:39 盘后公告 25–50 亿回购，存储链 11/20 的催化（长鑫 {ZX['close']:.2f}、兆易、佰维），<b>高开不追</b>。</li>
</ul>

<h2>六、偏差记录</h2>
<table>
<thead><tr><th>项</th><th>博主口径</th><th>实测 / 处理</th></tr></thead>
<tbody>
<tr><td>06:31 外盘三数字<br><span class="tag tag-bull">分毫不差</span></td><td class="text">道指下跌561点，纳指上涨101点、标普下跌17点</td>
    <td class="text">11/18 实测道指 <b>−561.25</b>、纳指 <b>+101.51</b>、标普 <b>−16.89</b>，<b>三个数字全部对上</b>。外盘播报仍可直接当数据源用。</td></tr>
<tr><td>11:14 燧原 + GPU/CPU 被砸<br><span class="tag tag-bull">分毫不差</span></td><td class="text">燧原前面只用了9个交易日差不多涨翻番，今天被砸了20厘米。整体看，今天GPU和CPU板块集体被砸！</td>
    <td class="text">燧原 688801：11/04 低 321.36 → 11/13 高 613.00 = <b>+90.8%</b>，历时 <b>9 个交易日</b>；今日开 430 即最高，最低=收盘 <b>364.33（−20.00%）</b>。GPU/CPU 池 <b>{p_gpu['avg']:+.2f}%</b>。<b>本期最硬的核验</b>。</td></tr>
<tr><td>10:55 封装/光刻胶/设备<br><span class="tag tag-bull">兑现</span></td><td class="text">封装，光刻胶，半导体设备等局部走红</td>
    <td class="text">设备 <b>{p_eq['avg']:+.2f}%</b>（{p_eq['up']}涨{p_eq['down']}跌）、光刻胶 <b>{p_liq['avg']:+.2f}%</b>（江化微、格林达双涨停）、封装 <b>{p_pkg['avg']:+.2f}%</b> —— <b>三个方向全中</b>。</td></tr>
<tr><td>14:49「早盘曾大跌17.4%」<br><span class="tag tag-bull">分毫不差</span></td><td class="text">早盘曾大跌17.4%，现在是小跌3.3%.......</td>
    <td class="text"><b>标的 = 海光信息 688041</b>（她没说名字，靠盘面反推）：最低 <b>{HG['low']:.2f} = {HG_LOW_PCT:.2f}%</b>，发帖时约 −3.3%，收盘 {HG['close']:.2f}。</td></tr>
<tr><td>11/18 21:07「利好国产替代」<br><span class="tag tag-bear">被证伪</span></td><td class="text">#英伟达停止向中国供应H200#利好国产替代！</td>
    <td class="text"><b>今日 GPU/CPU 池 {p_gpu['avg']:+.2f}%、海光盘中 {HG_LOW_PCT:.2f}%</b> —— <b>隔夜催化不但没兑现，还成了杀跌理由</b>。
    <b>11/19 最该记住的一条：盘后催化 ≠ 次日买点。</b></td></tr>
</tbody>
</table>
<p class="meta" style="margin-bottom:0">
  其余 <b>2 条无方向信号</b>：14:26 台湾卖空新规（对 A 股无映射）、14:51/14:55「给了我一个小 V」（情绪，对应尾盘回拉）。
  采集：weibo skill 两轮补采 → <b>12 条</b>（06:31–20:46）；行情：<b>Tushare Pro 日线</b>（前复权），全市场单次全量算涨跌停、板块均值与涨停梯队。
</p>

<div class="foot">
  <p><b>免责声明</b>：本报告为公开微博内容整理与技术面统计，<b>不构成投资建议</b>；
  「3 板块 + 3 个股」是博主观点 + 实测强度的归纳。</p>
  <p>
    报告生成：2026-11-19 收盘版 · 数据源 weibo skill + Tushare Pro 日线 ·
    脚本 <code>collect_tushare_20261119.py</code> / <code>collect_pools_20261119.py</code> /
    <code>collect_mkt_20261119.py</code> / <code>make_wu2198_charts_20261119.py</code> /
    <code>gen_wu2198_report_20261119.py</code>。
  </p>
</div>

</div>
</body>
</html>
"""

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fix_mobile_tables import patch_html

if __name__ == "__main__":
    out = ROOT / "html" / "wu2198-20261119.html"
    out.write_text(patch_html(HTML), encoding="utf-8")
    print(f"[out] {out}  ({len(HTML)} bytes)")
