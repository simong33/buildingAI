import pandas as pd

from sklearn.preprocessing import RobustScaler, MinMaxScaler,LabelEncoder,OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split

from app.params import *

def classic_clean(df:pd.DataFrame,)->pd.DataFrame:
    data = df.copy()
    #On retire les ligne duppliquées
    clean_data = data.drop_duplicates()

    return clean_data

def create_preprocessor()->ColumnTransformer:
    """
    Cette fonction permet de créer un preprocessor qui intègre les dfférentes catégories de columns
    """

    #Mapping columns
    mapping = pd.DataFrame.from_dict(COLUMNS_TO_KEEP,columns=['type','scale','impute'])

    #On prépare les imputers
    str_imputer = SimpleImputer(strategy='constant',fill_value='INDETERMINE')
    num_imputer = SimpleImputer(strategy='mean')

    #On définit les différent pipelines
    #Pour le moment quatre pipelines : num + ordinal + categorical

    #NUM - Robuts
    selection = (mapping.type=='num'& mapping.scale=='robust')
    cols_num_r = list(mapping[selection].index)
    r_scale = RobustScaler()
    num_robust_pipe = make_pipeline(num_imputer,r_scale)



    #NUM - MinMax
    selection = (mapping.type=='num'& mapping.scale=='minmax')
    cols_num_mm = list(mapping[selection].index)
    mm_scale = MinMaxScaler()
    num_minmax_pipe = make_pipeline(num_imputer,
                                    mm_scale
                                    )

    #CAT
    selection = (mapping.type=='cat')
    cols_cat = list(mapping[selection].index)
    ohe = OneHotEncoder()
    cat_pipe = make_pipeline(str_imputer,
                             ohe
                             )

    #On assemble les différents pipes
    final_preprocessor = ColumnTransformer(
        [
            ('numerical_cols_r',num_robust_pipe,cols_num_r),
            ('numerical_cols_mm',num_minmax_pipe,cols_num_mm),
            ('categorical_cols',cat_pipe,cols_cat)
        ],
        n_jobs=-1,
        remainder='passthrough'
    )

    return final_preprocessor

def preprocess(df: pd.DataFrame, split_ratio:float)-> tuple:
    """
    Input : dataframe
    Output : tuple X_train, y_train, X_test, y_test
    Cette fonction produit un dataframe :
    1. nettoyé,
    2. complété des données manquantes,
    3. scalé
    4. encodé
    """
    #On nettoie la données
    df_clean = classic_clean(df)

    #On définit les features et la target
    X = df_clean.drop(columns='class_bilan_dpe')
    y = df_clean['class_bilan_dpe']

    #On transforme les features et la target
    #----------------------------------------------
    #target
    #----------------------------------------------
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)

    #----------------------------------------------
    #features
    #----------------------------------------------
    #On instancie le preprocessor
    preprocessor = create_preprocessor()

    #On split la donnée Train vs Test
    X_train, y_train, X_test, y_test = train_test_split(X,y_encoded,test_size=split_ratio)

    #On transforme les features
    preprocessor.fit(X_train)

    X_train_preproc = preprocessor.transform(X_train)
    X_test_preproc = preprocessor.transform(X_test)

    return X_train_preproc, y_train, X_test_preproc, y_test
