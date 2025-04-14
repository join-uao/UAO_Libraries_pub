import threading
import logging
import traceback
import importlib
import os
import sys

class ClientThread(threading.Thread):
    def __init__(self, task_type, id, data_queue):
        threading.Thread.__init__(self, name=f'{task_type}_{id}', daemon=True)

        self.ENDCHAR = '$'
        self.root_path = os.path.join(sys.path[0],
                                     'resources', 
                                     'available_tasks')
        
        self.task_type = task_type
        self.data = data_queue     # queue with tuples like (connection, client_address, task_kwargs). It communicates one specific task with the handler
        self.current_conn = None    # socket to respond to Automation Expert with the obtained result
        self.task_instance = self.prepare_task()
        
        
    def run(self):
        while True:
            try:
                logging.info('Awaiting new connection...')
                self.current_conn, client_address, kwargs = self.data.get()
                logging.info(f'New connection with {client_address}.')
                
                logging.info(f'Executing the task {self.task_type} with the arguments "{kwargs}"...')
                result = self.task_instance.execute(**kwargs)
                logging.info(f'Final result: "{result}". Sending....')
                self.send(result)
                logging.info(f'Task completed.')
                
            except:
                logging.error(traceback.format_exc())
                print(f'{client_address}: ¡¡¡ERROR in the task!!!. Check logfile for more details.')
                
            finally:
                # Clean up the connection
                self.current_conn.close()    
            
    def prepare_task(self):
        sys.path.append(self.root_path)
        logging.info(f'Importing the task file {self.task_type}.py...')
        mod = importlib.import_module(f'{self.task_type}')
        class_ = getattr(mod, self.task_type)
        instance = class_()
        
        return instance
    
    def send(self, item):
        item = str(item) + self.ENDCHAR
        self.current_conn.sendall(item.encode('utf-8'))
    