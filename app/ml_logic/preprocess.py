import pandas as pd
import numpy as np
import pickle
import time
import glob

from sklearn.preprocessing import (
    RobustScaler,
    StandardScaler,
    MinMaxScaler,
    LabelEncoder,
    OrdinalEncoder,
    OneHotEncoder,
)
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split

from google.cloud import storage

from app.params import *
from app.ml_logic.data import load_dataframe


def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False


def clean_usage(txt: str):
    if txt is None or isfloat(txt):
        return False
    else:
        for t in ["]", "[", '"']:
            txt = txt.replace(t, "")
        usages = txt.strip().split(",")
        return (
            True
            if usages[0] == "Résidentiel"
            or (len(usages) == 2 and usages[1] == "Résidentiel")
            else False
        )


def classic_clean(
    df: pd.DataFrame,
) -> pd.DataFrame:
    data = df.copy()
    # On retire les ligne duppliquées
    clean_data = data.drop_duplicates()

    # On retire les lignes qui ne correspondent pas à des données résidentielles
    # On utilise la colonne de bdtopo l_usage_1
    selection = clean_data.l_usage_1.map(clean_usage)
    clean_data = clean_data[selection]

    return clean_data


def gen_pipe(df: pd.DataFrame, mapping: pd.DataFrame, scaler: str):

    num_imputer = SimpleImputer(strategy="mean")

    selection = (mapping.type == "num") & (mapping.scale == scaler)

    cols = list(mapping[selection].index)
    cols = [
        col
        for col in df.columns
        if col in cols or len([c for c in cols if c in col]) > 0
    ]

    match scaler:
        case "RobustScaler":
            scaler = RobustScaler()
        case "StandardScaler":
            scaler = RobustScaler()
        case _:
            scaler = MinMaxScaler()

    num_pipe = make_pipeline(num_imputer, scaler)

    return num_pipe, cols


def create_preprocessor(df: pd.DataFrame) -> ColumnTransformer:
    """
    Cette fonction permet de créer un preprocessor qui intègre les dfférentes catégories de columns
    """

    # Mapping columns
    mapping = pd.DataFrame.from_dict(
        COLUMNS_TO_KEEP, orient="index", columns=["type", "scale", "impute"]
    )

    # On définit les différent pipelines
    # Pour le moment quatre pipelines : num + ordinal + categorical

    # NUM - Robuts
    num_robust_pipe, cols_num_r = gen_pipe(df, mapping, "RobustScaler")

    # NUM - MinMax
    num_minmax_pipe, cols_num_mm = gen_pipe(df, mapping, "MinMaxScaler")

    # NUM - Standard
    num_standard_pipe, cols_num_std = gen_pipe(df, mapping, "StandardScaler")

    # CAT
    # On prépare les imputers
    str_imputer = SimpleImputer(strategy="constant", fill_value="INDETERMINE")
    selection = mapping.type == "cat"
    cols_cat = list(mapping[selection].index)
    ohe = OneHotEncoder(sparse_output=False)
    cat_pipe = make_pipeline(str_imputer, ohe)

    # On assemble les différents pipes
    final_preprocessor = ColumnTransformer(
        [
            ("numerical_cols_r", num_robust_pipe, cols_num_r),
            ("numerical_cols_mm", num_minmax_pipe, cols_num_mm),
            ("numerical_cols_std", num_standard_pipe, cols_num_std),
            ("categorical_cols", cat_pipe, cols_cat),
        ],
        n_jobs=-1,
        remainder="drop",
    )

    return final_preprocessor


def save_preprocessor(preprocessor: ColumnTransformer):
    """
    Save preproc to pickle
    """
    timestamp = time.strftime("%Y%m%d-%H%M%S")

    preproc_path = os.path.join(LOCAL_PREPROC_PATH, f"{timestamp}.pkl")
    with open(preproc_path, "wb") as preproc_file:
        pickle.dump(preprocessor, preproc_file)

    if MODEL_TARGET == "gcs":

        model_filename = timestamp
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(f"preproc/{model_filename}.pkl")
        blob.upload_from_filename(preproc_path)

        print("✅ Preproc saved to GCS")

        return None
    return None


def load_preprocessor(gcs: bool = True) -> ColumnTransformer:
    """
    Load preproc from pickle
    """
    if gcs:
        client = storage.Client()
        blobs = list(client.get_bucket(BUCKET_NAME).list_blobs(prefix="preproc"))
        try:
            latest_blob = max(blobs, key=lambda x: x.updated)
            print(f"Latest blob: {latest_blob.name}")
            # if LOCAL_PREPROC_PATH does not exist, create it
            if not os.path.exists(LOCAL_PREPROC_PATH):
                os.makedirs(LOCAL_PREPROC_PATH)
            latest_preproc_path_to_save = os.path.join(
                LOCAL_PREPROC_PATH, latest_blob.name.split("/")[-1]
            )
            latest_blob.download_to_filename(latest_preproc_path_to_save)

            latest_preproc = pickle.load(open(latest_preproc_path_to_save, "rb"))

            print("✅ Latest preproc downloaded from cloud storage")

            return latest_preproc
        except Exception as e:
            print(f"\n❌ No preproc found in GCS bucket {BUCKET_NAME}: {e}")
            return None

    local_preproc_directory = os.path.join(LOCAL_PREPROC_PATH)
    local_preproc_paths = glob.glob(f"{local_preproc_directory}/*")
    local_preproc_paths = sorted(local_preproc_paths, reverse=True)
    most_recent_preproc_path_on_disk = local_preproc_paths[0]
    preproc = pickle.load(open(most_recent_preproc_path_on_disk, "rb"))

    return preproc


