"""类二买共振股池 2026-11-18 · 分析页 HTML（白底 · DYH 报表风格）

📏 正文 ≤2000 中文字、表格 ≤4 张；K 线图 13 张紧跟标的。
输出：html/duyiehua-pool-20261118.html
"""
import json
import sys
from pathlib import Path

REPO = Path("/Users/maoling/workspace/mnote.github.io")
sys.path.insert(0, str(REPO / "scripts"))
from fix_mobile_tables import patch_html  # noqa: E402

RPT = REPO / "reports/pool-20261118"
P = json.loads((RPT / "pool_stats.json").read_text(encoding="utf-8"))
BY = {s["code"]: s for s in P}
OUT = REPO / "html/duyiehua-pool-20261118.html"

TITLE = "DYH 股池 - 2026-11-18（周三 类二买13只，红利强题材弱）"

CSS = """<style>
  :root{--bg:#fff;--panel:#f8f9fb;--border:#e5e7eb;--text:#1f2937;--muted:#6b7280;
    --bull:#16a34a;--bullbg:#dcfce7;--up:#e0392e;--down:#26a69a;--bear:#dc2626;--bearbg:#fee2e2;
    --neutral:#d97706;--neutbg:#fef3c7;--none:#6b7280;--nonebg:#f3f4f6;--accent:#2563eb;--accentbg:#dbeafe;--key:#7c3aed;}
  *{box-sizing:border-box}
  body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei","Segoe UI",sans-serif;
    background:var(--bg);color:var(--text);line-height:1.6;font-size:14.5px}
  .wrap{max-width:1200px;margin:0 auto;padding:26px 24px 60px}
  h1{font-size:24px;margin:0 0 5px}h2{font-size:18px;margin:26px 0 10px;padding-bottom:6px;border-bottom:2px solid var(--border)}
  h3{font-size:15.5px;margin:18px 0 6px}
  p{margin:6px 0}a{color:var(--accent);text-decoration:none}
  .meta{color:var(--muted);font-size:12px}
  .hero{background:linear-gradient(135deg,#fff7ed,#fffdf7);border:1px solid #fdba74;border-radius:12px;padding:18px 22px;margin-bottom:14px}
  .hero h1{color:#9a3412}.hero .stance{font-size:14.5px;margin:7px 0 0}
  .grid4{display:grid;grid-template-columns:repeat(4,1fr);gap:11px}
  @media(max-width:900px){.grid4{grid-template-columns:1fr 1fr}}@media(max-width:700px){.grid4{grid-template-columns:1fr}}
  .kpi{background:#fff;border:1px solid var(--border);border-radius:8px;padding:10px 12px;text-align:center}
  .kpi .label{font-size:11.5px;color:var(--muted)}.kpi .val{font-size:18px;font-weight:600;margin:2px 0}
  .kpi .sub{font-size:11px;color:var(--muted)}
  table{width:100%;border-collapse:collapse;margin:9px 0;font-size:13px}
  th,td{padding:6px 8px;text-align:left;border-bottom:1px solid var(--border);vertical-align:top}
  th{background:var(--panel);font-weight:600;white-space:nowrap}
  .up{color:var(--up)}.down{color:var(--down)}.vol{color:var(--neutral);font-weight:600}
  .num{font-variant-numeric:tabular-nums;white-space:nowrap}
  .kn{color:var(--key);font-weight:600}
  .tag{display:inline-block;padding:1px 7px;border-radius:10px;font-size:11.5px;white-space:nowrap}
  .tag-bear{background:var(--bearbg);color:var(--bear)}
  .tag-bull{background:var(--bullbg);color:var(--bull)}
  .tag-neutral{background:var(--neutbg);color:var(--neutral)}
  .tag-none{background:var(--nonebg);color:var(--none)}
  .box{background:var(--panel);border-left:4px solid var(--accent);border-radius:6px;padding:11px 14px;margin:9px 0}
  .box-g{background:var(--bullbg);border-left-color:var(--bull)}
  .box-r{background:var(--bearbg);border-left-color:var(--bear)}
  .box-a{background:var(--accentbg);border-left-color:var(--accent)}
  img.chart{width:100%;max-width:100%;display:block;margin:10px 0 4px;border:1px solid var(--border);border-radius:8px;background:#fff}
  .cap{color:var(--muted);font-size:12px;margin:0 0 14px}
  .foot{margin-top:30px;padding-top:12px;border-top:1px solid var(--border);font-size:11.5px;color:var(--muted)}
</style>"""

TAGCLS = {"新高附近": "tag-bull", "中继向上": "tag-neutral", "修复中": "tag-none", "破位区": "tag-bear"}

