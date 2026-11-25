import json, os, importlib.util
spec = importlib.util.spec_from_file_location("wc", "/Users/maoling/.minimax/skills/wu2198/scripts/wu_collect.py")
wc = importlib.util.module_from_spec(spec); spec.loader.exec_module(wc)
import tushare as ts
pro = ts.pro_api(os.environ["TUSHARE_TOKEN"])
P="/Users/maoling/workspace/mnote.github.io/charts/_wu_20261124.json"
d=json.load(open(P))
extra={"688256.SH":"寒武纪","603662.SH":"柯力传感","688037.SH":"芯源微",
       "300476.SZ":"胜宏科技","688836.SH":"宇树科技","000636.SZ":"风华高科",
       "301413.SZ":"安培龙","603228.SH":"景旺电子"}
for c,n in extra.items():
    daily=wc.norm(pro.daily(ts_code=c,start_date="20250101",end_date="20261124"))
    adj=wc.norm(pro.adj_factor(ts_code=c,start_date="20250101",end_date="20261124"))
    rows=wc.fwd_adj(daily,adj)
    d["rows"][c]=rows
    s=wc.summarize(rows); s["name"]=n
    d["stocks"][c]=s
    print(c,n,s["close"],f'{s["pct_chg"]:+.2f}%',"MA20",s["ma20"],"量比",s["vol_ratio5"],"额",s["amount_yi"])
json.dump(d,open(P,"w"),ensure_ascii=False)
print("rows now", len(d["rows"]))
