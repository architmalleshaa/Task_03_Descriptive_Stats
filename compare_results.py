"""Compare every output statistic and group with explicit numeric tolerance."""
import argparse,json,math
from itertools import zip_longest
from pathlib import Path
from stats_common import open_text

def compare(a,b,path='root'):
    if isinstance(a,dict) and isinstance(b,dict):
        assert a.keys()==b.keys(),(path,'keys differ')
        for k in a:compare(a[k],b[k],path+'.'+k)
    elif isinstance(a,list) and isinstance(b,list):
        assert len(a)==len(b),(path,'length differs')
        for i,(x,y) in enumerate(zip(a,b)):compare(x,y,f'{path}[{i}]')
    elif isinstance(a,(int,float)) and isinstance(b,(int,float)):
        assert math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-9),(path,a,b)
    else:assert a==b,(path,a,b)

def main():
    p=argparse.ArgumentParser();p.add_argument('directories',nargs='+',type=Path);args=p.parse_args();base=args.directories[0]
    counts=[]
    for other in args.directories[1:]:
        compare(json.loads((base/'summary.json').read_text()),json.loads((other/'summary.json').read_text()))
        left=json.loads((base/'run.json').read_text())['groupings'];right=json.loads((other/'run.json').read_text())['groupings'];compare(left,right)
        n=0
        for group in left:
            with open_text(base/group['file'],'rt') as a,open_text(other/group['file'],'rt') as b:
                for i,(x,y) in enumerate(zip_longest(a,b),1):
                    assert x is not None and y is not None,'Different group record counts'
                    compare(json.loads(x),json.loads(y),f"{group['file']}:{i}");n+=i>1
        counts.append({'reference':str(base),'compared':str(other),'group_records':n,'result':'PASS'})
    print(json.dumps(counts,indent=2))
if __name__=='__main__':main()
