from fabric.api import local, run, env, put, sudo
from fabric.context_managers import cd
from datetime import datetime as dt

REPO_PATH = '/tmp/online_test/'

def build(path):
    local('docker build {}'.format(path))

def clone(url):
    with cd('/tmp'):
        local('git clone {0} {1}'.format(url, REPO_PATH))

def stop(id):
    sudo('docker stop {}'.format(id))

def copy(id, source, destination):
    sudo('docker cp {0} {1}:{2}'.format(source, id, destination))

def commit(id, image):
    sudo('docker commit {0} {1}'.format(id, image))

def run(image, server_port, pool_port, cmd):
    sudo('docker run -d -p {0}:{0} -p {1}:{1} {2} {3}'.format(server_port, pool_port, image, cmd))

def update(id=None,
        setting_path=None,
        url='https://github.com/FOSSEE/online_test.git',
        image='yaksh_{}'.format(dt.strftime(dt.now(), '%y%m%d%s')),
        server_port='8001',
        pool_port='53579',
        cmd='python -m yaksh.code_server'
    ):
    if id == None:
        abort("No Container ID provided!")
    if setting_path == None:
        abort("No Settings file path provided!")
    repo_source = REPO_PATH + '.'
    repo_destination = '/src/online_test'
    setting_source = setting_path
    setting_destination = '/src/online_test/yaksh'

    clone(url)
    stop(id)
    copy(id, repo_source, repo_destination) #docker cp ./yaksh/. a0736872a21b:/src/online_test/yaksh
    copy(id, setting_source, setting_destination) #docker cp ./yaksh/settings.py ID:/src/online_test/yaksh
    commit(id, image)
    run(image, server_port, pool_port, cmd)