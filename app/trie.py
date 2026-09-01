import heapq
from dataclasses import dataclass, field

from .normalize import fold_key


@dataclass
class Suggestion:
    label: str
    score: float
    key: str = ""


@dataclass
class TrieNode:
    children: dict[str, "TrieNode"] = field(default_factory=dict)
    entry: Suggestion | None = None
    # Best score found anywhere in this node's subtree (including entry). Kept up
    # to date on insert so prefix queries can walk the trie best-first and stop
    # once enough results are collected instead of exploring every descendant.
    subtree_best: float = float("-inf")


class SuggestionTrie:
    def __init__(self):
        self.root = TrieNode()
        self._size = 0

    def __len__(self):
        return self._size

    def insert(self, phrase: str, score: float, label: str | None = None):
        key = fold_key(phrase)
        if not key:
            return

        node = self.root
        node.subtree_best = max(node.subtree_best, score)
        for char in key:
            node = node.children.setdefault(char, TrieNode())
            node.subtree_best = max(node.subtree_best, score)

        if node.entry is None:
            self._size += 1
            node.entry = Suggestion(label or phrase, score, key)
        elif score > node.entry.score:
            # Same surface form inserted twice (e.g. a city name shared across
            # countries); keep the more popular one for ranking purposes.
            node.entry = Suggestion(label or phrase, score, key)

    def _descend(self, prefix_key: str) -> TrieNode | None:
        node = self.root
        for char in prefix_key:
            node = node.children.get(char)
            if node is None:
                return None
        return node

    def has_prefix(self, prefix: str) -> bool:
        return self._descend(fold_key(prefix)) is not None

    def rank_prefix(self, prefix: str, limit: int) -> list[Suggestion]:
        prefix_key = fold_key(prefix)
        if not prefix_key or limit <= 0:
            return []
        start = self._descend(prefix_key)
        if start is None:
            return []

        # Best-first search over the subtree. The heap mixes two kinds of items:
        # a node keyed by the best score anywhere beneath it, and a concrete
        # entry keyed by its own score. Because a node is always ordered ahead of
        # (or equal to) everything it contains, popping items until we have
        # `limit` entries yields exactly the top `limit` matches for the prefix.
        counter = 0
        frontier: list[tuple[float, int, str, object]] = [
            (-start.subtree_best, 0, "node", start)
        ]
        results: list[Suggestion] = []

        while frontier and len(results) < limit:
            _, _, kind, payload = heapq.heappop(frontier)
            if kind == "entry":
                results.append(payload)
                continue

            node: TrieNode = payload
            if node.entry is not None:
                counter += 1
                heapq.heappush(frontier, (-node.entry.score, counter, "entry", node.entry))
            for child in node.children.values():
                counter += 1
                heapq.heappush(frontier, (-child.subtree_best, counter, "node", child))

        return results

    def iter_entries(self):
        stack = [self.root]
        while stack:
            node = stack.pop()
            if node.entry is not None:
                yield node.entry
            stack.extend(node.children.values())