def save_encoder(encoder: LabelEncoder):
    """
    Save encoder to GCS
    """
    timestamp = time.strftime("%Y%m%d-%H%M%S")

    encoder_path = os.path.join(LOCAL_ENCODERS_PATH, f"{timestamp}.pkl")
    with open(encoder_path, "wb") as file:
        pickle.dump(encoder, file)

    if MODEL_TARGET == "gcs":

        encoder_filename = "encoder_" + timestamp
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(f"encoders/{encoder_filename}.pkl")
        blob.upload_from_filename(encoder_path)

        print("✅ Encoder saved to GCS")

        return None
    return None


def load_encoder(gcs: bool = True) -> LabelEncoder:
    """
    Load LabelEncoder from GCS
    """
    if gcs:
        client = storage.Client()
        blobs = list(client.get_bucket(BUCKET_NAME).list_blobs(prefix="encoders"))
        try:
            latest_blob = max(blobs, key=lambda x: x.updated)
            if not os.path.exists(LOCAL_ENCODERS_PATH):
                os.makedirs(LOCAL_ENCODERS_PATH)
            latest_encoder_path_to_save = os.path.join(
                LOCAL_ENCODERS_PATH, latest_blob.name.split("/")[-1]
            )
            latest_blob.download_to_filename(latest_encoder_path_to_save)

            latest_encoder = pickle.load(open(latest_encoder_path_to_save, "rb"))

            print("✅ Latest encoder downloaded from cloud storage")

            return latest_encoder
        except:
            print(f"\n❌ No encoder found in GCS bucket {BUCKET_NAME}")
            return None

    local_encoder_directory = os.path.join(LOCAL_ENCODERS_PATH)
    local_encoder_paths = glob.glob(f"{local_encoder_directory}/*")
    local_encoder_paths = sorted(local_encoder_paths, reverse=True)
    most_recent_encoder_path_on_disk = local_encoder_paths[0]
    return pickle.load(open(most_recent_encoder_path_on_disk, "rb"))


def save_one_preproc():
    """
    Test method to be removed
    """
    df = load_dataframe()
    preprocess(df, 0.2)


def preprocess(df: pd.DataFrame, split_ratio: float = 0.2, prod: bool = False) -> tuple:
    """
    Input : dataframe
    Output : tuple X_train, X_test, y_train, y_test
    Cette fonction produit un dataframe :
    1. nettoyé,
    2. complété des données manquantes,
    3. scalé
    4. encodé
    """
    # On nettoie la données
    if prod:
        df = fake_imputer(df)

    df_clean = classic_clean(df)
    target_col = "classe_bilan_dpe"

    # On définit les features et la target
    X = df_clean.drop(columns=[target_col, "geom_groupe", "batiment_groupe_id"])
    y = df_clean[target_col]

    if prod:
        preprocessor = load_preprocessor(True)
        X_train_preproc = preprocessor.transform(X)
        return X_train_preproc

    # On transforme les features et la target
    # ----------------------------------------------
    # target
    # ----------------------------------------------
    label_encoder = LabelEncoder()
    label_encoder.fit(y)
    save_encoder(label_encoder)
    y_encoded = label_encoder.transform(y)

    # ----------------------------------------------
    # features
    # ----------------------------------------------
    # On instancie le preprocessor
    preprocessor = create_preprocessor(df=X)

    # On split la donnée Train vs Test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=split_ratio
    )

    # On transforme les features
    preprocessor.fit(X_train)
    save_preprocessor(preprocessor)
    X_train_preproc = preprocessor.transform(X_train)
    X_test_preproc = preprocessor.transform(X_test)

    print(preprocessor.get_feature_names_out())

    return X_train_preproc, X_test_preproc, y_train, y_test


def fake_imputer(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fake missing values for demo purposes
    """
    mat_mur_txt = "PIERRE"
    mat_toit_txt = "TUILES"
    gaz_conso_tot = 342642
    gaz_conso_tot_par_pdl = 76438
    annee_construction = 1915
    nb_log = 21
    elec_conso_tot = 143393
    elec_conso_tot_par_pdl = 10483

    df = df.replace("nan", np.nan)

    if df.isnull().values.any():
        df["mat_mur_txt"] = df["mat_mur_txt"].fillna(mat_mur_txt)
        df["mat_toit_txt"] = df["mat_toit_txt"].fillna(mat_toit_txt)
        df["gaz_conso_tot"] = df["gaz_conso_tot"].fillna(gaz_conso_tot)
        df["gaz_conso_tot_par_pdl"] = df["gaz_conso_tot_par_pdl"].fillna(
            gaz_conso_tot_par_pdl
        )
        df["annee_construction"] = df["annee_construction"].fillna(annee_construction)
        df["nb_log"] = df["nb_log"].fillna(nb_log)
        df["elec_conso_tot"] = df["elec_conso_tot"].fillna(elec_conso_tot)
        df["elec_conso_tot_par_pdl"] = df["elec_conso_tot_par_pdl"].fillna(
            elec_conso_tot_par_pdl
        )
    return df
