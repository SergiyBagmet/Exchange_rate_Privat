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

class ExchangeError(Exception):
    pass

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
    
    
class PrivateParser:
    
    
    def __init__(self, currencys: t.Iterable[str] | None) -> None:
        self.currencys = currencys
        self.filtred_data = None
        self.parse_data = None
        
        
    def __filter(self, all_rate: list[dict[str, str | float]]):
        return {
            rates.get("currency") : 
                {
                    k:v for k,v in rates.items() if k not in ("baseCurrency", "currency")
                }
                                                            for rates in all_rate if rates.get("currency") !="UAH"
            }
    
    def parse(self, api_data: dict[str, str | int | list[dict[str, str | float]]] ):
        self.filtred_data = self.__filter(api_data.get("exchangeRate"))
        
        if self.currencys is None:
            self.currencys = ("USD", "EUR")
        elif self.currencys is False:
            self.currencys = list(self.filtred_data.keys())
            
            
             
        self.parse_data = {api_data.get("date"): {
                            currency: {
                                "sale PB": rates.get("saleRate", "--empty--"),
                                "purchase PB": rates.get("purchaseRate", "--empty--"),
                                "sale NB": rates.get("saleRateNB"),
                                "purchase NB": rates.get("purchaseRateNB"),
                            }
                            for currency, rates in self.filtred_data.items()
                            if currency in self.currencys
                        }}
        return self.parse_data
    
    
       
async def fetch_and_parse(requester: AsyncApiRequester, parser: PrivateParser) -> dict:
    data_json = await requester.get_json()
    parsed_data = parser.parse(data_json)
    return parsed_data
        
async def get_currency_from_privat(delta_d: int, currencys: t.Iterable[str]) -> list[dict]:
   
    parser = PrivateParser(currencys)
    futures = [fetch_and_parse(AsyncApiRequester(url), parser) for url in get_urls(delta_d)]
    return await asyncio.gather(*futures, return_exceptions=True) 
    
    
  
if __name__ == "__main__":
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    delta_d = int(sys.argv[1])
    print(asyncio.run(get_currency_from_privat(delta_d, None)))
    
   