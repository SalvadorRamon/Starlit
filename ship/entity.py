'''
Created on Apr 23, 2016

@author: Matias
'''

import struct
import player


# from interface import Interface


class Entity(player.Competitor):
	'''
	classdocs
	'''
	DefaultPlayer = None  # "ship-1.egg"
	DefaultSpeed = 10
	DefaultScale = 1
	DefaultHUD = None  # Interface()

	LimitThrottle = 100

	@property
	def shooting(self):
		return self._atomicProtectedGet("shooting")

	@shooting.setter
	def shooting(self, newValue):
		self._atomicProtectedSet("shooting", newValue)

	@property
	def phase(self):
		return self._atomicProtectedGet("phase")

	@phase.setter
	def phase(self, newValue):
		self._atomicProtectedSet("phase", newValue)

	@property
	def throttle(self):
		return self._atomicProtectedGet("throttle")

	@throttle.setter
	def throttle(self, newValue):
		if newValue < 0: newValue = 0
		if newValue > Entity.LimitThrottle: newValue = Entity.LimitThrottle
		self._atomicProtectedSet("throttle", newValue)

	'''
	def explode(self):
		self._entityPropertyWillChange("explode", False, True)
		self.health = 0
		self._entityPropertyDidChange("explode", False, True)

	def forward(self):
		self._entityPropertyWillChange("forward", False, True)
		self.position += self.direction * self.speed
		self._entityPropertyDidChange("forward", False, True)

	def backward(self):
		self._entityPropertyWillChange("backward", False, True)
		self.position -= self.direction * self.speed
		self._entityPropertyDidChange("backward", False, True)
	'''

	@staticmethod
	def Config(model=None, speed=None, hud=None):  # , scale = None):
		config = {}
		config["model"] = model or Entity.Defaultplayer.Entity
		config["speed"] = speed or Entity.DefaultSpeed
		# config["scale"] = scale or Entity.DefaultScale
		config["hud"] = hud or Entity.DefaultHUD

		return config

	def __init__(self, config):  # , config = Entity.Config()):
		'''
		Constructor
		'''
		player.Competitor.__init__(self, config)

		# self.model = config["model"]
		# self.speed = config["speed"] # distance / time
		# self.scale = config["scale"]
		# self.hud = config["hud"]

		self._atomicPropertyRegister("shooting", False, \
		                             lambda value: struct.pack("?", value), \
		                             lambda content: struct.unpack("?", content)[0])
		self._atomicPropertyRegister("phase", 0, \
		                             lambda value: struct.pack("B", value), \
		                             lambda content: struct.unpack("B", content)[0])
		self._atomicPropertyRegister("throttle", 0, \
		                             lambda value: struct.pack("B", value), \
		                             lambda content: struct.unpack("B", content)[0])

		self._modelOffset["direction"] = (180, 0, 0)
		self._modelAxis["direction"] = (1, -1, -1)