import sys
import requests

webhook_host = 'https://webhook.link/'
consume_filename = 'consume.py'


def new_route():
    """ Create a new route, get webhook URL """

    r = requests.get(webhook_host + 'api/new')

    if r.status_code != 200:
        raise RuntimeError(
            'Failed to create webhook. Error %d.' % (r.status_code))

    return (r.json()['routes']['webhook'], r.json()['routes']['inspect']['api'])


def read_stdin():
    """ Read and return stdin """

    if sys.stdin.isatty():
        print('Usage:')
        print('  some_command | python3 %s' % (__file__))
        sys.exit()

    stdin = ''
    for line in sys.stdin:
        stdin += line

    return stdin


def call_webhook(route, body):
    """ Post a payload to a webhook """

    r = requests.post(
        route,
        data=body,
        headers={
            "content-type": "text",
            "X-Origin": __file__,
            "X-Origin-Version": "1.0",
        }
    )

    if r.status_code != 200:
        raise RuntimeError(
            'Failed to post webhook. Error %d.' % (r.status_code))


route, inspect = new_route()
call_webhook(route, read_stdin())

print('OK')
print('Consume this data with:')
print('  python3 %s -i %s' % (consume_filename, inspect))
