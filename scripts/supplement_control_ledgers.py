"""Reconstruct omitted control-invalid detail with unchanged frozen numeric code."""
import json
import time
import torch
import pandas as pd

from risktrace.analysis import load_analysis
from risktrace.core import ROOT,write_json
from risktrace.holdout import require_frozen_plan,load_checkpoint
from risktrace.predictive import role_frame
from risktrace.temporal import sequence
from risktrace.graph_models import prepare_graph
from risktrace.explanation_eval import financial_audit,parameter_hash


def main():
    plan=require_frozen_plan();panel,roles,prep,_=load_analysis()
    records=json.load(open(ROOT/'results/final_evaluation/fit_manifest.json'))
    logged=json.load(open(ROOT/'results/explanations/run_manifest.json'))['runs']
    saved=pd.read_csv(ROOT/'results/explanations/control_financial_cases.csv.gz')
    test=role_frame(panel,roles,'final','test');fit=role_frame(panel,roles,'final','train')
    spec=plan['settings']['explanations'];torch.set_num_threads(2)
    bad_frames=[];checks=[]
    for family in spec['null_controls']+['gat_gru_other_k']:
        start=time.perf_counter()
        r=next(r for r in records if r['report_label']==family and r['seed']==11)
        m=load_checkpoint(r)
        for p in m.parameters():p.requires_grad_(False)
        before=parameter_hash(m)
        seq=sequence(panel,prep['final'],test.report_date.max());prepare_graph(seq,m.kind,m.k,m.seed)
        with torch.no_grad():_,h=m(seq,True)
        threshold_family='gat_gru' if family=='gat_gru_other_k' else family
        cases,bad=financial_audit(m,seq,h,panel,test,prep['final'],spec,11,
            dict(sample=True,train_keys=fit.row_id,threshold=plan['seed_alert_thresholds'][threshold_family]['11']))
        original=saved.loc[saved.family.eq(family)].sort_values(['row_id','lag']).reset_index(drop=True)
        replay=cases.sort_values(['row_id','lag']).reset_index(drop=True)
        pd.testing.assert_series_equal(original.row_id,replay.row_id,check_names=False)
        for metric in ['mean_gap','max_gap','valid_subsets']:
            __import__('numpy').testing.assert_allclose(original[metric],replay[metric],atol=1e-12,rtol=1e-10)
        log=next(x for x in logged if x.get('family')==family)
        assert len(cases)==log['cases'] and len(bad)==log['invalid_records'] and parameter_hash(m)==before
        bad['family']=family;bad_frames.append(bad)
        checks.append(dict(family=family,cases=len(cases),invalid_detail_rows=len(bad),
                           saved_case_values_reproduced=True,parameters_unchanged=True,seconds=time.perf_counter()-start))
    pd.concat(bad_frames).to_csv(ROOT/'results/explanations/control_invalid_attempts.csv.gz',index=False,
                                compression={'method':'gzip','mtime':0})
    write_json(ROOT/'results/explanations/reporting_corrections.json',dict(
        finding='Independent reviewer identified omitted detailed control invalid-attempt ledgers; counts were present',
        correction='Supplementary reporting replay with exact same frozen settings/code/models; no retuning or refreeze',
        primary_results_changed=False,checks=checks))
    print('Saved control invalid ledgers; all replayed case values and counts match the original frozen results')


if __name__=='__main__':main()
