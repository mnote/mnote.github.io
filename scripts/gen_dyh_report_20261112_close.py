"""生成 2026-11-12 都业华《高级班》收评纪要 HTML（白底 · 收盘版）

⛔ 2026-11-11 禁令：只用日线 + 实时快照，不调用 1/15 分钟 K 线、不调用 czsc。
📏 2026-11-12 篇幅硬约束：正文 ≤ 2000 字、表格 ≤ 4 张，K 线图保留不计字数。
数据：reports/duyiehua-20261112/data_20261112_close.json
输出：~/workspace/mnote.github.io/2026-11-12-都业华-高级班收评纪要.html
     ~/workspace/mnote.github.io/_posts/2026-11-12-都业华-高级班收评纪要.html
"""
import json
import re
from pathlib import Path

REPO = Path("/Users/maoling/workspace/mnote.github.io")
RPT = REPO / "reports/duyiehua-20261112"
D = json.loads((RPT / "data_20261112_close.json").read_text(encoding="utf-8"))

IDX, BASKET, QUOTES = D["index"], D["basket"], D["quotes"]
ZT, DT, MKT = D.get("zt_pool", {}), D.get("dt_pool", {}), D.get("today_market", {})
PREV = D.get("prev_market", {})
SNAP = D["snapshot_time"].replace(" close", "").split(" ")[-1]

TITLE_SUMMARY = "放量杀跌，机器人崩盘"
TITLE_FULL = f"DYH 收评 - 2026-11-12（周四 {TITLE_SUMMARY}）"

CSS = """<style>
  :root{--bg:#fff;--panel:#f8f9fb;--panel2:#f1f3f6;--border:#e5e7eb;--text:#1f2937;--muted:#6b7280;
    --bull:#16a34a;--bullbg:#dcfce7;--up:#e63946;--down:#2a9d8f;--bear:#dc2626;--bearbg:#fee2e2;--neutral:#d97706;--neutbg:#fef3c7;
    --none:#6b7280;--nonebg:#f3f4f6;--accent:#2563eb;--accentbg:#dbeafe;--key:#7c3aed;}
  *{box-sizing:border-box}
  body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei","Segoe UI",sans-serif;
    background:var(--bg);color:var(--text);line-height:1.6;font-size:14.5px}
  .wrap{max-width:1200px;margin:0 auto;padding:26px 24px 60px}
  h1{font-size:24px;margin:0 0 5px}h2{font-size:18px;margin:26px 0 10px;padding-bottom:6px;border-bottom:2px solid var(--border)}
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
  th{background:var(--panel2);font-weight:600;color:var(--muted);font-size:11.5px}
  tr:hover{background:var(--panel)}td.num{font-variant-numeric:tabular-nums;text-align:right;white-space:nowrap}
  .tag{display:inline-block;padding:1px 7px;border-radius:999px;font-size:10.5px;font-weight:500;white-space:nowrap}
  .tag-bull{background:var(--bullbg);color:var(--bull)}.tag-bear{background:var(--bearbg);color:var(--bear)}
  .tag-neutral{background:var(--neutbg);color:var(--neutral)}.tag-none{background:var(--nonebg);color:var(--none)}
  .chart{width:100%;height:auto;display:block;margin:8px 0 2px;border:1px solid var(--border);border-radius:6px;background:#fff}
  .up{color:var(--up);font-weight:600}.down{color:var(--down);font-weight:600}
  .kn{color:var(--key);font-weight:700;font-variant-numeric:tabular-nums}
  .box{border-radius:8px;padding:8px 12px;margin:8px 0;font-size:13.5px}
  .box-r{background:var(--bearbg)}.box-a{background:var(--accentbg)}.box-g{background:var(--bullbg)}
  .foot{margin-top:30px;padding-top:12px;border-top:1px solid var(--border);font-size:11.5px;color:var(--muted)}
  .vol{color:var(--neutral);font-weight:600}
</style>"""


def cls(v):
    return "up" if v > 0 else ("down" if v < 0 else "flat")


def pct(v):
    return f"{v:+.2f}%"


def q(n):
    for r in QUOTES:
        if r["名称"] == n:
            return r
    return {}


def sp(n):
    r = q(n)
    if not r:
        return "—"
    return f'<span class="{cls(r["涨跌幅%"])}">{r["现价"]:.2f} ({pct(r["涨跌幅%"])})</span>'


sh, sz, cy, kc = IDX["上证指数"], IDX["深证成指"], IDX["创业板指"], IDX["科创50"]
amt_now = round(sh["amount_yi"] + sz["amount_yi"], 1)
amt_prev = round(PREV["sh_amount_yi"] + PREV["sz_amount_yi"], 1)
amt_ratio = round(amt_now / amt_prev * 100, 1)
amt_growth = round((amt_now / amt_prev - 1) * 100, 1)
down_ratio = round(MKT["down"] / MKT["n"] * 100, 1)
B = BASKET

bask_rows = "".join(
    f'<tr><td>{k}</td><td class="num {cls(v["avg_pct"])}">{v["avg_pct"]:+.2f}%</td>'
    f'<td class="num">{v["up"]}/{v["n"]}</td></tr>'
    for k, v in B.items())

