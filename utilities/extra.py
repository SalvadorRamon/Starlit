'''
Created on May 8, 2016

@author: matiasbarcenas
'''

import math
from vector import Vector


def AnglesFromVector3D(vector):
	(x, y, z) = vector.component() if isinstance(vector, Vector) else vector
	yaw = math.degrees(math.atan2(-x, y))
	pitch = math.degrees(math.asin(z))
	return (yaw, pitch, 0)


def Vector3DFromAngles(angles):
	(yaw, pitch) = angles[:2]
	radYaw, radPitch = math.radians(yaw), math.radians(pitch)
	x = -math.sin(radYaw) * math.cos(radPitch)
	y = math.cos(radYaw) * math.cos(radPitch)
	z = math.sin(radPitch)
	return Vector((x, y, z))
