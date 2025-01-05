# websocket-connect4

https://websockets.readthedocs.io/en/stable/intro/tutorial1.html#connect4.PLAYER1

```bash
py -3 -m venv .venv
```

# 2 - Activate the environment

```bash
source .venv/Scripts/activate
```

# 3 - Install websockets

```bash
pip install websockets
```

# 4 - Run the websocket server

```bash
py app.py
```

# 5 - Start the http server

```bash
py -m http.server
```

# Part 1 - Send & receive

## Prerequisites

This tutorial assumes basic knowledge of Python and JavaScript.

If you’re comfortable with virtual environments, you can use one for this tutorial. Else, don’t worry: websockets doesn’t have any dependencies; it shouldn’t create trouble in the default environment.

If you haven’t installed websockets yet, do it now:

```bash
pip install websockets
```

Confirm that websockets is installed:

```bash
$ py -m websockets --version
```

## Download the starter kit

Create a directory and download these three files: connect4.js, connect4.css, and connect4.py.

## Bootstrap the web UI

Create an index.html file next to connect4.js and connect4.css with this content:

```html
<!-- /index.html -->
<!DOCTYPE html>
<html lang="en">
  <head>
    <title>Connect Four</title>
  </head>
  <body>
    <div class="board"></div>
    <script src="main.js" type="module"></script>
  </body>
</html>
```

This HTML page contains an empty <div> element where you will draw the Connect Four board. It loads a main.js script where you will write all your JavaScript code.

Create a main.js file next to index.html. In this script, when the page loads, draw the board:

```js
// /main.js
import { createBoard, playMove } from "./connect4.js";

window.addEventListener("DOMContentLoaded", () => {
  // Initialize the UI.
  const board = document.querySelector(".board");
  createBoard(board);
});
```

Open a shell, navigate to the directory containing these files, and start an HTTP server:

```bash
py -m http.server
```

Open http://localhost:8000/ in a web browser. The page displays an empty board with seven columns and six rows. You will play moves in this board later.

## Bootstrap the server

Create an app.py file next to connect4.py with this content:

```python
# /app.py

#!/usr/bin/env python

import asyncio

from websockets.asyncio.server import serve


async def handler(websocket):
    while True:
        message = await websocket.recv()
        print(message)


async def main():
    async with serve(handler, "", 8001):
        await asyncio.get_running_loop().create_future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
```

The entry point of this program is asyncio.run(main()). It creates an asyncio event loop, runs the main() coroutine, and shuts down the loop.

The main() coroutine calls serve() to start a websockets server. serve() takes three positional arguments:

1. handler is a coroutine that manages a connection. When a client connects, websockets calls handler with the connection in argument. When handler terminates, websockets closes the connection.

2. The second argument defines the network interfaces where the server can be reached. Here, the server listens on all interfaces, so that other devices on the same local network can connect.

3. The third argument is the port on which the server listens.

Invoking serve() as an asynchronous context manager, in an async with block, ensures that the server shuts down properly when terminating the program.

For each connection, the handler() coroutine runs an infinite loop that receives messages from the browser and prints them.

Open a shell, navigate to the directory containing app.py, and start the server:

```bash
py app.py
```

This doesn’t display anything. Hopefully the WebSocket server is running. Let’s make sure that it works. You cannot test the WebSocket server with a web browser like you tested the HTTP server. However, you can test it with websockets’ interactive client.

Open another shell and run this command:

```bash
py -m websockets ws://localhost:8001/
```

You get a prompt. Type a message and press “Enter”. Switch to the shell where the server is running and check that the server received the message. Good!

Exit the interactive client with Ctrl-C or Ctrl-D.

Now, if you look at the console where you started the server, you can see the stack trace of an exception:

```bash
connection handler failed
Traceback (most recent call last):
  ...
  File "app.py", line 22, in handler
    message = await websocket.recv()
  ...
websockets.exceptions.ConnectionClosedOK: received 1000 (OK); then sent 1000 (OK)
```

Indeed, the server was waiting for the next message with recv() when the client disconnected. When this happens, websockets raises a ConnectionClosedOK exception to let you know that you won’t receive another message on this connection.

