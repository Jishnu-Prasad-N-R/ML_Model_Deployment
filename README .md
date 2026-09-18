# ML Model Deployment as a Monitored REST API

## Iris Species Classifier

## Overview

This project turns a trained machine learning model into a production-style REST API using **FastAPI**.

The API accepts Iris flower measurements, validates the input, performs inference using a **scikit-learn** model, and returns predictions through versioned endpoints.

The project also includes:

* Pydantic input validation
* API versioning
* API-key authentication
* Batch prediction
* Structured logging
* Configuration management
* Prometheus monitoring
* Automated testing
* Integration testing
* Load testing
* Docker and Docker Compose
* Continuous integration via GitHub Actions

The goal is to demonstrate the complete process of taking an ML model and turning it into a **secure, tested, monitored, and containerized API service**.

---

## Live Demo

**Live URL:** https://ml-model-deployment-2y62.onrender.com
**Interactive docs:** https://ml-model-deployment-2y62.onrender.com/docs

Deployed on Render's free tier. Free-tier services spin down after ~15 minutes of inactivity, so the first request after a period of idleness may take 30–60 seconds to respond while the container restarts — subsequent requests are fast.

---

## Dataset & Problem

The project uses scikit-learn's built-in **Iris dataset** with `load_iris()`.

The model classifies a flower into one of three species:

* `setosa`
* `versicolor`
* `virginica`

It uses four input features:

* Sepal length
* Sepal width
* Petal length
* Petal width

The trained scikit-learn pipeline is saved using **joblib** and loaded once when the FastAPI application starts.

---

## API Contract

### v1 Prediction Endpoint

**POST** `/api/v1/predict`

### Example Request

```json
{
  "sepal_length": 5.1,
  "sepal_width": 3.5,
  "petal_length": 1.4,
  "petal_width": 0.2
}
```

### Example Response

```json
{
  "prediction": "setosa",
  "confidence": 1.0,
  "request_id": "generated-request-id",
  "model_version": "v1"
}
```

Protected prediction and model-information endpoints require API-key authentication, while public endpoints such as `/api/v1/health` and `/metrics` remain accessible without an API key.

---

## Architecture

```text
Client / Swagger / curl
        ↓
Docker / Uvicorn
        ↓
FastAPI
        ↓
Request Logging Middleware
        ↓
API Key Authentication
        ↓
Pydantic Validation
        ↓
API Router (v1 or v2)
        ↓
Prediction Service (app/service/prediction.py)
        ↓
Scikit-learn Model
        ↓
Prediction Response
        ↓
Structured Logging + Prometheus Metrics
```

The model is loaded once during application startup using FastAPI's **lifespan** mechanism and reused for every prediction request.

---

## Request Flow

The request follows these steps:

1. The client sends a request to the API.
2. FastAPI receives the request.
3. A unique request ID is created in middleware.
4. Protected endpoints verify the `X-API-Key` header.
5. Pydantic validates the input:

   * Data types
   * Allowed ranges
   * Required fields
   * Unexpected fields
6. Invalid input is rejected before the model runs.
7. Valid input is passed to the prediction service.
8. The pre-loaded scikit-learn model performs inference.
9. The API returns the prediction response.
10. Logs and Prometheus metrics are updated.

---

## Tech Stack

| Technology                        | Purpose                     |
| --------------------------------- | --------------------------- |
| Python 3.13                       | Programming language        |
| FastAPI                           | REST API framework          |
| Pydantic                          | Request/response validation |
| pydantic-settings                 | Configuration management    |
| Uvicorn                           | ASGI server                 |
| scikit-learn                      | Machine learning model      |
| joblib                            | Model serialization         |
| httpx                             | HTTP client and testing     |
| pytest                            | Automated testing           |
| Docker                            | Containerization            |
| Docker Compose                    | Container orchestration     |
| prometheus-client                 | Custom Prometheus metrics   |
| prometheus-fastapi-instrumentator | FastAPI monitoring          |
| GitHub Actions                    | Continuous integration      |

---

# API Versioning

## API v1

**POST** `/api/v1/predict`

Returns:

* `prediction`
* `confidence`
* `request_id`
* `model_version`

## API v2

**POST** `/api/v2/predict`

Returns:

* `prediction`
* `probabilities`
* `request_id`
* `model_version`

The v2 endpoint provides a full probability breakdown across all three species.

