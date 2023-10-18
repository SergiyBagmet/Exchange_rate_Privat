from datetime import date
import platform
import typing as t
import sys

import asyncio
import aiohttp

from my_lib.my_date import DateDeltaDay

URL_PRIVATE_BODY = 'https://api.privatbank.ua/p24api/exchange_rates?json&date='

def get_urls(delta_d: int) -> list[str]:
    delta = DateDeltaDay(date.today(), delta_d, negative=True)
    return [URL_PRIVATE_BODY + date.strftime('%d.%m.%Y') for date in delta.get_min_max_date()]

class AsyncApiRequester:
    
    
    
    def __init__(self, url):
       self.url = url

    async def get_json(self):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.url) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(f"Error status: {response.status} for {self.url}")
            except aiohttp.ClientConnectorError as err:
                print(f'Connection error: {self.url}', str(err))
    
    
    
class AsyncPrivateParser(AsyncApiRequester):
    
    
    def __init__(self, url, currencys: tuple[t.LiteralString] | None=None):
        super().__init__(url)
        self.currencys = currencys if not None else ("EUR", "USD")

    async def a_parse(self):# TODO
        data: dict[str, str | int | list[dict[str, str | float]]] = await self.get_json()
        return {
                    data["date"]: {
                                    currency['currency']: {
                                                            'sale': currency['saleRate'],
                                                            'purchase': currency['purchaseRate']
                                                            } for currency in data["exchangeRate"] 
                                                            if currency["currency"] in (self.currencys)
                                    }
                }
  
        
async def main_privat():
    delta_d = int(sys.argv[1])
    urls = get_urls(delta_d)  
    return await asyncio.gather(*[AsyncPrivateParser(url, ("USD")).a_parse() for url in urls], return_exceptions=True) 
     
if __name__ == "__main__":
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    print(asyncio.run(main_privat()))
   