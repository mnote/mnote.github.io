"""wu2198 投资日报 2026-11-18（周三 · 收盘版）— 线上产物生成器

用法： python3 scripts/gen_wu2198_report_20261118.py
产物： html/wu2198-20261118.html
行情口径：Tushare Pro 日线（pro.daily / pro.index_daily + adj_factor 前复权）
篇幅： 正文 ≤ 2000 中文字 / 表格 ≤ 4 张
"""
import json
import sys
from pathlib import Path

ROOT = Path("/Users/maoling/workspace/mnote.github.io")
CH = ROOT / "charts"

KPI = json.loads((CH / "_kpic_20261118.json").read_text(encoding="utf-8"))
TS = json.loads((CH / "_ts_20261118.json").read_text(encoding="utf-8"))
POOLS = json.loads((CH / "_pools_20261118.json").read_text(encoding="utf-8"))
MKT = json.loads((CH / "_mkt_20261118.json").read_text(encoding="utf-8"))

SH, CY = KPI["000001.SH"], KPI["399006.SZ"]
HD, HX, ZJ = KPI["002463.SZ"], KPI["688256.SH"], KPI["300308.SZ"]
ZG = TS["stocks"]["000938.SZ"]
P = POOLS["pools"]
B = MKT["days"]["20261118"]
B17 = MKT["days"]["20261117"]

p_idc, p_pcb, p_sw = P["算力租赁/IDC"], P["PCB"], P["交换机"]
p_gpu, p_cpo, p_wine, p_mil = (P["GPU/国产算力芯片"], P["CPO/光通信"],
                                P["白酒/食品饮料"], P["军工"])


def amt_on(code, date):
    for r in TS["rows"][code]:
        if r["trade_date"] == date:
            return r["amount"] / 1e5      # 千元 → 亿元
    return None


# 沪深两市成交额：pro.daily_info 的 SH_MARKET + SZ_MARKET（亿元）
AMT_18 = B["sz_amount_yi"]
AMT_17 = B17["sz_amount_yi"]
AMT_D = AMT_18 - AMT_17
AMT_P = AMT_D / AMT_17 * 100
ZJ_GAP = (ZJ["ma20"] / ZJ["close"] - 1) * 100

SH_GAP = 3706 - SH["close"]
CY_GAP = 2626 - CY["close"]
CY_LO = 2263.74        # 她的 2263 点 / 11/17 最低
SH_LO = 3560.45        # 11/18 最低 = 60 日新低

TITLE = "wu2198 - 2026-11-18（周三 C5确认，算力涨停潮）"


def mem(pool, n_top=3):
    ms = sorted(pool["members"], key=lambda m: -m["pct"])[:n_top]
    fmt = lambda m: f'<b class="{"up" if m["pct"] >= 0 else "down"}">{m["pct"]:+.2f}%</b>'
    return "、".join(f'{m["name"]} {fmt(m)}' for m in ms)


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
    <span>🕘 截稿 2026-11-18 22:45（<b>收盘版</b>）</span>
    <span>📡 weibo skill（两轮补采，<b>14 条</b>，09:26–22:01）</span>
    <span>💹 Tushare Pro 日线（前复权，11/18 收盘）</span>
  </div>
  <p class="stance">
    <b>🟢🟢 09:26「昨日创业板指数试2263点，符合预期的C5低点区域了，等待构筑新波段行情即可」</b>
    —— <b>C5 分毫不差</b>（11/17 最低 {CY_LO:.2f}），今日最低 {CY['low']:.2f} 未破，<b>二次确认</b>。
    13:22/13:53 点名<b>算力租赁涨停潮、交换机反击、PCB龙头冲板</b>全部兑现；21:07 英伟达断供 H200 → <b>国产替代</b>（盘后）。
    <b>但地量普跌：成交额 {AMT_18:,.0f} 亿缩 {abs(AMT_D):,.0f} 亿、跌 {B['down']} 家、沪指又创新低 {SH_LO:.2f}。
    → 底部二次确认 ≠ 反转；只在 PCB/算力/国产算力芯片做，回踩分批，总仓 ≤3 成。</b>
  </p>
</div>

