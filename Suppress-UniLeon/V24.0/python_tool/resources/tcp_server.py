import socket
from queue import Queue
import logging
from resources.handler import Handler


class TCP_Server:
    def __init__(self, ip, port, limit_connections=None):

        # Create a TCP/IP socket and set it as non-blocking
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setblocking(False)

        # Bind the socket to the port
        server_address = (ip, port)
        logging.info(f'TCP Server starting on {server_address}...')

        # Reuse the socket address
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Create a queue to store the connections and start the handler
        self.connections = Queue()
        self.handler = Handler(self.connections, connections_timeout=0.020)
        self.handler.start()
        

        try:
            self.sock.bind(server_address)
        except socket.error as msg:
            import sys
            logging.error('bind failed.')
            logging.error(msg)
            sys.exit()

        # Listen for incoming connections
        if limit_connections:
            self.sock.listen(limit_connections)
        else:
             self.sock.listen()

    def handle(self):
        # Wait for a connection
        try:
            connection, client_address = self.sock.accept()
            logging.info(f'connection from {client_address} captured. Passing it to handler...')
            self.connections.put((connection, client_address))
        except BlockingIOError: #None connection available
            pass
        
    def stop(self):
        self.sock.close()