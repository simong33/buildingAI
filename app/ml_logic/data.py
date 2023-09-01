import pandas as pd
import numpy as np
import os
from tqdm import tqdm
from app.params import COLUMNS_TO_KEEP, DUPLICATE_COLUMNS, LOCAL_DATA_PATH
from app.ml_logic.features import add_features

def save_dataframe():
    """
    Save a dataframe in the data folder.
    """
    df = build_dataframe()
    if not os.path.exists(LOCAL_DATA_PATH):
        os.makedirs(LOCAL_DATA_PATH)
    df.to_csv(f"{LOCAL_DATA_PATH}/dpe.csv", index=False)

def load_dataframe() -> pd.DataFrame:
    """
    Load a dataframe from the data folder.
    """
    if not os.path.exists(LOCAL_DATA_PATH):
        os.makedirs(LOCAL_DATA_PATH)
    if os.path.exists(f"{LOCAL_DATA_PATH}/dpe.csv"):
        df = pd.read_csv(f"{LOCAL_DATA_PATH}/dpe.csv")
    else:
        df = build_dataframe()
        df.to_csv(f"{LOCAL_DATA_PATH}/dpe.csv", index=False)
    return df


def build_dataframe(path="raw_data/csv") -> pd.DataFrame:
    """
    Build a dataframe from the CSV files in raw_data/csv.
    """
    df = pd.read_csv(f"{path}/batiment_groupe.csv", sep=",")
    df = df.drop_duplicates()
    initial_number_of_rows = df.shape[0]
    for dirpath, dirnames, filenames in os.walk(path):
        for f in tqdm(filenames):
            if f.startswith("rel_") or f.endswith(".csvt") or f.endswith(".prj"):
                continue
            fp = os.path.join(dirpath, f)
            if "batiment_groupe.csv" not in fp:
                df_tmp = pd.read_csv(fp, sep=",")
                df_tmp = df_tmp.drop_duplicates()
                if "batiment_groupe_id" not in df_tmp.columns:
                    print(
                        f"File {fp} does not contain batiment_groupe_id, using rel table."
                    )
                    df = merge_df_with_rel_table(df, df_tmp, fp)
                    continue
                print(f"Merging {fp}")
                if "multimillesime" in fp:
                    # Keep last millesime for each building
                    df_tmp["millesime"] = df_tmp["millesime"].astype(str)
                    df_tmp = df_tmp.sort_values(by=["millesime"], ascending=False)
                    df_tmp = df_tmp.drop_duplicates(subset=["batiment_groupe_id"])
                if "construction" in fp:
                    df_tmp = df_tmp.drop_duplicates(subset=["batiment_groupe_id"])

                df_tmp = craft_unique_column_names(
                    df, df_tmp, prefix=fp, exceptions=["batiment_groupe_id"]
                )
                df = df.merge(df_tmp, on="batiment_groupe_id", how="left")
                print(f"Shape of the dataframe: {df.shape}")
    if initial_number_of_rows != df.shape[0]:
        print(
            f"Warning: the number of rows has changed from {initial_number_of_rows} to {df.shape[0]}."
        )
    df = drop_unrelevant_columns(df)
    df = drop_duplicate_columns(df)
    df = rename_columns(df)
    df = remove_duplicate_headers(df)
    df = force_types(df)

    df=add_features(df)
    df = drop_rows_without_target(df)
    print(f"FINAL Shape of the dataframe: {df.shape}")
    return df


def drop_unrelevant_columns(df=None) -> pd.DataFrame:
    """
    Drop columns that are not relevant for the analysis.
    """
    col_to_keep = list(COLUMNS_TO_KEEP.keys())
    col_to_keep.append("batiment_groupe_id")
    initial_number_of_columns = df.shape[1]
    columns_to_drop = [
        col for col in df.columns if not any(x in col for x in col_to_keep)
    ]
    df = df.drop(columns=columns_to_drop)
    number_of_droped_columns = initial_number_of_columns - df.shape[1]
    print(
        f"Number of columns droped: {number_of_droped_columns} out of {initial_number_of_columns}."
    )
    print(f"Shape of the dataframe: {df.shape}")
    return df