# 每只标的的一句话结论（数字由数据生成，判断为人写）
TODO = {
    "002821.SZ": ("凯莱英", "医疗服务",
                "入池以来仍 <b>+13.1%</b>，是破位股里唯一大幅浮盈的。但 11/05 MACD 金叉后 8 个交易日就跌回 MA20（144.31）下方，"
                "60 日高 194.32 距今 -27.3%，MA60 162.46 高悬 —— 反弹没转成反转，按类二买口径属<b>结构失效</b>，不补仓。"),
    "603009.SH": ("北特科技", "汽车零部件·机器人",
                "11/11 见 60 日高 <b>55.00</b> 后 5 个交易日跌 <b>-18.0%</b>，MACD 已转空头，量比 0.76 缩量下跌说明无承接。"
                "机器人题材退潮期，等 40.00（60 日低）区域是否出日线底分型。"),
    "300593.SZ": ("新雷能", "其他电源设备",
                "池内最弱：入池（8/26）以来 <b>-34.9%</b>，距 60 日高 35.08 有 -43.0%，距 60 日低 19.03 只剩 <b>5.0%</b>，MA60 27.54 高悬。"
                "不破 19.03 仍算箱体下沿，破则彻底失效。"),
    "603225.SH": ("新凤鸣", "化学纤维",
                "夹在 MA20（16.93）与 MA60（17.59）之间缩量整理（量比 0.80），距 60 日高 -19.9%。"
                "<span class=kn>17.59</span> 是分水岭：站上则中期结构修复，有效跌破 16.93 回到弱势。"),
    "600236.SH": ("桂冠电力", "电力·红利",
                "当日池内最强 <b>+3.48%</b>，量比 <b>2.09</b> 放量突破 MA5/10/20 三线粘连区（8.94/8.96/8.99），MACD 11/11 金叉延续。"
                "唯一门槛是 MA60 <span class=kn>9.57</span> —— 收复即完成均线全多头。"),
    "601107.SH": ("四川成渝", "公路铁路运输·红利",
                "入池（10/09）以来 <b>+15.8%</b>，池内浮盈第一；MA5>MA10>MA20>MA60 完整多头排列（7.30/7.17/6.83/6.30）。"
                "涨幅温和但趋势最顺，回踩 MA5 7.30 不破即继续持有。"),
    "600028.SH": ("中国石化", "石油加工贸易·红利",
                "收盘 5.97 恰好 <b>创 60 日新高</b>（收盘=最高=60 日高），量比 1.01 与 5 日均量持平，属<b>创新高不放量</b>的健康形态。"
                "入池（11/02）以来仅 +1.19%，说明突破集中在最近 3 个交易日，属新启动而非追高。"),
    "000001.SZ": ("平安银行", "银行·红利",
                "贴着 9/03 的 60 日高 12.35 横盘，距高 -1.2%，量比 <b>0.80 缩量</b> —— 蓄势但没量。"
                "放量站上 <span class=kn>12.35</span> 才算突破，否则只是高位震荡。"),
    "300364.SZ": ("中文在线", "文化传媒",
                "11/11 冲高 30.38（=当日最高）后 A 型回落，6 个交易日 <b>-23.4%</b>，跌破 MA20 25.43 与 MA60 24.75。"
                "量比 0.65 缩量下跌，短线反抽先看能否收回 <span class=kn>24.75</span>。"),
    "600323.SH": ("瀚蓝环境", "环境治理",
                "池内结构最干净：盘中 <b>31.90 创 60 日新高</b>，收 31.66，量比 1.33 温和放量，MACD <b>当日金叉</b>。"
                "入池（11/09）以来 +1.8%，几乎还在成本区。"),
    "300607.SZ": ("拓斯达", "自动化设备",
                "当日池内最弱 <b>-3.93%</b>，MACD 死叉，距 60 日高 41.94 有 -39.4%，距 60 日低 24.95 只剩 <b>1.9%</b>。"
                "自动化设备方向退潮，<span class=kn>24.95</span> 破位即从池内剔除。"),
    "600993.SH": ("马应龙", "中药",
                "盘中冲到 26.44（=60 日高）后回落收 -0.88%，<b>新高未站稳</b>。但 MA5>10>20>60 全多头排列完好（25.33/25.00/24.65/23.60），"
                "MACD 11/17 金叉；缩量回踩 24.65–25.00 不破则等二次冲高。"),
    "603129.SH": ("春风动力", "汽车服务及其他",
                "入池（11/17）次日 -0.85%，价格在 MA20（303.04）上方、60 日高 329.60（8/20）下方 -5.3%。"
                "20 日高 <span class=kn>325</span> 未过前属高位平台震荡，突破 325 才是右侧加仓信号。"),
}