<div class="grid-4" style="margin-bottom:8px">
  <div class="kpi"><div class="label">上证指数</div><div class="val">{SH['close']:.2f}</div>
    <div class="sub"><span class="up">{SH['pct']:+.2f}%</span> · 最低 <b>{SH_LO:.2f}</b>（<b>60 日新低</b>）</div></div>
  <div class="kpi"><div class="label">创业板指</div><div class="val">{CY['close']:.2f}</div>
    <div class="sub"><span class="up">{CY['pct']:+.2f}%</span> · 最低 <b>{CY['low']:.2f}</b>（2263 未破 ✓）</div></div>
  <div class="kpi"><div class="label">沪深成交额</div><div class="val">{AMT_18:,.0f} 亿</div>
    <div class="sub"><span class="vol">缩量 {abs(AMT_D):,.0f} 亿（{AMT_P:+.1f}%）· 年内地量</span></div></div>
  <div class="kpi"><div class="label">涨跌家数</div><div class="val">{B['up']} / {B['down']}</div>
    <div class="sub">涨停 {B['zt']}（昨 {B17['zt']}）· <span class="down">跌停 {B['dt']}（昨 {B17['dt']}）</span></div></div>
</div>

<h2>一、博主说了什么（10 条）</h2>
<table>
<thead><tr><th>时间</th><th>信号</th><th>原文</th><th>判读 / 日线实测</th></tr></thead>
<tbody>
<tr><td><b>09:26</b></td><td>🟢🟢 位置确认</td><td class="text">昨日创业板指数试2263点，符合预期的C5低点区域了，所以接下来等待构筑新波段行情即可</td>
  <td class="text"><b>分毫不差</b>：11/17 创业板最低 <b>{CY_LO:.2f}</b> = 她的 2263 点；今日最低 {CY['low']:.2f} <b>未破</b> → <b>C5 二次确认</b>。但只说「等待构筑新波段」，<b>没给标的/点位/仓位</b>。</td></tr>
<tr><td><b>09:48</b></td><td>⚪ 情绪</td><td class="text">这么压法，坏得很！</td>
  <td class="text"><b>盘中确实被压</b>：沪指开 {SH['open']:.2f} 即当日最高，一路走低收 {SH['close']:.2f}，最低 {SH_LO:.2f} 再创新低。</td></tr>
<tr><td><b>13:22</b></td><td>🟢🟢 板块点名</td><td class="text">算力租赁板块出现涨停潮！</td>
  <td class="text"><b>兑现</b>：19 只池 <b>{p_idc['zt']} 家涨停</b>（美利云、中嘉博创、润建股份、华胜天成、城地香江、利通电子、恒润股份、动力源），{p_idc['up']} 涨 {p_idc['down']} 跌、均值 <b class="up">{p_idc['avg']:+.2f}%</b>、额 {p_idc['amount_yi']:,.0f} 亿。</td></tr>
<tr><td><b>13:31</b></td><td>🟡 自我复盘</td><td class="text">在ABC结构调整的第四大浪中，当C3和C5区域我喊分批布局……</td>
  <td class="text">回顾 11/13 的 <b>C3/C5 分批布局</b>，框架未变。<b>属回顾非新指令</b>，但确认 C5 是可动手区间。</td></tr>
<tr><td><b>13:53</b></td><td>🟢🟢 板块点名</td><td class="text">目前算力租赁板块出现涨停潮，交换机板块连续反击，PCB龙头冲板！</td>
  <td class="text"><b>PCB 兑现</b>：池 {p_pcb['up']} 涨 {p_pcb['down']} 跌、均值 <b class="up">{p_pcb['avg']:+.2f}%</b>，<b>沪电+深南双涨停</b>。
    <b>交换机偏弱</b>：池 {p_sw['avg']:+.2f}%、<b>0 涨停</b>。</td></tr>
<tr><td><b>14:20</b></td><td>⚪ 疑</td><td class="text">看看铁几？</td>
  <td class="text">钢铁池 <b class="up">{P['钢铁']['avg']:+.2f}%</b>、铁路运营 <b class="up">{P['铁路运营']['avg']:+.2f}%</b>，<b>均无涨停</b> → 未成主线。</td></tr>
<tr><td><b>14:28</b></td><td>🟡 定性</td><td class="text">暂时还是缺乏力度！</td>
  <td class="text"><b>当日最准一句</b>：地量 {AMT_18:,.0f} 亿、跌 {B['down']} 家、沪指新低、连板最高仅 4 板（华东重机）→ <b>「缺乏力度」成立</b>。</td></tr>
