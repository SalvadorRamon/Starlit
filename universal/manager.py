'''
Created on Apr 21, 2016

@author: matiasbarcenas
'''

import threading, struct
from entity import Entity
from networking import Package


class Manager(object):
	'''
	classdocs
	'''
	UpdateEntity = 0
	UnloadEntity = 1
	LoadEntity = 2

	# There's a bug where things always appear at coordinates (0, 0) before jumping
	# to the correct coordinates because no information for updating that is
	# available, mainly because none of that information is sent with the load command.
	def update(self, package, sender=None):
		for update in package.contents:
			if update.identifier == Manager.UpdateEntity:
				self._managerProcessUpdateEntity(Package(update.content), sender)

			elif update.identifier == Manager.LoadEntity:
				identity = struct.unpack("P", update.content)[0]
				self.loadEntity((identity, sender))

			elif update.identifier == Manager.UnloadEntity:
				identity = struct.unpack("P", update.content)[0]
				self.unloadEntity((identity, sender))

			else:
				print("Invalid manager package with ID " + str(package.identifier))

	def updates(self):
		updates = Package()

		with self._managerLoadersLock:
			for entityID in self._managerLoadedEntities:
				updates += Package(Manager.LoadEntity, struct.pack("P", entityID))

			self._managerLoadedEntities.clear()

			for entityID in self._managerUnloadedEntities:
				updates += Package(Manager.UnloadEntity, struct.pack("P", entityID))

			self._managerUnloadedEntities.clear()

		with self._managerEntitiesLock:
			for entityID in self._managerEntities:
				entity = self._managerEntities[entityID]
				entityUpdatesPackage = entity.updates()
				if not entityUpdatesPackage.content: continue
				# print("Packed update for ID {0}.".format(entityID))
				entityPackage = Package(entityID, entityUpdatesPackage)
				updates += Package(Manager.UpdateEntity, entityPackage)

		return updates

	def updatesAll(self):
		with self._managerLoadersLock:
			with self._managerEntitiesLock:
				for identity in self._managerEntities:
					self._managerLoadedEntities.add(identity)
					self._managerEntities[identity].updatesAll()

	def select(self, config):
		(identity, owner) = config if isinstance(config, tuple) else (config, None)
		
		with self._managerEntitiesLock:
			# Check the entity hasn't already been loaded.
			if identity not in self._managerEntities:
				#print("select: Entity with ID {0} does not exists.".format(identity))
				return None
			
			# Select the entity	
			entity = self._managerEntities[identity]
			
			# Check for proper ownership, reject if not an owner.
			if entity.owner and not entity.isOwnedBy(owner):
				raise Exception("Foreign owner attempted high-jacking entity! FUCK YOU!")
		
		return entity

	# Takes a configuration of the following form:
	# config ::= EntityID | ( EntityID, Owner ) 
	def loadEntity(self, config):
		(identity, owner) = config if isinstance(config, tuple) else (config, None)
		#print("Load: Attempting to load entity with ID {0}.".format(identity))

		with self._managerEntitiesLock:
			# Check the entity hasn't already been loaded.
			entity = self.select(config)
			
			if entity: return self.select(config)#raise Exception("Attempted to load an entity that's already been loaded.")
			
			entity = self.NewEntityType((identity, owner))
			entity.delegate = self

			self._managerEntities[identity] = entity

			#print("Manager loaded entity with ID {0}.".format(identity))
			#print("\tManager contains {0} entities.".format(len(self._managerEntities)))
			
			if self.delegate and hasattr(self.delegate, "_managerLoadedEntity"):
				self.delegate._managerLoadedEntity(self, entity)

		with self._managerLoadersLock:
			self._managerLoadedEntities.add(identity)

			return entity

	def unloadEntity(self, config):
		identity = config[0] if isinstance(config, tuple) else config
		#print("Unload: Attempting to unload entity with ID {0}.".format(identity))

		with self._managerEntitiesLock:
			# If the owner can select the entity, it can do anything to it.
			entity = self.select(config)
			
			if not entity: return #raise Exception("Failed to unload entity with ID {0}, does not exist.".format(identity))
		
			del self._managerEntities[identity]
			
			#print("Manager unloaded entity with ID {0}.".format(identity))
			#print("\tManager contains {0} entities.".format(len(self._managerEntities)))
			
			if self.delegate and hasattr(self.delegate, "_managerUnloadedEntity"):
				self.delegate._managerUnloadedEntity(self, entity)

		with self._managerLoadersLock:
			self._managerUnloadedEntities.add(identity)

	def _managerProcessUpdateEntity(self, package, sender):
		entity = self.select((package.identifier, sender))

		if not entity: return #raise Exception("Entity with ID {0} does not exist!".format(package.identifier))
		
		# Load the received data into the entity
		entity.update(Package(package.content))
	
	# ================================================================
	# Entity Delegation
	# ================================================================
	def _atomicPropertyWillChange(self, entity, identifier, oldValue, newValue):
		if self.delegate and hasattr(self.delegate, "_managerWillUpdateEntity"):
			self.delegate._managerWillUpdateEntity(self, entity, identifier, oldValue, newValue)

	def _atomicPropertyDidChange(self, entity, identifier, oldValue, newValue):
		if self.delegate and hasattr(self.delegate, "_managerDidUpdateEntity"):
			self.delegate._managerDidUpdateEntity(self, entity, identifier, oldValue, newValue)

	def __init__(self, newEntityType=Entity):
		'''
		Constructor
		'''
		self.delegate = None

		self.NewEntityType = newEntityType

		self._managerEntitiesLock = threading.RLock();
		self._managerEntities = {}

		self._managerLoadersLock = threading.Lock();
		self._managerLoadedEntities = set()
		self._managerUnloadedEntities = set()
