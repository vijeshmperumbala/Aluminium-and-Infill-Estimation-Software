import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'amoeba',
        'USER': 'postgres',
        'PASSWORD': '12345',
        'HOST': 'localhost',
        'PORT': '5432',
        'ATOMIC_REQUESTS': True,
        'CONNECTION_POOL_KWARGS': {
            'max_connections': 20,  # Adjust the number of connections as needed
            'GEVENT': True,
        }
    },    
}


# CHANNEL_LAYERS = {
#     "default": {
#         # "BACKEND": "channels.layers.InMemoryChannelLayer",
#         "BACKEND": "channels_redis.core.RedisChannelLayer",
#         "CONFIG": {
#             "hosts": [("127.0.0.1", 6379)],
#             "capacity": 500,  # Set the maximum number of concurrent tasks
#             "expiry": 3600,   # Sets the default message expiry to one hour (3600 seconds).
#         },
        
#     },
# }

# CACHES = { 
#           'default': { 
#               'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
#                 'LOCATION': 'amoeba_cache',
#               }
#           }

ROWS_PER_PAGE = 16

INTERNAL_IPS = ('127.0.0.1',)
DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK" : lambda request: True,
}
# SILKY_PYTHON_PROFILER = True

EMAIL_HOST_USER = 'vijesh.convibe@gmail.com'
EMAIL_HOST_PASSWORD = 'your-email account-password'

X_FRAME_OPTIONS = 'ALLOWALL'

XS_SHARING_ALLOWED_METHODS = ['POST','GET','OPTIONS', 'PUT', 'DELETE']


######################## Celery Settings ####################### 

CELERY_BROKER_URL = 'redis://127.0.0.1:6379'  
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379'  
CELERY_BROKER_REDIS_URL="redis://127.0.0.1:6379"

# DJANGO SECURITY FUNCTIONS

# Cross-site Scripting (XSS): minimize the damage of XSS attacks
# SECURE_BROWSER_XSS_FILTER = True 
# SECURE_CONTENT_TYPE_NOSNIFF = True

# #  SSL redirect, redirects all non-HTTPS requests to HTTP
# # HTTP Strict Transport Security (HSTS): prevent from man-in-the-middle attacks
# SECURE_SSL_REDIRECT = False
# SECURE_HSTS_SECONDS = 86400
# # SECURE_HSTS_PRELOAD = True 
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# # Cross-site request forgery (CSRF) protection
# SESSION_COOKIE_SECURE = False 
# CSRF_COOKIE_SECURE = False

# CORS_REPLACE_HTTPS_REFERER      = False
# HOST_SCHEME                     = "http://"
# SECURE_PROXY_SSL_HEADER         = None
# SECURE_FRAME_DENY               = False

CACHE_MIDDLEWARE_SECONDS = 0


# SESSION_EXPIRE_SECONDS = 1800
SESSION_TIMEOUT_REDIRECT = 'signin'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True 
# SESSION_COOKIE_AGE = 1200

## add to middleware
## 'csp.middleware.CSPMiddleware',
# Content Security Policy

# CSP_IMG_SRC = ("'self'")

# CSP_STYLE_SRC = ("'self', 'sha256-bbeWA+kPO5LBumStmg0hG56Q6DPALzjhvdXYaPWHoSg='", 'https://fonts.googleapis.com/', )

# CSP_SCRIPT_SRC = ("'self'", 'https://cdn.amcharts.com/', 'https://cdnjs.cloudflare.com/', 'unsafe-inline', 'unsafe-eval')
# CSP_FONT_SRC = ("'self'", 'https://fonts.googleapis.com/')

# CSP_DEFAULT_SRC = ("'self'", 'https://cdn.amcharts.com/', 'https://cdnjs.cloudflare.com/', 'https://fonts.googleapis.com/')


# STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
STATIC_URL = 'static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static/'),
)


PATH = os.path.join(BASE_DIR,'/')
# STATIC_URL = '/static/'
# STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
# MEDIA_URL = '/media/'


# sudo service redis-server restart




