import argparse,ast,csv,json,math,statistics
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--task1',type=Path,required=True);p.add_argument('--task2',type=Path,required=True);p.add_argument('--output',type=Path,default=Path('spend_validation.json'));a=p.parse_args()
csv.field_size_limit(100000000);ranges={}
with a.task1.open(newline='') as f:
 for row in csv.DictReader(f):
  value=ast.literal_eval(row['spend']);ranges[row['ad_id']]=(float(value['lower_bound']),float(value['upper_bound']))
matches=within=0;usd=[];seen=set()
with a.task2.open(newline='') as f:
 for row in csv.DictReader(f):
  seen.add(row['ad_id']);value=float(row['estimated_spend']);lo,hi=ranges[row['ad_id']];matches+=value==math.floor((lo+hi)/2);within+=lo<=value<=hi
  if row['currency']=='USD':usd.append(value)
assert seen==set(ranges),'Ad universes differ'
result={'matched_ad_ids':len(seen),'estimated_spend_equal_floor_midpoint':matches,'estimated_spend_within_interval':within,'usd_spend_mean':statistics.mean(usd),'usd_spend_median':statistics.median(usd),'usd_spend_std':statistics.stdev(usd)}
a.output.write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
