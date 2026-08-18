from kubernetes_remediation_governor.verifier import HealthSnapshot, HealthVerifier


def test_verifier_accepts_healthy_post_action_state():
    baseline = HealthSnapshot(3, 3, 0.010, 100.0)
    after = HealthSnapshot(5, 5, 0.011, 110.0)
    result = HealthVerifier().verify(baseline, after)
    assert result.healthy is True


def test_verifier_flags_degraded_state():
    baseline = HealthSnapshot(3, 3, 0.010, 100.0)
    after = HealthSnapshot(4, 5, 0.050, 150.0)
    result = HealthVerifier().verify(baseline, after)
    assert result.healthy is False
    assert len(result.reasons) == 3
