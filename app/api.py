from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel

from .dataset import load_cities
from .fuzzy import closest_matches
from .trie import SuggestionTrie

MAX_RESULTS = 10
WEB_DIR = Path(__file__).resolve().parent.parent / "web"

index = SuggestionTrie()
_all_entries: list = []


def build_index() -> None:
    cities = load_cities()
    fresh = SuggestionTrie()
    for city in cities:
        fresh.insert(city.name, float(city.population), label=city.display_label)

    global index, _all_entries
    index = fresh
    _all_entries = list(fresh.iter_entries())


@asynccontextmanager
async def lifespan(_: FastAPI):
    build_index()
    yield


app = FastAPI(title="Seeker", lifespan=lifespan)


class Match(BaseModel):
    label: str
    population: int


class SuggestResponse(BaseModel):
    query: str
    mode: str  # "prefix", "fuzzy", or "none"
    matches: list[Match]


@app.get("/suggest", response_model=SuggestResponse)
def suggest(q: str = Query(default=""), limit: int = Query(default=MAX_RESULTS, ge=1, le=50)):
    prefix = q.strip()
    if not prefix:
        return SuggestResponse(query=q, mode="none", matches=[])

    ranked = index.rank_prefix(prefix, limit)
    if ranked:
        mode = "prefix"
    else:
        ranked = closest_matches(prefix, _all_entries, limit)
        mode = "fuzzy" if ranked else "none"

    matches = [Match(label=s.label, population=int(s.score)) for s in ranked]
    return SuggestResponse(query=q, mode=mode, matches=matches)


@app.get("/healthz")
def healthz():
    return {"status": "ok", "indexed_cities": len(index)}


@app.get("/")
def home():
    return FileResponse(WEB_DIR / "index.html")
