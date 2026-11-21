"""wu2198 投资日报 2026-11-20（周五 · 收盘版）— 线上产物生成器

用法： python3 scripts/gen_wu2198_report_20261120.py
产物： html/wu2198-20261120.html
行情口径：Tushare Pro 日线（pro.daily / pro.index_daily + adj_factor 前复权）
篇幅： 正文 ≤ 2000 中文字 / 表格 ≤ 4 张
"""
import json
import sys
from pathlib import Path

ROOT = Path("/Users/maoling/workspace/mnote.github.io")
CH = ROOT / "charts"

KPI = json.loads((CH / "_kpic_20261120.json").read_text(encoding="utf-8"))
TS = json.loads((CH / "_ts_20261120.json").read_text(encoding="utf-8"))
POOLS = json.loads((CH / "_pools_20261120.json").read_text(encoding="utf-8"))
MKT = json.loads((CH / "_mkt_20261120.json").read_text(encoding="utf-8"))

SH, CY = KPI["000001.SH"], KPI["399006.SZ"]
ZW, YB, MT = KPI["688012.SH"], KPI["600036.SH"], KPI["600519.SH"]
HG = TS["stocks"]["688041.SH"]
SY = TS["stocks"]["688801.SH"]
XG = TS["stocks"]["300502.SZ"]
P = POOLS["pools"]
B = MKT["days"]["20261120"]
B19 = MKT["days"]["20261119"]

p_bank, p_eq, p_wine = P["银行/红利"], P["半导体设备"], P["白酒/食品饮料"]
p_pkg, p_liq, p_idc = P["先进封装"], P["光刻胶/材料"], P["算力租赁/IDC"]
p_cpo, p_sw, p_gpu = P["CPO/光通信"], P["交换机"], P["GPU/CPU"]


def mem(pool, n_top=3):
    ms = sorted(pool["members"], key=lambda m: -m["pct"])[:n_top]
    fmt = lambda m: f'<b class="{"up" if m["pct"] >= 0 else "down"}">{m["pct"]:+.2f}%</b>'
    return "、".join(f'{m["name"]} {fmt(m)}' for m in ms)


AMT_20 = B["sz_amount_yi"]
AMT_19 = B19["sz_amount_yi"]
AMT_D = AMT_20 - AMT_19
AMT_P = AMT_D / AMT_19 * 100

SH_GAP = 3706 - SH["close"]
CY_GAP = 2626 - CY["close"]
CY_LO = 2263.74        # 她的 2263 点 / 11/17 最低
CY_BREAK = CY_LO - CY["low"]
CY_BREAK_P = CY_BREAK / CY_LO * 100

TITLE = "wu2198 - 2026-11-20（周五 银行新高，创业板破2263）"

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
    <span>🕘 截稿 2026-11-21 12:15（<b>11/20 收盘版 + 11/21 早间复盘</b>）</span>
    <span>📡 weibo skill（两轮补采，<b>11 条</b>，11/20 09:43 – 11/21 09:39）</span>
    <span>💹 Tushare Pro 日线（前复权，11/20 收盘）</span>
  </div>
  <p class="stance">
    <b>🟢 09:49「工行，建行改写新高」—— 全中</b>：工行 +3.30%、建行 +3.07%，<b>两只都创年内新高</b>，农行 +1.57% 同创新高；申万一级<b>只有银行收正（+0.22%）</b>。
    但另一面更重：<b>创业板最低 {CY['low']:.2f} = 收盘，跌破她的 2263 点（差 {CY_BREAK:.2f} 点）</b>；沪指最低 {SH['low']:.2f} 又是 60 日新低；
    跌 {B['down']} 家、<b>下跌放量 {AMT_D:,.0f} 亿（{AMT_P:+.1f}%）</b>。
    <b>11/19 点名的封装 / 光刻胶 / 设备今天全被砸。</b>
    → 她 11/21 早上自认「<b>抄C5抄成了股Z</b>」；<b>只做银行/红利 + 站上 MA20 的半导体龙头，别的都等。</b>
  </p>
</div>

