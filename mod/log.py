"""logging functions"""
import sys

# log colors
RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[1;36m'
DEF = '\033[39m'

#-------------------------------------------------------------------------------
def error(msg, fatal=True):
    """
    Print error message and exit with error code 10 
    unless 'fatal' is False.

    :param msg:     string message
    :param fatal:   exit program with error code 10 if True (default is true)
    """
    print(f'{RED}[ERROR]{DEF} {msg}')
    if fatal :
        sys.exit(10)

#-------------------------------------------------------------------------------
def warn(msg):
    """print a warning message"""
    print(f'{YELLOW}[WARNING]{DEF} {msg}') 

#-------------------------------------------------------------------------------
def ok(item, status):
    """print a green 'ok' message

    :param item:    first part of message
    :param status:  status (colored green)
    """
    print(f'{item}:\t{GREEN}{status}{DEF}')

#-------------------------------------------------------------------------------
def failed(item, status):
    """print a red 'fail' message

    :param item:    first part of message
    :param status:  status (colored red)
    """
    print(f'{item}:\t{RED}{status}{DEF}')

#-------------------------------------------------------------------------------
def optional(item, status):
    """print a yellow 'optional' message

    :param item:    first part of message
    :param status:  status (colored red)
    """
    print(f'{item}:\t{YELLOW}{status}{DEF}')

#-------------------------------------------------------------------------------
def info(msg) :
    """print a normal log message

    :param msg: message
    """
    print(msg)

#-------------------------------------------------------------------------------
def colored(color, msg):
    """print a colored log message

    :param color:   color escape sequence (e.g. log.YELLOW)
    :param msg:     text message
    """
    print(f'{color}{msg}{DEF}')

