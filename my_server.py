import asyncio
import logging
import names
from websockets.server import WebSocketServerProtocol, serve
from websockets.exceptions import ConnectionClosedOK
from jinja2 import Environment, FileSystemLoader

from ex_privat import get_currency_from_privat, ExchangeError

logging.basicConfig(level=logging.INFO)
ENV_J = Environment(loader=FileSystemLoader('templates'))

class MyServer:
    clients = set()

    async def register(self, ws: WebSocketServerProtocol):
        ws.name = names.get_full_name()
        self.clients.add(ws)
        logging.info(f'{ws.remote_address} connects')

    async def unregister(self, ws: WebSocketServerProtocol):
        self.clients.remove(ws)
        logging.info(f'{ws.remote_address} disconnects')

    async def send_to_clients(self, message: str):
        if self.clients:
            [await client.send(message) for client in self.clients]
    
    async def send_to_client(self, ws: WebSocketServerProtocol,  message: str):
        if ws in self.clients:
            await ws.send(message)      

    async def ws_handler(self, ws: WebSocketServerProtocol):
        await self.register(ws)
        try:
            await self.distrubute(ws)
        except ConnectionClosedOK:
            pass
        finally:
            await self.unregister(ws)

    async def distrubute(self, ws: WebSocketServerProtocol):
        async for message in ws:
            if message.lower().strip().startswith("exchange"):
            
                try:    
                    exchange_rates = await self._exchange_rates(message.split()[1:])
                    
                    
                    if len(exchange_rates) <= 1:
                        exc_to_render = exchange_rates 
                    else:     
                        exc_to_render = [exchange_rates[0], exchange_rates[-1]]
                    
                    exchange_msg = await self.exchange_render(exc_to_render)
                    
                    message = f'html:{message}{exchange_msg}' 
                except ExchangeError as err:
                    message = f'{message} ERROR : {err}'
                finally:      
                    await self.send_to_client(ws, message) 
            else:        
                await self.send_to_clients(f"{ws.name}: {message}")
                
    async def _exchange_rates(self, input_lst: list[str]):
        delta_d, currencies = None, None
        match input_lst:
            case [] :
                delta_d = 0
            case [num_str] if num_str.isnumeric():
                delta_d = int(num_str)
            case [*input_curr] if all(map(str.isalpha, input_curr)):
                delta_d, currencies = 0, input_curr
            case [num_str, *input_curr] if num_str.isnumeric() and all(map(str.isalpha, input_curr)):
                    delta_d, currencies = int(num_str), input_curr
            case _:
                raise ExchangeError("Invalid message format to exchange")   
        if currencies == ["ALL"] : 
            currencies = False
        return await get_currency_from_privat(delta_d, currencies)
       

    async def exchange_render(self, exh_data: list[dict]):
        template = ENV_J.get_template("exchanges.html")
        return template.render(data=exh_data)  

async def main():
    my_server = MyServer()
    async with serve(my_server.ws_handler, 'localhost', 8080):
        await asyncio.Future()  # run forever

if __name__ == '__main__':
    asyncio.run(main())