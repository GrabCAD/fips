"""wrapper for some git commands"""

import os
import re
import subprocess
from mod import log

name = 'git'
platforms = ['linux', 'osx', 'win']
optional = False
not_found = "git not found in path, can't happen(?)"

# default git clone depth
clone_depth = 10

#-------------------------------------------------------------------------------
def check_exists(fips_dir=None) :
    """test if git is in the path
    
    :returns:   True if git is in the path
    """
    try :
        subprocess.check_output(['git', '--version'])
        return True
    except (OSError, subprocess.CalledProcessError) :
        return False

#-------------------------------------------------------------------------------
def check_exists_with_error():
    """checks if git exists, and if not throws a fatal error"""
    if not check_exists():
        log.error("git not found, please run and fix './fips diag tools'")
        return False

#-------------------------------------------------------------------------------
def get_url_with_personal_access_token(url):
    """return the repo url for private repos using a github personal access token

         handles both git@github.com and https://github.com urls
            (they are converted to https with the PAT).

       ref: https://github.com/settings/tokens
    
    :param url:     the git url for the repo
    :returns:       the git url for the repo with the token added for private repo access
                    or the original url if the token is not available
    """
    github_https_url = 'https://github.com/'
    github_gitssh_url = 'git@github.com:'

    if github_personal_access_token := os.environ.get(
        'FIPS_GITHUB_PERSONAL_ACCESS_TOKEN', None
    ):
        url_remainder_start = 0
        if url.startswith(github_https_url):
            url_remainder_start = len(github_https_url)
        elif url.startswith(github_gitssh_url):
            url_remainder_start = len(github_gitssh_url)

        if url_remainder_start > 0:
            url = f'https://{github_personal_access_token}@github.com/{url[url_remainder_start:]}'

    return url

#-------------------------------------------------------------------------------
def clone(url, branch, depth, name, cwd):
    """git clone a remote git repo
    
    :param url:     the git url to clone from
    :param branch:  branch name (can be None)
    :param depth:   how deep to clone
    :param name:    the directory name to clone into
    :param cwd:     the directory where to run git
    :returns:       True if git returns successful
    """
    check_exists_with_error()
    cmd = 'git clone --recursive'
    if branch:
        cmd += f' --branch {branch} --single-branch'
    if depth:
        cmd += f' --depth {depth}'

    url = get_url_with_personal_access_token(url)
    cmd += f' {url} {name}'
    res = subprocess.call(cmd, cwd=cwd, shell=True)
    return res == 0

#-------------------------------------------------------------------------------
def add(proj_dir, update=False):
    """runs a 'git add .' in the provided git repo

    :param proj_dir:    path to a git repo
    :update:    if True, will run 'git add -u'
    """
    check_exists_with_error()
    cmd = 'git add ' + '-u' if update else '.'
    try:
        subprocess.check_call('git add .', cwd=proj_dir, shell=True)
    except subprocess.CalledProcessError as e:
        log.error(f"'git add .' failed with '{e.returncode}'")

#-------------------------------------------------------------------------------
def commit(proj_dir, msg):
    """runs a 'git commit -m msg' in the provided git repo

    :param proj_dir:    path to a git repo
    """
    check_exists_with_error()
    try:
        subprocess.check_call(f'git commit -m "{msg}"', cwd=proj_dir, shell=True)
    except subprocess.CalledProcessError as e:
        log.error(f"'git commit' failed with '{e.returncode}'")

#-------------------------------------------------------------------------------
def commit_allow_empty(proj_dir, msg):
    """same as commit(), but uses the --allow-empty arg so that the
    commit doesn't fail if there's nothing to commit.

    :param proj_dir:    path to a git repo
    """
    check_exists_with_error()
    try:
        subprocess.check_call(
            f'git commit --allow-empty -m "{msg}"', cwd=proj_dir, shell=True
        )
    except subprocess.CalledProcessError as e:
        log.error(f"'git commit' failed with '{e.returncode}'")

