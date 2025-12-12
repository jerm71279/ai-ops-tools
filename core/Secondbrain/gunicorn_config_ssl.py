"""
Gunicorn configuration for OberaConnect Tools Web Interface
Production-ready configuration with SSL/HTTPS
"""

import multiprocessing

# Server socket - HTTPS on port 5443 (use 443 for production with systemd)
bind = "0.0.0.0:5443"
backlog = 2048

# SSL Configuration
keyfile = "/home/mavrick/Projects/Secondbrain/ssl/server.key"
certfile = "/home/mavrick/Projects/Secondbrain/ssl/server.crt"

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 5

# Logging
accesslog = "/home/mavrick/Projects/Secondbrain/logs/access.log"
errorlog = "/home/mavrick/Projects/Secondbrain/logs/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "oberaconnect-tools-ssl"

# Server mechanics
daemon = False
pidfile = "/home/mavrick/Projects/Secondbrain/logs/gunicorn.pid"
umask = 0
user = None
group = None
tmp_upload_dir = None

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
