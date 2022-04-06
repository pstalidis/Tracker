import socket
from datetime import datetime

HOST, PORT = "195.251.117.224", 9999


# Extract lat, lon from transmitted data
def convert(transmission):
    try:
        _data = transmission.split(",")
        _lat = _data[7]
        n = 1 if _data[8] == "N" else -1
        _lon = _data[9]
        e = 1 if _data[10] == "E" else -1
        latitude = round(n * int(_lat[:2]) + float(_lat[2:]) / 60, 6)
        longitude = round(e * int(_lon[1:3]) + float(_lon[3:]) / 60, 6)
    except:
        latitude, longitude = 0.0, 0.0
    finally:
        return latitude, longitude


# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = (HOST, PORT)
print('Starting up on {} port {}'.format(*server_address))
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

connected = False
locations = []

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
                    debug.write("{}, {!r}\n".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),data))
                    debug.close()
                    if data.startswith(b'##'):
                        # Opened connection
                        connection.sendall(b"ON")
                        #connection.sendall(b"LOAD")
                    elif data.startswith(b'864895033864933'):
                        # Keep alive
                        connection.sendall(b"ON")
                    elif data.startswith(b'imei'):
                        # Tracker transmission
                        location = convert(data.decode("utf-8"))
                        lat, lon = location
                        print("Debug", 'location extracted: {},{}'.format(lat, lon))
                        store = open("locations.txt", "a")
                        store.write("%s,%.6f,%.6f\n" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), lat, lon))
                        store.close()
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

