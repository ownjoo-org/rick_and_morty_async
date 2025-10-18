import argparse
import json
import logging
from asyncio import run, gather, Queue
from sys import stderr
from typing import Optional

from ownjoo_utils.logging.consts import LOG_FORMAT
from ownjoo_utils.parsing.consts import TimeFormats

from rick_and_morty_async.client import get_data, get_characters, get_locations, get_episodes
from rick_and_morty_async.parser import parse


async def main():
    q = Queue(maxsize=10)
    await gather(
        # get_data(domain=args.domain, proxies=proxies, q=q),
        get_characters(domain=args.domain, proxies=proxies, q=q),
        get_locations(domain=args.domain, proxies=proxies, q=q),
        get_episodes(domain=args.domain, proxies=proxies, q=q),
        parse(q=q),
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--domain',
        default='example.com',
        type=str,
        required=True,
        help='The FQDN for your API (not full URL)',
    )
    parser.add_argument(
        '--proxies',
        type=str,
        required=False,
        help="JSON structure specifying 'http' and 'https' proxy URLs",
    )
    parser.add_argument(
        '--log-level',
        type=int,
        required=False,
        help="0 (NOTSET) - 50 (CRITICAL)",
        default=logging.INFO,
        dest='log_level',
    )

    args = parser.parse_args()

    logging.basicConfig(
        format=LOG_FORMAT,
        level=args.log_level,
        datefmt=TimeFormats.date_and_time.value,
        stream=stderr,
    )
    logger = logging.getLogger(__name__)

    proxies: Optional[dict] = None
    if proxies:
        try:
            proxies: dict = json.loads(args.proxies)
        except Exception as exc_json:
            logger.warning(f'failure parsing proxies: {exc_json}: proxies provided: {proxies}')

    run(main())
