import socket
from datetime import datetime


HOST, PORT = "195.251.117.224", 9999


# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = (HOST, PORT)
print('Starting up on {} port {}'.format(*server_address))
sock.bind(server_address)

with open("locations.csv", "r") as file:
    for line in file:
        clean = line.split(",")
    counter = int(clean[0]) + 1
print("waiting for location %d" % counter)


# Listen for incoming connections
sock.listen(1)


while True:
    # Wait for a connection
    print('Waiting for a connection')
    buffer = b''                                # store bytes coming from the connection to extract lines
    connection, client_address = sock.accept()  # accept a new connection
    print('Connected from ', client_address)
    while True:
        try:
            # Read data from the connection until a line is detected
            data = connection.recv(128)             # read 128 bytes
            #with open("debug.txt", "a") as debug:
            #    debug.write("{}, {!r}\n".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), data))
            buffer += data                          # append the bytes to the buffer
            tokens = buffer.split(b";")             # split the buffer into tokens (newline separator)
            if len(tokens) > 1:                     # if there are more than 1 token (at least one ";")
                line = tokens.pop(0)                # take the part before the first ";" and use it as a new line
                buffer = b";".join(tokens)          # rejoin the remaining tokens back to the buffer
                counter += 1
            else:
                continue
            #print("Received a new line")

            # Handle the detected line
            try:
                clean = line.decode("utf-8")            # decode bytes to utf-8 string
            except UnicodeDecodeError:
                with open("binary.txt", "ab") as binary:
                    binary.write(line)
                clean = ""
            if clean.startswith("imei"):              # this is useful data (a location)
                # result += clean + "\n"
                with open("locations.csv", "a") as file:
                    file.write("%d,%s\n" % (counter, clean))
            #if clean.startswith("##"):                  # this is how new connections start
            #    pass
            #elif clean.startswith("864895033864933"):   # this is a keep alive
            #    pass
            elif not clean:
                break
            else:
                #break
                pass
            connection.sendall(b"ON")
        except ConnectionResetError:
            break
