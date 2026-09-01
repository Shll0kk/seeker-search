import csv
from dataclasses import dataclass
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "unsd-citypopulation-year-both.csv"

# The UN dataset reports population for both "City proper" and "Urban
# agglomeration". Preferring city-proper figures keeps the popularity score
# comparable across cities; agglomeration is only used when it's all we have.
_AREA_PREFERENCE = {"City proper": 2, "Urban agglomeration": 1}


@dataclass(frozen=True)
class CityRecord:
    name: str
    country: str
    population: int

    @property
    def display_label(self) -> str:
        return f"{self.name}, {self.country}"


def load_cities(path: Path = DATA_FILE) -> list[CityRecord]:
    # One city appears many times (per census year, per area definition). Keep a
    # single row per (country, city): most recent year wins, then the preferred
    # area type, then the larger figure.
    best: dict[tuple[str, str], tuple[int, int, int]] = {}

    with path.open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            city = (row.get("City") or "").strip()
            country = (row.get("Country or Area") or "").strip()
            population = _parse_population(row.get("Value"))
            if not city or not country or population is None:
                continue

            year = _parse_year(row.get("Year"))
            area_rank = _AREA_PREFERENCE.get((row.get("City type") or "").strip(), 0)
            candidate = (year, area_rank, population)

            identity = (country.casefold(), _normalize_city(city))
            if identity not in best or candidate > best[identity][0]:
                best[identity] = (candidate, CityRecord(_titlecase(city), country, population))

    return [record for _, record in best.values()]


def _parse_population(raw: str | None) -> int | None:
    if not raw:
        return None
    try:
        value = int(round(float(raw)))
    except ValueError:
        return None
    return value if value > 0 else None


def _parse_year(raw: str | None) -> int:
    try:
        return int(raw)
    except (TypeError, ValueError):
        return 0


def _normalize_city(city: str) -> str:
    # Some rows annotate the city with a former or alternate name in parens;
    # collapse those so "Vanadzor (Kirovakan)" and "Vanadzor" don't split.
    head = city.split("(", 1)[0].strip()
    return (head or city).casefold()


def _titlecase(city: str) -> str:
    cleaned = city.split("(", 1)[0].strip() or city
    if cleaned.isupper() or cleaned.islower():
        return cleaned.title()
    return cleaned
