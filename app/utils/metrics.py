
from prometheus_client import Counter, Histogram

# WhatsApp Metrics
whatsapp_requests = Counter('whatsapp_requests_total', 'Total WhatsApp API requests')
whatsapp_latency = Histogram('whatsapp_request_latency_seconds', 'WhatsApp API latency')

# Instagram Metrics
instagram_requests = Counter('instagram_requests_total', 'Total Instagram API requests')
instagram_latency = Histogram('instagram_request_latency_seconds', 'Instagram API latency')