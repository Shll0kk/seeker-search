import type { SuggestResponse } from "../types";

const SUGGEST_LIMIT = 10;

export async function fetchSuggestions(
  query: string,
  signal?: AbortSignal,
): Promise<SuggestResponse> {
  const params = new URLSearchParams({ q: query, limit: String(SUGGEST_LIMIT) });
  const response = await fetch(`/suggest?${params}`, { signal });
  if (!response.ok) {
    throw new Error(`suggest request failed with status ${response.status}`);
  }
  return response.json();
}
