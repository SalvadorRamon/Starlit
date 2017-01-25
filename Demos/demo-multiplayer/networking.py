import threading
import socket
import struct
import Queue

import logging

# logging.basicConfig(level = logging.DEBUG)
log = logging.getLogger(__name__)


class SocketWrapper(object):
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
		return False

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

	def _prepareSocket(self):
		return True

	# Overwritten methods
	def __str__(self):
		return "SocketWrapper (" + object.__str__(self) + ")"

	def __init__(self, address, sock=None):
		object.__init__(self)

		self.socket = sock
		self.address = address

		self._stopLock = threading.Lock()
		self._startLock = threading.Lock()


class Client(SocketWrapper):
	# The following is a limit imposed on the size of the data to be sent.
	# h denotes short, aka, two bytes. This means the maximum amount of data
	# that can be sent and received by the clients is 2 ^ (8 * byteCount),
	# where byteCount is two. To determine byteCount, I'm using struct.calcsize.
	SendLimitDescriptor = "h"  # Short (2 bytes)
	SendLimit = 2 ** (struct.calcsize("h") * 8)

	ReceiveLimitDescriptor = "q"  # Long (8 bytes)
	ReceiveLimit = 2 ** (struct.calcsize("h") * 8)

	MetaLength = struct.calcsize("h")

	@staticmethod
	def Pack(data):
		# Prepend data with information about the data.
		info = struct.pack(Client.SendLimitDescriptor, len(data))
		return info + data

	@staticmethod
	def Unpack(data):
		# If the data isn't even big enough to contain metadata, it's invalid!
		if len(data) < Client.MetaLength: return None
		metadata = data[:Client.MetaLength]
		(length,) = struct.unpack(Client.SendLimitDescriptor, metadata)
		return (length, data[Client.MetaLength:])  # Returns (size, payload)

	def send(self, data):
		if not self.socket:
			log.debug("Aborting send, socket is missing!")
			return False

		if len(data) > Client.SendLimit:
			log.debug("Data size limit exceeded, aborting send!")
			return False

		# Add the data to the outbound/output queue to make send non-blocking.
		log.debug("Adding data to outbound queue.")
		self._oQueue.put(data)

		log.debug("oQueue has " + str(self._oQueue.qsize()) + " item(s).")

		return True

	def receiveBytes(self, total):
		data = ""
		while len(data) < total:
			log.debug("Waiting to receive data.")
			receive = None
			try:
				received = self.socket.recv(total - len(data))
			except:
				return None
			if not received: return None
			data += received

		log.debug("Received " + str(len(data)) + " bytes.")
		return data

	def receive(self):
		log.debug("Locking receiving method.")

		if not self._iThread.is_alive():
			log.debug("Receiving data (blocking-method).")

		# Pre-fetch metadata, since the metadata includes the length of the
		# entire data to be received.
		meta = self.receiveBytes(Client.MetaLength)

		if not isinstance(meta, str):
			log.debug("Failed to receive metadata!")
			self.stop()
			return None

		total = Client.Unpack(meta)[0]
		payload = self.receiveBytes(total)

		if not isinstance(payload, str):
			log.debug("Failed to receive payload!")
			self.stop()
			return None

		return payload

	def _iHandler(self):
		while self.connected:
			data = self.receive()
			if not isinstance(data, str): break
			# Notify the delegate of the socket's disconnection.
			if self.delegate and hasattr(self.delegate, "clientReceivedData"):
				self.delegate.clientReceivedData(self, data)
			else:
				log.debug("Unsupported delegate (clientReceivedData).")
		log.debug("Stopping input handler.")

	def _oHandler(self):
		while self.connected:
			data = Client.Pack(self._oQueue.get())
			try:
				self.socket.sendall(data)
			except:
				break
			log.debug("Sent " + str(len(data)) + " bytes.")
		log.debug("Stopping output handler.")

	def _started(self):
		if not self.socket:
			log.debug("Aborting _started method!")
			return False

		# If we're not connected, attempt to connect the socket.
		if not self.connected:
			log.debug("Connecting...")
			self.socket.connect(self.address)
			self.connected = True
		else:
			log.debug("Socket is already connected!")

		self._iThread.start()
		self._oThread.start()

		return True

	def _stopping(self):
		# Check the socket hasn't already been disconnected by another thread.
		if not self.connected:
			log.debug("The instance is already disconnected.")
			return False

		# Reflect the disconnection
		log.debug("Setting connected = False")
		self.connected = False
		return True

	def _stopped(self):
		# Notify the delegate of the socket's disconnection.
		if self.delegate and hasattr(self.delegate, "clientDisconnected"):
			self.delegate.clientDisconnected(self)
		else:
			log.debug("Unsupported delegate (clientDisconnected).")
		return True

	def __str__(self):
		return "Client (" + object.__str__(self) + ")"

	def __init__(self, address, sock=None):
		SocketWrapper.__init__(self, address, sock)

		# We'll assume a socket is already connected if one was passed.
		self.connected = True if sock else False

		# Prepare threads for concurrent operations.
		self._iThread = threading.Thread(target=self._iHandler)
		self._oThread = threading.Thread(target=self._oHandler)

		# Threads must be configured as daemons so they're automoatically.
		# killed when the main thread is completed.
		self._iThread.setDaemon(True)
		self._oThread.setDaemon(True)

		self._oQueue = Queue.Queue()

		if self.connected:
			self._iThread.start()
			self._oThread.start()


class Server(SocketWrapper):
	def accept(self):
		if not self._acceptThread.is_alive():
			log.debug("Thread unavailable (blocking-accept used)!")
			return self.socket.accept()

		log.debug("Starting accepting thread.")

		while self.accepting and self.socket:
			log.debug("Thread is waiting for clients (accept).")
			(sock, address) = self.socket.accept()

			log.debug("Accepted client with IP " + str(address[0]) + ".")
			self._lock.acquire()

			if self.delegate and hasattr(self.delegate, "serverFoundClient"):
				self.delegate.serverFoundClient(self, Client(address, sock))
			else:
				log.debug("Unsupported delegate (serverFoundClient).")

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

		log.debug("Will now listen for connections.")

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
		SocketWrapper.__init__(self, address, sock)

		self.accepting = sock is not None

		self._lock = threading.Lock()
		self._acceptThread = threading.Thread(target=self.accept)
		self._acceptThread.setDaemon(True)

		if self.accepting:
			self._acceptThread.start()
