'''
Created on Apr 27, 2016

@author: matiasbarcenas
'''

import time, struct
from networking import Package
from universal import Server
import player
import ship
import projectile

# import item


NetworkAddress = ("", 5000)


class StarlitServer(Server):
	'''
	classdocs
	'''
	UpdateMeta = 0
	UpdatePlayer = 1
	UpdateProjectile = 2
	UpdateItem = 3
	UpdateDeath = 4

	def update(self, package, sender=None):
		# print("{0} Server received update...".format(time.ctime()))
		if package.identifier == StarlitServer.UpdateMeta:
			print("See, this shit should've be printing. If it did, something fucking broke >:/")

		elif package.identifier == StarlitServer.UpdatePlayer:
			self._playerManager.update(Package(package.content), sender)
			self._starlitServerUpdateRelay(StarlitServer.UpdatePlayer, \
										   self._playerManager.updates(), \
										   sender)

		elif package.identifier == StarlitServer.UpdateProjectile:
			self._projectileManager.update(Package(package.content))

		else:
			print("Invalid Starlit Package!")

	def _starlitServerUpdateRelay(self, starlitType, package, sender):
		update = Package(starlitType, package.data)
		self._serverClientUpdates.put((update, sender))

	def _serverFoundClient(self, server, client):
		Server._serverFoundClient(self, server, client)
		
		# Generate an identity for the client
		clientIdentity = id(client)
		
		# Send client its identity
		clientIdentityPackage = Package(StarlitServer.UpdateMeta, struct.pack("P", clientIdentity))
		client.send(clientIdentityPackage.data)

		# Load player for client owned by both the server and the client
		self._playerManager.loadEntity((clientIdentity, (self, client)))

		# Send the current state of everyone (Bugged)
		self._playerManager.updatesAll()

		# Update ranks
		self._playerManager.updateRanks()
		
		print("({0}) [{1}] Player joined the server.".format(time.ctime(), id(client)))

	def _clientDisconnected(self, client):
		Server._clientDisconnected(self, client)
		
		# Retrieve the client's identity
		clientIdentity = id(client)
		
		# Unload the player owned by the client.
		self._playerManager.unloadEntity((clientIdentity, self))
		
		# Update ranks
		self._playerManager.updateRanks()
		
		print("({0}) [{1}] Player left the server.".format(time.ctime(), id(client)))

	def _serverPrepareUpdates(self):
		playerUpdates = self._playerManager.updates()
		if playerUpdates.content:
			self._starlitServerUpdateRelay(StarlitServer.UpdatePlayer, playerUpdates, None)

		projectileUpdates = self._projectileManager.updates()
		if projectileUpdates.content:
			self._starlitServerUpdateRelay(StarlitServer.UpdateProjectile, projectileUpdates, None)

	# ================================================================
	# Manager Delegation
	# ================================================================
	def _managerDidUpdateEntity(self, manager, entity, identifier, oldValue, newValue):
		# print("Updated entity's {0} from {1} to {2}".format(identifier, oldValue, newValue))
		if manager is self._playerManager:
			pass
		#print(manager, identifier)

	def _managerLoadedEntity(self, manager, entity):
		if manager is self._playerManager:
			self._projectileManager.addShooter(entity)

	def _managerUnloadedEntity(self, manager, entity):
		if manager is self._playerManager:
			self._projectileManager.removeShooter(entity)

	def _projectileManagerDetectedHit(self, manager, projectile, victim):
		player = projectile.singleOwner(ship.Entity)
		# Players can only attack other players when they're both alive,
		# and if they're on the same phase in the universe.
		if player.phase != victim.phase:
			print("Players in different phases.")
			return False

		if not player.alive():
			print("Player is dead, can't gain points while dead.")
			return False

		if not victim.alive():
			print("Victim isn't alive, can't collide")
			return False

		if player is victim:
			print("Invalid hit, player's projectiles can't harm itself.")
			return False

		victim.condition -= 10
		player.score += 1
		
		# Update ranks
		self._playerManager.updateRanks()
		
		# Check if player died
		if not victim.alive():
			playerDeath = Package(StarlitServer.UpdateDeath, struct.pack("P", victim.identity))
			self._serverClientUpdates.put((playerDeath, None))
			victim.condition = 100 # Reset health


		print("Player {0} was hit by player {1}! (HP {2})".format(victim.identity, player.identity, victim.condition))
		print("Player {0} has a score of {1}.".format(player.identity, player.score))
		return True

	def __init__(self, address=None):
		Server.__init__(self, address)

		self._playerManager = player.Manager(ship.Entity)
		self._playerManager.delegate = self
		self._projectileManager = projectile.Manager()
		self._projectileManager.delegate = self


def run():
	slServer = StarlitServer(NetworkAddress)
	slServer.start()

	print("({0}) Starting Starlit Server...".format(time.ctime()))
	while True:
		print("Awaiting Command...")
		command = raw_input()

		if command in ("stop", "quit", "exit", "close"):
			break

		if command in ("phase", "p", "shift"):
			for entity in slServer._pHolder:
				entity.phase += 1
				break
			continue

		print("Invalid command...")

	slServer.stop()
	print("Terminating...")


run()
