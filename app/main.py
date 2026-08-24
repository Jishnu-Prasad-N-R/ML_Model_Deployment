from contextlib import asynccontextmanager
from fastapi import FastAPI
import joblib

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

def predict(data: dict = {
    
    "sepal_length": 6.0,
    "sepal_width": 2.7,
    "petal_length": 4.5,
    "petal_width": 1.5,
    
    }):
    
    features = [[
        
        data["sepal_length"],
        data["sepal_width"],
        data["petal_length"],
        data["petal_width"],
        
    ]]
    
    prediction = ml_models["pipeline"].predict(features)
    
    species = species_names[prediction[0]]
    
    return {"prediction": species}
