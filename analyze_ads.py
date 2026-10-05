"""Domain interpretation of only the supplied election CSV files."""
import csv,ast,collections,hashlib,json,math
from pathlib import Path
from functools import lru_cache
csv.field_size_limit(100000000)
@lru_cache(maxsize=10000)
def literal(s):
 try:return ast.literal_eval(s)
 except (ValueError,SyntaxError,TypeError):return None

def analyze(path):
 groups=collections.defaultdict(lambda:{'rows':0,'lower':0,'upper':0,'estimate':0,'open_upper':0})
 mentions=collections.Counter();months=collections.Counter();regions=collections.Counter();currencies=collections.Counter();dates=[];n=bad=0
 adids=set();currency_missing=0;spendmissing=0;bounds_tot={'lower':0,'upper':0,'open_upper':0};esttotal=0
 with path.open(newline='') as f:
  reader=csv.DictReader(f)
  for r in reader:
   n+=1;adids.add(r['ad_id']);currency=r['currency'];currencies[currency]+=1
   date=r.get('ad_creation_time','');dates.append(date);months[date[:7]]+=1
   v=literal(r.get('illuminating_mentions',''))
   if isinstance(v,list):mentions.update(set(v))
   else:bad+=1
   name=r.get('bylines') or '[missing byline]';g=groups[(currency,name)];g['rows']+=1
   if 'spend' in r:
    s=literal(r['spend'])
    if not isinstance(s,dict):spendmissing+=1;continue
    lo=float(s['lower_bound']) if s.get('lower_bound') is not None else None
    hi=float(s['upper_bound']) if s.get('upper_bound') is not None else None
    if currency=='USD':
     bounds_tot['lower']+=lo or 0;bounds_tot['upper']+=hi or 0;bounds_tot['open_upper']+=hi is None
    g['lower']+=lo or 0;g['upper']+=hi or 0;g['open_upper']+=hi is None
   else:
    try:sp=float(r['estimated_spend'])
    except ValueError:spendmissing+=1;continue
    g['estimate']+=sp
    if currency=='USD':esttotal+=sp
    regions_obj=literal(r.get('delivery_by_region',''))
    if isinstance(regions_obj,dict) and currency=='USD':
     for name,value in regions_obj.items():
      if isinstance(value,dict):regions[name]+=value.get('spend',0)
 result={'rows':n,'unique_ad_ids':len(adids),'currencies':dict(currencies),'creation_min':min(dates),'creation_max':max(dates),
         'mentions_per_row':mentions.most_common(),'unparsed_mentions':bad,'spend_missing_or_malformed':spendmissing,
         'ad_creation_month_counts':sorted(months.items()),'usd_range_sum':bounds_tot,'usd_estimated_spend_total':esttotal,
         'top_usd_bylines':sorted([dict(byline=k[1],**v) for k,v in groups.items() if k[0]=='USD'],key=lambda d:-(d['estimate'] or d['lower']))[:15],
         'usd_top_regions':regions.most_common(15),'usd_region_allocated_total':sum(regions.values())}
 return result,adids

if __name__=="__main__":
 import argparse
 p=argparse.ArgumentParser();p.add_argument("input",type=Path);p.add_argument("--output",type=Path,default=Path("ad_findings.json"));a=p.parse_args()
 result,_=analyze(a.input);a.output.write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
