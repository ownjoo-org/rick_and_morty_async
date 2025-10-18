from asyncio import Queue
from json import dumps


async def json_out(q: Queue, subscriber_count: int = 1) -> None:
    endl = ''  # start with nothing prepended
    print('[')
    while subscriber_count > 0:
        result = await q.get()
        if result is None:
            subscriber_count -= 1
        else:
            print(f'{endl}{dumps(result, indent=4)}', end='')
        endl = ',\n'  # prepend to this line the previous line's endl (no trailing ',' for JSON correctness)
    print('\n]')
    q.task_done()  # TODO: this is for Queue.join().  How can I use that?