GROUPS = [
    ("一、新高附近（5 只）· 收盘距 60 日高 ≤2%", ["600028.SH", "000001.SZ", "601107.SH", "600323.SH", "600993.SH"],
     "四只红利/低估值 + 一只中药，是池内唯一站在 60 日高附近的组合；共同点是 MA5>MA10>MA20 多头排列，"
     "不同点是量能——瀚蓝 1.33 放量、石化 1.01 持平、平安 0.80 缩量、成渝 0.82 缩量，<b>突破质量按此排序</b>。"),
    ("二、中继向上（1 只）· 站上 MA20+MA60、距高 5% 内", ["603129.SH"],
     "唯一维持中期多头且未破位的成长股。"),
    ("三、修复中（2 只）· 站上 MA20、MA60 未收复", ["600236.SH", "603225.SH"],
     "两只都已收复短期均线群、仍在 MA60 之下：桂冠靠放量、新凤鸣靠缩量整理。MA60 是这两只的中期开关。"),
    ("四、破位区（5 只）· 跌破 MA20，距 60 日高均超 18%", ["002821.SZ", "603009.SH", "300593.SZ", "300364.SZ", "300607.SZ"],
     "无一例外是 9–11 月的高位股在杀估值/杀题材：机器人（北特、拓斯达）、传媒（中文在线）、电源（新雷能）、CXO（凯莱英）。"
     "缩量下跌（0.65–1.04）说明抛压未释放完，<b>只观察不参与</b>。"),
]


def cls(v):
    return "up" if v > 0 else ("down" if v < 0 else "")


def spy(s, v, fmt="{:.2f}", pct=True):
    t = f"{fmt.format(v)}" + (f" ({v:+.2f}%)" if pct else "")
    return f'<span class="{cls(v)}">{t}</span>'


# 汇总
n_up = sum(1 for s in P if s["pct"] > 0)
n_down = sum(1 for s in P if s["pct"] < 0)
amt = sum(s["amount_yi"] for s in P)
n_hi = sum(1 for s in P if s["tag"] == "新高附近")
n_brk = sum(1 for s in P if s["tag"] == "破位区")
n_win = sum(1 for s in P if (s["entry_pct"] or 0) > 0)

rows = []
for s in P:
    rows.append(
        f'<tr><td class="num">{s["idx"]}</td>'
        f'<td><b>{s["name"]}</b> <span class="meta">{s["code"].split(".")[0]}</span></td>'
        f'<td>{s["industry"]}</td>'
        f'<td class="num">{s["close"]:.2f}</td>'
        f'<td class="num"><span class="{cls(s["pct"])}">{s["pct"]:+.2f}%</span></td>'
        f'<td class="num">{s["amount_yi"]:.2f}</td>'
        f'<td class="num">{s["total_mv_yi"]:.0f}</td>'
        f'<td class="num">{s["from_hi"]:+.1f}%</td>'
        f'<td class="num"><span class="{cls(s["entry_pct"] or 0)}">{s["entry_pct"]:+.2f}%</span></td>'
        f'<td><span class="tag {TAGCLS[s["tag"]]}">{s["tag"]}</span></td></tr>'
    )

TABLE = ('<div class="twx" data-tw="1"><div class="tw" data-tw="1"><table>'
         '<thead><tr><th>#</th><th>标的</th><th>所属行业</th><th>收盘</th><th>涨跌</th>'
         '<th>成交额(亿)</th><th>总市值(亿)</th><th>距60日高</th><th>入池以来</th><th>结构</th></tr></thead>'
         f'<tbody>{"".join(rows)}</tbody></table></div></div>')

sections = []
for title, codes, lead in GROUPS:
    blocks = []
    for c in codes:
        s = BY[c]
        name, ind, text = TODO[c]
        blocks.append(
            f'<h3>{s["idx"]}. {name} {s["code"].split(".")[0]} <span class="meta">· {ind} · 入池 {s["in_date"][4:6]}/{s["in_date"][6:]}</span> '
            f'<span class="tag {TAGCLS[s["tag"]]}">{s["tag"]}</span></h3>'
            f'<p>{text}</p>'
            f'<img class="chart" src="../charts/{s["chart"]}" alt="{name} 日线K线">'
            f'<p class="cap">{name} · 收 {s["close"]:.2f}（{s["pct"]:+.2f}%）· MA20 {s["ma20"]:.2f} · '
            f'量比 {s["vol_ratio"]:.2f} · 60 日高 {s["hi60"]:.2f}（{s["hi_date"][5:]}）</p>'
        )
    sections.append(f'<h2>{title}</h2><p>{lead}</p>{"".join(blocks)}')

