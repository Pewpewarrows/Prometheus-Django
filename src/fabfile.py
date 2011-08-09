# Credits to http://stevelosh.com/blog/2011/06/django-advice/ 
# for many ideas in this file.

from __future__ import with_statement
import datetime

from fabric.api import *
from fabric.colors import *
from fabric.contrib.console import confirm
from fabric.contrib.files import *
from yaml import safe_load as load_yaml

# import other mini-fabfiles for namespacing? (@task(default=True)) && __all__

# Global Configuration

env.config_file = 'fabconfig.yaml'
# env.key_filename
# (for EC2 edge cases) env.disable_known_hosts = True

# TODO: allow multiple config files types (json, xml, python)
try:
    _config = load_yaml(open(env.config_file, 'r'))
except IOError:
    print red('The required fabric configuration file could not be found: %s' % env.config_file)
    abort()

servers = _config['servers']
roles = _config['roles']

env.datetime = datetime.datetime.now().strftime('%Y-%m-%d-%H%M%S')
env.project = _config['env']['project']
env.user = _config['env']['user']
env.webserver_software = _config['env']['webserver_software']
env.db_software = _config['env']['db_software']
env.live_url = _config['env']['live_url']

try:
    env.path = _config['env']['path'] % env
except:
    print red('The required app install path could not be parsed: %s' % _config['env']['path'])
    abort()

# with lcd(''):
# with path(''):
# with settings(warn_only=True):
#
# confirm('text', default=True)
# prompt('text', default='', validate=None)
# require()
# result.failed / result.return_code / result.succeeded
# get(remote_path, local_path)
# put(local_path, remote_path, use_sudo=False, mirror_local_mode=False, mode=None)
# exists()
# upload_template() ???
# rsync_project() ??? # for things like user-uploaded content
#
# @hosts()
# @roles()
# @runs_once()
# @with_settings(warn_only=True)
#
# http://docs.fabfile.org/en/1.2.0/api/contrib/django.html
# fab -l

# Helper Functions

# TODO: fix these to use env.roles && env.roledefs ???

# $ fab server:www command
@task
def server(name):
    if name not in servers:
        error('Could not find the current attempted server in config: %s' % name)
        abort()

    env.hosts = env.hosts or []

    if 'port' in servers[name]:
        port = servers[name]['port']
    else:
        port = 22

    env.hosts.append('%s@%s:%s' % (env.user, servers[name]['ip'], port))

# $ fab role:app command
@task
def role(name):
    if name not in roles:
        error('Could not find the current attempted role in config: %s' % name)

    env.role = name

    for server_name in roles[name]:
        server(server_name)

def refresh_env():
    # TODO: is there a way to get around having to put this at the top of every task?
    server = None
    for s in servers:
        if s['ip'] == env.host:
            server = s
            break

    if server is None:
        error('Could not find the current attempted server in config: %s' % env.host)

    if 'stage' in server:
        env.stage = server['stage']
    else:
        env.stage = 'prod'

    if 'os' in server:
        env.os = server['os']
    else:
        env.os = 'ubuntu'

    if env.os == 'ubuntu':
        env.sudoers = 'wheel'

    if 'deploy_type' in server:
        env.deploy_type = server['deploy_type']
    else:
        env.deploy_type = 'shell'

# Color-coded print wrappers
# unused: blue, green, magenta
def info(txt):
    print cyan('* ' + txt)

def instruct(txt):
    print magenta('*' + txt)

def warn(txt):
    print yellow('* ' + txt)

def error(txt):
    abort(red('* ' + txt))

