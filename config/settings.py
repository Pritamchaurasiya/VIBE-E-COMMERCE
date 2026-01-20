# Content Security Policy - Use constant for common values
CSP_SELF = "'self'"
CSP_DEFAULT_SRC = (CSP_SELF,)
CSP_SCRIPT_SRC = (CSP_SELF, "'unsafe-inline'", "'unsafe-eval'", "https://js.stripe.com")
CSP_STYLE_SRC = (CSP_SELF, "'unsafe-inline'", "https://fonts.googleapis.com")
CSP_FONT_SRC = (CSP_SELF, "https://fonts.gstatic.com")
CSP_IMG_SRC = (CSP_SELF, "data:", "https:", "http:")
CSP_CONNECT_SRC = (CSP_SELF, "https://api.stripe.com", "wss:", "ws:")
