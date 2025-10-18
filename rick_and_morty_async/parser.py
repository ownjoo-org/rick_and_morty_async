from asyncio import Queue
from json import dumps


async def parse(q: Queue):
    endl = ''
    print('[')
    while result := await q.get():
        print(f'{endl}{dumps(result, indent=4)}', sep='')
        endl = ',\n'
    print(']')
