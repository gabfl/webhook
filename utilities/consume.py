import sys
import requests
from subprocess import call

import argparse

ingest_filename = 'ingest.py'

# Compatible versions of ingest.py
ingest_compatible_versions = ['1.0']

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
                    help="Open file with a program")
args = parser.parse_args()


def read_body():
    """ Read body from first webhook """

    r = requests.get(args.inspect)

    if r.status_code != 200:
        raise RuntimeError(
            'Failed to read inspect API. Error %d.' % (r.status_code))

    # Get first callback
    callback = r.json()['callbacks'][0]

    x_origin_version = callback['headers'].get('X-Origin-Version', '1.0')
    if x_origin_version not in ingest_compatible_versions:
        raise RuntimeError(
            'This payload was ingested with %s v%s.\nPlease a compatible version of %s.' % (ingest_filename, x_origin_version, __file__))

    return callback['body']['data']


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