# (名称, 老师给的触发条件/位, 实测印证, 状态)
ROWS = [
    ("药明康德", "破 <span class='kn'>157.8</span> 出三买", "最高 151.70 未触，差 6.1"),
    ("中国船舶", "等收复上沿", "最低 33.90 破昨低"),
    ("瑞芯微", "下沿止跌+底分型", "234.88 → 收 220.72，未兑现"),
    ("伊利股份", "破 <span class='kn'>30.46</span> 再拉回", "最低 30.50，差 0.04 未破"),
    ("中文在线", "破 <span class='kn'>30.38</span> 出三买", "最高 29.49 未触"),
    ("海天瑞声", "类二买对称+止跌", "最低 121.31 破 134.03"),
    ("奥普特", "破 <span class='kn'>186.8</span> 或下沿止跌", "最高 173.97 未触 186.8"),
    ("柯力传感", "调整充分+底分型", "最低 54.61 未到 53"),
    ("兆易创新", "止损 <span class='kn'>252.85</span>", "273.68 → 收 258.85"),
    ("云铝股份", "底分型+小级别共振", "收全天最低，距 60 日低 1.3%"),
    ("模塑科技", "回调 <span class='kn'>14.95</span> 止跌", "最高 16.99 &lt; 昨收 17.09"),
    ("汉威科技", "老师直接<b>剔除跟踪</b>", "最低 40.02 跌破 40，转弱"),
    ("长盈精密", "破 <span class='kn'>32.08</span> 出三买", "最高 30.39 未破 32.08"),
]
body_rows = ""
for nm, trig, meas in ROWS:
    body_rows += (f'<tr><td><b>{nm}</b></td><td class="num">{sp(nm)}</td><td>{trig}</td>'
                  f'<td>{meas}</td></tr>')

CAND = [
    ("五粮液 000858", "72.63", "-5.1%", "+1.9%", "距高 76.50"),
    ("洋河股份 002304", "35.89", "-14.8%", "-3.6%", "白酒中最低"),
    ("双汇发展 000895", "24.32", "-4.9%", "+2.1%", "贴高未透支"),
]
cand_rows = "".join(
    f'<tr><td><b>{n}</b></td><td class="num">{c}</td><td class="num">{d}</td><td class="num">{r}</td><td>{note}</td></tr>'
    for n, c, d, r, note in CAND)

CHART_CODES = ["603259_SH", "600150_SH", "603893_SH", "600887_SH", "300364_SZ", "688787_SH",
               "688686_SH", "603662_SH", "603986_SH", "000807_SZ", "000700_SZ", "300007_SZ",
               "300115_SZ"]

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
  <div class="meta">收盘版 · 数据截至 {SNAP}</div>
  <p class="stance"><b>结论：放量杀跌。</b>上证 {sh['price']:.2f}（{pct(sh['pct'])}），两市 {amt_now} 亿（+{amt_growth}%）却 <b>{MKT['down']} 家下跌（{down_ratio}%）</b>、涨停仅 {ZT.get('n','—')} 只。<b>3750 未破仍弱势</b>；最低 {sh['low']:.2f} 破 11/11、11/09 低点 → <b>「创新低」条件已触发</b>，等底背驰。人形机器人 {B['人形机器人']['avg_pct']:+.2f}%（18 只 0 涨）＋两股跌停，强势股洗盘。<b>总仓 ≤4 成、轻仓不追涨；13 只标的全无买点。</b></p>
</div>

<div class="grid4">
  <div class="kpi"><div class="label">上证指数 · 3750 未破</div><div class="val down">{pct(sh['pct'])}</div></div>
  <div class="kpi"><div class="label">两市成交额 · +{amt_growth}%</div><div class="val vol">{amt_now} 亿</div></div>
  <div class="kpi"><div class="label">涨 / 跌家数</div><div class="val"><span class="up">{MKT['up']}</span> / <span class="down">{MKT['down']}</span></div></div>
  <div class="kpi"><div class="label">涨停 / 跌停 · 昨 118</div><div class="val">{ZT.get('n','—')} / {DT.get('n','—')}</div></div>
</div>

<h2>一、指数：弱势定性成立</h2>
<p>上证 {sh['price']:.2f}（低 {sh['low']:.2f}），冲高回落，<b>3750 未破（差 2.6%）</b>。<b>最低 {sh['low']:.2f} 破 11/11 低 3650.31、11/09 低 3653.05 → 老师「向下创新低出底背驰」的新低条件已触发</b>。<b>急涨慢跌</b>：创业板最高 {cy['high']:.2f} → 收 {cy['price']:.2f}（<b>{pct(cy['pct'])}，从高回落 {((cy['high']-cy['price'])/cy['high']*100):.1f}%</b>），<b>科创50 {pct(kc['pct'])}</b> 逆势翻红。放量 {MKT.get('amount_vs_prev_%','—')}% 却普跌 → <b>放量杀跌</b>。</p>
<img class="chart" src="charts/000001_SH_DY_20261112C.png">
<img class="chart" src="charts/399006_SZ_DY_20261112C.png">

