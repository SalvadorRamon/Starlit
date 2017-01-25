'''
Created on Apr 27, 2016

@author: matiasbarcenas
'''

import time, threading, Queue
import networking


class Client(object):
	'''
	classdocs
	'''
	TicksPerSecond = 30

	def start(self):
		self._clientRunning = True
		self._clientLink.start()
		self._clientUpdatesThread.start()

	def stop(self):
		self._clientRunning = False
		self._clientLink.stop()

	def update(self, package, sender=None):
		pass

	def updates(self):
		return networking.Package()

	def _clientUpdateServer(self):
		while self._clientRunning:
			self._clientPrepareUpdates()

			while not self._clientServerUpdates.empty():
				package = self._clientServerUpdates.get()

				if package.content:
					self._clientLink.send(package.data)

			# Keep the divisor as a float, otherwise it'll do int division
			time.sleep(1.0 / Client.TicksPerSecond)

	def _clientPrepareUpdates(self):
		pass

	def _clientReceivedData(self, client, data):
		# print("({0}) Client received update".format(time.ctime()))
		self.update(networking.Package(data), client)

	def _clientDisconnected(self, client):
		print("({0}) Disconnected from world!".format(time.ctime()))

	def __init__(self, address):
		'''
		Constructor
		'''

		self._clientLink = networking.Client(address)
		self._clientLink.setDelegate(self)

		# This queue is used to store package updates
		self._clientServerUpdates = Queue.Queue()

		self._clientUpdatesThread = threading.Thread(target=self._clientUpdateServer)
		self._clientUpdatesThread.setDaemon(True)