This exception creates noise in the server logs, making it more difficult to spot real errors when you add functionality to the server. Catch it in the handler() coroutine:

```python
from websockets.exceptions import ConnectionClosedOK

async def handler(websocket):
    while True:
        try:
            message = await websocket.recv()
        except ConnectionClosedOK:
            break
        print(message)
```

Stop the server with Ctrl-C and start it again:

```bash
py app.py
```

```
NOTE: You must restart the WebSocket server when you make changes
```

Try connecting and disconnecting the interactive client again. The ConnectionClosedOK exception doesn’t appear anymore.

This pattern is so common that websockets provides a shortcut for iterating over messages received on the connection until the client disconnects:

```python
async def handler(websocket):
    async for message in websocket:
        print(message)
```

Restart the server and check with the interactive client that its behavior didn’t change.

At this point, you bootstrapped a web application and a WebSocket server. Let’s connect them.

## Transmit from browser to server

In JavaScript, you open a WebSocket connection as follows:

```js
const websocket = new WebSocket("ws://localhost:8001/");
```

Before you exchange messages with the server, you need to decide their format. There is no universal convention for this.

Let’s use JSON objects with a type key identifying the type of the event and the rest of the object containing properties of the event.

Here’s an event describing a move in the middle slot of the board:

```js
const event = { type: "play", column: 3 };
```

Here’s how to serialize this event to JSON and send it to the server:

```js
websocket.send(JSON.stringify(event));
```

Now you have all the building blocks to send moves to the server.

Add this function to main.js:

```js
// /main.js
function sendMoves(board, websocket) {
  // When clicking a column, send a "play" event for a move in that column.
  board.addEventListener("click", ({ target }) => {
    const column = target.dataset.column;
    // Ignore clicks outside a column.
    if (column === undefined) {
      return;
    }
    const event = {
      type: "play",
      column: parseInt(column, 10),
    };
    websocket.send(JSON.stringify(event));
  });
}
```

sendMoves() registers a listener for click events on the board. The listener figures out which column was clicked, builds a event of type "play", serializes it, and sends it to the server.

Modify the initialization to open the WebSocket connection and call the sendMoves() function:

```js
window.addEventListener("DOMContentLoaded", () => {
  // Initialize the UI.
  const board = document.querySelector(".board");
  createBoard(board);
  // Open the WebSocket connection and register event handlers.
  const websocket = new WebSocket("ws://localhost:8001/");
  sendMoves(board, websocket);
});
```

Check that the HTTP server and the WebSocket server are still running. If you stopped them, here are the commands to start them again:

```bash
# Terminal 1
py -m http.server
```

```bash
# Terminal 2
py app.py
```

Refresh http://localhost:8000/ in your web browser. Click various columns in the board. The server receives messages with the expected column number.

There isn’t any feedback in the board because you haven’t implemented that yet. Let’s do it.

## Transmit from server to browser

In JavaScript, you receive WebSocket messages by listening to message events. Here’s how to receive a message from the server and deserialize it from JSON:

```js
websocket.addEventListener("message", ({ data }) => {
  const event = JSON.parse(data);
  // do something with event
});
```

You’re going to need three types of messages from the server to the browser:

```js
{type: "play", player: "red", column: 3, row: 0}
{type: "win", player: "red"}
{type: "error", message: "This slot is full."}
```

The JavaScript code receiving these messages will dispatch events depending on their type and take appropriate action. For example, it will react to an event of type "play" by displaying the move on the board with the playMove() function.

Add this function to main.js:

```js
function showMessage(message) {
  window.setTimeout(() => window.alert(message), 50);
}

function receiveMoves(board, websocket) {
  websocket.addEventListener("message", ({ data }) => {
    const event = JSON.parse(data);
    switch (event.type) {
      case "play":
        // Update the UI with the move.
        playMove(board, event.player, event.column, event.row);
        break;
      case "win":
        showMessage(`Player ${event.player} wins!`);
        // No further messages are expected; close the WebSocket connection.
        websocket.close(1000);
        break;
      case "error":
        showMessage(event.message);
        break;
      default:
        throw new Error(`Unsupported event type: ${event.type}.`);
    }
  });
}
```

