import argparse
import json
import logging
from asyncio import Queue, gather, run
from sys import stderr
from typing import Coroutine, List, Optional

from ownjoo_toolkit.logging.consts import LOG_FORMAT
from ownjoo_toolkit.parsing.consts import TimeFormats
from rick_and_morty_async.client import (
    get_data, list_characters, list_characters_paginated, list_episodes,
    list_episodes_paginated, list_locations, list_locations_paginated, list_results_paginated,
)
from rick_and_morty_async.parser import json_out


async def main():
    q = Queue(maxsize=100)
    client_coroutines: List[Coroutine] = [
        # get_data(domain=args.domain, proxies=proxies, q=q),
        # list_characters_paginated(domain=args.domain, proxies=proxies, q=q),
        # list_locations_paginated(domain=args.domain, proxies=proxies, q=q),
        # list_episodes_paginated(domain=args.domain, proxies=proxies, q=q),
        list_characters(url=args.domain, proxies=proxies, q=q),
        list_locations(url=args.domain, proxies=proxies, q=q),
        list_episodes(url=args.domain, proxies=proxies, q=q),
    ]
    parser_coroutines: List[Coroutine] = [
        json_out(q=q),
    ]
    await gather(
        *client_coroutines,
        *parser_coroutines,
        q.join(),  # for multiple queue consumer workers (which we don't have right now)
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
