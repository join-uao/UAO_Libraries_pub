import logging
import os
import sys

sys.path.append(os.path.join(os.path.dirname(sys.path[0])))

from resources.tcp_server import TCP_Server

if __name__ == "__main__":

    # Configure the logging output
    log_path = os.path.join(sys.path[0], 'resources', 'error_list.log')
    if os.path.isfile(log_path):
        os.remove(log_path)
    logging.basicConfig(filename=log_path,
                        level=logging.INFO,
                        format='[%(asctime)s][%(levelname)s][%(threadName)s] %(message)s')
    
    # Creates the tcp server to communicate with Ecostruxure Automation Expert
    server = TCP_Server('127.0.0.1',61499)
    
    while True:
        try:
            server.handle()
        except KeyboardInterrupt:
            logging.info('interrupted server')
            server.stop()
            sys.exit(0)