<div class="grid-4" style="margin-bottom:8px">
  <div class="kpi"><div class="label">上证指数</div><div class="val">{SH['close']:.2f}</div>
    <div class="sub"><span class="down">{SH['pct']:+.2f}%</span> · 最低 <b>{SH['low']:.2f}</b>（<b>60 日新低</b>）</div></div>
  <div class="kpi"><div class="label">创业板指</div><div class="val">{CY['close']:.2f}</div>
    <div class="sub"><span class="down">{CY['pct']:+.2f}%</span> · 最低=收盘（<b>2263 已破</b>）</div></div>
  <div class="kpi"><div class="label">沪深成交额</div><div class="val">{AMT_20:,.0f} 亿</div>
    <div class="sub"><span class="vol">放量 {AMT_D:,.0f} 亿（{AMT_P:+.1f}%）· 下跌放量</span></div></div>
  <div class="kpi"><div class="label">涨跌家数</div><div class="val">{B['up']} / {B['down']}</div>
    <div class="sub">涨停 {B['zt']}（昨 {B19['zt']}）· <span class="down">跌停 {B['dt']}（昨 {B19['dt']}）</span></div></div>
</div>

<h2>一、博主说了什么（8 条）</h2>
<table>
<thead><tr><th>时间</th><th>信号</th><th>原文</th><th>判读 / 日线实测</th></tr></thead>
<tbody>
<tr><td><b>11/20 09:43</b></td><td>⚪ 亚太播报</td><td class="text">截止目前看，日本股市跌4.29%；韩国股市跌4.31%，台湾省股市跌4.95%。</td>
  <td class="text"><b>盘中口径</b>（09:43 亚市开盘一小时）。收盘实为日经 <b class="down">−5.06%</b>、韩国 <b class="down">−5.21%</b>、台湾 <b class="down">−6.23%</b> —— <b>比她报的还多跌</b>，方向一致。</td></tr>
<tr><td><b>11/20 09:49</b></td><td>🟢🟢 板块点名</td><td class="text">工行，建行改写新高。</td>
  <td class="text"><b>分毫不差</b>：工行最高 9.49、建行最高 12.78，<b>双双创年内新高</b>；收盘 +3.30% / +3.07%，农行 +1.57% 同创年内新高。</td></tr>
<tr><td><b>11/20 10:39</b></td><td>🟡 前瞻</td><td class="text">2027年，年度高低点的判断，我会提前分析……但是我只给喜欢我的人看。</td>
  <td class="text"><b>要发 2027 年度高低点判断</b>（互动 1.9 万，当日第一）。<b>不构成可执行信号，等内容</b>。</td></tr>
<tr><td><b>11/20 23:16</b></td><td>⚪ 外盘盘中</td><td class="text">美国市场现在是道指涨375点，纳指跌306点。科技股领跌！</td>
  <td class="text"><b>盘中口径</b>（「现在」）。收盘为道指 <b class="down">−949.73</b>、纳指 <b class="down">−1261.47</b>、标普 <b class="down">−265.44</b>。</td></tr>
<tr><td><b>11/21 05:52</b></td><td>⚪ 外盘收盘</td><td class="text">周五晚美国股市全线大跌，收盘道指下跌949点，纳指跌1261点、标普下跌265点。</td>
  <td class="text"><b>三个数字分毫不差</b>：−949.73 / −1261.47 / −265.44。连续第 5 次外盘播报全中。</td></tr>
<tr><td><b>11/21 06:10 / 06:29</b></td><td>🔴 自我检讨</td><td class="text">本来高位己经撤离了…………坏了，我又陷进去了！ / 多少次暴风雨……这次还是老样子，先想办法如何活下去吧！</td>
  <td class="text"><b>罕见地承认自己被套</b>。她 6/8 高位撤离是本系列的标杆动作，这次「又陷进去了」= <b>高位没跑、低位抄底也套</b>。</td></tr>
<tr><td><b>11/21 06:37 / 06:46</b></td><td>🔴🔴 框架失效</td><td class="text">抄C5抄成了股Z……难道这就是命？ / 技术分析失效的情况下，只能靠风险控制或靠意志。</td>
  <td class="text"><b>本期最重要的一条</b>：她的 <b>C5 抄底被自己证伪</b>（11/20 创业板跌破 2263 点），并给出替代方案：<b>技术面失效时靠风控和纪律</b>，不是靠点位。</td></tr>
<tr><td><b>11/21 09:39</b></td><td>⚪ 情绪</td><td class="text">慌啥子嘛？</td>
  <td class="text">情绪帖，无新信号。</td></tr>
</tbody>
</table>

