# Testing Report

## Integration Testing

The tests/integration/test_integration.py was run against the live Docker container started with

```bash

docker compose up --build

```

The tests make actual httpx calls to the following endpoints

```python

"/api/v1/health",
"/api/v1/predict",
"/api/v1/predict-batch",
"/metrics"

```

Test Results

```

4 passed

```

This verified that the dockerized api works correctly end-to-end.

---

## Load Testing

The scripts/load_test.py was created to make concurrent requests to

```

/api/v1/predict

```

### 100 Concurrent Requests (First Run)

```

Total requests: 100
Successful requests: 100
Failed requests: 0
Total test time: 3.9016 sec
Average response time: 3.7642 sec
Fastest response: 3.3653 sec
Slowest response: 3.8410 sec

```

### Single Request Test

```

Total requests: 1
Successful requests: 1
Failed requests: 0
Total test time: 0.3577 sec
Average response time: 0.3548 sec
Fastest response: 0.3548 sec
Slowest response: 0.3548 sec

```

### 100 Concurrent Requests (Second Run)

```

Total requests: 100
Successful requests: 100
Failed requests: 0
Total test time: 7.4784 sec
Average response time: 7.1309 sec
Fastest response: 5.5696 sec
Slowest response: 7.3601 sec

```

The API handled all requests successfully without any failures. It can be seen that the response time increases
significantly when sending a higher number of concurrent requests.

---

## Health Check

After performing the load test, a GET request to

```

/api/v1/health

```

returned

```

{"status":"ok","model_loaded":true}

```

indicating that the API and the ML model are healthy.

---

## Metrics Verification

The metrics endpoint

```

/metrics

```

was checked after testing, and it was confirmed that successful HTTP requests and ML predictions are being counted
correctly by Prometheus.

For example,

```

ml_predictions_total{model_version="v1",predicted_class="versicolor"} 101.0
ml_predictions_total{model_version="v1",predicted_class="setosa"} 2.0

```

indicates that there have been 101 successful predictions for the "versicolor" class and 2 successful predictions
for the "setosa" class using model version "v1".

---

## Issue Found

It was discovered during testing that while the /api/v1/predict-batch endpoint returns predictions correctly, 
it does not count towards the ml_predictions_total custom Prometheus metric.
This means that the ML monitoring is not capturing predictions made via the batch prediction API.

---

## Fix Applied

I fixed the issue by adding the prediction counter inside the loop for processing batch predictions:

```python

species = species_names[pred]
prediction_counter.labels(predicted_class=species,model_version=model_version).inc()

```

calling /api/v1/predict-batch did not change any ml_predictions_total values, even though predictions
were returned correctly. After fix: calling /api/v1/predict-batch with 2 items increased the corresponding 
ml_predictions_total counters by 2, confirmed via /metrics.