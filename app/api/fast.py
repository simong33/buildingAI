import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.ml_logic.preprocess import preprocess

# from app.ml_logic.registry import load_model

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/predict")
def predict():
    """
    Predict class of a building.
    """
    # X_pred
    # X_pred_preproc = preprocess(X_pred)
    try:
        # y_pred = app.state.model.predict(X_pred_preproc)
        # y_pred_to_dict = y_pred.tolist()
        y_pred = "F"
        return {"classe": y_pred}
    except Exception as e:
        print(e)
        return {"prediction": "error", "error": e}


@app.get("/")
def root():
    json = {"greeting": "Hello"}
    return json
