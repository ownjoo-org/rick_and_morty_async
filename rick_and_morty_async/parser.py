from asyncio import Queue
from json import dumps


async def parse(q: Queue, subscriber_count: int = 1) -> None:
    should_continue: bool = True
    endl = ''
    print('[')
    while subscriber_count > 0:
        result = await q.get()
        if result is None:
            subscriber_count -= 1
        print(f'{endl}{dumps(result, indent=4)}', end='')
        endl = ',\n'
    print(']')
    q.task_done()
