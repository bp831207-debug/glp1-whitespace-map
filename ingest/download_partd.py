"""Stream CMS Part D prescriber files and keep only diabetes drugs.

Usage: python ingest/download_partd.py --db data/glp1.duckdb --years 2022 2023 2024
The full by-Provider-and-Drug file is ~3 GB/year; DuckDB streams it over HTTP and
filters on the fly, so only a few hundred MB end up in the database.
"""
import argparse

from common import DIABETES_PATTERNS, cms_csv_urls, connect, log, lower_cols_select


def load_drug(con, years):
    urls = cms_csv_urls("partd_prescriber_drug")
    regex = "|".join(DIABETES_PATTERNS)
    con.execute("DROP TABLE IF EXISTS raw.partd_prescriber_drug")
    for i, y in enumerate(years):
        if y not in urls:
            log.warning("Part D drug file for %s not found; available: %s", y, list(urls))
            continue
        q = lower_cols_select(con, urls[y], f"WHERE regexp_matches(lower(Gnrc_Name), '{regex}')", y)
        verb = "CREATE TABLE raw.partd_prescriber_drug AS" if i == 0 else "INSERT INTO raw.partd_prescriber_drug BY NAME"
        log.info("Loading Part D drug %s ...", y)
        con.execute(f"{verb} {q}")
        n = con.execute(f"SELECT count(*) FROM raw.partd_prescriber_drug WHERE data_year={y}").fetchone()[0]
        log.info("  %s rows for %s", f"{n:,}", y)


def load_provider(con, years):
    urls = cms_csv_urls("partd_prescriber")
    con.execute("DROP TABLE IF EXISTS raw.partd_prescriber")
    for i, y in enumerate(years):
        if y not in urls:
            log.warning("Part D provider file for %s not found", y)
            continue
        q = lower_cols_select(con, urls[y], year=y)
        q = f"SELECT prscrbr_npi, prscrbr_zip5, prscrbr_state_abrvtn, prscrbr_type, tot_clms, tot_benes, data_year FROM ({q})"
        verb = "CREATE TABLE raw.partd_prescriber AS" if i == 0 else "INSERT INTO raw.partd_prescriber BY NAME"
        log.info("Loading Part D provider %s ...", y)
        con.execute(f"{verb} {q}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="data/glp1.duckdb")
    ap.add_argument("--years", nargs="+", type=int, default=[2022, 2023, 2024])
    a = ap.parse_args()
    con = connect(a.db)
    load_drug(con, a.years)
    load_provider(con, a.years)
