from sklearn.neighbors import KNeighborsClassifier
from app.ml_logic.preprocess import preprocess
from app.params import LOCAL_DATA_PATH
import pandas as pd


def build_model():
    """
    Build model.
    """
    model = initialize_model()
    df = pd.read_csv(f"{LOCAL_DATA_PATH}/dpe.csv")
    X_train, X_test, y_train, y_test = preprocess(df)
    model = train_model(model, X_train, y_train)
    return model


def initialize_model():
    """
    Initialize model.
    """
    model = KNeighborsClassifier()
    return model


def train_model(model, X_train, y_train):
    """
    Train model.
    """
    model.fit(X_train, y_train)
    print("Model trained.")
    return model
