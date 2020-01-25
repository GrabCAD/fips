"""package fips project into a zip file

package
package [config]
"""

from mod import log, util, project, settings

#-------------------------------------------------------------------------------
def get_package_rules(fips_dir, proj_dir) :
    """get the rules for packaging

    :param proj_dir:    the project directory
    :returns:           dictionary object with packaging rules (can be empty)
    """
    dic = {}
    if util.is_valid_project_dir(proj_dir) :
        dic = util.load_fips_yml(proj_dir)
    return dic.get("package")

#-------------------------------------------------------------------------------
def run(fips_dir, proj_dir, args) :
    """pacakge fips project"""
    if not util.is_valid_project_dir(proj_dir) :
        log.error('must be run in a project directory')
    cfg_name = None
    tool_args = None
    if '--' in args:
        idx = args.index('--')
        tool_args = args[(idx + 1):]
        args = args[:idx]
    if len(args) > 0 :
        cfg_name = args[0]
    if not cfg_name :
        cfg_name = settings.get(proj_dir, 'config')
    log.info("fips package-prebuilt %s".format(cfg_name))
    rules = get_package_rules(fips_dir, proj_dir)
    print(rules)
    # project.build(fips_dir, proj_dir, cfg_name, None, tool_args)


#-------------------------------------------------------------------------------
def help() :
    """print package help"""
    log.info(log.YELLOW +
            "fips package\n"
            "fips package [config]\n" + log.DEF +
            "    create package for current or named config")

