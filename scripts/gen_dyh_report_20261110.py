"""生成 2026-11-10 都业华《高级班收评》纪要 HTML（白底）

数据源：Tushare Pro（行情/指数）、东方财富（板块/涨停池/15分钟K线）、czsc（缠论分型笔）
原始数据：~/workspace/mnote.github.io/reports/duyiehua-20261110/
输出：~/workspace/mnote.github.io/2026-11-10-都业华-高级班收评纪要.html
"""
import csv
import json
from pathlib import Path

REPO = Path("/Users/maoling/workspace/mnote.github.io")
RPT = REPO / "reports/duyiehua-20261110"
AUX = REPO / "reports/dyh-1400-check-20261110"

market = json.loads((RPT / "market_20261110.json").read_text(encoding="utf-8"))
czv = json.loads((RPT / "czsc_verdict.json").read_text(encoding="utf-8"))
idx = json.loads((RPT / "index_20261110.json").read_text(encoding="utf-8"))
sec = json.loads((RPT / "sectors_20261110.json").read_text(encoding="utf-8"))
struct = json.loads((AUX / "dyh_close_struct.json").read_text(encoding="utf-8"))
IND, CON = sec["行业"], sec["概念"]

OUT = REPO / "2026-11-10-都业华-高级班收评纪要.html"

TITLE_SUMMARY = "尾盘跳水，主线切传媒机器人"          # 13 字
TITLE_FULL = f"DYH 高级收评 - 2026-11-10（周二 {TITLE_SUMMARY}）"

CSS = """<style>
  :root {
    --bg:#ffffff; --panel:#f8f9fb; --panel-2:#f1f3f6;
    --border:#e5e7eb; --border-strong:#d1d5db;
    --text:#1f2937; --muted:#6b7280;
    --bull:#16a34a; --bull-bg:#dcfce7;
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
  .grid-2{display:grid;grid-template-columns:1fr 1fr;gap:16px}
  .grid-3{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}
  .grid-4{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}
  @media(max-width:900px){.grid-4{grid-template-columns:1fr 1fr}}
  @media(max-width:760px){.grid-2,.grid-3,.grid-4{grid-template-columns:1fr}}
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
  .up{color:var(--bull);font-weight:600}
  .down{color:var(--bear);font-weight:600}
  .flat{color:var(--muted);font-weight:600}
  .kn{color:var(--key);font-weight:700;font-variant-numeric:tabular-nums}
  .foot{margin-top:48px;padding-top:20px;border-top:1px solid var(--border);font-size:12px;color:var(--muted)}
  ul.tight{margin:8px 0;padding-left:22px}ul.tight li{margin:4px 0}
  .sector{background:#fff;border:1px solid var(--border);border-left:4px solid var(--accent);border-radius:10px;padding:16px 20px;margin:16px 0}
  .sector.r2{border-left-color:#d97706}
  .sector.r3{border-left-color:#7c3aed}
</style>"""


def cls(v):
    return "up" if v > 0 else ("down" if v < 0 else "flat")


def pct(v):
    return f"{v:+.2f}%"


def zs_txt(name):
    z = czv.get(name, {}).get("zs_now")
    if not z:
        return "—"
    return f"{z['ZD']}–{z['ZG']}"


def bi_txt(name):
    b = czv.get(name, {}).get("last_bi")
    if not b:
        return "—"
    return f"末笔{b['dir']}（{b['edt'][5:16]}，力度 {b['power']}）"


B = market["breadth"]
sh, sz, cy, hs300 = idx["上证指数"], idx["深证成指"], idx["创业板指"], idx["沪深300"]
# 深市成交额统一用东财口径（tushare 指数 amount 与东财口径不一致，此处取东财分时累计核验值）
PREV_SZ_AMT = 8001.0
tot_amt = round(sh["amount_yi"] + sz["amount_yi"], 1)
tot_amt_prev = round(sh["prev_amount_yi"] + PREV_SZ_AMT, 1)
amt_chg = round((tot_amt / tot_amt_prev - 1) * 100, 1)

m1_sh = struct["上证"]["m1_zs"][-1]
m1_sz = struct["深成"]["m1_zs"][-1]
m1_cy = struct["创业板"]["m1_zs"][-1]
aiv_bi = struct["AI视频"]["bi"]
aiv_zs = struct["AI视频"]["zs"]

# ── 玄学链 ─────────────────────────────────────────
xuan = list(csv.DictReader(open(RPT / "data/xuanxue_20261110.csv")))
xuan.sort(key=lambda r: float(r["涨跌幅%"]), reverse=True)
xuan_rows = []
for r in xuan:
    v = float(r["涨跌幅%"])
    xuan_rows.append(
        f'<tr><td>{r["名称"]}</td><td class="num">{r["代码"]}</td>'
        f'<td class="num">{r["收盘"]}</td>'
        f'<td class="num {cls(v)}">{pct(v)}</td></tr>')

# ── 候选股 ─────────────────────────────────────────
cands = list(csv.DictReader(open(RPT / "data/candidates_20261110.csv")))
cand_rows = []
for r in cands[:16]:
    v = float(r["涨跌幅%"])
    cand_rows.append(
        f'<tr><td>{r["名称"]}</td><td class="num">{r["代码"]}</td>'
        f'<td class="num">{r["收盘"]}</td>'
        f'<td class="num {cls(v)}">{pct(v)}</td>'
        f'<td class="num">{r["60日涨幅%"]}%</td>'
        f'<td class="num">{r["距60日高%"]}%</td>'
        f'<td class="num">{r["近5日涨幅%"]}%</td>'
        f'<td class="num">{r["今日量/5日均量"]}</td></tr>')

# ── 个股行情 ────────────────────────────────────────
quotes = {r["名称"]: r for r in csv.DictReader(open(RPT / "data/quotes_20261110.csv"))}


def q(name):
    r = quotes[name]
    v = float(r["涨跌幅%"])
    return f'<span class="{cls(v)}">{float(r["收盘"]):.2f} ({pct(v)})</span>'


def board_rows(names, src):
    out = []
    for n in names:
        b = src.get(n)
        if not b:
            continue
        v = b["pct"]
        out.append(
            f'<tr><td>{n}</td><td class="num {cls(v)}">{v:+.2f}%</td>'
            f'<td class="num">{b["up"]} / {b["down"]}</td>'
            f'<td class="num">{b["amount_yi"]} 亿</td>'
            f'<td class="num">{b["main_net_yi"]:+.2f} 亿</td></tr>')
    return "\n".join(out)


