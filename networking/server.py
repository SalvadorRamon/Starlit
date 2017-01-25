'''
Created on Apr 23, 2016

@author: Matias
'''

import logging, socket, threading
from networking import SocketWrapper
from networking import Client

# logging.basicConfig(level = logging.DEBUG)
log = logging.getLogger(__name__)


class Server(SocketWrapper):
	def accept(self):
		if not self._acceptThread.is_alive():
			log.debug("Thread unavailable (blocking-accept used)!")
			return self.socket.accept()

		log.debug("Starting accepting thread.")

		while self.accepting and self.socket:
			log.debug("Thread is waiting for clients (accept).")
			(sock, address) = self.socket.accept()

			log.info("Accepted client with IP {0}".format(address[0]))
			self._lock.acquire()

			if self.delegate and hasattr(self.delegate, "_serverFoundClient"):
				self.delegate._serverFoundClient(self, Client(address, sock))
			else:
				log.debug("Unsupported delegate (_serverFoundClient).")

			self._lock.release()

		log.debug("Stopping accepting thread.")

	def _prepareSocket(self):
		if not self.socket:
			log.debug("Aborting _prepareSocket method!")
			return False

		log.debug("Preparing socket.")

		# Bind the service to it's port at the address
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.socket.bind(self.address)

		return True

	def _started(self):
		if not self.socket:
			log.debug("Aborting _starting method!")
			return False

		log.info("Serving, will now wait for clients.")

		# Open port for potential clients.
		# By default, allow up to five clients to queue
		# to be accepted later on. We begin listening for connections
		# at this point in the program. We need to accept next.
		# REMEMBER: 5 clients is typically the maximum.
		self.socket.listen(5)

		self.accepting = True
		self._acceptThread.start()

		return True

	def _stopping(self):
		self.accepting = False
		return True

	def __init__(self, address, sock=None):
		'''
		Constructor
		'''
		SocketWrapper.__init__(self, address, sock)

		self.accepting = sock is not None

		self._lock = threading.Lock()
		self._acceptThread = threading.Thread(target=self.accept)
		self._acceptThread.setDaemon(True)

		if self.accepting:
			self._acceptThread.start()