<tr><td><b>21:04 / 21:07</b></td><td>🟢🟢 盘后催化</td><td class="text">英伟达的临时CEO称，将不再向中国出货H200芯片。#英伟达停止向中国供应H200#利好国产替代！</td>
  <td class="text"><b>催化在盘后，11/19 才交易</b>。今天 GPU 池 <b class="up">{p_gpu['avg']:+.2f}%</b>（{p_gpu['up']} 涨 {p_gpu['down']} 跌）<b>不是这条催化的结果</b>。</td></tr>
<tr><td><b>21:43</b></td><td>⚪ 数据</td><td class="text">截至收盘，沪深两市全天成交额13890亿元，创年内地量纪录</td>
  <td class="text"><b>方向一致</b>：实测沪深两市 {AMT_18:,.0f} 亿（全A {B['amount_yi']:,.0f} 亿，她报 13,890 亿，差 1.3%），较昨缩 {abs(AMT_D):,.0f} 亿（{AMT_P:+.1f}%），<b>确为年内地量</b>。</td></tr>
</tbody>
</table>

<h2>二、大盘关键点位</h2>
<p class="meta" style="margin-bottom:6px">K 线<b>红涨绿跌</b>；关键位在图<b>左侧虚线</b>。数据源 <b>Tushare Pro 日线</b>（前复权），11/18 <b>完整收盘 K 线</b>。</p>

<h3>上证指数 · {SH['close']:.2f}（{SH['pct']:+.2f}%）</h3>
<img class="chart" src="../charts/000001_SH_20261118.png" alt="上证指数 2026-11-18 K线">
<p class="chart-caption">开 {SH['open']:.2f}（<b>= 当日最高</b>）/ 高 {SH['high']:.2f} / 低 <b>{SH_LO:.2f}</b> / 收 {SH['close']:.2f}。
<b>最低 {SH_LO:.2f} = 又是 60 日新低</b>（前低 3565.59 再破）；<b>3706 差 {SH_GAP:.2f} 点（{SH_GAP/3706*100:.2f}%）</b>，MA20 {SH['ma20']:.2f} 失守。</p>

<h3>创业板指 · {CY['close']:.2f}（{CY['pct']:+.2f}%）</h3>
<img class="chart" src="../charts/399006_SZ_20261118.png" alt="创业板指 2026-11-18 K线">
<p class="chart-caption">开 {CY['open']:.2f} / 高 {CY['high']:.2f} / 低 <b>{CY['low']:.2f}</b> / 收 {CY['close']:.2f}。
<b>最低 {CY['low']:.2f} &gt; 昨日 {CY_LO:.2f} → 她的 2263 点二次确认不破</b>；较日低拉回 {CY['close']-CY['low']:.2f} 点；<b>2626 差 {CY_GAP:.2f} 点（{CY_GAP/2626*100:.2f}%）</b>，MA20 {CY['ma20']:.2f} 远在头顶。</p>

<div class="risk">
  <b>⚠️ 地量普跌 ≠ 反转。</b>跌 {B['down']} 家 vs 涨 {B['up']} 家、成交额 {AMT_18:,.0f} 亿创年内新低、沪指再创 60 日新低；唯一改善是<b>跌停 {B17['dt']}→{B['dt']} 家</b>。
  她 09:26 说「等待构筑新波段」、14:28 说「缺乏力度」——<b>位置对了，力度没来</b>。今天能买的只有算力链涨停票，<b>明天缩量反弹不追高。</b>
</div>

<h2>三、最值得投资的 3 个板块</h2>
<table>
<thead><tr><th>板块</th><th>11/18 收盘实测</th><th>博主口径 / 打法</th></tr></thead>
<tbody>
<tr><td><b>① PCB / AI 服务器硬件</b><br><span class="tag tag-bull">首选 · 业绩最硬</span></td>
    <td>池 {p_pcb['n']} 只 <b class="up">{p_pcb['up']} 涨 {p_pcb['down']} 跌</b>，均值 <b class="up">{p_pcb['avg']:+.2f}%</b>，额 {p_pcb['amount_yi']:,.0f} 亿，<b>{p_pcb['zt']} 家涨停</b><br>
      {mem(p_pcb, 3)}</td>
    <td><b>她 13:53 点名「PCB龙头冲板」，兑现</b>。沪电 Q3 营收 <b>+71.9%</b>、ROE 31.5%、资产负债 52.5%。
    <b>但今日涨停、收 {HD['close']:.2f} 仍在 MA20 {HD['ma20']:.2f} 之下 → 首板不是反转</b>：回踩 {HD['lo60']:.2f} 不破才分批。</td></tr>
