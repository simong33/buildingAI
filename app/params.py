BDNB_FILES_URI = "https://open-data.s3.fr-par.scw.cloud/bdnb_millesime_2022-10-d/"
UNRELEVANT_TABLES_SIMON = [
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
]
RELEVANT_FILES_SIMON = ["batiment_groupe_rnc", "dpe_logement"]
UNRELEVANT_TABLES = []

UNRELEVANT_TABLES_THOMAS = [
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

RELEVANT_FILES_THOMAS= [
    "batiment_construction",# batiment_groupe_id,batiment_construction_id, geometry, alitude, hauteur
    "batiment_groupe",#batiment_groupe_id , s_geom_groupe, geom_groupe
    "batiment_groupe_argiles",#batiment_groupe_id, alea  -> exposition aux risques climatiques du batiment
    "batiment_groupe_bdtopo_bat",#batiment_groupe_id, l_etat -> en projet; en construction, hauteur_mean, altitude_sol_mean
    "batiment_groupe_dle_elec_multimillesime",#batiment_groupe_id et données conso
    "batiment_groupe_dle_gaz_multimillesime",#batiment_groupe_id et données conso
    "batiment_groupe_dle_reseaux_multimillesime"#batiment_groupe_id et données conso
]
