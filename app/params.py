import os

LOCAL_DATA_PATH = os.path.join(os.path.expanduser("~"), ".lewagon", "mlops", "data")
LOCAL_REGISTRY_PATH = os.path.join(
    os.path.expanduser("~"), ".lewagon", "mlops", "training_outputs"
)
BUCKET_NAME = os.environ.get("BUCKET_NAME")
MODEL_TARGET = "gcs"  # "local" or "gcs"
BDNB_FILES_URI = "https://open-data.s3.fr-par.scw.cloud/bdnb_millesime_2022-10-d/"

DEP_CODES = [69]
CITY_CODES = [
    "06088",
    132,  # Marseille arr.
    6938,  # Lyon arr.
    31555,
    33063,
    34172,
    44109,
    59350,
    67482,
    751,  # Paris prefix of arrondissements
]
UNRELEVANT_TABLES = [
    "dpe_logement",
    "batiment_groupe_dle_reseaux_multimillesime",
    "batiment_construction",
    "qpv",
    "radon",
    "proprietaire",
    "iris_simulations_valeur_verte",
    "local",
    "local_simulation_dpe",
    "parcelle_unifiee",
    "parcelle_unifiee_metrique",
    "bdnb_version",
    "synthese_systeme_energetique_logement",
    "synthese_periode_construction",
    "synthese_enveloppe",
    "simulations_valeur_verte",
    "simulations_dvf",
    "simulations_dpe",
    "batiment_groupe_dvf",
    "batiment_groupe_dpe",
    "batiment_groupe_dpe_logtype",
    "batiment_groupe_dvf_logtype",
    "batiment_groupe_dvf_open_representatif",
    "batiment_groupe_dvf_open_statistique",
    "batiment_groupe_energie",
    "batiment_groupe_enepdl",
    "batiment_groupe_enethermo",
    "batiment_groupe_exposition_bruit_logement_social",
    "batiment_groupe_geospx",
    "batiment_groupe_hthd",
    "merimee",
    "osm_building",
    "batiment_groupe_pie",
    "batiment_groupe_proprietaire",
    "adresse",  # sauf si cle_interop_adr nécessaire
    "adresse_metrique",
    "batiment",  # inaccessible
    "batiment_groupe_adresse",
    "bdtopo_equ",  # détail gare métro etc ..
    "bdtopo_zoac",  # détail lieu public
    "bpe",  # détail activité au sein d'un batiment (psy, supermarché etc..)
    "batiment_groupe_dle_elec_2020",  # compris dans dle_elec_multimillesime
    "batiment_groupe_dle_gaz_2020",  # compris dans dle_gaz_multimillesime
    "batiment_groupe_dle_reseaux_2020",  # compris dans dle_reseaux_multimillesime
]


COLUMNS_TO_KEEP = {
    "classe_bilan_dpe": ["ord", "oe", ""],
    "annee_construction": ["num", "MinMaxScaler", "mean_geo"],
    "mat_mur_txt": ["cat", "oeh", "knn_cat"],
    "mat_toit_txt": ["cat", "oeh", "knn_cat"],
    "nb_log": ["num", "RobustScaler", "mean_geo"],
    "l_usage_1": ["none", "", ""],
    "geom_groupe": [
        "Multypolygon",
        "",
        "",
    ],  # batiment group 70k lignes 1.3%de null sur paris
    "conso_tot_par_pdl": [
        "num",
        "RobustScaler",
        "",
    ],  # dle_elec 207653 lignes, Si on garde le max du couple (id, millesime ): 52976 dont 98% sont de 2021
    "conso_tot": ["num", "RobustScaler", ""],
    # 'gaz_conso_tot_par_pdl': ['num','RobustScaler',''],#dle_gaz 55178 lignes, Si on garde le max du couple (id, millesime ): 19825 dont 89% sont de 2021
    # 'gaz_conso_tot': ['num','RobustScaler',''],
    # 'res_conso_tot_par_pdl': ['num','RobustScaler',''],#dle reseaux 8131 lignes, Si on garde le max du couple (id, millesime ): 4852 dont 99% sont de 2021
    # 'res_conso_tot': ['num','RobustScaler',''],
    "hauteur_mean": ["num", "StandartScaler", "mean avec geom_groupe"],
    "volume_mean" :["num", "StandartScaler", "mean"]
}
DUPLICATE_COLUMNS = [
    "contient_fictive_geom_groupe",
    "annee_construction_dpe",
    "l_annee_construction",
    "batiment_groupe_rnc_nb_log",
]