<tr><td><b>② 算力租赁 / IDC</b><br><span class="tag tag-bull">情绪主线 · 只做龙头</span></td>
    <td>池 {p_idc['n']} 只 <b class="up">{p_idc['up']} 涨 {p_idc['down']} 跌</b>，均值 <b class="up">{p_idc['avg']:+.2f}%</b>，额 {p_idc['amount_yi']:,.0f} 亿，<b>{p_idc['zt']} 家涨停</b><br>
      {mem(p_idc, 3)}</td>
    <td><b>她两次点名，兑现</b>，但 8 只涨停全是<b>低价题材票</b>（中嘉博创 3.38 元、营收 -9.0%）→ <b>不符合她「业绩增速明显」的公式</b>。
    <b>只做有业绩的：紫光股份 {ZG['close']:.2f} 站上 MA20 {ZG['ma20']:.2f}、营收 +32.1%</b>；涨停小票不碰。</td></tr>
<tr><td><b>③ GPU / 国产算力芯片</b><br><span class="tag tag-neutral">隔夜催化 · 11/19 才交易</span></td>
    <td>池 {p_gpu['n']} 只 <b class="up">{p_gpu['up']} 涨 {p_gpu['down']} 跌</b>，均值 <b class="up">{p_gpu['avg']:+.2f}%</b>，额 {p_gpu['amount_yi']:,.0f} 亿<br>
      {mem(p_gpu, 3)}</td>
    <td><b>21:07「英伟达停止对中国供应H200 #利好国产替代」</b>——催化在盘后。寒武纪 Q3 营收 <b>+106.8%</b>、毛利率 56.5%、资产负债 32.4%，最符合她「高成长+行业向好」。
    <b>11/19 高开不追，等回踩 MA20 {HX['ma20']:.2f}。</b></td></tr>
</tbody>
</table>
<p class="meta" style="margin-bottom:0">
  <b>回避</b>：白酒/食品饮料 <b class="down">{p_wine['avg']:+.2f}%</b>（0 涨 8 跌，11/17 唯一正收益池今天全绿）、军工 <b class="down">{p_mil['avg']:+.2f}%</b>、传媒 -3.12%、有色 -1.86%。
  <b>CPO/光通信</b> 池 {p_cpo['avg']:+.2f}% 弱反弹，中际旭创仍在 MA20 下方 {ZJ_GAP:.1f}% → <b>还没走出来</b>。
  申万一级：<b>通信 +1.57%</b> 唯一均值正收益，<b>计算机涨停 10 家最多</b>，电子 +0.03%（216 涨 272 跌）→ <b>结构性行情，非普涨</b>。
</p>

<h2>四、3 支个股</h2>
<table>
<thead><tr><th>代码 名称</th><th class="score">收盘</th><th class="score">涨跌</th>
<th class="score">成交额</th><th>关键位</th><th>实测印证 / 动作</th></tr></thead>
<tbody>
<tr><td><b>002463</b> 沪电股份</td><td class="score">{HD['close']:.2f}</td><td class="score"><span class="up">{HD['pct']:+.2f}%</span></td>
    <td class="score">{HD['amount_yi']:.1f} 亿</td><td>MA20 <b>{HD['ma20']:.2f}</b> · 60 日低 <b>{HD['lo60']:.2f}</b> · 60 日高 <b>{HD['hi60']:.2f}</b></td>
    <td class="text"><b>她 13:53 点名的 PCB 龙头</b>：收盘封板、放量 {HD['vol_ratio5']:.0f}%、Q3 营收 +71.9%。
    <b>但收盘仍低于 MA20 {HD['ma20']:.2f}、MACD 柱仅 +{HD['macd_bar']:.2f} → 首板不是反转</b>。今日不追，回踩 {HD['lo60']:.2f} 不破分批。</td></tr>
