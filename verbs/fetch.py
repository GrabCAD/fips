"""fetch project imports

fetch
fetch [project]
"""

from mod import log, util, dep, settings, config

#-------------------------------------------------------------------------------
def run(fips_dir, proj_dir, args) :
    """fetch external project imports

    :param fips_dir:    absolute fips directory
    :param proj_dir:    absolute project directory
    :args:              additional args
    """
    if len(args) > 0 :
        proj_name = args[0]
        proj_dir = util.get_project_dir(fips_dir, proj_name)
    cfg_name = settings.get(proj_dir, 'config')
    configs = config.load(fips_dir, proj_dir, cfg_name)
    if configs :
        for cfg in configs :
            # check if config is valid
            config_valid, _ = config.check_config_valid(fips_dir, proj_dir, cfg, print_errors = True)
            if config_valid :
                platform = cfg['platform']
                dep.fetch_imports(fips_dir, proj_dir, platform)
            else :
                log.error("'{}' is not a valid config".format(cfg['name']), False)
    else :
        log.error("No configs found for '{}'".format(cfg_name))

#-------------------------------------------------------------------------------
def help() :
    """print fetch help"""
    log.info(log.YELLOW + 
            "fips fetch\n" 
            "fips fetch [proj]\n" + log.DEF +
            "    fetch external dependencies for current or named project") 