PV_BOARD = ["光伏设备", "光伏主材", "光伏辅材", "光伏电池组件", "光伏发电", "光伏加工设备"]
ROBO_BOARD = ["通用设备", "专用设备", "汽车零部件", "自动化设备", "光学光电", "消费电子零部件及组装"]
MEDIA_BOARD = ["影视院线", "广告营销", "游戏", "数字媒体", "出版"]
EDGE_BOARD = ["AI眼镜", "AI手机", "AIPC", "智能穿戴", "智能音箱", "消费电子"]
AI_BOARD = ["AI视频", "AI语料", "AIGC概念", "ChatGPT概念", "多模态AI", "AI应用"]
COMPUTE_BOARD = ["算力概念", "CPO概念", "液冷服务器", "数据中心", "光通信模块"]


def chart(code, name, caption, prefix="charts/"):
    return (f'<img class="chart" src="{prefix}{code}_DY_20261110.png" alt="{name}">'
            f'<div class="cap">{caption}</div>')


zt_ind = market.get("zt_by_industry", {})
zt_top = sorted(zt_ind.items(), key=lambda x: -x[1])[:12]
zt_top_txt = "、".join(f"{k} {v} 家" for k, v in zt_top)

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
    <span>🕘 收评时间：2026-11-10 收盘后</span>
    <span>📡 数据源：都业华《高级班》收评原文 + Tushare Pro + 东方财富</span>
    <span>💹 行情：Tushare Pro（11/10 收盘 · 前复权）</span>
    <span>🔮 缠论核验：czsc（15 分钟 / 1 分钟 K 线 · 三笔重叠算中枢）</span>
    <span>📌 执业编号 A0400626100004</span>
  </div>
  <p class="stance"><b>结论先行：</b>指数高开低走、<b>尾盘跳水</b>，收盘几乎平盘；15 分钟下跌中枢下沿在收盘时被跌破，定性仍为弱势。总仓位上限 <b>4 成</b>、不追涨。中线 4 只、短线 5 只<b>全部不给买点</b>，其中江波龙、华策影视被<b>直接剔除跟踪</b>。可验证的主线是<b>AI 视频 / 传媒 + 人形机器人</b>（涨停池里机器人与端侧 AI 占多数，算力硬件 0 家）；AI 视频 15 分钟中枢逐级上移但<b>力度已衰减（顶背驰要素具备）</b>。另附老师布置的作业题：<b>万兴科技 vs 中文在线</b>二选一纳入跟踪。</p>
</div>

<div class="grid-4">
  <div class="kpi"><div class="label">上证指数</div><div class="val up">{pct(sh['pct'])}</div><div class="sub">{sh['close']} · 开 {sh['open']} 高 {sh['high']} 低 {sh['low']}</div></div>
  <div class="kpi"><div class="label">深证成指 / 创业板</div><div class="val up">{pct(sz['pct'])} / {pct(cy['pct'])}</div><div class="sub">{sz['close']} · {cy['close']} · 沪深300 {pct(hs300['pct'])}</div></div>
  <div class="kpi"><div class="label">两市成交额</div><div class="val up">{tot_amt} 亿</div><div class="sub">较前日 {tot_amt_prev} 亿 {pct(amt_chg)} · 沪缩深放</div></div>
  <div class="kpi"><div class="label">涨 / 跌 家数</div><div class="val"><span class="up">{B['up']}</span> / <span class="down">{B['down']}</span></div><div class="sub">涨停 {B['zt_em']} · 跌停 {B['dt_em']} · 中位 {B['median_pct']}%</div></div>
</div>

<div class="panel">
  <h4>老师原文立场（2026-11-10 收评）</h4>
  <div class="quote"><span class="who">指数</span>指数运行比较沉闷，成交量持续缩量，上证指数 15 分钟维持下跌中枢，观察中枢方向选择：<b>向上需突破压力 3750 点后出回抽确认三买；向下要创新低出底背驰，目前定性为弱势</b>。各指数内部结构不一，<b>上证指数构建 1 分钟上涨中枢震荡，深成指和创业板构建 1 分钟下跌中枢</b>，各指数 1-2 天短线存在变盘，但大结构走势不理想，别着急。谨慎对待市场，控制仓位，<b>总仓位上限控制在 4 成，不追涨</b>。被套仓位：仓位轻、心态不慌可酌情结合反弹高抛，或结合短线高低点灵活高抛低吸倒差价；仓位重建议不硬顶也不额外加仓，可酌情主动降低部分仓位，或在个股无基本面风险前提下等反弹。交易心态不要消极，理清思路。买点买、卖点卖，做好风控设好止损，仓位控制好；对市场要有耐心。</div>
  <div class="quote"><span class="who">板块</span>市场温度 <b>25 度</b>。一类热点：无，二类热点：<b>光伏设备、人形机器人、玄学链</b>。今日前期活跃板块短线重新洗牌：光伏设备、玄学链、传媒以及人形机器人表现尚可，其中<b>人形机器人和文化传媒相对强，光伏设备略弱</b>，走势维持震荡，没出短线高点。如果市场能走出行情，<b>人形机器人和文化传媒板块中期转强概率偏高</b>。玄学链中「羊字辈」到带「东方」字样题材<b>不作为重点推荐</b>，对应个股操作难度大。<b>AI 视频内部走势是两中枢向上，需观察走势是否顶背驰回头</b>，因此短线控制节奏，不追涨。<b>算力硬件方向，端侧 AI 这条线目前表现比超跌线要强</b>，继续观察。</div>
  <div class="quote"><span class="who">中线股 / 短线股</span>中线 4 只：药明康德（大医药，走势僵住，短期无买点，等 15 分钟二买 + 日线有力度底分型）、中国船舶（无买点，等收复上沿后做 15 分钟共振上涨中枢）、<b>瑞芯微（端侧 AI，无买点，今日涨停不追涨，防范前高走势回头，如直接向上突破可辅助日线底分型回抽确认高点 248.49 元的三买机会）</b>、伊利股份（大消费防守，无买点，调整不充分，等跌破下沿出日线有力度顶分型调整后的止跌机会）。<br>短线 5 只：江波龙（无买点，<b>短线剔除跟踪</b>，未离场的重设止损 208）、兆易创新（无买点，近期创新低，等底背驰 + 日线底分型，或突破 15 分钟下跌中枢后的三买）、海天瑞声（无买点，走势临近前高 155.5 元，不建议快速突破时追涨）、<b>华策影视（AI 视频，走势出不了三买直接上冲无买点，短线建议放弃、剔除跟踪）</b>、云铝股份（非热点，无买点，等向上突破 25.91 元后出 15 分钟底分型回抽确认的三买）。</div>
  <div class="quote"><span class="who">布置作业</span>AI 视频相关的<b>万兴科技（300624）和中文在线（300364）</b>可先跟踪思考选取哪个纳入跟踪，明日老师会公布结果，<b>注意个股不是直接去买</b>。</div>
