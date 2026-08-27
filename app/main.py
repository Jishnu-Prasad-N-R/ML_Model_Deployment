from contextlib import asynccontextmanager
from fastapi import FastAPI,HTTPException,Request
from fastapi.responses import JSONResponse
import joblib
import uuid
from app.models.schemas import PredictionInput,PredictionOutput

ml_models = {}

species_names = ["setosa", "versicolor", "virginica"]

model_version = "v1"

@asynccontextmanager

async def lifespan(app: FastAPI):
    
    ml_models["pipeline"] = joblib.load("ml/saved_model/model.joblib")
    
    print("Model loaded successfully")
    
    yield
    
    ml_models.clear()
    
app = FastAPI(lifespan=lifespan)

@app.exception_handler(ValueError)

async def value_error_handler(request : Request, exception : ValueError):

    print(f"ValueError caught: {exception}")
    
    return JSONResponse(
        
        status_code=500,
    
        content={"detail": "Internal error or server error occur while processing the prediction"},
    )
    
@app.get("/")

def root():
    
    return {"message": "ML API is alive"}

@app.get("/health")

def health():
    
    model_loaded = "pipeline" in ml_models
    
    return {"status":"ok","model_loaded":model_loaded}

@app.post("/predict",response_model=PredictionOutput)

def predict(data: PredictionInput):
    
    features = [[
        
        data.sepal_length,
        data.sepal_width,
        data.petal_length,
        data.petal_width,
        
    ]]
    
    try:
    
        prediction = ml_models["pipeline"].predict(features)
    
        probabilities = ml_models["pipeline"].predict_proba(features)
    
    except ValueError:
        
        raise
    
    except Exception as error:
        
        print(f"Prediction error: {error}")
        
        raise HTTPException(status_code=500, detail="Prediction failed") from error
        
    confidence = float(max(probabilities[0]))
    
    request_id = str(uuid.uuid4())
    
    species = species_names[prediction[0]]
    
    return {
        
            "prediction": species,
            "confidence":confidence,
            "request_id":request_id,
            "model_version":model_version
            
            }