API versioning allows new response formats to be introduced without breaking clients that still depend on v1.

The v1 router, schema, and behavior were not modified when v2 was added.

---

# API Endpoints

| Method | Endpoint                | Auth | Purpose                            |
| ------ | ----------------------- | ---- | ---------------------------------- |
| GET    | `/`                     | No   | API status                         |
| GET    | `/api/v1/health`        | No   | Health and model status            |
| POST   | `/api/v1/predict`       | Yes  | Single prediction with confidence  |
| POST   | `/api/v1/predict-batch` | Yes  | Batch predictions (1–100 inputs)   |
| GET    | `/api/v1/model-info`    | Yes  | Model metadata                     |
| POST   | `/api/v2/predict`       | Yes  | Prediction with full probabilities |
| GET    | `/metrics`              | No   | Prometheus metrics                 |
| GET    | `/docs`                 | No   | Swagger documentation              |

---

# Security and Validation

Protected endpoints require an `X-API-Key` header.

The API key is stored in `.env` and is never committed to Git.

## Pydantic Validation

Pydantic validation checks:

* Required fields
* Numeric types
* Allowed value ranges
* Unexpected extra fields

Unexpected fields are rejected using:

```python
extra="forbid"
```

Invalid requests are rejected with **HTTP 422** before inference runs.

Missing or incorrect API keys are rejected with **HTTP 401**.

---

# Configuration

Configuration is handled using **pydantic-settings** and loaded from `.env`.

| Variable              | Purpose                                          |
| --------------------- | ------------------------------------------------ |
| `API_TITLE`           | Title shown in `/docs`                           |
| `MODEL_PATH`          | Path to the trained model file                   |
| `MODEL_METADATA_PATH` | Path to the model metadata JSON                  |
| `LOG_LEVEL`           | Logging verbosity                                |
| `MAX_BATCH_SIZE`      | Maximum inputs allowed per `/predict-batch` call |
| `API_KEY`             | Secret required for protected endpoints          |
| `ALLOWED_ORIGINS`     | CORS-allowed origins in JSON array format         |

The `.env` file is git-ignored.

The `.env.example` file documents the required variable names without containing real secret values.

On the live deployment, these variables are configured directly in Render's dashboard, not committed to the repository.

---

# Monitoring and Logging

Prometheus metrics are available at:

```text
/metrics
```

The API exposes default HTTP metrics such as:

* Request count
* Request latency
* Request size
* Response size

It also provides a custom metric:

```text
ml_predictions_total
```

This metric tracks successful predictions and is labeled by:

* Predicted class
* Model version

The metric is updated for both single and batch predictions.

## Structured Logging

Structured logs are written to:

```text
Console
app/logs/app.log
```

The application uses rotating file logging.

Logs include information such as:

* Request ID
* HTTP method
* Request path
* HTTP status code
* Request duration
* Prediction outcome
* Errors

---

# Testing

## Run the Full Pytest Suite

```bash
python -m pytest -v
```

---

## Integration Testing

Integration tests are executed against the live, running Docker container.

Start the application:

```bash
docker compose up --build
```

Then run:

```bash
python -m pytest tests/integration/test_integration.py -v
```

### Result

```text
4 passed
```

The integration tests verify:

1. Health endpoint
2. Single prediction
3. Batch prediction
4. Prometheus metrics

These tests run against the **real containerized API**, rather than only testing the application in-process.

---

## Load Testing

The project also includes a basic concurrent load test.

Run it using:

```bash
python -m scripts.load_test
```

The `-m` option is required because the script imports configuration from:

```python
app.config
```

Full load-test results, an observed anomaly between runs, and a genuine bug discovered and fixed during testing are documented in:

```text
TESTING.md
```

---

# Running With Docker Compose

## Prerequisites

Before running the project, install:

* Docker Desktop
* Git

Create `.env` from `.env.example` and provide a real `API_KEY`.

## Start the Application

```bash
docker compose up --build
```

The API will be available at:

```text
http://localhost:8000
```

### Swagger Documentation

```text
http://localhost:8000/docs
```

### Prometheus Metrics

```text
http://localhost:8000/metrics
```

---

## Docker Compose Commands

### Restart Without Rebuilding

```bash
docker compose up
```

### Stop Everything

```bash
docker compose down
```

### Restart Only the API

For example, after replacing a retrained model:

```bash
docker compose restart api
```

---

## Model Volume Mount

