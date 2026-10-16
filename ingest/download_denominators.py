"""Load enrollment, chronic conditions, CDC PLACES and the ZCTA→county crosswalk."""
import argparse

from common import SOURCES, cms_csv_urls, connect, log, lower_cols_select


def load_enrollment(con):
    url = SOURCES["medicare_enrollment"].get("override") or list(cms_csv_urls("medicare_enrollment").values())[-1]
    log.info("Loading enrollment from %s", url)
    con.execute(f"CREATE OR REPLACE TABLE raw.medicare_enrollment AS {lower_cols_select(con, url)}")


def load_chronic(con, years):
    urls = cms_csv_urls("chronic_conditions")
    con.execute("DROP TABLE IF EXISTS raw.chronic_conditions")
    first = True
    for y in years:
        if y not in urls:
            log.warning("Chronic conditions %s not found; available %s", y, list(urls))
            continue
        q = lower_cols_select(con, urls[y], "WHERE lower(Bene_Cond) LIKE '%diabetes%'", y)
        verb = "CREATE TABLE raw.chronic_conditions AS" if first else "INSERT INTO raw.chronic_conditions BY NAME"
        con.execute(f"{verb} {q}")
        first = False


def load_places(con):
    url = SOURCES["places_county"]["url"]
    log.info("Loading CDC PLACES")
    con.execute(f"CREATE OR REPLACE TABLE raw.places_county AS {lower_cols_select(con, url)}")


def load_zcta(con):
    url = SOURCES["zcta_county"]["url"]
    log.info("Loading ZCTA→county crosswalk")
    con.execute(f"CREATE OR REPLACE TABLE raw.zcta_county AS {lower_cols_select(con, url, delim='|')}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="data/glp1.duckdb")
    ap.add_argument("--years", nargs="+", type=int, default=[2022, 2023, 2024])
    a = ap.parse_args()
    con = connect(a.db)
    load_zcta(con)
    load_places(con)
    load_enrollment(con)
    load_chronic(con, a.years)
