'''
Created on Apr 26, 2016

@author: matiasbarcenas
'''

from math import sqrt
from numbers import Number


class Vector:
	# Methods' implementation below
	def __add__(self, other):
		other = Vector(other, self.dimensions()) if isinstance(other, Number) else Vector(other)
		return Vector(tuple(a + b for a, b in zip(self.component(), other.component())))

	def __sub__(self, other):
		other = Vector(other, self.dimensions()) if isinstance(other, Number) else Vector(other)
		return Vector(tuple(a - b for a, b in zip(self.component(), other.component())))

	def __mul__(self, other):
		other = Vector(other, self.dimensions()) if isinstance(other, Number) else Vector(other)
		return Vector(tuple(n * s for n, s in zip(self.component(), other.component())))

	def __div__(self, other):
		other = Vector(other, self.dimensions()) if isinstance(other, Number) else Vector(other)
		return Vector(tuple(n / s for n, s in zip(self.component(), other.component())))

	def __neg__(self):
		return self.scale(-1)

	def add(self, other):
		return self + other

	def subtract(self, other):
		return self - other

	def multiply(self, other):
		return self * other

	def divide(self, other):
		return self / other

	def scale(self, scale):
		return self * scale

	def magnitude(self):
		return sqrt(sum(tuple(pow(element, 2) for element in self.component())))

	def normalized(self):
		magnitude = self.magnitude()
		return Vector(tuple(n / magnitude for n in self.component()))

	def component(self, index=None):
		return self._component[index] if index is not None else self._component

	def dotProduct(self, other):
		return sum(self.scale(other).component())

	def dimensions(self):
		return len(self.component())

	def __str__(self):
		# Use python's built-in string interpolation
		return str(self.component())

	def __init__(self, value, dimensions=None):
		if isinstance(value, Number): value = (value,) * (dimensions or 1)
		if isinstance(value, Vector): value = value.component()
		self._component = tuple(value)
