import json
import pytest
from risktrace.core import config
from risktrace.data import FDIC


def test_pagination_checks_source_total_and_retains_all_rows(monkeypatch, tmp_path):
    c = FDIC(config(), tmp_path)
    pages = iter([dict(meta=dict(total=3), data=[dict(data={"CERT": 1}), dict(data={"CERT": 2})]),
                  dict(meta=dict(total=3), data=[dict(data={"CERT": 3})])])
    monkeypatch.setattr(c, "page", lambda *args: next(pages))
    assert len(c.fetch("financials", "", ["CERT"])) == 3
    pages = iter([dict(meta=dict(total=2), data=[dict(data={"CERT": 1})]),
                  dict(meta=dict(total=3), data=[dict(data={"CERT": 2})])])
    monkeypatch.setattr(c, "page", lambda *args: next(pages))
    with pytest.raises(ValueError, match="total changed"):
        c.fetch("financials", "", ["CERT"])


def test_cache_tampering_is_detected(tmp_path):
    import hashlib
    import urllib.parse
    c = FDIC(config(), tmp_path)
    params = {"limit": 1}
    url = c.spec["api"]["base"] + "/financials?" + urllib.parse.urlencode(params)
    key = hashlib.sha256(url.encode()).hexdigest()[:24]
    p = tmp_path / "data/raw" / f"financials_{key}.json"
    p.parent.mkdir(parents=True)
    p.write_text("tampered")
    p.with_suffix(".meta.json").write_text(json.dumps({"sha256": "wrong"}))
    with pytest.raises(ValueError, match="checksum mismatch"):
        c.page("financials", params)
