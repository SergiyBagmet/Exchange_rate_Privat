import asyncio
import logging
import websockets
import names
from websockets.server import WebSocketServerProtocol, serve
from websockets.exceptions import ConnectionClosedOK
from jinja2 import Environment, FileSystemLoader

from ex_privat import get_currency_from_privat
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
        ##TODO
        async for message in ws:
            if message.lower().strip().startswith("exchange"):
                exchange_msg = await self._exchange_msg(message.split()[1:]) 
                await self.send_to_client(ws, f'html:{message}{exchange_msg}') ##TODO
            else:        
                await self.send_to_clients(f"{ws.name}: {message}")
                
    async def _exchange_msg(self, input_lst: list[str]):
        delta_d, num_str, currencies = None, None, None
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
                exchange_msg = ":  Invalid message format to exchange"   
        try:
            if currencies == ["ALL"] : currencies = False
            exchange_rates = await get_currency_from_privat(delta_d, currencies)
            template = ENV_J.get_template("exchanges.html")
            exchange_msg = template.render(data=exchange_rates)
            pass # TODO grafik
        except ValueError as err:
            exchange_msg = str(err)
        finally:
            return exchange_msg

            

async def main():
    my_server = MyServer()
    async with serve(my_server.ws_handler, 'localhost', 8080):
        await asyncio.Future()  # run forever

if __name__ == '__main__':
    asyncio.run(main())