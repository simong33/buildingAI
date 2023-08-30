import pandas as pd

from sklearn.preprocessing import RobustScaler, StandardScaler, MinMaxScaler,LabelEncoder,OneHotEncoder
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

def gen_pipe(df:pd.DataFrame,mapping:pd.DataFrame,scaler:str):

    num_imputer = SimpleImputer(strategy='mean')

    selection = (mapping.type=='num') & (mapping.scale==scaler)

    cols = list(mapping[selection].index)
    cols = [
    col for col in df.columns
    if col in cols or len([c for c in cols if c in col])>0
    ]

    match scaler :
        case 'RobustScaler':
            scaler = RobustScaler()
        case 'StandardScaler':
            scaler = RobustScaler()
        case _:
            scaler = MinMaxScaler()

    num_pipe = make_pipeline(num_imputer,scaler)

    return num_pipe, cols

def create_preprocessor(df:pd.DataFrame)->ColumnTransformer:
    """
    Cette fonction permet de créer un preprocessor qui intègre les dfférentes catégories de columns
    """

    #Mapping columns
    mapping = pd.DataFrame.from_dict(COLUMNS_TO_KEEP,
                                     orient='index',
                                     columns=['type',
                                              'scale',
                                              'impute'
                                              ]
                                     )

    #On définit les différent pipelines
    #Pour le moment quatre pipelines : num + ordinal + categorical

    #NUM - Robuts
    num_robust_pipe,cols_num_r = gen_pipe(df,mapping,'RobustScaler')

    #NUM - MinMax
    num_minmax_pipe,cols_num_mm = gen_pipe(df,mapping,'MinMaxScaler')

    #NUM - Standard
    num_standard_pipe,cols_num_std = gen_pipe(df,mapping,'StandardScaler')


    #CAT
    #On prépare les imputers
    str_imputer = SimpleImputer(strategy='constant',
                                fill_value='INDETERMINE')

    selection = (mapping.type=='cat')
    cols_cat = list(mapping[selection].index)
    ohe = OneHotEncoder(sparse_output=False)
    cat_pipe = make_pipeline(str_imputer,
                             ohe
                             )

    #On assemble les différents pipes
    final_preprocessor = ColumnTransformer(
        [
            ('numerical_cols_r',num_robust_pipe,cols_num_r),
            ('numerical_cols_mm',num_minmax_pipe,cols_num_mm),
            ('numerical_cols_std',num_standard_pipe,cols_num_std),
            ('categorical_cols',cat_pipe,cols_cat)
        ],
        n_jobs=-1,
        remainder='drop'
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
    target_col = 'classe_bilan_dpe'

    #On définit les features et la target
    X = df_clean.drop(columns=[target_col, 'geom_groupe','batiment_groupe_id'])
    y = df_clean[target_col]

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
    preprocessor = create_preprocessor(df=X)

    #On split la donnée Train vs Test
    X_train, X_test, y_train, y_test = train_test_split(X,
                                                        y_encoded,
                                                        test_size=split_ratio)

    #On transforme les features
    preprocessor.fit(X_train)

    X_train_preproc = preprocessor.transform(X_train)
    X_test_preproc = preprocessor.transform(X_test)

    print(preprocessor.get_feature_names_out())

    return X_train_preproc, X_test_preproc, y_train, y_test