```
NOTE: Why does showMessage use window.setTimeout?
When playMove() modifies the state of the board, the browser renders changes asynchronously. Conversely, window.alert() runs synchronously and blocks rendering while the alert is visible.

If you called window.alert() immediately after playMove(), the browser could display the alert before rendering the move. You could get a “Player red wins!” alert without seeing red’s last move.

We’re using window.alert() for simplicity in this tutorial. A real application would display these messages in the user interface instead. It wouldn’t be vulnerable to this problem.
```

Modify the initialization to call the receiveMoves() function:

```js
window.addEventListener("DOMContentLoaded", () => {
  // Initialize the UI.
  const board = document.querySelector(".board");
  createBoard(board);
  // Open the WebSocket connection and register event handlers.
  const websocket = new WebSocket("ws://localhost:8001/");
  receiveMoves(board, websocket);
  sendMoves(board, websocket);
});
```

At this point, the user interface should receive events properly. Let’s test it by modifying the server to send some events.

Sending an event from Python is quite similar to JavaScript:

```python
event = {"type": "play", "player": "red", "column": 3, "row": 0}
await websocket.send(json.dumps(event))
```

Don’t forget to serialize the event with json.dumps(). Else, websockets raises TypeError: data is a dict-like object.

Modify the handler() coroutine in app.py as follows:

```python
import json

from connect4 import PLAYER1, PLAYER2

async def handler(websocket):
    for player, column, row in [
        (PLAYER1, 3, 0),
        (PLAYER2, 3, 1),
        (PLAYER1, 4, 0),
        (PLAYER2, 4, 1),
        (PLAYER1, 2, 0),
        (PLAYER2, 1, 0),
        (PLAYER1, 5, 0),
    ]:
        event = {
            "type": "play",
            "player": player,
            "column": column,
            "row": row,
        }
        await websocket.send(json.dumps(event))
        await asyncio.sleep(0.5)
    event = {
        "type": "win",
        "player": PLAYER1,
    }
    await websocket.send(json.dumps(event))
```

Restart the WebSocket server and refresh http://localhost:8000/ in your web browser. Seven moves appear at 0.5 second intervals. Then an alert announces the winner.

Good! Now you know how to communicate both ways.

Once you plug the game engine to process moves, you will have a fully functional game.

## Add the game logic

In the handler() coroutine, you’re going to initialize a game:

```python
# /app.py
from connect4 import Connect4

async def handler(websocket):
    # Initialize a Connect Four game.
    game = Connect4()

    ...
```

Then, you’re going to iterate over incoming messages and take these steps:

1. parse an event of type "play", the only type of event that the user interface sends;

2. play the move in the board with the play() method, alternating between the two players;

3. if play() raises ValueError because the move is illegal, send an event of type "error";

4. else, send an event of type "play" to tell the user interface where the checker lands;

5. if the move won the game, send an event of type "win".

Try to implement this by yourself!

Keep in mind that you must restart the WebSocket server and reload the page in the browser when you make changes.

When it works, you can play the game from a single browser, with players taking alternate turns.

NOTE: Enable debug logs to see all messages sent and received. Here’s how to enable debug logs:

```python
import logging

logging.basicConfig(format="%(message)s", level=logging.DEBUG)
```

# Part 2 - Route & broadcast

In the first part of the tutorial, you opened a WebSocket connection from a browser to a server and exchanged events to play moves. The state of the game was stored in an instance of the Connect4 class, referenced as a local variable in the connection handler coroutine.

Now you want to open two WebSocket connections from two separate browsers, one for each player, to the same server in order to play the same game. This requires moving the state of the game to a place where both connections can access it.

## Share game state

As long as you’re running a single server process, you can share state by storing it in a global variable.

```
NOTE: What if you need to scale to multiple server processes?
In that case, you must design a way for the process that handles a given connection to be aware of relevant events for that client. This is often achieved with a publish / subscribe mechanism.
```

How can you make two connection handlers agree on which game they’re playing? When the first player starts a game, you give it an identifier. Then, you communicate the identifier to the second player. When the second player joins the game, you look it up with the identifier.

In addition to the game itself, you need to keep track of the WebSocket connections of the two players. Since both players receive the same events, you don’t need to treat the two connections differently; you can store both in the same set.

