bind = "0.0.0.0:5000"
workers = 1
threads = 1
timeout = 240

# Enable logs
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Apache-style access log format
access_log_format = (
    '%(h)s - - [%(t)s] "%(m)s %(U)s %(H)s" %(s)s -'
)
