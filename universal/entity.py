'''
Created on May 3, 2016

@author: matiasbarcenas
'''

import struct
from atomic import Atomic


class Entity(Atomic):
	'''
	classdocs
	'''

	@property
	def identity(self):
		return self._atomicProtectedGet("identity")

	@identity.setter
	def identity(self, newValue):
		self._atomicProtectedSet("identity", newValue)

	@property
	def condition(self):
		return self._atomicProtectedGet("condition")

	@condition.setter
	def condition(self, newValue):
		self._atomicProtectedSet("condition", newValue)
		
	@property
	def owner(self):
		return self._atomicProtectedGet("owner")

	@owner.setter
	def owner(self, newValue):
		self._atomicProtectedSet("owner", newValue)
		
	def isOwnedBy(self, owner):
		if not hasattr(owner, '__iter__'):
			return owner in self.owner
		
		for anOwner in owner:
			if anOwner in self.owner: return True
			
		return False
	
	def addOwner(self, owner):
		currentOwners = set(self.owner)
		newOwners = set(owner if isinstance(owner, tuple) else (owner,))
		self.owner = currentOwners | newOwners
		
	def removeOwner(self, owner):
		owners = set(self.owner)
		self.owner = owners - owner
		
	def singleOwner(self, ownerType = None):
		for owner in self.owner:
			if isinstance(owner, ownerType or Entity):
				return owner

	# Takes a tuple (identifier, owner) or just identifier
	def __init__(self, config=None):
		'''
		Constructor
		'''
		Atomic.__init__(self)

		identifier = config[0] if isinstance(config, tuple) else config
		owner = config[1] if isinstance(config, tuple) else None

		# For delegation pattern
		self.delegate = None

		# Register properties
		self._atomicPropertyRegister("identity", identifier, \
		                             lambda value: struct.pack("P", value), \
		                             lambda content: struct.unpack("P", content)[0])
		self._atomicPropertyRegister("condition", 100, \
		                             lambda value: struct.pack("B", value), \
		                             lambda content: struct.unpack("B", content)[0])
		# For object ownership
		owner = owner if owner else ()
		owner = owner if isinstance(owner, tuple) else (owner,)
		self._atomicPropertyRegister("owner", set(owner), \
		                             lambda value: struct.pack("P", id(value)), \
		                             lambda content: struct.unpack("P", content)[0])

		self.updatesIgnoreProperty("owner")