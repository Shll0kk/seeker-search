function fold(text: string): string {
  return text
    .normalize("NFKD")
    .replace(/\p{Diacritic}/gu, "")
    .toLowerCase();
}

export function matchedPrefixLength(label: string, query: string): number {
  const foldedQuery = fold(query.trim());
  if (!foldedQuery) return 0;

  const foldedLabel = fold(label);
  if (foldedLabel.length !== label.length) return 0;

  let matched = 0;
  while (
    matched < foldedQuery.length &&
    matched < foldedLabel.length &&
    foldedLabel[matched] === foldedQuery[matched]
  ) {
    matched += 1;
  }

  return matched === foldedQuery.length ? matched : 0;
}