<h2>二、板块：防守居首，机器人崩盘</h2>
<table>
  <tr><th>方向（自建篮子）</th><th>均值</th><th>涨/样本</th></tr>
  {bask_rows}
</table>
<p><b>老师四条描述逐条兑现：</b>① <b>半导体放量遇阻回落</b>——上午累计 302.3 亿已超昨日全天 289.1 亿，午盘 +0.90% → 收盘 {B['半导体']['avg_pct']:+.2f}%；② <b>算力冲高回落</b>——午盘 +1.51% → 收盘 {B['算力硬件']['avg_pct']:+.2f}%，中际旭创 -6.11%；③ <b>防守型居前</b>——{B['防守/消费']['avg_pct']:+.2f}% 全场第一，涨停池含白酒、燃气；④ <b>强势股洗牌</b>——福莱新材 -10.00%、上海电影 -9.99% 双跌停。<b>温度 25 度</b>（未连续 3 天站上 30）→ <b>一类热点无</b>；「东方」系高位仍强（日出东方 5 板、大东方 5 板）→「不推荐重点参与」成立。</p>

<h2>三、中线 8 + 短线 5：全无买点</h2>
<table>
  <tr><th>标的</th><th>收盘</th><th>老师给的触发条件（老师口径）</th><th>实测印证（日线触达判据）</th></tr>
  {body_rows}
</table>
{''.join(f'<img class="chart" src="charts/{c}_DY_20261112C.png">' for c in CHART_CODES)}

<h2>四、潜在强势股</h2>
<p>老师只给逻辑「<b>剔除涨幅大、位置不高、中线有上涨概率</b>」，不推荐直接买入；下表 3 只为<b>我方自建观察池</b>：</p>
<table>
  <tr><th>标的</th><th>收盘</th><th>距 60 日高</th><th>20 日</th><th>位置依据</th></tr>
  {cand_rows}
</table>

<h2>五、明日盯什么</h2>
<div class="box box-g">
① <b>3750</b>：突破并出回抽确认三买 → 弱势定性改写；未破仍弱势。<br>
② <b>向下路径</b>：新低 {sh['low']:.2f} 已出，<b>底背驰是否出现</b>决定止跌还是续跌。<br>
③ <b>全 A 反拉</b>：{MKT['down']} 家下跌后能否反拉，上不去即震荡。<br>
④ <b>机器人 18 只 0 涨</b>后是否止跌；强势股是否继续洗牌。<br>
⑤ <b>三条挂单线</b>：兆易止损 252.85、伊利支撑 30.46、药明门槛 157.8 —— 触达才动。
</div>

<h2>六、偏差记录</h2>
<table>
  <tr><th>老师原文</th><th>实测</th><th>判定</th></tr>
  <tr><td>中文在线「维持强势震荡」</td><td>收 -7.69%，跌破 11/10 收盘</td><td><span class="tag tag-bear">偏乐观</span></td></tr>
  <tr><td>药明门槛 157.8（原 151）</td><td>最高 151.70，差 6.1 元</td><td><span class="tag tag-neutral">门槛上移</span></td></tr>
  <tr><td>「全 A 下午顶背驰成立」</td><td>无 881001 数据源，<b>无法核验</b></td><td><span class="tag tag-none">无法核验</span></td></tr>
  <tr><td>「涨幅榜靠前是饮料、白酒」</td><td>涨停池白酒 1 只</td><td><span class="tag tag-neutral">口径偏宽</span></td></tr>
</table>

<div class="foot">
  <p>来源：都业华《高级班》2026-11-12 收评，执业编号 A0400626100004。<b>仅供参考，不作为买卖依据，据此操作风险自担。投资有风险，入市需谨慎！</b><b>口径：</b>{SNAP} 收盘快照 + Tushare 日线；板块为自建篮子均值；涨跌停用东财池（不含 ST）；缠论定性按老师口径。</p>
</div>

</div>
</body>
</html>
"""

OUT = REPO / "2026-11-12-都业华-高级班收评纪要.html"
OUT.write_text(HTML, encoding="utf-8")

# 线上 URL 版：去 Jekyll 后不需要 front matter / permalink，
# 直接把 permalink 当文件名放在仓库根目录即可（图片路径与根目录版一致，不用改 ../）
ONLINE = REPO / "duyiehua-report-20261112.html"
ONLINE.write_text(HTML, encoding="utf-8")

# 正文字数统计（含页脚，去标签、去图、去 CSS）
body = HTML.split("<body>")[1].split("</body>")[0]
text = re.sub(r"<[^>]+>", " ", body)
text = re.sub(r"\s+", "", text)
print(f"written: {OUT.name}  {len(HTML)} bytes")
print(f"written: {ONLINE.name}  {len(HTML)} bytes")
print(f"正文字数（含页脚）: {len(text)} 字 | 表格数: {HTML.count('<table>')} | 图数: {HTML.count('class=\"chart\"')}")
