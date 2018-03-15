#!/usr/bin/env python
# encoding: utf-8


"""EMC Command Line Interface"""

import sys
import argparse
import logging
from EMCUnity import *

module = sys.modules['__main__'].__file__
log = logging.getLogger(module)

def parse_command_line(argv):
    """Parse command line argument. See -h option

    :param argv: arguments on the command line must include caller file name.
    """
    formatter_class = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(description=__doc__)

    # Optional Arguments
    parser.add_argument('-e', '--host', dest='host', default="usdwest01emc",
                        type=str, help='Hostname of EMC Unity device')
    parser.add_argument('-u', '--user', dest='user', type=str, default="restapi",
                        help='Username used for EMC Array login')
    parser.add_argument('-p', '--password', dest='password', action='store_true',
                        help='Prompt for Password')
    #parser.add_argument("--version", action="version",
    #                    version="%(prog)s {}".format(__version__))
    parser.add_argument("-v", "--verbose", dest="verbose_count",
                        action="count", default=0,
                        help="increases log verbosity for each occurence.")
    parser.add_argument('-o', metavar="output",
                        type=argparse.FileType('w'), default=sys.stdout,
                        help="redirect output to a file")

    # Sub-Commands
    # Functions can be defined as their own subcommands
    subparsers = parser.add_subparsers(title='subcommands',
                                       description='valid subcommands',
                                       dest='subparser_name' )

    def subcommand(func, aliases=[], parent=subparsers):
        parser = parent.add_parser(func.__name__, aliases=aliases, help=func.__doc__)
        parser.set_defaults(func=func)
        return parser

    # def create_lun(self, lun_name, pool_id, size, lun_description=None):
    # Unity.create_lun.__code__.co_varnames
    p_create_lun = subcommand(Unity.create_lun, aliases=['cl'])
    p_create_lun.add_argument('-o', '--pool', dest='pool', default="pool_1",
                                   type=str, help='Name of Pool of str arg')
    p_create_lun.add_argument('-s', '--size', dest='size', default="p1099511627776",
                                   type=str, help='Name of Pool of str arg')
    p_create_lun.add_argument('lun_name', metavar='lun_name', type=str,
                        help='Name of LUN to create in format: ldom-vol#')

#    def get_from_type(self, url_path, object_type, payload = None):
#        """
#        Performs a request of all fields for a given object_type unless
#        specific fields have been requested as part of the payload
#        """
    p_get_from_type = subcommand(Unity.get_from_type, aliases=['get'])
    p_get_from_type.add_argument('object_type', metavar='object_type', type=str,
                        help='the object type to return')

    p_delete_lun = subcommand(Unity.delete_lun)
    p_delete_lun.add_argument('lun_id', metavar='lun_id', type=str,
                                   help='Storage Resource lun_id')


    # parse the args and call whatever function was selected
    args = parser.parse_args()
    return args

def main():
    """Main program. Sets up logging and do some work."""
    log.info(sys.argv)
    args = parse_command_line(sys.argv)
    levels = [logging.WARNING, logging.INFO, logging.DEBUG]
    level = levels[min(len(levels)-1,args.verbose_count)]  # capped to number of levels
    log.info("Arguments: {}".format(args))
    logging.basicConfig(stream=sys.stderr, level=level,
                        format='%(name)s (%(levelname)s): %(message)s')
    # Sets log level to WARN going more verbose for each new -v.
    log.setLevel(max(3 - args.verbose_count, 0) * 10)

    # Never ask for a password in command-line. Manually ask for it here
    if args.password:
        password = getpass.getpass()
    else:
        #for now using default password
        password = 'NceSsa7I3STo!'

    try:
        # Create the unity session
        #unity = Unity('unity.ktelep.local','admin','TooManySecrets')
        unity = Unity(args.host, args.user, password)
        args.func(args)
    except KeyboardInterrupt:
        log.error('Program interrupted!')
    finally:
        logging.shutdown()

if __name__ == "__main__":
    sys.exit(main())
