"""package fips project into a zip file

package
package [config]
"""

import os
import zipfile

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
def template_specialize(src, replacements) :
    dest = src
    for key,val in replacements:
        dest = dest.replace(key, val)
    return dest

#-------------------------------------------------------------------------------
def run(fips_dir, proj_dir, args) :
    """pacakge fips project"""
    if not util.is_valid_project_dir(proj_dir) :
        log.error('must be run in a project directory')
    cfg_name = None
    if len(args) > 0 :
        cfg_name = args[0]
    if not cfg_name :
        cfg_name = settings.get(proj_dir, 'config')
    log.info("fips package {}".format(cfg_name))
    proj_name = util.get_project_name_from_dir(proj_dir)
    platform = util.get_platform_from_config(cfg_name)
    rules = get_package_rules(fips_dir, proj_dir)
    if not rules:
        log.error('no packaging rules defined in fips.yml')
        return
    workspace_dir = util.get_workspace_dir(fips_dir)
    dist_dir = os.path.join(workspace_dir, 'fips-dist', proj_name, cfg_name)
    if not os.path.exists(dist_dir) :
        log.info('creating {}'.format(dist_dir))
        os.makedirs(dist_dir)
    version = rules.get('version')
    if not version:
            version = 'dev'
    package_root_dir = rules.get('package_root_dir')
    if not package_root_dir:
        package_root_dir = proj_dir
    zip_name = rules.get('filename')
    if not zip_name:
        zip_name = '%s-%s-%s.zip' % (proj_name, version, platform)
    replacements = [
        ('$FIPS_DIR', workspace_dir),
        ('$VERSION', version),
        ('$PLATFORM', platform),
        ('$CONFIG', cfg_name),
        ('$PROJ_NAME', proj_name),
    ]
    zip_name = template_specialize(zip_name, replacements)
    contents = rules.get('contents')
    if not contents:
        log.error('no package contents defined in fips.yml package section')
        return
    zip_file = os.path.join(dist_dir, zip_name)
    with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as archive_file:
        for content in contents:
            src = content.get('src')
            dest = content.get('dest')
            if not src:
                log.error('package content is missing src field')
                continue
            if not dest:
                dest = os.path.relpath(src, proj_dir)
            src = template_specialize(src, replacements)
            dest = template_specialize(dest, replacements)
            if not os.path.exists(src):
                log.error('package source {} does not exist'.format(src))
                continue
            if os.path.isdir(src):
                for root, _dirnames, filenames in os.walk(src):
                    common = os.path.commonprefix([src, root])
                    for filename in filenames:
                        src_path = os.path.join(root, filename)
                        archive_path = os.path.join(dest, root[len(common) + 1:], filename)
                        log.colored(log.DEF, '{} -> {}'.format(src_path, archive_path))
                        archive_file.write(src_path, archive_path)
            else:
                if dest == '.':
                    dest = src
                # log.colored(log.YELLOW, '  src:  {}'.format(src))
                # log.colored(log.YELLOW, '  dest: {}'.format(dest))
                src_path = src
                archive_path = dest
                log.colored(log.DEF, '{} -> {}'.format(src_path, archive_path))
                archive_file.write(src_path, archive_path)
    log.info('wrote package {}'.format(zip_file))


#-------------------------------------------------------------------------------
def help() :
    """print package help"""
    log.info(log.YELLOW +
            "fips package\n"
            "fips package [config]\n" + log.DEF +
            "    create package for current or named config")

