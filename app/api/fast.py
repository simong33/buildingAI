import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.ml_logic.preprocess import preprocess, load_encoder

from app.ml_logic.registry import load_model
from app.ml_logic.data import get_building_df

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.model = load_model()


@app.get("/predict")
def predict(
    building_id: str,
):
    """
    Predict class of a building.
    """
    model = app.state.model
    try:
        X_pred = get_building_df(building_id)
        X_pred_preproc = preprocess(X_pred, 0.2, True)
        y_pred = model.predict(X_pred_preproc)
        le = load_encoder()
        pred = y_pred.tolist()[0]
        letter = le.inverse_transform([pred])[0]
        return {"classe": letter}
    except Exception as e:
        print(e)
        return {"prediction": "error", "error": e}


@app.get("/")
def root():
    json = {"greeting": "Hello"}
    return json
