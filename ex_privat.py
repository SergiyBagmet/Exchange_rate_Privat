from datetime import date
import platform
import typing as t
import sys

import asyncio
import aiohttp

from my_lib.my_date import DateDeltaDay

URL_PRIVATE_BODY = 'https://api.privatbank.ua/p24api/exchange_rates?json&date='


class AsyncApiRequester:
    
    def __init__(self):
        self.session = aiohttp.ClientSession()

    async def get_json(self, url):
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    data_json = await response.json()
                    return data_json
                else:
                    print(f"Error status: {response.status} for {url}")
        except aiohttp.ClientConnectorError as err:
            print(f'Connection error: {url}', str(err))
    
    async def close_session(self):
        if self.session:
            await self.session.close()
    
    def __del__(self):
        if self.session and not self.session.closed:
            self.session.close()


async def a_parse_api_privat(
    data: dict[str, str | int | list[dict[str, str | float]]], 
    currencys: tuple[t.LiteralString]=("EUR", "USD")
    ):# TODO
    return {
                data["date"]: {
                                currency['currency']: {
                                                        'sale': currency['saleRate'],
                                                        'purchase': currency['purchaseRate']
                                                        } for currency in data["exchangeRate"] 
                                                        if currency["currency"] in (currencys)
                                }
            }

async def a_fasade(url, a_requester: AsyncApiRequester):
        data = await a_requester.get_json(url)
        return await a_parse_api_privat(data)

async def main(urls):
    a_requester = AsyncApiRequester()
    results = await asyncio.gather(*[a_fasade(url, a_requester) for url in urls], return_exceptions=True) 
    await a_requester.close_session()
    return results

def get_urls(delta_d: int) -> list[str]:
    delta_5 = DateDeltaDay(date.today(), delta_d, negative=True)
    return [URL_PRIVATE_BODY + date.strftime('%d.%m.%Y') for date in delta_5.get_min_max_date()]
       
if __name__ == "__main__":
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    delta_d = int(sys.argv[1])
    urls = get_urls(delta_d)  
    print(asyncio.run(main(urls)))
   