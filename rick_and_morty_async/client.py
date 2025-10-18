import logging
from asyncio import Queue
from typing import AsyncGenerator, Optional

from httpx import AsyncClient, HTTPError, HTTPStatusError, Response
from ownjoo_utils import get_value
from ownjoo_utils.logging.decorators import timed_async_generator
from retry_async import retry

from rick_and_morty_async.consts import PAGE_SIZE

logger = logging.getLogger(__name__)


@retry(exceptions=Exception, tries=3, delay=1, backoff=2, max_delay=5, logger=logger, is_async=True)
async def get_response(
        url: str,
        method: str = 'GET',
        params=None,
        json: Optional[dict] = None,
        data: Optional[dict] = None,
        proxies: Optional[dict] = None,
) -> Optional[dict]:
    async with AsyncClient(follow_redirects=True) as session:  # TODO: this will need to be a 1-time thing
        try:
            if isinstance(proxies, dict):
                session.proxies = proxies
            session.headers.update(
                {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                }
            )
            session.verify = False  # for convenience...  evaluate for yourself if this is acceptable.

            r: Response = await session.request(
                method=method or 'get',
                url=url,
                data=data,
                json=json,
                params=params,
                timeout=30,
            )
            r.raise_for_status()
            return r.json()
        except HTTPStatusError as exc_status:
            if exc_status.response.status_code == 404:
                return None
            else:
                logger.exception(
                    f'HTTP Error: {exc_status=}:\n'
                    f'{exc_status.response.status_code=}\n'
                    f'{exc_status.request.url=}\n'
                )
                raise
        except HTTPError as exc_http:
            logger.exception(
                f'HTTP Error: {exc_http=}:\n'
                f'{exc_http.request.url=}\n'
            )
            raise
        except Exception as exc:
            logger.exception(f'UNEXPECTED ERROR: {exc=}')
            raise


@timed_async_generator(log_progress=False, log_level=logging.DEBUG, logger=logger)
async def list_results(
    url: str, additional_params: Optional[dict] = None,
    proxies: Optional[dict] = None,
) -> AsyncGenerator[dict, None]:
    should_continue: bool = True
    params: dict = {
        'page': 0,
        'count': PAGE_SIZE,
    }
    if isinstance(additional_params, dict):
        params.update(additional_params)
    while should_continue:
        data_raw: dict = await get_response(method='get', url=url, params=params, proxies=proxies)
        results: list[dict] = get_value(src=data_raw, path=['results'], exp=list, default=[])
        if not results or len(results) < PAGE_SIZE:
            should_continue = False
        params['page'] += 1
        for result in results:
            yield result


async def list_characters(domain: str, proxies: Optional[dict] = None, q: Optional[Queue] = None) -> None:
    r: dict = await get_response(url=domain, proxies=proxies)
    async for character in list_results(url=get_value(src=r, path=['characters'], exp=str, default=[]), proxies=proxies):
        await q.put(character)
    await q.put(None)  # counting these in the parser so we know when parsing should stop pulling from queue


async def list_locations(domain: str, proxies: Optional[dict] = None, q: Optional[Queue] = None) -> None:
    r: dict = await get_response(url=domain, proxies=proxies)
    async for location in list_results(url=get_value(src=r, path=['locations'], exp=str, default=[]), proxies=proxies):
        await q.put(location)
    await q.put(None)  # counting these in the parser so we know when parsing should stop pulling from queue


async def list_episodes(domain: str, proxies: Optional[dict] = None, q: Optional[Queue] = None) -> None:
    r: dict = await get_response(url=domain, proxies=proxies)
    async for episode in list_results(url=get_value(src=r, path=['episodes'], exp=str), proxies=proxies):
        await q.put(episode)
    await q.put(None)  # counting these in the parser so we know when parsing should stop pulling from queue


async def get_data(
    domain: str,
    proxies: Optional[dict] = None,
    q: Optional[Queue] = None,
) -> None:
    r = await get_response(url=domain, proxies=proxies)
    async for character in list_results(url=get_value(src=r, path=['characters'], exp=str), proxies=proxies):
        await q.put(character)

    async for location in list_results(url=get_value(src=r, path=['locations'], exp=str), proxies=proxies):
        await q.put(location)

    async for episode in list_results(url=get_value(src=r, path=['episodes'], exp=str), proxies=proxies):
        await q.put(episode)

    await q.put(None)
