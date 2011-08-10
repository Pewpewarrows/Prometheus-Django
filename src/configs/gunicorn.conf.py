import os

def num_cpus():
    if not hasattr(os, "sysconf"):
        raise RuntimeError("No sysconf detected.")
    return os.sysconf("SC_NPROCESSORS_ONLN")

bind = 'unix:/tmp/projectname_gunicorn.sock'
backlog = 2048

daemon = False

workers = num_cpus() * 2 + 1
preload_app = True

pidfile = '/tmp/projectname_gunicorn.pid'
