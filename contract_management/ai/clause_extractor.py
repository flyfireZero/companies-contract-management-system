import re
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from contract_management.models.clause import ClauseType

@dataclass
class ExtractedClauseResult:
    clause_type: ClauseType
    title: str
    text: str
    section_ref: Optional[str]
    confidence_score: float
    is_standard: bool
    risk_score: float
    risk_explanation: str
    suggested_revision: Optional[str] = None

class ClauseExtractor:
    """
    Rule-based & Heuristic NLP engine to extract, classify, and evaluate legal clauses.
    """

    KEYWORD_MAP: Dict[ClauseType, List[str]] = {
        ClauseType.CONFIDENTIALITY: [
            r"confidential(ity)?", r"proprietary information", r"non-disclosure", r"trade secret"
        ],
        ClauseType.INDEMNIFICATION: [
            r"indemnif(y|ication|ies)", r"hold harmless", r"defend and hold"
        ],
        ClauseType.LIMITATION_OF_LIABILITY: [
            r"limitation of liability", r"aggregate liability", r"consequential damages",
            r"indirect damages", r"cap on liability"
        ],
        ClauseType.GOVERNING_LAW: [
            r"governing law", r"jurisdiction", r"choice of law", r"venue", r"dispute resolution"
        ],
        ClauseType.TERMINATION: [
            r"termination for cause", r"termination for convenience", r"right to terminate", r"notice of termination"
        ],
        ClauseType.PAYMENT_TERMS: [
            r"payment terms", r"fees and billing", r"invoic(e|ing)", r"net \d+", r"interest on late payments"
        ],
        ClauseType.INTELLECTUAL_PROPERTY: [
            r"intellectual property", r"ip ownership", r"work made for hire", r"patent", r"copyright"
        ],
        ClauseType.DATA_PRIVACY_GDPR: [
            r"data protection", r"gdpr", r"personal data", r"security incident", r"data breach"
        ],
        ClauseType.FORCE_MAJEURE: [
            r"force majeure", r"acts of god", r"events beyond reasonable control"
        ],
        ClauseType.WARRANTY: [
            r"warrant(y|ies)", r"as is", r"disclaimer of warranties", r"merchantability"
        ],
        ClauseType.NON_COMPETE: [
            r"non-compete", r"restrictive covenant", r"non-solicitation"
        ],
        ClauseType.AUDIT_RIGHTS: [
            r"right to audit", r"inspection of books", r"compliance audit"
        ]
    }

    def classify_text(self, text: str) -> Optional[Tuple[ClauseType, float]]:
        text_lower = text.lower()
        best_type = None
        highest_score = 0.0

        for ctype, patterns in self.KEYWORD_MAP.items():
            matches = sum(len(re.findall(p, text_lower)) for p in patterns)
            if matches > 0:
                score = min(0.95, 0.5 + 0.15 * matches)
                if score > highest_score:
                    highest_score = score
                    best_type = ctype

        if best_type and highest_score >= 0.5:
            return best_type, round(highest_score, 2)
        return None

    def analyze_clause_content(self, ctype: ClauseType, text: str) -> Tuple[bool, float, str, Optional[str]]:
        """
        Returns (is_standard, risk_score 0-100, risk_explanation, suggested_revision)
        """
        text_lower = text.lower()
        is_standard = True
        risk = 10.0
        explanation = "Standard commercial clause terms."
        revision = None

        if ctype == ClauseType.LIMITATION_OF_LIABILITY:
            if "unlimited liability" in text_lower or ("no cap" in text_lower and "liability" in text_lower):
                is_standard = False
                risk = 95.0
                explanation = "CRITICAL: Contract stipulates unlimited liability with no monetary cap."
                revision = "Total aggregate liability of either party shall be capped at the total fees paid in previous 12 months."
            elif "solely by vendor" in text_lower or "one-sided" in text_lower:
                risk = 70.0
                explanation = "Unilateral liability restriction favoring counterparty."
                revision = "Mutual limitation of liability applying equally to both parties."
            else:
                risk = 25.0

        elif ctype == ClauseType.INDEMNIFICATION:
            if "solely indemnify" in text_lower or "customer shall indemnify vendor against all claims" in text_lower:
                is_standard = False
                risk = 80.0
                explanation = "One-way indemnification with broad exposure."
                revision = "Mutual indemnification limited to third-party IP infringement and gross negligence."
            else:
                risk = 30.0

        elif ctype == ClauseType.TERMINATION:
            if "sole discretion" in text_lower and "without notice" in text_lower:
                is_standard = False
                risk = 85.0
                explanation = "Immediate unilateral termination without cure period."
                revision = "Either party may terminate upon 30 days written notice with a 30-day cure period for material breach."
            else:
                risk = 20.0

        elif ctype == ClauseType.DATA_PRIVACY_GDPR:
            if "without warranty" in text_lower and "security" in text_lower:
                risk = 75.0
                explanation = "Inadequate data protection assurances and warranty disclaimers."
                revision = "Vendor warrants compliance with GDPR, SOC 2 Type II, and standard contractual clauses (SCCs)."
            else:
                risk = 15.0

        return is_standard, risk, explanation, revision

    def extract_from_sections(self, sections: List[Any]) -> List[ExtractedClauseResult]:
        results = []
        for sec in sections:
            header_combined = f"{sec.title} {sec.content[:200]}"
            classification = self.classify_text(header_combined)
            if not classification:
                # Try entire content if short
                if len(sec.content) < 1500:
                    classification = self.classify_text(sec.content)

            if classification:
                ctype, conf = classification
                is_std, risk, expl, rev = self.analyze_clause_content(ctype, sec.content)
                results.append(ExtractedClauseResult(
                    clause_type=ctype,
                    title=sec.title if len(sec.title) > 3 else ctype.value.replace("_", " ").title(),
                    text=sec.content,
                    section_ref=sec.section_number,
                    confidence_score=conf,
                    is_standard=is_std,
                    risk_score=risk,
                    risk_explanation=expl,
                    suggested_revision=rev
                ))
        return results
