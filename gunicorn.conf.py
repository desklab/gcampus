wsgi_app = "gcampus.wsgi"
errorlog = "-"  # log to stderr
loglevel = "info"
# capture_output = True
bind = "0.0.0.0:8000"
workers = 4
worker_class = "sync"  # default worker. Change if needed
