"""Polars expressions and group_by; independent of Pandas and pure Python stats."""
import polars as pl
from stats_common import execute,categorical_result,key_sort,safe

def loader(args):
    # Decode strictly, including UTF-8 BOM and explicitly selected legacy encodings.
    with args.input.open(encoding=args.encoding,errors='strict') as f:text=f.read()
    import io
    df=pl.read_csv(io.StringIO(text),infer_schema=False,missing_utf8_is_empty_string=True,truncate_ragged_lines=False)
    return df.columns,df.to_dict(as_series=False),f'polars {pl.__version__}\nshape={df.shape}\nschema={df.schema}\n'

def summarize(data,kinds,ddof,return_frame=False):
    frame=pl.DataFrame({c:pl.Series(c,v,dtype=pl.Float64 if kinds[c]=='numeric' else pl.String) for c,v in data.items()})
    n=frame.height;out={}
    for c in frame.columns:
        s=frame[c]
        if kinds[c]=='numeric':
            vals=frame.select(pl.col(c).count().alias('count'),pl.col(c).mean().alias('mean'),pl.col(c).min().alias('min'),
                  pl.col(c).max().alias('max'),pl.col(c).std(ddof=ddof).alias('std'),pl.col(c).median().alias('median')).row(0,named=True)
            vals={k:safe(v) for k,v in vals.items()};vals.update(missing=n-vals['count'],missing_percent=100*(n-vals['count'])/n if n else None);out[c]=vals
        else:
            present=s.drop_nulls();counts=present.value_counts().rows()
            out[c]=categorical_result(counts,n)
            assert present.n_unique()==out[c]['unique']
    if return_frame:frame.describe()
    return out,frame if return_frame else None

def groups(data,frame,keys):
    grouped=frame.with_row_index('__row_index__').group_by(keys,maintain_order=True).agg(pl.col('__row_index__'))
    rows=[(tuple(row[k] for k in keys),row['__row_index__']) for row in grouped.iter_rows(named=True)]
    yield from sorted(rows,key=lambda x:key_sort(x[0]))
if __name__=='__main__':execute('polars',loader,summarize,groups)