Let’s sketch this in code.

A module-level dict enables lookups by identifier:

```python
JOIN = {}
```

When the first player starts the game, initialize and store it:

```python
import secrets

async def handler(websocket):
    ...

    # Initialize a Connect Four game, the set of WebSocket connections
    # receiving moves from this game, and secret access token.
    game = Connect4()
    connected = {websocket}

    join_key = secrets.token_urlsafe(12)
    JOIN[join_key] = game, connected

    try:

        ...

    finally:
        del JOIN[join_key]
```

When the second player joins the game, look it up:

```python
async def handler(websocket):
    ...

    join_key = ...

    # Find the Connect Four game.
    game, connected = JOIN[join_key]

    # Register to receive moves from this game.
    connected.add(websocket)
    try:

        ...

    finally:
        connected.remove(websocket)
```

Notice how we’re carefully cleaning up global state with try: ... finally: ... blocks. Else, we could leave references to games or connections in global state, which would cause a memory leak.

In both connection handlers, you have a game pointing to the same Connect4 instance, so you can interact with the game, and a connected set of connections, so you can send game events to both players as follows:

```python
async def handler(websocket):

    ...

    for connection in connected:
        await connection.send(json.dumps(event))

    ...
```

Perhaps you spotted a major piece missing from the puzzle. How does the second player obtain join_key? Let’s design new events to carry this information.

To start a game, the first player sends an "init" event:

```js
{
  type: "init";
}
```

The connection handler for the first player creates a game as shown above and responds with:

```js
{type: "init", join: "<join_key>"}
```

With this information, the user interface of the first player can create a link to http://localhost:8000/?join=<join_key>. For the sake of simplicity, we will assume that the first player shares this link with the second player outside of the application, for example via an instant messaging service.

To join the game, the second player sends a different "init" event:

```js
{type: "init", join: "<join_key>"}
```

The connection handler for the second player can look up the game with the join key as shown above. There is no need to respond.

Let’s dive into the details of implementing this design.

## Start a game

We’ll start with the initialization sequence for the first player.

In main.js, define a function to send an initialization event when the WebSocket connection is established, which triggers an open event:

```js
// /main.js

function initGame(websocket) {
  websocket.addEventListener("open", () => {
    // Send an "init" event for the first player.
    const event = { type: "init" };
    websocket.send(JSON.stringify(event));
  });
}
```

Update the initialization sequence to call initGame():

```js
// /main.js

window.addEventListener("DOMContentLoaded", () => {
  // Initialize the UI.
  const board = document.querySelector(".board");
  createBoard(board);
  // Open the WebSocket connection and register event handlers.
  const websocket = new WebSocket("ws://localhost:8001/");
  initGame(websocket);
  receiveMoves(board, websocket);
  sendMoves(board, websocket);
});
```

In app.py, define a new handler coroutine — keep a copy of the previous one to reuse it later:

```python
# /app.py

import secrets

JOIN = {}

async def start(websocket):
    # Initialize a Connect Four game, the set of WebSocket connections
    # receiving moves from this game, and secret access token.
    game = Connect4()
    connected = {websocket}

    join_key = secrets.token_urlsafe(12)
    JOIN[join_key] = game, connected

    try:
        # Send the secret access token to the browser of the first player,
        # where it'll be used for building a "join" link.
        event = {
            "type": "init",
            "join": join_key,
        }
        await websocket.send(json.dumps(event))

        # Temporary - for testing.
        print("first player started game", id(game))
        async for message in websocket:
            print("first player sent", message)

    finally:
        del JOIN[join_key]


async def handler(websocket):
    # Receive and parse the "init" event from the UI.
    message = await websocket.recv()
    event = json.loads(message)
    assert event["type"] == "init"

    # First player starts a new game.
    await start(websocket)
```

In index.html, add an <a> element to display the link to share with the other player.

```html
<!-- /index.html -->
<body>
  <div class="actions">
    <a class="action join" href="">Join</a>
  </div>
  <!-- ... -->
</body>
```

In main.js, modify receiveMoves() to handle the "init" message and set the target of that link:

```js
// /main,js

switch (event.type) {
  case "init":
    // Create link for inviting the second player.
    document.querySelector(".join").href = "?join=" + event.join;
    break;
  // ...
}
```

