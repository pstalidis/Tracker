import asyncio
import os


devices = set()
with open(os.path.join("data", "locations.csv"), "r") as file:
    for line in file:
        clean = line.split(",")
    last = int(clean[0]) + 1
print("waiting for location %d" % last)


async def listener(reader, writer):
    global last
    while True:
        try:
            data = await reader.readuntil(separator=b';')
            address = writer.get_extra_info('peername')
            print(f"From {address!r}, Received {data!r}")

            message = data.decode()
            if not message:
                break

            if message.startswith('##'):
                devices.add(message.rstrip(";").split(",")[1].split(":")[-1])
            elif message.startswith(tuple(devices)):
                pass
            elif message.startswith('imei:'):
                last += 1
                with open(os.path.join("data", "locations.csv"), "a") as loc:
                    loc.write("%d,%s\n" % (last, message.rstrip(";")))
            else:
                print("what the fuck!")

            writer.write(b'ON')
            await writer.drain()

        except asyncio.exceptions.IncompleteReadError:
            break

    print("Closing the connection")
    writer.close()
    await writer.wait_closed()
    print("Connection closed")


async def main():
    server = await asyncio.start_server(listener, "195.251.117.224", 9999)

    address = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    print(f'Serving on {address}')

    async with server:
        await server.serve_forever()


asyncio.run(main())

