import re
import unicodedata
from num2words import num2words

class TextNormalizer:
    SYMBOL_MAP = {
        '∪': ' union ',
        '∩': ' intersection ',
        '∈': ' is in ',
        '∉': ' is not in ',
        '⊂': ' is a subset of ',
        '⊆': ' is a subset or equal to ',
        '⊃': ' is a superset of ',
        '⊇': ' is a superset or equal to ',
        '∅': ' the empty set ',
        '≠': ' does not equal ',
        '≈': ' is approximately ',
        '≤': ' is less than or equal to ',
        '≥': ' is greater than or equal to ',
        '∞': ' infinity ',
        '→': ' implies ',
        '—': ', ',
        '–': ', ',
        '=': ' equals ',
    }

    # ---------- helpers ----------

    @staticmethod
    def _speak_list_raw(items: str) -> str:
        parts = [p.strip() for p in items.split(',') if p.strip()]
        spoken = []
        for p in parts:
            if re.fullmatch(r'\d+', p):
                spoken.append(num2words(int(p)))
            else:
                spoken.append(p)
        return '; '.join(spoken)

    @staticmethod
    def _speak_set(match: re.Match) -> str:
        inner = match.group(1)

        # ordered pairs inside set → preserve commas
        if re.search(r'\([^()]+,[^()]+\)', inner):
            return f" the set of {inner} "

        spoken = TextNormalizer._speak_list_raw(inner)
        return f" the set of {spoken} "

    # ---------- main ----------

    @staticmethod
    def normalize_math_and_symbols(text: str) -> str:
        clean = text

        # --- Fix UTF-8 mojibake that has already been tokenized ---
        clean = re.sub(
        r'â\s*euro\s*sign\s*"?',
        '—',
        clean,
        flags=re.IGNORECASE
        )


        # 1. ALL CAPS → lowercase (PRACTICE, UNION, etc.)
        clean = re.sub(r'\b[A-Z]{4,}\b', lambda m: m.group(0).lower(), clean)

        # 2. Complement FIRST (before symbols/braces)
        clean = re.sub(
            r'\b([A-Za-z])\s*(?:\'|’|′|\^\s*c)\b',
            r'\1 complement',
            clean
        )

        # 3. Ellipses → pause
        clean = re.sub(r'\.{2,}', '.', clean)

        # 4. Set-builder notation
        clean = re.sub(
            r'\{\s*(.*?)\s*\|\s*(.*?)\s*\}',
            r' the set of \1 such that \2 ',
            clean
        )

        # 5. Cardinality |A|
        clean = re.sub(
            r'\|\s*(.*?)\s*\|',
            r' the number of elements in \1 ',
            clean
        )

        # 6. Explicit brace sets
        clean = re.sub(r'\{(.*?)\}', TextNormalizer._speak_set, clean)

        # 7. Protect ordered-pair commas
        clean = re.sub(
            r'\(([^()]+?)\)',
            lambda m: m.group(0).replace(',', '<<COMMA>>'),
            clean
        )

        # 8. Numeric lists → semicolon
        clean = re.sub(r'(?<=\d)\s*,\s*(?=\d)', '; ', clean)

        # restore ordered-pair commas
        clean = clean.replace('<<COMMA>>', ',')

        # 9. Arithmetic
        clean = re.sub(r'\+', ' plus ', clean)
        clean = re.sub(r'(?<=\d)\s*-\s*(?=\d)', ' minus ', clean)

        # 10. Cartesian product
        clean = re.sub(
            r'\b([A-Za-z])\s*×\s*([A-Za-z])\b',
            r'\1 cross \2',
            clean
        )
        clean = clean.replace('×', ' cross ')

        # 11. Symbol expansion
        for sym, rep in TextNormalizer.SYMBOL_MAP.items():
            clean = clean.replace(sym, rep)

        # 12. Numbers → words (ONCE, at the end)
        clean = re.sub(
            r'\b\d+\b',
            lambda m: num2words(int(m.group())),
            clean
        )

        # (x,one) -> x comma one
        clean = re.sub(
        r'\(\s*([^,()]+)\s*,\s*([^()]+)\s*\)',
        r'\1 comma \2',
        clean
        )

        # 13. Exponents (after numbers)
        clean = re.sub(
            r'\b(\w+)\s*\^\s*(\w+)\b',
            r'\1 to the power of \2',
            clean
        )

        # 14. Unicode fallback (last resort)
        out = []
        for ch in clean:
            if ord(ch) > 128 and not ch.isalnum():
                try:
                    out.append(f" {unicodedata.name(ch).lower()} ")
                except ValueError:
                    pass
            else:
                out.append(ch)

        clean = ''.join(out)

        # 15. Final cleanup
        clean = re.sub(r'\s*;\s*', '; ', clean)
        clean = re.sub(r'\s+', ' ', clean).strip()

        return clean