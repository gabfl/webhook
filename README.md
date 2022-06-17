# webhook

[![Build Status](https://github.com/gabfl/webhook/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/gabfl/webhook/actions)
[![codecov](https://codecov.io/gh/gabfl/webhook/branch/main/graph/badge.svg)](https://codecov.io/gh/gabfl/webhook)
[![MIT licensed](https://img.shields.io/badge/license-MIT-green.svg)](https://raw.githubusercontent.com/gabfl/webhook/main/LICENSE)

Webhook is an open source project available at [https://webhook.link](https://webhook.link).

It allows you to easily test webhooks and other HTTP requests and log their attributes and payloads.

## Usage example

This projects generates random ephemeral routes like `/3989c985-0659-4c2d-b38f-9d83d74fe0bb`.

You can send any HTTP request to the route, for example:

```bash
curl -X POST https://webhook.link/3989c985-0659-4c2d-b38f-9d83d74fe0bb \
-H "Content-Type: application/json" \
-H "X-MyHeader: 123" \
-d '{"hello": "world", "is_true": true}'
```

And the result will be available on `/inspect/3989c985-0659-4c2d-b38f-9d83d74fe0bb`:

![Demo](img/screenshot.png?raw=true)


## Installation

```bash
$ cd webhook/
$ pip3 install -r requirements.txt
$ python3 -m src
```

## Try it out in docker
* Build the image: `docker build webhook:latest .`
* Run the image: `docker run -it --rm -p 5000:5000 webhook:latest`
* [Open in browser](http://localhost:5000)
