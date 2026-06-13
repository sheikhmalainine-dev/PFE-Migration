# Flask API

Stress-test application with two endpoints:
- `GET /memory-leak` — allocates memory progressively (never freed)
- `GET /cpu-stress` — runs a CPU-intensive loop

## Build & Run
```bash
docker build -t flask-api .
docker run -p 5000:5000 flask-api
```

## Deploy to K8s
```bash
kubectl apply -f ../manifests/
```
