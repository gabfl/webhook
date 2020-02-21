import requests

import argparse

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("-i", "--inspect", type=str, help="Webhook Inspect API URL",
                    required=True)
args = parser.parse_args()


inspect_api_url = args.inspect
total = 0


def load_inspect_api(url):
    """ Load inspect API and return Json response """

    r = requests.get(url)

    if r.status_code != 200:
        raise RuntimeError(
            'Failed to read inspect API. Error %d.' % (r.status_code))

    return r.json()


def loop_thru_callbacks(url):
    """ Loop thru callbacks and return next page URL """

    # Load API and retrieve Json response
    inspect = load_inspect_api(url)

    # Loop thru callbacks
    for callback in inspect['callbacks']:
        process_callback(callback)

    return inspect.get('next')


def process_callback(callback):
    """ Process a callback """

    global total

    # Read variables
    total += 1
    # args = callback['args']
    body_data = callback['body']['data']
    # body_size = callback['body']['size']
    date = callback['date']
    headers = callback['headers']
    id_ = callback['id']
    method = callback['method']
    # referrer = callback['referrer']
    # remote_addr = callback['remote_addr']

    print('**** Payload ID %s ****' % (f'{id_:,}'))
    print('Payload number: %s' % (f'{total:,}'))
    print('Method %s on %s' % (method, date))
    print('%s headers' % (len(headers)))
    print('Body -> %s' % (body_data))
    print()


next_ = inspect_api_url
while True:
    # Load a page and process webhook
    next_ = loop_thru_callbacks(next_)

    # Stop when there are no next pages
    if not next_:
        break
