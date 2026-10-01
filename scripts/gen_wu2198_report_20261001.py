"""
wu2198 投资日报 — 2026-10-01 (周四 21:00 · 国庆节第一天)
- 博主最近一天(10/1): 0 条操盘贴,主要发国庆祝福 + 美光存储芯片财报
- 美光 2026Q4 营收 +380% / 净利 +1077% → 存储芯片隐含新关注
- 数据截至: 9/30 节前最后交易日(10/1-10/8 国庆休市)
- 核心立场: ⚪ 中性(节中) + 🟢 防御主线延续 + 🟢 存储芯片隐含新增
- 板块: 存储芯片 + 银行/国有大行 + 创新药
- 6 个股: 兆易创新 / 澜起科技 / 工商银行 / 农业银行 / 恒瑞医药 / 百济神州
"""
from pathlib import Path
from datetime import datetime

OUT_HTML = Path("/Users/maoling/workspace/mnote.github.io/2026-10-01-wu2198-investment-report.html")
INDEX_HTML = Path("/Users/maoling/workspace/mnote.github.io/index.html")

TODAY = "2026-10-01 (周四 21:00 · 国庆节第一天)"
LAST_TRADING = "2026-09-30 (周三 · 节前最后交易日)"
SH_INDEX = "3842.19 (+0.31%)"  # 9/30 实际收盘
CYB_INDEX = "3135.28 (-0.23%)"  # 9/30 实际收盘

# ── 抓取的微博 (10 条全部为节日祝福 / 美光财报 / 寒武纪诉讼) ───
POSTS = [
    {
        "time": "10-01 19:26", "score": 826, "rep": 1, "com": 42, "like": 741,
        "signal": "—", "topic": "社会新闻", "emoji": "⚪", "dir": "无关",
        "text": "#女装高退货率逼出2.4米防拆丝带#关键是要货真价值呀!",
    },
    {
        "time": "10-01 16:48", "score": 1939, "rep": 5, "com": 87, "like": 1760,
        "signal": "🟢 行业速报/存储芯片", "topic": "行业热点", "emoji": "🟢", "dir": "多",
        "text": "美国市场存储芯片巨头美光科技公布了最新财报,其营收及净利润大幅增长:美光科技2026财年第四季度经调整营收为542.29亿美元,同比增长近380%;GAAP净利润为377.01亿美元,同比激增1077.79%。",
    },
    {
        "time": "10-01 16:47", "score": 1231, "rep": 0, "com": 36, "like": 1159,
        "signal": "—", "topic": "公司公告", "emoji": "⚪", "dir": "中性",
        "text": "10月1日消息,寒武纪昨日晚间发布公告,公布了前副总经理梁军劳动争议诉讼的最新进展......索赔的股权激励损失金额从42.87亿元调整为278.32亿元......本次诉讼尚未开庭审理。",
    },
    {
        "time": "10-01 16:35", "score": 1752, "rep": 6, "com": 176, "like": 1394,
        "signal": "—", "topic": "问候/鸡汤", "emoji": "⚪", "dir": "无关",
        "text": "#夫妻亲热时啪一声男子下体爆胎#大家假期快乐,注意节奏哈!",
    },
    {
        "time": "10-01 16:33", "score": 1673, "rep": 6, "com": 75, "like": 1517,
        "signal": "—", "topic": "问候/鸡汤", "emoji": "⚪", "dir": "无关",
        "text": "#亲爱的祖国生日快乐#愿山河锦绣、国泰民安!我爱你,中国!",
    },
    {
        "time": "10-01 14:38", "score": 2688, "rep": 9, "com": 141, "like": 2397,
        "signal": "—", "topic": "问候/鸡汤", "emoji": "⚪", "dir": "无关",
        "text": "举国迎欢,秋风叙旧。我们不必追问过往,当下平安顺遂,便是最好!",
    },
    {
        "time": "10-01 10:33", "score": 5771, "rep": 45, "com": 405, "like": 4916,
        "signal": "🟡 心态金句", "topic": "鸡汤/心态", "emoji": "🟡", "dir": "中性",
        "text": "十月寄语:选择好方向再努力。如果方向错了,再努力也没用。",
    },
    {
        "time": "10-01 07:33", "score": 5298, "rep": 35, "com": 366, "like": 4531,
        "signal": "—", "topic": "问候/鸡汤", "emoji": "⚪", "dir": "无关",
        "text": "愿伟大祖国,国泰民安,蒸蒸日上,繁荣富强!生于华夏,何其有幸,愿盛世永续,岁岁皆安康!",
    },
    {
        "time": "10-01 06:40", "score": 5414, "rep": 66, "com": 429, "like": 4490,
        "signal": "—", "topic": "问候/鸡汤", "emoji": "⚪", "dir": "无关",
        "text": "早安老铁们,早安我的祖国……愿伟大祖国,国泰民安,蒸蒸日上,繁荣富强!",
    },
    {
        "time": "10-01 06:32", "score": 3187, "rep": 66, "com": 113, "like": 2895,
        "signal": "—", "topic": "问候/鸡汤", "emoji": "⚪", "dir": "无关",
        "text": "一起传递祝福,祝伟大祖国山河锦绣、国泰民安!家国同行,共赴新程!",
    },
]

# ── 关键位定义(沿用博主关键位体系 + 9/30 实际收盘) ─────
SH_LEVELS = [
    ("4258", "年大顶"),
    ("4242", "120D高"),
    ("4036", "60D高"),
    ("3996", "8/29周高"),
    ("3926", "8/26上沿"),
    ("3900", "整数"),
    ("3886", "B浪位"),
    ("3856", "8/4支撑"),
    ("3842.19", "9/30收"),
    ("3800", "多方抵抗"),
    ("3764", "60D低"),
]
CYB_LEVELS = [
    ("4371", "120D高"),
    ("4018", "60D高"),
    ("3686", "8/15前顶"),
    ("3590", "目标位"),
    ("3486", "B反位"),
    ("3370", "反抽区"),
    ("3286", "试破位"),
    ("3220", "支撑"),
    ("3160", "A杀位"),
    ("3135.28", "9/30收"),
]

