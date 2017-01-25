'''
Created on May 7, 2016

@author: matiasbarcenas
'''

import threading
from networking import Package


class Atomic(object):
	'''
	classdocs
	'''

	def updates(self):
		updatePackage = Package()
		with self.__updateLock:
			for identifier in self.__propertyUpdates:
				if identifier in self.__propertyUpdatesIgnored:
					continue
				
				with self.__propertyLock:
					propertyMeta = self.__property[identifier]
					propertyID = propertyMeta["id"]
					value = self._atomicProtectedGet(identifier)
					# print("Making update package for {0}, changed to {1}.".format(identifier, value))
					content = propertyMeta["pack"](value)
					updatePackage += Package(propertyID, content)

			with self.__propertyLock:
				self.__propertyUpdates.clear()
		return updatePackage

	def updatesClear(self):
		with self.__updateLock:
			self.__propertyUpdates.clear()

	def updatesAll(self):
		with self.__updateLock:
			with self.__propertyLock:
				for identifier in self.__property:
					self.__propertyUpdates.add(identifier)

	def updatesSingle(self, identifier):
		with self.__updateLock:
			with self.__propertyLock:
				if identifier in self.__property:
					self.__propertyUpdates.add(identifier)
					# else: print("Not a property '{0}'...".format(identifier))

	def update(self, package):
		with self.__updateLock:
			for package in package.contents:
				with self.__propertyLock:
					if package.identifier in self.__propertyByID:
						# Need the text based identifier, since it's calling the delegate
						atomicProperty = self.__propertyByID[package.identifier]
						identifier = atomicProperty["identifier"]
						
						if identifier in self.__propertyUpdatesIgnored: continue
						
						value = atomicProperty["unpack"](package.content)
						# print("Setting update of {0} to {1}.".format(identifier, value))
						self._atomicProtectedSet(identifier, value)
					else:
						print("Invalid package with ID {0}.".format(package.identifier))
						
	def updatesIgnoreProperty(self, atomicProperty):
		with self.__updateLock:
			self.__propertyUpdatesIgnored.add(atomicProperty)
			
	def updatesUnignoreProperty(self, atomicProperty):
		with self.__updateLock:
			self.__propertyUpdatesIgnored.discard(atomicProperty)

	def _atomicPropertyWillChange(self, identifier, oldValue, newValue):
		if self.delegate and hasattr(self.delegate, "_atomicPropertyWillChange"):
			self.delegate._atomicPropertyWillChange(self, identifier, oldValue, newValue)

	def _atomicPropertyDidChange(self, identifier, oldValue, newValue):
		if self.delegate and hasattr(self.delegate, "_atomicPropertyDidChange"):
			self.delegate._atomicPropertyDidChange(self, identifier, oldValue, newValue)

	def _atomicProtectedGet(self, identifier):
		with self.__propertyLock:
			return self.__property[identifier]["value"]

	def _atomicProtectedSet(self, identifier, newValue, silent = False):
		oldValue = self._atomicProtectedGet(identifier)

		if oldValue != newValue:
			if not silent: self._atomicPropertyWillChange(identifier, oldValue, newValue)
			with self.__propertyLock:
				self.__property[identifier]["value"] = newValue
			with self.__updateLock:
				if not silent: self.__propertyUpdates.add(identifier)
			if not silent: self._atomicPropertyDidChange(identifier, oldValue, newValue)

	def _atomicPropertyRegister(self, identifier, value, compressor, decompressor):
		with self.__propertyLock:
			self.__property[identifier] = dict()

			propertyID = len(self.__property)

			self.__property[identifier]["id"] = propertyID
			self.__property[identifier]["value"] = value
			self.__property[identifier]["pack"] = compressor
			self.__property[identifier]["unpack"] = decompressor
			self.__property[identifier]["identifier"] = identifier

			self.__propertyByID[propertyID] = self.__property[identifier]

	def __init__(self):
		'''
		Constructor
		'''
		# Constant time accessible storage for properties of entity
		self.__property = dict()
		self.__propertyByID = dict()

		# The following set keeps track of updated properties.
		self.__propertyUpdates = set()
		
		# The following set keeps track of ignored property updates.
		self.__propertyUpdatesIgnored = set()

		# Property lock, prevents multi-threading from corrupting
		# the contents of properties, by muxing reads and writes.
		self.__propertyLock = threading.RLock()

		# Update lock, pLock, prevents multi-threading from corrupting
		# the contents of _updatedProperty, by muxing reads and writes.
		self.__updateLock = threading.RLock()
