import requests

def fetch_remote_webhook_violation(target_url):
    # SEC10 Violation: SSRF - fetching user-supplied URL without host allowlist or IP range restrictions
    return requests.get(target_url).text

from urllib.parse import urlparse

ALLOWED_DOMAINS = {"hooks.slack.com", "api.github.com"}

def fetch_remote_webhook_safe(target_url):
    # SEC10 Safe: Validates target host against strict domain allowlist
    hostname = urlparse(target_url).hostname
    if hostname not in ALLOWED_DOMAINS:
        raise ValueError("Invalid target domain")
    return requests.get(target_url).text

