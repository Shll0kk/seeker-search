import unicodedata


def fold_key(text: str) -> str:
    # Diacritics are dropped so a user typing "zurich" or "sao paulo" still
    # reaches "Zürich" / "São Paulo". The original spelling is kept for display;
    # only the lookup key is folded.
    decomposed = unicodedata.normalize("NFKD", text)
    without_marks = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    return without_marks.casefold().strip()