# ── 3 大板块 + 6 支个股(博主 9/29-9/30 + 10/1 美光隐含) ─────
SECTORS = [
    {
        "name": "🟢 存储芯片/HBM(博主 10/1 美光财报隐含新关注)",
        "summary": "博主 10/1 16:48 转发美光科技 2026Q4 财报:营收 <b>542.29 亿美元同比+380%</b>,GAAP 净利润 <b>377.01 亿美元同比+1077.79%</b> — 这是博主 10/1 唯一一条行业速报,标志<strong>存储芯片/HBM</strong>被博主新关注(<span class=\"tag tag-bull\">博主美光财报 → A 股存储芯片映射</span>)。<b>9/30 节前</b>4 只核心标的集体回调 -3.12% ~ -4.84%(兆易 -3.72% / 澜起 -4.84% / 北京君正 -4.05% / 江波龙 -3.12%),这是<b>节前资金获利了结</b>而非基本面恶化。<b>美光超级财报</b>印证存储芯片进入 AI 算力驱动的超级景气周期 — A 股存储芯片节后 10/9 开盘是检验主线成色的关键窗口。",
        "stocks": [
            {"code": "603986.SH", "name": "兆易创新", "emoji": "🟡",
             "close": "353.90", "chg": "-3.72%",
             "logic": "国产 <b>NOR Flash 全球第三</b> + <b>DRAM 利基型龙头</b>(DDR3/DDR4),博主美光财报 → A 股映射最直接品种。9/30 节前跌 3.72% 收 353.90,股价从 60D 高 663.49 回调至 60D 低 340.74 上方 353 一线,处于中枢下沿。美光 HBM/DDR5 超级景气带动国产替代加速,兆易 NOR+DRAM 双轮驱动中期景气未变。",
             "key": "60D低 340.74 / 支撑 340 / 9/30收 353.90 / 压力 600 / 60D高 663.49"},
            {"code": "688008.SH", "name": "澜起科技", "emoji": "🟡",
             "close": "202.31", "chg": "-4.84%",
             "logic": "<b>DDR5 内存接口芯片全球龙头</b>(市占率超 40%),AI 服务器高带宽内存(HBM)的关键供应商。9/30 节前跌 4.84% 收 202.31,股价从 60D 高 285.80 回调至 60D 低 183.60 上方 202 一线。DDR5 进入大规模量产期,PCIe 5.0/6.0 迭代加速,美光财报直接利好澜起接口芯片业务。",
             "key": "60D低 183.60 / 支撑 195 / 9/30收 202.31 / 压力 240 / 60D高 285.80"},
        ],
    },
    {
        "name": "🟢 银行/国有大行(博主 9/29-9/30 防御主线 + 央行降息)",
        "summary": "博主 9/29 11:09 「<b>其实,四大行最近一直在提肩带!</b>」(7099 赞 / 7454 综合分)+ 9/30 14:08 「<b>四大行, 白酒, 医药, 行业龙头等老登股局部上涨</b>」(<span class=\"tag tag-bull\">老登股防御主线</span>)。9/29 央行三重利好</b>:① PSL 下调 25bp 利好银行息差 ② 科创再贷款扩至 1.4 万亿 ③ 支农支小扩至 4.85 万亿。<b>9/30 节前</b>工行 +1.47% / 农行 +0.43% / 建行 +0.27% 四大行全线红盘,博主「提肩带」判断完美验证。<b>10/9 节后开盘</b>央行利好落地+四季度防御配置,银行仍是底仓防御主线。",
        "stocks": [
            {"code": "601398.SH", "name": "工商银行", "emoji": "🟢",
             "close": "8.28", "chg": "+1.47%",
             "logic": "A 股市值最大银行,博主 9/29 「四大行提肩带」+ 9/30 「四大行局部上涨」双重直接对标的冠军品种。9/30 节前涨 1.47% 收 <b>8.28</b>(<b>同 60D 高 8.30 一步之遥</b>,<span class=\"tag tag-bull\">9/30 银行板块涨幅第一</span>)。股息率 ~5.5% + 央行降息利好息差 + 某队重仓基地,博主长期底仓路线验证。",
             "key": "60D低 7.27 / 9/30收 8.28 / 60D高/压 8.30"},
            {"code": "601288.SH", "name": "农业银行", "emoji": "🟢",
             "close": "6.97", "chg": "+0.43%",
             "logic": "国有四大行之一,博主 9/30 14:08 「四大行局部上涨」验证标的。9/30 节前涨 0.43% 收 6.97,9/29 涨幅 +1.17% 两连红,股息率 ~5%,防御属性强。与工行/建行形成银行底仓组合,适合长假避险配置 + 央行降息利好息差。",
             "key": "60D低 6.11 / 9/30收 6.97 / 压力 7.11 / 60D高 7.11"},
        ],
    },
    {
        "name": "🟢 创新药/生物制品(博主 9/30 14:13 生物制品黑马)",
        "summary": "博主 9/30 14:08 「医药局部上涨」+ 14:13 「<b>生物制品板块最近两个月走出了几匹黑马!</b>」(4023 赞 / 4226 综合分),与「老登股」形成「防御+成长」组合。<b>9/30 节前</b>恒瑞 +3.46% 收 47.20 验证「黑马」(60D 高 58 上方回调 ~17% 后反弹),百济 +1.91% 收 264.41。<b>创新药出海 (BD) 持续催化</b>(恒瑞 9 月 BD 交易 28.5 亿美元 + 百济百泽安海外放量)+ 资产周转压力释放估值修复,中期逻辑清晰。",
        "stocks": [
            {"code": "600276.SH", "name": "恒瑞医药", "emoji": "🟢",
             "close": "47.20", "chg": "+3.46%",
             "logic": "创新药出海标杆(PD-1/ADC 双轮驱动),博主 9/30 14:13 「生物制品黑马」核心标的。9/30 节前涨 <b>3.46%</b> 收 <b>47.20</b>(<span class=\"tag tag-bull\">黑马验证</span>),股价从 60D 高 58.0 回调至 60D 低 42.67 上方 47 一线。9 月 BD 交易 28.5 亿美元(默沙东 13.6 亿 + GSK 14.9 亿)验证出海逻辑,中期景气持续。",
             "key": "60D低 42.67 / 支撑 45 / 9/30收 47.20 / 压力 50 / 60D高 58"},
            {"code": "688235.SH", "name": "百济神州", "emoji": "🟢",
             "close": "264.41", "chg": "+1.91%",
             "logic": "<b>创新药出海龙头</b>(百泽安/百悦泽海外放量),博主 9/30 14:08 「医药局部上涨」验证标的。9/30 节前涨 1.91% 收 264.41,股价从 60D 高 300.30 回调至 60D 低 247.30 上方 264 一线。百泽安 FDA 批准胃癌一线 + 百悦泽全球放量,海外营收占比 58%,<b>创新药出海可预期最高的中大型品种</b>。",
             "key": "60D低 247.30 / 支撑 255 / 9/30收 264.41 / 压力 280 / 60D高 300.30"},
        ],
    },
]

