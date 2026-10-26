import numpy as np
import pandas as pd
from risktrace.metrics import alarm_threshold,prediction_metrics


def test_ties_cannot_exceed_requested_false_alarm_rate():
    y=np.r_[np.zeros(100),1]
    p=np.r_[np.full(100,.2),.9]
    threshold=alarm_threshold(y,p,.01)
    assert ((p[y==0]>threshold).mean())<=.01
    assert p[-1]>threshold


def test_event_warning_uses_available_date_and_deduplicates_quarters():
    f=pd.DataFrame(dict(CERT=["1","1","2"],y=[1,1,0],probability=[.9,.8,.01],
                        availability_date=["2020-06-01","2020-09-01","2020-06-01"],failure_date=["2020-12-01","2020-12-01",None]))
    m,w=prediction_metrics(f,.5)
    assert m["distinct_positive_banks"]==1 and m["event_recall"]==1
    assert w[0]["warning_days"]==183
