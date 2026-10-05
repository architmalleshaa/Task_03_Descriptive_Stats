"""Compare all actual shared columns, preserving non-null denominators."""
import argparse,json
from pathlib import Path

def create(paths,output):
 summaries={name:json.loads(path.read_text()) for name,path in paths.items()}
 common=sorted(set.intersection(*(set(s['columns']) for s in summaries.values())))
 result={c:{name:s['columns'][c] for name,s in summaries.items()} for c in common}
 output.mkdir(parents=True,exist_ok=True);(output/'shared_column_statistics.json').write_text(json.dumps(result,indent=2))
 lines=['# Shared column comparison','','Means below use non-null observations. All shared columns in these supplied files are binary indicators; multiply their means by 100 to obtain the percentage labeled positive. They are recorded annotations, not verified political facts.','','| Column | Ads mean | Facebook posts mean | Twitter posts mean | Valid n ads / FB / X | Missing ads / FB / X |','|---|---:|---:|---:|---|---|']
 for c,values in result.items():
  ordered=[values[n] for n in paths]
  means=[f"{v['mean']:.6f}" if v.get('mean') is not None else 'not numeric' for v in ordered]
  lines.append('| '+c+' | '+' | '.join(means)+' | '+' / '.join(str(v['count']) for v in ordered)+' | '+' / '.join(str(v['missing']) for v in ordered)+' |')
 lines+=['','The JSON companion includes count, minimum, maximum, median, sample standard deviation, missing count and missing percentage for every shared column in each file. No engagement or account-identifier column is literally common to all three sources.']
 (output/'SHARED_COLUMNS.md').write_text('\n'.join(lines)+'\n');return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--ads',type=Path,required=True);p.add_argument('--facebook',type=Path,required=True);p.add_argument('--twitter',type=Path,required=True);p.add_argument('--output',type=Path,default=Path('comparison'));a=p.parse_args();create(dict(ads=a.ads,facebook=a.facebook,twitter=a.twitter),a.output)
