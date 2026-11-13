"""生成 2026-11-11 都业华《高级班收评》纪要 HTML（白底）

数据源：Tushare Pro（行情/指数/全市场宽度）+ 新浪 15 分钟 K + czsc（缠论分型笔）
原始数据：~/workspace/mnote.github.io/reports/duyiehua-20261111/data_20261111.json
输出：~/workspace/mnote.github.io/2026-11-11-都业华-高级班收评纪要.html
"""
import json
from pathlib import Path

REPO = Path("/Users/maoling/workspace/mnote.github.io")
RPT = REPO / "reports/duyiehua-20261111"
D = json.loads((RPT / "data_20261111.json").read_text(encoding="utf-8"))

IDX, MKT, BASKET, CZV, QUOTES = D["index"], D["market"], D["basket"], D["czsc"], D["quotes"]
XUAN = D.get("xuanxue", {})
TODAY, PREV = "20261111", "20261110"

OUT = REPO / "2026-11-11-都业华-高级班收评纪要.html"

TITLE_SUMMARY = "温度35度，机器人升一类热点"          # 14 字
TITLE_FULL = f"DYH 收评 - 2026-11-11（周三 {TITLE_SUMMARY}）"

CSS = """<style>
  :root {
    --bg:#ffffff; --panel:#f8f9fb; --panel-2:#f1f3f6;
    --border:#e5e7eb; --border-strong:#d1d5db;
    --text:#1f2937; --muted:#6b7280;
    --bull:#16a34a; --bull-bg:#dcfce7;--up:#e63946;--down:#2a9d8f;
    --bear:#dc2626; --bear-bg:#fee2e2;
    --neutral:#d97706; --neutral-bg:#fef3c7;
    --none:#6b7280; --none-bg:#f3f4f6;
    --accent:#2563eb; --accent-bg:#dbeafe;
    --key:#7c3aed; --key-bg:#ede9fe;
  }
  *{box-sizing:border-box}
  body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei","Segoe UI",sans-serif;
       background:var(--bg);color:var(--text);line-height:1.7;font-size:15px}
  .wrap{max-width:1200px;margin:0 auto;padding:32px 24px 80px}
  h1,h2,h3,h4{font-weight:600;line-height:1.3}
  h1{font-size:27px;margin:0 0 8px}
  h2{font-size:20px;margin:38px 0 14px;padding-bottom:8px;border-bottom:2px solid var(--border)}
  h3{font-size:17px;margin:24px 0 10px}
  h4{font-size:15px;margin:16px 0 8px;color:var(--muted);font-weight:500}
  p{margin:8px 0}
  a{color:var(--accent);text-decoration:none}
  .meta{color:var(--muted);font-size:13px}.meta span{margin-right:14px}
  .hero{background:linear-gradient(135deg,#f0f9ff 0%,#f8fbff 100%);border:1px solid #7dd3fc;border-radius:12px;padding:22px 26px;margin-bottom:26px}
  .hero h1{color:#0c4a6e}
  .hero .stance{font-size:15.5px;margin:10px 0 0}
  .quote{background:var(--panel);border-left:4px solid var(--border-strong);border-radius:8px;padding:12px 16px;margin:10px 0;font-size:14.5px}
  .quote .who{color:var(--muted);font-size:12px;display:block;margin-bottom:5px}
  .verify{background:var(--accent-bg);border-radius:8px;padding:10px 14px;margin:10px 0;font-size:14px}
  .risk{background:var(--bear-bg);border-radius:8px;padding:10px 14px;margin:10px 0;font-size:14px}
  .action{background:var(--bull-bg);border-radius:8px;padding:10px 14px;margin:10px 0;font-size:14px}
  .panel{background:var(--panel);border:1px solid var(--border);border-radius:10px;padding:16px 20px;margin:16px 0}
  .grid-4{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}
  @media(max-width:900px){.grid-4{grid-template-columns:1fr 1fr}}
  @media(max-width:760px){.grid-4{grid-template-columns:1fr}}
  .kpi{background:#fff;border:1px solid var(--border);border-radius:8px;padding:12px 14px;text-align:center}
  .kpi .label{font-size:12px;color:var(--muted);letter-spacing:.5px}
  .kpi .val{font-size:20px;font-weight:600;margin:4px 0}
  .kpi .sub{font-size:12px;color:var(--muted)}
  table{width:100%;border-collapse:collapse;margin:12px 0;font-size:14px}
  th,td{padding:8px 10px;text-align:left;border-bottom:1px solid var(--border);vertical-align:top}
  th{background:var(--panel-2);font-weight:600;color:var(--muted);font-size:12px}
  tr:hover{background:var(--panel)}
  td.num{font-variant-numeric:tabular-nums;text-align:right;white-space:nowrap}
  .tag{display:inline-block;padding:2px 8px;border-radius:999px;font-size:11px;font-weight:500;margin:0 2px}
  .tag-bull{background:var(--bull-bg);color:var(--bull)}
  .tag-bear{background:var(--bear-bg);color:var(--bear)}
  .tag-neutral{background:var(--neutral-bg);color:var(--neutral)}
  .tag-none{background:var(--none-bg);color:var(--none)}
  .tag-accent{background:var(--accent-bg);color:var(--accent)}
  .tag-key{background:var(--key-bg);color:var(--key)}
  .chart{width:100%;height:auto;display:block;margin:12px 0;border:1px solid var(--border);border-radius:6px;background:#fff}
  .cap{font-size:12px;color:var(--muted);margin:-4px 0 18px}
  .up{color:var(--up);font-weight:600}
  .down{color:var(--down);font-weight:600}
  .flat{color:var(--muted);font-weight:600}
  .kn{color:var(--key);font-weight:700;font-variant-numeric:tabular-nums}
  .foot{margin-top:48px;padding-top:20px;border-top:1px solid var(--border);font-size:12px;color:var(--muted)}
  ul.tight{margin:8px 0;padding-left:22px}ul.tight li{margin:4px 0}
  .sector{background:#fff;border:1px solid var(--border);border-left:4px solid var(--accent);border-radius:10px;padding:16px 20px;margin:16px 0}
  .sector.r1{border-left-color:#16a34a}
  .sector.r2{border-left-color:#d97706}
  .sector.r3{border-left-color:#7c3aed}
  .vol{color:var(--neutral);font-weight:600}
</style>"""


def cls(v):
    return "up" if v > 0 else ("down" if v < 0 else "flat")


def pct(v):
    return f"{v:+.2f}%"


def q(name):
    for r in QUOTES:
        if r["名称"] == name:
            return r
    return None


def qs(name):
    r = q(name)
    if not r:
        return "—"
    return f'<span class="{cls(r["涨跌幅%"])}">{r["收盘"]:.2f} ({pct(r["涨跌幅%"])})</span>'


def zs15(name):
    z = ((CZV.get(name) or {}).get("m15") or {}).get("zs_now")
    return f"{z['ZD']}–{z['ZG']}" if z else "—"


def zsM(name):
    z = ((CZV.get(name) or {}).get("month") or {}).get("zs_now")
    return f"{z['ZD']}–{z['ZG']}" if z else "—"


def bi15(name):
    b = ((CZV.get(name) or {}).get("m15") or {}).get("bi")
    if not b:
        return "—"
    b = b[-1]
    return f"末笔{b['dir']}（{b['edt'][5:16]}，力度 {b['power']}）"


def biM(name):
    b = ((CZV.get(name) or {}).get("month") or {}).get("bi")
    if not b:
        return "—"
    b = b[-1]
    return f"月线末笔{b['dir']}（{b['edt']}，力度 {b['power']}）"


def chart(code, name, caption, prefix="charts/"):
    return (f'<img class="chart" src="{prefix}{code}_DY_20261111.png" alt="{name}">'
            f'<div class="cap">{caption}</div>')


sh, sz, cy, kc, hs = IDX["上证指数"], IDX["深证成指"], IDX["创业板指"], IDX["科创50"], IDX["沪深300"]
T, P = MKT[TODAY], MKT[PREV]
amt_chg = round((T["amount_yi"] / P["amount_yi"] - 1) * 100, 1)
zt_ind = MKT.get("zt_by_industry", {})
zt_top = list(zt_ind.items())[:10]

bask_rows = []
for bname, b in BASKET.items():
    bask_rows.append(
        f'<tr><td>{bname}</td><td class="num {cls(b["avg_pct"])}">{b["avg_pct"]:+.2f}%</td>'
        f'<td class="num">{b["median_pct"]:+.2f}%</td><td class="num">{b["up"]} / {b["n"]}</td>'
        f'<td class="num">{b["zt"]}</td></tr>')

