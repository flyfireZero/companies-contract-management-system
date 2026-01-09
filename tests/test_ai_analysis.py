from pathlib import Path
from contract_management.ingestion.parser import DocumentParser
from contract_management.ai.clause_extractor import ClauseExtractor
from contract_management.ai.obligation_miner import ObligationMiner
from contract_management.models.clause import ClauseType

def test_parse_and_extract_msa_clauses():
    parser = DocumentParser()
    extractor = ClauseExtractor()
    msa_file = Path("data/samples/sample_msa.txt")
    doc = parser.parse_file(str(msa_file))

    assert len(doc.sections) >= 5
    clauses = extractor.extract_from_sections(doc.sections)

    extracted_types = {c.clause_type for c in clauses}
    assert ClauseType.CONFIDENTIALITY in extracted_types
    assert ClauseType.LIMITATION_OF_LIABILITY in extracted_types
    assert ClauseType.INDEMNIFICATION in extracted_types
    assert ClauseType.PAYMENT_TERMS in extracted_types
    assert ClauseType.TERMINATION in extracted_types

def test_high_risk_detection():
    parser = DocumentParser()
    extractor = ClauseExtractor()
    risk_file = Path("data/samples/sample_high_risk_agreement.txt")
    doc = parser.parse_file(str(risk_file))

    clauses = extractor.extract_from_sections(doc.sections)
    high_risks = [c for c in clauses if c.risk_score >= 70.0]
    assert len(high_risks) >= 2

    # Verify suggested revision is present for high risk clauses
    for hr in high_risks:
        assert hr.suggested_revision is not None
        assert not hr.is_standard

def test_obligation_miner():
    miner = ObligationMiner()
    sample_text = "Vendor shall invoice Customer on a monthly basis. Customer shall pay within Net 30 days. Vendor will provide the Q2 security audit report by June 15, 2026."
    obs = miner.mine(contract_id=1, text=sample_text)
    assert len(obs) >= 2
    types = [o.obligation_type.value for o in obs]
    assert "PAYMENT" in types
