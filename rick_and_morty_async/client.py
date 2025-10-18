import logging
from asyncio import sleep, Queue
from typing import AsyncGenerator, Optional

from httpx import AsyncClient, Client, Response
from ownjoo_utils import get_value
from ownjoo_utils.logging.decorators import timed_async_generator

logger = logging.getLogger(__name__)

C: Optional[Client] = None


@timed_async_generator(log_progress=False, log_level=logging.DEBUG, logger=logger)
async def list_results(
    url: str, additional_params: Optional[dict] = None
) -> AsyncGenerator[dict, None]:
    should_continue: bool = True
    params: dict = {
        'offset': 0,
        'limit': 1000,
    }
    if isinstance(additional_params, dict):
        params.update(additional_params)
    expected_total: int = 0
    count: int = 0
    retries: int = 3
    while should_continue and retries > 0:
        try:
            r: Response = await C.request(method='GET', url=url, params=params)
            r.raise_for_status()
            data_raw: dict = r.json()
            if not expected_total:
                expected_total = data_raw.get('count') or 0
                # logger.info(f'Expected count of {expected_total} for {url}')
            if not data_raw or True:
                should_continue = False
            count += len(data_raw)
            params['offset'] += 1000
            yield data_raw
            retries = 3
        except Exception as e:
            logger.error(f'ERROR {url}: {str(e)[:200]}.  Retries: {retries}')
            retries -= 1
            await sleep(5)


async def get_data(
    domain: str,
    proxies: Optional[dict] = None,
    q: Optional[Queue] = None,
) -> None:
    global C
    async with AsyncClient(follow_redirects=True) as C:
        if isinstance(proxies, dict):
            C.proxies = proxies

        C.headers.update(
            {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                # 'Authorization': f'THIS_IS_WRONG {api_key}',
            }
        )

        C.verify = False  # for convenience...  evaluate for yourself if this is acceptable.

        r = await anext(list_results(url=domain))
        async for character in list_results(url=get_value(src=r, path=['characters'], exp=str)):
            await q.put(character)

        async for location in list_results(url=get_value(src=r, path=['locations'], exp=str)):
            await q.put(location)

        async for episode in list_results(url=get_value(src=r, path=['episodes'], exp=str)):
            await q.put(episode)

        await q.put(None)
