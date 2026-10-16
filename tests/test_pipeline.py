"""End-to-end check on synthetic data: dbt builds and the marts look sane."""
import os
import sys
import subprocess
from pathlib import Path

import duckdb
import pytest

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "test.duckdb"


@pytest.fixture(scope="module")
def con():
    DB.unlink(missing_ok=True)
    subprocess.run([sys.executable, "scripts/make_sample_data.py", "--db", str(DB)], cwd=ROOT, check=True)
    env = {**os.environ, "GLP1_DB": str(DB)}
    subprocess.run(["dbt", "build", "--profiles-dir", "."], cwd=ROOT / "dbt", env=env, check=True)
    c = duckdb.connect(str(DB), read_only=True)
    yield c
    c.close()


def test_combo_products_classified_as_glp1(con):
    cls = con.execute(
        "select distinct drug_class from intermediate.int_drug_classified where generic_name like 'Insulin Degludec/Liraglutide'"
    ).fetchall()
    assert cls == [("GLP-1 RA",)]


def test_all_four_segments_present(con):
    segs = {r[0] for r in con.execute("select distinct segment from marts.mart_hcp_segments").fetchall()}
    assert segs == {"Untapped", "Champions", "Emerging", "Deprioritize"}


def test_gap_non_negative(con):
    assert con.execute("select count(*) from marts.mart_county_opportunity where whitespace_gap_patients < 0").fetchone()[0] == 0


def test_brand_shares_sum_to_one(con):
    rows = con.execute("select data_year, sum(glp1_claim_share) from marts.mart_brand_trends group by 1").fetchall()
    assert all(abs(s - 1) < 1e-9 for _, s in rows)
