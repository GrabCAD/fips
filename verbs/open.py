"""implement the 'open' verb

open
open [config]
"""

import os
import glob
import subprocess

from mod import log, util, settings, config, project
from mod.tools import vscode, clion

#-------------------------------------------------------------------------------
def run(fips_dir, proj_dir, args):
    """run the 'open' verb (opens project in IDE)"""
    if not util.is_valid_project_dir(proj_dir) :
        log.error('must be run in a project directory')
    proj_name = util.get_project_name_from_dir(proj_dir)
    cfg_name = args[0] if len(args) > 0 else None
    if not cfg_name :
        cfg_name = settings.get(proj_dir, 'config')

    if configs := config.load(fips_dir, proj_dir, cfg_name):
        # hmm, only look at first match, 'open' doesn't
        # make sense with config-patterns
        cfg = configs[0]

        # find build dir, if it doesn't exist, generate it
        build_dir = util.get_build_dir(fips_dir, proj_name, cfg['name'])
        if not os.path.isdir(build_dir) :
            log.warn("build dir not found, generating...")
            project.gen(fips_dir, proj_dir, cfg['name'])

        # first check if this is a VSCode project
        if cfg['build_tool'] == 'vscode_cmake':
            vscode.run(proj_dir)
            return
        # check if this is a CLion project
        if cfg['build_tool'] == 'clion':
            clion.run(proj_dir)
            return
        if proj := glob.glob(f'{build_dir}/*.xcodeproj'):
            subprocess.call(f'open "{proj[0]}"', shell=True)
            return
        if proj := glob.glob(f'{build_dir}/*.sln'):
            subprocess.call(f'cmd /c start {proj[0]}', shell=True)
            return
        if proj := glob.glob(f'{build_dir}/.cproject'):
            subprocess.call(
                f'eclipse -nosplash --launcher.timeout 60 -application org.eclipse.cdt.managedbuilder.core.headlessbuild -import "{build_dir}"',
                shell=True,
            )
            subprocess.call('eclipse', shell=True)
            return

        log.error(
            f"don't know how to open a '{cfg['generator']}' project in {build_dir}"
        )
    else:
        log.error(f"config '{cfg_name}' not found")

#-------------------------------------------------------------------------------
def help() :
    """print help for verb 'open'"""
    log.info(log.YELLOW + 
            "fips open\n" 
            "fips open [config]\n" + log.DEF +
            "   open IDE for current or named config")

