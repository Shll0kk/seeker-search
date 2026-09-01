from fastapi.testclient import TestClient

from app.api import app


def test_prefix_query_returns_ranked_matches():
    with TestClient(app) as ready:
        body = ready.get("/suggest", params={"q": "tok", "limit": 5}).json()

    assert body["mode"] == "prefix"
    assert body["matches"][0]["label"].startswith("Tokyo")
    assert all(
        a["population"] >= b["population"]
        for a, b in zip(body["matches"], body["matches"][1:])
    )


def test_typo_uses_fuzzy_fallback():
    with TestClient(app) as ready:
        body = ready.get("/suggest", params={"q": "tokio"}).json()

    assert body["mode"] == "fuzzy"
    assert body["matches"][0]["label"].startswith("Tokyo")


def test_blank_query_is_empty_none_mode():
    with TestClient(app) as ready:
        body = ready.get("/suggest", params={"q": "  "}).json()

    assert body["mode"] == "none"
    assert body["matches"] == []


def test_healthz_reports_index_size():
    with TestClient(app) as ready:
        body = ready.get("/healthz").json()

    assert body["status"] == "ok"
    assert body["indexed_cities"] > 1000