</div>

<h2>一、指数：高开低走、尾盘跳水，15 分钟中枢下沿被破</h2>
<p>实测：上证 <span class="up">{pct(sh['pct'])}</span> 收 {sh['close']}（开 {sh['open']} / 高 {sh['high']} / 低 {sh['low']}），深成指 <span class="up">{pct(sz['pct'])}</span>，创业板指 <span class="up">{pct(cy['pct'])}</span>，沪深300 {pct(hs300['pct'])}。<b>走势形态与老师描述的「高开后震荡下行、走势比较沉闷」完全一致</b>：上证最高点就是开盘那一分钟（3683.73），全天从 +0.58% 一路回落，收盘几乎平盘且贴近日内最低。</p>
<p>两市成交额 {tot_amt} 亿（沪 {sh['amount_yi']} 亿 + 深 {sz['amount_yi']} 亿），较前一日 {tot_amt_prev} 亿<b>微增 {abs(amt_chg)}%</b>。但这是<b>结构分化</b>：沪市 {sh['prev_amount_yi']} → {sh['amount_yi']} 亿（<span class="down">缩量</span>），深市 {PREV_SZ_AMT} → {sz['amount_yi']} 亿（<span class="up">放量</span>）—— 钱去了成长与题材，权重端没有承接。</p>
<p>涨跌家数 <span class="up">{B['up']}</span> / <span class="down">{B['down']}</span>（平 {B['flat']}），个股涨跌幅中位数 <span class="up">{B['median_pct']}%</span>，涨停 {B['zt_em']} 家、跌停 {B['dt_em']} 家。<b>赚钱效应明显好于昨日</b>（11/09 为 2242 涨 / 3148 跌），但老师仍给「市场温度 25 度」—— 老师看的是结构（热点高度、连板质量）而非数量，本纪要在偏差表中记录这一差异。</p>

{chart("000001_SH", "上证指数", "上证指数（000001.SH）日线 · 15 分钟下跌中枢 3664.40–3689.91，收盘 3663.72 已跌破下沿 0.68 点；向上确认位 3750 未触及。")}
{chart("399006_SZ", "创业板指", "创业板指（399006.SZ）日线 · 15 分钟中枢 2529.73–2570.23，收盘 2494.40 位于中枢下方，但今日涨幅 +1.46% 强于沪指。")}

<div class="verify"><b>缠论核验：</b>15 分钟级别（东财 15 分钟 K 线 + czsc 分型/笔 + 三笔重叠算中枢），上证当前中枢 <span class="kn">3664.40–3689.91</span>，与 11/09 收评报出的同一中枢一致；<b>今日收盘 3663.72 首次落到中枢下沿之下</b>——「维持下跌中枢、定性弱势」成立，且向下方向已打开第一道口子。<br><br><b>1 分钟级别（老师：上证构建上涨中枢震荡，深成和创业板构建下跌中枢）：</b><br>· 上证 <span class="kn">{m1_sh['ZD']}–{m1_sh['ZG']}</span>（14:33–14:49 窄幅 3 点）<br>· 深成 <span class="kn">{m1_sz['ZD']}–{m1_sz['ZG']}</span><br>· 创业板 <span class="kn">{m1_cy['ZD']}–{m1_cy['ZG']}</span><br>三个指数收盘均落在各自 1 分钟中枢下沿外，<b>「结构不一、1-2 天短线存在变盘」得到实测支持，变盘窗口指向 11/11</b>。</div>

<h2>二、当日盘中三档观点（十点 / 两点 / 午评）逐条核验</h2>
<p>11/10 老师除收评外还给出三档盘中快评，本纪要一并核验（这是本期新增内容源）。</p>
<table>
  <tr><th>时点</th><th>老师判据</th><th>实测</th><th>判定</th></tr>
  <tr><td>10:00</td><td>受外围影响明显高开，后震荡下行；上证仍未突破 3750，不能说止跌企稳，先当超跌反弹看；预估成交额 1.5 万亿</td><td>高开：创业板 +2.44%、科创50 +2.37%；三指数最高点都在 09:30 那一分钟；3750 未触（最高 3683.73）；早盘至 10:30 成交 7208 亿（同比 -4.9%）</td><td><span class="tag tag-bull">一致</span></td></tr>
  <tr><td>10:00</td><td>算力高开震荡下行；AI 应用 / AI 短剧 / 游戏 / 传媒强势且有持续性</td><td>CPO 开 +3.20%→现 +2.77%（回落 0.69pp）、算力租赁回落 0.34pp；短剧互动游戏 +5.48%、传媒 +4.53%、AI 视频 +4.60%</td><td><span class="tag tag-bull">一致</span></td></tr>
  <tr><td>14:00</td><td>午后继续震荡；没有对 3750 形成 1 分钟三买之前不急于提高仓位；量能还没有有效恢复</td><td>午后 1 分钟中枢仅 3664.99–3668.01、摆幅约 1 点；3750 从未触及，三买前提位置不存在；至 14:15 成交 12629 亿（同比 -0.3%），收盘 15049 亿（同比 +1.5%）</td><td><span class="tag tag-bull">一致</span><span class="tag tag-neutral">量能口径需分</span></td></tr>
  <tr><td>14:00</td><td>算力午后出现资金回流，特别是端侧 AI；端侧 AI 前期抗跌，今天再次异动</td><td>算力概念午盘 +1.81%→收 +2.60%；AI 眼镜 +4.55%、消费电子 +4.28%、AIPC +3.32%、智能音箱 +6.11%；11/09 AI 眼镜 +0.85%（同日传媒 -0.51%、光伏 -2.22%）</td><td><span class="tag tag-bull">一致</span></td></tr>
  <tr><td>午评</td><td>宇树科技「昨天高点 760 元」，今日回拉若低于 760 即短期高点</td><td>688836 11/09 高 <b>759.99</b>；11/10 开 739（开盘即低于 760）、最高 809、收 749.5 —— <b>判据当日盘中已触发</b></td><td><span class="tag tag-bull">分毫不差</span></td></tr>
  <tr><td>午评</td><td>瑞芯微上午冲高回落，存在上不去拉回来继续震荡的概率</td><td>15 分钟：10:15 高 230.00 → 11:30 低 221.22（上午确实回落）；下午 13:30 反手封 233.20 涨停</td><td><span class="tag tag-neutral">上午一致，下午反超</span></td></tr>
  <tr><td>午评</td><td>药明康德未完成对 151 元的修复；华策影视两度封板没封住；云铝今天走势直接向下</td><td>药明康德上午 15 分钟收盘全部收在 151 附近、下午一度站上 151.78 又回落；华策最高 11.64 = 涨停价未封住；云铝开 25.00 收 23.72（-4.62%）</td><td><span class="tag tag-bull">一致</span></td></tr>
