"""Pandas calculations; shared semantics, independent aggregation."""
import io
import pandas as pd
from stats_common import execute,categorical_result,key_sort,safe

def loader(args):
    df=pd.read_csv(args.input,dtype=str,keep_default_na=False,na_filter=False,encoding=args.encoding,on_bad_lines='error')
    b=io.StringIO();df.info(buf=b)
    return list(df.columns),df.to_dict(orient='list'),f'pandas {pd.__version__}\nshape={df.shape}\n{df.dtypes}\n{b.getvalue()}'

def summarize(data,kinds,ddof,return_frame=False):
    frame=pd.DataFrame({c:pd.Series(v,dtype='float64' if kinds[c]=='numeric' else 'object') for c,v in data.items()})
    n=len(frame);out={}
    for c in frame.columns:
        s=frame[c];present=s.dropna()
        if kinds[c]=='numeric':
            desc=s.describe();count=int(desc['count'])
            out[c]={'count':count,'mean':safe(desc['mean']),'min':safe(desc['min']),'max':safe(desc['max']),
                    'std':safe(s.std(ddof=ddof)),'median':safe(s.median()) if count else None,'missing':n-count,'missing_percent':100*(n-count)/n if n else None}
        else:
            desc=s.describe();counts=present.value_counts(dropna=True)
            out[c]=categorical_result(counts.items(),n)
            assert int(present.nunique(dropna=True))==out[c]['unique']
    if return_frame:
        # Both numeric and nonnumeric describe reports are actually executed.
        frame.describe(include='all')
    return out,frame if return_frame else None

def groups(data,frame,keys):
    gb=frame.groupby(keys[0] if len(keys)==1 else keys,dropna=False,sort=False)
    indices=gb.indices
    normalized=[]
    for key,idx in indices.items():
        key=(key,) if len(keys)==1 else key
        normalized.append((tuple(None if pd.isna(x) else x for x in key),idx.tolist()))
    yield from sorted(normalized,key=lambda x:key_sort(x[0]))
if __name__=='__main__':execute('pandas',loader,summarize,groups)
