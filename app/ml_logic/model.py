from sklearn.neighbors import KNeighborsClassifier
from app.ml_logic.preprocess import preprocess
from app.ml_logic.data import load_dataframe
from app.params import LOCAL_DATA_PATH
import pandas as pd
from lightgbm import LGBMClassifier


def build_model():
    """
    Build model.
    """
    model = initialize_model()
    df = load_dataframe()
    X_train, X_test, y_train, y_test = preprocess(df)
    model = train_model(model, X_train, y_train)
    return model


def initialize_model():
    """
    Initialize model.
    """
    model = LGBMClassifier()
    return model


def train_model(model, X_train, y_train):
    """
    Train model.
    """
    model.fit(X_train, y_train)
    print("Model trained.")
    return model
