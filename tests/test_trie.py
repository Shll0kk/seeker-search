from app.trie import SuggestionTrie


def build(pairs):
    trie = SuggestionTrie()
    for label, score in pairs:
        trie.insert(label, score, label=label)
    return trie


def test_prefix_ranking_returns_top_scores_first():
    trie = build([
        ("Paris", 2_140_000),
        ("Parma", 195_000),
        ("Pareora", 1_100),
        ("Berlin", 3_500_000),
    ])

    ranked = [s.label for s in trie.rank_prefix("par", limit=2)]
    assert ranked == ["Paris", "Parma"]


def test_empty_prefix_yields_nothing():
    trie = build([("Paris", 10), ("Berlin", 20)])
    assert trie.rank_prefix("", limit=5) == []


def test_prefix_with_no_matches():
    trie = build([("Paris", 10), ("Berlin", 20)])
    assert trie.rank_prefix("xyz", limit=5) == []
    assert not trie.has_prefix("xyz")


def test_case_insensitive_lookup():
    trie = build([("São Paulo", 12_000_000)])
    assert [s.label for s in trie.rank_prefix("SÃO P", limit=5)] == ["São Paulo"]


def test_duplicate_surface_form_keeps_higher_score():
    trie = SuggestionTrie()
    trie.insert("Springfield", 117_000, label="Springfield, United States")
    trie.insert("Springfield", 60_000, label="Springfield, Canada")

    assert len(trie) == 1
    top = trie.rank_prefix("spring", limit=1)[0]
    assert top.label == "Springfield, United States"


def test_limit_is_respected_and_full_result_is_sorted():
    trie = build([(f"City{i}", i) for i in range(50)])
    ranked = trie.rank_prefix("city", limit=5)
    assert [s.score for s in ranked] == [49, 48, 47, 46, 45]
