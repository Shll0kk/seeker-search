export type SuggestMode = "prefix" | "fuzzy" | "none";

export type RequestStatus = "idle" | "loading" | "done" | "error";

export interface Suggestion {
  label: string;
  population: number;
}

export interface SuggestResponse {
  query: string;
  mode: SuggestMode;
  matches: Suggestion[];
}
