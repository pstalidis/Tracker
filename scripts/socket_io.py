from datetime import datetime
import socketserver
import logging


console = logging.StreamHandler()
console.setFormatter(logging.Formatter('[%(name)s: %(levelname)-4s] %(message)s'))
logger = logging.getLogger(__name__)
logger.addHandler(console)
# logger.setLevel(os.environ.get("LOGGER", "INFO"))
logger.setLevel("DEBUG")


# Extract lat, lon from transmitted data
def convert(transmission):
    _data = transmission.split(",")
    _lat = _data[7]
    n = 1 if _data[8] == "N" else -1
    _lon = _data[9]
    e = 1 if _data[10] == "E" else -1
    latitude = round(n * int(_lat[:2]) + float(_lat[2:]) / 60, 6)
    longitude = round(e * int(_lon[1:3]) + float(_lon[3:]) / 60, 6)
    return latitude, longitude


class TrackerHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.
    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    def handle(self):
        # self.request is the TCP socket connected to the client
        data = self.request.recv(1024).strip()
        if data:
            debug = open("debug.txt", "a")
            debug.write(str(datetime.now()) + " " + data.decode("utf-8") + "\n")
            debug.close()
            if data.startswith(b'##'):
                # Opened connection
                self.request.sendall(b"LOAD")
            elif data.startswith(b'864895033864933'):
                # Keep alive
                self.request.sendall(b"ON")
            elif data.startswith(b'imei'):
                # Tracker transmission
                location = convert(data.decode("utf-8"))
                lat, lon = location
                print("Debug", 'location extracted: lat {}, lon {}'.format(lat, lon))
                store = open("locations.txt", "a")
                store.write("%s,%f0.6,%f0.6\n" % (str(datetime.now()), lat, lon))
                store.close()
                self.request.sendall(b"ON")


if __name__ == "__main__":
    HOST, PORT = "195.251.117.224", 9999
    # Create the server, binding to localhost on port 9999
    with socketserver.TCPServer((HOST, PORT), TrackerHandler) as server:
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        server.serve_forever()
