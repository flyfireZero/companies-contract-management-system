from typing import Dict, Any
from contract_management.models.clause import ClauseType

STANDARD_CLAUSE_CATALOG: Dict[ClauseType, Dict[str, Any]] = {
    ClauseType.CONFIDENTIALITY: {
        "benchmark_summary": "Mutual non-disclosure with standard exceptions (public domain, legally required disclosure) lasting 3-5 years.",
        "preferred_posture": "Mutual protection with standard carve-outs and prompt notification of legal process.",
        "max_acceptable_risk": 30.0
    },
    ClauseType.LIMITATION_OF_LIABILITY: {
        "benchmark_summary": "Mutual cap equal to 12 months fees, mutual exclusion of indirect/consequential damages.",
        "preferred_posture": "Capped at 1x to 2x trailing 12-month fees with carve-outs for breach of confidentiality and willful misconduct.",
        "max_acceptable_risk": 40.0
    },
    ClauseType.INDEMNIFICATION: {
        "benchmark_summary": "Mutual defense and indemnification for third-party intellectual property infringement.",
        "preferred_posture": "Limited to IP claims, bodily injury, and gross negligence with prompt notice requirement.",
        "max_acceptable_risk": 35.0
    },
    ClauseType.TERMINATION: {
        "benchmark_summary": "Termination for convenience upon 30-60 days notice; termination for cause upon 30 days cure.",
        "preferred_posture": "Mutual convenience rights with reasonable notice and standard 30-day cure for breach.",
        "max_acceptable_risk": 30.0
    },
    ClauseType.PAYMENT_TERMS: {
        "benchmark_summary": "Net 30 days from invoice date with standard dispute resolution mechanism.",
        "preferred_posture": "Net 30 or Net 45; late fee capped at 1.0% per month.",
        "max_acceptable_risk": 25.0
    }
}
