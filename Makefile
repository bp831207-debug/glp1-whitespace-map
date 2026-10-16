DB ?= data/glp1.duckdb
YEARS ?= 2019 2020 2021 2022 2023 2024

.PHONY: sample ingest build test clean

sample:            ## full pipeline on synthetic data (no downloads)
	python scripts/make_sample_data.py --db $(DB)
	cd dbt && dbt build --profiles-dir . --vars '{latest_year: 2024}'

ingest:            ## download real public data into $(DB)
	python ingest/run_all.py --db $(DB) --years $(YEARS)

build:             ## dbt seed + run + test
	cd dbt && dbt build --profiles-dir .

test:
	pytest -q

clean:
	rm -f $(DB) $(DB).wal && rm -rf dbt/target dbt/logs
