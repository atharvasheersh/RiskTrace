"""Small explicit source selectors for the manuscript evidence map (no eval)."""
import json
import pandas as pd
import yaml
from risktrace.core import ROOT


def select(spec):
    if spec['kind'] in ['json','yaml']:
        source=ROOT/spec['source']
        obj=json.loads(source.read_text()) if spec['kind']=='json' else yaml.safe_load(source.read_text())
        for key in spec.get('path',[]):obj=obj[key]
        value=len(obj) if spec.get('op')=='len' else obj
    elif spec['kind']=='json_glob':
        value=sum(len(json.loads(p.read_text())) for p in ROOT.glob(spec['source']))
    else:
        frame=pd.read_csv(ROOT/spec['source'])
        for field,op,target in spec.get('filters',[]):
            frame=frame.loc[frame[field].eq(target) if op=='eq' else ~frame[field].eq(target)]
        op=spec.get('op','first')
        if op=='count':value=len(frame)
        else:
            s=frame[spec['field']]
            if op=='first':value=s.iloc[0]
            elif op=='max':value=s.max()
            elif op=='min':value=s.min()
            elif op=='nunique':value=s.nunique()
            elif op=='sum':value=s.sum()
            else:raise ValueError(op)
    if 'scale' in spec:value=value*spec['scale']
    return value
