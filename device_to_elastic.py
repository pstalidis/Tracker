import asyncio
import elasticsearch
from datetime import datetime
import time

elastic_settings = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 1
    },
    "mappings": {
        "properties": {
            "device": {
                "type": "keyword"
            },
            "operation": {
                "type": "keyword"
            },
            "datetime": {
                "type": "date",
                "format": "yyyy-MM-dd HH:mm:ss"
            },
            "location": {
                "type": "geo_point"
            },
            "F": {
                "type": "keyword"
            },
            "A": {
                "type": "keyword"
            },
            "pitch": {
                "type": "float"
            },
            "heading": {
                "type": "float"
            },
        }
    }
}

time.sleep(60)

es = elasticsearch.Elasticsearch(["elastic:9200"])
if not es.indices.exists(index='cobra'):
    es.indices.create(index='cobra', body=elastic_settings)


def dms2dd(sample, head):
    # example: s = """2257.702"""
    degrees, minutes = divmod(float(sample), 100)
    dd = round(float(degrees) + float(minutes) / 60, 6)
    if head in {"S", "W"}:
        dd *= -1
    return dd


def parser(line):
    info = line.split(",")
    if len(info) == 13:
        doc = {
            "device": info[0],
            "operation": info[1],
            "datetime": datetime.strptime(info[2], "%y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S"),
            "unk1": info[3],
            "F": info[4],
            # "clock": datetime.strptime(info[5], "%H%M%S.%U").time(),
            "A": info[6],
            "location": {
                "lat": dms2dd(info[7], info[8]),
                "lon": dms2dd(info[9], info[10]),
            },
            # "lat": dms2dd(info[7]),
            # "N": info[8],
            # "lon": dms2dd(info[9]),
            # "E": info[10],
            "pitch": info[11],
            "heading": info[12]
        }
        return doc, info[2]


devices = set()


# with open("locations.csv", "r") as file:
#     for l in file:
#         clean = l.split(",")
#     last = int(clean[0]) + 1
# print("waiting for location %d" % last)


async def listener(reader, writer):
    print("Starting listener; Elastic index: ", es.indices.exists(index='cobra'))
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
                document, identifier = parser(message.rstrip(";"))
                r = es.index(index='cobra', document=document, id=identifier)
            else:
                print("what the fuck!")

            writer.write(b'ON')
            await writer.drain()

        except asyncio.exceptions.IncompleteReadError:
            break
        except ConnectionResetError:
            break

    print("Closing the connection")
    writer.close()
    await writer.wait_closed()
    print("Connection closed")


async def main():
    server = await asyncio.start_server(listener, "0.0.0.0", 5000)

    address = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    print(f'Serving on {address}')

    async with server:
        await server.serve_forever()


asyncio.run(main())