def drop_duplicate_columns(df=None) -> pd.DataFrame:
    """
    Final drop of duplicate columns after merge.
    """

    df = df.drop(columns=DUPLICATE_COLUMNS)
    columns_to_drop = [col for col in df.columns if "nb_classe_bilan_dpe" in col]
    df = df.drop(columns=columns_to_drop)
    return df


def drop_rows_without_target(df=None) -> pd.DataFrame:
    """
    Remove rows without DPE target.
    """
    print("Removing rows without DPE target.")
    df.loc[
        ~df["classe_bilan_dpe"].isin(["A", "B", "C", "D", "E", "F", "G"]),
        "classe_bilan_dpe",
    ] = np.nan
    df = df.dropna(subset=["classe_bilan_dpe"])
    return df


def get_dataframe_shape(df=None):
    """
    Print the shape of the dataframe.
    """
    df = build_dataframe()
    print(f"Shape of the dataframe: {df.shape}")
    return df.shape


def craft_unique_column_names(
    df1=None, df2=None, prefix="None", exceptions=[]
) -> pd.DataFrame:
    """
    If duplicate column names in df2 compared to df1, add a prefix to the column names of df2.
    """
    prefix = prefix.split("/")[-1].split(".")[0]
    col_names = df2.columns
    for col_name in col_names:
        if col_name in df1.columns and col_name not in exceptions:
            df2 = df2.rename(columns={col_name: f"{prefix}_{col_name}"})
    return df2


def rename_columns(df=None) -> pd.DataFrame:
    """
    Rename columns for multimillesime.
    """
    col = {
        "conso_tot": "gaz_conso_tot",
        "conso_tot_par_pdl": "gaz_conso_tot_par_pdl",
        "batiment_groupe_dle_elec_multimillesime_conso_tot": "elec_conso_tot",
        "batiment_groupe_dle_elec_multimillesime_conso_tot_par_pdl": "elec_conso_tot_par_pdl",
    }
    return df.rename(columns=col)


def merge_df_with_rel_table(df1, df2, fp) -> pd.DataFrame:
    """
    Use the join table to merge the two tables.
    """
    table_name = fp.split("/")[-1].split(".")[0]
    join_file_path = fp.replace(table_name, f"rel_batiment_groupe_{table_name}")
    join_df = pd.read_csv(join_file_path, sep=",")
    join_df = join_df.drop_duplicates(subset=["batiment_groupe_id"])
    df2 = craft_unique_column_names(
        df1, df2, prefix=fp, exceptions=["batiment_groupe_id"]
    )
    if fp == "raw_data/csv/dpe_logement.csv":
        join_df = join_df.rename(columns={"identifiant_dpe": "dpe_logement_id"})
        df2 = df2.rename(columns={"dpe_logement_identifiant_dpe": "dpe_logement_id"})

    join_df = craft_unique_column_names(
        df1, join_df, prefix=join_file_path, exceptions=["batiment_groupe_id"]
    )
    df = df1.merge(join_df, on="batiment_groupe_id", how="left")
    df = df.merge(df2, on=f"{table_name}_id", how="left")
    print("Shape of the joined dataframe: ", df.shape)
    return df


def remove_duplicate_headers(df) -> pd.DataFrame:
    """
    Remove duplicate headers if necessary
    """
    dup = df.query('batiment_groupe_id=="batiment_groupe_id"').index
    df = df.drop(dup.tolist())
    return df


def force_types(df) -> pd.DataFrame:
    """
    Force types of columns
    """
    dict_type = {
        "geom_groupe": object,
        "batiment_groupe_id": str,
        "s_geom_groupe": float,
        "gaz_conso_tot": float,
        "gaz_conso_tot_par_pdl": float,
        "hauteur_mean": float,
        "annee_construction": float,
        "mat_mur_txt": str,
        "mat_toit_txt": str,
        "nb_log": float,
        "classe_bilan_dpe": str,
        "elec_conso_tot": float,
        "elec_conso_tot_par_pdl": float,
    }
    return df.astype(dict_type)

def save_frame(name):
    """
    Save a dataframe in the data folder.
    """
    if not os.path.exists(LOCAL_DATA_PATH):
        os.makedirs(LOCAL_DATA_PATH)
    df.to_csv(f"{LOCAL_DATA_PATH}/{name}.csv", index=False)
    breakpoint()