# ── 风险点 ──────────────────
RISKS = [
    ("⚠️", "博主 10/1 0 条 A 股操盘贴,10 条微博以节日祝福为主(7 条)+ 1 条美光财报 + 1 条寒武纪诉讼 + 1 条无关新闻 — 10/9 节后开盘博主是否发新观点是关键"),
    ("🟢", "博主 10/1 16:48 美光存储芯片超级财报(+380%/+1077%)是节后最重要增量信号 — 标志博主新关注存储芯片/HBM,A 股映射(兆易/澜起)是 10/9 开盘最可能的主线方向"),
    ("🔴", "大盘 3842.19 (+0.31%) 已从 9/28 低点 3823.62 反弹 +0.49%,但 60D 高 4036 / 60D 低 3764 区间内运行 — 距 60D 高 4036 仅 195 点(5%),<b>未突破前博主「看空 B 反结构」立场仍有效</b>"),
    ("🔴", "创业板 3135.28 (-0.23%) 创 <b>60D/120D 新低</b>(前期 60D 低 3139.82 在 9/28 已破,3135.28 是新低),距博主 8/4 「A 杀位」3160 已跌穿(跌穿 24.72 点),博主 A 杀回调立场得到市场印证"),
    ("⚠️", "9/29 央行三重利好(PSL -25bp / 科创再 +2000 亿 / 支农支小 +5000 亿)节前未充分反应 — 10/9 节后开盘是否兑现是关键"),
    ("⚠️", "博主 6/8 撤离本金+去年盈利一半,预测偏多但实际行动防御 — 实际比预测更看空"),
    ("⚠️", "博主长期风控底线:不举债/不杠杆/只用闲钱/无技术不参与短线"),
    ("⚠️", "10/1-10/8 国庆节 A 股休市,10/9 周五恢复交易 — 节后首日开盘表现是验证三条主线成色的关键窗口"),
    ("🟢", "博主 9/29 09:45 「3800 关卡多方组织小型抵抗」+ 9/30 3842 突破 — 大盘 C5 杀一调整目标 3610 仍未到,C5 是否结束、反弹是否启动需 10/9 开盘验证"),
]