# 涨停行业归链（按行业口径归入主线）
zt_robot = zt_ind.get("专用机械", 0) + zt_ind.get("汽车配件", 0) + zt_ind.get("机械基件", 0)
zt_compute = zt_ind.get("通信设备", 0) + zt_ind.get("元器件", 0) + zt_ind.get("半导体", 0)

x9, x10, x11 = XUAN.get("20261109", {}), XUAN.get("20261110", {}), XUAN.get("20261111", {})
xu_rows = "".join(
    f'<tr><td>{d}</td><td class="num">{x.get("zt_n", 0)}</td>'
    f'<td>{"、".join(x.get("zt", [])) or "—"}</td>'
    f'<td>{"、".join(f"{n} {p:+.2f}%" for n, p in x.get("yang", [])) or "—"}</td></tr>'
    for d, x in (("11/09", x9), ("11/10", x10), ("11/11", x11)))

HTML = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{TITLE_FULL}</title>
{CSS}
</head>
<body>
<div class="wrap">

<div class="hero">
  <h1>📈 {TITLE_FULL}</h1>
  <div class="meta">
    <span>🕘 收评时间：2026-11-11 收盘后</span>
    <span>📡 数据源：都业华《高级班》收评原文 + Tushare Pro</span>
    <span>💹 行情：Tushare Pro（11/11 收盘 · 前复权）</span>
    <span>🔮 缠论核验：czsc（新浪 15 分钟 K + 日线聚合月线/周线 · 三笔重叠算中枢）</span>
    <span>📌 执业编号 A0400626100004</span>
  </div>
  <p class="stance"><b>结论先行：</b>市场温和上涨，<b>创业板 +{cy['pct']}%、科创50 +{kc['pct']}%</b> 领涨，但指数级仍属<b>弱势</b>——上证 15 分钟下跌中枢 {zs15('上证指数')} 继续延伸，向上未破 3750，<b>向下今日最低 {sh['low']} 已微幅跌破 11/09 前低 3653.05，「创新低」条件在尾盘前的日内已经触发</b>，收盘 {sh['close']} 拉回中枢内；1 分钟中枢尝试向上离开但<b>力度不够</b>。市场温度由 25 度升到 <b>35 度</b>，<b>人形机器人升为一类热点</b>。总仓位上限 <b>4 成</b>、谨慎不追涨；中线扩到 <b>8 只</b>（新增中文在线、海天瑞声转中线、奥普特、柯力传感），短线只剩 2 只，<b>全部不给买点</b>，仅给触发条件与止损位。<br><b>本期实测与老师口径有三处不一致</b>：① 当日涨幅与涨停家数最强的是<b>算力硬件</b>（篮子均值 +{BASKET['算力硬件']['avg_pct']:.2f}%、涨停链 {zt_compute} 只）而非人形机器人（+{BASKET['人形机器人']['avg_pct']:.2f}%、{zt_robot} 只）；② 「端侧 AI 比超跌半导体更强」在<b>自建篮子口径上相反</b>（端侧 {BASKET['端侧AI']['avg_pct']:+.2f}% ＜ 半导体 {BASKET['半导体']['avg_pct']:+.2f}%），仅在老师点名的瑞芯微（+{q('瑞芯微')['涨跌幅%']:.2f}%）上成立；③ 同花顺全A 的 1325 点<b>本机无数据源，无法核验</b>。</p>
</div>

<div class="grid-4">
  <div class="kpi"><div class="label">上证指数</div><div class="val up">{pct(sh['pct'])}</div><div class="sub">{sh['close']} · 高 {sh['high']} 低 {sh['low']} · {sh['vol_bear_ma']}</div></div>
  <div class="kpi"><div class="label">创业板指 / 科创50</div><div class="val up">{pct(cy['pct'])} / {pct(kc['pct'])}</div><div class="sub">{cy['close']} · {kc['close']} · 沪深300 {pct(hs['pct'])}</div></div>
  <div class="kpi"><div class="label">全 A 成交额</div><div class="val vol">{T['amount_yi']} 亿</div><div class="sub">较前日 {P['amount_yi']} 亿 {pct(amt_chg)} · 略放</div></div>
  <div class="kpi"><div class="label">涨 / 跌 家数</div><div class="val"><span class="up">{T['up']}</span> / <span class="down">{T['down']}</span></div><div class="sub">涨停级 {T['zt_ge98']} · 跌停级 {T['dt_le98']} · 中位 {T['median_pct']}%</div></div>
</div>

<div class="panel">
  <h4>老师原文立场（2026-11-11 收评）</h4>
  <div class="quote"><span class="who">指数</span>市场温和上涨，创业板和科创板指数涨幅力度稍大，结构本身没有大的变化，成交量略放，但<b>均量线还是空头排列</b>。上证指数 15 分钟依旧维持下跌中枢延伸，观察中枢方向选择：<b>向上需突破压力 3750 点后出回抽确认三买；向下要创新低出底背驰，目前定性为弱势</b>。总仓位上限控制在 4 成，谨慎不追涨。上证指数内部 1 分钟中枢今日尝试向上离开，但<b>力度不够，效果不好，延续性不强</b>。<b>同花顺全A 指数站上 20 日均线，明日走势不能回头，转强需要向上突破 1325 点后出三买</b>。被套仓位：仓位轻可酌情结合反弹高抛，或结合短线高低点灵活高抛低吸倒差价；仓位重建议不硬顶也不额外加仓，心态压力大可酌情主动降低部分仓，或在个股无基本面风险前提下等反弹。交易心态不要消极，理清思路。买点买、卖点卖，做好风控设置好止损，仓位控制好；对市场要有耐心。</div>
  <div class="quote"><span class="who">板块</span>市场温度 <b>35 度</b>（第一天上 30 度）。<b>一类热点：人形机器人</b>，二类热点：玄学链。盘面市场有热点延续迹象，<b>人形机器人炒的是增量，围绕数据采集等</b>。AI 视频比较活跃但无法上热点榜，走势延续向上还没有摆脱顶背驰风险，可观察后续走势变化。算力硬件中<b>半导体板块今日先看成超跌反弹</b>，因为前期跌幅大所以反弹力度稍大，<b>走势转强需要先突破上方压力，防范无法突破压力转成三卖</b>。<b>端侧 AI 比超跌的半导体等更强一些</b>。板块强弱排序：<b>人形机器人＞AI 视频＞算力硬件</b>。玄学链中「羊字辈」到带「东方」字样题材<b>不作为重点推荐</b>，因为个股操作难度大、节奏不好把握，<b>防范资金撤出</b>。</div>
  <div class="quote"><span class="who">中线股（8 只）</span>药明康德（大医药，走势下跌延续，<b>无买点、没有 15 分钟二买</b>，当下做出窄幅震荡雏形；结合医药方向的凯莱英走势建议等共振结构；昭衍新药共振雏形出现，需等突破后的三买；板块不是热点、防守性质，可以不用太着急）；中国船舶（无买点，未摆脱 15 分钟下跌中枢延伸，结构没见底止跌，等收复上沿后做 15 分钟共振上涨中枢）；瑞芯微（端侧 AI，无买点，日线前高上沿位置震荡，不建议追涨，<b>等向上突破后出日线底分型回抽确认高点 248.49 元的三买</b>，或等走势拉回中枢做共振结构）；伊利股份（大消费防守，无买点，日线顶分型向下回调到下沿附近，<b>等跌破支撑 30.46 元再拉回出日线有力度底分型</b>）；<b>中文在线（新增，AI 视频）</b>——体量大、业绩不是很好，月线强势震荡、结构出月线底分型，不追涨，<b>等突破压力高点 30.38 元后出 15 分钟底分型的三买机会</b>；<b>海天瑞声（新增 / 短线转中线，机器人）</b>——月线中枢震荡，第一波上涨起来比较猛，不建议直接追买，<b>等 15 分钟做出类二买结构后寻找机会</b>；<b>奥普特（新增，机器视觉）</b>——月线卡在前高震荡，要么等回调到临近中枢下沿找止跌机会，要么等突破高点 186.8 元后出日线底分型三买（稳健）/ 15 分钟底分型三买机会（激进）；<b>柯力传感（新增，六维传感器）</b>——月线向下突破后尝试被拉回，观察是否是假突破，等日线顶分型调整后的止跌机会。</div>
  <div class="quote"><span class="who">短线股（2 只）</span>兆易创新（无买点，震荡向上拉升，<b>没出 15 分钟底分型三买</b>，可继续等待观察三买机会；自行参与者建议设好止损，比如 <b>249 元附近</b>）；海天瑞声（人形机器人，<b>转中线跟踪，短线剔除</b>）；云铝股份（非热点，震荡向下、无买点，走势回到下沿，先观察是否止跌，辅助日线有力度底分型出现后小级别做共振机会）。</div>
