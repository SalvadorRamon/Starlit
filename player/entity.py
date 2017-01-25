'''
Created on Apr 21, 2016

@author: matiasbarcenas
'''

from universal import Model


class Entity(Model):
	'''
	classdocs
	'''

	@property
	def name(self):
		return self._atomicProtectedGet("name")

	@name.setter
	def name(self, newValue):
		self._atomicProtectedSet("name", newValue)

	def alive(self):
		return self.condition > 0

	def __eq__(self, other):
		if isinstance(other, Entity):
			return self.identity == other.identity

		if isinstance(other, int):
			return self.identity == other

		return False

	def __ne__(self, other):
		return not self.__eq__(other)

	def __init__(self, config=None, model=None):
		'''
		Constructor
		'''
		Model.__init__(self, config, model)

		self._atomicPropertyRegister("name", "", \
		                             lambda value: value, \
		                             lambda content: content)