FOCUS = [
    ("瀚蓝环境", "收盘站上 31.90（60 日高）且量比 &gt;1 → 突破确认；收在 31.00（MA20）下方 → 假突破"),
    ("中国石化", "连续 2 日收在 5.97 上方、缩量回踩不破 5.70（MA20）→ 突破有效"),
    ("马应龙", "回踩 24.65（MA20）缩量不破、再上攻 26.44 → 二次冲高成立"),
    ("桂冠电力", "收复 9.57（MA60）→ 升级为均线全多头，可提高观察级别"),
    ("拓斯达 / 新雷能", "跌破 24.95 / 19.03（各自 60 日低）→ 从池内剔除"),
]

focus_html = "".join(f"<li><b>{a}</b>：{b}</li>" for a, b in FOCUS)

HTML = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{TITLE}</title>
<link rel="stylesheet" href="../assets/css/report-table.css">
{CSS}
</head>
<body>
<div class="wrap">

<div class="hero">
  <h1>📊 {TITLE}</h1>
  <p class="meta">都业华《高级班》· 类二买共振股池 · 数据截至 2026-11-18 收盘</p>
  <p class="stance"><b>池内 4 涨 9 跌，结构极端分化：红利/低估值站在 60 日高附近，题材端全线破位。</b>
  类二买在池内并非同时兑现——只有 5 只仍在结构内、5 只已破位，仓位应向「新高附近 + 修复中」7 只倾斜。</p>
</div>

<div class="grid4">
  <div class="kpi"><div class="label">池内涨跌</div><div class="val"><span class="up">{n_up} 涨</span> / <span class="down">{n_down} 跌</span></div><div class="sub">13 只全部有成交</div></div>
  <div class="kpi"><div class="label">合计成交额</div><div class="val vol">{amt:.1f} 亿</div><div class="sub">单只中位 3.41 亿</div></div>
  <div class="kpi"><div class="label">新高附近</div><div class="val">{n_hi} 只</div><div class="sub">距 60 日高 ≤2%</div></div>
  <div class="kpi"><div class="label">破位区</div><div class="val">{n_brk} 只</div><div class="sub">跌破 MA20</div></div>
</div>

<h2>结论卡</h2>
<div class="box box-a">
<p><b>1. 强的更强、弱的更弱。</b>站上 60 日高附近的 5 只（石化、平安、成渝、瀚蓝、马应龙）全是红利/低估值/中药，无一只是 9 月后的题材股；
破位的 5 只全是机器人、传媒、电源方向的 9–11 月高位股。</p>
<p><b>2. 入池收益与当下结构无关。</b>入池以来 {n_win} 只正收益，但其中凯莱英（+13.1%）已破位、中文在线（-10.5%）早已转弱 ——
类二买是「买点信号」，不是「持有的理由」，信号失效就要按结构走。</p>
<p><b>3. 可动的只有 3 只。</b>瀚蓝（新高 + 当日金叉）、石化（新高不放量）、成渝（完整多头排列）结构内最干净；
其余 10 只等条件：修复中 2 只看 MA60，破位 5 只只观察。</p>
</div>

<h2>股池总表（2026-11-18 收盘）</h2>
{TABLE}
<p class="cap">成交额、总市值与老师原表逐项核对一致（中国石化 7206.7 vs 7207 亿、平安银行 2367.5 vs 2368 亿）。「入池以来」= 入池日收盘 → 11/18 收盘（前复权）。</p>

{"".join(sections)}

<h2>明日关注（5 条可验证条件）</h2>
<ol>{focus_html}</ol>

<h2>口径</h2>
<div class="box">
<p>· 数据：Tushare 日线前复权，基准 = 2026-11-18 收盘；MA/量比/MACD 均由该序列计算，量比 = 当日量 ÷ 含当日 5 日均量。</p>
<p>· 「类二买共振」为老师原文口径（至少两个周期同时出现类二买结构）；本页只做日线级核验，未复算分钟级结构。</p>
<p>· 日期列 = 入池日；结构分档按「距 60 日高 + MA20/MA60 + MACD」机械判定，不含主观加减分。</p>
</div>

<div class="foot">
<p>数据源：Tushare pro.daily / daily_basic · 图为日线 K 线（红涨绿跌）+ 成交量 + MACD，均线 MA5/10/20。
仅作方法与结构记录，不构成投资建议。生成于 2026-11-18。</p>
</div>

</div>
</body>
</html>
"""

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(patch_html(HTML), encoding="utf-8")
print("written", OUT)
