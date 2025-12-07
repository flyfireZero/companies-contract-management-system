from typing import Dict, Set, Optional, Tuple
from contract_management.models.contract import Contract, ContractStatus

class TransitionError(Exception):
    """Raised when an invalid contract status transition is attempted."""
    pass

class ContractStateMachine:
    """
    Governs strict enterprise state transitions for contracts.
    
    Valid workflow:
    DRAFT -> IN_REVIEW
    IN_REVIEW -> DRAFT (rejected/revisions needed)
    IN_REVIEW -> APPROVED
    APPROVED -> PENDING_SIGNATURE
    PENDING_SIGNATURE -> ACTIVE
    ACTIVE -> EXPIRING_SOON
    ACTIVE -> EXPIRED
    ACTIVE -> TERMINATED
    EXPIRING_SOON -> RENEWED
    EXPIRING_SOON -> EXPIRED
    EXPIRING_SOON -> TERMINATED
    RENEWED -> ACTIVE
    """

    VALID_TRANSITIONS: Dict[ContractStatus, Set[ContractStatus]] = {
        ContractStatus.DRAFT: {ContractStatus.IN_REVIEW, ContractStatus.TERMINATED},
        ContractStatus.IN_REVIEW: {ContractStatus.DRAFT, ContractStatus.APPROVED, ContractStatus.TERMINATED},
        ContractStatus.APPROVED: {ContractStatus.PENDING_SIGNATURE, ContractStatus.IN_REVIEW, ContractStatus.TERMINATED},
        ContractStatus.PENDING_SIGNATURE: {ContractStatus.ACTIVE, ContractStatus.IN_REVIEW, ContractStatus.TERMINATED},
        ContractStatus.ACTIVE: {ContractStatus.EXPIRING_SOON, ContractStatus.EXPIRED, ContractStatus.TERMINATED, ContractStatus.RENEWED},
        ContractStatus.EXPIRING_SOON: {ContractStatus.RENEWED, ContractStatus.EXPIRED, ContractStatus.TERMINATED},
        ContractStatus.EXPIRED: {ContractStatus.RENEWED},
        ContractStatus.RENEWED: {ContractStatus.ACTIVE},
        ContractStatus.TERMINATED: set(),
    }

    @classmethod
    def can_transition(cls, current_status: ContractStatus, target_status: ContractStatus) -> bool:
        if current_status == target_status:
            return True
        allowed = cls.VALID_TRANSITIONS.get(current_status, set())
        return target_status in allowed

    @classmethod
    def transition(
        cls,
        contract: Contract,
        target_status: ContractStatus,
        reason: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        if not cls.can_transition(contract.status, target_status):
            msg = f"Illegal transition from '{contract.status.value}' to '{target_status.value}' for contract '{contract.contract_number}'."
            raise TransitionError(msg)

        # Transition guard validations
        if target_status == ContractStatus.ACTIVE:
            if not contract.effective_date:
                raise TransitionError("Cannot activate contract without an effective date.")
        
        contract.status = target_status
        return True, reason
