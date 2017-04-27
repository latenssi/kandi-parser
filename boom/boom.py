from __future__ import absolute_import

# Edited from https://github.com/tarekziade/boom by Lauri Junkkari <latenssi@gmail.com>

import argparse
import gevent
import logging
import requests
import sys
import time
import re
import math
import numpy as np

try:
    import urlparse
except ImportError:
    from urllib import parse as urlparse

from collections import defaultdict, namedtuple

from gevent import monkey
from gevent.pool import Pool
from requests import RequestException
from requests.packages.urllib3.util import parse_url
from socket import gethostbyname, gaierror

from .util import resolve_name

monkey.patch_all()
logger = logging.getLogger('boom')


class RunResults(object):

    """Encapsulates the results of a single Boom run.

    Contains a dictionary of status codes to lists of request durations,
    a list of exception instances raised during the run and the total time
    of the run.
    """

    def __init__(self, num=1, url=None):
        # self.status_code_counter = defaultdict(list)
        self.all_res = []
        self.errors = []
        self.total_time = None

        if url:
            server_info = requests.head(url).headers.get('server', 'Unknown')
            self.server = re.sub(r"\s\(.*\)", "", server_info)


def calc_stats(results, url, number, concurrency):
    """Calculate stats (min, max, avg) from the given RunResults.

       The statistics are returned as a RunStats object.
    """

    all_res = results.all_res
    count = len(all_res)

    amax = np.amax(all_res)
    amin = np.amin(all_res)

    return {
        "rps": len(all_res) / float(results.total_time),
        "mean": np.mean(all_res),
        "min": amin,
        "max": amax,
        "amp": float(amax - amin),
        "median": np.median(all_res),
        "stdev": np.std(all_res),
        "perc_95": np.percentile(all_res, 95),
        "perc_80": np.percentile(all_res, 80),
        "failed": number - count,
        "total_time": results.total_time,
        "count": count,
        "number": number,
        "concurrency": concurrency,
        "server": results.server,
    }

def print_errors(errors):
    if len(errors) == 0:
        return
    print('')
    print('-------- Errors --------')
    for error in errors:
        print(error)


def print_json(results, url, number, concurrency):
    """Prints a JSON representation of the results to stdout."""
    import json
    stats = calc_stats(results, url, number, concurrency)
    print(json.dumps(stats))


def onecall(method, url, results, **options):
    """Performs a single HTTP call and puts the result into the
       status_code_counter.

    RequestExceptions are caught and put into the errors set.
    """
    start = time.time()

    try:
        res = method(url, **options)
    except RequestException as exc:
        results.errors.append(exc)
    else:
        duration = time.time() - start
        results.all_res.append(duration)
        # results.status_code_counter[res.status_code].append(duration)


def run(url, num=1, duration=None, concurrency=1, headers=None):

    if headers is None:
        headers = {}

    if 'content-type' not in headers:
        headers['Content-Type'] = 'text/plain'

    method = requests.get
    options = {'headers': headers}

    pool = Pool(concurrency)
    start = time.time()
    jobs = None
    res = RunResults(num, url)

    try:
        if num is not None:
            jobs = [pool.spawn(onecall, method, url, res, **options) for i in range(num)]
            pool.join()
        else:
            with gevent.Timeout(duration, False):
                jobs = []
                while True:
                    jobs.append(pool.spawn(onecall, method, url, res, **options))
                pool.join()
    except KeyboardInterrupt:
        # In case of a keyboard interrupt, just return whatever already got
        # put into the result object.
        pass
    finally:
        res.total_time = time.time() - start

    return res


def resolve(url):
    parts = parse_url(url)

    if not parts.port and parts.scheme == 'https':
        port = 443
    elif not parts.port and parts.scheme == 'http':
        port = 80
    else:
        port = parts.port

    original = parts.host
    resolved = gethostbyname(parts.host)

    # Don't use a resolved hostname for SSL requests otherwise the
    # certificate will not match the IP address (resolved)
    host = resolved if parts.scheme != 'https' else parts.host
    netloc = '%s:%d' % (host, port) if port else host

    if port not in (443, 80):
        host += ':%d' % port
        original += ':%d' % port

    return (urlparse.urlunparse((parts.scheme, netloc, parts.path or '',
                                 '', parts.query or '',
                                 parts.fragment or '')),
            original, host)


def main():
    parser = argparse.ArgumentParser(
        description='Simple HTTP Load runner.')

    parser.add_argument('-c', '--concurrency', help='Concurrency',
                        type=int, default=1)

    group = parser.add_mutually_exclusive_group()

    group.add_argument('-n', '--requests', help='Number of requests',
                       type=int)

    group.add_argument('-d', '--duration', help='Duration in seconds',
                       type=int)

    parser.add_argument('url', help='URL to hit', nargs='?')
    args = parser.parse_args()

    if args.url is None:
        print('You need to provide an URL.')
        parser.print_usage()
        sys.exit(0)

    if args.requests is None and args.duration is None:
        args.requests = 1

    try:
        url, original, resolved = resolve(args.url)
    except gaierror as e:
        print_errors(("DNS resolution failed for %s (%s)" %
                      (args.url, str(e)),))
        sys.exit(1)

    headers = {}
    if original != resolved and 'Host' not in headers:
        headers['Host'] = original

    try:
        res = run(url, args.requests, args.duration, args.concurrency, headers=headers)
    except RequestException as e:
        print_errors((e, ))
        sys.exit(1)

    print_json(res, url, args.requests, args.concurrency)

    logger.info('Bye!')


if __name__ == '__main__':
    main()