<h2>二、大盘关键点位</h2>
<p class="meta" style="margin-bottom:6px">K 线<b>红涨绿跌</b>；关键位在图<b>左侧虚线</b>。数据源 <b>Tushare Pro 日线</b>（前复权），11/20 <b>完整收盘 K 线</b>。</p>

<h3>上证指数 · {SH['close']:.2f}（{SH['pct']:+.2f}%）</h3>
<img class="chart" src="../charts/000001_SH_20261120.png" alt="上证指数 2026-11-20 K线">
<p class="chart-caption">开 {SH['open']:.2f} / 高 {SH['high']:.2f} / 低 <b>{SH['low']:.2f}</b> / 收 {SH['close']:.2f}。
<b>最低 {SH['low']:.2f} = 又是 60 日新低</b>（前低 3547.94 再破），尾盘自低点回拉 {SH['close']-SH['low']:.2f} 点；<b>3706 差 {SH_GAP:.2f} 点（{SH_GAP/3706*100:.2f}%）</b>，MA20 {SH['ma20']:.2f} 失守。</p>

<h3>创业板指 · {CY['close']:.2f}（{CY['pct']:+.2f}%）</h3>
<img class="chart" src="../charts/399006_SZ_20261120.png" alt="创业板指 2026-11-20 K线">
<p class="chart-caption">开 {CY['open']:.2f} / 高 {CY['high']:.2f} / 低 <b>= 收 {CY['low']:.2f}</b>。
<b>最低=收盘，全天无承接，直接破掉她的 2263 点（差 {CY_BREAK:.2f} 点、{CY_BREAK_P:.2f}%）</b>，并创新 60 日低；<b>2626 差 {CY_GAP:.2f} 点（{CY_GAP/2626*100:.2f}%）</b>，MA20 {CY['ma20']:.2f} 远在头顶。</p>

<div class="risk">
  <b>⚠️ 下跌放量破位，不是缩量磨底。</b>成交 {AMT_20:,.0f} 亿、<b>放量 {AMT_D:,.0f} 亿（{AMT_P:+.1f}%）</b>，涨 {B['up']} / 跌 <b>{B['down']}</b>，跌停 {B['dt']} 家，最高连板仅 2 板；申万一级<b>只有银行 +0.22% 收正</b>，电子 −5.86%、通信 −6.12%、军工 −6.20% 领跌。
  <b>她 11/19 点名的封装 / 光刻胶 / 半导体设备，今天分别 {p_pkg['avg']:+.2f}%、{p_liq['avg']:+.2f}%、{p_eq['avg']:+.2f}% —— 全线翻绿。</b>
  <b>结论：「点位到位但趋势未成立」，C5 已破位，<b>仓位压到 2 成以内</b>，只留防御和站上 MA20 的龙头。</b>
</div>

<h2>三、最值得投资的 3 个板块</h2>
<table>
<thead><tr><th>板块</th><th>11/20 收盘实测</th><th>博主口径 / 打法</th></tr></thead>
<tbody>
<tr><td><b>① 银行 / 红利</b><br><span class="tag tag-bull">首选 · 唯一正收益</span></td>
    <td>池 {p_bank['n']} 只 <b class="up">{p_bank['up']} 涨 {p_bank['down']} 跌</b>，均值 <b class="up">{p_bank['avg']:+.2f}%</b>，额 {p_bank['amount_yi']:,.0f} 亿<br>
      {mem(p_bank, 3)}</td>
    <td><b>她 09:49 点名「工行，建行改写新高」，兑现</b>：工行 +3.30%、建行 +3.07%、农行 +1.57% <b>三家都创年内新高</b>。中国石油 +4.67%、长江电力 +2.40% 同属红利线。
    <b>只做银行 + 高股息，不做题材。</b></td></tr>
<tr><td><b>② 半导体制造 + 设备</b><br><span class="tag tag-bull">次选 · 只做站上 MA20 的龙头</span></td>
    <td>设备池 {p_eq['up']} 涨 {p_eq['down']} 跌，均值 <b class="down">{p_eq['avg']:+.2f}%</b>；但<br>
      中芯国际 <b class="up">+2.63%</b>、粤芯半导体 <b class="up">+1.97%</b>、中微公司 <b class="up">+1.95%</b>、京东方A <b class="up">+1.39%</b></td>
    <td><b>科技里今天唯一还活着的分支</b>（对比：光刻胶 {p_liq['avg']:+.2f}%、封装 {p_pkg['avg']:+.2f}%、CPO {p_cpo['avg']:+.2f}%）。<b>中微公司收 {ZW['close']:.2f}、站上 MA20 {ZW['ma20']:.2f}、放量 {ZW['vol_ratio5']:.0f}%、MACD 柱 {ZW['macd_bar']:+.2f}</b> → 设备池 11 只里 4 只站上 MA20。<b>只做这类，不碰池平均。</b></td></tr>
