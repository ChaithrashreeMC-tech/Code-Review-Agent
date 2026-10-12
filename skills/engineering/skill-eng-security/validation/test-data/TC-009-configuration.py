class AppConfigViolation:
    # SEC09 Violation: Production configuration with DEBUG=True, wildcard CORS, and public stack traces
    DEBUG = True
    CORS_ALLOW_ALL_ORIGINS = True
    ALLOWED_HOSTS = ["*"]

class AppConfigSafe:
    # SEC09 Safe: Hardened production configuration
    DEBUG = False
    CORS_ALLOWED_ORIGINS = ["https://app.company.com"]
    ALLOWED_HOSTS = ["app.company.com"]

