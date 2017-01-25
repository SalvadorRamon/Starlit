'''
Created on Apr 26, 2016

@author: matiasbarcenas
'''


class Interface(object):
	'''
	classdocs
	'''

	@property
	def throttle(self):
		return self._throttle

	@throttle.setter
	def throttle(self, newValue):
		pass

	@property
	def health(self):
		return self._health

	@health.setter
	def health(self, newValue):
		pass

	@staticmethod
	def Config(reticle):
		pass

	def __init__(self, confi):
		'''
		Constructor
		'''
		pass
