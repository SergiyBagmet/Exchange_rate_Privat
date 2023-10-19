from datetime import date
import platform
import typing as t
import sys

import asyncio
import aiohttp

from my_lib.my_date import DateDeltaDay

URL_PRIVATE_BODY = 'https://api.privatbank.ua/p24api/exchange_rates?date='

def get_urls(delta_d: int) -> list[str]:
    delta = DateDeltaDay(date.today(), delta_d, negative=True)
    return [f"{URL_PRIVATE_BODY}{date.strftime('%d.%m.%Y')}" for date in delta.get_min_max_date()]

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
    
    
    
class ApiPrivateParser:
    
    
    def __init__(self, api_data: dict[str, str | int | list[dict[str, str | float]]], ) -> None:
        
        self.date = api_data.get("date")
        self.filter_data = self._all_rate_filter(api_data.get("exchangeRate"))
        
    def _all_rate_filter(self, all_rate: list[dict[str, str | float]]):
        return {
            rates.get("currency") : 
                {
                    k:v for k,v in rates.items() if k not in ("baseCurrency", "currency")
                }
                                                            for rates in all_rate if rates.get("currency") !="UAH"
            }
    
    def base_parse(self, currencys: t.Iterable[str]=("USD", "EUR")):
        return {
                self.date : 
                        {
                            currency: 
                                {
                                    "sale": rates.get("saleRate", rates.get("saleRateNB")),
                                    "purchase": rates.get("purchaseRate", rates.get("purchaseRateNB"))
                                }
                        for currency, rates in self.filter_data.items() if currency in currencys
                        }
                }
       
async def fetch_and_parse_data(url):
    data_json = await AsyncApiRequester(url).get_json()
    return ApiPrivateParser(data_json).base_parse()
        
async def main_privat():
    delta_d = int(sys.argv[1])
    urls = get_urls(delta_d)  
    return await asyncio.gather(*[fetch_and_parse_data(url) for url in urls], return_exceptions=True) 



     
if __name__ == "__main__":
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    print(asyncio.run(main_privat()))
   