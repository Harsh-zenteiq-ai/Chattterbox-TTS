import re

def break_long_sentence(sent: str, max_chars: int) -> list[str]:
    if len(sent) <= max_chars:
        return [sent]
    parts = []
    remaining = sent
    while len(remaining) > max_chars:
        idx = remaining.rfind(',', 0, max_chars)
        if idx == -1:
            idx = remaining.rfind(' ', 0, max_chars)
        if idx == -1:
            idx = max_chars
        parts.append(remaining[:idx].strip())
        remaining = remaining[idx:].strip()
    if remaining:
        parts.append(remaining)
    return parts

def smart_split_text(text: str, max_chars: int = 250) -> list[str]:
    pattern = r'(?<!\d)(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|!)\s'
    raw_sentences = re.split(pattern, text)
    chunks = []
    current_chunk = ""

    for sent in raw_sentences:
        sent = sent.strip()
        if not sent:
            continue

        if len(sent) > max_chars:
            pieces = break_long_sentence(sent, max_chars)
        else:
            pieces = [sent]

        for piece in pieces:
            if not current_chunk:
                current_chunk = piece
            elif len(current_chunk) + 1 + len(piece) <= max_chars:
                current_chunk = current_chunk + " " + piece
            else:
                chunks.append(current_chunk)
                current_chunk = piece

    if current_chunk:
        chunks.append(current_chunk)
    return chunks
