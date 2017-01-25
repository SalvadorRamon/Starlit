'''
Created on Apr 23, 2016

@author: Matias
'''

import logging, threading, struct, Queue
from networking import SocketWrapper

# logging.basicConfig(level = logging.DEBUG)
log = logging.getLogger(__name__)


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

		log.debug("oQueue has {0} items(s).".format(self._oQueue.qsize()))

		return True

	def receiveBytes(self, total):
		data = ""
		while len(data) < total:
			log.debug("Waiting to receive data.")
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
		log.debug("Attempting to receive {0} bytes of data.".format(total + Client.MetaLength))

		payload = self.receiveBytes(total)

		if not isinstance(payload, str):
			log.debug("Failed to receive payload!")
			self.stop()
			return None
		else:
			log.debug("Received all {0} bytes of data.".format(total + Client.MetaLength))

		return payload

	def _iHandler(self):
		while self.connected:
			data = self.receive()
			if not isinstance(data, str): break
			# Notify the delegate of the socket's disconnection.
			if self.delegate and hasattr(self.delegate, "_clientReceivedData"):
				self.delegate._clientReceivedData(self, data)
			else:
				log.debug("Unsupported delegate (_clientReceivedData).")
		log.debug("Stopping input handler.")

	def _oHandler(self):
		while self.connected:
			data = Client.Pack(self._oQueue.get())
			log.debug("Attempting to send " + str(len(data)) + " bytes.")
			try:
				self.socket.sendall(data)
			except:
				break
			log.debug("Sent all " + str(len(data)) + " bytes.")
		log.debug("Stopping output handler.")

	def _started(self):
		if not self.socket:
			log.debug("Aborting _started method!")
			return False

		# If we're not connected, attempt to connect the socket.
		if not self.connected:
			log.info("Connecting...")
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
		log.info("Disconnected...")
		self.connected = False
		return True

	def _stopped(self):
		# Notify the delegate of the socket's disconnection.
		if self.delegate and hasattr(self.delegate, "_clientDisconnected"):
			self.delegate._clientDisconnected(self)
		else:
			log.debug("Unsupported delegate (_clientDisconnected).")
		return True

	# def __del__(self):
	#    print("Deleted client...")

	def __str__(self):
		return "Client (" + object.__str__(self) + ")"

	def __init__(self, address, sock=None):
		'''
		Constructor
		'''
		SocketWrapper.__init__(self, address, sock)

		# We'll assume a socket is already connected if one was passed.
		self.connected = True if sock else False

		# Prepare threads for concurrent operations.
		self._iThread = threading.Thread(target=self._iHandler)
		self._oThread = threading.Thread(target=self._oHandler)

		# Threads must be configured as daemons so they're automatically.
		# killed when the main thread is completed.
		self._iThread.setDaemon(True)
		self._oThread.setDaemon(True)

		self._oQueue = Queue.Queue()

		if self.connected:
			self._iThread.start()
			self._oThread.start()