</div>

<h2>一、指数：温和上涨，但结构未变、均量线仍空头排列</h2>
<p>实测：上证 <span class="up">{pct(sh['pct'])}</span> 收 {sh['close']}（高 {sh['high']} 低 {sh['low']}），深成指 <span class="up">{pct(sz['pct'])}</span>，<b>创业板指 <span class="up">{pct(cy['pct'])}</span>、科创50 <span class="up">{pct(kc['pct'])}</span></b>，沪深300 {pct(hs['pct'])}。<b>「创业板和科创板涨幅力度稍大、结构本身没有大的变化」成立</b>：涨幅集中在成长端，权重与主板几乎没动（沪深300 仅 {pct(hs['pct'])}）。</p>
<p>全 A 成交额 {T['amount_yi']} 亿，较前一日 {P['amount_yi']} 亿<b>放量 {amt_chg}%</b>——「成交量略放」成立。但<b>均量线仍空头排列</b>：上证 5 日均量 {sh['vol_ma5']:,.0f} 手 &lt; 20 日均量 {sh['vol_ma20']:,.0f} 手（判定「{sh['vol_bear_ma']}」），即短期成交量虽回升，中期均量趋势仍未扭转。</p>
<p>涨跌家数 <span class="up">{T['up']}</span> / <span class="down">{T['down']}</span>（平 {T['flat']}），中位数 <span class="up">{T['median_pct']}%</span>，涨幅≥9.8% 共 {T['zt_ge98']} 只、跌幅≤-9.8% 共 {T['dt_le98']} 只。较 11/10（{P['up']} 涨 / {P['down']} 跌）<b>宽度有所收敛</b>，涨停级从 {P['zt_ge98']} 降到 {T['zt_ge98']}、跌停级从 {P['dt_le98']} 升到 {T['dt_le98']}——指数上涨但个股参与度下降，这是老师把行情定性为「温和上涨、结构没大变化」的盘面依据。</p>

{chart("000001_SH", "上证指数", f"上证指数（000001.SH）日线 · 15 分钟下跌中枢 {zs15('上证指数')} 自 11/05 未变、继续延伸；向上确认位 3750 未突破；今日最低 {sh['low']} 微幅跌破 11/09 前低 3653.05，收盘拉回中枢内；5 日均量仍低于 20 日均量。")}
{chart("399006_SZ", "创业板指", f"创业板指（399006.SZ）日线 · 今日 {pct(cy['pct'])} 领涨，收 {cy['close']}，在 15 分钟中枢 {zs15('创业板指')} 内运行、逼近上沿未站稳。")}

<div class="verify"><b>缠论核验（15 分钟，czsc 独立复算）：</b>上证当前中枢 <span class="kn">{zs15('上证指数')}</span>，<b>与 11/09、11/10 两期完全一致（中枢区间与形成时间均未变），说明下跌中枢仍在延伸、今日未选择方向</b>。两个观察条件中：<b>向上 3750 未触</b>（最高 {sh['high']}）；<b>向下「创新低」已触发</b>——今日最低 {sh['low']} 低于 11/09 前低 3653.05，幅度仅 2.74 点（0.07%），收盘 {sh['close']} 又拉回中枢内。<b>「向上需突破 3750 后回抽确认三买、向下要创新低出底背驰」的框架成立，且今日向下那一侧已被触及但幅度极小</b>：能否构成底背驰，还要看后续下跌笔的力度是否衰减（本机 1 分钟结构不可得，无法直接复算）。</div>

<div class="verify"><b>「1 分钟中枢今日尝试向上离开但力度不够」——旁证：</b>上证全天自最低 {sh['low']} 拉起收于 {sh['close']}，但收盘位置处于全天区间中位偏上、<b>未能站上全天最高 {sh['high']}</b>，收盘涨幅 {pct(sh['pct'])} 明显弱于创业板 {pct(cy['pct'])} 与科创50 {pct(kc['pct'])}，<b>离场力度弱于成长端，与「力度不够、延续性不强」一致</b>。</div>

<div class="risk"><b>「同花顺全A 站上 20 日均线 / 突破 1325 点出三买」——本机无法独立核验：</b>同花顺全A（881001）在东方财富与 Tushare 均无数据接口（本次采集期间东财接口又对本机限流），<b>1325 点无法核对</b>。可用的替代口径（全 A 日线统计）：成交额放量 {amt_chg}%、上涨家数 {T['up']} 明显多于下跌 {T['down']}、中位数 +{T['median_pct']}%，<b>量能与宽度均支持「转强」方向</b>，但具体点位需老师系统或同花顺终端确认。</div>

<h2>二、板块热点：温度 35 度，人形机器人升为一类热点</h2>

<div class="sector r1">
  <h3>2.1 板块强弱排序：老师口径「人形机器人＞AI 视频＞算力硬件」，实测强度排序不同</h3>
  <table>
    <tr><th>方向（我方测算篮子）</th><th>样本均值</th><th>中位数</th><th>上涨/样本</th><th>涨停级家数</th></tr>
    {"".join(bask_rows)}
  </table>
  <div class="verify"><b>实测排序：算力硬件 {BASKET['算力硬件']['avg_pct']:+.2f}% ＞ 人形机器人 {BASKET['人形机器人']['avg_pct']:+.2f}% ＞ AI 视频/传媒 {BASKET['AI视频/传媒']['avg_pct']:+.2f}% ＞ 半导体 {BASKET['半导体']['avg_pct']:+.2f}% ＞ 端侧 AI {BASKET['端侧AI']['avg_pct']:+.2f}% ＞ 光伏设备 {BASKET['光伏设备']['avg_pct']:+.2f}%。</b>与老师排序比对：<b>「AI 视频＞算力硬件」这一段不成立</b>——算力硬件是当日涨幅最大、涨停最多的方向；「人形机器人＞AI 视频」成立。<br><span class="cap">口径说明：东财概念板块接口本次不可用，改为按每条主线自建代表股篮子（每条 6–18 只）计算均值与涨停家数，为<b>本纪要测算</b>，非官方板块指数；篮子成分见附录。</span></div>
  <div class="risk"><b>但老师的「一类热点」判断在题材维度成立：</b>机器人链的涨停是<b>零部件全面扩散</b>（专用机械 13 只含杰普特/光智科技/佰奥智能/博杰股份等，汽车配件 10 只含兆丰股份/浙江世宝/襄阳轴承/光洋股份等丝杠轴承线，机械基件 5 只含瑞迪智驱/锋龙股份/永和智控等减速器线），合计 <b>{zt_robot} 只</b>，正对应「<b>炒的是增量，围绕数据采集等</b>」的定性——是中小市值的新资金进场，而非大票轮动。</div>
  <div class="verify"><b>对照算力链：</b>通信设备 17 只 + 元器件 14 只 + 半导体 4 只 = <b>{zt_compute} 只</b>，且集中在<b>大票</b>——中际旭创 +15.07%（收 542.00）、新易盛 +16.98%（收 215.00）、天孚通信 +13.96%、胜宏科技 +9.92%、深南电路、沪电股份、景旺电子涨停。这解释了老师说的「<b>创业板和科创板指数涨幅力度稍大</b>」：<b>创业板的权重正是这些算力硬件标的</b>。<br><b>因此「指数涨幅力度」与「热点分类」指向两个不同的方向</b>——量在算力硬件，题材在人形机器人。这不是矛盾，是两条线并行。</div>
</div>

