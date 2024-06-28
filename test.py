import platform
import asyncio
from asynparser import parse

wallet = ""

async def test():
    res = await parse(wallet)
    if res is False:
        print("Error")
    else:
        a = float(res)
        print(a)

if __name__ == '__main__':
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(test())