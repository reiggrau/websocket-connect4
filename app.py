#!/usr/bin/env python

import asyncio

from websockets.asyncio.server import serve
from websockets.exceptions import ConnectionClosedOK


async def handler(websocket):
    async for message in websocket:
        print(message)

#    while True:
#        try:
#            message = await websocket.recv()
#        # ConnectionClosedOK is raised when the client closes the connection cleanly.
#        except ConnectionClosedOK:
#            break
#        print(message)

#    while True:
#        message = await websocket.recv()
#        print(message)


async def main():
    """  serve() takes three positional arguments:
    handler is a coroutine that manages a connection. When a client connects, websockets calls handler with the connection in argument. When handler terminates, websockets closes the connection.
    The second argument defines the network interfaces where the server can be reached. Here, the server listens on all interfaces, so that other devices on the same local network can connect.
    The third argument is the port on which the server listens. """
    async with serve(handler, "", 8001):
        await asyncio.get_running_loop().create_future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
