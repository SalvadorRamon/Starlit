'''
Created on Apr 22, 2016

@author: matiasbarcenas
'''
from movable import Movable


class Model(Movable):
	'''
	classdocs
	'''

	def _atomicPropertyDidChange(self, identifier, oldValue, newValue):
		Movable._atomicPropertyDidChange(self, identifier, oldValue, newValue)

		if not self.model: return

		if identifier == "position":
			self._modelUpdatePosition(newValue)
		elif identifier == "direction":
			self._modelUpdateDirection(newValue)

	def _modelUpdatePosition(self, position):
		if not self._modelUpdate["position"]: return
		if "position" in self._modelOffset:
			position = tuple(v + n for v, n in zip(position, self._modelOffset["position"]))
		
		if "position" in self._modelAxis:
			position = tuple(v * n for v, n in zip(position, self._modelAxis["position"]))

		self.model.setPos(position)

	def _modelUpdateDirection(self, direction):
		if not self._modelUpdate["direction"]: return
		if "direction" in self._modelOffset:
			direction = tuple(v + n for v, n in zip(direction, self._modelOffset["direction"]))
			
		if "direction" in self._modelAxis:
			direction = tuple(v * n for v, n in zip(direction, self._modelAxis["direction"]))

		self.model.setHpr(direction)

	def configureUpdate(self, update):
		for updateType in self._modelUpdate:
			if updateType in update:
				self._modelUpdate[updateType] = update[updateType]

	def __init__(self, config, model=None):
		'''
		Constructor
		'''
		Movable.__init__(self, config)

		self.model = model
		self.modelExtra = dict()
		self._modelOffset = {}
		self._modelAxis = {}
		self._modelUpdate = {"position": True, "direction": True}
