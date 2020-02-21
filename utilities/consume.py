import sys
import requests
from subprocess import call

import argparse

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("-i", "--inspect", type=str, help="Webhook Inspect API URL",
                    required=True)
parser.add_argument("-o", "--out",
                    help="CSV destination", choices=['stdout', 'file'],
                    default='stdout')
parser.add_argument("-f", "--destination_file",
                    help="CSV destination file", default='/tmp/consumed.txt')
parser.add_argument("-p", "--open",
                    help="Open file with a MacOS program")
args = parser.parse_args()


def read_body():
    """ Read body sent t webhook """

    r = requests.get(args.inspect)

    if r.status_code != 200:
        raise RuntimeError(
            'Failed to create webhook. Error %d.' % (r.status_code))

    return r.json()['callbacks'][0]['body']['data']


def output(output):
    """ Print output to stdout or save to a file """

    # If we chose output to stdout and we are not opening a program
    if args.out == 'stdout' and not args.open:
        print(output)
    else:
        f = open(args.destination_file, "w")
        f.write(output)
        f.close()
        print('Output saved to %s' % (args.destination_file))


body = read_body()
output(body)

if args.open:
    call(["open", "-a" + args.open, args.destination_file])
