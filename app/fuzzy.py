from .normalize import fold_key
from .trie import Suggestion


def levenshtein(a: str, b: str, max_distance: int | None = None) -> int:
    if a == b:
        return 0
    if len(a) < len(b):
        a, b = b, a
    if not b:
        return len(a)
    if max_distance is not None and len(a) - len(b) > max_distance:
        return max_distance + 1

    previous = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        current = [i]
        row_best = i
        for j, cb in enumerate(b, start=1):
            cost = 0 if ca == cb else 1
            value = min(
                previous[j] + 1,
                current[j - 1] + 1,
                previous[j - 1] + cost,
            )
            current.append(value)
            row_best = min(row_best, value)
        # Once every cell in a row exceeds the budget the distance can only grow,
        # so bail out rather than finishing the matrix.
        if max_distance is not None and row_best > max_distance:
            return max_distance + 1
        previous = current

    return previous[-1]


def _distance_budget(query: str) -> int:
    # Allow roughly one edit per three characters, capped at 3. That covers the
    # common typo classes (a wrong letter, a dropped letter, a transposition
    # reads as two edits) without letting a 4-letter query match half the trie.
    return min(3, max(1, len(query) // 3))


def closest_matches(query: str, candidates, limit: int) -> list[Suggestion]:
    key = fold_key(query)
    budget = _distance_budget(key)

    scored: list[tuple[int, float, Suggestion]] = []
    for entry in candidates:
        target = entry.key or fold_key(entry.label)
        distance = levenshtein(key, target, max_distance=budget)
        if distance <= budget:
            scored.append((distance, -entry.score, entry))

    scored.sort(key=lambda item: (item[0], item[1]))
    return [entry for _, _, entry in scored[:limit]]
