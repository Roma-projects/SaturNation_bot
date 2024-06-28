import platform
import asyncio
import aiohttp
from bs4 import BeautifulSoup as BS
from fake_useragent import UserAgent

async def parse(wallet):
    url = "https://tonviewer.com/" + wallet + "/jetton/EQDT4L_7Wnd5szJoupdbgVKW4nrYAyhnCNF_a2v_9utx97Yh"
    headers = {"User-Agent": UserAgent().random}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            r = await response.text()
            soup = BS(r, "html.parser")
            item = soup.find("div", {'class': "bdtytpm bd27hoh"})
            if item is None or wallet == "":
                return False
            else:
                item = item.text.strip()[:-7:]
                result = float(item.replace(",", ""))
                return result



async def course_usdt():
    url = "https://www.geckoterminal.com/ru/ton/pools/EQBw3mMG8EDloqDN4ozgmDW9qZkOxJTaMuz7Dimxqpl-I_UR"
    headers = {"User-Agent": UserAgent().random}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            r = await response.text()
            soup = BS(r, "html.parser")
            item = soup.find("span", {'class': "headline-4 leading-none"})
            item = item.text.strip()[:-2]
            result = float((item.replace(",", ".")))
            return result




if __name__ == '__main__':
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(course_usdt())


