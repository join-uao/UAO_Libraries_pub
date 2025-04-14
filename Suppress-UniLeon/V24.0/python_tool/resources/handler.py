import threading
from queue import Queue, Empty
import logging
import traceback
from resources.client_thread import ClientThread

class Handler(threading.Thread):
    def __init__(self, conn_queue, connections_timeout=None):
        threading.Thread.__init__(self, name='Handler', daemon=True)
        
        self.ENDCHAR = '$'
        self.connections = conn_queue   # queue used by handler and tcp_server to communicate. It contains tuples (connection, client_address)
        self.current_conn = None    # got from the aforementioned queue
        self.timeout = connections_timeout  #timeout for every new connection
        self.queues = {}   # key: TASK_NAME, value: dict of TASK_ID: QUEUE
    
    def run(self):
        logging.info('dispatching incomming connections...')

        while True:
            self.current_conn, client_address = self.connections.get()
            
            try:
                logging.info(f'connection from {client_address}. Receiving data...')
                self.current_conn.settimeout(self.timeout)
                buffer = self.recv(2048)
                        
                logging.info('evaluating data received...')
                msg = self.eval(buffer)
                
                task_name, task_id, kwargs = self.parse_msg(msg)
                
                if not kwargs:    # Instantiation of the thread that will run the task
                    logging.info(f'instantiating a {task_name} type task...') 
                    q = Queue(maxsize=1)
                    new_task = ClientThread(task_name, task_id, q)
                    
                    self.add_queue(task_name, task_id, q)
                    new_task.start()
                    
                    logging.info(f'Task prepared. Sending the ID {task_id} to Automation Expert...')
                    self.send(task_id)
                    self.current_conn.close()
                    
                else:     # A task execution with specific kwargs is requested
                    q = self.queues[task_name][task_id]
                    try: #If it's successful, the last task was retarded and the last package loaded in the queue is obsolete, so the Handler will pop it out
                        conn, _, _= q.get_nowait()
                        conn.close()
                        
                    except Empty: # If no one package remains in the queue, ignore the exception
                        pass
                        
                    finally:
                        q.put((self.current_conn, client_address, kwargs)) # Load a new data package that the task joined to the queue will consume
            
            except Exception:
                logging.error(traceback.format_exc())
                print(f'¡¡¡ERROR in the handler!!!. Check logfile for more details.')
                
                try:    #If an exception occurs, try to close the connection
                    self.current_conn.close()
                except:
                    logging.error('Imposible to close the socket. It could be corrupted...')
    
    
    
    
    def eval(self, buffer):
        if buffer[0] == '{' and buffer[-1] == '}':  #dict-like buffer
            msg = eval(buffer)
        else:   #The buffer is only a string that contains the task name (SUM, MOVING AVG...)
            msg = buffer    
        return msg
                
    def parse_msg(self, msg):
        if isinstance(msg, str):    # A specific task ID is requested (so a new task is defined)
            id_ = self.get_new_id(msg)
            return msg, id_, None
            
        elif isinstance(msg, dict):  # A task execution with specific kwargs is requested
            task_name = next(iter(msg))
            task_id = int(msg[task_name])
            kwargs = msg['KWARGS']
            return task_name, task_id, kwargs
                
    def get_new_id(self, task_name):
        queues = self.queues.get(task_name)
        if not queues:   # Doesn't exist yet any instance of this type of tasks
            queues = {}
            self.queues[task_name] = queues
        return len(queues)+1
        
    def add_queue(self, task_name, id_, q):
        self.queues.update({task_name:{id_: q}})
        
        
    def recv(self, chunk_size):
        # Receive the data in small chunks, then return all data in a single string
        buffer = ''
        while True:
            data = (self.current_conn.recv(chunk_size)).decode('utf-8')
            
            logging.info(f'received "{data}"')
            if not data:
                raise Exception("No data received. Ignoring it...")
                
            if not self.ENDCHAR in data:
                buffer += data
            else:
                buffer += data.split(self.ENDCHAR)[0]
                break
        return buffer
        
    def send(self, item):
        item = str(item) + self.ENDCHAR
        self.current_conn.sendall(item.encode('utf-8'))