import os
from app.params import *


def download_and_extract(dep_codes: list = DEP_CODES):
    """
    Download and extract the data from the BDNB.
    """
    clean_raw_data()
    for dep_code in dep_codes:
        url = craft_download_url(dep_code)
        print(f"Downloading data from {url}")
        os.system(f"wget -P raw_data {url}")
        if not os.path.isdir(f"raw_data/{dep_code}"):
            os.system(f"mkdir raw_data/{dep_code}")
        print(f"Extracting data for dep {dep_code}")
        os.system(
            f"unzip -o raw_data/open_data_millesime_2022-10-d_dep{dep_code}_csv.zip -d raw_data/{dep_code}"
        )
        print(f"Removing zip file for dep {dep_code}")
        os.system(f"rm raw_data/open_data_millesime_2022-10-d_dep{dep_code}_csv.zip")
        remove_extra_files(dep_code)
        remove_unrelevant_tables(UNRELEVANT_TABLES, dep_code)
    merge_csv_files(dep_codes)
    remove_departements_directories(dep_codes)
    get_csv_size()


def merge_csv_files(dep_codes=DEP_CODES):
    """
    Create a single CSV files for each table from each departement CSV.
    """
    if not os.path.isdir("raw_data/csv"):
        os.system("mkdir raw_data/csv")

    file_names = os.listdir("raw_data/75/csv")
    for file_name in file_names:
        print(f"Merging {file_name}")
        # merge all files with the same name, only keep header from first file
        os.system(
            f"cat raw_data/*/csv/{file_name} | head -n 1 > raw_data/csv/{file_name}"
        )
        os.system(
            f"cat raw_data/*/csv/{file_name} | grep -v 'id' >> raw_data/csv/{file_name}"
        )


def remove_unrelevant_tables(table_names=UNRELEVANT_TABLES, dep_code: int = 75):
    """
    Remove the tables that are not relevant for our analysis.
    """
    for table_name in table_names:
        print(f"Removing table {table_name} if exists.")
        if os.path.isfile(f"raw_data/{dep_code}/csv/{table_name}.csv"):
            os.system(f"rm raw_data/{dep_code}/csv/{table_name}.csv")
        if os.path.isfile(
            f"raw_data/{dep_code}/csv/rel_batiment_groupe_{table_name}.csv"
        ):
            os.system(
                f"rm raw_data/{dep_code}/csv/rel_batiment_groupe_{table_name}.csv"
            )
        if os.path.isfile(f"raw_data/{dep_code}/csv/batiment_groupe_{table_name}.csv"):
            os.system(f"rm raw_data/{dep_code}/csv/batiment_groupe_{table_name}.csv")


def craft_download_url(dep_code: int):
    """Craft the URL to download the data from."""
    dep_url = f"millesime_2022-10-d_dep{dep_code}/open_data_millesime_2022-10-d_dep{dep_code}_csv.zip"
    return BDNB_FILES_URI + dep_url


def remove_extra_files(dep_code):
    """
    Remove CSVT files used in QGIS.
    """
    os.system(f"rm raw_data/{dep_code}/csv/*.csvt")
    os.system(f"rm raw_data/{dep_code}/csv/*.prj")


def remove_departements_directories(dep_codes):
    """
    Remove deps directories after merging.
    """
    for dep_code in dep_codes:
        os.system(f"rm -r raw_data/{dep_code}")


def clean_raw_data():
    """
    Remove all files in raw_data directory.
    """
    os.system("rm -r raw_data/*")


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
