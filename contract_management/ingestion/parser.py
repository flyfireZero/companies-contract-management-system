import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any, Optional

@dataclass
class DocumentSection:
    section_number: Optional[str]
    title: str
    content: str
    start_char: int
    end_char: int

@dataclass
class ParsedDocument:
    raw_text: str
    title: str
    sections: List[DocumentSection] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    word_count: int = 0

class DocumentParser:
    """
    Parses plain text, markdown, and contract documents into structured sections.
    """

    SECTION_PATTERN = re.compile(
        r'^(?:(?:Section|Article|Clause)\s+([0-9IVX]+(?:\.[0-9]+)*)[:.]?\s*([^\r\n]+)|([0-9]+(?:\.[0-9]+)*)\.?\s+([A-Z][^\r\n]+))$',
        re.MULTILINE
    )

    def parse_text(self, text: str, fallback_title: str = "Untitled Agreement") -> ParsedDocument:
        lines = text.strip().splitlines()
        title = fallback_title
        if lines:
            first_line = lines[0].strip("# \t*")
            if len(first_line) > 3:
                title = first_line

        sections: List[DocumentSection] = []
        matches = list(self.SECTION_PATTERN.finditer(text))

        if not matches:
            paragraphs = re.split(r'\n{2,}', text)
            current_offset = 0
            for i, p in enumerate(paragraphs):
                p_clean = p.strip()
                if not p_clean:
                    continue
                first_sentence = p_clean.split(".")[0][:60]
                sec = DocumentSection(
                    section_number=str(i + 1),
                    title=first_sentence,
                    content=p_clean,
                    start_char=current_offset,
                    end_char=current_offset + len(p_clean)
                )
                sections.append(sec)
                current_offset += len(p) + 2
        else:
            for idx, match in enumerate(matches):
                sec_num = match.group(1) or match.group(3) or f"Sec-{idx+1}"
                sec_title = (match.group(2) or match.group(4) or "General").strip()
                start_pos = match.start()
                end_pos = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
                sec_content = text[match.end():end_pos].strip()

                sections.append(DocumentSection(
                    section_number=sec_num,
                    title=sec_title,
                    content=sec_content,
                    start_char=start_pos,
                    end_char=end_pos
                ))

        word_count = len(text.split())
        return ParsedDocument(
            raw_text=text,
            title=title,
            sections=sections,
            word_count=word_count,
            metadata={"sections_count": len(sections), "word_count": word_count}
        )

    def parse_file(self, file_path: str) -> ParsedDocument:
        p = Path(file_path)
        if not p.exists():
            raise FileNotFoundError(f"Document file not found: {file_path}")
        with open(p, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        return self.parse_text(content, fallback_title=p.stem.replace("_", " ").title())