<tr><td><b>688256</b> 寒武纪</td><td class="score">{HX['close']:.2f}</td><td class="score"><span class="up">{HX['pct']:+.2f}%</span></td>
    <td class="score">{HX['amount_yi']:.1f} 亿</td><td>MA20 <b>{HX['ma20']:.2f}</b> · 60 日低 <b>{HX['lo60']:.2f}</b> · 60 日高 <b>{HX['hi60']:.2f}</b></td>
    <td class="text">正对她 10:47「高成长+行业向好」：Q3 营收 <b>+106.8%</b>、毛利率 56.5%。收 {HX['close']:.2f} <b>站上 MA20 {HX['ma20']:.2f}</b>、MACD 柱 +{HX['macd_bar']:.1f}（DIF 上穿 DEA）。
    <b>回踩 MA20 不破可分批，破位放弃；11/19 高开不追。</b></td></tr>
<tr><td><b>300308</b> 中际旭创</td><td class="score">{ZJ['close']:.2f}</td><td class="score"><span class="up">{ZJ['pct']:+.2f}%</span></td>
    <td class="score">{ZJ['amount_yi']:.1f} 亿</td><td>MA20 <b>{ZJ['ma20']:.2f}</b> · 60 日低 <b>{ZJ['lo60']:.2f}</b>（她的 385）</td>
    <td class="text">她 10:28 自验证那笔账（1416.88→385，-72.83%）。Q3 营收 <b>+178.1%</b> 全池最高；今日最低 {ZJ['low']:.2f} 未破 60 日低 {ZJ['lo60']:.2f}，二次探底不破。
    <b>但 MA20 {ZJ['ma20']:.2f} 远在头顶（差 {ZJ_GAP:.1f}%）、MACD 柱仍负 → 位置最低却未转势，不碰。</b></td></tr>
</tbody>
</table>

<h3>沪电股份（002463）· {HD['close']:.2f}（{HD['pct']:+.2f}%）</h3>
<img class="chart" src="../charts/002463_SZ_20261118.png" alt="沪电股份 2026-11-18 K线">
<p class="chart-caption">高 {HD['high']:.2f} = 收盘价（封板）/ 低 {HD['low']:.2f} / 收 {HD['close']:.2f}，额 {HD['amount_yi']:.1f} 亿。
涨停站上 MA5 {HD['ma5']:.2f}，但离 MA20 {HD['ma20']:.2f} 还差 {HD['ma20']-HD['close']:.2f} 元；60 日低 {HD['lo60']:.2f} 是支撑参考。</p>

<h3>寒武纪（688256）· {HX['close']:.2f}（{HX['pct']:+.2f}%）</h3>
<img class="chart" src="../charts/688256_SH_20261118.png" alt="寒武纪 2026-11-18 K线">
<p class="chart-caption">高 {HX['high']:.2f} / 低 {HX['low']:.2f} / 收 {HX['close']:.2f}，站上 MA5 {HX['ma5']:.2f} 与 MA20 {HX['ma20']:.2f}；60 日高 {HX['hi60']:.2f} 在左上（距今 {(HX['hi60']/HX['close']-1)*100:.1f}%），60 日低 {HX['lo60']:.2f} 在下方。</p>

<h3>中际旭创（300308）· {ZJ['close']:.2f}（{ZJ['pct']:+.2f}%）</h3>
<img class="chart" src="../charts/300308_SZ_20261118.png" alt="中际旭创 2026-11-18 K线">
<p class="chart-caption">高 {ZJ['high']:.2f} / 低 <b>{ZJ['low']:.2f}</b> / 收 {ZJ['close']:.2f}，额 {ZJ['amount_yi']:.1f} 亿（全场最大）。
距 60 日低 {ZJ['lo60']:.2f} 仅 {ZJ['dist_lo60']:.2f}%，但 MA20 {ZJ['ma20']:.2f} 压在头顶 {ZJ['ma20']/ZJ['close']*100-100:.1f}% 处 —— <b>底部区域，未转势</b>。</p>

<h2>五、11/19（周四）盯什么（5 条）</h2>
<ul class="tight">
  <li><b>她的 C5 之后给不给买点</b> —— 09:26 只说「等待构筑新波段行情」，<b>没给标的/点位/仓位</b>；11/19 仍不给就只是方向信号。</li>
  <li><b>沪指 60 日新低 {SH_LO:.2f} 不破</b> —— 破了说明 C5 判断还要下修。</li>
  <li><b>创业板 {CY_LO:.2f}（她的 2263 点）不破</b> —— 今日最低 {CY['low']:.2f}；破了看 2200 整数关。</li>
  <li><b>英伟达断供的兑现方式</b> —— 11/19 国产算力池能否<b>整体放量</b>走强（今天已 +{p_gpu['avg']:.2f}%，高开不追）。</li>
  <li><b>地量之后能不能放量</b> —— {AMT_18:,.0f} 亿创年内新低；<b>站上 1.5 万亿才算有承接</b>，否则缩量反弹不追。</li>
