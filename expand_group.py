"""Expand one compact singleton record into the same full statistics schema."""
import argparse,json
from pathlib import Path
from stats_common import open_text

def expand(record,header):
 if record.get('encoding')!='singleton_statistics_v1':return record
 result={'key':record['key'],'rows':1,'columns':{}}
 for c,v in record['values'].items():
  n=int(v is not None);s={'count':n,'missing':1-n,'missing_percent':100*(1-n)}
  if header['types'][c]=='numeric':
   s.update(mean=v,min=v,max=v,median=v,std=0.0 if n and header['ddof']==0 else None)
  else:s.update(unique=n,mode=v,mode_frequency=n,top5=[[v,1]] if n else [])
  result['columns'][c]=s
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('file',type=Path);p.add_argument('--key',required=True,help='JSON array of group key values');args=p.parse_args();key=json.loads(args.key)
 with open_text(args.file,'rt') as f:
  header=json.loads(next(f))
  for line in f:
   record=json.loads(line)
   if record['key']==key:print(json.dumps(expand(record,header),indent=2));break
  else:raise SystemExit('Group key not found')
