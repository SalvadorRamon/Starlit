'''
Created on Apr 28, 2016

@author: matiasbarcenas
'''

import time, threading, Queue
import networking


class Server(object):
	'''
	classdocs
	'''
	DefaultAddress = ("", 5000)
	TicksPerSecond = 30

	def start(self):
		self._serverRunning = True
		self._serverLink.start()
		self._serverUpdatesThread.start()

	def stop(self):
		self._serverRunning = False
		self._serverLink.stop()

		# Disconnect all clients
		for client in self._serverClients:
			client.stop()

	def update(self, package, sender=None):
		# By default, the server is a relay server, repeating
		# every package sent to it directly to the clients.
		# In other words, to use it, override the update method.
		self._serverClientUpdates.put((package, sender))

	def updates(self):
		updatesData = ""

		while not self._serverClientUpdates.empty():
			update = self._serverClientUpdates.get()
			package = update[0]
			updatesData += package.data

		return networking.Package(updatesData)

	def _serverUpdateClients(self):
		while self._serverRunning:
			self._serverPrepareUpdates()

			while not self._serverClientUpdates.empty():
				# Get pops the elements from the queue
				# The queue is thread-safe
				(package, sender) = self._serverClientUpdates.get()

				for client in self._serverClients:

					# Skip sending the update to the one who sent the update
					if sender is client: continue
					client.send(package.data)

			# Keep the divisor as a float, otherwise it'll do int division
			time.sleep(1.0 / Server.TicksPerSecond)

	def _serverPrepareUpdates(self):
		pass

	# ================================================================
	# Server Delegation
	# ================================================================
	def _serverFoundClient(self, server, client):
		self._serverClients.add(client)
		client.setDelegate(self)
		print("({0}) Serving client at {1}...".format(time.ctime(), str(client.host())))

	# ================================================================
	# Client Delegation
	# ================================================================
	def _clientReceivedData(self, client, data):
		self.update(networking.Package(data), client)

	def _clientDisconnected(self, client):
		self._serverClients.remove(client)
		print("({0}) Client disconnected from {1}...".format(time.ctime(), str(client.host())))

	def __init__(self, address=DefaultAddress):
		'''
		Constructor
		'''

		self._serverLink = networking.Server(address)
		self._serverLink.setDelegate(self)

		self._serverClients = set()

		# This queue is used to store package-owner update tuples
		self._serverClientUpdates = Queue.Queue()

		self._serverUpdatesThread = threading.Thread(target=self._serverUpdateClients)
		self._serverUpdatesThread.setDaemon(True)

		self._serverRunning = False