def sad():
    print red(r'''
                                                                         
                              ud$$$**$$$$$$$bc.                          
                           u@**"        4$$$$$$$Nu                       
                         J                ""#$$$$$$r                     
                        @                       $$$$b                    
                      .F                        ^*3$$$                   
                     :% 4                         J$$$N                  
                     $  :F                       :$$$$$                  
                    4F  9                       J$$$$$$$                 
                    4$   k             4$$$$bed$$$$$$$$$                 
                    $$r  'F            $$$$$$$$$$$$$$$$$r                
                    $$$   b.           $$$$$$$$$$$$$$$$$N                
                    $$$$$k 3eeed$$b    $$$Euec."$$$$$$$$$                
     .@$**N.        $$$$$" $$$$$$F'L $$$$$$$$$$$  $$$$$$$                
     :$$L  'L       $$$$$ 4$$$$$$  * $$$$$$$$$$F  $$$$$$F         edNc   
    @$$$$N  ^k      $$$$$  3$$$$*%   $F4$$$$$$$   $$$$$"        d"  z$N  
    $$$$$$   ^k     '$$$"   #$$$F   .$  $$$$$c.u@$$$          J"  @$$$$r 
    $$$$$$$b   *u    ^$L            $$  $$$$$$$$$$$$u@       $$  d$$$$$$ 
     ^$$$$$$.    "NL   "N. z@*     $$$  $$$$$$$$$$$$$P      $P  d$$$$$$$ 
        ^"*$$$$b   '*L   9$E      4$$$  d$$$$$$$$$$$"     d*   J$$$$$r   
             ^$$$$u  '$.  $$$L     "#" d$$$$$$".@$$    .@$"  z$$$$*"     
               ^$$$$. ^$N.3$$$       4u$$$$$$$ 4$$$  u$*" z$$$"          
                 '*$$$$$$$$ *$b      J$$$$$$$b u$$P $"  d$$P             
                    #$$$$$$ 4$ 3*$"$*$ $"$'c@@$$$$ .u@$$$P               
                      "$$$$  ""F~$ $uNr$$$^&J$$$$F $$$$#                 
                        "$$    "$$$bd$.$W$$$$$$$$F $$"                   
                          ?k         ?$$$$$$$$$$$F'*                     
                           9$$bL     z$$$$$$$$$$$F                       
                            $$$$    $$$$$$$$$$$$$                        
                             '#$$c  '$$$$$$$$$"                          
                              .@"#$$$$$$$$$$$$b                          
                            z*      $$$$$$$$$$$$N.                       
                          e"      z$$"  #$$$k  '*$$.                     
                      .u*      u@$P"      '#$$c   "$$c                   
               u@$*"""       d$$"            "$$$u  ^*$$b.               
             :$F           J$P"                ^$$$c   '"$$$$$$bL        
            d$$  ..      @$#                      #$$b         '#$       
            9$$$$$$b   4$$                          ^$$k         '$      
             "$$6""$b u$$                             '$    d$$$$$P      
               '$F $$$$$"                              ^b  ^$$$$b$       
                '$W$$$$"                                'b@$$$$"         
                                                         ^$$$*  
                            DANGER WILL ROBINSON!
                                    ERROR!
    ''')

def happy():
    print green('Success, nothing broke this time! Huzzah!')

def unavailable():
    abort(yellow('* This task is not yet available. Skipping.'))

# Tasks

# TODO: docs, info, warn, error everywhere!
# TODO: account for deploy_type everywhere!
# TODO: more server types (cache, search, load balancer, worker, queue, mail)
# TODO: assert roles and settings everywhere!
# TODO: large server-farm support

info('Starting fabric script at %s' % env.datetime)

# lint and test
@task
def lint():
    unavailable()

@task
def test():
    unavailable()

# find unused dependencies
@task
def clean_dependencies():
    unavailable()

@task
def check():
    '''Check that the home page of the site returns an HTTP 200.'''

    info('Checking site status...')

    if not '200 OK' in local('curl --silent -I "%s"' % env.live_url, capture=True):
        sad()
    else:
        happy()

# first-time server setup
@task
def setup_server():
    refresh_env()
    # TODO: allow customization for internal os package repo
    create_user(True, True)
    update_server()
    setup_general_server()

    if env.role == 'app':
        setup_app_server()
    elif env.role == 'db':
        setup_db_server()
    elif env.role == 'static':
        setup_static_server()

    secure_server()
    setup_server_configs()
    startup_server()

# create user/group, setup ssh keys
@task
def create_user(prompt_for_username=False, sudoer=False):
    refresh_env()
    unavailable()

    if prompt_for_username:
        # TODO: validate this username
        username = prompt('What should the admin username on this server be?')
    else:
        username = env.project

    sudo('adduser %s' % username)
    sudo('adduser %s %s' % (username, env.sudoers))

# secure server
@task
def secure_server():
    refresh_env()
    unavailable()

# update os
@task
def update_server():
    refresh_env()
    if env.os == 'ubuntu':
        sudo('apt-get update')
        sudo('apt-get safe-upgrade')

# install os packages
@task
def setup_general_server():
    refresh_env()
    if env.os == 'ubuntu':
        sudo('apt-get remove -y apache2 apache2-mpm-prefork apache2-utils')
        sudo('apt-get install -y build-essential python-dev python-setuptools')

    sudo('easy_install -U pip')

    sudo('pip install supervisor')
    sudo('echo; if [ ! -f /etc/supervisord.conf ]; then echo_supervisord_conf > /etc/supervisord.conf; fi')
    sudo('echo; if [ ! -d /etc/supervisor ]; then mkdir /etc/supervisor; fi')

@task
def setup_app_server():
    refresh_env()
    if env.webserver_software == 'nginx':
        if env.os == 'ubuntu':
            sudo('apt-get install -y nginx')
    elif env.webserver_software == 'apache':
        if env.os == 'ubuntu':
            sudo('apt-get install -y apache2-mpm-worker apache2-utils')
            sudo('apt-get install -y libapache2-mod-wsgi')

    # TODO: chef/puppet should handle the main nginx confs

    # virtualenvs
    sudo('pip install virtualenv')
    sudo('pip install virtualenvwrapper')

