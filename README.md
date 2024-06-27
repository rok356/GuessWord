# GuessWord
A simple client-server application in Python to facilitate a "Guess a Word" game over TCP sockets using the `socket` and `asyncio` libraries.

# Server and Client Application

## Server Application

- Handles connections over TCP sockets.
- Initiates communication upon client connection by sending a welcome message.
- Verifies a predefined password sent by the client; disconnects the client or continues based on its correctness.
- Manages a game session between the client and the server.
- Uses predefined words and hints to support the game. The word is determined when the session is initialized.
- Responds to client requests and sends updates about game progress.
- Supports multiple client connections, with each client participating in its own game session.
- All the guess words and hints are stored in `words.txt`, you can change it with your own words

## Client Application

- Connects to the server using a TCP socket.
- Sends a password and handles initial communication from the server.
- Can send guesses and receive hints.
- Disconnects upon completion of the game session.

## Web Interface

- Web interface to display ongoing matches and their statuses.

# Running the Application

- First, run the server with the command: `python .\server.py`
- Then, run the client with the command: `python .\client.py`
- Input the password to connect to the server: `secret`
- Now you can play the guessing game.
- If you open `index.html` from the `web` folder, you can see the clients that are connected to the server and their guessing attempts.
