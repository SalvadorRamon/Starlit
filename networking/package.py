'''
Created on Apr 21, 2016

@author: matiasbarcenas
'''

import numbers
import struct


class Package(object):
	'''
	classdocs
	'''
	'''
	MetaType = 0
	PositionType = 1
	DirectionType = 2
	StatusType = 3
	ActionType = 4
	ProjectileType = 5
	'''

	MetaData = "PH"
	MetaSize = struct.calcsize(MetaData)

	@property
	def data(self):
		return self._content

	@property
	def identifier(self):
		return self._identifier

	@property
	def content(self):
		return self._content[Package.MetaSize: Package.MetaSize + self._length]

	@property
	def contents(self):
		contents = []

		total = len(self._content)
		metaStart = 0

		while metaStart + Package.MetaSize < total:
			contentStart = metaStart + Package.MetaSize
			meta = self._content[metaStart: contentStart]
			(identifier, length) = struct.unpack(Package.MetaData, meta)
			content = self._content[contentStart: contentStart + length]
			contents.append(Package(identifier, content))
			metaStart += Package.MetaSize + length

		return tuple(contents)

	def copy(self, other):
		# If not a package, can't copy
		if not isinstance(other, Package): return False

		self._identifier = int(other._identifier)
		self._content = str(other._content)
		self._length = int(other._length)

		return True

	def load(self, data):
		# If not a string, can't load
		if not isinstance(data, str): return False
		if len(data) < Package.MetaSize: return False

		meta = data[: Package.MetaSize]
		(self._identifier, self._length) = struct.unpack(Package.MetaData, meta)
		self._content = str(data)

		return True

	def __add__(self, other):
		if not isinstance(other, Package): raise ValueError()

		return Package(self.data + other.data)

	def __iadd__(self, other):
		if not isinstance(other, Package): raise ValueError()

		if self.content:
			self.load(self.data + other.data)
		else:
			self.load(other.data)
		return self

	def __init__(self, identifier=0, content=""):
		'''
		Constructor
		'''

		# Treat identifier as a Package & attempt to copy it.
		# Upon success, return
		if self.copy(identifier): return

		# Treat identifier as a string of Package data & attempt to copy it.
		# Upon success, return
		if self.load(identifier): return

		# Check if we're trying to package a package
		if isinstance(content, Package):
			content = content.data

		identifier = identifier if isinstance(identifier, numbers.Number) else -1

		self._identifier = identifier
		self._length = len(content)
		self._content = struct.pack(Package.MetaData, identifier, self._length) + content
