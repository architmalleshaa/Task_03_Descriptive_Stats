"""Shared input semantics and output format; no third-party imports or statistics."""
from __future__ import annotations
import argparse, csv, gzip, hashlib, json, math, re, sys
from datetime import datetime
from functools import lru_cache
from pathlib import Path

MISSING = {'', 'na', 'n/a', 'nan', 'null', 'none', '-'}
NUMBER = re.compile(r'^[+-]?(?:(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$')

def clean(value):
    if value is None: return None
    s = str(value).strip()
    return None if s.casefold() in MISSING else s

@lru_cache(maxsize=50000)
def number(s):
    if s is None: return None
    t=s; neg=t.startswith('(') and t.endswith(')')
    if neg: t=t[1:-1]
    if t.startswith('$'): t=t[1:]
    pct=t.endswith('%')
    if pct: t=t[:-1]
    if not NUMBER.fullmatch(t): return None
    try: value=float(t.replace(',','')) * (-1 if neg else 1) / (100 if pct else 1)
    except (OverflowError,ValueError): return None
    return value if math.isfinite(value) else None

def identifier(name):
    n=name.strip().lower().replace(' ','_')
    return n in {'id','url','quoteid','inreplytoid'} or n.endswith('_id')

def infer(name, values, numeric=(), categorical=()):
    present=[v for v in values if v is not None]
    if name in categorical: return 'categorical'
    if name in numeric:
        bad=[v for v in present if number(v) is None]
        if bad: raise ValueError(f'{name}: forced numeric column contains nonnumeric values: {bad[:3]}')
        return 'numeric'
    if not present: return 'empty'
    if identifier(name): return 'identifier'
    if all(number(v) is not None for v in present): return 'numeric'
    if all(v.lower() in {'true','false'} for v in present): return 'boolean'
    # Only recognize unambiguous ISO dates/timestamps. Preserve the original strings.
    if all(re.fullmatch(r'\d{4}-\d{2}-\d{2}(?:[T ].+)?',v) for v in present):
        try:
            for v in set(present): datetime.fromisoformat(v.replace('Z','+00:00'))
            return 'datetime'
        except ValueError: pass
    if all(v.startswith(('[','{')) for v in present): return 'structured_text'
    return 'categorical'

def prepare(columns, raw, args):
    values={c:[clean(v) for v in raw[c]] for c in columns}
    kinds={c:infer(c,values[c],args.numeric,args.categorical) for c in columns}
    profile={c:{'type':kinds[c], 'parseable_numeric_values':sum(number(v) is not None for v in values[c] if v is not None) if kinds[c] in {'numeric','categorical'} else None} for c in columns}
    typed={c:[number(v) if kinds[c]=='numeric' else v for v in values[c]] for c in columns}
    return typed,kinds,profile

def safe(v):
    if hasattr(v,'item'): v=v.item()
    if isinstance(v,float) and not math.isfinite(v): return None
    return v

def categorical_result(counts,nrows):
    items=sorted(((str(k),int(v)) for k,v in counts if k is not None),key=lambda x:(-x[1],x[0]))
    n=sum(v for _,v in items)
    return {'count':n,'missing':nrows-n,'missing_percent':100*(nrows-n)/nrows if nrows else None,
            'unique':len(items),'mode':items[0][0] if items else None,'mode_frequency':items[0][1] if items else 0,
            'top5':[[k,v] for k,v in items[:5]]}

def singleton_record(key, row):
    # Lossless compact statistics for one-row groups, not an omitted computation.
    # Numeric x -> count=1, mean=min=max=median=x, std=null. Missing -> count=0.
    # Categorical x -> count=unique=mode_frequency=1, mode=x, top5=[[x,1]].
    return {'key':list(key),'rows':1,'encoding':'singleton_statistics_v1','values':{c:safe(v) for c,v in row.items()}}

