import time
from functools import wraps
from prometheus_client import Counter, Histogram
import sentry_sdk
from app.core.config import settings
from app.utils.metrics import get_metrics

# Initialize Sentry
if settings.SENTRY_DSN:
    sentry_sdk.init(dsn=settings.SENTRY_DSN, environment=settings.ENVIRONMENT)

def monitor_request(counter_metric=None, latency_metric=None):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            metrics = get_metrics()
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                if counter_metric:
                    metrics[counter_metric].inc()
                return result
            finally:
                if latency_metric:
                    metrics[latency_metric].observe(time.time() - start_time)
        return wrapper
    return decorator

# WhatsApp Metrics

whatsapp_requests = Counter('whatsapp_requests_total', 'Total WhatsApp API requests')
whatsapp_latency = Histogram('whatsapp_request_latency_seconds', 'WhatsApp API latency')

# Instagram Metrics

instagram_requests = Counter('instagram_requests_total', 'Total Instagram API requests')
instagram_latency = Histogram('instagram_request_latency_seconds', 'Instagram API latency')

# Sentry Metrics

sentry_errors = Counter('sentry_errors_total', 'Total Sentry errors')
sentry_latency = Histogram('sentry_request_latency_seconds', 'Sentry API latency')

# Monitor WhatsApp requests

def monitor_whatsapp_request(func):
    return monitor_request(whatsapp_requests, whatsapp_latency)(func)

# Monitor Instagram requests

def monitor_instagram_request(func):
    return monitor_request(instagram_requests, instagram_latency)(func)
