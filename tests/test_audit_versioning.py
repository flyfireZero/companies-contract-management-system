from contract_management.audit.logger import AuditLogger
from contract_management.audit.versioning import ContractVersionManager
from contract_management.models.audit import AuditAction

def test_audit_logger_chain_integrity(memory_db):
    logger = AuditLogger(memory_db)
    e1 = logger.log(AuditAction.CONTRACT_CREATED, "Contract created: MSA-01", contract_id=1)
    e2 = logger.log(AuditAction.STATUS_TRANSITION, "Moved to IN_REVIEW", contract_id=1, previous_state="DRAFT", new_state="IN_REVIEW")
    e3 = logger.log(AuditAction.RISK_ASSESSED, "Risk score computed: 25.0", contract_id=1)

    assert e1.id == 1
    assert e2.id == 2
    assert e3.id == 3
    assert logger.verify_chain() is True

def test_version_clause_diff():
    v1 = "The liability cap shall be $1,000,000 for all claims."
    v2 = "The aggregate liability cap shall not exceed $2,500,000 for any and all claims."
    diff = ContractVersionManager.compute_clause_diff(v1, v2, "Liability")

    assert diff.has_changes is True
    assert diff.added_lines > 0
    assert diff.deleted_lines > 0
