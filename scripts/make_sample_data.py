"""Create small synthetic raw tables with the same column names as the real CMS/CDC/Census files.

Lets anyone (and CI) run the full dbt pipeline in seconds without downloading GBs.
Numbers are random. Never use them for findings.
"""
import argparse
import random
from pathlib import Path

import duckdb
import pandas as pd

random.seed(42)
YEARS = [2022, 2023, 2024]
COUNTIES = [("01001", "AL", "Autauga"), ("06037", "CA", "Los Angeles"), ("12086", "FL", "Miami-Dade"),
            ("17031", "IL", "Cook"), ("48201", "TX", "Harris"), ("36061", "NY", "New York"),
            ("21195", "KY", "Pike"), ("28049", "MS", "Hinds")]
ZIPS = {c[0]: [f"{random.randint(10000, 99999)}" for _ in range(3)] for c in COUNTIES}
DRUGS = [("Semaglutide", "Ozempic"), ("Semaglutide", "Rybelsus"), ("Tirzepatide", "Mounjaro"),
         ("Dulaglutide", "Trulicity"), ("Liraglutide", "Victoza"), ("Metformin HCl", "Metformin HCl"),
         ("Empagliflozin", "Jardiance"), ("Sitagliptin Phosphate", "Januvia"), ("Glipizide", "Glipizide"),
         ("Insulin Glargine,Hum.Rec.Anlog", "Lantus Solostar"), ("Insulin Degludec/Liraglutide", "Xultophy")]
TYPES = ["Internal Medicine", "Family Practice", "Endocrinology", "Nurse Practitioner", "Physician Assistant"]


def s(x):  # raw tables are all VARCHAR, like the real ingest
    return None if x is None else str(x)


def build():
    drug_rows, prov_rows, enr_rows, cc_rows = [], [], [], []
    npis = [(str(1000000000 + i), random.choice(COUNTIES), random.choice(TYPES)) for i in range(400)]
    for y in YEARS:
        growth = 1 + 0.35 * (y - 2022)
        for npi, (fips, st, _), ptype in npis:
            prov_rows.append(dict(prscrbr_npi=npi, prscrbr_zip5=random.choice(ZIPS[fips]), prscrbr_state_abrvtn=st,
                                  prscrbr_type=ptype, tot_clms=s(random.randint(200, 5000)), tot_benes=s(random.randint(50, 900)),
                                  data_year=y))
            for g, b in random.sample(DRUGS, k=random.randint(2, 7)):
                is_glp1 = any(k in g.lower() for k in ("glutide", "tirzepatide"))
                clms = int(random.randint(11, 400) * (growth if is_glp1 else 1))
                benes = random.randint(5, max(6, clms // 4))
                drug_rows.append(dict(prscrbr_npi=npi, prscrbr_last_org_name="Doe", prscrbr_first_name="J",
                                      prscrbr_city="X", prscrbr_state_abrvtn=st, prscrbr_state_fips=fips[:2],
                                      prscrbr_type=ptype, prscrbr_type_src="S", brnd_name=b, gnrc_name=g,
                                      tot_clms=s(clms), tot_30day_fills=s(clms * 1.1), tot_day_suply=s(clms * 30),
                                      tot_drug_cst=s(round(clms * (900 if is_glp1 else 40), 2)),
                                      tot_benes=None if benes < 11 else s(benes), data_year=y))
        for fips, st, name in COUNTIES:
            enr = random.randint(8000, 900000)
            enr_rows.append(dict(year=s(y), month="Year", bene_geo_lvl="County", bene_state_abrvtn=st,
                                 bene_county_desc=name, bene_fips_cd=fips, tot_benes=s(int(enr * 1.3)),
                                 prscrptn_drug_tot_benes=s(enr)))
            cc_rows.append(dict(bene_geo_lvl="County", bene_geo_desc=name, bene_geo_cd=fips, bene_age_lvl="All",
                                bene_demo_lvl="All", bene_demo_desc="All", bene_cond="Diabetes",
                                prvlnc=s(round(random.uniform(0.2, 0.35), 3)), data_year=y))
    places = []
    for fips, st, name in COUNTIES:
        for m, lo, hi in (("DIABETES", 8, 18), ("OBESITY", 25, 45)):
            places.append(dict(year="2023", stateabbr=st, locationname=name, locationid=fips, measureid=m,
                               datavaluetypeid="CrdPrv", data_value=s(round(random.uniform(lo, hi), 1)),
                               totalpop18plus=s(random.randint(20000, 8000000))))
    zcta = [dict(geoid_zcta5_20=z, geoid_county_20=f, arealand_part=s(random.randint(1_000_000, 90_000_000)))
            for f, zs in ZIPS.items() for z in zs]
    return dict(partd_prescriber_drug=drug_rows, partd_prescriber=prov_rows, medicare_enrollment=enr_rows,
                chronic_conditions=cc_rows, places_county=places, zcta_county=zcta)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="data/glp1.duckdb")
    db = ap.parse_args().db
    Path(db).parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(db)
    con.execute("CREATE SCHEMA IF NOT EXISTS raw")
    for name, rows in build().items():
        df = pd.DataFrame(rows).astype("string")
        con.register("df", df)
        con.execute(f"CREATE OR REPLACE TABLE raw.{name} AS SELECT * FROM df")
        con.unregister("df")
        print(f"raw.{name:<24} {len(df):>6} rows")
