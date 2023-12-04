"""implement 'gdb' verb (debugs a single target with gdb)

gdb
gdb [target]
gdb [target] [config]
"""

import subprocess

from mod import log, util, config, project, settings

#-------------------------------------------------------------------------------
def gdb(fips_dir, proj_dir, cfg_name, target=None, target_args=None):
    """debug a single target with gdb"""

    # prepare
    proj_name = util.get_project_name_from_dir(proj_dir)
    util.ensure_valid_project_dir(proj_dir)

    if configs := config.load(fips_dir, proj_dir, cfg_name):
        for cfg in configs:
            # check if config is valid
            config_valid, _ = config.check_config_valid(fips_dir, proj_dir, cfg, print_errors = True)
            if config_valid:
                deploy_dir = util.get_deploy_dir(fips_dir, proj_name, cfg['name'])
                log.colored(log.YELLOW, f"=== gdb: {cfg['name']}")
                cmdLine = ['gdb', "-ex", "run", "--args", target]
                if target_args :
                    cmdLine.extend(target_args)
                try:
                    subprocess.call(args = cmdLine, cwd = deploy_dir)
                except OSError :
                    log.error("Failed to execute gdb (not installed?)")
            else:
                log.error(f"Config '{cfg['name']}' not valid in this environment")
    else:
        log.error(f"No valid configs found for '{cfg_name}'")

    return True

#-------------------------------------------------------------------------------
def run(fips_dir, proj_dir, args):
    """debug a single target with gdb"""
    if not util.is_valid_project_dir(proj_dir) :
        log.error('must be run in a project directory')
    target_args = []
    if '--' in args :
        idx = args.index('--')
        target_args = args[(idx + 1):]
        args = args[:idx]
    tgt_name = args[0] if len(args) > 0 else None
    cfg_name = args[1] if len(args) > 1 else None
    if not cfg_name :
        cfg_name = settings.get(proj_dir, 'config')
    if not tgt_name :
        tgt_name = settings.get(proj_dir, 'target')
    if not tgt_name :
        log.error('no target specified')
    gdb(fips_dir, proj_dir, cfg_name, tgt_name, target_args)

#-------------------------------------------------------------------------------
def help() :
    """print 'gdb' help"""
    log.info(log.YELLOW +
            "fips gdb [-- args]\n"
            "fips gdb [target] [-- args]\n"
            "fips gdb [target] [config] [-- args]\n" + log.DEF +
            "   debug a single target in current or named config")
