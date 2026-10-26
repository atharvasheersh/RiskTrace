import torch
from risktrace.temporal import TemporalBaseline,deterministic


def seq(x,reset=None):
    t,n,_=x.shape
    return dict(x=x,ids=list(range(n)),active=torch.ones(t,n,dtype=torch.bool),
                reset=torch.zeros(t,n,dtype=torch.bool) if reset is None else reset)


def test_future_features_cannot_change_earlier_predictions_and_reset_discards_past():
    deterministic(11)
    m=TemporalBaseline(8,10)
    a=torch.randn(4,2,5);b=a.clone();b[-1]+=100
    with torch.no_grad():
        torch.testing.assert_close(m(seq(a))[:-1],m(seq(b))[:-1])
        reset=torch.zeros(4,2,dtype=torch.bool);reset[2]=True
        torch.testing.assert_close(m(seq(a,reset))[2:],m(seq(a[2:])) )
