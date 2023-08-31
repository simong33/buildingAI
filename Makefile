ML_DIR=~/.lewagon/mlops

run_file_prep:
	python -c 'from scripts.files_prep import download_and_extract; download_and_extract()'

remove_unrelevant_tables:
	python -c 'from scripts.files_prep import remove_unrelevant_tables; remove_unrelevant_tables()'

remove_all_tables:
	rm -rf raw_data/*

get_csv_size:
	python -c 'from scripts.files_prep import get_csv_size; get_csv_size()'
	
print_dataframe_shape:
	python -c 'from app.ml_logic.data import get_dataframe_shape; get_dataframe_shape()'

save_dataframe:
	python -c 'from app.ml_logic.data import save_dataframe; save_dataframe()'

run_api:
	uvicorn app.api.fast:app

save_model:
	python -c 'from app.ml_logic.registry import save_model; save_model()'

load_model:
	python -c 'from app.ml_logic.registry import load_model; load_model()'

reset_local_files:
	rm -rf ${ML_DIR}
	mkdir -p ~/.lewagon/mlops/data/
	mkdir ~/.lewagon/mlops/data/raw
	mkdir ~/.lewagon/mlops/data/processed
	mkdir ~/.lewagon/mlops/training_outputs
	mkdir ~/.lewagon/mlops/training_outputs/metrics
	mkdir ~/.lewagon/mlops/training_outputs/models
	mkdir ~/.lewagon/mlops/training_outputs/params

# Tests

test_api_on_prod:
	pytest \
	tests/api/test_cloud_endpoints.py --asyncio-mode=strict -W "ignore"