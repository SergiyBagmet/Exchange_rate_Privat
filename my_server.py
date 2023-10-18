import asyncio
import logging
import websockets
import names
from websockets.server import WebSocketServerProtocol, serve
from websockets.exceptions import ConnectionClosedOK

from ex_privat import get_urls, AsyncPrivateParser
logging.basicConfig(level=logging.INFO)


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
                currencys = None
                match message.split():
                    case [_] :
                        delta_d = 0
                    case [_, num_str] if num_str.isnumeric():
                        delta_d = int(num_str)
                    case [_, num_str, *currencys] if num_str.isnumeric():
                        delta_d = int(num_str)
                        currencys = tuple(map(str.upper, currencys))
                    case _:
                        pass    
                try:
                    #TODO
                    results = await asyncio.gather(*[AsyncPrivateParser(url, (currencys)).a_parse() for url in get_urls(delta_d)], return_exceptions=True) 
                    exchange_msg = '\n'.join(str(res) for res in results)
                except ValueError as err:
                    exchange_msg = str(err)
                finally:
                    await self.send_to_client(ws, exchange_msg) ##TODO
            else:        
                await self.send_to_clients(f"{ws.name}: {message}")


async def main():
    my_server = MyServer()
    async with serve(my_server.ws_handler, 'localhost', 8080):
        await asyncio.Future()  # run forever

if __name__ == '__main__':
    asyncio.run(main())