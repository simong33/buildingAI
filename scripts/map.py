import pandas as pd
from shapely import wkt, ops
from pyproj import Transformer
from tqdm import tqdm
import json
import os


def save_df_to_geojson(df: pd.DataFrame, batch_size=500):
    if not os.path.exists("raw_data/geojson"):
        os.makedirs("raw_data/geojson")
        df_to_geojson(df, "raw_data/geojson/dpe_initial.geojson", batch_size=batch_size)


def df_to_geojson(df: pd.DataFrame, path: str, batch_size=500):
    """
    Convert a dataframe to a geojson file.
    """
    transformer = Transformer.from_crs("epsg:2154", "epsg:4326", always_xy=True)

    with open(path, "w") as f:
        f.write('{"type": "FeatureCollection", "features": [')

        first_feature = True
        for i in tqdm(range(0, len(df), batch_size), desc="Processing batches"):
            batch = df.iloc[i : i + batch_size]

            for (
                idx,
                row,
            ) in batch.iterrows():  # idx captures the index position of the row
                try:
                    geometry_wkt = (
                        row["geom_groupe"] if pd.notna(row["geom_groupe"]) else None
                    )
                    if geometry_wkt:
                        shape = wkt.loads(geometry_wkt)
                        shape = ops.transform(transformer.transform, shape)
                        geometry = shape.__geo_interface__
                    else:
                        geometry = None
                except Exception as e:
                    print(f"Error with {row['batiment_groupe_id']}")
                    print(e)
                    continue

                if geometry:
                    feature = {
                        "type": "Feature",
                        "id": idx,
                        "properties": {
                            prop: row[prop]
                            for prop in df.columns
                            if prop != "geom_groupe"
                        },
                        "geometry": geometry,
                    }

                    if not first_feature:
                        f.write(",")
                    else:
                        first_feature = False

                    json.dump(feature, f)

        f.write("]}")
