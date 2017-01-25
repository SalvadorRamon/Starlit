from direct.showbase.ShowBase import ShowBase
from direct.gui.OnscreenText import OnscreenText
from direct.task import Task
from panda3d.core import WindowProperties, TextNode

from quaternion import Quaternion, Vector3D
from utilities import Vector
import math


class Universe(ShowBase):
	def __init__(self):
		ShowBase.__init__(self)

		# Generate UI text
		self.instructions = list()
		self.instructions.append(self.genLabelText("Controls: WASD & Mouse | ESC to exit", 0))
		self.instructions.append(self.genLabelText("Mouse Controls", 1))
		self.instructions.append(self.genLabelText("> Left-Right: Ailerons (Roll)", 2))
		self.instructions.append(self.genLabelText("> Up-Down: Elevators (Pitch)", 3))
		self.instructions.append(self.genLabelText("Keyboard Controls", 4))
		self.instructions.append(self.genLabelText("> W & S: Throttle", 5))
		self.instructions.append(self.genLabelText("> A & D: Rudder (Yaw)", 6))

		self.tText = self.genLabelText("", 8)
		self.hprText = self.genLabelText("", 9)
		self.xyText = self.genLabelText("", 10)

		# Shader configuration
		# render.clearShader()

		# Create some text environment (ground).
		self.ground = self.loader.loadModel("environment")
		self.ground.reparentTo(self.render)

		self.ground.setScale(1, 1, 1)
		self.ground.setPos(0, 0, 0)

		# Setup Keyboard
		self.keys = {}
		for key in ['a', 'd', 'w', 's']:
			self.keys[key] = 0
			self.accept(key, self.push_key, [key, 1])
			# self.accept('shift-%s' % key, self.push_key, [key, 1])
			self.accept('%s-up' % key, self.push_key, [key, 0])

		self.accept('escape', __import__('sys').exit, [0])

		# Setup Mouse
		self.mouse = {'x': None, 'y': None, 'dx': 0, 'dy': 0}

		# Default camera mouse control behavior will be disabled
		self.disableMouse()
		wp = WindowProperties()
		wp.setMouseMode(WindowProperties.M_relative)
		wp.setCursorHidden(True)
		wp.setSize(1080, 720)
		wp.setOrigin(0, 0)
		# wp.setFullscreen(True)
		wp.setTitle("Starlit - Alpha")
		self.win.requestProperties(wp)

		# Preset values
		self.direction = (0, 1, 0)
		self.roll = 0

		# Preset camera
		self.camera.setPos(40, -150, 50)

		# Add the update task every frame.
		self.taskMgr.add(self.update, "Main Task")
		self.taskMgr.add(self.mouseTask, "Mouse Task")
		self.taskMgr.add(self.cameraUpdate, "Camera Control Task")

	def push_key(self, key, value):
		# Store the value for the key
		self.keys[key] = value

	def cameraUpdate(self, taks):
		(x, y, z) = self.direction
		yaw = math.degrees(math.atan2(-x, y))
		pitch = math.degrees(math.asin(z))

		self.camera.setHpr(yaw, pitch, self.roll)
		return Task.cont

	def update(self, task):
		delta = globalClock.getDt()

		# Prepare camera variables
		currentRoll = self.camera.getR()
		currentPitch = self.camera.getP()
		currentYaw = self.camera.getH()

		# Prepare mouse variables with a limit
		dxMouse = self.mouse['dx']
		dyMouse = -self.mouse['dy']

		# yUnit = math.cos(math.radians(currentRoll))
		# xUnit = math.sin(math.radians(currentRoll))
		# rollAxis = Vector((xUnit, yUnit, 0))
		# rollAxis = rollAxis.normalize()
		# self.roll = self.roll + dxMouse * 10

		radYaw, radPitch = math.radians(currentYaw), math.radians(currentPitch + 90)
		hAxisAngleX = -math.sin(radYaw) * math.cos(radPitch)
		hAxisAngleY = math.cos(radYaw) * math.cos(radPitch)
		hAxisAngleZ = math.sin(radPitch)

		radYaw, radPitch = math.radians(currentYaw + 90), math.radians(currentPitch)
		vAxisAngleX = -math.sin(radYaw) * math.cos(radPitch)
		vAxisAngleY = math.cos(radYaw) * math.cos(radPitch)
		vAxisAngleZ = math.sin(radPitch)

		hAxisAngleVector = (hAxisAngleX, hAxisAngleY, hAxisAngleZ)
		vAxisAngleVector = (vAxisAngleX, vAxisAngleY, vAxisAngleZ)

		self.roll += (self.keys['d'] - self.keys['a'])

		# Direction and Transformation quaternians
		dQuaternion = Quaternion(math.radians(0),
		                         self.direction)  # .FromAxisAngle(self.direction, math.radians(0))#(0, direction)
		rQuaternion = Quaternion.FromAxisAngle(self.direction, math.radians(-self.roll))
		tHQuaternion = Quaternion.FromAxisAngle(hAxisAngleVector, math.radians(dxMouse * 25))
		tVQuaternion = Quaternion.FromAxisAngle(vAxisAngleVector, math.radians(-dyMouse * 25))

		# tQuaternion = tQuaternion * rQuaternion
		result = dQuaternion * tHQuaternion * rQuaternion * tVQuaternion * rQuaternion
		# rQuaternion = dQuaternion * tHQuaternion * tVQuaternion
		# rDirection, angle = rQuaternion.toAxisAngle()
		rDirection, angle = result.toAxisAngle()
		self.direction = rDirection.value

		'''
		xAxis = (1, 0, 0)
		yAxis = (0, 1, 0)
		yawOffset = -self.keys['a'] + self.keys['d']
		pitchOffset = dyMouse * turnSpeed

		yRotation = Quaternion.FromAxisAngle(yAxis, math.radians(yawOffset))
		xRotation = Quaternion.FromAxisAngle(xAxis, math.radians(pitchOffset))

		self.viewAxis = yRotation * self.viewAxis
		self.viewAxis = xRotation * self.viewAxis

		(yaw, pitch, roll) = Vector3D(self.viewAxis).scale(90).value
		roll = 0
		'''

		'''
		if dxMouse:

			self.viewAxis = Quaternion.FromAxisAngle((0, 1, 0),


		pitch, roll, yaw = Vector3D(self.viewAxis).scale(360)
		'''

		self.tText.setText("MdX: {0:0.2f}, MdY: {1:0.2f}".format(dxMouse, dyMouse))
		self.hprText.setText(
			"Roll: {0:0.2f}, Pitch: {1:0.2f}, Yaw: {2:0.2f}".format(currentRoll, currentPitch, currentYaw))
		self.xyText.setText("Coordinates: ({0:0.2f}, {1:0.2f})".format(self.camera.getX(), self.camera.getY()))

		return Task.cont

	def mouseTask(self, task):
		mw = self.mouseWatcherNode

		# Get the new coordinates
		x = mw.getMouseX() if mw.hasMouse() else 0
		y = mw.getMouseY() if mw.hasMouse() else 0

		# Calculate the difference between old and new coordinates.
		self.mouse['dx'] = x - self.mouse['x'] if self.mouse['x'] is not None else 0
		self.mouse['dy'] = y - self.mouse['y'] if self.mouse['y'] is not None else 0

		# Update the  old coordinates to the new ones.
		self.mouse['x'] = x
		self.mouse['y'] = y
		return Task.cont

	def genLabelText(self, text, i):
		text = OnscreenText(text=text, pos=(-1.3, .5 - .05 * i), fg=(0, 1, 0, 1), align=TextNode.ALeft, scale=.05)
		return text


if __name__ == "__main__":
	universe = Universe()
	universe.run()
