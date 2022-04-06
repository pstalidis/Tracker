import socket
from datetime import datetime
# import pandas as pd
# import time

HOST, PORT = "195.251.117.224", 9999


def convert_to_decimal(degrees):
    degrees = float(degrees)
    hours = degrees // 100
    minutes = degrees % 100
    coordinate = round(hours + minutes/60, 6)
    return coordinate


# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = (HOST, PORT)
print('Starting up on {} port {}'.format(*server_address))
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

# Dataframe to store information
# df = pd.read_csv("locations.csv", index_col="packet")

with open("locations.csv", "r") as file:
    for line in file:
        try:
            last = int(line.split(",")[0])
        except:
            pass


while True:
    # Wait for a connection
    print('Waiting for a connection')
    connection, client_address = sock.accept()
    try:
        print('Connection from', client_address)
        # Receive the data in small chunks and retransmit it
        while True:
            try:
                data = connection.recv(128)
                print("Debug", 'received {!r}'.format(data))
                if data:
                    debug = open("debug.txt", "a")
                    debug.write("{}, {!r}\n".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), data))
                    debug.close()
                    if data.startswith(b'##'):
                        # Opened connection
                        connection.sendall(b"ON")
                        # connection.sendall(b"LOAD")
                    elif data.startswith(b'864895033864933'):
                        # Keep alive
                        connection.sendall(b"ON")
                    elif data.startswith(b'imei'):
                        # Tracker transmission
                        info = data.decode("utf-8").rstrip(";")#.split(",")
                        # information = {
                        #     "device": info[0],
                        #     "operation": info[1],
                        #     "datetime": datetime.strptime(info[2], "%y%m%d%H%M%S"),
                        #     "unk1": info[3],
                        #     "F": info[4],
                        #     "clock": time.strptime(info[5].split(".")[0], "%H%M%S"),
                        #     "A": info[6],
                        #     "lat": convert_to_decimal(info[7]),
                        #     "N": info[8],
                        #     "lon": convert_to_decimal(info[9]),
                        #     "E": info[10],
                        #     "pitch": info[11],
                        #     "heading": info[12]
                        # }
                        # df.append(information, ignore_index=True)
                        # df.to_csv("locations.csv")
                        last += 1
                        with open("locations.csv", "a") as file:
                            file.write("%d,%s\n" % (last, info))
                        connection.sendall(b"ON")
                    else:
                        print("Debug", "probably loading file...")
                else:
                    print('No data from', client_address, ', closing the connection!')
                    break
            except ConnectionResetError:
                break
    except KeyboardInterrupt:
        print('Exit')
        # connection.close()
    finally:
        # Clean up the connection
        connection.close()