</table>
<div class="verify"><b>量能口径说明：</b>老师 14:00 说「量能还没有有效恢复」—— <b>上午成立</b>（至 10:30 同比 -4.9%），<b>收盘口径被尾盘放量修正</b>（尾盘 45 分钟放量约 3200 亿，全天 +1.5%）。若按「对比 11/05 放量高点」口径则仍属萎缩：AI 眼镜 830 vs 1218 亿、算力概念 1322 vs 2119 亿、人形机器人 1558 vs 2000 亿（普遍 -22% ~ -38%）。<b>老师「容错率不高」的判断不受影响</b>——增量全在题材端，权重端持续缩量。</div>

<h2>三、板块热点：无一类热点，二类为光伏设备 + 人形机器人 + 玄学链</h2>

<div class="sector r2">
  <h3>3.1 光伏设备：老师定性「略弱、走势维持震荡，没出短线高点」</h3>
  <table>
    <tr><th>板块</th><th>涨跌幅</th><th>涨/跌家数</th><th>成交额</th><th>主力净流入</th></tr>
    {board_rows(PV_BOARD, IND)}
  </table>
  <div class="verify"><b>实测印证：</b>光伏设备 <span class="up">+1.44%</span>、光伏概念 +1.31%（概念口径主力净流出 14.59 亿），涨幅在两市所有板块中垫底之一，明显弱于人形机器人（+3.70%）与文化传媒（+4.53%）——「光伏设备略弱」成立。光伏全产业链今日整体翻红，说明 11/09 的「跌破中枢见高点风险」<b>未在今天继续恶化</b>，但也没有重新走强的迹象。</div>
</div>

<div class="sector r3">
  <h3>3.2 人形机器人 + 文化传媒：老师认为「中期转强概率偏高」</h3>
  <table>
    <tr><th>板块</th><th>涨跌幅</th><th>涨/跌家数</th><th>成交额</th><th>主力净流入</th></tr>
    {board_rows(ROBO_BOARD + MEDIA_BOARD, IND)}
  </table>
  <table>
    <tr><th>概念板块</th><th>涨跌幅</th><th>涨/跌家数</th><th>成交额</th><th>主力净流入</th></tr>
    {board_rows(["人形机器人", "机器人概念", "机器人执行器", "虚拟机器人"], CON)}
    {board_rows(["传媒", "影视概念", "短剧互动游戏", "AI视频", "AI语料"], CON)}
  </table>
  <div class="verify"><b>实测印证：</b>人形机器人 <span class="up">+3.70%</span>（主力净流入 +57.7 亿）、传媒 <span class="up">+4.53%</span>（主力 +46.9 亿）、短剧互动游戏 <span class="up">+5.48%</span>（主力 +31.7 亿）、影视院线 +7.05%（17 涨 1 跌，主力 +14.7 亿），均强于光伏与算力硬件 —— 「人形机器人和文化传媒相对强」成立。<br><b>涨停池结构（{B['zt_em']} 家）</b>：{zt_top_txt} —— 机器人链（汽车零部 / 通用设备 / 光学光电 / 自动化设备）与端侧 AI、传媒影视三分天下，<b>算力硬件侧仅通信设备 2 家、元件 2 家、半导体 2 家，无一家主线涨停</b>。</div>
  <div class="risk"><b>但龙头已先转弱：</b>老师午评给的量化判据「宇树科技今日回拉不能低于昨天高点 760 元」—— 11/10 开盘 739 即已低于 760，最高 809 后收 749.5，<b>冲高回落 -7.3%，判据当日盘中触发</b>。板块强、龙头弱是典型的后期特征，「中期转强概率偏高」需要龙头先修复。</div>
</div>

<div class="sector">
  <h3>3.3 AI 视频：老师「两中枢向上，需观察是否顶背驰回头」—— 顶背驰要素已具备</h3>
  <table>
    <tr><th>15 分钟中枢序列（czsc 独立复算）</th><th>区间</th><th>时间</th></tr>
    {"".join(f'<tr><td>中枢 {i+1}</td><td class="kn">{z["ZD"]}–{z["ZG"]}</td><td>{z["from"][5:16]} → {z["to"][5:16]}</td></tr>' for i, z in enumerate(aiv_zs))}
  </table>
  <table>
    <tr><th>最近三笔</th><th>方向</th><th>高</th><th>低</th><th>力度</th></tr>
    {"".join(f'<tr><td>{b["edt"][5:16]}</td><td>{b["dir"]}</td><td class="num">{b["high"]}</td><td class="num">{b["low"]}</td><td class="num">{b["power"]}</td></tr>' for b in aiv_bi[-3:])}
  </table>
  <div class="verify"><b>实测印证：</b>中枢区间逐级抬高（{aiv_zs[-3]['ZD']}–{aiv_zs[-3]['ZG']} → {aiv_zs[-2]['ZD']}–{aiv_zs[-2]['ZG']} → {aiv_zs[-1]['ZD']}–{aiv_zs[-1]['ZG']}），「两中枢向上」成立。但<b>末笔（11/10 11:00，向上）力度 {aiv_bi[-1]['power']}，明显小于前一笔向上笔的 {aiv_bi[-3]['power']}（衰减 {round((1 - aiv_bi[-1]['power'] / aiv_bi[-3]['power']) * 100, 1)}%），且创出新高 1042.62 后收于 1034.60</b> —— <b>顶背驰要素已具备</b>，老师「短线控制节奏、不追涨」的判断在当日盘面已经兑现。</div>
