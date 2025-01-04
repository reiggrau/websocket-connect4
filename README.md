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

# 4 - Run the server

```bash
py app.py
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

NOTE: You must restart the WebSocket server when you make changes

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

````bash
# Terminal 2
py app.py
```

Refresh http://localhost:8000/ in your web browser. Click various columns in the board. The server receives messages with the expected column number.

There isn’t any feedback in the board because you haven’t implemented that yet. Let’s do it.
````
