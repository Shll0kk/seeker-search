import { matchedPrefixLength } from "../lib/highlight";
import type { RequestStatus, Suggestion, SuggestMode } from "../types";

interface SuggestionListProps {
  status: RequestStatus;
  matches: Suggestion[];
  mode: SuggestMode;
  query: string;
  activeIndex: number;
  onSelect: (suggestion: Suggestion) => void;
}

export function SuggestionList({
  status,
  matches,
  mode,
  query,
  activeIndex,
  onSelect,
}: SuggestionListProps) {
  const hasResults = matches.length > 0;
  const showEmptyState = status === "done" && !hasResults;
  const showErrorState = status === "error" && !hasResults;

  if (!hasResults && !showEmptyState && !showErrorState) {
    return null;
  }

  return (
    <div className="absolute z-10 mt-2 w-full origin-top animate-suggestions-in overflow-hidden rounded-xl border border-neutral-200 bg-white shadow-lg">
      {mode === "fuzzy" && hasResults && (
        <p className="border-b border-neutral-100 px-4 py-2 text-xs text-neutral-400">
          No exact match. Showing closest names.
        </p>
      )}

      {showEmptyState && (
        <p className="px-4 py-3 text-sm text-neutral-500">
          No cities match "{query.trim()}".
        </p>
      )}

      {showErrorState && (
        <p className="px-4 py-3 text-sm text-neutral-500">
          Could not reach the suggestion service.
        </p>
      )}

      {hasResults && (
        <ul>
          {matches.map((suggestion, index) => (
            <SuggestionRow
              key={suggestion.label}
              suggestion={suggestion}
              query={query}
              isActive={index === activeIndex}
              onSelect={onSelect}
            />
          ))}
        </ul>
      )}
    </div>
  );
}

interface SuggestionRowProps {
  suggestion: Suggestion;
  query: string;
  isActive: boolean;
  onSelect: (suggestion: Suggestion) => void;
}

function SuggestionRow({ suggestion, query, isActive, onSelect }: SuggestionRowProps) {
  const matchLength = matchedPrefixLength(suggestion.label, query);
  const matchedText = suggestion.label.slice(0, matchLength);
  const remainingText = suggestion.label.slice(matchLength);

  return (
    <li>
      <button
        type="button"
        onMouseDown={(event) => event.preventDefault()}
        onClick={() => onSelect(suggestion)}
        className={`flex w-full items-baseline justify-between gap-3 px-4 py-2.5 text-left text-sm ${
          isActive ? "bg-neutral-100" : "bg-white"
        }`}
      >
        <span className="truncate">
          {matchedText && <span className="font-semibold text-neutral-900">{matchedText}</span>}
          <span className={matchedText ? "text-neutral-500" : "text-neutral-900"}>
            {remainingText}
          </span>
        </span>
        <span className="shrink-0 tabular-nums text-xs text-neutral-400">
          {suggestion.population.toLocaleString()}
        </span>
      </button>
    </li>
  );
}
