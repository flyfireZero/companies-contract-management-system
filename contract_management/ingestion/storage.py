import hashlib
import os
import shutil
from pathlib import Path
from typing import Tuple
from contract_management.config import STORAGE_DIR

class DocumentStorage:
    """
    Manages secure, versioned, checksum-verified contract document persistence.
    """

    def __init__(self, storage_root: str = STORAGE_DIR):
        self.root = Path(storage_root)
        self.root.mkdir(parents=True, exist_ok=True)

    def compute_sha256(self, content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()

    def store_document(
        self,
        contract_number: str,
        filename: str,
        content: bytes,
        version: str = "1.0"
    ) -> Tuple[str, str]:
        """
        Stores document bytes under storage/{contract_number}/v{version}/{filename}
        Returns: (relative_saved_path, sha256_hash)
        """
        digest = self.compute_sha256(content)
        sanitized_num = "".join(c for c in contract_number if c.isalnum() or c in "-_")
        target_dir = self.root / sanitized_num / f"v{version}"
        target_dir.mkdir(parents=True, exist_ok=True)

        target_file = target_dir / filename
        with open(target_file, "wb") as f:
            f.write(content)

        rel_path = str(target_file.relative_to(self.root.parent))
        return rel_path, digest

    def read_document(self, rel_path: str) -> bytes:
        p = self.root.parent / rel_path
        if not p.exists():
            raise FileNotFoundError(f"Stored document not found: {rel_path}")
        with open(p, "rb") as f:
            return f.read()

    def verify_integrity(self, rel_path: str, expected_hash: str) -> bool:
        content = self.read_document(rel_path)
        actual = self.compute_sha256(content)
        return actual.lower() == expected_hash.lower()
