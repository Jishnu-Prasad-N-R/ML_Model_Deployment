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