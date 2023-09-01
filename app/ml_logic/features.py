import pandas as pd
import numpy as np

from shapely.geometry import MultiPolygon,Point,Polygon
from shapely.wkt import loads
from shapely.ops import unary_union
from shapely.errors  import GEOSException


import geojson

from shapely import wkt, ops
from pyproj import Transformer
from tqdm import tqdm




#Useless
def assemble_geojson_list(geojson_list):
    # Créer une liste vide pour stocker les features
    features = []
    # Itérer à travers la liste de GeoJSON
    for geojson_obj in geojson_list:
        features.append(geojson_obj)
    # Créer le GeoJSON final avec la liste de features
    final_geojson = {
        'type': 'FeatureCollection',
        'features': features
    }
    return final_geojson





def add_geom_groupe_geo_and_convert_geom_groupe (newdf=None) -> pd.DataFrame:

  transformer = Transformer.from_crs("epsg:2154", "epsg:4326", always_xy=True)

  multipolygon_wkt = newdf['geom_groupe']
  batiments = loads(multipolygon_wkt)
  newbat = []
  count = 0
  for i in range(len(batiments)):
    try :
        newbat.append(ops.transform(transformer.transform, batiments[i]))
    except Exception as e:
        print(f"Error transforming geometry {i}: {e}")
        newbat.append(None)
        count +=1

  newdf['geom_groupe_geo']  = newbat
  newdf['geom_groupe'] = batiments
  print(count)
  return newdf


def add_volume (newdf=None) -> pd.DataFrame:
  newdf['volume_mean']  = newdf['hauteur_mean']*newdf['s_geom_groupe']
  return newdf


def list_unique(liste_de_listes) :
  listes_uniques = set()
  resultat = []
  for lst in liste_de_listes:
    tuple_lst = tuple(lst)  # Convertir la liste en tuple pour permettre l'ajout à un ensemble
    if tuple_lst not in listes_uniques:
        listes_uniques.add(tuple_lst)
        resultat.append(lst)
  return resultat

def est_mitoyen(newdf=None) :  # liste de couple mitoyen
  batiments = newdf['geom_groupe']
  # Liste pour stocker les paires de bâtiments mitoyens ainsi que la liste des batiments mitoyens
  mitoyennete = []
  estmitoyen = []
  # Parcours de chaque paire de bâtiments
  for i in tqdm(range((len(batiments)))):

      # on regarde seulement les batiments dans la même parcelle
      parcelle = newdf['batiment_groupe_id'].iloc[i][:10]
      batiment_parcelle = newdf[newdf['batiment_groupe_id'].str.contains(parcelle)].drop(i)['geom_groupe']

      for j in range(len(batiment_parcelle)):

        try:
            if batiments[i].touches(batiment_parcelle.iloc[j]) or batiments[i].intersects(batiment_parcelle.iloc[j]):
                index_j = batiment_parcelle.index[j]
                tuples = sorted((i, index_j))
                mitoyennete.append(tuples)
                estmitoyen.append(i)
                estmitoyen.append(index_j)

        except GEOSException as e:
                print(f"Error processing building pair {i} and {j}: {e}")
  #newdf['estmitoyen']= newdf.index.isin(list(set(estmitoyen)))

  return mitoyennete

def convert_prof_geo(polygone_prog) : #polygone geo
  transformer = Transformer.from_crs("epsg:2154", "epsg:4326", always_xy=True)
  batiments = polygone_prog
  newbat = ops.transform(transformer.transform, batiments)
  return newbat

def calculate_side_lengths_multipolygon(multipolygon):
    # Liste pour stocker les tailles de côtés de tous les bâtiments
    all_side_lengths = []

    # Itérer à travers les composants du MultiPolygon (bâtiments)
    for polygon in multipolygon.geoms:
        # Coordonnées du bâtiment (Polygon)
        coordinates = list(polygon.exterior.coords)

        # Liste pour stocker les tailles de côtés du bâtiment
        side_lengths = []

        # Calculer la taille de chaque côté du bâtiment
        for i in range(len(coordinates) - 1):
            p1 = Point(coordinates[i])
            p2 = Point(coordinates[i + 1])
            side_length = p1.distance(p2)
            side_lengths.append(side_length)

        all_side_lengths.append(side_lengths)

    return all_side_lengths

def calculate_side_lengths_polygon(polygon):
    # Coordonnées du Polygon
    coordinates = list(polygon.exterior.coords)

    # Liste pour stocker les tailles de côtés
    side_lengths = []

    # Calculer la taille de chaque côté
    for i in range(len(coordinates) - 1):
        p1 = Point(coordinates[i])
        p2 = Point(coordinates[i + 1])
        side_length = p1.distance(p2)
        side_lengths.append(side_length)

    return side_lengths

