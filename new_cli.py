#!/usr/bin/python

"""EMC Command Line Interface"""
import sys
import logging
import getpass
from EMCUnity import *
from enum import Enum
from argparse import ArgumentParser

cli = ArgumentParser(description=__doc__)
subparsers = cli.add_subparsers(dest="subcommand")

def argument(*name_or_flags, **kwargs):
    """Convenience function to properly format arguments to pass to the
    subcommand decorator.

    """
    return name_or_flags, kwargs

def subcommand(args=[], parent=subparsers):
    """Decorator to define a new subcommand in a sanity-preserving way.
    The function will be stored in the ``func`` variable when the parser
    parses arguments so that it can be called directly like so::

        args = cli.parse_args()
        args.func(args)

    Usage example::

        @subcommand([argument("-d", help="Enable debug mode", action="store_true")])
        def subcommand(args):
            print(args)

    Then on the command line::

        $ python cli.py subcommand -d

    """
    def decorator(func):
        parser = parent.add_parser(func.__name__, description=func.__doc__)
        for arg in args:
            parser.add_argument(*arg[0], **arg[1])
        parser.set_defaults(func=func)
    return decorator


@subcommand()
def nothing(args):
    print("Nothing special!")


@subcommand([argument("-e", "--host", dest='host', default="usdwest01emc", type=str, help="Hostname of EMC Unity Device")])
def hosts(args):
    unity = Unity(args.host, 'restapi', 'NceSsa7I3STo!')
    hosts = unity.host()
    print hosts

@subcommand([argument("-e", "--host", dest='host', default="usdwest01emc", type=str, help="Hostname of EMC Unity Device"),
             argument("-f", "--item_filter", dest='item_filter', default=None, type=str, help="filter of specific UnityLUN object"),
             argument("-i", "--item_id", dest='item_id', default=None, type=str, help="id of specific UnityLUN object"),
             argument("-n", "--item_name", dest='item_name', default=None, type=str, help="Name of specific UnityLUN object")])
def luns(args):
    ''' Query the existing LUNS'''
    unity = Unity(args.host, 'restapi', 'NceSsa7I3STo!')
    print unity
    print unity.is_auth
    luns = unity.lun(item_filter=args.item_filter, item_id=args.item_id, item_name=args.item_name)
    for lun in luns:
        print lun.name
        print lun.health
        print lun.id
        print lun
        #print lun.hostAccess

@subcommand([argument("-e", "--host", dest='host', default="usdwest01emc", type=str, help="Hostname of EMC Unity Device"),
             argument("-p", "--pool", dest='pool_id', default="pool_1", type=str, help="Name of Pool of str arg"),
             argument("-s", "--size", dest='size', default="1099511627776", type=str, help="Size of Pool as unsigned integer (default of 1TB)"),
             argument("-d", "--description", dest='lun_description', default=None, type=str, help="Description of new Lun object"),
             argument("lun_name", metavar='lun_name', type=str, help="Name for LUN")])
def create_lun(args):
    """ Creates a new block LUN in pool_id, returns a lun object """
    #unity = Unity(args.host, 'restapi', 'NceSsa7I3STo!')
    unity = Unity(args.host, 'restapi', 'NceSsa7I3STo!')
    host_access_list = generateHostAccessList()
    lun_parameters = {
        'pool': {'id':args.pool_id},
        'isThinEnabled':'true',
        'isCompressionEnabled':'true',
        'size': args.size,
        'hostAccess' : host_access_list
        }
    payload = {'name':args.lun_name,
               'lunParameters': lun_parameters }

    response = unity.post('/types/storageResource/action/createLun', payload)
    new_id = response.json()['content']['storageResource']['id']
    return unity.lun(item_id=new_id)

def generateHostAccessList(hosts=""):
    '''Generate hostAccess list from list of hosts'''
    if hosts == "":
        hostAccessList = [{'host': {'id': 'Host_11'}, 'accessMask': 1},
                        {'host': {'id': 'Host_9'}, 'accessMask': 1},
                        {'host': {u'id': u'Host_8'}, 'accessMask': 1},
                        {'host': {u'id': u'Host_7'}, 'accessMask': 1},
                        {'host': {u'id': u'Host_6'}, 'accessMask': 1},
                        {'host': {u'id': u'Host_5'}, 'accessMask': 1},
                        {'host': {u'id': u'Host_4'}, 'accessMask': 1},
                        {'host': {u'id': u'Host_3'}, 'accessMask': 1},
                        {'host': {u'id': u'Host_2'}, 'accessMask': 1},
                        {'host': {u'id': u'Host_10'}, 'accessMask': 1}]
    return hostAccessList

#@subcommand([argument("-e", "--host", dest='host', default="usdwest01emc", type=str, help="Hostname of EMC Unity Device")])
@subcommand()
def test(args):
    ''' Currently Testing authenticated responses'''
    unity = Unity(args.emc, args.user, 'NceSsa7I3STo!')

    url_path = '/types/snap/instances'
    response = unity.unity_request(url_path)
    print "Is it Authorized?: {}".format(unity.is_auth)
    #print unity.snap()['0']['entries']['content']
    #print (vars(unity))
    #print unity.headers

@subcommand()
def status(args):
    ''' Default Subprocess when none is given '''
    unity = Unity(args.emc, args.user, 'NceSsa7I3STo!')
    print unity.name
    print unity.model
    print unity.software
    print "Is Authenticated: {}".format(unity.is_auth)

if __name__ == "__main__":
    '''CLI Top Level Parsing'''
    cli.add_argument('-u', '--user', dest='user', type=str, default="restapi", help='Username used for EMC Array login')
    cli.add_argument('-p', '--password', dest='password', action='store_true', help='Password for EMC Array login')
    cli.add_argument('-e', '--emc', dest='emc', default="usdwest01emc", type=str, help='Name of EMC device')
    args = cli.parse_args()
    unity = Unity(args.emc, args.user, 'NceSsa7I3STo!')
    #unity = Unity(args.host, 'restapi', 'NceSsa7I3STo!')
    if args.subcommand is None:
        print unity.name
        print unity.model
        print unity.software
        cli.print_help()
    else:
        args.func(args)
