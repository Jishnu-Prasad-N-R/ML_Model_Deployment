# ML Model Deployment as a Monitored REST API
# Iris Species Classifier

## Overview

This project takes a trained ML model and turns it into a REST API that
other programs can call over the internet — with input validation and
monitoring — instead of just running predictions inside a notebook.

## Dataset & Problem

Using scikit-learn's built-in Iris dataset (load_iris()) — The model
classifies a flower into one of three species (setosa, versicolor,
virginica) based on four measurements: sepal length, sepal width, petal
length, and petal width.

## API Contract

The /predict endpoint takes in four measurements of an iris flower —
its sepal length, sepal width, petal length, and petal width — and tells
you which of three species (setosa, versicolor, or virginica) the flower
most likely belongs to, along with a confidence score showing how sure
the model is about that answer.

In Technically: it accepts a POST request with four numeric fields
(sepal_length, sepal_width, petal_length, petal_width) and
returns the predicted species along with a confidence score.

## Request Flow

1. Client sends a  POST  request to  /predict  with the 4 measurements.
2. Pydantic validates that all fields are present and are the correct type.
3. If invalid, FastAPI automatically returns a  422  error, and the model never runs.
4. If valid, the pre-loaded model runs  model.predict()  to get the species, and  model.predict_proba()  to get the confidence score.
5. The API returns the prediction and confidence as a JSON response.

## Tech Stack (planned)

Python 3.11+, FastAPI, Pydantic, Uvicorn, scikit-learn, pytest, Docker, Prometheus

## v2 Design Plan (Task 10 Challenge) 

If /api/v2/predict needed to return an extra field — for example,
a full per-class probability breakdown instead of just the top
confidence score — here is what would change, and what would NOT:

1. A new PredictionOutputV2 schema would be added to schemas.py.
   The existing PredictionOutput would stay untouched, since any
   client still calling /api/v1/predict is relying on that exact
   shape never changing.

2. A new file, app/routers/v2.py, would be created with its own
   APIRouter(prefix="/api/v2"). It would NOT reuse v1's router or
   modify v1.py — v1 and v2 live side by side, independently.

3. The model itself, and the shared ml_models state, would be
   reused as-is — versioning applies to the API's request/response
   CONTRACT, not to the underlying model or business logic.

4. In main.py, the new router would simply be included alongside
   the existing one: app.include_router(v2_router).

   This way, existing v1 clients are never affected by v2 changes —
   which is the entire point of versioning.