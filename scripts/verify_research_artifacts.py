"""Reproduce saved inference/metrics without fitting or changing the frozen plan."""
from __future__ import annotations
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from risktrace.analysis import load_analysis, sha
from risktrace.core import ROOT, write_json
from risktrace.holdout import require_frozen_plan, load_checkpoint
from risktrace.metrics import prediction_metrics
from risktrace.predictive import role_frame, predict_tabular
from claim_sources import select


def main():
    args=argparse.ArgumentParser()
    args.add_argument('--recompute-predictions',action='store_true')
    args.add_argument('--require-clean-env',action='store_true')
    options=args.parse_args()
    clean=Path(sys.prefix).resolve()!= (ROOT/'.venv').resolve()
    if options.require_clean_env and not clean:raise ValueError('A separate fresh environment is required')
    plan=require_frozen_plan()
    panel,roles,preprocessing,meta=load_analysis()
    original=json.loads(subprocess.check_output(['git','show','51e3652:data/manifests/analysis_v1.json'],cwd=ROOT))
    # This independent historical check closes the current study's indirect
    # manifest/preprocessor binding; do not rewrite its already opened plan.
    for field in ['sha256','split_keys_sha256','preprocessing_sha256']:
        assert meta[field]==original[field],field
    assert sha((ROOT/'artifacts/analysis/preprocessing.json').read_bytes())==original['preprocessing_sha256']
    evaluation=role_frame(panel,roles,'final','test')
    runs=json.loads((ROOT/'results/final_evaluation/fit_manifest.json').read_text())
    table=pd.read_csv(ROOT/'results/final_evaluation/results.csv').set_index('model')
    recovered={};checkpoints=0
    for run in runs:
        model=load_checkpoint(run);checkpoints+=1
        if options.recompute_predictions:
            if run['family'] in ['prevalence','logistic','xgboost']:
                p=predict_tabular(model,evaluation,preprocessing['final'])
            else:
                from risktrace.temporal import predict_neural,deterministic
                deterministic(run['seed'],2)
                p=predict_neural(model,panel,evaluation,preprocessing['final'])
            recovered.setdefault(run['report_label'],[]).append(p)
    verified=[]
    output=ROOT/'results/reproduction';output.mkdir(exist_ok=True)
    for name,row in table.iterrows():
        saved=pd.read_csv(ROOT/f'results/final_evaluation/{name}_predictions.csv.gz',dtype={'CERT':str})
        assert saved.row_id.tolist()==evaluation.row_id.tolist()
        assert saved.y.tolist()==evaluation.label_12m.astype(int).tolist()
        delta=None
        if options.recompute_predictions:
            p=np.mean(recovered[name],axis=0)
            delta=float(np.max(np.abs(saved.probability-p)))
            assert delta<1e-6,(name,delta)
            saved['probability']=p
        metrics,_=prediction_metrics(saved,float(row.threshold))
        for key,value in metrics.items():
            expected=row[key]
            if value is None:assert pd.isna(expected),(name,key)
            else:assert np.isclose(value,float(expected),rtol=2e-5,atol=1e-8),(name,key,value,expected)
        verified.append(dict(model=name,max_probability_error=delta,**metrics))
    pd.DataFrame(verified).to_csv(output/'principal_table_reproduced.csv',index=False)
    # The generated claim map is itself reconciled to its machine-readable sources.
    content=json.loads((ROOT/'paper/manuscript/content.json').read_text())
    claims=pd.read_csv(ROOT/'docs/claim_evidence_map.csv')
    assert len(claims)>=110 and content['dataset_id']==meta['dataset_id']
    for claim in claims.itertuples():
        if pd.notna(claim.check_json):
            assert np.isclose(float(claim.value),float(select(json.loads(claim.check_json))),rtol=1e-12,atol=1e-15),claim.claim_id
        elif claim.claim_id.startswith('test_') and claim.claim_id!='test_rows' and claim.claim_id!='test_distinct_failures':
            suffix=next(s for s in ['average_precision','brier','false_alarm_rate','quarter_recall','event_recall'] if claim.claim_id.endswith('_'+s))
            family=claim.claim_id[5:-(len(suffix)+1)]
            assert np.isclose(claim.value,table.loc[family,suffix],rtol=1e-12,atol=1e-15)
        elif claim.claim_id.startswith('development_'):
            family=claim.claim_id[len('development_'):-len('_AP')]
            dev=pd.read_csv(ROOT/claim.source).set_index('family')
            assert np.isclose(claim.value,dev.loc[family,'average_precision'],rtol=1e-12)
        else:
            values={'dataset_rows':meta['rows'],'dataset_banks':meta['banks'],'test_rows':len(evaluation),
                    'test_distinct_failures':evaluation.loc[evaluation.label_12m.eq(1),'CERT'].nunique()}
            if claim.claim_id in values:assert claim.value==values[claim.claim_id]
            elif claim.claim_id.startswith('current_'):
                summary=pd.read_csv(ROOT/claim.source).set_index(['seed','lag']).loc[(11,0)]
                value=summary['mean_gap' if 'gap' in claim.claim_id else 'top1_disagreement']*100
                assert np.isclose(claim.value,value,rtol=1e-12)
            elif claim.claim_id=='undefined_AP_bootstrap_draws':
                x=pd.read_csv(ROOT/claim.source);assert claim.value==x.loc[x.metric.eq('average_precision'),'undefined_draws'].iloc[0]
            elif claim.claim_id=='edge_targets_predicted_failure_class':
                x=pd.read_csv(ROOT/claim.source);assert claim.value==x.drop_duplicates('row_id').original_probability.ge(.5).sum()
            else:raise AssertionError(claim.claim_id)
    write_json(output/'verification.json',dict(status='passed',clean_environment=clean,python=sys.version,
        prefix=sys.prefix,code_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        verifier_sha256=sha(Path(__file__).read_bytes()),environment_lock_sha256=plan['environment_lock_sha256'],
        original_data_commit='51e3652',original_preprocessing_sha256=original['preprocessing_sha256'],
        dataset_id=meta['dataset_id'],checkpoint_fits_checked=checkpoints,models_checked=len(table),claims_checked=len(claims),
        predictions_recomputed=options.recompute_predictions,
        scope='Saved weights inference, nine primary tables and declared numeric claim map; no training or tuning rerun',
        limits='Fresh environment on same machine and raw snapshot; not independent data collection or finance review'))
    print(f'Passed: {checkpoints} checkpoints, {len(table)} model tables, {len(claims)} claims; fresh environment={clean}')


if __name__=='__main__':main()