Restart the WebSocket server and reload http://localhost:8000/ in the browser. There’s a link labeled JOIN below the board with a target that looks like http://localhost:8000/?join=95ftAaU5DJVP1zvb.

The server logs say first player started game .... If you click the board, you see "play" events. There is no feedback in the UI, though, because you haven’t restored the game logic yet.

Before we get there, let’s handle links with a join query parameter.

## Join a game

We’ll now update the initialization sequence to account for the second player.

In main.js, update initGame() to send the join key in the "init" message when it’s in the URL:

```js
// /main.js

function initGame(websocket) {
  websocket.addEventListener("open", () => {
    // Send an "init" event according to who is connecting.
    const params = new URLSearchParams(window.location.search);
    let event = { type: "init" };
    if (params.has("join")) {
      // Second player joins an existing game.
      event.join = params.get("join");
    } else {
      // First player starts a new game.
    }
    websocket.send(JSON.stringify(event));
  });
}
```

In app.py, update the handler coroutine to look for the join key in the "init" message, then load that game:

```python
# /app.py

async def error(websocket, message):
    event = {
        "type": "error",
        "message": message,
    }
    await websocket.send(json.dumps(event))


async def join(websocket, join_key):
    # Find the Connect Four game.
    try:
        game, connected = JOIN[join_key]
    except KeyError:
        await error(websocket, "Game not found.")
        return

    # Register to receive moves from this game.
    connected.add(websocket)
    try:

        # Temporary - for testing.
        print("second player joined game", id(game))
        async for message in websocket:
            print("second player sent", message)

    finally:
        connected.remove(websocket)


async def handler(websocket):
    # Receive and parse the "init" event from the UI.
    message = await websocket.recv()
    event = json.loads(message)
    assert event["type"] == "init"

    if "join" in event:
        # Second player joins an existing game.
        await join(websocket, event["join"])
    else:
        # First player starts a new game.
        await start(websocket)
```

Restart the WebSocket server and reload http://localhost:8000/ in the browser.

Copy the link labeled JOIN and open it in another browser. You may also open it in another tab or another window of the same browser; however, that makes it a bit tricky to remember which one is the first or second player.

```
NOTE: You must start a new game when you restart the server.

Since games are stored in the memory of the Python process, they’re lost when you stop the server.

Whenever you make changes to app.py, you must restart the server, create a new game in a browser, and join it in another browser.
```

The server logs say first player started game ... and second player joined game .... The numbers match, proving that the game local variable in both connection handlers points to same object in the memory of the Python process.

Click the board in either browser. The server receives "play" events from the corresponding player.

In the initialization sequence, you’re routing connections to start() or join() depending on the first message received by the server. This is a common pattern in servers that handle different clients.

```
NOTE: Why not use different URIs for start() and join()?

Instead of sending an initialization event, you could encode the join key in the WebSocket URI e.g. ws://localhost:8001/join/<join_key>. The WebSocket server would parse websocket.path and route the connection, similar to how HTTP servers route requests.

When you need to send sensitive data like authentication credentials to the server, sending it an event is considered more secure than encoding it in the URI because URIs end up in logs.

For the purposes of this tutorial, both approaches are equivalent because the join key comes from an HTTP URL. There isn’t much at risk anyway!
```

Now you can restore the logic for playing moves and you’ll have a fully functional two-player game.

## Add the game logic

Once the initialization is done, the game is symmetrical, so you can write a single coroutine to process the moves of both players:

```python
async def play(websocket, game, player, connected):
    ...
```

With such a coroutine, you can replace the temporary code for testing in start() by:

```python
await play(websocket, game, PLAYER1, connected)
```

and in join() by:

```python
await play(websocket, game, PLAYER2, connected)
```

The play() coroutine will reuse much of the code you wrote in the first part of the tutorial.

Try to implement this by yourself!

Keep in mind that you must restart the WebSocket server, reload the page to start a new game with the first player, copy the JOIN link, and join the game with the second player when you make changes.

When play() works, you can play the game from two separate browsers, possibly running on separate computers on the same local network.

A complete solution is available at the bottom of this document.