#-------------------------------------------------------------------------------
def push(proj_dir):
    """runs a 'git push' in the provided git repo
    
    :param proj_dir:    path to git repo
    """
    check_exists_with_error()
    try:
        res = subprocess.check_call('git push', cwd=proj_dir, shell=True)
    except subprocess.CalledProcessError as e:
        log.error(f"'git push' failed with '{e.returncode}'")

#-------------------------------------------------------------------------------
def has_local_changes(proj_dir):
    """checks if a git repo has uncommitted or unpushed changes (basically
    anything which would make a git pull unsafe"""
    check_exists_with_error()
    if output := subprocess.check_output(
        'git status --porcelain', cwd=proj_dir, shell=True
    ).decode("utf-8"):
        return True
    # get current branch name and tracked remote if exists, this has
    # either the form:
    #       ## master...origin/master [optional stuff]
    # ...if there's a remote tracking branch setup, or just
    #       ## my_branch
    # ...if this is a local branch
    #
    cur_status = subprocess.check_output('git status -sb', cwd=proj_dir, shell=True).decode("utf-8")[3:].rstrip().split(' ')[0]
    if '...' in cur_status:
        str_index = cur_status.find('...')
        cur_branch = cur_status[:str_index]
        cur_remote = cur_status[str_index+3:]
    else:
        cur_branch = cur_status
        cur_remote = ''
    if output := subprocess.check_output(
        f'git log {cur_remote}..{cur_branch} --oneline',
        cwd=proj_dir,
        shell=True,
    ).decode("utf-8"):
        return True

#-------------------------------------------------------------------------------
def update_submodule(proj_dir):
    """runs a 'git submodule sync --recursive' followed by a
    git submodule update --recursive' on the provided git repo,
    unconditionally (it will *not* check for local changes)

    :param proj_dir:    a git repo dir
    """
    check_exists_with_error()
    try:
        subprocess.call('git submodule sync --recursive', cwd=proj_dir, shell=True)
        subprocess.call('git submodule update --recursive', cwd=proj_dir, shell=True)
    except subprocess.CalledProcessError:
        log.error("Failed to call 'git submodule sync/update'")

#-------------------------------------------------------------------------------
def update(proj_dir):
    """runs a git pull --rebase && git submodule update --recursive on the
    provided git repo, but only if the repo has no local changes

    :param proj_dir:    a git repo dir
    """
    check_exists_with_error()
    if not has_local_changes(proj_dir):
        subprocess.call('git pull', cwd=proj_dir, shell=True)
        update_submodule(proj_dir)
        return True
    else:
        log.warn(f'skipping {proj_dir}, uncommitted or unpushed changes!')
        return False

#-------------------------------------------------------------------------------
def get_branches(proj_dir) :
    """get a dictionary with all local branch names of a git repo as keys,
    and their remote branch names as value
    
    :param proj_dir:    a git repo dir
    :returns:           dictionary of all local and remote branches
    """
    branches = {}
    try:
        output = subprocess.check_output('git branch -vv', cwd=proj_dir, shell=True).decode("utf-8")
        lines = output.splitlines()
        for line in lines :
            tokens = line[2:].split()
            local_branch = tokens[0]
            if re.compile("^\[.*(:|\])$").match(tokens[2]) :
                remote_branch = tokens[2][1:-1]
                branches[local_branch] = remote_branch
    except subprocess.CalledProcessError :
        log.error("failed to call 'git branch -vv'")
    return branches;

#-------------------------------------------------------------------------------
def checkout(proj_dir, revision):
    """checkout a specific revision hash of a repository

    :param proj_dir:    a git repo dir
    :param revision:    SHA1 hash of the commit
    :returns:           True if git returns successful
    """
    try:
        output = subprocess.check_output(
            f'git checkout {revision}', cwd=proj_dir, shell=True
        ).decode("utf-8")
        update_submodule(proj_dir)
        return output.split(':')[0] != 'error'
    except subprocess.CalledProcessError :
        log.error("failed to call 'git checkout'")
        return None

