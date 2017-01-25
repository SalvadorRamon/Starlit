'''
Created on May 7, 2016

@author: matiasbarcenas
'''

import struct
from entity import Entity


class Competitor(Entity):
	'''
	classdocs
	'''

	@property
	def score(self):
		return self._atomicProtectedGet("score")

	@score.setter
	def score(self, newValue):
		self._atomicProtectedSet("score", newValue)
		
	@property
	def rank(self):
		return self._atomicProtectedGet("rank")
		
	@rank.setter
	def rank(self, newValue):
		self._atomicProtectedSet("rank", newValue)

	def __init__(self, config=None, model=None):
		'''
		Constructor
		'''
		Entity.__init__(self, config, model)

		self._atomicPropertyRegister("score", 0, \
		                             lambda value: struct.pack("B", value), \
		                             lambda content: struct.unpack("B", content)[0])
		
		self._atomicPropertyRegister("rank", 100, \
		                             lambda value: struct.pack("B", value), \
		                             lambda content: struct.unpack("B", content)[0])
