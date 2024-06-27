import asyncio
from datetime import datetime
import json
import websockets
from collections import defaultdict
from game_logic import initialize_game_state, process_guess, is_game_won, is_game_over

PREDEFINED_PASSWORD = "secret"
clients = defaultdict(dict)  # Track connected game clients
websockets_clients = set()  # Track connected WebSocket clients

async def send_to_web_clients():
    while True:
        if websockets_clients:
            data = {
                "clients": list(clients.keys()),
                "details": [{k: v} for k, v in clients.items()]  # Send the entire client dict, including game state
            }
            message = json.dumps(data, default=str)  # Use default=str to handle any non-serializable types
            tasks = [asyncio.create_task(ws.send(message)) for ws in websockets_clients]
            await asyncio.wait(tasks)
        await asyncio.sleep(1)

async def register_websocket(websocket, path):
    websockets_clients.add(websocket)
    try:
        await websocket.wait_closed()
    except Exception as e:
        print(f"WebSocket connection error: {e}")
    finally:
        websockets_clients.remove(websocket)

async def handle_client(reader, writer):
    address = writer.get_extra_info('peername')
    print(f"New connection from {address}")

    # Identify the type of client
    data = await reader.read(100)
    client_type = data.decode().strip()

    if client_type == "web":
        await register_websocket(writer, None)  # Register WebSocket client
    elif client_type == "game":
        await handle_game_client(reader, writer, address)
    else:
        print(f"Unknown client type: {client_type}")
        writer.close()
        await writer.wait_closed()

async def handle_game_client(reader, writer, address):
    async def send_message(message):
        writer.write((message + '\n').encode())
        await writer.drain()

    address_str = f"{address[0]}:{address[1]}"  # Convert tuple to string
    clients[address_str] = {"start_time": datetime.now()}

    try:
        await send_message("Welcome to the Guess a Word game!")
        await send_message("Please enter the password:")

        data = await reader.readline()
        password = data.decode().strip()

        if password != PREDEFINED_PASSWORD:
            await send_message("Incorrect password. Disconnecting...")
            writer.close()
            await writer.wait_closed()
            print(f"Disconnected {address} due to incorrect password.")
            return

        await send_message("Password correct! Let's start the game.")

        # Initialize game state
        game_state = initialize_game_state()

        await send_message(f"Hint: {game_state['hint']}")
        await send_message(f"The word has {len(game_state['word'])} letters.")
        await send_message(f"Word: {game_state['revealed_word']}")
        await send_message(f"You have {game_state['attempts_left']} attempts to guess the word.")

        while True:
            await send_message("Enter your guess (single letter):")
            guess = (await reader.readline()).decode().strip().lower()

            if len(guess) != 1 or not guess.isalpha():
                await send_message("Invalid guess. Please enter a single letter.")
                continue

            # When processing a guess
            game_state = process_guess(game_state, guess)
            clients[address_str]['game_state'] = {
                "attempts_left": game_state['attempts_left'],
                "game_won": is_game_won(game_state),
                "game_over": is_game_over(game_state),
                # Add more details as needed
            }

            await send_message(game_state['feedback'])
            await send_message(f"Word: {game_state['revealed_word']}")
            await send_message(f"Attempts left: {game_state['attempts_left']}")

            if is_game_won(game_state):
                await send_message("Congratulations! You guessed the word correctly!")
                break

            if is_game_over(game_state):
                await send_message(f"Out of attempts. The word was: {game_state['word']}. Better luck next time!")
                break

    except Exception as e:
        print(f"Error with client {address}: {e}")
    finally:
        del clients[address_str]  # Remove client from tracking
        writer.close()
        await writer.wait_closed()
        print(f"Connection closed for {address}")

async def main():
    game_server = await asyncio.start_server(handle_client, '127.0.0.1', 8888)
    websocket_server = await websockets.serve(register_websocket, '127.0.0.1', 5678)

    addr_game = game_server.sockets[0].getsockname()
    addr_ws = websocket_server.sockets[0].getsockname() if websocket_server.sockets else ('127.0.0.1', 5678)
    print(f'Serving on {addr_game} for game clients and on {addr_ws} for WebSocket clients')

    asyncio.create_task(send_to_web_clients())

    async with game_server, websocket_server:
        await asyncio.gather(
            game_server.serve_forever(),
            websocket_server.wait_closed()
        )

if __name__ == "__main__":
    asyncio.run(main())