<div class="sector r1">
  <h3>2.2 人形机器人升为一类热点：涨停行业分布（客观口径）</h3>
  <table>
    <tr><th>涨停行业（申万口径，Tushare 全 A 统计）</th><th>涨停级家数</th><th>主线归类</th><th>代表涨停个股</th></tr>
    <tr><td>通信设备</td><td class="num">{zt_ind.get('通信设备', 0)}</td><td>算力硬件（光模块/CPO）</td><td>新易盛、中际旭创、天孚通信、太辰光、仕佳光子、联特科技、光库科技、光迅科技、长飞光纤、剑桥科技</td></tr>
    <tr><td>元器件</td><td class="num">{zt_ind.get('元器件', 0)}</td><td>算力硬件（PCB/覆铜板）+ 散热</td><td>胜宏科技、深南电路、沪电股份、景旺电子、致尚科技、秋田微、南亚新材、炬光科技、中石科技</td></tr>
    <tr><td>专用机械</td><td class="num">{zt_ind.get('专用机械', 0)}</td><td>人形机器人 + 液冷 + 光伏设备</td><td>同飞股份、杰普特、光智科技、唯科科技、佰奥智能、科瑞技术、英维克、博杰股份</td></tr>
    <tr><td>汽车配件</td><td class="num">{zt_ind.get('汽车配件', 0)}</td><td>人形机器人（丝杠/轴承/线控）</td><td>德尔股份、兆丰股份、浙江世宝、岱美股份、襄阳轴承、光洋股份、新坐标、金麒麟</td></tr>
    <tr><td>机械基件</td><td class="num">{zt_ind.get('机械基件', 0)}</td><td>人形机器人（减速器）</td><td>瑞迪智驱、锋龙股份、永和智控、申科股份、宁波东力</td></tr>
    <tr><td>半导体</td><td class="num">{zt_ind.get('半导体', 0)}</td><td>算力硬件（光芯片/算力芯片）</td><td>利扬芯片、源杰科技、长光华芯、燧原科技</td></tr>
    <tr><td>互联网 / 出版业 / 影视音像</td><td class="num">{zt_ind.get('互联网', 0)} / {zt_ind.get('出版业', 0)} / {zt_ind.get('影视音像', 0)}</td><td>AI 视频 / 传媒</td><td>凯撒文化（+10.06%）、果麦文化（+20.00%）、文投控股（+10.18%）、上海电影（+10.01%）、中信出版（+10.86%）</td></tr>
  </table>
  <div class="verify"><b>「无法上热点榜」的旁证：</b>AI 视频/传媒方向的涨停级个股仅 <b>{BASKET['AI视频/传媒']['zt']} 只</b>（凯撒文化），而通信设备 {zt_ind.get('通信设备', 0)} 只、专用机械 {zt_ind.get('专用机械', 0)} 只——<b>强度与扩散度都明显不足，符合「比较活跃但无法上热点榜」</b>。同时老师 11/10 午评已提示 AI 视频 15 分钟末笔力度 54.98 &lt; 前笔 76.91（衰减 28.5%）的顶背驰要素，<b>今日仍未摆脱</b>——该板块属「走势延续向上但需防回头」状态，不宜追。</div>
</div>

<div class="sector r2">
  <h3>2.3 算力硬件：当日最强，但老师定性为「半导体先看成超跌反弹、防转三卖」</h3>
  <div class="verify"><b>实测印证：</b>算力硬件篮子均值 <span class="up">{BASKET['算力硬件']['avg_pct']:+.2f}%</span>（11 只全涨、涨停级 {BASKET['算力硬件']['zt']} 只），半导体篮子 <span class="up">{BASKET['半导体']['avg_pct']:+.2f}%</span>（兆易创新 +6.15%、澜起科技 +5.21%）。涨幅集中在<b>前期跌幅大的品种</b>——兆易创新 60 日涨幅仍为 {q('兆易创新')['60日涨幅%']}%、距 60 日高 {q('兆易创新')['距60日高%']}%，半导体是典型超跌修复。<b>「走势转强需要先突破上方压力，防范无法突破压力转成三卖」正是当前位置的风险点</b>：压力位未破之前，任何追涨都要按「反弹而非反转」处理。</div>
  <div class="risk"><b>排序与老师口径相反，需要留意：</b>老师把算力硬件排在第三，实测它是当日最强方向（篮子均值 +{BASKET['算力硬件']['avg_pct']:.2f}%、涨停链 {zt_compute} 只）。<b>但「强度最强」与「可持续」是两回事</b>——算力链的涨停集中在大票、而老师同时提醒半导体是超跌反弹且防转三卖；若明日算力硬件无法延续、掉头回落，则今天的强度只是反弹而非趋势，<b>老师的排序更像是在提示「不要去追最强的、要看有增量的」</b>。这是本期最需要跟踪验证的一处分歧。</div>
</div>

<div class="sector r2">
  <h3>2.4 端侧 AI vs 超跌半导体：老师口径与篮子口径相反</h3>
  <div class="verify"><b>实测：</b>端侧 AI 篮子 <span class="down">{BASKET['端侧AI']['avg_pct']:+.2f}%</span>（10 只中仅 3 只上涨，传音控股 -3.35%、领益智造 -2.94%、歌尔股份 -2.14% 拖累）<b>＜</b> 半导体篮子 <span class="up">{BASKET['半导体']['avg_pct']:+.2f}%</span>，<b>与「端侧 AI 比超跌的半导体等更强一些」相反</b>。但老师本期点名的端侧标的<b>瑞芯微 +{q('瑞芯微')['涨跌幅%']:.2f}%</b> 确实上涨（收 {q('瑞芯微')['收盘']}，15 分钟中枢上移至 {zs15('瑞芯微')}）。<br><b>判定：在老师指定标的上成立、在自建篮子口径上不成立</b>——差异来自篮子把消费电子链（歌尔/领益/蓝思/水晶光电）纳入端侧，而当日这批是回调而非领涨。消费电子链当日回调，与「前期涨幅大、今天在回吐」的解释一致。</div>
</div>

<div class="sector r3">
  <h3>2.5 玄学链：涨停家数持平不退，但结构已明显走弱</h3>
  <table>
    <tr><th>日期</th><th>涨停级家数</th><th>涨停名单</th><th>「羊字辈」表现</th></tr>
    {xu_rows}
  </table>
  <div class="verify"><b>实测印证：</b>11/09 涨停 8 只 → 11/10 收敛到 4 只 → <b>11/11 维持 4 只</b>，但<b>成分换了</b>：11/10 的东方新能掉出，新增东方通信（+9.99%）；日出东方、东方环宇、大东方<b>连续两日涨停</b>。同时<b>「羊字辈」今日转跌</b>（三羊马 -2.57%、水羊股份 -4.15%，前两日均为上涨）。<b>「防范资金撤出」成立</b>：涨停家数不再扩散、剩余标的分散在家用电器/供气供热/医疗保健等<b>非主线行业</b>（唯一强势的东方通信实际归属通信设备/算力链）、龙头高度仅 2 板、羊字辈掉头向下——这条链已连续三日退潮，不作为重点推荐的处理是正确的。</div>
</div>

