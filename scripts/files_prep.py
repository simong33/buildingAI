import os
from app.params import *


def download_and_extract(dep_code=75):
    """
    Download and extract the data from the BDNB.
    """
    url = craft_download_url(dep_code)
    print(f"Downloading data from {url}")
    os.system(f"wget -P raw_data {url}")
    print(f"Extracting data for dep {dep_code}")
    os.system(
        f"unzip -o raw_data/open_data_millesime_2022-10-d_dep{dep_code}_csv.zip -d raw_data/"
    )
    print(f"Removing zip file for dep {dep_code}")
    os.system(f"rm raw_data/open_data_millesime_2022-10-d_dep{dep_code}_csv.zip")
    remove_extra_files()
    remove_unrelevant_tables()


def remove_unrelevant_tables(table_names=UNRELEVANT_TABLES):
    """
    Remove the tables that are not relevant for our analysis.
    """
    for table_name in table_names:
        print(f"Removing table {table_name} if exists.")
        if os.path.isfile(f"raw_data/csv/{table_name}.csv"):
            os.system(f"rm raw_data/csv/{table_name}.csv")
        if os.path.isfile(f"raw_data/csv/rel_batiment_groupe_{table_name}.csv"):
            os.system(f"rm raw_data/csv/rel_batiment_groupe_{table_name}.csv")
        if os.path.isfile(f"raw_data/csv/batiment_groupe_{table_name}.csv"):
            os.system(f"rm raw_data/csv/batiment_groupe_{table_name}.csv")


def craft_download_url(dep_code: int):
    """Craft the URL to download the data from."""
    dep_url = f"millesime_2022-10-d_dep{dep_code}/open_data_millesime_2022-10-d_dep{dep_code}_csv.zip"
    return BDNB_FILES_URI + dep_url


def remove_extra_files():
    """
    Remove CSVT files used in QGIS.
    """
    os.system("rm raw_data/csv/*.csvt")


def get_csv_size(path="raw_data/csv"):
    """
    Print the total size of the files in the given path.
    """
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    print(f"Total size of files in {path}: {total_size / 1e6} MB")
