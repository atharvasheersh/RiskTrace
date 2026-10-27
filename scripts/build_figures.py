"""Generate scientific figures and case extracts directly from saved frozen outputs."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from risktrace.core import ROOT

NAMES={'prevalence':'Prevalence','logistic':'Logistic','xgboost':'XGBoost','gru':'GRU','gat':'Static GAT',
       'gat_gru':'GAT+GRU','gat_gru_random':'Random GAT+GRU','gat_gru_exogenous':'State GAT+GRU'}
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'figure.dpi':150,'svg.hashsalt':'RiskTrace-v1'})


def save(fig,name):
    folder=ROOT/'paper/figures';folder.mkdir(parents=True,exist_ok=True)
    fig.savefig(folder/f'{name}.png',dpi=300,bbox_inches='tight')
    svg=folder/f'{name}.svg'
    fig.savefig(svg,bbox_inches='tight',metadata={'Date':None})
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf8').splitlines())+'\n',encoding='utf8',newline='\n')
    plt.close(fig)


def main():
    development=pd.read_csv(ROOT/'results/predictive/validation_results.csv').set_index('family')
    test=pd.read_csv(ROOT/'results/final_evaluation/results.csv').set_index('model')
    keys=['logistic','xgboost','gru','gat','gat_gru','gat_gru_random','gat_gru_exogenous']
    x=np.arange(len(keys));width=.36
    fig,axes=plt.subplots(1,2,figsize=(12.5,4.8))
    for ax,metric,title in zip(axes,['average_precision','brier'],['Average precision','Brier score']):
        ax.bar(x-width/2,development.loc[keys,metric],width,label='Development OOF',color='#31588e')
        ax.bar(x+width/2,test.loc[keys,metric],width,label='Frozen test',color='#bc643c')
        ax.set_xticks(x,[NAMES[k] for k in keys],rotation=28,ha='right');ax.set_title(title);ax.grid(axis='y',alpha=.2)
    axes[0].set_yscale('log');axes[0].set_ylabel('Average precision (log scale)')
    axes[1].set_ylabel('Mean squared probability error');axes[1].ticklabel_format(axis='y',style='sci',scilimits=(-3,-3))
    axes[0].legend(frameon=False);fig.suptitle('Sparse-event forecasts: development ranking did not transfer reliably')
    fig.tight_layout();save(fig,'predictive_comparison')

    cases=pd.read_csv(ROOT/'results/explanations/financial_cases.csv.gz',dtype={'CERT':str})
    primary=cases.loc[cases.seed.eq(11)]
    summary=pd.read_csv(ROOT/'results/explanations/financial_summary.csv').set_index(['seed','lag'])
    fig,axes=plt.subplots(1,2,figsize=(11.5,4.2))
    for lag,color in [(0,'#31588e'),(1,'#bc643c')]:
        g=primary.loc[primary.lag.eq(lag)];values=np.sort(np.maximum(g.mean_gap.to_numpy()*100,1e-8))
        axes[0].plot(values,np.arange(1,len(values)+1)/len(values),label=f'Lag {lag}, n={len(g):,}',color=color)
    axes[0].set_xscale('log');axes[0].set_xlabel('Mean gap per case (percentage points; zeros at 1e-8)')
    axes[0].set_ylabel('Cumulative fraction');axes[0].legend(frameon=False);axes[0].grid(alpha=.2)
    for lag,offset,color in [(0,-.18,'#31588e'),(1,.18,'#bc643c')]:
        s=summary.loc[(11,lag)];values=np.array([s.top1_disagreement,s.alert_disagreement])*100
        bars=axes[1].bar(np.arange(2)+offset,values,.36,label=f'Lag {lag}',color=color)
        axes[1].bar_label(bars,fmt='%.2f%%',padding=3,fontsize=8)
    axes[1].set_xticks([0,1],['Top-1 change\n(complete audits)','Any paired alert change\n(donor-matched cases)'])
    axes[1].set_ylabel('Percentage of stated cases');axes[1].set_ylim(0,16.5);axes[1].legend(frameon=False)
    fig.suptitle('Conditional versus pipeline responses: small average gaps, different rankings')
    fig.tight_layout();save(fig,'financial_audit')

    fig,axes=plt.subplots(1,2,figsize=(11.5,4.5))
    colors=['#31588e','#bc643c','#4d8166','#7a638d','#777777']
    for family,color in zip(['logistic','xgboost','gru','gat','gat_gru'],colors):
        bins=pd.read_csv(ROOT/f'results/final_evaluation/{family}_calibration.csv')
        axes[0].plot(bins.mean_probability,bins.observed_frequency,'o-',label=NAMES[family],color=color,markersize=3)
    bound=max(axes[0].get_xlim()[1],axes[0].get_ylim()[1]);axes[0].plot([0,bound],[0,bound],'--',color='black',lw=.8)
    axes[0].set_xlabel('Mean predicted probability');axes[0].set_ylabel('Observed failure-quarter fraction')
    axes[0].set_title('Descriptive quantile-bin calibration');axes[0].legend(frameon=False,fontsize=8)
    axes[1].bar(x,test.loc[keys,'false_alarm_rate']*100,color='#31588e')
    axes[1].axhline(1,color='#bc643c',ls='--',label='Validation target: 1%')
    axes[1].set_xticks(x,[NAMES[k] for k in keys],rotation=28,ha='right')
    axes[1].set_ylabel('Achieved test false-alarm rate (%)');axes[1].set_title('Thresholds retained without test retuning');axes[1].legend(frameon=False)
    fig.suptitle('Only 16 positive test quarters from four banks; calibration is uncertain')
    fig.tight_layout();save(fig,'calibration_and_alarms')

    register=pd.read_csv(ROOT/'results/case_studies/proposed_case_register.csv',dtype={'CERT':str,'matched_survivor':str})
    trajectory=pd.read_csv(ROOT/'results/case_studies/forecast_trajectories.csv',dtype={'CERT':str,'case_CERT':str})
    trajectory['availability_date']=pd.to_datetime(trajectory.availability_date)
    fig,axes=plt.subplots(2,2,figsize=(12,8.6));handles=None
    for ax,row in zip(axes.ravel(),register.itertuples()):
        g=trajectory.loc[trajectory.case_CERT.eq(row.CERT)]
        for family,color in [('xgboost','#31588e'),('gat_gru','#bc643c')]:
            for cert,style,label in [(row.CERT,'-',f'Failed bank: {NAMES[family]}'),(row.matched_survivor,'--',f'Matched bank: {NAMES[family]}')]:
                h=g.loc[g.CERT.eq(cert)&g.model.eq(family)].sort_values('availability_date')
                ax.plot(h.availability_date,h.probability,style,color=color,marker='o',ms=3,label=label)
            ax.axhline(test.loc[family,'threshold'],color=color,ls=':',lw=.9,label=f'{NAMES[family]} threshold')
        ax.axvline(pd.Timestamp(row.failure_date),color='black',ls='-.',lw=.9,label='FDIC failure date')
        ax.set_title(f'{row.name}\nCERT {row.CERT} | failure {row.failure_date}',fontsize=10)
        ax.set_ylabel('Failure probability')
        span=(pd.Timestamp(row.failure_date)-g.availability_date.min()).days
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3 if span<420 else 6))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'));ax.tick_params(axis='x',rotation=20)
        ax.grid(alpha=.2);handles=ax.get_legend_handles_labels()
    fig.suptitle('Proposed retrospective case packets: finance interpretation pending')
    fig.legend(*handles,loc='lower center',ncol=4,frameon=False,fontsize=8,bbox_to_anchor=(.5,-.015))
    fig.tight_layout(rect=(0,.07,1,.96));save(fig,'case_forecasts')

    # Extract exact existing explanations into the proposed finance packets, not new analyses.
    financial=[];edges=[]
    edge_table=pd.read_csv(ROOT/'results/explanations/edge_cases.csv.gz')
    for row in register.itertuples():
        for cert,role in [(row.CERT,'failed_bank'),(row.matched_survivor,'matched_bank')]:
            key=f"{cert}_{row.matching_report.replace('-','')}"
            f=primary.loc[primary.row_id.eq(key)].copy();f['case_CERT']=row.CERT;f['case_role']=role;financial.append(f)
            e=edge_table.loc[edge_table.row_id.eq(key)].copy();e['case_CERT']=row.CERT;e['case_role']=role;edges.append(e)
    pd.concat(financial).to_csv(ROOT/'results/case_studies/financial_explanation_packets.csv',index=False)
    pd.concat(edges).to_csv(ROOT/'results/case_studies/edge_explanation_packets.csv',index=False)
    print('Generated four data-derived figure pairs and exact proposed case explanation extracts')


if __name__=='__main__':main()
