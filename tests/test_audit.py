import numpy as np
from risktrace.audit import COL, FrozenPilot, feature_array, financially_valid, replace_groups, replay, synthetic_data


def test_real_dependencies_preserve_unchanged_quality_and_accounting():
    data = synthetic_data()
    r, donor = data.raw[0, 0], data.raw[0, 1]
    edited = replace_groups(r, donor, ["asset_mix"])
    assert financially_valid(edited)
    assert np.isclose(feature_array(edited)[4], feature_array(r)[4])
    assert edited[COL["EQTOT"]] == r[COL["EQTOT"]]
    all_changed = replace_groups(r, donor, ["capital", "asset_mix", "credit_quality"])
    assert financially_valid(all_changed)
    broken = all_changed.copy(); broken[COL["LIAB"]] += 1000
    assert not financially_valid(broken)


def test_identity_and_exogenous_controls_do_not_create_topology_effects():
    d = synthetic_data()
    for kind, k in [("none", 0), ("exogenous", 3), ("random", 3), ("feature", 3)]:
        model = FrozenPilot(d, kind, k, 11)
        before = model.fingerprint()
        r = d.raw[8, 0]
        assert np.isclose(model.edited_prediction(r, 0, 8, True)[0], model.pred[-1, 0])
        if kind != "feature":
            changed = replace_groups(r, d.raw[8, 1], ["capital", "asset_mix"])
            assert model.edited_prediction(changed, 0, 8, False)[0] == model.edited_prediction(changed, 0, 8, True)[0]
        assert model.fingerprint() == before


def test_feature_dependency_rebuild_changes_edges_for_known_synthetic_edit():
    d = synthetic_data()
    model = FrozenPilot(d, "feature", 3, 11)
    original = d.raw[11, 0].copy()
    changed = replace_groups(original, d.raw[11, 1], ["capital", "asset_mix", "credit_quality"])
    a = model.edited_prediction(changed, 0, 11, False)
    b = model.edited_prediction(changed, 0, 11, True)
    assert b[1] > 0
    assert abs(a[0] - b[0]) > 1e-8
    np.testing.assert_array_equal(d.raw[11, 0], original)


def test_replay_propagates_past_changes_and_resets_missing_history():
    r = np.zeros((3, 1, 1)); r[0, 0, 0] = 1
    active = np.ones((3, 1), bool)
    assert replay(r, active)[-1, 0, 0] == .125
    active[1] = False
    assert replay(r, active)[-1, 0, 0] == 0
