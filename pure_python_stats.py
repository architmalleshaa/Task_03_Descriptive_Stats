"""Pure standard-library analysis. No Pandas, NumPy, or third-party packages."""
import csv,math
from collections import Counter,defaultdict
from stats_common import execute,categorical_result,key_sort

def compute_numeric_stats(values,ddof=1):
    v=[x for x in values if x is not None];n=len(v);ordered=sorted(v)
    mean=math.fsum(v)/n if n else None
    median=(ordered[(n-1)//2]+ordered[n//2])/2 if n else None
    sd=math.sqrt(math.fsum((x-mean)**2 for x in v)/(n-ddof)) if n>ddof else None
    return {'count':n,'mean':mean,'min':min(v) if n else None,'max':max(v) if n else None,'std':sd,'median':median}

def loader(args):
    csv.field_size_limit(100_000_000)
    with args.input.open(newline='',encoding=args.encoding,errors='strict') as f:
        r=csv.reader(f);columns=next(r,[])
        if not columns:raise ValueError('CSV requires a header')
        if len(columns)!=len(set(columns)):raise ValueError('Duplicate column names')
        raw={c:[] for c in columns}
        for i,row in enumerate(r,2):
            if len(row)!=len(columns):raise ValueError(f'Row {i} has {len(row)} cells, expected {len(columns)}')
            for c,v in zip(columns,row):raw[c].append(v)
    return columns,raw,f'csv.reader with strict {args.encoding} decoding; {len(raw[columns[0]])} rows; {len(columns)} columns'

def summarize(data,kinds,ddof,return_frame=False):
    n=len(next(iter(data.values()),[]));out={}
    for c,v in data.items():
        if kinds[c]=='numeric':
            s=compute_numeric_stats(v,ddof);s.update(missing=n-s['count'],missing_percent=100*(n-s['count'])/n if n else None)
        else:s=categorical_result(Counter(x for x in v if x is not None).items(),n)
        out[c]=s
    return out,None

def groups(data,frame,keys):
    buckets=defaultdict(list)
    for i,key in enumerate(zip(*(data[k] for k in keys))):buckets[key].append(i)
    for key in sorted(buckets,key=key_sort):yield key,buckets[key]
if __name__=='__main__':execute('pure_python',loader,summarize,groups)