</div>

<div class="sector">
  <h3>3.4 算力硬件 vs 端侧 AI：老师「端侧 AI 这条线表现比超跌线要强」</h3>
  <table>
    <tr><th>板块</th><th>涨跌幅</th><th>涨/跌家数</th><th>成交额</th><th>主力净流入</th></tr>
    {board_rows(EDGE_BOARD, CON)}
    {board_rows(COMPUTE_BOARD, CON)}
  </table>
  <div class="verify"><b>实测印证：</b>端侧 AI 载体今日涨幅 3.3%–6.1%（智能音箱 +6.11%、AI 眼镜 +4.55%、消费电子 +4.28%、智能穿戴 +4.03%、AI 手机 +3.46%、AIPC +3.32%），<b>全面强于算力硬件</b>（算力概念 +2.60%、CPO 概念 +2.69%，且 CPO 概念 10 日累计仍为 -4.63%）；「端侧 AI 比超跌线强」成立。<br>「前期抗跌」同样成立：11/09 AI 眼镜 <span class="up">+0.85%</span>，而同日传媒 -0.51%、光伏设备 -2.22%、算力概念 +0.20% —— 端侧 AI 是当日最抗跌的方向之一。</div>
</div>

<div class="sector r2">
  <h3>3.5 玄学链：老师「羊字辈→东方字样不作为重点推荐，操作难度大」</h3>
  <table>
    <tr><th>名称</th><th>代码</th><th>收盘</th><th>涨跌幅</th></tr>
    {"".join(xuan_rows[:16])}
  </table>
  <div class="verify"><b>实测印证：</b>含「东方 / 羊」字样的 32 只股票中，涨停数由 11/09 的 <b>8 只收敛到 4 只</b>（东方新能 3 连板、日出东方 3 连板、东方环宇 2 连板、大东方 3 连板），<b>羊字辈明显走弱</b>（三羊马 +4.02%、水羊股份 +1.28%）—— 「羊字辈切到东方字样」与「不作为重点推荐」均成立。<br>留下的 4 只全部是 3 连板以上高位股，<b>风险收益比已经明显恶化</b>。</div>
</div>

<h2>四、中线股（4 只）：老师全部不给买点，只给触发条件</h2>
<p>老师纪律：中线参与需先结合市场强弱评估仓位上限；可操作仓内分仓，持仓 3–5 只，<b>试探性第一笔约为该股仓位的 5%</b>；买点买、卖点卖、做好风控；中线走势没坏前建议持有，但内部会有短线回调，想好自己的买卖策略。</p>
<table>
  <tr><th>标的</th><th>题材</th><th>收盘</th><th>老师定性</th><th>15 分钟中枢（实测）</th><th>触发条件</th><th>动作</th></tr>
  <tr>
    <td><b>药明康德</b><br>603259</td><td>大医药</td>
    <td class="num">{q('药明康德')}</td>
    <td>走势僵住，存做震荡概率，<b>短期无买点</b></td>
    <td class="kn">{zs_txt('药明康德')}<br><span class="cap">{bi_txt('药明康德')}</span></td>
    <td>先观察 <b>15 分钟二买</b>，辅助日线有力度验证底分型机会<br><span class="cap">实测：今日高开 157.00 → 最高 157.80 → 收 150.30，15 分钟收盘反复未站稳 151</span></td>
    <td><span class="tag tag-none">观望</span></td>
  </tr>
  <tr>
    <td><b>中国船舶</b><br>600150</td><td>船舶</td>
    <td class="num">{q('中国船舶')}</td>
    <td><b>无买点</b>，15 分钟内部下跌中枢延伸、结构没见底</td>
    <td class="kn">{zs_txt('中国船舶')}<br><span class="cap">{bi_txt('中国船舶')}</span></td>
    <td>等<b>收复上沿</b>后做 15 分钟共振上涨中枢再找机会<br><span class="cap">实测：今日最高 35.20，仍低于上沿 35.58；末笔力度 0.26，几乎无反抽</span></td>
    <td><span class="tag tag-none">观望</span></td>
  </tr>
  <tr>
    <td><b>瑞芯微</b><br>603893</td><td>端侧 AI</td>
    <td class="num">{q('瑞芯微')}</td>
    <td><b>无买点</b>，今日涨停不追涨，防范前高走势回头</td>
    <td class="kn">{zs_txt('瑞芯微')}<br><span class="cap">{bi_txt('瑞芯微')}</span></td>
    <td>先观察是否有<b>对称震荡结构</b>；如直接向上突破，可辅助日线底分型回抽确认<b>高点 248.49</b> 的三买机会<br><span class="cap">实测：248.49 = 2025-09-01 的历史高点（周线级），现价 233.20 距其 +6.5%</span></td>
    <td><span class="tag tag-neutral">不追涨</span></td>
  </tr>
  <tr>
    <td><b>伊利股份</b><br>600887</td><td>大消费 / 防守</td>
    <td class="num">{q('伊利股份')}</td>
    <td><b>无买点</b>，加速上涨后不追、调整不充分</td>
    <td class="kn">{zs_txt('伊利股份')}<br><span class="cap">{bi_txt('伊利股份')}</span></td>
    <td>15 分钟围绕 1 分钟中枢反复震荡，等<b>跌破下沿</b>出日线有力度顶分型调整后的止跌机会<br><span class="cap">实测：今日全天 30.74–31.20 极窄幅，60 日高 31.65 未破</span></td>
    <td><span class="tag tag-none">观望</span></td>
  </tr>
</table>

{chart("603259_SH", "药明康德", "药明康德（603259.SH）日线 · 关键位 151（突破门槛），今日高开 157.80 后回落收 150.30。")}
{chart("600150_SH", "中国船舶", "中国船舶（600150.SH）日线 · 15 分钟中枢 35.00–35.58，今日最高 35.20 未收复上沿，收 34.26（-2.14%）。")}
{chart("603893_SH", "瑞芯微", "瑞芯微（603893.SH）日线 · 今日涨停 233.20；年线级前高 248.49（2025-09-01）为老师给的三买确认位。")}
{chart("600887_SH", "伊利股份", "伊利股份（600887.SH）日线 · 60 日高 31.65 未破，全天窄幅震荡收 31.14。")}

