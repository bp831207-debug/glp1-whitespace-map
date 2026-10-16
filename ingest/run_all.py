"""Run every ingest step and print a row-count summary."""
import argparse

from common import connect, log
import download_denominators as den
import download_partd as partd

ap = argparse.ArgumentParser()
ap.add_argument("--db", default="data/glp1.duckdb")
ap.add_argument("--years", nargs="+", type=int, default=[2022, 2023, 2024])
a = ap.parse_args()

con = connect(a.db)
den.load_zcta(con)
den.load_places(con)
den.load_enrollment(con)
den.load_chronic(con, a.years)
partd.load_drug(con, a.years)
partd.load_provider(con, a.years)

for (t,) in con.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='raw' ORDER BY 1").fetchall():
    log.info("raw.%-24s %12s rows", t, f"{con.execute(f'SELECT count(*) FROM raw.{t}').fetchone()[0]:,}")
