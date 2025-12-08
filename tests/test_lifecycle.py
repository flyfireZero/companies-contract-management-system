import pytest
from contract_management.models.contract import Contract, ContractStatus
from contract_management.lifecycle.state_machine import ContractStateMachine, TransitionError

def test_valid_lifecycle_progression():
    c = Contract(
        title="Enterprise SLA",
        contract_number="SLA-101",
        status=ContractStatus.DRAFT,
        effective_date="2026-01-01"
    )
    # DRAFT -> IN_REVIEW -> APPROVED -> PENDING_SIGNATURE -> ACTIVE
    ContractStateMachine.transition(c, ContractStatus.IN_REVIEW)
    assert c.status == ContractStatus.IN_REVIEW

    ContractStateMachine.transition(c, ContractStatus.APPROVED)
    assert c.status == ContractStatus.APPROVED

    ContractStateMachine.transition(c, ContractStatus.PENDING_SIGNATURE)
    assert c.status == ContractStatus.PENDING_SIGNATURE

    ContractStateMachine.transition(c, ContractStatus.ACTIVE)
    assert c.status == ContractStatus.ACTIVE

def test_invalid_lifecycle_transition():
    c = Contract(
        title="Draft Contract",
        contract_number="CNT-BAD-01",
        status=ContractStatus.DRAFT
    )
    # Cannot jump directly from DRAFT to ACTIVE
    with pytest.raises(TransitionError):
        ContractStateMachine.transition(c, ContractStatus.ACTIVE)

def test_activation_guard_requires_effective_date():
    c = Contract(
        title="Pending Agreement",
        contract_number="CNT-BAD-02",
        status=ContractStatus.PENDING_SIGNATURE,
        effective_date=None
    )
    with pytest.raises(TransitionError, match="effective date"):
        ContractStateMachine.transition(c, ContractStatus.ACTIVE)
