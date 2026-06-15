import hashlib
import threading
import time
from flask import Flask, jsonify, request, Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

REQUEST_COUNT = Counter("http_requests_total", "Total requetes", ["endpoint"])
REQUEST_LATENCY = Histogram("http_request_duration_seconds", "Latence", ["endpoint"])
CACHE_SIZE = Gauge("app_cache_size_mb", "Taille cache MB")

cache = []
_leak_active = False
_leak_lock = threading.Lock()


def _leak_worker(rate_mb_per_sec):
    global _leak_active
    interval = 1.0 / rate_mb_per_sec
    while _leak_active:
        cache.append("X" * 1_000_000)
        CACHE_SIZE.set(len(cache))
        time.sleep(interval)


@app.route("/")
def index():
    start = time.time()
    data = b"stress"
    for _ in range(20_000):
        data = hashlib.sha256(data).digest()
    cache.append("X" * 1_000_000)
    CACHE_SIZE.set(len(cache))
    REQUEST_LATENCY.labels(endpoint="/").observe(time.time() - start)
    REQUEST_COUNT.labels(endpoint="/").inc()
    return jsonify({"status": "ok", "cache_mb": len(cache)})


@app.route("/leak")
def leak():
    # Demarre un thread qui alloue N MB/s en arriere-plan -> courbe RAM lisse sur Grafana
    # Parametre: ?rate=1  (MB par seconde, defaut 1)
    global _leak_active
    rate = int(request.args.get("rate", 1))
    rate = max(1, min(rate, 20))

    with _leak_lock:
        if _leak_active:
            return jsonify({"status": "already_leaking", "cache_mb": len(cache)})
        _leak_active = True
        t = threading.Thread(target=_leak_worker, args=(rate,), daemon=True)
        t.start()

    REQUEST_COUNT.labels(endpoint="/leak").inc()
    return jsonify({"status": "leaking", "rate_mb_per_sec": rate,
                    "estimated_oom_seconds": max(0, (256 - len(cache)) // rate)})


@app.route("/leak/stop")
def leak_stop():
    global _leak_active
    _leak_active = False
    return jsonify({"status": "stopped", "cache_mb": len(cache)})


@app.route("/bomb")
def bomb():
    # Alloue 10 MB instantanement (demo rapide)
    start = time.time()
    for _ in range(10):
        cache.append("X" * 1_000_000)
    CACHE_SIZE.set(len(cache))
    REQUEST_LATENCY.labels(endpoint="/bomb").observe(time.time() - start)
    REQUEST_COUNT.labels(endpoint="/bomb").inc()
    return jsonify({"status": "ok", "cache_mb": len(cache)})


@app.route("/reset")
def reset():
    global _leak_active
    _leak_active = False
    freed = len(cache)
    cache.clear()
    CACHE_SIZE.set(0)
    return jsonify({"status": "reset", "freed_mb": freed})


@app.route("/health")
def health():
    return jsonify({"status": "ok", "cache_mb": len(cache), "leaking": _leak_active})


@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


app.run(host="0.0.0.0", port=8080, threaded=True)
