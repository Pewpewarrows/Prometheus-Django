from __future__ import with_statement
from datetime.datetime import now
from os import open

from fabric.api import *
from fabric.colors import *
from fabric.contrib.console import confirm
from fabric.contrib.files import *
from yaml import safe_load as load_yaml

# import other mini-fabfiles for namespacing? (@task(default=True)) && __all__

# Global Configuration
env.colors = True
env.config_file = 'fabconfig.yaml'
env.format = True

# env.key_filename
# (for EC2 edge cases) env.disable_known_hosts = True

# TODO: check if file exists first
# TODO: allow multiple config files types (json, xml, python)
_yaml = load_yaml(open('fabconfig.yaml'))
servers = _yaml.servers
roles = _yaml.roles

env.project = _yaml.env.project
env.user = _yaml.env.user
env.webserver_software = _yaml.env.webserver_software
# TODO: make these configurable
env.path = '/home/%(user)s/public_html/$(project_name)s' % env
env.stage = 'prod'
env.os = 'ubuntu'
env.role = 'app'
env.datetime = now().strftime('%Y-%m-%d-%H%M%S')

# with cd(''):
# with lcd(''):
# with path(''):
# with prefix(''):
# with settings(warn_only=True):
#
# local()
# run()
# sudo()
# confirm('text', default=True)
# prompt('text', default='', validate=None)
# abort()
# require()
# result.failed / result.return_code / result.succeeded
# 'test -d %s' # for testing that a dir exists!
# get(remote_path, local_path)
# put(local_path, remote_path, use_sudo=False, mirror_local_mode=False, mode=None)
# exists()
# upload_template() ???
# rsync_project() ??? # for things like user-uploaded content
#
# @hosts()
# @roles()
# @task()
# @runs_once()
# @with_settings(warn_only=True)
#
# http://docs.fabfile.org/en/1.2.0/api/contrib/django.html
# fab -l

# Helper Functions

# TODO: fix these to use env.roles && env.roledefs
# TODO: use stage variables

# $ fab server:www command
def server(name):
    env.hosts = env.hosts or []

    if 'port' in servers[name]:
        port = servers[name]['port']
    else:
        port = 22

    env.hosts.append('%s@%s:%s' % (env.user, servers[name]['ip'], port))

# $ fab role:app command
def role(name):
    for server_name in roles[name]:
        server(server_name)

# Color-coded print wrappers
# unused: blue, green, magenta
def info(txt):
    print cyan(txt)

def warn(txt):
    print yellow(txt)

def error(txt):
    print red(txt)

# Tasks

info('Starting fabric script at %s' % env.datetime)

# first-time server setup
@task
def setup_server():
    if env.webserver_software == 'nginx':
        pass

# create user with root privs
# secure server

# update os
@task
def update_server():
    if env.os == 'ubuntu':
        sudo('apt-get update')
        sudo('apt-get safe-upgrade')

# install os packages
@task
def setup_general_server():
    if env.os == 'ubuntu':
        sudo('apt-get remove -y apache2 apache2-mpm-prefork apache2-utils')

    sudo('echo; if [ ! -f /etc/supervisord.conf ]; then echo_supervisord_conf > /etc/supervisord.conf; fi')
    sudo('echo; if [ ! -d /etc/supervisor ]; then mkdir /etc/supervisor; fi')

@task
def setup_app_server():
    sudo('apt-get install nginx')

    # TODO: chef/puppet should handle the main nginx confs, how to ensure it's occured?

    sudo('/etc/init.d/nginx start')

    sudo('apt-get install -y build-essential python-dev python-setuptools')
    sudo('easy_install -U pip')

    # virtualenvs
    sudo('pip install virtualenv')
    sudo('pip install virtualenvwrapper')

# setup global configs
# create user/group, setup ssh keys

# create project ready for deploy
@task
def setup_new_project():
    venv_dir = '/home/%(user)s/.virtualenvs' % env
    run('mkdir -p %s' % venv_dir)

    if not exists('/home/%(user)s/.bashrc' % env):
        run('touch /home/%(user)s/.bashrc' % env)

    run('echo "export WORKON_HOME=/home/%(user)s/.virtualenvs" >> ~/.bashrc' % env)
    # TODO: how to use the above .virtualenvs dir for mkvirtualenv here?
    run('mkvirtualenv --no-site-packages %(project_name)s' % env)

    run('mkdir -p %s' % env.path)

    if not exists('%(path)s/releases' % env):
        run('cd %(path)s; mkdir releases' % env)

    if not exists('%(path)s/logs' % env):
        run('cd %(path)s; mkdir logs' % env)

@task
def deploy():
    archive_project()
    upload_project()
    install_requirements()
    symlink_release()
    migrate_db()
    reload_webserver()

# archive project
@task
def archive_project():
    local('git archive --format=tar master | gzip > /tmp/fabric/%(project)s-%(datetime)s.tar.gz' % env)

# upload archive
@task
def upload_project():
    run('mkdir -p %(path)s/releases/%(datetime)s' % env)
    put('/tmp/fabric/%(project)-%(datetime)s.tar.gz' % env, '%(path)s/releases' % env)
    run('cd %(path)s/releases/%(datetime)s && tar zxf ../%(project)s-%(datetime)s.tar.gz' % env)

    run('rm %(path)s/releases/%(project)-%(datetime)s.tar.gz' % env)
    local('rm /tmp/fabric/%(project)s-%(datetime)s.tar.gz' % env)

# setup project release
@task
def install_requirements():
    with prefix('workon %(project)s' % env):
        run('pip install -r %(path)s/src/conf/common/requirements.txt')

@task
def symlink_release():
    # TODO: rotate out old directories
    run('cd %(path)s/releases; ln -s %(datetime)s current' % env)

# migrate db
@task
def migrate_db():
    pass

# sync static files
# push db to live / pull db from live
# push uploads to live / pull uploads from live

# reload webserver
@task
def reload_webserver():
    if env.role != 'app':
        return

    if env.webserver_software == 'nginx':
        sudo('/etc/init.d/nginx reload')

# restart webserver
# rollback