<h2>三、中线股（8 只）：4 只新增，全部不给买点</h2>
<p>老师纪律：先结合市场强弱评估仓位上限；可操作仓内分仓，持仓 3–5 只，<b>试探性第一笔约为该股仓位的 5%</b>；买点买、卖点卖、做好风控；中线走势没坏前建议持有，但内部会有短线回调，想好自己的买卖策略。</p>
<table>
  <tr><th>标的</th><th>题材</th><th>收盘</th><th>老师定性</th><th>15 分钟中枢（实测）</th><th>触发条件</th><th>动作</th></tr>
  <tr>
    <td><b>药明康德</b><br>603259</td><td>大医药</td>
    <td class="num">{qs('药明康德')}</td>
    <td>走势下跌延续，<b>无买点、没有 15 分钟二买</b>，当下做出窄幅震荡雏形</td>
    <td class="kn">{zs15('药明康德')}<br><span class="cap">{bi15('药明康德')}</span></td>
    <td>结合<b>凯莱英</b>走势建议等共振结构；<b>昭衍新药</b>共振雏形出现，需等突破后的三买<br><span class="cap">实测：15 分钟末笔<b>向下</b>（力度 {((CZV['药明康德']['m15']['bi'][-1])['power'])}），无底分型二买；收 {q('药明康德')['收盘']} 回到中枢 {zs15('药明康德')} 内 → <b>窄幅震荡雏形成立</b>。但<b>今日共振不成立</b>：药明康德 {pct(q('药明康德')['涨跌幅%'])}，凯莱英 +0.36%、昭衍新药 0.00%</span></td>
    <td><span class="tag tag-none">观望（防守）</span></td>
  </tr>
  <tr>
    <td><b>中国船舶</b><br>600150</td><td>船舶</td>
    <td class="num">{qs('中国船舶')}</td>
    <td><b>无买点</b>，未摆脱 15 分钟下跌中枢延伸，结构没见底止跌</td>
    <td class="kn">{zs15('中国船舶')}<br><span class="cap">{bi15('中国船舶')}</span></td>
    <td>等<b>收复上沿</b>后做 15 分钟共振上涨中枢再找机会<br><span class="cap">实测：<b>中枢已下移</b>——11/10 的 [35.00–35.58] 变为 {zs15('中国船舶')}；今日高 {q('中国船舶')['最高']}（= 新中枢上沿）、低 {q('中国船舶')['最低']}（低于下沿 34.10）、收 {q('中国船舶')['收盘']}，末笔向上但力度仅 {((CZV['中国船舶']['m15']['bi'][-1])['power'])}（前笔 {((CZV['中国船舶']['m15']['bi'][-2])['power'])}）→ <b>下跌中枢延续且重心下移，老师的「等收复上沿」目标位应更新为 34.34</b></span></td>
    <td><span class="tag tag-none">观望</span></td>
  </tr>
  <tr>
    <td><b>瑞芯微</b><br>603893</td><td>端侧 AI</td>
    <td class="num">{qs('瑞芯微')}</td>
    <td><b>无买点</b>，日线前高上沿位置震荡，不建议追涨</td>
    <td class="kn">{zs15('瑞芯微')}<br><span class="cap">{bi15('瑞芯微')}</span></td>
    <td>等向上突破后出日线底分型回抽确认<b>高点 248.49</b> 的三买；或等走势拉回中枢做共振结构<br><span class="cap">实测：中枢由 [211.28–221.00] 上移至 {zs15('瑞芯微')}，今日高 {q('瑞芯微')['最高']}（60 日新高）、收 {q('瑞芯微')['收盘']} 在中枢内 → <b>「拉回中枢做共振结构」这一条今日已成立</b>；但<b>三买条件未成立</b>（距 248.49 还差 {round((248.49 / q('瑞芯微')['收盘'] - 1) * 100, 1)}%）。月线中枢 {zsM('瑞芯微')}，{biM('瑞芯微')}</span></td>
    <td><span class="tag tag-neutral">不追涨</span></td>
  </tr>
  <tr>
    <td><b>伊利股份</b><br>600887</td><td>大消费 / 防守</td>
    <td class="num">{qs('伊利股份')}</td>
    <td><b>无买点</b>，加速上涨后不追，今日日线顶分型向下回调到下沿附近</td>
    <td class="kn">{zs15('伊利股份')}<br><span class="cap">{bi15('伊利股份')}</span></td>
    <td>等<b>跌破支撑 30.46</b> 再拉回出日线有力度底分型<br><span class="cap">实测：今日最低 {q('伊利股份')['最低']}，<b>距 30.46 仅差 0.07 元、未跌破</b>，收 {q('伊利股份')['收盘']}；末笔向下（力度 {((CZV['伊利股份']['m15']['bi'][-1])['power'])}）→ <b>条件未触发，仍在等</b>。另：收 {q('伊利股份')['收盘']} 已跌破月线中枢下沿 30.90</span></td>
    <td><span class="tag tag-none">等条件</span></td>
  </tr>
  <tr>
    <td><b>中文在线</b><br>300364</td><td>AI 视频</td>
    <td class="num">{qs('中文在线')}</td>
    <td><b>新增</b>，体量大、业绩不好，月线强势震荡、结构出月线底分型</td>
    <td class="kn">{zs15('中文在线')}<br><span class="cap">{bi15('中文在线')}</span></td>
    <td>不追涨，等<b>突破压力高点 30.38</b> 后出 15 分钟底分型的三买<br><span class="cap">实测：<b>今日最高 {q('中文在线')['最高']} 恰好触及 30.38</b>（同时是 60 日新高），但收盘 {q('中文在线')['收盘']} 回落 → <b>触及而未有效突破</b>，假突破风险上升。15 分钟中枢上移至 {zs15('中文在线')}、末笔向上。月线中枢 {zsM('中文在线')}（收 {q('中文在线')['收盘']} 在中枢上方）、{biM('中文在线')} → <b>「月线强势震荡、出月线底分型」成立</b></span></td>
    <td><span class="tag tag-accent">新增观察</span></td>
  </tr>
  <tr>
    <td><b>海天瑞声</b><br>688787</td><td>机器人</td>
    <td class="num">{qs('海天瑞声')}</td>
    <td><b>短线转中线</b>；月线中枢震荡，第一波上涨猛，不建议直接追买</td>
    <td class="kn">{zs15('海天瑞声')}<br><span class="cap">{bi15('海天瑞声')}</span></td>
    <td>等 <b>15 分钟做出类二买结构</b>后再找机会<br><span class="cap">实测：今日 {pct(q('海天瑞声')['涨跌幅%'])} 至 {q('海天瑞声')['收盘']}（最高 {q('海天瑞声')['最高']}），已过 141 门槛，但<b>冲高后回落、15 分钟末笔转为向下</b>（力度 {((CZV['海天瑞声']['m15']['bi'][-1])['power'])}，前笔向上 {((CZV['海天瑞声']['m15']['bi'][-2])['power'])} 明显更强）→ <b>类二买结构未出现，今日属追高被套盘</b>。距 60 日高 155.50（10/26）尚 {abs(q('海天瑞声')['距60日高%'])}%</span></td>
    <td><span class="tag tag-neutral">不追买</span></td>
  </tr>
  <tr>
    <td><b>奥普特</b><br>688686</td><td>机器视觉</td>
    <td class="num">{qs('奥普特')}</td>
    <td><b>新增</b>，月线卡在前高震荡，不建议直接追买</td>
    <td class="kn">{zs15('奥普特')}<br><span class="cap">{bi15('奥普特')}</span></td>
    <td>稳健：等<b>突破高点 186.8</b> 后出日线底分型三买；激进：15 分钟底分型三买；或等回调到临近中枢下沿找止跌<br><span class="cap">实测：今日最高 {q('奥普特')['最高']}（60 日新高）后回落，最低 {q('奥普特')['最低']} <b>精准落在 15 分钟中枢下沿 168.66</b>，收 {q('奥普特')['收盘']} 在中枢内 → <b>「回调到中枢下沿」这一条今日到位，但止跌未确认</b>（末笔仍向下，力度 {((CZV['奥普特']['m15']['bi'][-1])['power'])} vs 前笔 {((CZV['奥普特']['m15']['bi'][-2])['power'])}）。186.8 未触（差 {round((186.8 / q('奥普特')['最高'] - 1) * 100, 1)}%）</span></td>
    <td><span class="tag tag-accent">新增观察</span></td>
  </tr>
  <tr>
    <td><b>柯力传感</b><br>603662</td><td>六维传感器</td>
    <td class="num">{qs('柯力传感')}</td>
    <td><b>新增</b>，月线向下突破后尝试被拉回，观察是否是假突破</td>
    <td class="kn">{zs15('柯力传感')}<br><span class="cap">{bi15('柯力传感')}</span></td>
    <td>等日线顶分型调整后的止跌机会<br><span class="cap">实测：今日最高 {q('柯力传感')['最高']}（= 11/10 的 60 日高）后回落收 {q('柯力传感')['收盘']}，15 分钟末笔向下；<b>月线末笔仍是 2025-02 至今的向下笔（高 90.89 低 40.19，力度 50.7，前笔向上 71.51）</b> → <b>「月线假突破」的观察成立，止跌未确认</b>。15 分钟中枢 {zs15('柯力传感')}，价格仍在其上方</span></td>
    <td><span class="tag tag-accent">新增观察</span></td>
  </tr>
</table>

{chart("603259_SH", "药明康德", "药明康德（603259.SH）日线 · 收 148.70（-1.06%），跌破 151 门槛；15 分钟末笔向下、无二买，回到中枢内形成窄幅震荡雏形。")}
{chart("600150_SH", "中国船舶", "中国船舶（600150.SH）日线 · 收 34.06（-0.58%）；15 分钟下跌中枢下移至 34.10–34.34，未见底止跌。")}
{chart("603893_SH", "瑞芯微", "瑞芯微（603893.SH）日线 · 收 235.01（+0.78%），15 分钟中枢上移 229.61–235.68 并已站上月线中枢上沿 233.88；248.49 仍是三买确认位。")}
{chart("600887_SH", "伊利股份", "伊利股份（600887.SH）日线 · 收 30.61（-1.70%），日线顶分型回调；今日最低 30.53 距 30.46 仅 0.07 元未跌破。")}
{chart("300364_SZ", "中文在线", "中文在线（300364.SZ）日线 · 新增中线 · 收 29.39（+1.17%）；今日最高 30.38 触及压力位（亦为 60 日新高）后回落，未有效突破。")}
{chart("688787_SH", "海天瑞声", "海天瑞声（688787.SH）日线 · 短线转中线 · 收 145.59（+6.82%），已过 141 门槛，但冲高回落、15 分钟末笔向下，类二买未出。")}
{chart("688686_SH", "奥普特", "奥普特（688686.SH）日线 · 新增中线 · 收 173.74（-2.34%），冲高 182.88 后回落至 15 分钟中枢下沿 168.66，186.8 未触。")}
{chart("603662_SH", "柯力传感", "柯力传感（603662.SH）日线 · 新增中线 · 收 57.40（+0.47%），冲高 60.20 后回落，月线向下笔未走完。")}

