from concurrent.futures import ThreadPoolExecutor
import errno
import socket                                         
import time
import sys
import threading
import re
import client_handler
from client_handler import client_h 


class tcp_server():

	def __init__(self, port, connQueue, server_threads = 5):
		self.server_socket = self.init_server_socket(port, connQueue)
		self.pool = ThreadPoolExecutor(server_threads)


	def serve(self):
		print("Server running")
		running = True
		kill_service_lock = threading.Lock()
		while running:
			#implementing non-blocking socket.accept() here - so server can check if KILL_SERVICE has
			#been issued and can immediately, and gracefully, teardown
			try:
				client_socket, client_addr = self.server_socket.accept()      
				print("servicing new connection")
				self.pool.submit(
					launch_client_handler, 
					client_socket, 
					client_addr, 
					self.server_info, 
					kill_service_lock
				)
			except IOError as e:  # and here it is handeled
				if e.errno == errno.EWOULDBLOCK:
					pass

			#checking if we should kill service as the result of a "KILL_SERVICE" command
			if kill_service_lock.acquire(False):
				if client_handler.kill_service_value:
					running = False
					self.pool.shutdown()
					print("KILLING SERVICE...")
				kill_service_lock.release()
				

		self.server_socket.close()
		print("Server has been shut down")

	def init_server_socket(self, port, connQueue):
		"""
		NOTE - this also sets the configuration settings dict 
		for the server.
		"""
		server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
		#TODO remove this hard coded host in production
		server_host = "localhost" #socket.gethostname()                           
		server_port = port
		server_socket.bind((server_host, server_port))                                  
		server_socket.listen(connQueue)                                           
		server_socket.setblocking(0)

		#configuration settings for server
		self.server_info = {
			"host": str(server_host),
			"port": str(port),
			"sid": "11315921"
		}
		return server_socket

#launches a client handler instance
def launch_client_handler(client_sock, client_addr, server_info, kill_service_lock):
    new_client = client_h(client_sock, client_addr, server_info, kill_service_lock)

if __name__ == '__main__':
    s = tcp_server(int(sys.argv[1]), 5)
    s.serve()


