"""unset a default setting

unset config
unset target
"""

from mod import log, settings

valid_nouns = ['config', 'target', 'jobs', 'ccache']

#-------------------------------------------------------------------------------
def run(fips_dir, proj_dir, args):
    """run the 'unset' verb"""
    if len(args) > 0:
        noun = args[0]
        if noun in valid_nouns:
            settings.unset(proj_dir, noun)
        else:
            log.error(f"invalid noun '{noun}', must be: {', '.join(valid_nouns)}")
    else:
        log.error(f"expected noun: {', '.join(valid_nouns)}")

#-------------------------------------------------------------------------------
def help():
    """print 'unset' help"""
    log.info(
        f"{log.YELLOW}fips unset [{'|'.join(valid_nouns)}]\n{log.DEF}    unset currently active config or make-target"
    )


    