</ul>

<h2>六、偏差记录</h2>
<table>
<thead><tr><th>项</th><th>博主口径</th><th>实测 / 处理</th></tr></thead>
<tbody>
<tr><td>09:26「C5 低点区域」<br><span class="tag tag-bull">分毫不差</span></td><td class="text">昨日创业板指数试2263点，符合预期的C5低点区域了</td>
    <td class="text">11/17 创业板最低 <b>{CY_LO:.2f}</b> = 她的 2263 点；今日最低 {CY['low']:.2f} 未破 → <b>二次确认</b>。本期最硬的核验，也是<b>她第一次给「已到达」的点位</b>。</td></tr>
<tr><td>13:22 / 13:53 板块点名<br><span class="tag tag-bull">兑现</span></td><td class="text">算力租赁出现涨停潮，交换机连续反击，PCB龙头冲板</td>
    <td class="text">算力池 <b>{p_idc['zt']} 家涨停</b>、{p_idc['up']}涨{p_idc['down']}跌、均值 <b>{p_idc['avg']:+.2f}%</b>；PCB 池 <b>沪电+深南双涨停</b>、均值 {p_pcb['avg']:+.2f}%。<b>唯独交换机偏弱</b>（{p_sw['avg']:+.2f}%、0 涨停）。</td></tr>
<tr><td>21:07「利好国产替代」<br><span class="tag tag-neutral">盘后 · 未兑现</span></td><td class="text">#英伟达停止向中国供应H200#利好国产替代！</td>
    <td class="text"><b>发布于 21:07 收盘后，11/19 才交易</b>。今天 GPU 池 +{p_gpu['avg']:.2f}% 不是这条催化的结果 → <b>不能算她提前判断对了</b>。</td></tr>
<tr><td>14:20「看看铁几？」<br><span class="tag tag-neutral">未成主线</span></td><td class="text">看看铁几？</td>
    <td class="text">钢铁池 {P['钢铁']['avg']:+.2f}%、铁路运营 {P['铁路运营']['avg']:+.2f}%，<b>均无涨停</b>；收盘口径判不出盘中意图，<b>记为未成主线</b>。</td></tr>
<tr><td>11/17 报告标的名称<br><span class="tag tag-bear">更正</span></td><td class="text">11/17 报告把「1416.88→385」的标的写成「新易盛 300308」</td>
    <td class="text"><b>代码 300308 实为中际旭创，新易盛是 300502</b>（11/18 收 158.21）。11/17 的价格与跌幅计算没错，<b>错的是名称</b>，已更正。</td></tr>
</tbody>
</table>
<p class="meta" style="margin-bottom:0">
  其余 <b>9 条口径自洽</b>：09:48「这么压法」、13:31「C3/C5 分批布局」、14:28「缺乏力度」、14:40「看到一点希望」、20:28「今小红」等 —— 实测均吻合（地量、跌停 80→{B['dt']}、连板最高 4 板、涨停 42 家）。
  采集：weibo skill 两轮补采 → <b>14 条</b>（09:26–22:01）；行情：<b>Tushare Pro 日线</b>（前复权），全市场单次全量算涨跌停与板块均值。
</p>

<div class="foot">
  <p><b>免责声明</b>：本报告为公开微博内容整理与技术面统计，<b>不构成投资建议</b>；
  「3 板块 + 3 个股」是博主观点 + 实测强度的归纳，股市有风险，谨慎。</p>
  <p>
    报告生成：2026-11-18 收盘版 · 数据源 weibo skill + Tushare Pro 日线 ·
    脚本 <code>collect_tushare_20261118.py</code> / <code>collect_pools_20261118.py</code> /
    <code>collect_mkt_20261118.py</code> / <code>make_wu2198_charts_20261118.py</code> /
    <code>gen_wu2198_report_20261118.py</code>。
  </p>
</div>

</div>
</body>
</html>
"""

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fix_mobile_tables import patch_html

if __name__ == "__main__":
    out = ROOT / "html" / "wu2198-20261118.html"
    out.write_text(patch_html(HTML), encoding="utf-8")
    print(f"[out] {out}  ({len(HTML)} bytes)")
