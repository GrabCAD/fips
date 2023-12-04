"""wrapper for cmake tool"""
import subprocess
from subprocess import PIPE
import platform

from mod import log,util
from mod.tools import ninja

name = 'cmake'
platforms = ['linux', 'osx', 'win']
optional = False
not_found = 'please install cmake 2.8 or newer'

#------------------------------------------------------------------------------
def check_exists(fips_dir, major=2, minor=8):
    """test if cmake is in the path and has the required version
    
    :returns:   True if cmake found and is the required version
    """
    try:
        out = subprocess.check_output(['cmake', '--version']).decode("utf-8")
        ver = out.split()[2].split('.')
        if int(ver[0]) > major or (int(ver[0]) == major and int(ver[1]) >= minor):
            return True
        log.info(
            f'{log.RED}NOTE{log.DEF}: cmake must be at least version {major}.{minor} (found: {ver[0]}.{ver[1]}.{ver[2]})'
        )
        return False
    except (OSError, subprocess.CalledProcessError):
        return False

#------------------------------------------------------------------------------
def run_gen(cfg, fips_dir, project_dir, build_dir, toolchain_path, defines):
    """run cmake tool to generate build files
    
    :param cfg:             a fips config object
    :param project_dir:     absolute path to project (must have root CMakeLists.txt file)
    :param build_dir:       absolute path to build directory (where cmake files are generated)
    :param toolchain:       toolchain path or None
    :returns:               True if cmake returned successful
    """
    cmdLine = 'cmake'
    if cfg['generator'] != 'Default':
        cmdLine += f""" -G "{cfg['generator']}\""""
    if cfg['generator-platform']:
        cmdLine += f""" -A "{cfg['generator-platform']}\""""
    if cfg['generator-toolset']:
        cmdLine += f""" -T "{cfg['generator-toolset']}\""""
    cmdLine += f" -DCMAKE_BUILD_TYPE={cfg['build_type']}"
    if cfg['build_tool'] == 'ninja' and platform.system() == 'Windows':
        cmdLine += f' -DCMAKE_MAKE_PROGRAM={ninja.get_ninja_tool(fips_dir)}'
    if toolchain_path is not None:
        cmdLine += f' -DCMAKE_TOOLCHAIN_FILE={toolchain_path}'
    cmdLine += f" -DFIPS_CONFIG={cfg['name']}"
    if cfg['defines'] is not None:
        for key in cfg['defines']:
            val = cfg['defines'][key]
            if type(val) is bool:
                cmdLine += f" -D{key}={'ON' if val else 'OFF'}"
            else:
                cmdLine += f' -D{key}="{val}"'
    for key in defines:
        cmdLine += f' -D{key}={defines[key]}'
    cmdLine += f' -B{build_dir}'
    cmdLine += f' -H{project_dir}'

    print(cmdLine)
    res = subprocess.call(cmdLine, cwd=build_dir, shell=True)
    return res == 0

#------------------------------------------------------------------------------
def run_build(fips_dir, target, build_type, build_dir, num_jobs=1):
    """run cmake in build mode

    :param target:          build target, can be None (builds all)
    :param build_type:      CMAKE_BUILD_TYPE string (e.g. Release, Debug)
    :param build_dir:       path to the build directory
    :param num_jobs:        number of parallel jobs (default: 1)
    :returns:               True if cmake returns successful
    """
    cmdLine = f'cmake --build . --config {build_type}'
    if target:
        cmdLine += f' --target {target}'
    if platform.system() == 'Windows':
        cmdLine += f' -- /nologo /verbosity:minimal /maxcpucount:{num_jobs}'
    else:
        cmdLine += f' -- -j{num_jobs}'
    print(cmdLine)
    res = subprocess.call(cmdLine, cwd=build_dir, shell=True)
    return res == 0

#------------------------------------------------------------------------------
def run_clean(fips_dir, build_dir) :
    """run cmake in build mode

    :param build_dir:   path to the build directory
    :returns:           True if cmake returns successful    
    """
    try :
        res = subprocess.call('cmake --build . --target clean', cwd=build_dir, shell=True)
        return res == 0
    except (OSError, subprocess.CalledProcessError) :
        return False
