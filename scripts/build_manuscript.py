"""Build manuscript text/tables/TeX and a numeric claim map from frozen outputs."""
from __future__ import annotations
import html
import json
import re
import shutil
from pathlib import Path
import pandas as pd
from risktrace.core import ROOT,write_json
from claim_sources import select


def fmt(x,n=6):return f'{float(x):.{n}f}'


def main():
    meta=json.load(open(ROOT/'data/manifests/analysis_v1.json'))
    development=pd.read_csv(ROOT/'results/predictive/validation_results.csv').set_index('family')
    final=pd.read_csv(ROOT/'results/final_evaluation/results.csv').set_index('model')
    summary=pd.read_csv(ROOT/'results/explanations/financial_summary.csv').set_index(['seed','lag'])
    intervals=pd.read_csv(ROOT/'results/robustness/crossed_intervals.csv')
    cases=pd.read_csv(ROOT/'results/case_studies/proposed_case_register.csv',dtype={'CERT':str})
    edge=pd.read_csv(ROOT/'results/explanations/edge_cases.csv.gz')
    current,historical=summary.loc[(11,0)],summary.loc[(11,1)]
    claims=[]
    def claim(key,value,source,selector):
        claims.append(dict(claim_id=key,value=value,source=source,selector=selector));return value
    n=claim('dataset_rows',meta['rows'],'data/manifests/analysis_v1.json','rows')
    banks=claim('dataset_banks',meta['banks'],'data/manifests/analysis_v1.json','banks')
    holdout_n=claim('test_rows',int(final.iloc[0]['rows']),'results/final_evaluation/results.csv','all models: rows')
    test_events=claim('test_distinct_failures',int(final.iloc[0]['distinct_positive_banks']),'results/final_evaluation/results.csv','all models: distinct_positive_banks')
    gap=claim('current_mean_gap_pp',float(current.mean_gap)*100,'results/explanations/financial_summary.csv','seed11 lag0 mean_gap * 100')
    ranking=claim('current_top1_change_percent',float(current.top1_disagreement)*100,'results/explanations/financial_summary.csv','seed11 lag0 top1_disagreement * 100')
    undefined=claim('undefined_AP_bootstrap_draws',int(intervals.loc[intervals.metric.eq('average_precision'),'undefined_draws'].iloc[0]),'results/robustness/crossed_intervals.csv','average_precision: undefined_draws')
    pos_edge=claim('edge_targets_predicted_failure_class',int(edge.drop_duplicates('row_id').original_probability.ge(.5).sum()),'results/explanations/edge_cases.csv.gz','unique targets with p1 >= 0.5')
    for family,row in final.iterrows():
        for metric in ['average_precision','brier','false_alarm_rate','quarter_recall','event_recall']:
            claim(f'test_{family}_{metric}',float(row[metric]),'results/final_evaluation/results.csv',f'model={family}; {metric}')
    for family,row in development.iterrows():
        claim(f'development_{family}_AP',float(row.average_precision),'results/predictive/validation_results.csv',f'family={family}; average_precision')
    sections=[]
    def section(title,paragraphs,citations=()):sections.append(dict(title=title,paragraphs=paragraphs,citations=list(citations)))
    title='RiskTrace: Conditional and Pipeline Explanations in Sparse-Event Bank-Failure Forecasting'
    abstract=(f'We examine whether explanations of bank-failure forecasts change when financial-input edits propagate through feature-derived graph construction. '
        f'The study uses {n:,} eligible quarterly reports from {banks:,} FDIC-insured banks, explicit historical label-maturity gates, '
        'strong tabular baselines and bounded static/temporal graph models. Annual development validation contains only six distinct failed banks. '
        f'The observable holdout contains {holdout_n:,} reports from 2022Q1 through 2025Q1 and {test_events} distinct failed banks. '
        'At fixed validation-derived alert thresholds, XGBoost and all graph variants miss every failure; logistic regression detects one with an achieved false-alarm rate near 2%. '
        f'The primary current-input audit has a mean conditional/pipeline probability gap of {gap:.4f} percentage points and '
        f'{ranking:.2f}% top-one disagreement among complete interventions. All class-conditional edge masks explain nonfailure, '
        f'and {undefined}/500 bank/time bootstrap draws have undefined average precision. These exploratory results separate audit targets '
        'but do not establish predictive superiority, economic materiality, causal validity or strong methodological novelty.')
    section('1. Introduction',[
        'Bank-level failure forecasting is a rare-event problem in which repeated quarterly warnings can disguise a very small number of distinct events. '
        'A graph model can add another difficulty: financial attributes can define both node inputs and similarity links. Editing an attribute while keeping links fixed therefore answers a different question from propagating that edit through the complete fitted pipeline.',
        'RiskTrace studies that distinction as an empirical audit question. The conditional-network target is legitimate; disagreement does not by itself make its explanation wrong. '
        'The pipeline target instead follows the deterministic dependencies actually implemented by the predictor. Neither target estimates a causal financial intervention or systemic spillover.',
        'The study supplies a versioned public-source build, forecast-origin contracts, comparable predictive baselines and a paired response ledger with invalid-attempt accounting. '
        'These are reproducible artifacts and scoped empirical findings, not a claim to introduce a new GNN architecture, a first faithfulness metric or a publication-ready supervisory system. '
        'The observed weak warning performance is central to interpreting the explanations.'
    ])
    section('2. Related work and scope of the candidate contribution',[
        'Temporal bank graph forecasting, financial factual/counterfactual explanation and uncertain network reconstruction already exist. '
        'The banking preprints and CF3 overlap with substantial parts of the proposed application; Ahn and colleagues study uncertainty in financial-network risk. '
        'A similarity graph inferred from balance-sheet ratios must not be confused with measured bilateral exposures.',
        'GNNExplainer formulates compact feature/subgraph explanations through mask optimization. GInX-Eval, DSE and Robust Fidelity address important distributional or fidelity-evaluation problems, '
        'while fragility, uncertainty, curvature and degeneracy work show why explanation scores alone need careful interpretation. '
        'Our frozen raw-input dependency audit has a narrower target than retraining on degraded graphs or generating surrogate completions. '
        'Selected prior implementation paths were inspected, but the study does not reproduce every close method or prove that no equivalent pipeline audit exists.',
        'Accordingly, the remaining candidate contribution is an explicit and falsifiable comparison of conditional-network and full-pipeline responses under a bank-feature dependency contract. '
        'The elementary composition identity, graph rebuilding, attention visualization and use of a standard explainer are not claimed as new. '
        'Independent close-baseline reproductions and broader evidence are needed for a strong novelty claim.'
    ],['stgat2026','multiplex2026','cf3_2025','ahn2024','gnnexplainer2019','ginx2023','dse2022','rfidelity2024','fragile2024','eugnn2024','curvature2025','degenerate2026','xgnncert2025'])
    section('3. Data, outcome and information clocks',[
        f'The source snapshot contains {n:,} bank-quarter records and {banks:,} distinct FDIC certificate identifiers over 2010Q1--2025Q4. '
        'Eligibility is evaluated at each historical report: USD 1 billion inclusive to USD 250 billion exclusive in assets and the specified domestic insured commercial/savings classes. '
        'There is no current-survivor filter. This is an operational asset band, not a regulatory definition of regional banking. The unit is an individual insured bank, not its holding company.',
        'Official FDIC BankFind financial and failure responses are checksum-preserved. Raw amounts retain the documented USD-thousands convention. '
        'Core ratios are total equity capital (EQTOT)/assets, cash/assets, net loans/assets, securities/assets and noncurrent/gross loans. '
        'EQTOT, rather than the distinct EQ field, closes the accounting identity. Structurally undefined ratios and failed range checks remain flagged/excluded rather than zero-filled. '
        'Domestic uninsured deposit scope, duration gaps and depositor concentration are not silently replaced with invented proxies.',
        'The primary outcome is a recorded charter-termination failure within twelve calendar months after assumed information availability. '
        'Assistance/reprivatization transactions are excluded. Already-failed observations are unusable; unobservable horizons are censored. '
        'Availability is report date plus 60 calendar days, explicitly an assumption. Failure observation is conservatively capped at the source index date, 25 August 2026. '
        'These are revised historical snapshots, not verified point-in-time vintages or forecasts issued contemporaneously.',
        'CERT is the outcome/node key. Three certificates have RSSD changes, six RSSDs span multiple certificates, and 224 certificates have historical name changes. '
        'No histories are spliced across certificates; recurrent state resets at unavailable/unusable reports or RSSD changes. '
        'Legal succession, independent historical-roster completeness and merger competing-event interpretation remain source/finance limitations.',
        'The centrally assembled canonical panel is not described as a verified submission by Ayush. The allocation gives each collaborator 807 banks, '
        'but Ayush\'s own submission and finance review were not received. Collection provenance and authorship approval are separate from the successful internal dataset checks.'
    ])
    section('4. Chronological evaluation and predictive models',[
        'The original 2019--2021 validation block contains no positive failures. After comparing concrete alternatives, the user approved annual expanding-origin development validation for 2012--2020. '
        'Every model fits at 30 May of its report year and only uses training records whose entire twelve-month outcome window ends strictly earlier, for both classes. '
        'All validation years, including zero-event years, remain in pooled out-of-fold evaluation. There are 26,104 validation records, 17 positive quarters and six distinct failed banks; repeated windows are not independent events.',
        'A static final model fits as of 30 May 2022 using 31,319 mature records through 2020Q4 and 22 distinct failed banks. '
        'Late-2021 outcome labels cannot select or calibrate that model, because many were not known by the first test forecast. '
        '2021 covariates can warm temporal state as they become available. The nominal 2022--2025 holdout was previously counted for feasibility and is not described as completely unseen; '
        f'its fully observable evaluation reports end at 2025Q1, giving {holdout_n:,} rows, 16 positive quarters and four distinct failed banks.',
        'Each fold fits its own median/mean/scale on exact training keys. No identifier, future failure date, ownership, label or legacy split flag enters the model. '
        'Logistic regression and XGBoost precede a no-graph GRU. The bounded search uses two configurations per primary learned family, fixed k=3 random/state controls, one deterministic reference/logistic seed and three stochastic seeds (11, 29, 47). '
        'Training-prevalence initialization and analytic prior correction are documented; no flexible posthoc calibrator is fitted to six validation banks. '
        'Stochastic primary forecasts average the prespecified seeds. Neural optimization uses fixed epochs, clipping and L2 decay on CPU.',
        'Static GAT uses one attention head, a linear projection, additive attention, softmax over self and valid neighbors, ELU and a readout. '
        'GAT+GRU passes those contemporaneous representations through an own-bank recurrent state. Financial graphs use k=3 or 7 nearest neighbors in training-standardized ratio space; the self edge is additional. '
        'No-graph, random fixed-k neighbor-count and state-first controls make their definitions explicit. Only currently active banks enter a snapshot. '
        'Contemporaneous covariates of other banks are assumed available under the common lag. Messages do not contain other banks\' hidden states.',
        'Primary metrics are average precision (AP), Brier score, event warnings and quarter recall at a validation-derived false-alarm operating point. '
        'AP is not trapezoidal PR area. Thresholds are the pooled validation-negative 99th percentile with strict greater-than comparison; achieved test false-alarm rates are reported rather than retuned. '
        'Warning time starts at assumed availability, and event detection deduplicates certificates. AUROC is secondary.',
        'Model/data/configuration/source/environment hashes and the complete explanation/robustness plan were committed before the first test opening. '
        'An initial equality guard rejected a Windows CRLF/LF mismatch before any test computation; the original plan and technical revision are preserved. '
        'The scientific choices were unchanged when the corrected plan was committed. The main study comprises 297 development fits and 23 final fits; the earlier small mechanism pilot is separate.'
    ],['xgboost2016','gru2014','gat2018'])
    section('5. Explanation targets and financial probes',[
        'Write the fitted predictor as F(B)=f(T(B),g(T(B))), where B denotes the observed bank-history records, T the fixed training-fitted transformation and g the specified graph builder. '
        'For a raw replacement P, compare p_A=f(T(P(B)),g(T(B))) with p_B=f(T(P(B)),g(T(P(B)))). '
        'Both recompute actual derived inputs, attention coefficients and affected recurrent states. The difference is whether feature-derived adjacency follows the edit. '
        'Fitted parameters and preprocessing remain fixed, and genuinely exogenous components remain unchanged.',
        'Three prespecified raw groups cover capital, asset composition and credit quality. Same-quarter/same-charter donors are within a factor of two in assets; '
        'a stable hash selects among the nearest eight log-asset matches. Donor amounts are scaled to target assets, with liabilities and dependent loan-quality quantities adjusted as specified. '
        'All seven nonempty group subsets are attempted. Invalid accounting/ranges are logged without donor resampling; marginal range and nearest-training-distance diagnostics do not establish economic or joint-distribution support.',
        'Current and one-quarter-historical edits are evaluated. Target-local rebuilding and own-bank replay are exact for this architecture because its messages contain contemporaneous ratios, not neighbor hidden states; '
        'unit and independent actual-checkpoint tests compare this shortcut to a full edited snapshot/history pass. Changes outside the target\'s prediction path are not measured systemic spillovers.',
        'The primary financial audit uses seed 11 across all eligible targets with explicit exclusions. Additional seeds, null controls and the other k use the lowest-hash 32 rows per quarter, independent of outcomes. '
        'Full rankings require seven valid subsets; partial cases still retain available-subset response gaps. Necessity and keep-only sufficiency are signed p1 responses. '
        'Top-one rankings use absolute group responses at equal one-group budgets. A paired alert change means the two counterfactual target probabilities straddle the same seed-specific OOF threshold in at least one valid subset.',
        'A separate edge-unit comparison evaluates attention, an edge-only GNNExplainer-style mask optimization adaptation and random rankings, at two nonself edges. '
        'It preserves the original predicted binary class, fixes previous state and optimizes only current masks for 30 steps with predeclared penalties. '
        'It is not a complete reproduction of every original feature/temporal setting, nor a universal explanation-quality oracle. Edge and financial-group budgets are not cross-ranked.'
    ],['gnnexplainer2019','rfidelity2024'])
    section('6. Predictive results',[
        f'Development AP is {development.loc["xgboost","average_precision"]:.6f} for XGBoost, {development.loc["logistic","average_precision"]:.6f} for logistic, '
        f'{development.loc["gat","average_precision"]:.6f} for static GAT and {development.loc["gat_gru","average_precision"]:.6f} for financial GAT+GRU. '
        'The temporal graph has a slightly smaller development Brier score than XGBoost, but no graph predictive-superiority claim follows. '
        'Configuration selection and sparse event concentration make these development results optimistic for future generalization.',
        f'On the held-out data, XGBoost AP is {final.loc["xgboost","average_precision"]:.6f}; financial GAT+GRU AP is {final.loc["gat_gru","average_precision"]:.6f}. '
        'Both miss every failed bank at their frozen operating thresholds. Static GAT, no-graph GRU and random/state controls also detect none. '
        f'Logistic detects one of four banks, with AP {final.loc["logistic","average_precision"]:.6f} and achieved FPR {final.loc["logistic","false_alarm_rate"]*100:.3f}%. '
        'Its first warning for that one detected event is 332 days under assumed availability; that does not describe the three missed events.',
        'The observed false-alarm rates differ from the validation 1% target. They are not matched 1% test-FPR comparisons. '
        'Calibration is uncertain, and a tiny Brier difference under rare events is not proof of an economically useful gain. '
        'The deterioration does not identify a causal explanation for regime change. No setting is replaced with a hindsight-selected test winner.'
    ])
    section('7. Paired explanation results',[
        f'Current edits have {int(current.cases):,} donor-matched cases after three no-donor exclusions; {int(current.complete_audits):,} have all seven subsets valid. '
        f'The mean paired gap is {gap:.6f} percentage points, while the largest is {current.max_gap*100:.6f} pp. '
        f'Top-one disagreement is {ranking:.2f}% among complete audits. Any paired operating-threshold disagreement occurs in {current.alert_disagreement*100:.4f}% of donor-matched cases. '
        'A large ranking-change fraction can accompany a small average probability response; it is not automatically a material financial effect.',
        f'Historical edits have {int(historical.cases):,} cases after 274 unavailable-history/no-donor exclusions, with a mean gap of {historical.mean_gap*100:.6f} pp '
        f'and {historical.top1_disagreement*100:.2f}% top-one disagreement among {int(historical.complete_audits):,} complete audits. '
        'Across both primary lags, 14,420 of 177,023 attempted subsets fail financial constraints (8.15%). '
        'Partially valid cases and all unattempted/invalid records remain visible. Null graph controls produce zero paired gaps as required by their definitions.',
        f'All {edge.row_id.nunique():,} edge targets have p1 below 0.5 (maximum {edge.original_probability.max():.5f}); '
        f'{pos_edge} optimized masks therefore target the failure class. The mask objective explains nonfailure throughout, while alert thresholds are much lower. '
        'Signed necessity below zero can mean that deleting nonfailure-supporting edges raises failure probability; it does not establish inferior fidelity. '
        'Attention is not declared superior from a positive signed mean. This target mismatch is a substantive limitation for risk-alert interpretation and must not be silently redesigned on the same test.',
        'The independent reviewer found that the original control export retained invalid-attempt counts but omitted their detailed invalid rows. '
        'A supplementary replay with identical frozen code/models/settings reproduced all saved control case values and exported 508 detailed invalid/unavailable records per family. '
        'This is a reporting repair, not a changed primary analysis.'
    ])
    section('8. Robustness and proposed case studies',[
        'Seed ranges, both neighbor counts, static/temporal/no-graph components, random/state controls and report-year strata are reported without reselection. '
        'Report-year strata do not equal failure years: a late-year report may become available in the next year, with a horizon extending further. '
        'Zero-event strata have unavailable discrimination metrics rather than an invented zero score.',
        f'The paired uncertainty diagnostic independently resamples connected CERT/RSSD clusters and calendar-year blocks, multiplying row counts. '
        f'{undefined} of 500 AP draws contain no positive event and are undefined; the displayed percentile ranges condition on the other {500-undefined}. '
        'With four failed banks and four year blocks, one partial, these are exploratory pigeonhole-style sensitivities, not established nominal 95% coverage or a robust significance certificate for nonlinear AP. '
        'The paired ranges do not establish a graph gain. Year blocking may not capture all common-shock/serial dependence.',
        'Proposed packets cover Silicon Valley Bank (CERT 24735, 2023), Signature Bank (57053, 2023), First Republic Bank (59017, 2023) and Republic Bank (27332, 2024). '
        'The two Republic institutions are distinct. Each comparison uses a same-report/same-charter, factor-two-asset, nearest-size nonfailure-horizon bank outside the failed bank\'s identity component. '
        'Case selection is retrospective and separate from primary evaluation. Plots use valid held-out forecast origins, not fabricated pre-2022 forecasts from a model fitted in 2022.',
        'Case forecasts and exact saved financial/edge explanation extracts are supplied for finance review. They do not infer the economic cause of a failure, and '
        'Ayush\'s case selection, source interpretation and approval remain pending. The illustrated XGBoost/GAT+GRU curves were selected by the development protocol; '
        'logistic\'s one detected event is reported in the primary table rather than substituted into the illustration as a hindsight winner.'
    ],['owen2007'])
    section('9. Limitations and verification',[
        'The narrow asset band discards many bank failures, leaving six development and four test failing banks. Repeated positive quarters do not solve that event budget. '
        'The fitted models use only five aggregate ratios; concentration, maturity structure, actual exposures and some potentially important contemporaneous information are absent. '
        'A bounded small-architecture search does not prove that all graph models fail. The revised snapshots, lag assumption, roster completeness and competing mergers limit deployment interpretation.',
        'Accounting-valid donor probes are not proven realistic, jointly supported or causal; a range check cannot certify them. '
        'Current-edge explanation of nonfailure does not validate risk alerts, and one-lag history probes do not exhaust all temporal explanation questions. '
        'Close evaluator implementations were not all independently reproduced, and neither an exhaustive novelty search nor expert explanation ground truth exists.',
        'A separate AI reviewer independently checked all split memberships and training statistics, failure labels, final checkpoint hashes and metrics, actual target-local replay, '
        'explanation budgets/denominators, bootstrap outputs and case matching. This is technical verification, not external peer review or human finance validation. '
        'The review also identified a prospective plan-hardening gap: preprocessing is checked through the analysis manifest rather than directly pinned by the plan. '
        'For this study, both artifacts were independently compared with the committed Step 8 digest and matched; no self-consistent alteration occurred. '
        'Future protocols should bind them directly. Clean-environment inference/table reproduction is reported separately, including its exact scope.'
    ])
    section('10. Conclusion',[
        'RiskTrace distinguishes two legitimate explanation questions and measures their effect under an explicit financial-input dependency contract. '
        'The observed ranking changes coexist with small average probability gaps and poor warning performance. '
        'These results do not establish graph predictive superiority, economic usefulness, causal validity, systemic-risk measurement or high methodological novelty.',
        'The appropriate output is a transparent sparse-event feasibility/audit study and reproducibility package. '
        'Before a strong journal submission, the authors must resolve finance/source interpretation, independent-event power, alert-target alignment, close-method comparisons, '
        'authorship and venue requirements. Any redesign must use a new development protocol and acknowledge that this holdout has been examined.'
    ])
    section('Declarations and review status',[
        'Working draft only; no submission or acceptance has occurred. Proposed contributors are Ayush Sinha and Atharva Sheersh Pandey; author order, affiliations, corresponding author, '
        'funding, conflicts, actual contribution statements and final approval have not been confirmed. No coauthor review is invented.',
        'OpenAI Codex assisted code generation/editing, experiment orchestration, source checking, plots and manuscript drafting. A separate AI agent audited the implementation and outputs. '
        'The exact tool/model build identifier and the named authors\' substantive oversight statement must be confirmed from logs and by the authors before submission. '
        'AI assistance is not authorship, human critical review or independent financial expertise. The authors must review, amend and approve the complete text and research responsibilities.',
        'Source acquisition instructions, configuration locks, versioned manifests, model checkpoints, figure generators, saved results and the numerical claim map accompany the draft. '
        'Exact raw snapshots are preserved locally; public archival/reuse terms and a software license require author confirmation. '
        'The current journal guides/fees and direct current Q1 rankings are not verified; no submission-ready claim is made.'
    ])
    names={'prevalence':'Prevalence','logistic':'Logistic','xgboost':'XGBoost','gru':'GRU','gat':'Static GAT','gat_gru':'GAT+GRU',
           'gat_gru_random':'Random graph','gat_gru_exogenous':'State graph','gat_gru_other_k':'Other k sensitivity'}
    prediction_table=[['Model','Development AP','Test AP','Test Brier','Test FPR (%)','Events detected']]
    for family,row in final.iterrows():
        dev=development.loc[family,'average_precision'] if family in development.index else None
        prediction_table.append([names[family],'-' if dev is None else fmt(dev),fmt(row.average_precision),fmt(row.brier,8),
                                 fmt(row.false_alarm_rate*100,3),f'{int(row.detected_events)}/{int(row.distinct_positive_banks)}'])
    financial_table=[['Lag','Matched cases','Complete cases','Mean gap (pp)','Max gap (pp)','Top-1 change (%)']]
    for lag,s in [(0,current),(1,historical)]:
        financial_table.append([str(lag),str(int(s.cases)),str(int(s.complete_audits)),fmt(s.mean_gap*100),fmt(s.max_gap*100),fmt(s.top1_disagreement*100,2)])
    source_bib=(ROOT/'paper/references.bib').read_text(encoding='utf8')
    refs=[]
    for match in re.finditer(r'@\w+\{([^,]+),\s*(.*?)(?=\n@|\Z)',source_bib,re.S):
        fields={k:v for k,v in re.findall(r'(\w+)\s*=\s*\{(.*?)\}\s*[,\n]',match[2]+'\n',re.S)}
        refs.append(dict(key=match[1],**fields))
    assert len(refs)==17 and all(r.get('author') and r.get('title') and r.get('year') for r in refs)
    figures=[dict(file='predictive_comparison.png',caption='Development OOF and held-out metrics at unchanged settings. Compare Brier within each split: event prevalence differs across periods.'),
             dict(file='calibration_and_alarms.png',caption='Descriptive calibration and achieved test false-alarm rates. The 1% target was selected on validation, not enforced on test. Sparse positives make calibration uncertain.'),
             dict(file='financial_audit.png',caption='Primary seed-11 mean-gap distribution and changes in rankings/paired alert decisions. Mean gaps use donor-matched cases; rankings use complete seven-subset cases. Zero gaps use the stated plotting floor.'),
             dict(file='case_forecasts.png',caption='Proposed retrospective case packets for the preselected XGBoost and GAT+GRU models. CERT27332 (Republic Bank, 2024) is distinct from CERT59017 (First Republic, 2023). Finance interpretation is pending; these are revised-snapshot reconstructions, not forecasts issued at those dates.')]
    content=dict(title=title,status='WORKING DRAFT - NOT APPROVED FOR SUBMISSION',
                 proposed_authors='Ayush Sinha; Atharva Sheersh Pandey (author order and affiliations pending)',
                 abstract=abstract,sections=sections,tables=[dict(caption='Predictive comparison. Test recall uses fixed validation-derived thresholds; achieved FPR differs.',rows=prediction_table),
                 dict(caption='Paired financial-input audit. Probability gaps are percentage points, not percentages of original risk.',rows=financial_table)],
                 figures=figures,references=refs,dataset_id=meta['dataset_id'])
    manuscript=ROOT/'paper/manuscript';manuscript.mkdir(exist_ok=True)
    write_json(manuscript/'content.json',content)
    markdown=['# '+title,'',content['status'],'',content['proposed_authors'],'','## Abstract','',abstract]
    for section_ in sections:
        markdown.extend(['','## '+section_['title'],'',*sum(([p,''] for p in section_['paragraphs']),[])])
        if section_['citations']:markdown.append('Sources: '+', '.join('[@'+key+']' for key in section_['citations']))
    for table in content['tables']:
        markdown.extend(['','### '+table['caption'],'','| '+' | '.join(table['rows'][0])+' |','| '+' | '.join(['---']*len(table['rows'][0]))+' |'])
        markdown.extend('| '+' | '.join(row)+' |' for row in table['rows'][1:])
    for figure in figures:markdown.extend(['',f"![{figure['caption']}](../figures/{figure['file']})"])
    markdown.extend(['','## References',''])
    for index,r in enumerate(refs,1):markdown.append(f"{index}. {r['author']} ({r['year']}). {r['title']}. {r.get('url',r.get('doi',''))}")
    (manuscript/'manuscript.md').write_text('\n'.join(markdown)+'\n',encoding='utf8',newline='\n')
    # Supplement every other empirical numerical prose claim with explicit
    # selectors. Method constants are mapped separately to the frozen contract.
    def checked(key,source,kind='csv',**spec):
        spec=dict(kind=kind,source=source,**spec);value=select(spec)
        claims.append(dict(claim_id=key,value=value,source=source,selector=json.dumps(spec,sort_keys=True),check_json=json.dumps(spec,sort_keys=True)))
    for field in ['rows','positive_quarters','distinct_positive_banks']:
        checked('OOF_'+field,'results/predictive/validation_results.csv',field=field)
    for family in ['gat_gru','xgboost']:
        checked('OOF_'+family+'_brier','results/predictive/validation_results.csv',field='brier',filters=[['family','eq',family]])
    for field in ['rows','distinct_positive_banks']:
        checked('fit_'+field,'data/manifests/analysis_v1.json','json',path=['final_fit_counts',field])
    for field in ['certs_with_multiple_rssd_ids','rssd_ids_shared_by_multiple_certs','certs_with_multiple_names']:
        checked('identity_'+field,'data/manifests/analysis_v1.json','json',path=['identifier_audit',field])
    for field in ['positive_quarters','detected_events','missed_events','median_warning_days_detected']:
        checked('logistic_'+field,'results/final_evaluation/results.csv',field=field,filters=[['model','eq','logistic']])
    checked('warning_logistic_crosscheck','results/final_evaluation/logistic_warning_events.csv',field='warning_days',op='max')
    for family in final.index:
        checked('detected_events_'+family,'results/final_evaluation/results.csv',field='detected_events',filters=[['model','eq',family]])
    for lag in [0,1]:
        for field in ['cases','complete_audits','mean_gap','max_gap','top1_disagreement','alert_disagreement']:
            checked(f'financial_lag{lag}_{field}','results/explanations/financial_summary.csv',field=field,
                    filters=[['seed','eq',11],['lag','eq',lag]],scale=100 if field not in ['cases','complete_audits'] else 1)
        checked(f'excluded_lag{lag}','results/explanations/invalid_attempts.csv.gz',op='count',
                filters=[['seed','eq',11],['lag','eq',lag],['subset','eq','not_attempted']])
    checked('invalid_subset_attempts','results/explanations/invalid_attempts.csv.gz',op='count',
            filters=[['seed','eq',11],['subset','ne','not_attempted']])
    checked('attempted_subsets','results/explanations/financial_cases.csv.gz',op='count',filters=[['seed','eq',11]],scale=7)
    checked('edge_unique_targets','results/explanations/edge_cases.csv.gz',field='row_id',op='nunique')
    checked('edge_max_original_p1','results/explanations/edge_cases.csv.gz',field='original_probability',op='max')
    for family in ['gat_gru_random','gat_gru_exogenous','gat_gru_other_k']:
        checked('control_invalid_'+family,'results/explanations/control_invalid_attempts.csv.gz',op='count',filters=[['family','eq',family]])
    for family in ['gat_gru_random','gat_gru_exogenous']:
        checked('null_gap_'+family,'results/explanations/control_financial_cases.csv.gz',field='max_gap',op='max',filters=[['family','eq',family]])
    checked('development_fit_count','results/predictive/*_run_manifest.json','json_glob')
    checked('final_fit_count','results/final_evaluation/fit_manifest.json','json',op='len')
    for owner in ['Ayush Sinha','Atharva Sheersh Pandey']:
        checked('allocation_'+owner.replace(' ','_'),'data/bank_allocation.csv',op='count',filters=[['owner','eq',owner]])
    checked('AP_defined_bootstrap_draws','results/robustness/crossed_intervals.csv',field='defined_draws',filters=[['metric','eq','average_precision']])
    checked('bootstrap_replicates','results/robustness/method.json','json',path=['replicates'])
    pd.DataFrame(claims).to_csv(ROOT/'docs/claim_evidence_map.csv',index=False)
    methods=[dict(claim='Calendar periods, origin dates and censoring rule',source='configs/splits.yaml; data/manifests/analysis_v1.json; results/final_evaluation/*_predictions.csv.gz',
                  selector='fold dates and min/max report_date; outcome_cutoff; effective test ends2025Q1'),
             dict(claim='USD1B inclusive to250B exclusive; lag60days; horizon12months',source='configs/data_spec.yaml; src/risktrace/analysis.py',selector='population and labels; raw amounts USD thousands'),
             dict(claim='Five inputs, three stochastic seeds, two candidate configurations, k3/7, one GAT head',source='configs/experiments.yaml; src/risktrace/graph_models.py',selector='model_features,seeds,families,GraphTemporal'),
             dict(claim='Three financial groups; seven nonempty subsets; nearest8 donors; factor2assets; twoedge masks;30masksteps;32rowsperquarter; lag0/1',
                  source='configs/final_evaluation.yaml; src/risktrace/explanation_eval.py',selector='settings.explanations and probe/edge implementation'),
             dict(claim='Four cases: CERT/name/failure year and matching',source='results/case_studies/proposed_case_register.csv',selector='all four rows; CERT24735/57053/59017=2023;27332=2024'),
             dict(claim='Invalid subset percent8.15%',source='docs/claim_evidence_map.csv',selector='100*invalid_subset_attempts/attempted_subsets; report rounding'),
             dict(claim='Four report-year blocks with2025partial; APquantiles2.5/97.5%; seedranges notCIs',source='results/final_evaluation/*_predictions.csv.gz; src/risktrace/robustness.py',selector='report_date yearnunique; crossed_draws and quantiles'),
             dict(claim='Predicted class boundary0.5; validationtargetFPR1%; warning332days',source='src/risktrace/explanation_eval.py; configs/experiments.yaml; results/final_evaluation/logistic_warning_events.csv',selector='masktarget;false_alarm_rate;detected bankwarning')]
    pd.DataFrame(methods).to_csv(ROOT/'docs/method_claim_sources.csv',index=False)
    # Self-contained TeX project: same text, tables, figures and verified bibliography.
    def tex(s):
        replacements={'\\':r'\textbackslash{}','&':r'\&','%':r'\%','$':r'\$','#':r'\#','_':r'\_','{':r'\{','}':r'\}','~':r'\textasciitilde{}'}
        return ''.join(replacements.get(ch,ch) for ch in str(s))
    out=[r'\documentclass[11pt]{article}',r'\usepackage[T1]{fontenc}',r'\usepackage[utf8]{inputenc}',r'\usepackage[margin=24mm]{geometry}',
         r'\usepackage{graphicx,booktabs,longtable,natbib,hyperref}',r'\title{'+tex(title)+'}',r'\author{'+tex(content['proposed_authors'])+'}',
         r'\date{Working draft, 27 October 2026}',r'\begin{document}',r'\maketitle',r'\begin{center}\textbf{'+content['status']+r'}\end{center}',
         r'\begin{abstract}'+tex(abstract)+r'\end{abstract}']
    for section_ in sections:
        heading=re.sub(r'^\d+\. ','',section_['title']);out.append(r'\section{'+tex(heading)+'}')
        out.extend(tex(p)+'\n' for p in section_['paragraphs'])
        if section_['citations']:out.append(r'\citep{'+','.join(section_['citations'])+'}.')
    for table in content['tables']:
        out.extend([r'\begin{table}[p]\centering',r'\caption{'+tex(table['caption'])+'}',r'\resizebox{\textwidth}{!}{%',r'\begin{tabular}{'+'l'*len(table['rows'][0])+'}',r'\toprule'])
        for i,row in enumerate(table['rows']):out.append(' & '.join(tex(c) for c in row)+r' \\'+(r'\midrule' if i==0 else ''))
        out.extend([r'\bottomrule\end{tabular}}',r'\end{table}'])
    images=manuscript/'images';images.mkdir(exist_ok=True)
    for figure in figures:
        shutil.copyfile(ROOT/'paper/figures'/figure['file'],images/figure['file'])
        out.extend([r'\begin{figure}[p]\centering',r'\includegraphics[width=\textwidth]{images/'+figure['file']+'}',
                    r'\caption{'+tex(figure['caption'])+'}',r'\end{figure}'])
    out.extend([r'\clearpage\bibliographystyle{plainnat}',r'\bibliography{references}',r'\end{document}'])
    (manuscript/'main.tex').write_text('\n'.join(out)+'\n',encoding='utf8',newline='\n')
    (manuscript/'references.bib').write_text(source_bib,encoding='utf8',newline='\n')
    print(f'Built manuscript, {len(sections)} sections, {len(refs)} references, {len(claims)} numeric claims and self-contained TeX')


if __name__=='__main__':main()