def intersect_batiment(bat1,bat2) : #retourne la taille du mur mitoyen entre bat1 et bat2
  intersection = bat1.intersection(bat2)
  if intersection.__geo_interface__['type'] == 'Polygon' :
    taille = max(calculate_side_lengths_polygon(intersection))
  elif intersection.__geo_interface__['type'] == 'MultiPolygon' :
    tab_taille = calculate_side_lengths_multipolygon(intersection)
    max_values=[]
    for sublist in tab_taille:
        max_value = max(sublist)  # Trouver le maximum dans la liste actuelle
        max_values.append(max_value)
    taille = sum(max_values)
  elif intersection.__geo_interface__['type'] =='LineString' :
    taille = intersection.length
  elif  intersection.__geo_interface__['type'] =='MultiLineString' :
    total_length = sum(line.length for line in intersection.geoms)

    taille = total_length
  else :
    taille = 0
  return taille

def surface_tour_batiment(bat1,hauteur) :  #retourne la surface du tour du batiment
  cotes = calculate_side_lengths_multipolygon(bat1)
  surface = 0
  for i in range(len(cotes)) :
    for j in cotes[i] :
      surface +=hauteur * j
  return surface

def df_surface_mitoyenne(liste_mitoyen,df) : # retourne un dataframe avec le batiment id, la surface mitoyenne et la surface du tour du batiment
  df_features = pd.DataFrame(columns=['batiment_groupe_id','surface_mitoyenne','surface_batiment'])

  for i in liste_mitoyen :
    hauteur_min = min(df['hauteur_mean'].iloc[i[0]],df['hauteur_mean'].iloc[i[1]])
    a = intersect_batiment(df['geom_groupe'].iloc[i[0]],df['geom_groupe'].iloc[i[1]])
    surface_batiment =   surface_tour_batiment(df['geom_groupe'].iloc[i[0]],df['hauteur_mean'].iloc[i[0]])
    #df_features = df_features.append(pd.DataFrame([[df['batiment_groupe_id'].iloc[i[0]],hauteur_min*a,surface_batiment]], columns=['batiment_groupe_id', 'surface_mitoyenne', 'surface_batiment'])
     #                                     , ignore_index=True)

    df_features = pd.concat([df_features, pd.DataFrame([[df['batiment_groupe_id'].iloc[i[0]],hauteur_min*a,surface_batiment]], columns=['batiment_groupe_id', 'surface_mitoyenne', 'surface_batiment'])
                                          ], ignore_index=True)

  return df_features

def merge_final(df,df_features) : #return le df merge avec les features
  df = df.merge(df_features,how='left',on='batiment_groupe_id')
  return df


def add_features(moncsv) :
    moncsv = add_geom_groupe_geo_and_convert_geom_groupe(moncsv) #converti la colonne geom et ajoute ajoute une colonne geom_geospatiale
    moncsv = add_volume(moncsv)#ajoute le volume du batiments
    breakpoint()

    mitoyennete = est_mitoyen(moncsv)#creer une liste avec les batiments mitoyen
    mitoyennete=list_unique(mitoyennete)#unicité dans la liste précédente


    df_mitoyen_ = df_surface_mitoyenne(mitoyennete,moncsv) #creation d'un dataframe avec les surfaces mitoyenne
    df_mitoyen_ = df_mitoyen_.groupby('batiment_groupe_id').sum('surface_mitoyenne').reset_index()
    df_mitoyen_['percent_mitoyen'] = df_mitoyen_['surface_mitoyenne']/df_mitoyen_['surface_batiment']#creation de la colonne avec mon percent mitoyen
    moncsv= merge_final(moncsv,df_mitoyen_)

    return moncsv


def add_features(moncsv) :
    #moncsv = add_geom_groupe_geo_and_convert_geom_groupe(moncsv) #converti la colonne geom et ajoute ajoute une colonne geom_geospatiale
    moncsv = add_volume(moncsv)#ajoute le volume du batiments


    #breakpoint()

    #mitoyennete = est_mitoyen(moncsv)#creer une liste avec les batiments mitoyen
    #mitoyennete=list_unique(mitoyennete)#unicité dans la liste précédente


    #df_mitoyen_ = df_surface_mitoyenne(mitoyennete,moncsv) #creation d'un dataframe avec les surfaces mitoyenne
    #df_mitoyen_ = df_mitoyen_.groupby('batiment_groupe_id').sum('surface_mitoyenne').reset_index()
    #df_mitoyen_['percent_mitoyen'] = df_mitoyen_['surface_mitoyenne']/df_mitoyen_['surface_batiment']#creation de la colonne avec mon percent mitoyen
    #moncsv= merge_final(moncsv,df_mitoyen_)

    return moncsv
