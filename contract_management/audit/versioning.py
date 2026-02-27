import difflib
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class VersionDiff:
    clause_title: str
    has_changes: bool
    diff_lines: List[str]
    added_lines: int
    deleted_lines: int

class ContractVersionManager:
    """
    Tracks contract amendments, revisions, and semantic text diffs across contract drafts.
    """

    @classmethod
    def compute_clause_diff(cls, original_text: str, revised_text: str, title: str = "Clause") -> VersionDiff:
        orig_lines = original_text.splitlines()
        rev_lines = revised_text.splitlines()

        matcher = difflib.unified_diff(
            orig_lines, rev_lines,
            fromfile=f"original/{title}",
            tofile=f"revised/{title}",
            lineterm=""
        )
        diff_lines = list(matcher)
        added = sum(1 for line in diff_lines if line.startswith("+") and not line.startswith("+++"))
        deleted = sum(1 for line in diff_lines if line.startswith("-") and not line.startswith("---"))

        return VersionDiff(
            clause_title=title,
            has_changes=len(diff_lines) > 0,
            diff_lines=diff_lines,
            added_lines=added,
            deleted_lines=deleted
        )
