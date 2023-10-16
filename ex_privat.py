from datetime import date
import platform
import typing as t

import asyncio
import aiohttp

from my_lib.my_date import DateHandler

URL_PRIVATE_BODY = 'https://api.privatbank.ua/p24api/exchange_rates?json&date='

class AsyncApiRequester:
    
    
    def __init__(self, url) -> None:
        self.url = url
        
    async def get_json(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as response:
                try:   
                    if response.status == 200:
                        data_json = await response.json()
                        return data_json
                    else:
                            print(f"Error status: {response.status} for {self.url}")
                except aiohttp.ClientConnectorError as err:
                    print(f'Connection error: {self.url}', str(err))



async def main():
    today_handler = DateHandler(date.today())
    delta_handler = today_handler.get_delta_days(-5)
    url_today = URL_PRIVATE_BODY + today_handler.formated_date()
    url_delta = URL_PRIVATE_BODY + delta_handler.formated_date()

    today_requester = AsyncApiRequester(url_today)
    delta_requester = AsyncApiRequester(url_delta)

    result = await asyncio.gather(today_requester.get_json(), delta_requester.get_json())
    return result

if __name__ == "__main__":
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    print(asyncio.run(main()))
   