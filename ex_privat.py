from datetime import date
import platform
import typing as t
import sys

import asyncio
import aiohttp

from my_lib.my_date import DateDeltaDay

URL_PRIVATE_BODY = 'https://api.privatbank.ua/p24api/exchange_rates?json&date='

def get_urls(delta_d: int) -> list[str]:
    delta_5 = DateDeltaDay(date.today(), delta_d, negative=True)
    return [URL_PRIVATE_BODY + date.strftime('%d.%m.%Y') for date in delta_5.get_min_max_date()]

class AsyncApiRequester:
    
    def __init__(self, url):
       self.url = url

    async def get_json(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.url) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(f"Error status: {response.status} for {self.url}")
        except aiohttp.ClientConnectorError as err:
            print(f'Connection error: {self.url}', str(err))
    


async def a_parse_data_privat(
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


async def fetch_gen(urls):
    for url in urls:
        requester = AsyncApiRequester(url)
        yield await requester.get_json()
   

async def main_privat(currencys):
    delta_d = int(sys.argv[1])
    urls = get_urls(delta_d)
    return await asyncio.gather(*[a_parse_data_privat(data_json, currencys) async for data_json in fetch_gen(urls)], return_exceptions=True) 
     
if __name__ == "__main__":
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    print(asyncio.run(main_privat(("PLN"))))
   