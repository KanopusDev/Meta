
import time
from functools import wraps
from prometheus_client import Counter, Histogram
import sentry_sdk
from app.core.config import settings

# Initialize Sentry
if settings.SENTRY_DSN:
    sentry_sdk.init(dsn=settings.SENTRY_DSN, environment=settings.ENVIRONMENT)

def monitor_request(counter: Counter, histogram: Histogram):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                counter.inc()
                return result
            finally:
                duration = time.time() - start_time
                histogram.observe(duration)
        return wrapper
    return decorator