<h2>四、短线股（2 只）：全部无买点，1 只转中线</h2>
<table>
  <tr><th>标的</th><th>题材</th><th>收盘</th><th>老师定性</th><th>15 分钟中枢（实测）</th><th>关键位 / 止损</th><th>动作</th></tr>
  <tr>
    <td><b>兆易创新</b><br>603986</td><td>存储 / 半导体</td>
    <td class="num">{qs('兆易创新')}</td>
    <td><b>无买点</b>，震荡向上拉升，<b>没出 15 分钟底分型三买</b></td>
    <td class="kn">{zs15('兆易创新')}<br><span class="cap">{bi15('兆易创新')}</span></td>
    <td>继续等待 15 分钟底分型三买；自行参与者设止损 <span class="kn">249</span> 附近<br><span class="cap">实测：今日 {pct(q('兆易创新')['涨跌幅%'])}，<b>盘中最低 {q('兆易创新')['最低']} 已跌破 249 止损参考位</b>，尾盘拉回收 {q('兆易创新')['收盘']}。15 分钟结构上：11/11 09:45 向下笔止于 {q('兆易创新')['最低']}（未破 11/09 新低 237.28），随后向上笔力度 {((CZV['兆易创新']['m15']['bi'][-1])['power'])} &gt; 前笔 {((CZV['兆易创新']['m15']['bi'][-2])['power'])}（<b>无顶背驰</b>）→ <b>底分型三买的力度要素在尾盘 14:30 才补齐，收盘已上穿中枢上沿 248.88</b>；老师盘中给出「没出三买」判断时该结构尚未完成，<b>时点差异，不是矛盾</b></span></td>
    <td><span class="tag tag-none">等三买 / 守 249</span></td>
  </tr>
  <tr>
    <td><b>海天瑞声</b><br>688787</td><td>机器人</td>
    <td class="num">{qs('海天瑞声')}</td>
    <td><b>转中线跟踪，短线剔除</b></td>
    <td class="num kn">{zs15('海天瑞声')}</td>
    <td>见中线表（等 15 分钟类二买结构，今日未出）</td>
    <td><span class="tag tag-neutral">转中线</span></td>
  </tr>
  <tr>
    <td><b>云铝股份</b><br>000807.SZ</td><td>非热点</td>
    <td class="num">{qs('云铝股份')}</td>
    <td>震荡向下、<b>无买点</b>，走势回到下沿</td>
    <td class="kn">{zs15('云铝股份')}<br><span class="cap">{bi15('云铝股份')}</span></td>
    <td>先观察是否止跌，辅助日线有力度底分型出现后小级别做共振机会<br><span class="cap">实测：今日 {pct(q('云铝股份')['涨跌幅%'])}，最低 {q('云铝股份')['最低']} <b>创 60 日新低且跌破 15 分钟中枢下沿 24.45</b>，收 {q('云铝股份')['收盘']} 仍在中枢下方；末笔向下（力度 {((CZV['云铝股份']['m15']['bi'][-1])['power'])}）→ <b>「回到下沿」已变成「跌破下沿」，止跌尚未出现</b></span></td>
    <td><span class="tag tag-none">等止跌</span></td>
  </tr>
</table>

{chart("603986_SH", "兆易创新", "兆易创新（603986.SH）日线 · 尾盘拉回 259.62（+6.15%），但盘中最低 241.22 已跌破 249 止损参考位；15 分钟底分型三买要素尾盘才补齐。")}
{chart("000807_SZ", "云铝股份", "云铝股份（000807.SZ）日线 · 收 23.41（-1.31%），最低 23.00 创 60 日新低、跌破 15 分钟中枢下沿 24.45，尚未止跌。")}

<div class="panel">
  <h4>跟踪池变化（本期结构性调整，值得单列）</h4>
  <table>
    <tr><th>变化</th><th>标的</th><th>老师处理</th><th>我方观察点</th></tr>
    <tr><td><span class="tag tag-accent">新增中线</span></td><td>中文在线 300364</td><td>AI 视频，体量大、业绩不好，月线强势震荡、出月线底分型</td><td>突破压力高点 30.38 → 15 分钟底分型三买；<b>今日最高恰好触及 30.38 后回落</b></td></tr>
    <tr><td><span class="tag tag-neutral">短线转中线</span></td><td>海天瑞声 688787</td><td>机器人，月线中枢震荡，第一波上涨猛，不追</td><td>15 分钟类二买结构；<b>今日 +6.82% 已过 141 但末笔转下，未出类二买</b></td></tr>
    <tr><td><span class="tag tag-accent">新增中线</span></td><td>奥普特 688686</td><td>机器视觉，月线卡前高震荡</td><td>回调到中枢下沿找止跌，或突破 186.8 出三买；<b>今日已回调至下沿 168.66</b></td></tr>
    <tr><td><span class="tag tag-accent">新增中线</span></td><td>柯力传感 603662</td><td>六维传感器，月线假突破观察</td><td>日线顶分型调整后的止跌机会；<b>月线向下笔未走完</b></td></tr>
    <tr><td><span class="tag tag-bear">短线剔除</span></td><td>海天瑞声 688787</td><td>转中线跟踪</td><td>—</td></tr>
    <tr><td><span class="tag tag-bear">短线剔除（11/10）</span></td><td>江波龙 301308</td><td>无买点、既没创新低也没共振</td><td>已不在老师跟踪池中</td></tr>
    <tr><td><span class="tag tag-bear">短线放弃（11/10）</span></td><td>华策影视 300133</td><td>出不了三买直接上冲</td><td>已不在老师跟踪池中</td></tr>
  </table>
  <div class="verify"><b>池子结构变化：</b>中线 4 只 → <b>8 只</b>（3 只新增 + 1 只短线转入），短线 5 只 → <b>2 只</b>。这不是「标的多了」，而是<b>跟踪重心从短线打板转向中线结构选股</b>——与人形机器人升为一类热点、市场温度从 25 度升到 35 度的判断一致：热点延续但结构未变，所以要「等结构」而不是「追题材」。<br><b>但也要如实说：</b>新增的 4 只里，<b>没有一只有买点</b>——中文在线触及未站稳、海天瑞声追高回落、奥普特回调到位但未止跌、柯力传感月线向下笔未走完。<b>池子在扩，机会没在扩</b>。</div>
</div>

<h2>五、潜在强势股</h2>
<div class="verify"><b>原文缺失说明：</b>老师原文第五节只给了<b>筛选逻辑</b>（「选取热点细分中表现强势标的，剔除掉涨幅大的个股，保留位置不高，中线有上涨概率」），<b>未列出具体标的</b>。本期该逻辑的落点非常明确：<b>热点细分 = 人形机器人</b>（一类热点），因此低位置候选应从机器人链里找，而非从已经涨停的 AI 视频、传媒里找。</div>
<table>
  <tr><th>名称</th><th>代码</th><th>收盘</th><th>涨跌幅</th><th>60 日涨幅</th><th>距 60 日高</th><th>近 5 日涨幅</th></tr>
  {"".join(f'<tr><td>{r["名称"]}</td><td class="num">{r["代码"]}</td><td class="num">{r["收盘"]:.2f}</td><td class="num {cls(r["涨跌幅%"])}">{pct(r["涨跌幅%"])}</td><td class="num">{r["60日涨幅%"]}%</td><td class="num">{r["距60日高%"]}%</td><td class="num">{r["近5日涨幅%"]}%</td></tr>' for r in QUOTES)}
