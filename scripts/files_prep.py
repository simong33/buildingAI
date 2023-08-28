import os

def download_and_extract(dep_code: int):
    """
    Download and extract the data from the BDNB.
    """
    url = craft_download_url(dep_code)
    print(f"Downloading data from {url}")
    os.system(f"wget -P raw_data {url}")
    print(f"Extracting data for dep {dep_code}"")
    os.system(
        f"unzip -o raw_data/open_data_millesime_2022-10-d_dep{dep_code}_csv.zip -d data"
    )
    print(f"Removing zip file for dep {dep_code}")
    os.system(f"rm data/open_data_millesime_2022-10-d_dep{dep_code}_csv.zip")
    remove_extra_files()
    
def remove_unrelevant_tables(table_names: UNRELEVANT_TABLES):
    """
    Remove the tables that are not relevant for our analysis.
    """
    for table_name in table_names:
        print(f"Removing table {table_name}")
        os.system(f"rm raw_data/{table_name}.csv"))
        os.system(f"rm raw_data/csv/batiment_groupe_{table_name}.csv")
        os.system(f"rm raw_data/csv/rel_batiment_groupe_{table_name}.csv")

def craft_download_url(dep_code: int):
    """Craft the URL to download the data from."""
    dep_url = f"millesime_2022-10-d_dep{dep_code}/open_data_millesime_2022-10-d_dep{dep_code}_csv.zip"
    return BDNB_FILES_URI + dep_url

def remove_extra_files():
    os.system("rm raw_data/csv/*.csvt")