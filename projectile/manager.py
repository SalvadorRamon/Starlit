'''
Created on May 5, 2016

@author: matiasbarcenas
'''

import time, threading, math
from utilities import Vector
from entity import Entity
import universal


class Manager(universal.Manager):
	'''
	classdocs
	'''

	StartOffset = 2
	QuantityLimit = 100
	GlobalTimeout = 0.5

	TicksPerSecond = 30

	HitRadius = 1.5

	def updates(self):
		with self._updatesLock:
			return universal.Manager.updates(self)

	def spawnFromMovable(self, movable, config=None):
		with self._updatesLock:
			projectile = self.loadEntity((self._projectileID, movable))

			(yaw, pitch) = movable.direction[:2]

			radYaw, radPitch = math.radians(yaw), math.radians(pitch)
			x = -math.sin(radYaw) * math.cos(radPitch)
			y = math.cos(radYaw) * math.cos(radPitch)
			z = math.sin(radPitch)

			direction = Vector((x, y, z))
			position = Vector(movable.position)

			projectile.direction = direction.component()
			startPosition = position + direction * Manager.StartOffset
			projectile.position = startPosition.component()

			# Skip zero, otherwise the ID will be the ID of movable's owner
			self._projectileID += 1 if self._projectileID <= Manager.QuantityLimit else -(Manager.QuantityLimit - 1)

	def addShooter(self, shooter):
		with self._shooterLock:
			self._shooters.add(shooter)
			self._timeout[shooter] = 0

	def removeShooter(self, shooter):
		with self._shooterLock:
			self._shooters.discard(shooter)
			del self._timeout[shooter]

	def _managerProjectileUpdater(self):
		finishedProjectiles = list()

		lastTime = time.time()
		currentTime = time.time()

		while self._managerProjectileUpdaterRunning:

			lastTime = currentTime
			currentTime = time.time()

			# Spawn new projectiles if possible
			with self._shooterLock:
				for shooter in self._shooters:
					if shooter.shooting and self._timeout[shooter] <= currentTime:
						self.spawnFromMovable(shooter)
						self._timeout[shooter] = currentTime + Manager.GlobalTimeout

			# Process projectiles already being managed
			with self._managerEntitiesLock:
				for projectileID in self._managerEntities:
					projectile = self._managerEntities[projectileID]

					if projectile.distance <= 0:
						# Uncomment line below to reveal bug
						# print("Sending projectile {0} unload command.".format(projectileID))
						finishedProjectiles.append((projectileID, projectile.owner))
						continue

					projectilePosition = Vector(projectile.position)
					projectileDirection = Vector(projectile.direction)
					projectileDistance = (currentTime - lastTime) * projectile.speed
					projectileDestination = projectilePosition + projectileDirection * projectileDistance

					# Check for projectile hits
					with self._shooterLock:
						for shooter in self._shooters:
							targetPosition = Vector(shooter.position)
							distanceToTargetVector = projectilePosition - targetPosition
							distanceToTarget = distanceToTargetVector.magnitude()

							# Check if the projectile wont make it to the player and stop calculating
							if distanceToTarget > projectileDistance: continue
							# if distanceToTarget <= Manager.HitRadius:

							projectileProjection = projectileDirection * distanceToTarget
							projectileInterval = projectilePosition + projectileProjection

							projectileTargetDifference = projectileInterval - targetPosition

							if projectileTargetDifference.magnitude() <= Manager.HitRadius:
								if self.delegate and hasattr(self.delegate, "_projectileManagerDetectedHit"):
									if not self.delegate._projectileManagerDetectedHit(self, projectile, shooter):
										continue

								finishedProjectiles.append((projectileID, projectile.owner))
								break

					# Update the projectile's position
					projectile.position = projectileDestination.component()
					projectile.distance -= projectileDistance

					projectile.updatesSingle("direction")

			for projectileMeta in finishedProjectiles:
				self.unloadEntity(projectileMeta)

			del finishedProjectiles[:]  # Remove all of them
			# finishedProjectiles.clear()

			# Keep the divisor as a float, otherwise it'll do int division
			time.sleep(1.0 / Manager.TicksPerSecond)

	# ================================================================
	# Entity Delegation
	# ================================================================
	def _entityPropertyWillChange(self, entity, identifier, oldValue, newValue):
		universal.Manager._atomicPropertyWillChange(self, entity, identifier, oldValue, newValue)

	def _entityPropertyDidChange(self, entity, identifier, oldValue, newValue):
		universal.Manager._atomicPropertyDidChange(self, entity, identifier, oldValue, newValue)

	def __del__(self):
		self._managerProjectileUpdaterRunning = False

	def __init__(self, shooters=None):
		'''
		Constructor
		'''
		universal.Manager.__init__(self, Entity)

		self.delegate = None

		self._shooters = set(shooters or ())
		self._timeout = {}

		self._projectileID = 1

		self._updatesLock = threading.Lock()
		self._shooterLock = threading.Lock()

		self._managerProjectileUpdaterThread = threading.Thread(target=self._managerProjectileUpdater)
		self._managerProjectileUpdaterThread.setDaemon(True)
		self._managerProjectileUpdaterRunning = True
		self._managerProjectileUpdaterThread.start()
