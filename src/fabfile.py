# Credits to http://stevelosh.com/blog/2011/06/django-advice/ 
# for many ideas in this file.

from __future__ import with_statement
import datetime
import os
import random

from fabric.api import *
from fabric.colors import *
from fabric.contrib import django
from fabric.contrib.console import *
from fabric.contrib.files import *
from fabric.contrib.project import *
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

# TODO: validate the vars obtained from the config file
env.datetime = datetime.datetime.now().strftime('%Y-%m-%d-%H%M%S')
env.project = _config['env']['project']
env.user = _config['env']['user']
env.webserver_software = _config['env']['webserver_software']
env.db_software = _config['env']['db_software']
env.live_url = _config['env']['live_url']
# TODO: make local/remote upload dirs configurable
env.local_uploads = os.path.join(env.real_fabfile, '..', 'uploads')
# TODO: make local/remote static dirs configurable
# TODO: support multiple django static file apps (not just mediagenerator)

try:
    env.path = _config['env']['path'] % env
except:
    print red('The required app install path could not be parsed: %s' % _config['env']['path'])
    abort()

WORDLIST_PATHS = [os.path.join('/', 'usr', 'share', 'dict', 'words')]

# with settings(warn_only=True):
#
# confirm('text', default=True)
# require()
#
# @hosts()
# @roles()
# @runs_once()
# @with_settings(warn_only=True)

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
    for k, v in servers.itervalues():
        if v['ip'] == env.host:
            server = v
            env.server_name = k
            break

    if server is None:
        error('Could not find the current attempted server in config: %s' % env.host)

    if 'stage' in server:
        env.stage = server['stage']
    else:
        env.stage = 'prod'

    django.settings_module('conf.%(stage)s.settings' % env)
    from django.conf import settings
    env.django_settings = settings

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
                                    DANGER!
    ''')

def happy():
    print green('Success, nothing broke this time! Huzzah!')

def unavailable():
    abort(yellow('* This task is not yet available. Skipping.'))

# For use with production tasks that you don't want to accidentally call
def protect(word_count=1):
    """Prompt the user to enter random words to prevent doing something stupid."""

    valid_wordlist_paths = [wp for wp in WORDLIST_PATHS if os.path.exists(wp)]

    if not valid_wordlist_paths:
        error('No wordlists found!')

    with open(valid_wordlist_paths[0]) as wordlist_file:
        words = wordlist_file.readlines()

    warn('Are you sure you want to do this?')

    for i in range(int(word_count)):
        word = words[random.randint(0, len(words))].strip()
        p_msg = '[%d/%d] Type "%s" to continue (^C quits):' % (i+1, word_count, word)
        answer = prompt(p_msg, validate=r'^%s$' % word)

# Tasks

# TODO: docs, info, warn, error everywhere!
# TODO: account for deploy_type, stage, os everywhere!
# TODO: assert roles and settings everywhere!
# TODO: more server types (cache, search, load balancer, worker, queue, mail)
# TODO: large server-farm support:
#   - one machine, several roles, several types, several projects
#   - several machines, each several roles, each a single type, each several projects
#   - several machines, each a single role, multiple machines per type, each a single project
# TODO: handling file permissions
# TODO: race conditions when checking if files/dirs exist?
# TODO: pidfiles and logs under project dir?

info('Starting fabric script at %s' % env.datetime)

# lint and test
@task
def lint():
    unavailable()

@task
def test():
    unavailable()

# find unused dependencies, updates available to existing requirements
@task
def clean_dependencies():
    unavailable()

@task
def check():
    """Check that the home page of the site returns an HTTP 200."""

    info('Checking site status...')

    if not '200 OK' in local('curl --silent -I "http://%s"' % env.live_url, capture=True):
        sad()
    else:
        happy()

# first-time server setup
@task
def setup_server():
    refresh_env()

    # TODO: check if this server has already been setup?
    #   - also, a confirmation before executing on an existing setup server?
    # TODO: allow customization for internal os package repo

    update_server()
    setup_general_server()
    create_user(True, True)

    if env.role == 'app':
        setup_app_server()
    elif env.role == 'db':
        setup_db_server()
    elif env.role == 'static':
        setup_static_server()

    setup_server_configs()
    #secure_server()
    startup_server()

# create user/group, setup ssh keys
@task
def create_user(prompt_for_username=False, sudoer=False):
    refresh_env()

    if prompt_for_username:
        # TODO: validate this username can exist on os
        username = prompt('What should the admin username on this server be?')
    else:
        username = env.project

    sudo('adduser %s' % username)
    sudo('adduser %s %s' % (username, env.sudoers))

    # SSH
    ssh_key = prompt('Paste a public ssh key to access this server with the new user:')
    sudo('-u %s mkdir /home/%s/.ssh' % (username, username))
    sudo('-u %s touch /home/%s/.ssh/authorized_keys' % (username, username))
    sudo('-u %s echo "%s" >> /home/%s/.ssh/authorized_keys' % (username, ssh_key, username))
    sudo('chmod 0600 "/home/%s/.ssh/authorized_keys"' % username)

# secure server
@task
def secure_server():
    refresh_env()
    unavailable()

    # /etc/sudoers
    # TODO: disable root login, disable password login, enable ssh key login, only allow my users
    # TODO: change ssh port to 31337
    # TODO: install ufw, configure it, disallow port scans
    # TODO: install DDOS prevention modules in webserver software
    # TODO: runaway CPU/RAM/Disk monitor and killer?
    # TODO: root's bash profile should e-mail sudoers everytime it's logged-in
    # TODO: install logwatch/logcheck/logcheck-database/tripwire to watch for config file changes
    # TODO: install fail2ban/denyhosts/denyhosts-remove for auto bans
    # TODO: make webserver software not broadcast itself
    # TODO: confirm critical file permissions and ownership
    # TODO: log all terminal commands from all users, e-mail sudoers at the end of the week?
    # TODO: e-mail an nmap of localhost every week to sudoers?

# update os
@task
def update_server():
    refresh_env()

    # TODO: just e-mail sudoers with updates instead of applying automatically, option?

    if env.os == 'ubuntu':
        sudo('apt-get update')
        sudo('apt-get safe-upgrade --show-upgraded')

# install os packages
@task
def setup_general_server():
    refresh_env()

    if env.os == 'ubuntu':
        sudo('apt-get remove -y apache2 apache2-mpm-prefork apache2-utils')
        sudo('apt-get install -y wget vim less htop')
        sudo('apt-get install -y openssl-devel gpg make gcc build-essential')
        sudo('apt-get install -y python python-dev python-setuptools')

    sudo('easy_install -U pip')
    sudo('pip install supervisor')

    sudo('dpkg-reconfigure locales')
    sudo('update-locale LANG=en_US.UTF-8')

    # Hostname
    sudo('echo %(server_name)s > /etc/hostname' % env)
    sudo('hostname -F /etc/hostname')
    sudo('echo -e "\n127.0.0.1 %(server_name)s.local %(server_name)s\n" >> /etc/hosts' % env)

    # TODO: set the timezone: http://library.linode.com/getting-started#sph_id16
    # TODO: install qmail
    # TODO: centralized logging / log rotation?
    # TODO: monitoring software, like graphite / nagios / munin
    # TODO: automated backups
    # TODO: create a saner default home dir in /etc/skel?

    # Time sync
    sudo('echo -e "ntpdate ntp.ubuntu.com" > /etc/cron.daily/ntpdate')
    sudo('chmod 755 /etc/cron.daily/ntpdate')

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

    # virtualenvs
    sudo('pip install virtualenv')
    sudo('pip install virtualenvwrapper')

@task
def setup_db_server():
    refresh_env()

    if env.db_software == 'postgresql':
        if env.os == 'ubuntu':
            sudo('apt-get install -y postgresql-contrib postgresql-dev postgresql-client libpq-dev')
    elif env.db_software == 'mysql':
        if env.os == 'ubuntu':
            sudo('apt-get install -y mysql-server')

@task
def setup_static_server():
    refresh_env()

    if env.os == 'ubuntu':
        sudo('apt-get install -y nginx')

# setup global configs
@task
def setup_server_configs():
    refresh_env()

    sudo('echo; if [ ! -f /etc/supervisord.conf ]; then echo_supervisord_conf > /etc/supervisord.conf; fi')
    sudo('echo; if [ ! -d /etc/supervisor ]; then mkdir /etc/supervisor; fi')

    put('conf/common/supervisord.conf', '/etc/supervisord.conf', use_sudo=True)
    put('conf/common/supervisord-init', '/etc/init.d/supervisord', use_sudo=True)
    sudo('chmod +x /etc/init.d/supervisord')
    sudo('update-rc.d supervisord defaults')

    if env.role == 'app' or env.role == 'static':
        sudo('rm -rf /etc/nginx/sites-enabled/*')
        sudo('rm -rf /etc/nginx/sites-available/*')
        upload_template('conf/common/fastcgi_params', '/etc/nginx/', env, use_sudo=True)
        upload_template('conf/common/mime.types', '/etc/nginx/', env, use_sudo=True)
        upload_template('conf/common/nginx.conf', '/etc/nginx/', env, use_sudo=True)
        upload_template('conf/common/nginx-default', '/etc/nginx/sites-available/default', env, use_sudo=True)
    elif env.role == 'db':
        pass

# startup server software
@task
def startup_server():
    refresh_env()

    sudo('service supervisord start')
    sudo('supervisorctl status')

    if env.role == 'app':
        if env.webserver_software == 'nginx':
            sudo('service nginx start')
        elif env.webserver_software == 'apache':
            pass
    elif env.role == 'db':
        if env.db_software == 'postgresql':
            sudo('service postgresql start')
        elif env.db_software == 'mysql':
            sudo('service mysql start')
    elif env.role == 'static':
        sudo('service nginx start')

# create project ready for deploy
@task
def setup_new_project():
    refresh_env()

    # TODO: check that this project name hasn't been used before
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

        run('echo "export DJANGO_SETTINGS_MODULE=\"src.conf.%(stage)s.settings\"" >> /home/%(project)s/.bashrc' % env)
        run('echo "export WORKON_HOME=/home/%(project)s/.virtualenvs" >> /home/%(project)s/.bashrc' % env)
        run('echo "source /usr/local/bin/virtualenvwrapper.sh" >> /home/%(project)s/.bashrc' % env)

        with prefix('source /home/%(project)s/.bashrc' % env):
            run('mkvirtualenv --no-site-packages %(project)s' % env)

        if not exists('%(path)s/releases' % env):
            run('cd %(path)s; mkdir releases' % env)

        if not exists('%(path)s/logs' % env):
            run('cd %(path)s; mkdir logs' % env)

        # TODO: check for a stage specific config file
        upload_template('conf/common/nginx-%(project)s' % env, '/etc/nginx/sites-available/%(project)s' % env, env, use_sudo=True)
        sudo('ln -s /etc/nginx/sites-available/%(project)s /etc/nginx/sites-enabled/%(project)s' % env)
        upload_template('conf/common/supervisor-%(project)s.conf' % env, '/etc/supervisor/%(project)s.conf' % env, env, use_sudo=True)
    elif env.role == 'db':
        sudo('su - postgres -c "echo \'CREATE ROLE %(project)s WITH LOGIN ENCRYPTED PASSWORD \"%(project)s\";\' | psql"' % env)
        sudo('-u postgres createdb --encoding=UTF8 --owner=%(project)s %(project)s' % env)
    elif env.role == 'static':
        if not exists('%(path)s/static' % env):
            run('cd %(path)s; mkdir static' % env)

        # TODO: should these by on static, or their own server role?
        # TODO: nginx config for serving uploads
        if not exists('%(path)s/uploads' % env):
            run('cd %(path)s; mkdir uploads' % env)

        # TODO: check for a stage specific config file
        upload_template('conf/common/nginx-%(project)s-static' % env, '/etc/nginx/sites-available/%(project)s-static' % env, env, use_sudo=True)
        sudo('ln -s /etc/nginx/sites-available/%(project)s-static /etc/nginx/sites-enabled/%(project)s-static' % env)

# deploy
@task
def deploy():
    archive_project()
    upload_project()
    upload_secrets()
    generate_static()
    push_static()
    install_requirements()
    symlink_release()
    migrate_db()
    reload_gunicorn()
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
    # TODO: provide repo, branch options
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
    refresh_env()

    # TODO: account for custom pypi server (ala chishop)
    # TODO: check for gunicorn in here!
    with prefix('workon %(project)s' % env):
        run('pip install -r %(path)s/releases/%(datetime)s/src/conf/common/requirements.txt')

        if exists('%(path)s/releases/%(datetime)s/src/conf/%(stage)s/requirements.txt'):
            run('pip install -r %(path)s/releases/%(datetime)s/src/conf/%(stage)s/requirements.txt')

@task
def symlink_release():
    # TODO: delete old directories
    with cd('%(path)s/releases'):
        if exists('previous'):
            run('rm previous')
        run('mv current previous')
        run('ln -s %(datetime)s current' % env)

@task
def reset_db():
    unavailable()

# migrate db
@task
def migrate_db():
    # TODO: ensure this is only run once overall
    run('python manage.py syncdb')
    run('python manage.py migrate')

# generate, compile, minify static files
@task
def generate_static():
    local('python manage.py generatemedia')

# sync static files
@task
def push_static():
    # TODO: --dry-run first, with a prompt to continue?
    rsync_project('%(path)s/static' % env, '_generated_media/')

# push db to live / pull db from live
@task
def pull_db():
    db_pass = None
    for k in env.django_settings.DATABASES.keys():
        if env.django_settings.DATABASES[k]['HOST'] == env.host:
            db_pass = env.django_settings.DATABASES[k]['PASSWORD']
            break

    db_pass_string = ''
    if db_pass is not None:
        db_pass_string = '-p%s' % db_pass

    # TODO: have configurable db user, db name, no pass required, etc

    django.settings_module('conf.local.settings')
    from django.conf import settings as local_settings
    
    # Assumes only one db in your local secret_settings.py
    local_db = local_settings.DATABASES.itervalues().next()
    
    if env.db_software == 'postgresql':
        run('pg_dump -u%s %s %s > /tmp/fabric/%s-%s.db' % (
            env.user,
            db_pass_string,
            env.project,
            env.project,
            env.datetime,
        ))
        get('/tmp/fabric/%(project)s-%(datetime).db' % env, '/tmp/fabric/')
        local('psql -u%s -p%s %s < /tmp/fabric/%s-%s.db' % (
            local_db['USERNAME'],
            local_db['PASSWORD'],
            local_db['NAME'],
            env.project,
            env.datetime,
        ))
    elif env.db_software == 'mysql':
        pass

    run('rm /tmp/fabric/%(project)s-%(datetime)s.db' % env)
    local('rm /tmp/fabric/%(project)s-%(datetime)s.db' % env)

@task
def push_db():
    unavailable()

# push uploads to live / pull uploads from live
@task
def pull_uploads():
    # Ripped in part from fabric's rsync_project function

    # Honor SSH key(s)
    key_string = ''
    if env.key_filename:
        keys = env.key_filename
        # For ease of use, coerce stringish key filename into list
        if not isinstance(env.key_filename, (list, tuple)):
            keys = [keys]
        key_string = '-i ' + ' -i '.join(keys)

    # Honor nonstandard port
    port_string = ('-p %s' % env.port) if (env.port != '22') else ''

    # RSH
    rsh_string = ''
    if key_string or port_string:
        rsh_string = '--rsh="ssh %s %s"' % (port_string, key_string)
        
    rsync_cmd = r"""rsync -rlptvhz %s %s@%s:%s %s""" % (
        rsh_string,
        env.user,
        env.host,
        '%(path)s/uploads/' % env,
        env.local_uploads
    )

    # TODO: --dry-run first, with a prompt to continue?
    print local(rsync_cmd, capture=False)

@task
def push_uploads():
    result = local('test -d %(local_uploads)s' % env)
    if result.failed:
        error('The local uploads directory does not exist at: %(local_uploads)s' % env)

    # TODO: --dry-run first, with a prompt to continue?
    rsync_project('%(path)s/uploads' % env, env.local_uploads + '/')

# refresh supervisord
@task
def refresh_supervisord():
    sudo('supervisorctl reread')
    sudo('supervisorctl update')

# reload gunicorn
@task
def reload_gunicorn():
    refresh_env()

    if env.role != 'app':
        return

    # TODO: waiting for this to be fixed: https://github.com/benoitc/gunicorn/issues/219
    #sudo('kill -HUP `cat /tmp/%(project)s_gunicorn.pid`')

    sudo('supervisorctl restart %(project)s_gunicorn' % env)

# reload webserver
@task
def reload_webserver():
    refresh_env()

    if env.role != 'app':
        return

    if env.webserver_software == 'nginx':
        sudo('service nginx reload')

# restart webserver
@task
def restart_webserver():
    refresh_env()

    if env.role != 'app':
        return

    if env.webserver_software == 'nginx':
        sudo('service nginx restart')

# rollback
@task
def rollback():
    with cd('%(path)s/releases'):
        if exists('previous'):
            run('rm current')
            run('mv previous current')

    reload_gunicorn()
    reload_webserver()

# view tail of server logs
@task
def tailgun():
    unavailable()