<h2>五、短线股（5 只）：2 只被明确剔除跟踪</h2>
<table>
  <tr><th>标的</th><th>题材</th><th>收盘</th><th>老师定性</th><th>15 分钟中枢（实测）</th><th>关键位 / 止损</th><th>动作</th></tr>
  <tr>
    <td><b>江波龙</b><br>301308</td><td>存储</td>
    <td class="num">{q('江波龙')}</td>
    <td><b>无买点</b>，既没创新低也没共振机会，<b>短线剔除跟踪</b></td>
    <td class="kn">{zs_txt('江波龙')}<br><span class="cap">{bi_txt('江波龙')}</span></td>
    <td>未离场同学：重新设止损点 <span class="kn">208</span> 后酌情参考选择<br><span class="cap">实测：今日最低 219.54，未创新低（11/09 低 215.52），止损未触发</span></td>
    <td><span class="tag tag-bear">剔除跟踪 / 守 208</span></td>
  </tr>
  <tr>
    <td><b>兆易创新</b><br>603986</td><td>存储</td>
    <td class="num">{q('兆易创新')}</td>
    <td><b>无买点</b>，近期创新低</td>
    <td class="kn">{zs_txt('兆易创新')}<br><span class="cap">{bi_txt('兆易创新')}</span></td>
    <td>观察底背驰 + 日线有力度底分型，或突破 15 分钟下跌中枢后的三买<br><span class="cap">实测：11/09 低 237.28 为近期新低，今日反弹至 248.88 后收 244.57</span></td>
    <td><span class="tag tag-none">等条件</span></td>
  </tr>
  <tr>
    <td><b>海天瑞声</b><br>688787</td><td>人形机器人</td>
    <td class="num">{q('海天瑞声')}</td>
    <td><b>无买点</b>，结构维持震荡、弱势不追涨</td>
    <td class="kn">{zs_txt('海天瑞声')}<br><span class="cap">{bi_txt('海天瑞声')}</span></td>
    <td>走势临近前高 <span class="kn">155.50</span>，不建议快速突破时追涨，一般建议做出共振结构后再考虑<br><span class="cap">实测：155.50 = 10/26 的 60 日最高；今日最高 138.00，141 门槛仍未过</span></td>
    <td><span class="tag tag-none">先观察</span></td>
  </tr>
  <tr>
    <td><b>华策影视</b><br>300133</td><td>AI 视频</td>
    <td class="num">{q('华策影视')}</td>
    <td>走势出不了三买直接上冲，<b>无买点，短线建议放弃、剔除跟踪</b></td>
    <td class="kn">{zs_txt('华策影视')}<br><span class="cap">{bi_txt('华策影视')}</span></td>
    <td>不追涨；该位置放大量后无法离开中枢再被拉回，基本就是短期高点<br><span class="cap">实测：最高 11.64 = 涨停价（9.70×1.2）触及未封住，成交 36.69 亿 = 昨日的 2 倍</span></td>
    <td><span class="tag tag-bear">放弃 / 剔除跟踪</span></td>
  </tr>
  <tr>
    <td><b>云铝股份</b><br>000807</td><td>非热点 / 震荡</td>
    <td class="num">{q('云铝股份')}</td>
    <td>震荡向下，<b>无法满足方法买点</b></td>
    <td class="kn">{zs_txt('云铝股份')}<br><span class="cap">{bi_txt('云铝股份')}</span></td>
    <td>等向上突破 <span class="kn">25.91</span> 后出 15 分钟底分型回抽确认的三买<br><span class="cap">实测：今日最高 25.08 未达 25.91，全天下行收 23.72（-4.62%）</span></td>
    <td><span class="tag tag-none">等条件</span></td>
  </tr>
</table>

{chart("301308_SZ", "江波龙", "江波龙（301308.SZ）日线 · 止损位 208；今日反弹 +2.49% 但未创新低，老师已剔除跟踪。")}
{chart("603986_SH", "兆易创新", "兆易创新（603986.SH）日线 · 11/09 创 237.28 新低后反弹 +2.58%，仍属反弹非止跌。")}
{chart("688787_SH", "海天瑞声", "海天瑞声（688787.SH）日线 · 今日 +8.00% 至 136.30，距前高 155.50 尚差 12.3%，141 门槛未过。")}
{chart("300133_SZ", "华策影视", "华策影视（300133.SZ）日线 · 最高 11.64（涨停价）未封住，收 11.29（+16.39%），放巨量，老师建议短线放弃。")}
{chart("000807_SZ", "云铝股份", "云铝股份（000807.SZ）日线 · 25.91 突破位未达，全天震荡向下收 23.72（-4.62%）。")}

<h2>六、布置作业：AI 视频二选一 —— 万兴科技 vs 中文在线</h2>
<p>老师布置：AI 视频相关的万兴科技（300624）与中文在线（300364），可先跟踪思考选取哪个纳入跟踪，<b>明日公布结果，注意个股不是直接去买</b>。下表为同日收盘的实测对比。</p>
<table>
  <tr><th>维度</th><th>万兴科技 300624</th><th>中文在线 300364</th></tr>
  <tr><td>11/10 收盘</td><td class="num">{q('万兴科技')}</td><td class="num">{q('中文在线')}</td></tr>
  <tr><td>当日区间</td><td class="num">50.51 – 54.63</td><td class="num">26.53 – 29.83（触及涨停价后回落）</td></tr>
  <tr><td>成交额 / 总市值</td><td class="num">14.83 亿 / 102.5 亿</td><td class="num">46.44 亿 / 211.6 亿</td></tr>
  <tr><td>距 60 日高</td><td class="num"><b>-11.3%</b>（60 日高 59.77）</td><td class="num"><b>-2.8%</b>（60 日高 29.90）</td></tr>
  <tr><td>60 日 / 10 日 / 5 日涨幅</td><td class="num">-5.2% / +10.5% / +18.6%</td><td class="num">+15.2% / <b>+23.9%</b> / +18.1%</td></tr>
  <tr><td>MACD</td><td class="num">金叉，DIF -0.13 仍在<b>零轴下</b></td><td class="num">金叉，DIF 0.76 已上零轴</td></tr>
  <tr><td>概念主线</td><td class="num">AI 视频（最纯正）、VR、数字人、AIGC、Kimi</td><td class="num">文字媒体、短剧互动游戏、数字媒体、AI 语料、快手</td></tr>
  <tr><td>15 分钟中枢（实测）</td><td class="num kn">{zs_txt('万兴科技')}<br><span class="cap">{bi_txt('万兴科技')}</span></td><td class="num kn">{zs_txt('中文在线')}<br><span class="cap">{bi_txt('中文在线')}</span></td></tr>
