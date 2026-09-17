# Testing Report

## Integration Testing

`tests/integration/test_integration.py` was run against the live Docker container, started with:

```bash
docker compose up --build
```

The tests make real `httpx` calls against the running container at `http://localhost:8000`, covering:

- `/api/v1/health`
- `/api/v1/predict`
- `/api/v1/predict-batch`
- `/metrics`

**Result:** `4 passed`

This verified that the dockerized API works correctly end-to-end, not just in isolated unit tests.

---

## Load Testing

`scripts/load_test.py` sends concurrent requests to `/api/v1/predict`. It must be run with:

```bash
python -m scripts.load_test
```

(Running it as `python scripts/load_test.py` fails with `ModuleNotFoundError`, since the script imports `app.config` and needs the project root on the import path.)

### Single Request (baseline)

```
Total requests: 1
Successful requests: 1
Failed requests: 0
Total test time: 0.3577 sec
Average response time: 0.3548 sec
```

### 100 Concurrent Requests — Run 1

```
Total requests: 100
Successful requests: 100
Failed requests: 0
Total test time: 3.9016 sec
Average response time: 3.7642 sec
Fastest response: 3.3653 sec
Slowest response: 3.8410 sec
```

### 100 Concurrent Requests — Run 2

```
Total requests: 100
Successful requests: 100
Failed requests: 0
Total test time: 7.4784 sec
Average response time: 7.1309 sec
Fastest response: 5.5696 sec
Slowest response: 7.3601 sec
```

**Observation:** The API handled all 201 total requests across every run with zero failures. However, average response time under identical 100-concurrent-request conditions nearly doubled between Run 1 (3.76s) and Run 2 (7.13s). This is a genuine, unresolved anomaly worth noting rather than glossing over. The most likely explanation is thread pool saturation carrying over between back-to-back load tests — FastAPI runs synchronous route handlers in a limited-size thread pool, so requests queue once that pool is under sustained pressure. Confirming this would require re-running the test with a cooldown period between runs; it is noted here as a follow-up rather than fully resolved in this pass.

---

## Health Check

After load testing, `GET /api/v1/health` returned:

```json
{"status": "ok", "model_loaded": true}
```

Confirming the API and the loaded model remained healthy throughout testing.

---

## Metrics Verification

`/metrics` was checked after testing and confirmed to be correctly counting successful predictions:

```
ml_predictions_total{model_version="v1",predicted_class="versicolor"} 101.0
ml_predictions_total{model_version="v1",predicted_class="setosa"} 2.0
```

This shows 101 successful `versicolor` predictions and 2 successful `setosa` predictions recorded for model version `v1`.

---

## Issue Found

While `/api/v1/predict-batch` returned correct predictions to the client, it was **not** incrementing the `ml_predictions_total` custom Prometheus counter. Individual calls to `/api/v1/predict` were counted correctly, but predictions made through the batch endpoint were invisible to monitoring — meaning real prediction volume would have been silently undercounted in any dashboard relying on this metric.

## Fix Applied

Added the missing counter increment inside the batch endpoint's result-building loop in `app/routers/v1.py`, so every item in a batch is now counted individually, the same way a single `/predict` call is:

```python
species = species_names[pred]
prediction_counter.labels(predicted_class=species, model_version=model_version).inc()
```

## Fix Verification

**Before fix:** calling `/api/v1/predict-batch` did not change any `ml_predictions_total` values, even though predictions were returned correctly to the client.

**After fix:** calling `/api/v1/predict-batch` with 2 items increased the corresponding `ml_predictions_total` counters by 2, confirmed by checking `/metrics` before and after the call.

---

## Conclusion

The containerized API passes integration testing against a real running instance, handles 100+ concurrent requests without failures, and one genuine monitoring gap (missing batch metrics) was found and fixed, with the fix verified through direct observation of `/metrics` before and after the change. The unexplained latency increase between load test runs is documented above as a known area for further investigation.