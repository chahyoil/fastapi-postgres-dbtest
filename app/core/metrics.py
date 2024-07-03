
from prometheus_client import Counter, Histogram
import time

REQUEST_COUNT = Counter(
    'request_count', 'App Request Count',
    ['app_name', 'method', 'endpoint', 'http_status']
)
REQUEST_LATENCY = Histogram(
    'request_latency_seconds', 'Request latency',
    ['app_name', 'endpoint']
)

def start_timer():
    return time.time()

def record_request_data(app_name, request, response, latency):
    REQUEST_COUNT.labels(
        app_name,
        request.method,
        request.url.path,
        response.status_code
    ).inc()
    REQUEST_LATENCY.labels(app_name, request.url.path).observe(latency)