</table>
{chart("300624_SZ", "万兴科技", "万兴科技（300624.SZ）日线 · AI 视频纯正标的，距 60 日高 -11.3%，位置不高。")}
{chart("300364_SZ", "中文在线", "中文在线（300364.SZ）日线 · 今日 +8.07% 触涨停价 29.83 后回落，距 60 日高仅 -2.8%，位置偏高。")}
<div class="verify"><b>本纪要测算（非老师原文结论）：</b>直接套用老师自己的筛选标准「剔除掉涨幅大的个股，保留位置不高、中线有上涨概率」—— <b>倾向万兴科技</b>：20 日涨幅仅 +2.6%（中文在线 +13.1%）、距 60 日高 -11.3%（中文在线已贴前高）、MACD 金叉但 DIF 仍在零轴下属底部初期。<b>反面口径（动量优先）会选中文在线</b>：流动性 3 倍、10 日 +23.9%、AI 语料 +4.5% 与当日尾盘最强的传媒/短剧同源。<b>无论选谁都不是买点</b>——真正的介入条件是 AI 视频板块顶背驰回头后重新站稳 1033.38，或个股自身出现 15 分钟底分型 + 共振。</div>

<h2>七、潜在强势股</h2>
<div class="verify"><b>原文缺失说明：</b>老师原文第五节只给了<b>筛选逻辑</b>（「选取热点细分中表现强势标的，剔除掉涨幅大的个股，保留位置不高，中线有上涨概率」），<b>未列出具体标的</b>。下表是本纪要按同一逻辑、用当日涨停池（{B['zt_em']} 家）+ 位置数据做的<b>补充测算</b>，<b>非老师原文清单</b>，仅供参考。</div>
<table>
  <tr><th>名称</th><th>代码</th><th>收盘</th><th>涨跌幅</th><th>60 日涨幅</th><th>距 60 日高</th><th>近 5 日涨幅</th><th>量比(今/5日均)</th></tr>
  {"".join(cand_rows)}
</table>
<p>按「剔除涨幅大、保留位置不高」筛出的<b>低位置候选</b>：<b>华体科技</b>（光学光电，60 日 -18.2%、距 60 日高 -32.5%）、<b>智微智能</b>（计算机设备，60 日 -23.4%、距高 -28.2%）、<b>亿道信息</b>（消费电子，60 日 -23.5%、距高 -27.5%）、<b>天普股份</b>（汽车零部件，60 日 -21.2%、距高 -27.0%）、<b>瀛通通讯</b>（消费电子，60 日 -20.2%）、<b>赛腾股份</b>（自动化设备，60 日 -8.3%）、<b>联创电子</b>（光学光电，60 日 -21.2%）。<b>位置偏高需剔除</b>：光洋股份（60 日 +126.7%）、上海电影（+130.0%）、襄阳轴承（+112.8%）、冰山冷热（+108.9%）、龙版传媒（+80.0%）、慈文传媒（+77.4%）、国光电器（+30.5%）、掌阅科技（+45.8%）。</p>
<div class="risk">老师同时提醒：<b>不推荐直接去买入</b>，感兴趣可结合风格跟踪、寻找符合方法的买入机会——以上标的<b>均未满足缠论买点</b>，仅作观察池。</div>

<h2>八、港股</h2>
<p>老师原话：港股因无涨跌幅限制，操作建议设止损；流动性不好，大资金慎入。<b>香港市场暂无个股推荐，先耐心观察等待。</b></p>

<h2>九、操作纪律（老师原文归纳）</h2>
<div class="action">
  <b>仓位：</b>总仓位上限 <b>4 成</b>；中线参与需先结合市场强弱评估仓位上限，可操作仓内分仓 3–5 只，<b>试探性第一笔约为该股仓位的 5%</b>；不追涨。
</div>
<div class="action">
  <b>被套处理：</b>仓位轻、心态不慌 → 酌情结合反弹高抛，或按短线高低点灵活高抛低吸倒差价；<b>仓位重 → 不硬顶、不额外加仓</b>，心态压力大可酌情主动降低部分仓位，或在个股无基本面风险前提下等反弹。
</div>
<div class="action">
  <b>方法与心态：</b>买点买、卖点卖，做好风控、设好止损、仓位控制好；客观应对盘中波动，养成持续复盘跟踪市场变化的习惯；<b>交易心态不要消极，理清思路</b>。中线走势没坏前建议持有，但内部会有短线回调，想好自己的买卖策略——<b>没有一个方案和策略是鱼和熊掌兼得</b>，不要因为短线回落、盈利幅度降低而事后抱怨。
</div>
<div class="action">
  <b>明日关注（据本日实测推导）：</b>① 上证 3664.40（15 分钟中枢下沿，已破）与 3653.05（11/09 前低，破则底背驰条件开始酝酿）；② 3701.59（11/05 高点，站上且沪市量能回到 7000 亿以上才算修复）；③ AI 视频板块 1033.38（中枢上沿，顶背驰后重新站稳才算修复）；④ 端侧 AI 与传媒能否在分歧中回补今日尾盘的回落。
</div>