The `ml/saved_model` directory is bind-mounted into the container:

```yaml
volumes:
  - ./ml/saved_model:/app/ml/saved_model
```

This means a retrained model can be placed into that directory and loaded after restarting the API.

For example:

```bash
docker compose restart api
```

No Docker image rebuild is required when only the model file is replaced.

Note: this bind-mount behavior applies to local Docker Compose only. The live Render deployment builds directly from the Dockerfile, with `ml/saved_model/` files committed to the repository and baked into the image via `COPY . .`, since Render has no access to a local filesystem to bind-mount.

---

# Local Development Without Docker

Create and activate a virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Create the environment file:

```powershell
cp .env.example .env
```

Train the model:

```powershell
python ml/train.py
```

Start the FastAPI development server:

```powershell
uvicorn app.main:app --reload
```

---

# Example Requests

Replace `http://localhost:8000` with the live URL above to test against the deployed version instead of a local one.

## Health Check

No API key is required.

```bash
curl http://localhost:8000/api/v1/health
```

---

## v1 Prediction

```bash
curl -X POST http://localhost:8000/api/v1/predict \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"sepal_length":5.1,"sepal_width":3.5,"petal_length":1.4,"petal_width":0.2}'
```

---

## v1 Batch Prediction

```bash
curl -X POST http://localhost:8000/api/v1/predict-batch \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"inputs":[{"sepal_length":5.1,"sepal_width":3.5,"petal_length":1.4,"petal_width":0.2}]}'
```

---

## v1 Model Information

```bash
curl -H "X-API-Key: YOUR_API_KEY" \
  http://localhost:8000/api/v1/model-info
```

---

## v2 Prediction

```bash
curl -X POST http://localhost:8000/api/v2/predict \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"sepal_length":5.1,"sepal_width":3.5,"petal_length":1.4,"petal_width":0.2}'
```

---

## Prometheus Metrics

```bash
curl http://localhost:8000/metrics
```

---

# Independent Extension: Continuous Integration with GitHub Actions

A GitHub Actions workflow was added at:

```text
.github/workflows/tests.yml
```

The workflow automatically runs the full pytest suite against the **real running Docker container**, rather than only running in-process tests.

The workflow runs on:

* Every push to `main`
* Every pull request targeting `main`

## CI Workflow

The workflow performs the following steps:

1. Checks out the repository.
2. Installs Python.
3. Installs project dependencies.
4. Trains the model from scratch.
5. Creates a temporary `.env` file for CI.
6. Starts the application using Docker Compose.
7. Waits for `/api/v1/health` to report that the application is ready.
8. Runs the complete test suite.
9. Tears down the containers after testing, regardless of the test result.

This closes an important gap by ensuring that tests are automatically executed against the actual containerized application before changes are merged.

The workflow was successfully verified on GitHub Actions.

---

# What I Learned

Building this project helped me understand that ML deployment involves much more than simply calling:

```python
model.predict()
```

I learned how the following components work together as one complete system:

* FastAPI
* Pydantic validation
* API versioning
* API-key authentication
* Configuration management
* Structured logging
* Prometheus monitoring
* Pytest
* Docker
* Docker Compose
* Integration testing
* Load testing
* Continuous integration

One of the most useful parts of the project was learning the difference between **automated tests, integration tests, and load tests**.

Integration testing showed me how to test the real Dockerized API, while load testing showed how the API behaves when many requests arrive concurrently.

I also learned how monitoring can expose problems that normal prediction testing may not reveal.

For example, monitoring helped identify missing Prometheus counter updates for batch predictions. This was a bug that could not have been discovered simply by checking whether `/predict-batch` returned the expected JSON response.

---

# Project Summary

The project demonstrates a complete ML API deployment workflow:

```text
Train ML Model
      ↓
Save Model with Joblib
      ↓
FastAPI Application
      ↓
Input Validation
      ↓
API Authentication
      ↓
Versioned API Endpoints
      ↓
Prediction Service
      ↓
Scikit-learn Inference
      ↓
Logging + Monitoring
      ↓
Automated Testing
      ↓
Integration Testing
      ↓
Load Testing
      ↓
Docker Containerization
      ↓
Docker Compose
      ↓
GitHub Actions CI
      ↓
Deployed to Render
```

The result is a **secure, versioned, tested, monitored, and containerized REST API for machine learning inference, deployed and publicly reachable.**