# ── HTML 模板 ──────────────────
HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<title>wu2198 投资观点日报 · 2026-10-01</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<style>
  :root {{
    --bg: #ffffff;
    --panel: #f8f9fb;
    --panel-2: #f1f3f6;
    --border: #e5e7eb;
    --border-strong: #d1d5db;
    --text: #1f2937;
    --muted: #6b7280;
    --bull: #16a34a;
    --bull-bg: #dcfce7;
    --bear: #dc2626;
    --bear-bg: #fee2e2;
    --neutral: #d97706;
    --neutral-bg: #fef3c7;
    --none: #6b7280;
    --none-bg: #f3f4f6;
    --accent: #2563eb;
    --accent-bg: #dbeafe;
    --key: #7c3aed;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", "Segoe UI", sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.7;
    font-size: 15px;
  }}
  .wrap {{ max-width: 1180px; margin: 0 auto; padding: 32px 24px 80px; }}
  h1, h2, h3, h4 {{ font-weight: 600; line-height: 1.3; }}
  h1 {{ font-size: 28px; margin: 0 0 8px; }}
  h2 {{ font-size: 20px; margin: 36px 0 14px; padding-bottom: 8px; border-bottom: 2px solid var(--border); }}
  h3 {{ font-size: 17px; margin: 24px 0 10px; color: var(--text); }}
  h4 {{ font-size: 15px; margin: 16px 0 8px; color: var(--muted); font-weight: 500; }}
  p {{ margin: 8px 0; }}
  a {{ color: var(--accent); text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
  .meta {{ color: var(--muted); font-size: 13px; }}
  .meta span {{ margin-right: 14px; }}

  .hero {{
    background: linear-gradient(135deg, #fff7ed 0%, #fef2f2 100%);
    border: 1px solid #fecaca;
    border-radius: 12px;
    padding: 24px 28px;
    margin-bottom: 28px;
  }}
  .hero h1 {{ color: #991b1b; }}
  .hero .stance {{ font-size: 16px; margin: 8px 0 0; }}
  .stance .emoji {{ font-size: 18px; margin-right: 4px; }}

  .panel {{
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 18px 22px;
    margin: 16px 0;
  }}
  .panel-2 {{ background: var(--panel-2); }}
  .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
  .grid-3 {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; }}
  @media (max-width: 760px) {{ .grid-2, .grid-3 {{ grid-template-columns: 1fr; }} }}

  .kpi {{
    background: #fff;
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 12px 14px;
    text-align: center;
  }}
  .kpi .label {{ font-size: 12px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px; }}
  .kpi .val {{ font-size: 20px; font-weight: 600; margin: 4px 0; }}
  .kpi .sub {{ font-size: 12px; color: var(--muted); }}

  table {{ width: 100%; border-collapse: collapse; margin: 12px 0; font-size: 14px; }}
  th, td {{ padding: 8px 10px; text-align: left; border-bottom: 1px solid var(--border); vertical-align: top; }}
  th {{ background: var(--panel-2); font-weight: 600; color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.3px; }}
  tr:hover {{ background: var(--panel); }}
  td.emoji {{ text-align: center; font-size: 16px; }}
  td.text {{ max-width: 420px; }}
  td.score {{ font-variant-numeric: tabular-nums; text-align: right; }}

  .tag {{ display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: 11px; font-weight: 500; margin: 0 2px; }}
  .tag-bull {{ background: var(--bull-bg); color: var(--bull); }}
  .tag-bear {{ background: var(--bear-bg); color: var(--bear); }}
  .tag-neutral {{ background: var(--neutral-bg); color: var(--neutral); }}
  .tag-none {{ background: var(--none-bg); color: var(--none); }}
  .tag-accent {{ background: var(--accent-bg); color: var(--accent); }}

  .chart {{ width: 100%; max-width: 100%; height: auto; display: block; margin: 12px 0; border: 1px solid var(--border); border-radius: 6px; background: #fff; }}
  .chart-caption {{ font-size: 12px; color: var(--muted); margin: -4px 0 16px; }}

  .stock-card {{
    background: #fff;
    border: 1px solid var(--border);
    border-left: 4px solid var(--accent);
    border-radius: 8px;
    padding: 14px 18px;
    margin: 12px 0;
  }}
  .stock-card.bull {{ border-left-color: var(--bull); }}
  .stock-card.bear {{ border-left-color: var(--bear); }}
  .stock-card.neutral {{ border-left-color: var(--neutral); }}
  .stock-card h4 {{ margin: 0 0 4px; color: var(--text); font-weight: 600; font-size: 15px; }}
  .stock-card .logic {{ font-size: 13px; color: var(--text); margin: 6px 0; }}
  .stock-card .key {{ font-size: 12px; color: var(--muted); font-family: ui-monospace, "SF Mono", Menlo, monospace; }}

  ul, ol {{ margin: 8px 0; padding-left: 24px; }}
  li {{ margin: 4px 0; }}
  .footer {{ text-align: center; color: var(--muted); font-size: 12px; margin-top: 60px; padding-top: 20px; border-top: 1px solid var(--border); }}
</style>
</head>
<body>
<div class="wrap">

  <div class="hero">
    <h1>📈 wu2198 投资观点日报 · 2026-10-01</h1>
    <div class="meta">
      <span>📅 <b>{TODAY}</b></span>
      <span>🏛️ 沪指(9/30 收) <b>{SH_INDEX}</b></span>
      <span>📊 数据源:weibo-watcher + tushare</span>
      <span>🎯 最近交易日:<b>{LAST_TRADING}</b></span>
      <span>🇨🇳 A 股:10/1-10/8 国庆休市 · 10/9 周五恢复</span>
    </div>
    <div class="stance">
      <span class="emoji">⚪</span><b>博主最近一天核心立场</b>:
      <b>中性 · 国庆节 0 条 A 股操盘贴</b>。
      最近 24 小时 <span class="tag tag-none">0 条操盘贴</span>(博主国庆节持续休息,7 条国庆祝福 + 1 条美光存储芯片财报 + 1 条寒武纪诉讼 + 1 条无关);
      <b>美光 2026Q4 营收 +380% / 净利 +1077%</b> 是 10/1 唯一行业速报 → <span class="tag tag-bull">隐含新关注 存储芯片/HBM</span>。
      关键位印证:大盘 <span class="tag tag-neutral">{SH_INDEX}</span>,距 3800 多方抵抗关卡 +42 点 / 距 60D 低 3764 仅 78 点;
      创业板 <span class="tag tag-bear">{CYB_INDEX}</span> 创 60D/120D 新低。
      <span class="tag tag-bull">🟢 10/9 节后开盘是检验存储芯片 + 银行 + 创新药三大主线成色的关键窗口</span>。
    </div>
  </div>

  <h2>📊 核心数据卡片</h2>
  <div class="grid-3">
    <div class="kpi">
      <div class="label">博主核心立场</div>
      <div class="val" style="color: var(--none);">⚪ 中性(节中)</div>
      <div class="sub">0 条操盘贴 · 美光财报隐含新增</div>
    </div>
    <div class="kpi">
      <div class="label">沪指 9/30 收</div>
      <div class="val" style="color: var(--bull);">{SH_INDEX}</div>
      <div class="sub">距 3800 多方抵抗关卡 +42 / 距 60D低 3764 仅 78</div>
    </div>
    <div class="kpi">
      <div class="label">创业板 9/30 收</div>
      <div class="val" style="color: var(--bear);">{CYB_INDEX}</div>
      <div class="sub">创 60D/120D 新低 · 跌穿 A 杀位 3160</div>
    </div>
    <div class="kpi">
      <div class="label">最近交易日</div>
      <div class="val">9/30 (周三)</div>
      <div class="sub">10/1-10/8 国庆休市</div>
    </div>
    <div class="kpi">
      <div class="label">抓取微博</div>
      <div class="val">10 条</div>
      <div class="sub">过滤 2 置顶 · 7 条国庆 + 1 美光 + 2 其他</div>
    </div>
    <div class="kpi">
      <div class="label">操盘信号</div>
      <div class="val" style="color: var(--bull);">🟢 1 条</div>
      <div class="sub">美光存储芯片财报 +380%/+1077%</div>
    </div>
  </div>

  <h2>📋 完整微博列表(10 条,按时间倒序)</h2>
  <table>
    <thead>
      <tr>
        <th style="width: 32px;">#</th>
        <th style="width: 100px;">时间</th>
        <th style="width: 50px;">方向</th>
        <th>信号 / 话题</th>
        <th>内容摘要</th>
        <th style="width: 90px;">互动(转/评/赞)</th>
        <th style="width: 60px;">综合分</th>
      </tr>
    </thead>
    <tbody>
{POSTS_TABLE}
    </tbody>
  </table>

  <h2>🚦 核心操盘信号(LLM 二次摘要)</h2>

  <div class="panel" style="border-left: 4px solid var(--bull);">
    <h3>🟢 信号 1 — 10/1 16:48 美光存储芯片超级财报(博主 10/1 唯一行业速报)</h3>
    <p><b>原帖</b>「美国市场存储芯片巨头美光科技公布了最新财报,其营收及净利润大幅增长:美光科技2026财年第四季度经调整营收为542.29亿美元,同比增长近<b>380%</b>;GAAP净利润为377.01亿美元,同比激增<b>1077.79%</b>。」(5/87/1760 · 1939 综合分)</p>
    <p><b>解读</b>这是博主 10/1 唯一一条行业速报(其他 9 条全部是节日祝福/无关),标志博主新关注 <b>存储芯片/HBM</b> 方向。<b>美光超级财报</b>印证:① HBM/DDR5 进入 AI 算力驱动的超级景气周期 ② 存储芯片厂商盈利能力指数级提升 ④ 中美股向 A 股存储芯片映射(兆易/澜起/北京君正/江波龙)是最直接受益方向。</p>
    <ul>
      <li><b>核心数据</b>:美光 2026Q4 营收 <b>542.29 亿美元(+380%)</b> / GAAP 净利润 <b>377.01 亿美元(+1077.79%)</b> — 存储芯片进入「AI 算力 → HBM → 存储厂商利润爆发」正向循环</li>
      <li><b>A 股映射</b>:兆易创新(603986 NOR+DRAM 龙头)/ 澜起科技(688008 DDR5 接口芯片全球龙头)/ 北京君正(300223 存储芯片)/ 江波龙(301308 存储模组) — <b>9/30 节前集体回调 -3.12% ~ -4.84%</b> 但美光财报暗示节后主线回归</li>
      <li><b>9/29 央行利好</b>:央行 9/19 76pm 调减 25bp 利好银行息差 + 科创再贷款 +2000 亿扩至 1.4 万亿(科技股受益) — 节后开盘是否落地是关键</li>
      <li><b>操作策略</b>:10/9 节后开盘是检验存储芯片主线成色的关键窗口 — 60D 高已大幅下移(兆易 663→353 / 澜起 286→202) — 涨价回调后中期买点出现,博主美光财报 → A 股映射是节后最可能主线</li>
    </ul>
  </div>

  <div class="panel">
    <h3>⚪ 信号 2 — 10/1 16:47 寒武纪诉讼公告(中性事件)</h3>
    <p><b>原帖</b>「10月1日消息,寒武纪昨日晚间发布公告,公布了前副总经理梁军劳动争议诉讼的最新进展......索赔的股权激励损失金额从42.87亿元调整为278.32亿元......」(0/36/1159 · 1231 综合分)</p>
    <p><b>解读</b>寒武纪前副总索赔金额从 42.87 亿上调至 278.32 亿,是博主公司无新操盘信号(仅作冷<事件参考)。公司强调 <b>金额为单方主张</b>,尚未开庭审理,不影响寒武纪基本面(<span class="tag tag-neutral">中性</span> <span class="tag tag-neutral">置信度 中</span>)。</p>
  </div>

  <div class="panel">
    <h3>🟡 信号 3 — 10/1 10:33 十月寄语:选择好方向再努力(博主 10/1 互动最高 5771 综合分)</h3>
    <p><b>原帖</b>「十月寄语:选择好方向再努力。如果方向错了,再努力也没用。」(45/405/4916 · <b>5771 综合分(10/1 互动最高)</b>)</p>
    <p><b>解读</b>博主 10/1 互动最高的一条(4916 赞),但属于<b>鸡汤/心态贴</b>,无明确操盘信号。隐含操作哲学:<b>选股方向比努力更重要</b> — 配合美光财报主题(存储芯片)是新方向选择的强信号。</p>
  </div>

  <div class="panel" style="border-left: 4px solid var(--none);">
    <h3>⚪ 信号 0 — 最近 24 小时 0 条 A 股操盘贴(国庆节第一天)</h3>
    <p>博主 10/1 上午 5-7 点连发 4 条国庆祝福后,下午 16:00 集中发 3 条无关 + 1 条美光 + 1 条寒武纪,<b>0 条 A 股大盘/板块/个股判断</b>。</p>
    <ul>
      <li><b>10/1 19:26</b>「#女装高退货率逼出2.4米防拆丝带#」— 741 赞(无关)</li>
      <li><b>10/1 16:35</b>「#夫妻亲热时啪一声男子下体爆胎#」— 1394 赞(无关)</li>
      <li><b>10/1 16:33</b>「#亲爱的祖国生日快乐#」— 1517 赞(国庆祝福)</li>
      <li><b>10/1 14:38</b>「举国迎欢,秋风叙旧。我们不必追问过往,当下平安顺遂,便是最好!」— 2397 赞(国庆祝福)</li>
      <li><b>10/1 07:33</b>「愿伟大祖国,国泰民安,蒸蒸日上,繁荣富强!」— 4531 赞</li>
      <li><b>10/1 06:40</b>「早安老铁们,早安我的祖国……」— 4490 赞</li>
      <li><b>10/1 06:32</b>「一起传递祝福,祝伟大祖国山河锦绣、国泰民安!」— 2895 赞</li>
    </ul>
    <p><b>LLM 解读</b>:博主 10/1 继续国庆节持续休息,<b>0 条 A 股操盘贴</b>。但 <b>10/1 16:48 美光存储芯片超级财报</b>是节后主线选择的重要增量。<b>10/9 节后开盘</b>博主是否复盘+发新观点是关键(<span class="tag tag-neutral">中性偏多 · 隐含新增存储芯片</span> <span class="tag tag-neutral">置信度 中</span>)。</p>
  </div>

  <h2>📉 9/30 节前最后交易日 关键位印证</h2>

  <div class="grid-2">
    <div class="panel" style="border-left: 4px solid var(--bull);">
      <h3>🟢 大盘 沪指 3842.19 +0.31%</h3>
      <p><b>关键位印证</b>:9/30 收 <b>3842.19</b>(涨 0.31%),从 9/28 低点 3823.62 反弹 +0.49%,验证博主 9/29 09:45 「<b>3800 关卡多方组织小型抵抗</b>」的判断(突破 3800 上方 +42 点)。</p>
      <ul>
        <li>距博主 9/29 多方抵抗关卡 <b>3800</b> +42 点</li>
        <li>距 8/4 关键支撑 <b>3856</b> 仅 14 点</li>
        <li>距 60D 低 <b>3764</b> 78 点</li>
        <li>距 60D 高 <b>4036</b> 194 点</li>
      </ul>
      <p><b>结论</b>:博主 9/29 「3800 关卡多方组织小型抵抗」判断得到验证,<b>3800 是关键多方分水岭</b>。10/9 节后开盘能否延续反弹突破 60D 高 4036 是关键。</p>
    </div>

    <div class="panel" style="border-left: 4px solid var(--bear);">
      <h3>🔴 创业板 3635.28 -0.23% 创 60D/120D 新低</h3>
      <p><b>关键位印证</b>:9/30 收 <b>3135.28</b>(跌 0.23%),<b>创 60D/120D 新低</b>(前期 60D 低 3139.82 在 9/28 已破,3135.28 是新低),距博主 8/4 「A 杀位」3160 已跌穿 24.72 点。</p>
      <ul>
        <li>距博主 8/4 「A 杀位」<b>3160</b> 跌穿 24.72 点</li>
        <li>距博主 8/4 「试破位」<b>3286</b> 跌穿 150.72 点</li>
        <li>距博主 8/4 「反抽区」<b>3370</b> 跌穿 234.72 点</li>
        <li>距博主 8/4 「B 反位」<b>3486</b> 跌穿 350.72 点</li>
      </ul>
      <p><b>结论</b>:博主 8/4 「A 杀位」3160 已跌穿,<b>创业板 C5 杀一调整目标 3050 岌岌可危</b>(距 3135 仅 85 点)。<b>10/9 节后开盘是否止跌是关键</b>。</p>
    </div>
  </div>

  <h2>📊 K 线图(关键位居左虚线标注 · 9/30 收盘基准)</h2>

  <h3>📈 大盘 沪指(博主关键位)</h3>
  <img class="chart" src="charts/000001_SH_20261001.png" alt="上证指数 K线图" />
  <div class="chart-caption">关键位(11 个):60D低 3764 / 多方抵抗 3800 / 9/30收 3842.19 / 8/4支撑 3856 / B浪位 3886 / 整数 3900 / 8/26上沿 3926 / 8/29周高 3996 / 60D高 4036 / 120D高 4242 / 年大顶 4258</div>

  <h3>📉 创业板指(博主关键位)</h3>
  <img class="chart" src="charts/399006_SZ_20261001.png" alt="创业板指 K线图" />
  <div class="chart-caption">关键位(10 个):9/30收 3135.28 / A杀位 3160 / 支撑 3220 / 试破位 3286 / 反抽区 3370 / B反位 3486 / 目标位 3590 / 8/15前顶 3686 / 60D高 4018 / 120D高 4371</div>

  <h2>💼 3 大板块 + 6 支个股(基于博主 9/29-10/1 实际提及)</h2>

  <div class="panel" style="border-left: 4px solid var(--bull);">
    <h3>{SECTOR_1_NAME}</h3>
    <p>{SECTOR_1_SUMMARY}</p>

    <div class="stock-card neutral">
      <h4>🟡 兆易创新 (603986.SH)</h4>
      <div class="logic">{STOCK_1_LOGIC}</div>
      <div class="key">关键位:{STOCK_1_KEY}</div>
    </div>

    <div class="stock-card neutral">
      <h4>🟡 澜起科技 (688008.SH)</h4>
      <div class="logic">{STOCK_2_LOGIC}</div>
      <div class="key">关键位:{STOCK_2_KEY}</div>
    </div>
  </div>

  <div class="panel" style="border-left: 4px solid var(--bull);">
    <h3>{SECTOR_2_NAME}</h3>
    <p>{SECTOR_2_SUMMARY}</p>

    <div class="stock-card bull">
      <h4>🟢 工商银行 (601398.SH)</h4>
      <div class="logic">{STOCK_3_LOGIC}</div>
      <div class="key">关键位:{STOCK_3_KEY}</div>
    </div>

    <div class="stock-card bull">
      <h4>🟢 农业银行 (601288.SH)</h4>
      <div class="logic">{STOCK_4_LOGIC}</div>
      <div class="key">关键位:{STOCK_4_KEY}</div>
    </div>
  </div>

  <div class="panel" style="border-left: 4px solid var(--bull);">
    <h3>{SECTOR_3_NAME}</h3>
    <p>{SECTOR_3_SUMMARY}</p>

    <div class="stock-card bull">
      <h4>🟢 恒瑞医药 (600276.SH)</h4>
      <div class="logic">{STOCK_5_LOGIC}</div>
      <div class="key">关键位:{STOCK_5_KEY}</div>
    </div>

    <div class="stock-card bull">
      <h4>🟢 百济神州 (688235.SH)</h4>
      <div class="logic">{STOCK_6_LOGIC}</div>
      <div class="key">关键位:{STOCK_6_KEY}</div>
    </div>
  </div>

  <h2>📉 6 个股 K 线图(关键位居左虚线标注)</h2>

  <h3>💾 存储芯片 — 兆易创新(博主 10/1 美光财报隐含新关注)</h3>
  <img class="chart" src="charts/603986_SH_20261001.png" alt="兆易创新 K线图" />
  <div class="chart-caption">博主美光财报 → A 股存储芯片映射最直接品种 · NOR Flash 全球第三 + DRAM 利基型龙头 · 节后中段是美光 → 兆易逻辑主线验证关键<br/>关键位:60D低 340.74 / 支撑 340 / 9/30收 353.90 / 压力 600 / 60D高 663.49</div>

  <h3>💾 存储芯片 — 澜起科技(DDR5 内存接口芯片全球龙头)</h3>
  <img class="chart" src="charts/688008_SH_20261001.png" alt="澜起科技 K线图" />
  <div class="chart-caption">DDR5 内存接口芯片全球龙头(市占率 40%+) · AI 服务器 HBM/DDR5 关键供应商 · 美光超级景气 → 澜起接口芯片业务直接利好<br/>关键位:60D低 183.60 / 支撑 195 / 9/30收 202.31 / 压力 240 / 60D高 285.80</div>

  <h3>🏦 银行/防御 — 工商银行(博主 9/29-9/30 提肩带)</h3>
  <img class="chart" src="charts/601398_SH_20261001.png" alt="工商银行 K线图" />
  <div class="chart-caption">博主 9/29 「四大行一直在提肩带」+ 9/30 「老登股局部上涨」双重直接对标的冠军品种 · 9/30 银行板块涨幅第一 · 股息率 ~5.5% + 央行降息利好息差<br/>关键位:60D低 7.27 / 9/30收 8.28 / 60D高/压 8.30</div>

  <h3>🏦 银行/防御 — 农业银行</h3>
  <img class="chart" src="charts/601288_SH_20261001.png" alt="农业银行 K线图" />
  <div class="chart-caption">博主 9/30 14:08 「四大行局部上涨」验证标的 · 9/30 涨 0.43% 收 6.97 · 国有四大行之一 · 高股息 (~5%) 防御主线 · 与工行/建行形成银行底仓组合<br/>关键位:60D低 6.11 / 支撑 6.50 / 9/30收 6.97 / 压力 7.11 / 60D高 7.11</div>

  <h3>💊 创新药 — 恒瑞医药(博主 9/30 14:13 生物制品黑马)</h3>
  <img class="chart" src="charts/600276_SH_20261001.png" alt="恒瑞医药 K线图" />
  <div class="chart-caption">博主 9/30 14:13 「生物制品黑马」核心标的 · 9/30 涨 3.46% 收 47.20 黑马验证 · PD-1/ADC 双轮驱动 · 9 月 BD 交易 28.5 亿美元验证出海逻辑<br/>关键位:60D低 42.67 / 支撑 45 / 9/30收 47.20 / 压力 50 / 60D高 58</div>

  <h3>💊 创新药出海 — 百济神州(博主 9/30 医药局部上涨)</h3>
  <img class="chart" src="charts/688235_SH_20261001.png" alt="百济神州 K线图" />
  <div class="chart-caption">博主 9/30 14:08 「医药局部上涨」验证标的 · 9/30 涨 1.91% 收 264.41 · 创新药出海龙头(百泽安/百悦泽海外放量) · 海外营收占比 58% · 可预期最高的中大型品种<br/>关键位:60D低 247.30 / 支撑 255 / 9/30收 264.41 / 压力 280 / 60D高 300.30</div>

  <h2>🚨 风险点 & 关注点</h2>
  <ul>
{RISKS_LIST}
  </ul>

  <h2>📌 操作建议(基于博主 9/29-10/1 观点)</h2>

  <h3>📌 板块策略</h3>
  <ul>
    <li><b>🟢 重点:存储芯片</b> — 博主 10/1 16:48 美光超级财报(+380%/+1077%)标志新关注,HBM/DDR5 进入 AI 算力驱动超级景气周期;兆易(603986)/ 澜起(688008) 是 A 股映射龙头;9/30 节前集体回调 -3.12% ~ -4.84% 但美光财报暗示节后主线回归</li>
    <li><b>🟢 防御底仓:银行/四大行</b> — 博主 9/29 「四大行一直在提肩带」+ 9/30 「老登股局部上涨」+ 央行 PSL -25bp 利好息差,工行(601398)/ 农行(601288) 是防御底仓</li>
    <li><b>🟢 成长:创新药</b> — 博主 9/30 14:13 「生物制品黑马」+ 14:08 「医药局部上涨」,恒瑞(600276)/ 百济(688235) 出海逻辑持续催化</li>
  </ul>

  <h3>📌 6 支个股监控</h3>
  <table>
    <thead><tr><th>标的</th><th>板块</th><th>支撑</th><th>9/30 收</th><th>压力</th><th>60D高</th><th>监控动作</th></tr></thead>
    <tbody>
      <tr><td>兆易创新 603986</td><td>存储芯片</td><td>340 / 340.74</td><td><b style="color:var(--bear)">353.90 (-3.72%)</b></td><td>600</td><td>663.49</td><td><b>博主美光财报 → A 股映射</b> · 9/30 节前资金利获利了结 · 60D低 340.74 接近,中期买点</td></tr>
      <tr><td>澜起科技 688008</td><td>存储芯片</td><td>195 / 183.60</td><td><b style="color:var(--bear)">202.31 (-4.84%)</b></td><td>240</td><td>285.80</td><td><b>美光超级景气 → DDR5 接口芯片</b> · 9/30 跌幅最大 · 60D低 183.60 接近</td></tr>
      <tr><td>工商银行 601398</td><td>银行</td><td>8.20 / 7.27</td><td><b style="color:var(--bull)">8.28 (+1.47%)</b></td><td>8.30</td><td>8.30</td><td><b>博主「四大行提肩带」验证</b> · 9/30 银行涨幅第一 · 60D高 8.30 一步之遥,持有</td></tr>
      <tr><td>农业银行 601288</td><td>银行</td><td>6.80 / 6.11</td><td><b style="color:var(--bull)">6.97 (+0.43%)</b></td><td>7.11</td><td>7.11</td><td><b>博主「老登股局部上涨」</b> · 与工行同节奏,股息率 ~5%,防御底仓</td></tr>
      <tr><td>恒瑞医药 600276</td><td>创新药</td><td>45 / 42.67</td><td><b style="color:var(--bull)">47.20 (+3.46%)</b></td><td>50 / 58</td><td>58.00</td><td><b>博主 9/30 14:13 「生物制品黑马」</b> · 9 月 BD 28.5 亿美元 · 60D高 58 待突破</td></tr>
      <tr><td>百济神州 688235</td><td>创新药</td><td>255 / 247.30</td><td><b style="color:var(--bull)">264.41 (+1.91%)</b></td><td>280</td><td>300.30</td><td><b>博主 9/30 14:08 「医药局部上涨」</b> · 出海龙头 · 海外营收占比 58%</td></tr>
    </tbody>
  </table>

  <h3>📌 博主 10/1 美光财报信号追踪</h3>
  <ul>
    <li><b>博主 10/1 16:48 美光财报</b> — 营收 +380% / 净利 +1077.79% — 是 10/1 唯一行业速报</li>
    <li><b>A 股映射逻辑</b> — 美光(HBM/DDR5) → 兆易创新(NOR+DRAM)/ 澜起科技(DDR5 接口) 是最直接受益品种</li>
    <li><b>9/30 节前表现</b> — 兆易 -3.72% / 澜起 -4.84% / 北京君正 -4.05% / 江波龙 -3.12% 集体回调</li>
    <li><b>10/9 节后开盘是关键</b> — 验证博主美光财报 → A 股映射主线是否成立</li>
  </ul>

  <div class="footer">
    <p>本报告基于 <b>wu2198 (UID 1216826604)</b> 公开微博观点整理,所有判断仅反映博主立场,不构成投资建议。<br/>
    数据源:<b>weibo-watcher skill</b>(微博抓取与分类)+ <b>tushare</b>(日线行情 + K 线 + MACD + 成交量)。<br/>
    关键位标注 · 60D 高/低 · 120D 高/低 · 博主历史关键位综合 · 2026-10-01 21:00 自动生成。</p>
    <p><a href="index.html">← 返回首页</a></p>
  </div>

</div>
</body>
</html>
"""

def render_posts_table():
    rows = []
    for i, p in enumerate(POSTS, 1):
        emoji = p["emoji"]
        text = p["text"].replace("<", "&lt;").replace(">", "&gt;")
        score = f"{p['rep']}/{p['com']}/{p['like']}"
        rows.append(
            f"      <tr>\n"
            f"        <td>{i}</td>\n"
            f"        <td>{p['time']}</td>\n"
            f"        <td class=\"emoji\">{emoji}</td>\n"
            f"        <td><span class=\"tag tag-{('bull' if p['dir']=='多' else 'bear' if p['dir']=='空' else 'neutral' if p['dir']=='中性' else 'none')}\">{p['dir']}</span> · {p['signal']}</td>\n"
            f"        <td style=\"font-size:12px\">{p['topic']}</td>\n"
            f"        <td class=\"text\">{text}</td>\n"
            f"        <td class=\"score\">R:{p['rep']} C:{p['com']} L:{p['like']}</td>\n"
            f"        <td class=\"score\">{p['score']}</td>\n"
            f"      </tr>"
        )
    return "\n".join(rows)

def render_risks():
    items = []
    for emoji, text in RISKS:
        items.append(f"    <li><b>{emoji}</b> {text}</li>")
    return "\n".join(items)

if __name__ == "__main__":
    s1, s2, s3 = SECTORS
    stk1, stk2 = s1["stocks"]
    stk3, stk4 = s2["stocks"]
    stk5, stk6 = s3["stocks"]

    out = HTML.format(
        TODAY=TODAY, SH_INDEX=SH_INDEX, CYB_INDEX=CYB_INDEX, LAST_TRADING=LAST_TRADING,
        POSTS_TABLE=render_posts_table(),
        RISKS_LIST=render_risks(),
        SECTOR_1_NAME=s1["name"], SECTOR_1_SUMMARY=s1["summary"],
        SECTOR_2_NAME=s2["name"], SECTOR_2_SUMMARY=s2["summary"],
        SECTOR_3_NAME=s3["name"], SECTOR_3_SUMMARY=s3["summary"],
        STOCK_1_LOGIC=stk1["logic"], STOCK_1_KEY=stk1["key"],
        STOCK_2_LOGIC=stk2["logic"], STOCK_2_KEY=stk2["key"],
        STOCK_3_LOGIC=stk3["logic"], STOCK_3_KEY=stk3["key"],
        STOCK_4_LOGIC=stk4["logic"], STOCK_4_KEY=stk4["key"],
        STOCK_5_LOGIC=stk5["logic"], STOCK_5_KEY=stk5["key"],
        STOCK_6_LOGIC=stk6["logic"], STOCK_6_KEY=stk6["key"],
    )
    OUT_HTML.write_text(out, encoding="utf-8")
    print(f"[html] saved: {OUT_HTML}  ({len(out.encode('utf-8'))} bytes)")