<h2>十、本纪要与老师原文的偏差记录</h2>
<table>
  <tr><th>项目</th><th>老师原文</th><th>实测数据</th><th>判定</th></tr>
  <tr><td>指数走势</td><td>运行比较沉闷，弱势震荡</td><td>上证 +0.08% 收 3663.72，高开 3682.04 → 尾盘贴近日内低</td><td><span class="tag tag-bull">一致</span></td></tr>
  <tr><td>成交量持续缩量</td><td>成交量持续缩量</td><td>两市 15049 亿 vs 前日 14826 亿（+1.5%），但沪市 6740 亿缩量、深市 8309 亿放量；上午至 10:30 同比 -4.9%</td><td><span class="tag tag-neutral">口径需分（沪缩深放）</span></td></tr>
  <tr><td>15 分钟下跌中枢</td><td>15 分钟维持下跌中枢</td><td>3664.40–3689.91，收盘 3663.72 <b>已跌破下沿 0.68 点</b></td><td><span class="tag tag-bull">一致（且已破位）</span></td></tr>
  <tr><td>1 分钟结构不一</td><td>上证 1 分钟上涨中枢，深成创业 1 分钟下跌中枢</td><td>上证 3664.99–3668.01、深成 11252.34–11266.14、创业板 2496.90–2501.10，三者收盘均在各自中枢下沿外</td><td><span class="tag tag-bull">一致</span></td></tr>
  <tr><td>市场温度 25 度</td><td>市场温度 25 度</td><td>涨 {B['up']} / 跌 {B['down']}，中位 {B['median_pct']}%，涨停 {B['zt_em']} 家、跌停 {B['dt_em']} 家（较 11/09 的 2242/3148 明显改善）</td><td><span class="tag tag-neutral">数量口径偏保守</span></td></tr>
  <tr><td>人形机器人 / 文化传媒相对强</td><td>人形机器人和文化传媒相对强</td><td>人形机器人 +3.70%（主力 +57.7 亿）、传媒 +4.53%（主力 +46.9 亿）</td><td><span class="tag tag-bull">一致</span></td></tr>
  <tr><td>光伏设备略弱</td><td>光伏设备略弱</td><td>光伏设备 +1.44%，主力净流出，涨幅垫底</td><td><span class="tag tag-bull">一致</span></td></tr>
  <tr><td>玄学链不作为重点推荐</td><td>羊字辈→东方字样不作为重点推荐，操作难度大</td><td>涨停由 8 只收敛到 4 只，全部 3 连板以上高位；羊字辈走弱</td><td><span class="tag tag-bull">一致</span></td></tr>
  <tr><td>AI 视频两中枢向上</td><td>内部走势是两中枢向上，需观察顶背驰</td><td>中枢 956.47–1002.72 → 987.64–1002.72 → 987.64–1033.38；末笔力度 54.98 &lt; 前笔 76.91（衰减 28.5%）</td><td><span class="tag tag-bull">一致（顶背驰要素已具备）</span></td></tr>
  <tr><td>端侧 AI 强于超跌线</td><td>端侧 AI 这条线表现比超跌线强</td><td>端侧载体 +3.3%~+6.1% vs 算力概念 +2.60%、CPO 10 日 -4.63%</td><td><span class="tag tag-bull">一致</span></td></tr>
  <tr><td>瑞芯微 248.49</td><td>回抽确认高点 248.49 元的三买机会</td><td>248.49 = 2025-09-01 历史高点（周线级），现价 233.20 距其 +6.5%</td><td><span class="tag tag-bull">一致（年线级压力）</span></td></tr>
  <tr><td>海天瑞声 155.5</td><td>走势临近前高 155.5 元</td><td>155.50 = 10/26 的 60 日最高；今日收 136.30，距前高 12.3%，141 门槛未过</td><td><span class="tag tag-neutral">价位准确，「临近」偏松</span></td></tr>
  <tr><td>中国船舶上沿</td><td>等收复上沿后做共振上涨中枢</td><td>最高 35.20 &lt; 上沿 35.58，未收复</td><td><span class="tag tag-bull">一致</span></td></tr>
  <tr><td>华策影视放弃</td><td>出不了三买直接上冲无买点，短线放弃</td><td>最高 11.64 = 涨停价未封住，收 +16.39%，成交 36.69 亿（昨 17.65 亿的 2.1 倍）</td><td><span class="tag tag-bull">一致</span></td></tr>
  <tr><td>江波龙剔除跟踪</td><td>既没创新低也没共振，短线剔除跟踪</td><td>今日低 219.54 未创新低（11/09 低 215.52）</td><td><span class="tag tag-bull">一致</span></td></tr>
  <tr><td>云铝 25.91</td><td>等向上突破 25.91 后出底分型回抽三买</td><td>最高 25.08 未达，全天收 23.72（-4.62%）</td><td><span class="tag tag-bull">一致</span></td></tr>
  <tr><td>潜在强势股清单</td><td>只给筛选逻辑，未列标的</td><td>本纪要用涨停池 + 位置数据补做</td><td><span class="tag tag-neutral">原文缺清单</span></td></tr>
  <tr><td>作业题答案</td><td>万兴科技 vs 中文在线，明日公布</td><td>本纪要按位置优先口径倾向万兴科技（已标注为测算）</td><td><span class="tag tag-accent">待老师公布</span></td></tr>
</table>

<h2>附录 · 数据口径</h2>
<ul class="tight">
  <li>行情：Tushare Pro（个股/指数日线、全部 A 股日线），前复权；成交额单位千元，÷1e5 折亿元；两市成交额对比采用<b>东方财富指数口径</b>（沪 6740 + 深 8309 = 15049 亿），tushare 深市指数 amount 与该口径不一致，不用于比较。</li>
  <li>涨停/跌停家数：东方财富涨停池 / 跌停池接口（<b>不含 ST</b>）；「全 A 涨跌家数」为 tushare 全量日线统计（中位数 {B['median_pct']}%）。</li>
  <li>板块涨跌幅：东方财富行业板块 / 概念板块快照（涨/跌家数为该板块口径，主力净流入为东财 f62 口径）。</li>
  <li>15 分钟与 1 分钟中枢：由东财 K 线经 czsc 生成笔，再按「连续三笔重叠区间」计算 ZG/ZD；为<b>独立复算</b>，与老师系统口径可能有级别或笔划分差异。</li>
  <li>玄学链样本：按公开题材梳理口径（羊/洋/阳/扬/杨 + 东方系）人工取样，非官方概念板块。</li>
  <li>「端侧 AI」在东方财富<b>没有独立板块</b>，本纪要用终端载体组合代理：AI 眼镜 BK1178 / 消费电子 BK1037 / 消费电子零部件及组装 BK1338 / AI 手机 BK1162 / AIPC BK1164 / 智能穿戴 BK0641 / 智能音箱 BK1766。</li>
</ul>

<div class="foot">
  <p>原文来源：都业华《高级班》2026-11-10 收评及当日盘中快评（十点看盘 / 两点看盘 / 午评），执业编号 A0400626100004。<b>以上内容仅供参考，不作为买卖依据，据此操作风险自担。投资有风险，入市需谨慎！历史案例不代表未来收益。</b></p>
  <p>本纪要为原文的结构化整理 + 独立数据核验，核验结论基于公开行情数据计算，<b>不构成任何投资建议</b>。</p>
</div>

</div>
</body>
</html>
"""

OUT.write_text(HTML, encoding="utf-8")
print("written:", OUT, len(HTML), "bytes")
