#!/usr/bin/python
from EMCUnity import *
from argparse import ArgumentParser

cli = ArgumentParser()
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
    luns = unity.lun(item_filter=args.item_filter, item_id=args.item_id, item_name=args.item_name)
    for lun in luns:
        print lun.name
        print lun.health
        print lun.id
        print lun.hostAccess

@subcommand([argument("-e", "--host", dest='host', default="usdwest01emc", type=str, help="Hostname of EMC Unity Device"),
             argument("-p", "--pool", dest='pool', default="pool_1", type=str, help="Name of Pool of str arg"),
             argument("-s", "--size", dest='size', default="1099511627776", type=str, help="Size of Pool as unsigned integer (default of 1TB)"),
             argument("-d", "--description", dest='description', default=None, type=str, help="Description of new Lun object"),
             argument("lun_name",  metavar='lun_name', type=str, help="Size of Pool as unsigned integer (default of 1TB)")])
def create_lun(args):
    unity = Unity(args.host, 'restapi', 'NceSsa7I3STo!')
    lun = unity.create_lun(args)
    print lun

@subcommand([argument("-d", help="Debug mode", action="store_true")])
def test(args):
    print(args)


@subcommand([argument("-f", "--filename", help="A thing with a filename")])
def filename(args):
    print(args.filename)


@subcommand([argument("name", help="Name")])
def name(args):
    print(args.name)


if __name__ == "__main__":
    args = cli.parse_args()
    if args.subcommand is None:
        cli.print_help()
    else:
        args.func(args)
