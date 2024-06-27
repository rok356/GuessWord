import asyncio

async def tcp_client():
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)
    expecting_input = False  # Flag to control message display
    writer.write(b'game\n')
    await writer.drain()
    
    try:
        buffer = ""

        while True:
            data = await reader.read(1024)
            if not data:
                break

            buffer += data.decode()
            while '\n' in buffer:
                line, buffer = buffer.split('\n', 1)
                line = line.strip()
                if line:
                    # Only print the line if we're not expecting input
                    if not expecting_input:
                        print(line)

                    if "Please enter the password:" in line or "Enter your guess (single letter):" in line:
                        expecting_input = True
                        user_input = input()  # Directly prompt for input
                        writer.write((user_input + '\n').encode())
                        await writer.drain()
                        expecting_input = False  # Reset the flag after input

                    if "Congratulations" in line or "Out of attempts" in line:
                        break

        writer.close()
        await writer.wait_closed()
    except ConnectionResetError:
        print("Connection lost. Server may have shut down or disconnected.")
    except Exception as e:
        print(f"An error occurred: {e}")

asyncio.run(tcp_client())