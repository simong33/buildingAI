run_file_prep:
	python -c 'from scripts.files_prep import download_and_extract; download_and_extract()'

run_delete_unrelevant_tables:
	python -c 'from scripts.files_prep import remove_unrelevant_tables; remove_unrelevant_tables()'