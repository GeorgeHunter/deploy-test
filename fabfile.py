from __future__ import with_statement
from time import time

from fabric.api import local, env, run, cd, get
from fabric.decorators import task
from fabric.contrib.files import exists

env.use_ssh_config = True
env.hosts = ['deploy-test']
# env.hosts = ['45.55.209.211']
# env.user = 'serial'
# env.key_filename = '~/.ssh/id_series'

git_repo        = 'git@github.com:georgehunter/deploy-test'
git_branch      = 'master'
release_dir     = '/home/application/hello-world.com/releases'
current_release = '/home/application/hello-world.com/current'
repo_dir        = '/home/application/hello-world.com/repo'
persist_dir     = '/home/application/hello-world.com/persist'
next_release    = "%(time).0f" % {'time': time()}

@task
def deploy():
    init()
    update_git()
    create_release()
    build_site()
    swap_symlinks()

def init():
    if not exists(release_dir):
        run("mkdir -p %s" % release_dir)

    if not exists(repo_dir):
        run("git clone -b %s %s %s" % (git_branch, git_repo, repo_dir))

    if not exists("%s/storage" % persist_dir):
        run("mkdir -p %s/storage" % persist_dir)
        run("mkdir -p %s/storage/app" % persist_dir)
        run("mkdir -p %s/storage/framework" % persist_dir)
        run("mkdir -p %s/storage/framework/cache" % persist_dir)
        run("mkdir -p %s/storage/framework/session" % persist_dir)
        run("mkdir -p %s/storage/framework/views" % persist_dir)
        run("mkdir -p %s/storage/logs" % persist_dir)

def update_git():
    with cd(repo_dir):
        run("git checkout %s" % git_branch)
        run("git pull origin %s" % git_branch)

def create_release():
    release_into = "%s/%s" % (release_dir, next_release)
    run("mkdir -p %s" % release_into)
    with cd(repo_dir):
        run("git archive --worktree-attributes %s | tar -x -C %s" % (git_branch, release_into))

def build_site():
    with cd("%s/%s" % (release_dir, next_release)):
        run("composer install")

def swap_symlinks():
    # Build release directory
    release_into = "%s/%s" % (release_dir, next_release)

    # Symlink new .env and existing storage
    run("ln -nfs %s/.env %s/.env" % (persist_dir, release_into))
    run("rm -rf %s/storage" % release_into)
    run("ln -nfs %s/storage %s/storage" % (persist_dir, release_into))

    # Put site live
    run("ln -nfs %s %s" % (release_into, current_release))

    # Reload PHP-FPM gracefully
    run('sudo service php7.1-fpm reload')