</table>
<p>按「剔除涨幅大、保留位置不高」双条件筛：<b>药明康德</b>（60 日 {q('药明康德')['60日涨幅%']}%、距 60 日高 {q('药明康德')['距60日高%']}%，老师给出窄幅震荡雏形 + 凯莱英共振思路）、<b>中国船舶</b>（距 60 日高 {q('中国船舶')['距60日高%']}%，等收复上沿）、<b>云铝股份</b>（距 60 日高 {q('云铝股份')['距60日高%']}%、60 日 {q('云铝股份')['60日涨幅%']}%，位置最低但今日创新低）、<b>奥普特</b>（距 60 日高 {q('奥普特')['距60日高%']}%，回调至中枢下沿）、<b>柯力传感</b>（距 60 日高 {q('柯力传感')['距60日高%']}%，月线假突破观察）。<br><b>当日涨幅已大、按逻辑应剔除</b>：兆易创新（+{q('兆易创新')['涨跌幅%']:.2f}%）、海天瑞声（+{q('海天瑞声')['涨跌幅%']:.2f}%）——注意<b>这两只恰恰是「位置不高」的</b>（兆易创新距 60 日高 {q('兆易创新')['距60日高%']}%、60 日涨幅仍为 {q('兆易创新')['60日涨幅%']}%），剔除理由是<b>当日涨幅</b>而非位置，<b>所以它们是「位置低但今日已涨」的短期追高风险</b>，不是中线候选。</p>
<div class="risk">老师同时提醒：<b>不推荐直接去买入</b>，感兴趣可结合风格跟踪、寻找符合方法的买入机会——以上标的<b>均未满足缠论买点</b>，仅作观察池。</div>

<h2>六、港股</h2>
<p>老师原话：港股因无涨跌幅限制，操作建议设止损；流动性不好，大资金慎入。<b>香港市场暂无个股推荐，先耐心观察等待。</b></p>

<h2>七、操作纪律与明日关注</h2>
<div class="action">
  <b>仓位：</b>总仓位上限 <b>4 成</b>，谨慎不追涨；中线分仓 3–5 只、<b>试探性第一笔约为该股仓位的 5%</b>；跟踪的中线股没必要个个都操作。
</div>
<div class="action">
  <b>被套处理：</b>仓位轻、心态不慌 → 酌情结合反弹高抛，或按短线高低点灵活高抛低吸倒差价；<b>仓位重 → 不硬顶、不额外加仓</b>，心态压力大可酌情主动降低部分仓位，或在个股无基本面风险前提下等反弹。
</div>
<div class="action">
  <b>方法与心态：</b>买点买、卖点卖，做好风控、设好止损、仓位控制好；客观应对盘中波动，养成持续复盘跟踪市场变化的习惯；<b>交易心态不要消极，理清思路</b>。中线走势没坏前建议持有，但存在内部短线回调，想好自己的买卖策略——<b>没有一个方案和策略是鱼和熊掌兼得</b>，不要因为短线回落、盈利幅度降低而事后抱怨。
</div>
<div class="action">
  <b>明日关注：</b>① 上证 <b>3750</b>（向上突破后回抽确认三买）——但<b>今日低点 {sh['low']} 已跌破 11/09 前低 3653.05</b>，先看能否站回并走出底背驰；② 均量线能否由空头排列转多头（5 日均量 {sh['vol_ma5']:,.0f} 上穿 20 日均量 {sh['vol_ma20']:,.0f}）；③ <b>算力硬件能否延续</b>——它才是今日涨幅与涨停第一的方向，若明日掉头则「超跌反弹、防转三卖」兑现；④ 人形机器人涨停能否延续（{zt_robot} 只的零部件扩散），同时注意<b>板块强、龙头弱</b>（宇树科技 11/10 即已在高位回落）；⑤ AI 视频 1033.38 中枢上沿能否站稳（顶背驰是否回头）；⑥ 新增 4 只中线的触发条件：中文在线 30.38（今日已触及未站稳）、伊利 30.46（最低 30.53 未破）、奥普特回调至 168.66 后是否止跌、海天瑞声 15 分钟类二买。
</div>