#-------------------------------------------------------------------------------
def has_uncommitted_files(proj_dir):
    """check whether a git repo has uncommitted files

    :param proj_dir:    a git repo dir
    :returns:           True/False and output string
    """
    try:
        output = subprocess.check_output('git status -s', cwd=proj_dir, shell=True).decode("utf-8")
        return (True, output) if len(output) > 0 else (False, output)
    except subprocess.CalledProcessError :
        log.error("failed to call 'git status -s'")
        return False, ''

#-------------------------------------------------------------------------------
def get_remote_rev(proj_dir, remote_branch):
    """get the head rev of a remote branch

    :param proj_dir:        a git repo dir
    :param remote_branch:   remote branch (e.g. origin/master)
    :returns:               the revision string of the remote branch head or None
    """
    tokens = remote_branch.split('/')
    try:
        output = subprocess.check_output(
            f'git ls-remote {tokens[0]} {tokens[1]}', cwd=proj_dir, shell=True
        ).decode("utf-8")
        # can return an empty string if the remote branch doesn't exist
        return output.split()[0] if output != '' else None
    except subprocess.CalledProcessError :
        log.error("failed to call 'git ls-remote'")
        return None

#-------------------------------------------------------------------------------
def get_local_rev(proj_dir, local_branch):
    """get the head rev of a local branch

    :param proj_dir:        a git repo dir
    :param local_branch:    local branch name (e.g. master)
    :returns:               the revision string of the local branch head or None
    """
    try:
        output = subprocess.check_output(
            f'git rev-parse {local_branch}', cwd=proj_dir, shell=True
        ).decode("utf-8")
        return output.rstrip()
    except subprocess.CalledProcessError :
        log.error("failed to call 'git rev-parse'")
        return None

#-------------------------------------------------------------------------------
def check_out_of_sync(proj_dir):
    """check through all branches of the git repo in proj_dir and
    returns an array of all branches that are out-of-sync with their
    remote branches (either have unpushed local changes, or un-pulled
    remote changes)

    :param proj_dir:    a git repo directory
    :returns:           array with branch names that are out-of-sync
    """
    check_exists_with_error()

    out_of_sync = False

    # first check whether there are uncommitted changes
    status, status_output = has_uncommitted_files(proj_dir)
    if status:
        out_of_sync = True
        log.warn(f"'{proj_dir}' has uncommitted changes:")
        log.info(status_output)

    # check whether local and remote branch are out of sync
    branches_out_of_sync = False
    branches = get_branches(proj_dir)
    if not branches:
        log.warn(f"'{proj_dir}' no remote branches found")
    for local_branch in branches:
        remote_branch = branches[local_branch]
        if remote_rev := get_remote_rev(proj_dir, remote_branch):
            local_rev = get_local_rev(proj_dir, local_branch)
            if remote_rev != local_rev:
                out_of_sync = True
                if not branches_out_of_sync:
                    # only show this once
                    log.warn(f"'{proj_dir}' branches out of sync:")
                    branches_out_of_sync = True
                log.info(f"  {local_branch}: {local_rev}")
                log.info(f"  {remote_branch}: {remote_rev}")

    return out_of_sync

#-------------------------------------------------------------------------------
def check_branch_out_of_sync(proj_dir, branch):
    """check if a single branch is out of sync with remote repo"""
    check_exists_with_error()

    out_of_sync = False
    remote_branches = get_branches(proj_dir)
    local_rev = get_local_rev(proj_dir, branch)
    if branch in remote_branches:
        remote_rev = get_remote_rev(proj_dir, remote_branches[branch])
        out_of_sync = remote_rev != local_rev
    else:
        log.warn(f"'{proj_dir}' no remote branch found for '{branch}'")

    return out_of_sync
