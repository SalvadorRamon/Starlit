'''
Created on May 3, 2016

@author: matiasbarcenas
'''

import struct
from entity import Entity


class Movable(Entity):
	'''
	classdocs
	'''

	@property
	def position(self):
		return self._atomicProtectedGet("position")

	@position.setter
	def position(self, newValue):
		self._atomicProtectedSet("position", newValue)

	@property
	def direction(self):
		return self._atomicProtectedGet("direction")

	@direction.setter
	def direction(self, newValue):
		self._atomicProtectedSet("direction", newValue)

	@property
	def speed(self):
		return self._atomicProtectedGet("speed")

	@speed.setter
	def speed(self, newValue):
		self._atomicProtectedSet("speed", newValue)

	def __init__(self, config=None):
		'''
		Constructor
		'''
		Entity.__init__(self, config)

		self._atomicPropertyRegister("position", (0, 0, 0), \
		                             lambda value: struct.pack("fff", value[0], value[1], value[2]), \
		                             lambda content: struct.unpack("fff", content))
		self._atomicPropertyRegister("direction", (0, 0, 0), \
		                             lambda value: struct.pack("fff", value[0], value[1], value[2]), \
		                             lambda content: struct.unpack("fff", content))
		self._atomicPropertyRegister("speed", 0, \
		                             lambda value: struct.pack("B", value), \
		                             lambda content: struct.unpack("B", content)[0])
