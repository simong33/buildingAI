run_file_prep:
	python -c 'from scripts.files_prep import download_and_extract; download_and_extract()'

remove_unrelevant_tables:
	python -c 'from scripts.files_prep import remove_unrelevant_tables; remove_unrelevant_tables()'

remove_all_tables:
	rm -rf raw_data/*

get_csv_size:
	python -c 'from scripts.files_prep import get_csv_size; get_csv_size()'
	
print_dataframe_shape:
	python -c 'from app.data.data import get_dataframe_shape; get_dataframe_shape()'