<h2>八、本纪要与老师原文的偏差记录</h2>
<table>
  <tr><th>项目</th><th>老师原文</th><th>实测数据</th><th>判定</th></tr>
  <tr><td>指数温和上涨、成长更强</td><td>创业板和科创板涨幅力度稍大</td><td>创业板 {pct(cy['pct'])}、科创50 {pct(kc['pct'])} vs 上证 {pct(sh['pct'])}、沪深300 {pct(hs['pct'])}</td><td><span class="tag tag-bull">一致</span></td></tr>
  <tr><td>成交量略放</td><td>成交量略放</td><td>全 A {T['amount_yi']} 亿 vs 前日 {P['amount_yi']} 亿（{pct(amt_chg)}）</td><td><span class="tag tag-bull">一致</span></td></tr>
  <tr><td>均量线还是空头排列</td><td>均量线还是空头排列</td><td>上证 5 日均量 {sh['vol_ma5']:,.0f} &lt; 20 日均量 {sh['vol_ma20']:,.0f}</td><td><span class="tag tag-bull">一致</span></td></tr>
  <tr><td>15 分钟下跌中枢延伸</td><td>15 分钟依旧维持下跌中枢延伸</td><td>中枢 {zs15('上证指数')}，自 11/05 未变、未选择方向</td><td><span class="tag tag-bull">一致</span></td></tr>
  <tr><td>向上需破 3750</td><td>向上需突破压力 3750 点</td><td>今日最高 {sh['high']}，未触发</td><td><span class="tag tag-none">未触发</span></td></tr>
  <tr><td>向下要创新低出底背驰</td><td>向下要创新低</td><td>今日最低 {sh['low']} &lt; 11/09 前低 3653.05，<b>创新低成立</b>（幅度 2.74 点），收盘拉回中枢</td><td><span class="tag tag-neutral">已触发（微幅），底背驰未确认</span></td></tr>
  <tr><td>1 分钟中枢尝试向上离开力度不够</td><td>力度不够、效果不好、延续性不强</td><td>上证自低 {sh['low']} 拉起收 {sh['close']}，未站稳全天高 {sh['high']}，涨幅 {pct(sh['pct'])} 远弱于创业板</td><td><span class="tag tag-neutral">旁证一致（1 分钟结构不可复算）</span></td></tr>
  <tr><td>同花顺全A 站上 20 日均线、破 1325 出三买</td><td>两个具体条件</td><td><b>本机无 881001 数据源（东财限流 + tushare 无该指数），1325 点无法核验</b>；替代口径：全 A 放量 {amt_chg}%、涨 {T['up']}/跌 {T['down']}</td><td><span class="tag tag-neutral">无法直接核验</span></td></tr>
  <tr><td>市场温度 35 度</td><td>第一天上 30 度</td><td>11/09 为 25 度 → 11/10 25 度 → 11/11 35 度，方向一致</td><td><span class="tag tag-bull">一致</span></td></tr>
  <tr><td>人形机器人一类热点、炒增量</td><td>人形机器人炒的是增量，围绕数据采集</td><td>机器人零部件链涨停 {zt_robot} 只（专用机械 {zt_ind.get('专用机械', 0)} + 汽车配件 {zt_ind.get('汽车配件', 0)} + 机械基件 {zt_ind.get('机械基件', 0)}），且为中小市值扩散</td><td><span class="tag tag-bull">一致</span></td></tr>
  <tr><td><b>板块强弱排序</b></td><td>人形机器人＞AI 视频＞算力硬件</td><td>篮子均值：算力硬件 {BASKET['算力硬件']['avg_pct']:+.2f}% ＞ 人形机器人 {BASKET['人形机器人']['avg_pct']:+.2f}% ＞ AI 视频 {BASKET['AI视频/传媒']['avg_pct']:+.2f}%；涨停链算力 {zt_compute} 只 ＞ 机器人 {zt_robot} 只</td><td><span class="tag tag-bear">不一致（算力硬件实测最强）</span></td></tr>
  <tr><td><b>端侧 AI 比超跌半导体更强</b></td><td>端侧 AI 比超跌的半导体等更强一些</td><td>端侧篮子 {BASKET['端侧AI']['avg_pct']:+.2f}% ＜ 半导体 {BASKET['半导体']['avg_pct']:+.2f}%；但老师点名的瑞芯微 +{q('瑞芯微')['涨跌幅%']:.2f}%</td><td><span class="tag tag-bear">篮子口径相反，指定标的一致</span></td></tr>
  <tr><td>AI 视频活跃但上不了热点榜、仍有顶背驰风险</td><td>无法上热点榜，需观察是否顶背驰回头</td><td>篮子均值 {BASKET['AI视频/传媒']['avg_pct']:+.2f}%，涨停级仅 {BASKET['AI视频/传媒']['zt']} 只，强度远低于算力/机器人</td><td><span class="tag tag-bull">一致</span></td></tr>
  <tr><td>半导体先看成超跌反弹、防转三卖</td><td>前期跌幅大反弹力度稍大，转强需先突破压力</td><td>半导体篮子 {BASKET['半导体']['avg_pct']:+.2f}%；主力涨幅来自兆易（60 日涨幅 {q('兆易创新')['60日涨幅%']}%）、澜起等前期深跌品种</td><td><span class="tag tag-bull">一致</span></td></tr>
  <tr><td>玄学链防范资金撤出</td><td>不作为重点推荐，防范资金撤出</td><td>涨停 8 只(11/09) → 4 只(11/10) → 4 只(11/11)，成分换血、仅 2 板、羊字辈今日转跌</td><td><span class="tag tag-bull">一致</span></td></tr>
  <tr><td>药明康德无 15 分钟二买、窄幅震荡雏形</td><td>无买点、窄幅震荡雏形</td><td>末笔向下、无底分型二买；收 {q('药明康德')['收盘']} 回到中枢 {zs15('药明康德')} 内</td><td><span class="tag tag-bull">一致</span></td></tr>
  <tr><td>药明康德等凯莱英/昭衍共振</td><td>等共振结构</td><td>今日药明康德 {pct(q('药明康德')['涨跌幅%'])} vs 凯莱英 +0.36%、昭衍新药 0.00%</td><td><span class="tag tag-neutral">共振今日不成立</span></td></tr>
  <tr><td>中国船舶等收复上沿</td><td>等收复上沿后做 15 分钟共振上涨中枢</td><td>中枢已由 [35.00–35.58] 下移至 {zs15('中国船舶')}，今日高 {q('中国船舶')['最高']}、低 {q('中国船舶')['最低']}、收 {q('中国船舶')['收盘']}</td><td><span class="tag tag-bull">一致（目标位需更新为 34.34）</span></td></tr>
  <tr><td>瑞芯微等回抽确认 248.49 / 拉回中枢共振</td><td>两个条件</td><td>三买未成立（距 248.49 {round((248.49 / q('瑞芯微')['收盘'] - 1) * 100, 1)}%）；<b>拉回中枢共振今日成立</b>（中枢上移至 {zs15('瑞芯微')}）</td><td><span class="tag tag-bull">一致（一条件已成立）</span></td></tr>
  <tr><td>伊利股份等跌破 30.46 再拉回</td><td>等跌破支撑 30.46 再拉回</td><td>今日最低 {q('伊利股份')['最低']}，距 30.46 差 0.07 元未破</td><td><span class="tag tag-bull">一致（条件未触发）</span></td></tr>
  <tr><td>中文在线等破 30.38 出三买</td><td>突破压力高点 30.38</td><td>今日最高 <b>{q('中文在线')['最高']} 恰好触及</b>，收盘 {q('中文在线')['收盘']} 回落未站稳；月线强势震荡、出月线底分型成立</td><td><span class="tag tag-neutral">触及未突破</span></td></tr>
  <tr><td>海天瑞声等 15 分钟类二买</td><td>等 15 分钟做出类二买结构</td><td>今日 {pct(q('海天瑞声')['涨跌幅%'])} 至 {q('海天瑞声')['收盘']}，冲高后末笔转下，类二买未出</td><td><span class="tag tag-bull">一致（未触发）</span></td></tr>
  <tr><td>奥普特等破 186.8 或回调到中枢下沿</td><td>两个条件二选一</td><td>186.8 未触（最高 {q('奥普特')['最高']}）；<b>回调至中枢下沿 168.66 今日到位</b>，止跌未确认</td><td><span class="tag tag-bull">一致（一条件到位）</span></td></tr>
  <tr><td>柯力传感月线假突破观察</td><td>月线向下突破后尝试被拉回</td><td>月线末笔仍是 2025-02 至今向下笔（高 90.89 低 40.19），今日冲高 60.20 后回落</td><td><span class="tag tag-bull">一致</span></td></tr>
  <tr><td>兆易创新没出 15 分钟底分型三买</td><td>没出三买</td><td>盘中确未出；但尾盘 14:30 向下笔止于 241.22 后向上笔力度 {((CZV['兆易创新']['m15']['bi'][-1])['power'])} &gt; 前笔 {((CZV['兆易创新']['m15']['bi'][-2])['power'])}，<b>结构在收盘前才补齐</b>；且盘中最低 {q('兆易创新')['最低']} 已破 249 止损位</td><td><span class="tag tag-neutral">时点差异（收盘成立，盘中未成立）</span></td></tr>
  <tr><td>云铝股份回到下沿、等止跌</td><td>先观察是否止跌</td><td>最低 {q('云铝股份')['最低']} <b>跌破 15 分钟中枢下沿 24.45 并创 60 日新低</b>，末笔向下</td><td><span class="tag tag-bull">一致（且比老师描述更弱）</span></td></tr>
  <tr><td>潜在强势股清单</td><td>只给筛选逻辑，未列标的</td><td>本纪要用当日涨停结构 + 位置数据补做</td><td><span class="tag tag-neutral">原文缺清单</span></td></tr>
</table>

<h2>附录 · 数据口径</h2>
<ul class="tight">
  <li>行情：<b>Tushare Pro</b>（个股/指数/全 A 日线，前复权），成交额单位千元 ÷1e5 折亿元；全市场成交额为全 A 日线汇总（11/11 样本 {T['n']} 只）。</li>
  <li>⚠️ <b>本期数据源受限</b>：东方财富接口采集期间对本机限流（连接被关闭），因此<b>官方概念板块快照、涨停池明细、1 分钟结构未能取得</b>；改用①<b>自建主线篮子</b>（每条线 7–18 只代表股）统计均值/中位数/涨停家数，②<b>涨停行业分布</b>取自 Tushare 全 A 日线 + 申万行业字段，③<b>15 分钟中枢</b>改用<b>新浪财经 15 分钟 K</b>（Tushare <code>stk_mins</code> 本次配额被限为 1 次/小时，不可用；新浪 K 线末日收盘与 Tushare 日线逐只一致，已交叉验证）。<b>板块数字为测算口径，非官方板块指数。</b></li>
  <li>15 分钟中枢：新浪 15 分钟 K（400 根）→ czsc 生成笔 → 「连续三笔重叠区间」计算 ZG/ZD，为<b>独立复算</b>；与 11/09、11/10 两期用 <code>stk_mins</code> 复算的上证/瑞芯微/伊利等中枢完全一致，可比。</li>
  <li>月线/周线中枢：Tushare 日线（2016 年起）聚合后喂 czsc 计算；月线中枢区间较宽、仅作趋势位置参考，不作精确买卖点。</li>
  <li>「同花顺全A」（881001）在本机无可用数据接口（东财无该指数、Tushare 无该代码），故其 20 日均线与 1325 点<b>无法独立核验</b>，报告内以全 A 量能/宽度作替代说明。</li>
  <li>涨停/跌停家数：Tushare 全 A 日线按 ±9.8% 统计（<b>含 ST</b>，与东财「不含 ST」口径有差异；11/11 含 *ST 香雪 1 只）。</li>
  <li>篮子成分（16 只/线以内，可复算）：人形机器人 603662/688787/688686/601689/688017/300124/603728/003021/601100/002472/300503/688160/688698/688320/002896/300607/688322/002527；AI 视频传媒 300364/300133/300624/603533/002343/002425/300413/300251/300058/002027/600977/000719；端侧 AI 603893/002241/002600/300433/688036/002351/002273/603501/002456/300136；算力硬件 300308/300502/300394/601138/000977/000938/002371/688041/688256/603496/300548；半导体 603986/603501/002371/688981/300782/688008/688012/603160；光伏设备 601012/002129/300274/688599/603806/002056/300118/605117。</li>
  <li>图表：<b>红涨绿跌</b>（A 股惯例），关键位一律置于底部图例、不画在图内；K 线数据为 Tushare 前复权日线。</li>
</ul>

<div class="foot">
  <p>原文来源：都业华《高级班》2026-11-11 收评，执业编号 A0400626100004。<b>以上内容仅供参考，不作为买卖依据，据此操作风险自担。投资有风险，入市需谨慎！历史案例不代表未来收益。</b></p>
  <p>本纪要为原文的结构化整理 + 独立数据核验，核验结论基于公开行情数据计算，<b>不构成任何投资建议</b>；与老师原文口径不一致之处已在「偏差记录」逐条标注。</p>
</div>

</div>
</body>
</html>
"""

OUT.write_text(HTML, encoding="utf-8")
print("written:", OUT, len(HTML), "bytes")
