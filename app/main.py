from contextlib import asynccontextmanager
from fastapi import FastAPI
import joblib

from app.models.schemas import PredictionInput

ml_models = {}

species_names = ["setosa", "versicolor", "virginica"]

@asynccontextmanager

async def lifespan(app: FastAPI):
    
    ml_models["pipeline"] = joblib.load("ml/saved_model/model.joblib")
    
    print("Model loaded successfully")
    
    yield
    
    ml_models.clear()
    
app = FastAPI(lifespan=lifespan)

@app.get("/")

def root():
    
    return {"message": "ML API is alive"}

@app.post("/predict")

def predict(data: PredictionInput):
    
    features = [[
        
        data.sepal_length,
        data.sepal_width,
        data.petal_length,
        data.petal_width,
        
    ]]
    
    prediction = ml_models["pipeline"].predict(features)
    
    species = species_names[prediction[0]]
    
    return {"prediction": species}
