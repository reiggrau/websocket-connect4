#!/usr/bin/env python

import asyncio
import itertools
import json

from websockets.asyncio.server import serve

from connect4 import Connect4, PLAYER1, PLAYER2

# import logging

# logging.basicConfig(format="%(message)s", level=logging.DEBUG)


async def handler(websocket):
    # Initialize a Connect Four game.
    game = Connect4()

    # Players take alternate turns, using the same browser.
    turns = itertools.cycle([PLAYER1, PLAYER2])  # cycle() returns an iterator.
    player = next(turns)  # next() returns the next item from the iterator.

    async for message in websocket:
        print(message)

        # Parse the message as JSON.
        event = json.loads(message)

        # Handle the event.
        # assert raises an AssertionError if the condition is false.
        assert event["type"] == "play"

        column = event["column"]

        try:
            # Play the move.
            row = game.play(player, column)
        except ValueError as exc:
            # Send an "error" event if the move was illegal.
            event = {
                "type": "error",
                "message": str(exc),
            }
            await websocket.send(json.dumps(event))
            continue

        # Send a "play" event to update the UI.
        event = {
            "type": "play",
            "player": player,
            "column": column,
            "row": row,
        }
        await websocket.send(json.dumps(event))

        # If move is winning, send a "win" event.
        if game.winner is not None:
            event = {
                "type": "win",
                "player": game.winner,
            }
            await websocket.send(json.dumps(event))

        # Switch players.
        player = next(turns)

        #    for player, column, row in [
        #        (PLAYER1, 3, 0),
        #        (PLAYER2, 3, 1),
        #        (PLAYER1, 4, 0),
        #        (PLAYER2, 4, 1),
        #        (PLAYER1, 2, 0),
        #        (PLAYER2, 1, 0),
        #        (PLAYER1, 5, 0),
        #    ]:
        #        event = {
        #            "type": "play",
        #            "player": player,
        #            "column": column,
        #            "row": row,
        #        }
        #        await websocket.send(json.dumps(event))
        #        await asyncio.sleep(0.5)
        #    event = {
        #        "type": "win",
        #        "player": PLAYER1,
        #    }
        #    await websocket.send(json.dumps(event))

        #    async for message in websocket:
        #        print(message)

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
