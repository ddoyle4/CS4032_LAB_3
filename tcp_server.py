from concurrent.futures import ThreadPoolExecutor
import errno
import socket                                         
import time
import sys
import threading
import re
import client_handler
from client_handler import client_h 
from chatroom import chatroom_manager, chatroom, message


class tcp_server():

	def __init__(self, port, connQueue, server_threads = 5):
		self.server_socket = self.init_server_socket(port, connQueue)
		self.global_variables_lock = threading.Lock()
		self.pool = ThreadPoolExecutor(server_threads)
                self.chatroom_manager = chatroom_manager()


	def serve(self):
		print("Server running")
		running = True
		while running:

			#implementing non-blocking socket.accept() here - so server can check if KILL_SERVICE has
			#been issued and can immediately, and gracefully, teardown

			try:    #accept only if there is something to accept
				client_socket, client_addr = self.server_socket.accept()      
                                new_client_id = self.get_new_client_id()
				print("servicing new connection")
				self.pool.submit(
					launch_client_handler, 
                                        new_client_id,
					client_socket, 
					client_addr, 
					self.server_info, 
					self.global_variables_lock,
                                        self.chatroom_manager
				)
			except IOError as e:  # otherwise just sleep for a while
				if e.errno == errno.EWOULDBLOCK:
                                        #should sleep when not working
			                time.sleep(0.001)   

			#checking if we should kill service as the result of a "KILL_SERVICE" command
			if self.global_variables_lock.acquire(False):
                            try:
				if client_handler.kill_service_value == True:
					running = False
                                        self.chatroom_manager.close_all()
					self.pool.shutdown(wait=False)
					print("KILLING SERVICE...")
                            finally:
				self.global_variables_lock.release()


		self.server_socket.close()
		print("Server has been shut down")

	def init_server_socket(self, port, connQueue):
		"""
		NOTE - this also sets the configuration settings dict 
		for the server.
		"""
		server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
		#TODO remove this hard coded host in production
		server_host = socket.gethostname()                           
                print "server_host:", server_host
		server_port = port
		server_socket.bind((server_host, server_port))                                  
		server_socket.listen(connQueue)                                           
		server_socket.setblocking(0)

		#configuration settings for this server
		self.server_info = {
			"host": socket.gethostbyname(server_host),
			"port": str(port),
			"sid": "11315921"
		}
		return server_socket

        def get_new_client_id(self):
            new_id = 0
            with self.global_variables_lock:
                client_handler.master_client_id += 1
                new_id = client_handler.master_client_id

            return new_id


#launches a client handler instance
def launch_client_handler(client_id, client_sock, client_addr, server_info, global_variables_lock, cr_manager):
    new_client = client_h(client_id, client_sock, client_addr, server_info, global_variables_lock, cr_manager)

if __name__ == '__main__':
    s = tcp_server(int(sys.argv[1]), 5)
    s.serve()


