# UTS Aggregator

## Build
docker build -t uts-aggregator .

## Run
docker run --rm -p 8080:8080 uts-aggregator

## Endpoints
POST /publish
GET  /events?topic=...
GET  /stats

## Run tests (locally, not in container)
pip install -r requirements.txt
pytest -q

## Stress test
# Ensure service running at localhost:8080
python3 stress/stress_test.py
