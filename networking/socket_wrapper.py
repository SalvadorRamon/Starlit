'''
Created on Apr 23, 2016

@author: Matias
'''

import logging, socket, threading

# logging.basicConfig(level = logging.DEBUG)
log = logging.getLogger(__name__)


class SocketWrapper(object):
	'''
	classdocs
	'''

	def setDelegate(self, delegate):
		self.delegate = delegate

	def setHost(self, host):
		self.address[0] = host

	def setPort(self, port):
		self.address[1] = port

	def host(self):
		return self.address[0]

	def port(self):
		return self.address[1]

	def ready(self):
		if not isinstance(self.host(), str):
			log.debug("Invalid host!")
			return False

		if not isinstance(self.port(), int):
			log.debug("Invalid port!")
			return False

		return True

	def _prepareSocket(self):
		# By default, we assume setting the socket failed, since this method needs
		# to be overwritten since the class is incapable of doing anything on its own.
		log.debug("Prepare socket must be overwritten!")
		return True

	def start(self):
		# Lock the method to prevent issues when multithreading.
		self._startLock.acquire()

		# Trigger the starting event handler method.
		if not self._starting():
			# Upon failure, release the lock.
			self._startLock.release()

			# Log the issue and return failure code (False).
			log.debug("Starting failed!")
			return False

		# Reset the socket to get it ready for a new connection.
		if not self.reset():
			# Upon failure, release the lock.
			self._startLock.release()

			# Log the issue and return failure code (False).
			log.debug("Reset failed!")
			return False

		# Trigger the started event handler method.
		result = self._started()

		# Release the lock to allow other threads to access the method.
		self._startLock.release()

		return result

	def stop(self):
		# Lock the method to prevent issues when multithreading.
		self._stopLock.acquire()

		# Trigger the stopping event handler method.
		if not self._stopping():
			# Upon failure, release the lock.
			self._stopLock.release()

			# Log the issue and return failure code (False).
			log.debug("Stopping failed!")
			return False

		# If there's a socket available, try to close it gracefully.
		if self.socket:
			try:
				log.debug("Attempting to close the socket.")
				self.socket.close()
			except:
				log.debug("Socket failed to close! (exception)")

		# Clear out the socket, to reflect the fact it's no longer usable.
		self.socket = None

		# Trigger the stopped event handler method.
		result = self._stopped()

		# Release the lock to allow other threads to access the method.
		self._stopLock.release()

		return result

	def reset(self):
		if not self.ready():
			log.debug("Aborting reset!")
			return False

		# Attempt to stop any open socket
		self.stop()

		# Create socket for service
		self.socket = socket.socket()

		return self._prepareSocket()

	# The following four method are for overwriting purposes
	def _starting(self):
		return True

	def _started(self):
		return True

	def _stopping(self):
		return True

	def _stopped(self):
		return True

	# Overwritten methods
	def __str__(self):
		return "SocketWrapper (" + object.__str__(self) + ")"

	def __init__(self, address, sock=None):
		'''
		Constructor
		'''
		self.delegate = None

		self.socket = sock
		self.address = address

		self._stopLock = threading.Lock()
		self._startLock = threading.Lock()
