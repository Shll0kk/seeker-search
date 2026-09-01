import { useEffect, useRef, useState } from "react";
import type { KeyboardEvent } from "react";
import { SearchBar } from "./components/SearchBar";
import { SuggestionList } from "./components/SuggestionList";
import { fetchSuggestions } from "./lib/api";
import { useDebouncedValue } from "./lib/useDebouncedValue";
import type { RequestStatus, Suggestion, SuggestMode } from "./types";

const DEBOUNCE_MS = 120;

interface QueryResult {
  query: string;
  matches: Suggestion[];
  mode: SuggestMode;
  failed: boolean;
}

const EMPTY_RESULT: QueryResult = { query: "", matches: [], mode: "none", failed: false };

export default function App() {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState<QueryResult>(EMPTY_RESULT);
  const [isOpen, setIsOpen] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);

  const inputRef = useRef<HTMLInputElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const debouncedQuery = useDebouncedValue(query, DEBOUNCE_MS);
  const trimmedQuery = debouncedQuery.trim();

  useEffect(() => {
    if (!trimmedQuery) return;

    const controller = new AbortController();

    fetchSuggestions(trimmedQuery, controller.signal)
      .then((response) => {
        setResult({
          query: trimmedQuery,
          matches: response.matches,
          mode: response.mode,
          failed: false,
        });
        setActiveIndex(-1);
      })
      .catch((error: unknown) => {
        if (error instanceof DOMException && error.name === "AbortError") return;
        setResult({ query: trimmedQuery, matches: [], mode: "none", failed: true });
      });

    return () => controller.abort();
  }, [trimmedQuery]);

  useEffect(() => {
    function handlePointerDown(event: MouseEvent) {
      if (!containerRef.current?.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handlePointerDown);
    return () => document.removeEventListener("mousedown", handlePointerDown);
  }, []);

  const hasQuery = trimmedQuery.length > 0;
  const isResultCurrent = hasQuery && result.query === trimmedQuery;
  const matches = hasQuery && result.query ? result.matches : [];
  const mode = hasQuery && result.query ? result.mode : "none";

  let status: RequestStatus = "idle";
  if (hasQuery) {
    if (!isResultCurrent) status = "loading";
    else status = result.failed ? "error" : "done";
  }

  const canNavigate = isOpen && matches.length > 0;

  function handleKeyDown(event: KeyboardEvent<HTMLInputElement>) {
    if (event.key === "Escape") {
      setIsOpen(false);
      return;
    }
    if (!canNavigate) return;

    if (event.key === "ArrowDown") {
      event.preventDefault();
      setActiveIndex((current) => (current + 1) % matches.length);
    } else if (event.key === "ArrowUp") {
      event.preventDefault();
      setActiveIndex((current) => (current <= 0 ? matches.length - 1 : current - 1));
    } else if (event.key === "Enter" && activeIndex >= 0) {
      event.preventDefault();
      selectSuggestion(matches[activeIndex]);
    }
  }

  function selectSuggestion(suggestion: Suggestion) {
    setQuery(suggestion.label.split(",")[0]);
    setIsOpen(false);
    setActiveIndex(-1);
    inputRef.current?.focus();
  }

  function handleQueryChange(value: string) {
    setQuery(value);
    setIsOpen(true);
  }

  return (
    <main className="min-h-screen bg-neutral-50 px-4 pt-16 text-neutral-900 sm:pt-28">
      <div className="mx-auto w-full max-w-xl">
        <header className="mb-6">
          <h1 className="text-lg font-semibold tracking-tight">Seeker</h1>
          <p className="mt-1 text-sm text-neutral-500">
            City name autocomplete, ranked by population.
          </p>
        </header>

        <div ref={containerRef} className="relative">
          <SearchBar
            value={query}
            onChange={handleQueryChange}
            onKeyDown={handleKeyDown}
            isLoading={status === "loading"}
            inputRef={inputRef}
          />
          {isOpen && (
            <SuggestionList
              status={status}
              matches={matches}
              mode={mode}
              query={trimmedQuery}
              activeIndex={activeIndex}
              onSelect={selectSuggestion}
            />
          )}
        </div>
      </div>
    </main>
  );
}
