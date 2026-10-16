"""Shared helpers: CMS catalog lookup and DuckDB loading."""
from __future__ import annotations

import logging
import re
from pathlib import Path

import duckdb
import requests
import yaml

log = logging.getLogger("ingest")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

ROOT = Path(__file__).resolve().parent
SOURCES = yaml.safe_load((ROOT / "sources.yml").read_text())

# Generic-name patterns kept at ingest. This is broader than the dbt seed on purpose;
# final classification happens in dbt.
DIABETES_PATTERNS = [
    "semaglutide", "tirzepatide", "dulaglutide", "liraglutide", "exenatide", "lixisenatide",
    "metformin", "gliflozin", "gliptin", "glipizide", "glimepiride", "glyburide",
    "pioglitazone", "insulin",
]


def connect(db_path: str) -> duckdb.DuckDBPyConnection:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(db_path)
    con.execute("INSTALL httpfs; LOAD httpfs;")
    con.execute("CREATE SCHEMA IF NOT EXISTS raw;")
    return con


_catalog_cache: dict | None = None


def cms_catalog() -> dict:
    global _catalog_cache
    if _catalog_cache is None:
        log.info("Fetching CMS catalog %s", SOURCES["cms_catalog_url"])
        r = requests.get(SOURCES["cms_catalog_url"], timeout=120)
        r.raise_for_status()
        _catalog_cache = r.json()
    return _catalog_cache


def _year_of(dist: dict) -> int | None:
    for field in ("temporal", "title", "downloadURL"):
        m = re.search(r"(20\d{2})", str(dist.get(field, "")))
        if m:
            return int(m.group(1))
    return None


def cms_csv_urls(source_key: str) -> dict[int, str]:
    """Return {year: csv_url} for a CMS dataset, overrides taking priority."""
    cfg = SOURCES[source_key]
    urls: dict[int, str] = {}
    try:
        title = cfg["catalog_title"].lower()
        # exact title match first, so "by Provider" does not pick up "by Provider and Drug"
        datasets = [d for d in cms_catalog()["dataset"] if d["title"].strip().lower() == title]
        if not datasets:
            datasets = [d for d in cms_catalog()["dataset"] if title in d["title"].lower()]
        for ds in datasets[:1]:
            for dist in ds.get("distribution", []):
                url = dist.get("downloadURL", "")
                if url.lower().endswith(".csv"):
                    y = _year_of(dist)
                    if y and y not in urls:
                        urls[y] = url
    except Exception as exc:  # network / catalog shape change
        log.warning("Catalog lookup failed for %s: %s", source_key, exc)
    for y, u in (cfg.get("overrides") or {}).items():
        urls[int(y)] = u
    if not urls:
        raise RuntimeError(
            f"No CSV URLs found for {source_key}. Add them under `overrides` in ingest/sources.yml."
        )
    return dict(sorted(urls.items()))


def lower_cols_select(
    con, csv_url: str, extra_where: str = "", year: int | None = None, delim: str | None = None
) -> str:
    """Build a SELECT over a remote CSV that lower-cases every column name.

    Everything is read as VARCHAR; typing happens in dbt staging models.
    """
    opts = "all_varchar=true, header=true, sample_size=20000" + (f", delim='{delim}'" if delim else "")
    reader = f"read_csv('{csv_url}', {opts})"
    cols = con.execute(f"DESCRIBE SELECT * FROM {reader}").fetchall()
    select = ", ".join(f'"{c[0]}" AS {c[0].strip().lower()}' for c in cols)
    year_col = f", {year} AS data_year" if year is not None else ""
    return f"SELECT {select}{year_col} FROM {reader} {extra_where}"
