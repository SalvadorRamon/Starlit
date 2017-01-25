import math


class Vector3D:
	def x(self):
		return self.value[0]

	def y(self):
		return self.value[1]

	def z(self):
		return self.value[2]

	def normalize(self, tolerance=0.00001):
		m2 = sum(n ** 2 for n in self.value)

		if abs(m2 - 1.0) > tolerance:
			m = math.sqrt(m2)
			return Vector3D(tuple(n / m for n in self.value))

		return self

	def scale(self, scale):
		return Vector3D(tuple(n * scale for n in self.value))

	def __str__(self):
		return str(self.value)

	def __init__(self, vector):
		self.value = vector.value if isinstance(vector, Vector3D) else vector


class Quaternion(Vector3D):
	def theta(self):
		return self.value[3]

	def conjugate(self):
		return Quaternion(self.theta(), tuple(-n for n in self.value[:3]))

	@staticmethod
	def FromAxisAngle(vector, theta):
		vector = Vector3D(vector).normalize()
		theta /= 2
		return Quaternion(math.cos(theta), vector.scale(math.sin(theta)))

	def toAxisAngle(self):
		return Vector3D(self.value[:3]).normalize(), math.acos(self.theta()) * 2.0

	def __mul__(self, that):
		if isinstance(that, tuple):
			return (self * Quaternion(0.0, that) * self.conjugate()).value[:3]

		q1 = self.normalize()
		q2 = that.normalize()

		(x1, y1, z1, w1) = q1.value
		(x2, y2, z2, w2) = q2.value
		w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
		x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
		y = w1 * y2 + y1 * w2 + z1 * x2 - x1 * z2
		z = w1 * z2 + z1 * w2 + x1 * y2 - y1 * x2

		return Quaternion(w, (x, y, z))

	def __init__(self, theta, vector):
		Vector3D.__init__(self, vector)
		self.value += (theta,)


'''
def pVector(v):
	return "({0}, {1}, {2})".format(int(v[0] * 180) , int(v[1] * 180), int(v[2] * 180))

def test():
	xaxis = (1,0,0)
	yaxis = (0,1,0)
	zaxis = (0,0,1)

	xR = Quaternion.FromAxisAngle(xaxis, math.radians(1))
	yR = Quaternion.FromAxisAngle(yaxis, math.radians(1))
	zR = Quaternion.FromAxisAngle(zaxis, math.radians(1))

	v = xaxis
	v
	for i in range(0, 180):
		output = "Angle " + str(i) + ": "
		output += pVector(v) + " | "
		v = yR * v
		output += pVector(v)
		print output

	for i in range(0, 180):
		output = "Angle " + str(i) + ": "
		output += pVector(v) + " | "
		v = zR * v
		output += pVector(v)
		print output

test()
'''