<tr><td><b>③ 白酒核心资产（茅台）</b><br><span class="tag tag-neutral">防御 · 逼近新高</span></td>
    <td>白酒池 <b class="down">{p_wine['avg']:+.2f}%</b>（{p_wine['up']} 涨 {p_wine['down']} 跌）<br>
      茅台 <b class="up">+1.75%</b> / 五粮液 <b class="down">−1.16%</b> / 山西汾酒 <b class="down">−1.21%</b></td>
    <td><b>池是跌的，只有茅台是红的</b>：最高 {MT['high']:.2f} = <b>60 日新高（今日）</b>，收 {MT['close']:.2f}，放量 {MT['vol_ratio5']:.0f}%、额 {MT['amount_yi']:.0f} 亿，站上 MA20 {MT['ma20']:.2f}。
    <b>她的底仓方向</b> → 防御垫，不加仓。</td></tr>
</tbody>
</table>
<p class="meta" style="margin-bottom:0">
  <b>回避</b>：先进封装 <b class="down">{p_pkg['avg']:+.2f}%</b>（长电 −9.50%）、光刻胶 <b class="down">{p_liq['avg']:+.2f}%</b>（江化微 −7.74%）、交换机 <b class="down">{p_sw['avg']:+.2f}%</b>、存储 <b class="down">−6.52%</b>（长鑫 −6.24%）、算力租赁 <b class="down">{p_idc['avg']:+.2f}%</b>、GPU/CPU <b class="down">{p_gpu['avg']:+.2f}%</b>。
  <b>她的 C5 抄底标的被证伪</b>：海光信息 11/20 <b class="down">{HG['pct_chg']:+.2f}%</b>，逼近 60 日低 {HG['lo60']:.2f}；燧原 {SY['pct_chg']:+.2f}%。→ <b>对应她 06:37 那句「抄C5抄成了股Z」。</b>
</p>

<h2>四、3 支个股</h2>
<table>
<thead><tr><th>代码 名称</th><th class="score">收盘</th><th class="score">涨跌</th>
<th class="score">成交额</th><th>关键位</th><th>实测印证 / 动作</th></tr></thead>
<tbody>
<tr><td><b>600036</b> 招商银行</td><td class="score">{YB['close']:.2f}</td><td class="score"><span class="up">{YB['pct']:+.2f}%</span></td>
    <td class="score">{YB['amount_yi']:.1f} 亿</td><td>MA20 <b>{YB['ma20']:.2f}</b> · 60 日高 <b>{YB['hi60']:.2f}</b>（今日）</td>
    <td class="text"><b>她 09:49 点名方向的流动性龙头</b>：最高 {YB['high']:.2f} = <b>60 日新高</b>，收 {YB['close']:.2f} 几乎收在最高，放量 {YB['vol_ratio5']:.0f}%、额 {YB['amount_yi']:.0f} 亿。
    <b>站上 MA5/MA10/MA20 {YB['ma20']:.2f}、MACD 柱 {YB['macd_bar']:+.2f}</b> → <b>底仓垫，回调不破 MA20 可续，破 MA20 减仓。</b></td></tr>
<tr><td><b>688012</b> 中微公司</td><td class="score">{ZW['close']:.2f}</td><td class="score"><span class="up">{ZW['pct']:+.2f}%</span></td>
    <td class="score">{ZW['amount_yi']:.1f} 亿</td><td>MA20 <b>{ZW['ma20']:.2f}</b> · 60 日低 <b>{ZW['lo60']:.2f}</b> · 60 日高 <b>{ZW['hi60']:.2f}</b></td>
    <td class="text"><b>科技里唯一站上 MA20 的主线龙头</b>（连续三日站上：244 → 256 → 261），放量 {ZW['vol_ratio5']:.0f}%、额 {ZW['amount_yi']:.0f} 亿、MACD 柱 {ZW['macd_bar']:+.2f}。
    <b>回踩 MA20 {ZW['ma20']:.2f} 不破可分批，破位放弃。</b></td></tr>
