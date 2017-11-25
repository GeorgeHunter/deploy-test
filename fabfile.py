from __future__ import with_statement
from fabric.api import cd, run, env
from fabric.decorators import task

env.use_ssh_config = True
env.hosts = 'deploy-test'

@task
def deploy():
	with cd('/home/application/hello-world.com/deploy-test'):
		run('git pull origin master')
		run('composer install')


