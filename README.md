# Seeker

Seeker is a prefix autocomplete service for world city names, ranked by
population, with a Levenshtein fallback for typos. It builds an in-memory trie
at startup and serves suggestions over HTTP.

Cities and their populations come from the UN Statistics Division "Population of
capital cities and cities of 100,000 or more inhabitants" dataset
(`data/unsd-citypopulation-year-both.csv`, via the datahub.io `population-city`
package), which is about 5,000 cities after deduplication.

## Running it

Requires Python 3.10+. The frontend build needs Node 20.19+ (or 22.12+).

Backend (API + prebuilt search page):

```
pip install -r requirements.txt
uvicorn app.api:app --reload
```

Then open http://127.0.0.1:8000/ for the search page, or call the API directly:

```
GET /suggest?q=lond&limit=10
{
  "query": "lond",
  "mode": "prefix",
  "matches": [
    {"label": "London, United Kingdom ...", "population": 8135667},
    {"label": "Londrina, Brazil", "population": 555965}
  ]
}
```

`mode` is `prefix` when the trie had matches, `fuzzy` when it fell back to
edit-distance, and `none` when nothing was close enough.

`GET /healthz` returns the number of indexed cities.

### Frontend

The search page lives in `frontend/` (React + Vite + TypeScript + Tailwind). The
checked-in `web/index.html` is its build output.

```
cd frontend
npm install
npm run dev      # http://localhost:5173, proxies /suggest and /healthz to :8000
```

Point the dev proxy elsewhere with `SEEKER_API_URL` if the backend is not on
port 8000.

```
npm run build    # bundles into a single web/index.html served by the backend
```

`npm run build` inlines the JS and CSS into one `web/index.html`, so the FastAPI
app can serve the page directly without any static-file configuration.

## Tests

```
pytest
```

Covers trie insert / prefix ranking / edge cases, the Levenshtein
implementation and its fallback behaviour, and the HTTP layer.

## Layout

| Path | Responsibility |
| --- | --- |
| `app/trie.py` | `SuggestionTrie` and its best-first top-N prefix search |
| `app/fuzzy.py` | bounded Levenshtein and the closest-match fallback |
| `app/dataset.py` | parsing/deduping the UN CSV into `CityRecord`s |
| `app/normalize.py` | diacritic-folding for lookup keys |
| `app/api.py` | FastAPI app, index build on startup, `/suggest` |
| `frontend/` | React/Vite/Tailwind search UI (source) |
| `web/index.html` | built frontend, served at `/` |

## Design notes

The trie is keyed on diacritic-folded city names; each terminal node holds the
display label ("City, Country") and the population, which doubles as the
popularity score. Every node also caches the best score in its subtree, so a
prefix query is a best-first walk over a heap ordered by that cached score and
stops as soon as it has collected N entries rather than enumerating the whole
subtree. For this dataset a prefix lookup is well under a millisecond.

When a prefix has no trie matches the query is almost certainly a typo, so the
service scans the indexed names and keeps those within a small edit-distance
budget (`len(query) // 3`, capped at 3) of the input, ranked by distance then
population. A linear scan with an early-exit Levenshtein is fast enough at this
size (~5k names, single-digit milliseconds); a BK-tree or n-gram index would be
the next step if the dataset grew by an order of magnitude.

The frontend is a small React app: it debounces keystrokes, aborts the previous
`/suggest` request when a new one starts, keeps the last results visible while
the next set loads, and highlights the matched prefix on each row.

## License

MIT. See [LICENSE](LICENSE).