def open_text(path,mode='wt'):
    return gzip.open(path,mode,encoding='utf-8') if str(path).endswith('.gz') else open(path,mode,encoding='utf-8')

def dump(obj,file): file.write(json.dumps(obj,ensure_ascii=False,allow_nan=False,separators=(',',':'))+'\n')
def key_sort(key): return tuple((v is not None,'' if v is None else str(v)) for v in key)

def parser():
    p=argparse.ArgumentParser(description='Reproducible descriptive statistics with explicit missing/type semantics.')
    p.add_argument('input',type=Path);p.add_argument('--output',type=Path,default=Path('results'))
    p.add_argument('--group',action='append',default=[],help='Comma-separated group keys; repeat for multiple groupings')
    p.add_argument('--numeric',action='append',default=[]);p.add_argument('--categorical',action='append',default=[])
    p.add_argument('--encoding',default='utf-8-sig');p.add_argument('--ddof',type=int,choices=[0,1],default=1)
    return p

def execute(engine, loader, summarize, groups):
    import time
    args=parser().parse_args();start=time.perf_counter()
    args.output.mkdir(parents=True,exist_ok=True)
    columns,raw,native_info=loader(args)
    if len(columns)!=len(set(columns)):raise ValueError('Duplicate column names are not supported')
    for c in args.numeric+args.categorical:
        if c not in columns:raise ValueError(f'Unknown override column: {c}')
    typed,kinds,profile=prepare(columns,raw,args);del raw
    n=len(typed[columns[0]]) if columns else 0
    base,frame=summarize(typed,kinds,args.ddof,return_frame=True)
    digest=hashlib.sha256()
    with args.input.open('rb') as source:
        for chunk in iter(lambda:source.read(1024*1024),b''):digest.update(chunk)
    report={'file':args.input.name,'source_sha256':digest.hexdigest(),'rows':n,'column_count':len(columns),
            'ddof':args.ddof,'types':kinds,'columns':base,'inference_profile':profile}
    (args.output/'summary.json').write_text(json.dumps(report,indent=2,allow_nan=False),encoding='utf-8')
    (args.output/'native_structure.txt').write_text(native_info,encoding='utf-8')
    print(f'{engine}: {args.input.name}: {n:,} rows x {len(columns)} columns; ddof={args.ddof}')
    for c,s in base.items():
        details=f"mean={s['mean']} median={s['median']} std={s['std']}" if kinds[c]=='numeric' else f"unique={s['unique']} mode={str(s['mode'])[:65]!r}"
        print(f"  {c}: {kinds[c]}, count={s['count']}, missing={s['missing']} | {details}")
    manifests=[]
    for spec in args.group:
        keys=spec.split(',')
        if any(k not in kinds for k in keys):raise ValueError(f'Unknown grouping: {spec}')
        group_file='groups_'+str(len(manifests)+1)+'.jsonl.gz'; total=singletons=0
        with open_text(args.output/group_file) as f:
            dump({'group_keys':keys,'types':kinds,'ddof':args.ddof,'singleton_encoding':'See FORMAT.md'},f)
            for key,indices in groups(typed,frame,keys):
                total+=1
                if len(indices)==1:
                    singletons+=1;record=singleton_record(key,{c:typed[c][indices[0]] for c in columns})
                else:
                    part={c:[typed[c][i] for i in indices] for c in columns}
                    stats,_=summarize(part,kinds,args.ddof)
                    record={'key':list(key),'rows':len(indices),'columns':stats}
                dump(record,f)
        manifests.append({'keys':keys,'groups':total,'singleton_groups':singletons,'file':group_file})
        print(f'  Grouping {spec}: {total:,} groups ({singletons:,} singleton groups)',flush=True)
    result={'engine':engine,'groupings':manifests,'elapsed_seconds':time.perf_counter()-start}
    (args.output/'run.json').write_text(json.dumps(result,indent=2))
    print(f"Elapsed: {result['elapsed_seconds']:.2f} seconds")