<tr><td><b>600519</b> 贵州茅台</td><td class="score">{MT['close']:.2f}</td><td class="score"><span class="up">{MT['pct']:+.2f}%</span></td>
    <td class="score">{MT['amount_yi']:.1f} 亿</td><td>MA20 <b>{MT['ma20']:.2f}</b> · 60 日高 <b>{MT['hi60']:.2f}</b>（今日）</td>
    <td class="text"><b>今日创 60 日新高</b>：最高 {MT['high']:.2f}、收 {MT['close']:.2f}，放量 {MT['vol_ratio5']:.0f}%、额 {MT['amount_yi']:.0f} 亿，站上 MA5/MA10/MA20 {MT['ma20']:.2f}、MACD 柱 {MT['macd_bar']:+.2f}。
    <b>但白酒池整体 −2.10%，是她自己的底仓 → 只当防御垫，不当进攻。</b></td></tr>
</tbody>
</table>

<h3>招商银行（600036）· {YB['close']:.2f}（{YB['pct']:+.2f}%）</h3>
<img class="chart" src="../charts/600036_SH_20261120.png" alt="招商银行 2026-11-20 K线">
<p class="chart-caption">高 {YB['high']:.2f} / 低 {YB['low']:.2f} / 收 {YB['close']:.2f}，额 {YB['amount_yi']:.1f} 亿。
<b>最高 {YB['high']:.2f} = 60 日新高</b>，收在最高附近；站上 MA5 {YB['ma5']:.2f} / MA10 {YB['ma10']:.2f} / MA20 {YB['ma20']:.2f}，60 日低 {YB['lo60']:.2f} 在下方。</p>

<h3>中微公司（688012）· {ZW['close']:.2f}（{ZW['pct']:+.2f}%）</h3>
<img class="chart" src="../charts/688012_SH_20261120.png" alt="中微公司 2026-11-20 K线">
<p class="chart-caption">高 {ZW['high']:.2f} / 低 {ZW['low']:.2f} / 收 {ZW['close']:.2f}，额 {ZW['amount_yi']:.1f} 亿。
站上 MA5 {ZW['ma5']:.2f} / MA10 {ZW['ma10']:.2f} / MA20 {ZW['ma20']:.2f}；60 日高 {ZW['hi60']:.2f} 在左上（距今 {(1-ZW['close']/ZW['hi60'])*100:.1f}%），60 日低 {ZW['lo60']:.2f} 在下方 —— <b>全市场唯一没破位的主线龙头</b>。</p>

<h3>贵州茅台（600519）· {MT['close']:.2f}（{MT['pct']:+.2f}%）</h3>
<img class="chart" src="../charts/600519_SH_20261120.png" alt="贵州茅台 2026-11-20 K线">
<p class="chart-caption">高 <b>{MT['high']:.2f}</b>（<b>60 日新高</b>）/ 低 {MT['low']:.2f} / 收 {MT['close']:.2f}，额 {MT['amount_yi']:.1f} 亿（全场最大之一）。
放量 {MT['vol_ratio5']:.0f}% 上攻后小幅回落收 {MT['close']:.2f}，仍站上 MA20 {MT['ma20']:.2f}。</p>

<h2>五、11/24（周一）盯什么（5 条）</h2>
<ul class="tight">
  <li><b>她的 C5 口径作废不改</b> —— 11/21 06:37「抄C5抄成了股Z」已自我证伪，<b>别再用 C5 当买点条件</b>；11/20 10:39 预告的 2027 年度高低点才是新的框架。</li>
  <li><b>沪指 60 日新低 {SH['low']:.2f} 不破</b> —— 破了说明还要往下找支撑。</li>
  <li><b>创业板 {CY_LO:.2f} 破了看哪里</b> —— 已破 {CY_BREAK:.2f} 点，下一个整数关 2200。</li>
  <li><b>美股暴跌的传导</b> —— 周五道指 −949、纳指 −1261、费半跌得最狠；<b>周一 A 股开盘别抄，等第一小时</b>。</li>
  <li><b>银行红利还能不能守</b> —— 今天是唯一的避风港（6 涨 0 跌）；<b>它一倒，就没有避风港了</b>。</li>
