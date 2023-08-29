BDNB_FILES_URI = "https://open-data.s3.fr-par.scw.cloud/bdnb_millesime_2022-10-d/"

UNRELEVANT_TABLES = [
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
    "batiment_groupe_dpe_logtype" "batiment_groupe_dvf_logtype",
    "batiment_groupe_dvf_open_representatif",
    "batiment_groupe_dvf_open_statistique",
    "batiment_groupe_energie",
    "batiment_groupe_enepdl",
    "batiment_groupe_enethermo",
    "batiment_groupe_exposition_bruit_logement_social",
    "batiment_groupe_geospx",
    "batiment_groupe_hthd",
    "batiment_groupe_merimee",
    "batiment_groupe_osm_building",
    "batiment_groupe_pie",
    "batiment_groupe_proprietaire",
    "adresse", #sauf si cle_interop_adr nécessaire
    "adresse_metrique",
    "batiment", #inaccessible
    "batiment_groupe_adresse",
    "batiment_groupe_bdtopo_equ", # détail gare métro etc ..
    "batiment_groupe_bdtopo_zoac", # détail lieu public
    "batiment_groupe_bpe", #détail activité au sein d'un batiment (psy, supermarché etc..)
    "batiment_groupe_dle_elec_2020",#compris dans dle_elec_multimillesime
    "batiment_groupe_dle_gaz_2020",#compris dans dle_gaz_multimillesime
    "batiment_groupe_dle_reseaux_2020"#compris dans dle_reseaux_multimillesime
]
RELEVANT_FILES_SIMON = ["batiment_groupe_rnc", "dpe_logement"]

RELEVANT_FILES_THOMAS= [
    "batiment_construction",# batiment_groupe_id,batiment_construction_id, geometry, alitude, hauteur
    "batiment_groupe",#batiment_groupe_id , s_geom_groupe, geom_groupe
    "batiment_groupe_argiles",#batiment_groupe_id, alea  -> exposition aux risques climatiques du batiment
    "batiment_groupe_bdtopo_bat",#batiment_groupe_id, l_etat -> en projet; en construction, hauteur_mean, altitude_sol_mean
    "batiment_groupe_dle_elec_multimillesime",#batiment_groupe_id et données conso
    "batiment_groupe_dle_gaz_multimillesime",#batiment_groupe_id et données conso
    "batiment_groupe_dle_reseaux_multimillesime"#batiment_groupe_id et données conso
]


dict_ffo_bat = {
    'annee_construction':['num','minmax','mean_geo'],
    'mat_mur_txt':['cat','oeh','knn_cat'],
    'mat_toit_txt':['cat','oeh','knn_cat'],
    'nb_log':['num','robust','mean_geo'],
    'geom_groupe' : ['Multypolygon','',''], #batiment group 70k lignes 1.3%de null sur paris
    'elec_conso_tot_par_pdl': ['num','RobustScaler',''], #dle_elec 207653 lignes, Si on garde le max du couple (id, millesime ): 52976 dont 98% sont de 2021
    'elec_conso_tot': ['num','RobustScaler',''],
    'gaz_conso_tot_par_pdl': ['num','RobustScaler',''],#dle_gaz 55178 lignes, Si on garde le max du couple (id, millesime ): 19825 dont 89% sont de 2021
    'gaz_conso_tot': ['num','RobustScaler',''],
    'res_conso_tot_par_pdl': ['num','RobustScaler',''],#dle reseaux 8131 lignes, Si on garde le max du couple (id, millesime ): 4852 dont 99% sont de 2021
    'res_conso_tot': ['num','RobustScaler',''],
}
