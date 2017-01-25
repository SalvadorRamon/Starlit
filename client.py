'''
Created on Apr 27, 2016

@author: matiasbarcenas
'''

import time, struct
from utilities import extra
from networking import Package
from universal import Client, Manager
from universe import Universe
import ship
import projectile
#from panda3d.core import TextureStage

# import item


NetworkAddress = ("192.168.10.22", 5000)

PANDA3D_CAPABLE = True


class StarlitClient(Client):
	'''
	classdocs
	'''
	UpdateMeta = 0
	UpdatePlayer = 1
	UpdateProjectile = 2
	UpdateItem = 3
	UpdateDeath = 4

	def update(self, package, sender=None):
		if package.identifier == StarlitClient.UpdateMeta:
			self._identity = struct.unpack("P", package.content)[0]
			self.player = self._playerManager.loadEntity((self._identity, (self, self._clientLink)))
			print("Server updated this client's identification to {0}.".format(self._identity))

		elif package.identifier == StarlitClient.UpdatePlayer:
			self._playerManager.update(Package(package.content), sender)

		elif package.identifier == StarlitClient.UpdateProjectile:
			self._projectileManager.update(Package(package.content), sender)
			
		elif package.identifier == StarlitClient.UpdateDeath:
			deathIdentity = struct.unpack("P", package.content)[0]
			print("Looks like some jackass died...")
			if deathIdentity == self._identity:
				print("Shit, it was me!?..")
				self.universe.respawn(message = "You were killed in action!")
		
		else:
			print("Invalid Starlit Package!")

	def _clientPrepareUpdates(self):
		if not self.player: return
		
		playerUpdates = self.player.updates()
		
		if playerUpdates.content:
			entityUpdates = Package(self.player.identity, playerUpdates.data)
			managerUpdates = Package(Manager.UpdateEntity, entityUpdates.data)
			serverUpdates = Package(StarlitClient.UpdatePlayer, managerUpdates)
			self._clientServerUpdates.put(serverUpdates)

	# ================================================================
	# Manager Delegation
	# ================================================================
	def _managerLoadedEntity(self, manager, entity):
		if manager is self._playerManager:
			if not self.player or entity is self.player: return
			
			if not PANDA3D_CAPABLE:
				print("Loaded player with ID " + str(entity.identity))
				return
			
			print("Loading enemy ship into the world")
			ship = self.universe.loader.loadModel("models/spaceship/mk2.egg")
			shipTexture = self.universe.loader.loadTexture("models/spaceship/mk2-texture-2.jpg")
			#ts = TextureStage("models/spaceship/mk2-texture-1.jpg")
			#ts.setMode(TextureStage.MModulateGlow)
			ship.reparentTo(self.universe.render)
			ship.setScale((0.25, 0.25, 0.25))
			#ship.setTexture(ts, shipTexture)
			ship.setTexture(shipTexture)
			entity.model = ship
			
			health = self.universe.loader.loadModel("models/weapon/ball.egg")
			health.reparentTo(entity.model)
			health.setColor(1,1,1,0.75)
			health.setScale((5, 5, 5))
			health.setPos((0, 0, 25))
			entity.modelExtra["health"] = health

		elif manager is self._projectileManager:
			if not PANDA3D_CAPABLE:
				print("Loaded projectile with ID " + str(entity.identity))
				return
				
			projectile = self.universe.loader.loadModel("models/weapon/projectile-laser.egg")
			projectileTexture = self.universe.loader.loadTexture("models/weapon/projectile-laser-texture-1.jpg")
			projectile.reparentTo(self.universe.render)
			projectile.setScale((5, 5, 5))
			projectile.setTexture(projectileTexture)
			entity.model = projectile

	def _managerUnloadedEntity(self, manager, entity):
		if not PANDA3D_CAPABLE:
			print("Removed entity with ID " + str(entity.identity))
			return
			
		# Same behavior for all managers
		self.universe.unloadModelEntity(entity)

	def _managerDidUpdateEntity(self, manager, entity, identifier, oldValue, newValue):
		if manager is self._playerManager:
			if entity is self.player:
				if identifier == "rank":
					self.universe.setHUDRank(newValue + 1)
				if identifier == "condition":
					self.universe.setHUDHealth(newValue)
				elif identifier in ("score", "condition", "speed", "rank", "phase"):
					print("Property '{0}' is now {1}...".format(identifier, newValue))
			else:
				if identifier == "condition":
					red = (100 - entity.condition) / 100.0
					green = (entity.condition) / 100.0
					entity.modelExtra["health"].setColor(red, green, 0, 0.75)
					
				entity.updatesClear()
				

		if manager is self._projectileManager:
			if identifier == "direction":
				entity.configureUpdate({"direction": False})
				angle = extra.AnglesFromVector3D(newValue)
				entity.model.setHpr((angle[0], angle[1] - 90, angle[2]))

	# ================================================================
	# Universe Delegation
	# ================================================================
	def _universeFrameUpdate(self):
		if not self.player or not PANDA3D_CAPABLE: return

		
		#if not self.player.alive():
		#	self.universe.respawn(message = "You were KIA!")

		# Update player
		self.player.direction = tuple(self.universe.camera.getHpr())
		self.player.position = tuple(self.universe.camera.getPos())
		self.player.shooting = self.universe.mouse["left"]
		self.player.throttle += (self.universe.keys["w"] - self.universe.keys["s"])

	def __init__(self, address=None):
		'''
		Constructor
		'''
		Client.__init__(self, address)

		if PANDA3D_CAPABLE: self.universe = Universe()
		if PANDA3D_CAPABLE: self.universe.delegate = self

		# The like of code below is required to prevent the delegate
		# handler from crashing the program.
		self.player = None

		self._playerManager = Manager(ship.Entity)
		self._playerManager.delegate = self

		self._projectileManager = Manager(projectile.Entity)
		self._projectileManager.delegate = self
		


client = StarlitClient(NetworkAddress)
print("({0}) Starting Starlit Client...".format(time.ctime()))
client.start()
if PANDA3D_CAPABLE: client.universe.run()

if not PANDA3D_CAPABLE:
	while True:
		print("Trigger action (y)? ")
		command = raw_input()
		client.player.phase += 1 if command == 'y' else 0
		print("Phase is now {0}.".format(client.player.phase))
		time.sleep(1)
