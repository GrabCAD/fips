"""wrapper for ninja build tool"""
import subprocess
import platform
import shutil

name = 'ninja'
platforms = ['linux', 'osx', 'win']
optional = True
not_found = "required for building '*-ninja-*' configs"

#-------------------------------------------------------------------------------
def get_ninja_name():
    return 'ninja.exe' if platform.system() == 'Windows' else 'ninja'

#-------------------------------------------------------------------------------
def get_ninja_tool(fips_dir):
    """get the ninja tool exe"""
    if platform.system() == 'Windows':
        # on Windows, use the precompiled ninja.exe coming with fips
        return f'{fips_dir}/tools/win32/{get_ninja_name()}'
    else:
        # everywhere else, expect it in the path
        return get_ninja_name()

#-------------------------------------------------------------------------------
def prepare_ninja_tool(fips_dir, build_dir) :
    """on Windows, copies the ninja.exe into the build dir, so that cmake 
    can find it
    """
    if platform.system() == 'Windows' :
        shutil.copy(get_ninja_tool(fips_dir), build_dir)

#------------------------------------------------------------------------------
def check_exists(fips_dir):
    """test if ninja is in the path
    
    :returns: True if ninja is in the path
    """
    try:
        out = subprocess.check_output([f'{get_ninja_tool(fips_dir)}', '--version'])
        return True
    except (OSError, subprocess.CalledProcessError):
        return False;

#-------------------------------------------------------------------------------
def run_build(fips_dir, target, build_dir, num_jobs=1):
    """build a target

    :param target:      name of build target, of None
    :param build_dir:   directory of the build.ninja file
    :param num_jobs:    number of parallel jobs (default: 1)
    :returns:           True if build was successful
    """
    if not target :
        target = 'all'
    prepare_ninja_tool(fips_dir, build_dir)
    cmdLine = f"{get_ninja_name()} -j {num_jobs} {target}"
    print(cmdLine)
    res = subprocess.call(cmdLine, cwd=build_dir, shell=True)
    return res == 0

#-------------------------------------------------------------------------------
def run_clean(fips_dir, build_dir):
    """run the special 'clean' target

    :param build_dir:   directory of the build.ninja file
    :returns:           True if ninja returned without error
    """
    prepare_ninja_tool(fips_dir, build_dir)
    try:
        cmdLine = f'{get_ninja_name()} clean'
        res = subprocess.call(cmdLine, cwd=build_dir, shell=True)
        return res == 0
    except (OSError, subprocess.CalledProcessError) :
        return False


