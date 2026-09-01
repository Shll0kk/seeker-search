from app.fuzzy import closest_matches, levenshtein
from app.trie import Suggestion


def test_levenshtein_basic_edits():
    assert levenshtein("kitten", "sitting") == 3
    assert levenshtein("", "abc") == 3
    assert levenshtein("abc", "abc") == 0


def test_levenshtein_respects_max_distance_shortcut():
    # Return value only needs to exceed the budget, not be exact.
    assert levenshtein("aaaaaa", "bbbbbb", max_distance=2) == 3


def candidates():
    # keys are stored pre-folded by the trie, so tests pass folded keys too.
    return [
        Suggestion("Zurich, Switzerland", 400_000, key="zurich"),
        Suggestion("Zaria, Nigeria", 975_000, key="zaria"),
        Suggestion("Munich, Germany", 1_450_000, key="munich"),
        Suggestion("Munster, Germany", 300_000, key="munster"),
    ]


def test_typo_falls_back_to_closest_city():
    matches = closest_matches("zurick", candidates(), limit=3)
    assert matches[0].label == "Zurich, Switzerland"


def test_diacritics_are_folded_before_matching():
    matches = closest_matches("Zürich", candidates(), limit=3)
    assert matches[0].label == "Zurich, Switzerland"


def test_closer_edit_distance_outranks_larger_population():
    # "munich" is an exact fold match; "munster" is two edits away and far more
    # of a stretch, so distance wins over raw popularity ordering.
    matches = closest_matches("munich", candidates(), limit=3)
    assert matches[0].label == "Munich, Germany"


def test_no_candidate_within_budget_returns_empty():
    assert closest_matches("xxxxxx", candidates(), limit=3) == []
