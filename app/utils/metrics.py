from prometheus_client import Counter, Histogram
from functools import lru_cache

@lru_cache()
def get_metrics():
    """Get or create metrics singleton to avoid duplicate registration"""
    return {
        'whatsapp_requests': Counter('whatsapp_requests_total', 'Total WhatsApp API requests'),
        'whatsapp_latency': Histogram('whatsapp_request_latency_seconds', 'WhatsApp API latency'),
        'instagram_requests': Counter('instagram_requests_total', 'Total Instagram API requests'),
        'instagram_latency': Histogram('instagram_request_latency_seconds', 'Instagram API latency')
    }