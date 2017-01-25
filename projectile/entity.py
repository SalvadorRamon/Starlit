'''
Created on May 2, 2016

@author: matiasbarcenas
'''

import struct
from universal import Model


class Entity(Model):
	'''
	classdocs
	'''
	DefaultTypeID = 0
	DefaultDamage = 10
	DefaultSpeed = 100
	DefaultPosition = (0, 0, 0)
	DefaultDirection = (0, 0, 0)
	DefaultDistance = 1000

	@property
	def typeID(self):
		return self._atomicProtectedGet("typeID")

	@typeID.setter
	def typeID(self, newValue):
		self._atomicProtectedSet("typeID", newValue)

	@property
	def distance(self):
		return self._atomicProtectedGet("distance")

	@distance.setter
	def distance(self, newValue):
		self._atomicProtectedSet("distance", newValue)

	@staticmethod
	def Config(typeID=DefaultTypeID,
	           damage=DefaultDamage, \
	           speed=DefaultSpeed, \
	           position=DefaultPosition, \
	           direction=DefaultDirection, \
	           distance=DefaultDistance):
		config = {}
		config["typeID"] = typeID
		config["damage"] = damage
		config["speed"] = speed
		config["position"] = position
		config["direction"] = direction
		config["distance"] = distance

		return config

	def __init__(self, entityConfig, config=None):
		'''
		Constructor
		'''
		Model.__init__(self, entityConfig)

		config = config or Entity.Config()

		self._atomicPropertyRegister("typeID", config["typeID"], \
		                             lambda value: struct.pack("B", value), \
		                             lambda content: struct.unpack("B", content)[0])

		self._atomicPropertyRegister("distance", config["distance"], \
		                             lambda value: struct.pack("i", value), \
		                             lambda content: struct.unpack("i", content)[0])

		self.speed = config["speed"]

		# self._typeID = config["typeID"]
		# self._damage = config["damage"]
		# self._speed = config["speed"]
		# self._position = config["position"]
		# self._direction = config["direction"]
		# self._distance = config["distance"]