@task
def setup_db_server():
    refresh_env()
    unavailable()

    if env.db_software == 'postgresql':
        if env.os == 'ubuntu':
            sudo('apt-get install -y postgresql')
    elif env.db_software == 'mysql':
        if env.os == 'ubuntu':
            sudo('apt-get install -y mysql-server')

@task
def setup_static_server():
    refresh_env()
    if env.os == 'ubuntu':
        sudo('apt-get install -y nginx')

    # TODO: chef/puppet should handle the main nginx confs

# setup global configs
@task
def setup_server_configs():
    refresh_env()
    unavailable()

# startup server software
@task
def startup_server():
    refresh_env()
    unavailable()

    sudo('/etc/init.d/supervisord start')

    if env.role == 'app':
        if env.webserver_software == 'nginx':
            sudo('/etc/init.d/nginx start')
        elif env.webserver_software == 'apache':
            pass
    elif env.role == 'db':
        pass
    elif env.role == 'static':
        sudo('/etc/init.d/nginx start')

# create project ready for deploy
@task
def setup_new_project():
    refresh_env()
    create_user()
    run('mkdir -p %s' % env.path)

    if env.role == 'app':
        venv_dir = '/home/%(project)s/.virtualenvs' % env
        run('mkdir -p %s' % venv_dir)

        if not exists('/home/%(project)s/.bash_profile' % env):
            run('touch /home/%(project)s/.bash_profile' % env)

        run('echo "source ~/.bashrc" >> /home/%(project)s/.bash_profile' % env)

        if not exists('/home/%(project)s/.bashrc' % env):
            run('touch /home/%(project)s/.bashrc' % env)

        run('echo "export WORKON_HOME=/home/%(project)s/.virtualenvs" >> /home/%(project)s/.bashrc' % env)
        run('echo "export source /usr/local/bin/virtualenvwrapper.sh" >> /home/%(project)s/.bashrc' % env)

        with prefix('source /home/%(project)s/.bashrc' % env):
            run('mkvirtualenv --no-site-packages %(project)s' % env)

        if not exists('%(path)s/releases' % env):
            run('cd %(path)s; mkdir releases' % env)

        if not exists('%(path)s/logs' % env):
            run('cd %(path)s; mkdir logs' % env)
    elif env.role == 'static':
        if not exists('%(path)s/static' % env):
            run('cd %(path)s; mkdir static' % env)

# deploy
@task
def deploy():
    archive_project()
    upload_project()
    upload_secrets()
    install_requirements()
    symlink_release()
    migrate_db()
    reload_webserver()
    check()

# deploy version
@task
def deploy_version():
    # TODO: allow for either archive datetime or git tag
    unavailable()

# archive project
@task
def archive_project():
    local('mkdir -p /tmp/fabric')
    local('git archive --format=tar master | gzip > /tmp/fabric/%(project)s-%(datetime)s.tar.gz' % env)

# upload archive
@task
def upload_project():
    run('mkdir -p %(path)s/releases/%(datetime)s' % env)
    put('/tmp/fabric/%(project)-%(datetime)s.tar.gz' % env, '%(path)s/releases' % env)

    with cd('%(path)s/releases/%(datetime)s' % env):
        run('tar zxf ../%(project)s-%(datetime)s.tar.gz .' % env)

    run('rm %(path)s/releases/%(project)-%(datetime)s.tar.gz' % env)
    local('rm /tmp/fabric/%(project)s-%(datetime)s.tar.gz' % env)

# upload secrets
@task
def upload_secrets():
    put('conf/%(stage)s/secret_settings.py', '%(path)s/releases/%(datetime)s/src/conf/%(stage)s/')

# setup project release
@task
def install_requirements():
    # TODO: account for custom pypi server (ala chishop)
    with prefix('workon %(project)s' % env):
        run('pip install -r %(path)s/src/conf/common/requirements.txt')

@task
def symlink_release():
    # TODO: delete old directories
    with cd('%(path)s/releases'):
        if exists('previous'):
            run('rm previous')
        run('mv current previous')
        run('ln -s %(datetime)s current' % env)

# migrate db
@task
def migrate_db():
    unavailable()

    run('python manage.py syncdb')
    run('python manage.py migrate')

# sync static files
@task
def sync_static():
    unavailable()

# push db to live / pull db from live
@task
def pull_db():
    unavailable()

@task
def push_db():
    unavailable()

# push uploads to live / pull uploads from live
@task
def pull_uploads():
    unavailable()

@task
def push_uploads():
    unavailable()

# reload webserver
@task
def reload_webserver():
    refresh_env()
    if env.role != 'app':
        return

    if env.webserver_software == 'nginx':
        sudo('/etc/init.d/nginx reload')

# restart webserver
@task
def restart_webserver():
    unavailable()

# rollback
@task
def rollback():
    with cd('%(path)s/releases'):
        if exists('previous'):
            run('rm current')
            run('mv previous current')

    reload_webserver()