</ul>

<h2>六、偏差记录</h2>
<table>
<thead><tr><th>项</th><th>博主口径</th><th>实测 / 处理</th></tr></thead>
<tbody>
<tr><td>11/20 09:49「工行，建行改写新高」<br><span class="tag tag-bull">分毫不差</span></td><td class="text">工行，建行改写新高。</td>
    <td class="text">工行最高 <b>9.49</b>、建行最高 <b>12.78</b>，<b>双双创年内新高</b>；收盘 +3.30% / +3.07%，农行 +1.57% 同创年内新高。<b>本期最硬的核验</b>，且是<b>唯一带方向且可执行的点名</b>。</td></tr>
<tr><td>11/21 05:52 外盘三数字<br><span class="tag tag-bull">分毫不差</span></td><td class="text">道指下跌949点，纳指跌1261点、标普下跌265点</td>
    <td class="text">11/20 实测道指 <b>−949.73</b>、纳指 <b>−1261.47</b>、标普 <b>−265.44</b>，<b>三个数字全部对上</b>。外盘播报第 5 次全中。</td></tr>
<tr><td>11/17「本周2263点可以了，接下来等吃肉了」<br><span class="tag tag-bear">已被证伪</span></td><td class="text">本周 2263 点可以了，接下来等吃肉了！</td>
    <td class="text">11/20 创业板最低=收盘 <b>{CY['low']:.2f}</b>，<b>直接跌破 2263 点（差 {CY_BREAK:.2f} 点、{CY_BREAK_P:.2f}%）</b>，并创新 60 日低。
    <b>她自己 11/21 06:37 承认「抄C5抄成了股Z」——是本系列首次自证点位失效。</b></td></tr>
<tr><td>11/19 10:55「封装/光刻胶/半导体设备局部走红」<br><span class="tag tag-bear">一日游</span></td><td class="text">封装，光刻胶，半导体设备等局部走红</td>
    <td class="text">11/20 先进封装 <b class="down">{p_pkg['avg']:+.2f}%</b>（长电 −9.50%）、光刻胶 <b class="down">{p_liq['avg']:+.2f}%</b>、半导体设备 <b class="down">{p_eq['avg']:+.2f}%</b> —— <b>三个方向隔天全绿转全跌，只红了一天</b>。</td></tr>
<tr><td>11/20 09:43 亚太三数字<br><span class="tag tag-neutral">盘中口径</span></td><td class="text">日本股市跌4.29%；韩国股市跌4.31%，台湾省股市跌4.95%</td>
    <td class="text">09:43 是亚市开盘一小时，<b>盘中口径无法用日线核验</b>。收盘实为日经 <b>−5.06%</b>、韩国 <b>−5.21%</b>、台湾 <b>−6.23%</b>，<b>方向一致、跌幅更大</b>。</td></tr>
</tbody>
</table>
<p class="meta" style="margin-bottom:0">
  其余 <b>3 条无方向信号</b>：10:39「2027 年度高低点」（待发布）、23:16 美股盘中「道指涨375点、纳指跌306点」（盘中口径，收盘 −949.73）、09:39「慌啥子嘛」（情绪）。
  采集：weibo skill 两轮补采 <b>11 条</b>（09:43 – 09:39）；行情：<b>Tushare Pro 日线</b>（前复权），全市场单次算涨跌停、板块均值与涨停梯队。
</p>

<div class="foot">
  <p><b>免责声明</b>：公开微博整理 + 技术面统计，<b>不构成投资建议</b>；「3 板块 + 3 个股」为博主观点 + 实测强度归纳。</p>
  <p>
    报告生成：2026-11-20 收盘版（11/21 早间复盘） · 数据源 weibo skill + Tushare Pro 日线 ·
    脚本 <code>collect_tushare_20261120.py</code> / <code>collect_pools_20261120.py</code> /
    <code>collect_mkt_20261120.py</code> / <code>make_wu2198_charts_20261120.py</code> /
    <code>gen_wu2198_report_20261120.py</code>。
  </p>
</div>

</div>
</body>
</html>
"""

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fix_mobile_tables import patch_html

if __name__ == "__main__":
    out = ROOT / "html" / "wu2198-20261120.html"
    out.write_text(patch_html(HTML), encoding="utf-8")
    print(f"[out] {out}  ({len(HTML)} bytes)")
