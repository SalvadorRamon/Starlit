import networking, asyncore, sys, struct
import threading, time

NetUpdate = 0.03


class RelayServer(object):
	def serverFoundClient(self, server, client):
		with self._cLock:
			if None in self.clients:
				i = self.clients.index(None)
				self.clients[i] = client
				self.clientData[i] = False
			else:
				self.clients.append(client)
				self.clientData.append(False)

			client.setDelegate(self)
			print("Serving client at " + str(client.host()) + "...")

	def clientReceivedData(self, client, data):
		v = struct.unpack("iffff?", data)

		with self._cLock:
			if v[0] == 0:  # Client is requesting ID
				position = self.clients.index(client)
				client.send(struct.pack("iffff?", 0, position + 1.5, 0, 0, 0, False))
			else:
				self.clientData[v[0] - 1] = data

	def clientDisconnected(self, client):
		with self._cLock:
			position = self.clients.index(client)

			self.clients[position] = None
			self.clientData[position] = None

			# Relay the data to every client first
			for aClient in self.clients:
				if not aClient: continue
				aClient.send(struct.pack("iffff?", 0, position + 1.5, 0, 0, 0, True))

		print(str(client) + " disconnected...")

	def clientUpdate(self):
		while self.updating:
			with self._cLock:
				for x in range(len(self.clients)):
					if not self.clients[x]: continue
					for y in range(len(self.clients)):
						if not self.clients[y]: continue
						if x == y or not self.clientData[y]: continue
						self.clients[x].send(self.clientData[y])
			time.sleep(NetUpdate)

	def start(self):
		self.updating = True

		self.server.start()
		self._updaterThread.start()

	def stop(self):
		for aClient in self.clients:
			aClient.stop()

		self.updating = False
		self.server.stop()

	def __init__(self):
		object.__init__(self)

		ip = sys.argv[1] if len(sys.argv) > 1 else ""
		port = sys.argv[2] if len(sys.argv) > 2 else 5000
		print("Using port " + str(port))
		self.server = networking.Server((ip, port))
		self.server.setDelegate(self)
		self.clients = list()
		self.clientData = list()

		self._updaterThread = threading.Thread(target=self.clientUpdate)
		self._updaterThread.setDaemon(True)

		self._cLock = threading.Lock()


def run():
	relay = RelayServer()
	relay.start()

	print("Starting relay server...")

	while True:
		outboundData = raw_input()

		if outboundData in ("quit", "exit"):
			break

		if not relay.clients:
			print("No clients, skipping...")
			continue

		for aClient in relay.clients:
			if not aClient.send(outboundData):
				print("Failed to send data to " + str(aClient))

	relay.stop()
	print("Terminating...")


run()
