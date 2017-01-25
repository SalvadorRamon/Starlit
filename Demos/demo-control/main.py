from direct.showbase.ShowBase import ShowBase
from direct.gui.OnscreenText import OnscreenText
from direct.task import Task
from panda3d.core import WindowProperties, TextNode

from quaternion import Quaternion, Vector3D
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
		# wp.setFullscreen(True)
		wp.setTitle("Starlit - Alpha")
		self.win.requestProperties(wp)

		# Preset values
		self.acceleration = 0
		self.viewAxis = (1, 0, 0)

		# Preset camera
		self.camera.setPos(40, -150, 50)

		# Add the update task every frame.
		self.taskMgr.add(self.update, "Main Task")
		self.taskMgr.add(self.mouseTask, "Mouse Task")

	def push_key(self, key, value):
		# Store the value for the key
		self.keys[key] = value

	def update(self, task):
		delta = globalClock.getDt()

		# Prepare camera variables
		currentRoll = self.camera.getR()
		currentPitch = self.camera.getP()
		currentYaw = self.camera.getH()

		# Prepare mouse variables with a limit
		dxMouse = self.mouse['dx']
		dyMouse = -self.mouse['dy']

		# Calculate the spaceship's acceleration with a limit
		self.acceleration += (0.01 if self.keys['w'] else -0.01)
		if self.acceleration < 0: self.acceleration = 0
		if self.acceleration > 1: self.acceleration = 1

		# Calculate limits and speed
		speed = 20 * 2
		baseSpeed = 0
		# We need to limit the turning when going fast
		turnSpeed = 10 * (1.50 - self.acceleration)

		# Physically move the camera
		offset = delta * baseSpeed + delta * speed * self.acceleration
		self.camera.setPos(self.camera, 0, offset, 0)

		horizon = delta * turnSpeed * (self.keys['a'] - self.keys['d'])

		# The roll of the camera directly translate from the offset of the mouse
		# to the camera's roll.
		roll = currentRoll + turnSpeed * dxMouse

		# The following two lines calculate the unit magnitude of x and y
		# relative to the vertical axis of the view of the camera.
		yUnit = math.sin(math.radians(roll + 90))
		xUnit = math.cos(math.radians(roll + 90))

		# These two lines set the x (yaw) and y (pitch) appropriately,
		# by factoring the the unit vectors of dyMouse, or the mouse's y axis.
		# The last value, horizon, is manually moving the camera based on the
		# horizontal axis relative to the view of the camera. The unit vectors
		# for horizon must be 90 degrees from the unit vectors of dyMouse, since
		# horizon is working with the the horizontal axis, not the vertical.
		# This can be accomplished by offsetting sin and cos by 90 degrees extra
		# but I decided to invert the unit vectors (ux -> uy, uy -> -ux).
		pitch = currentPitch + turnSpeed * yUnit * dyMouse + -xUnit * horizon
		yaw = currentYaw + turnSpeed * xUnit * dyMouse + yUnit * horizon

		# Temporary Fix
		if pitch > 90:
			pitch = 90 - (pitch - 90)
			yaw += 180
			roll += 180
		# Temporary Fix
		if pitch < -90:
			pitch = -90 - (pitch + 90)
			yaw += 180
			roll += 180

		self.camera.setHpr(yaw, pitch, roll)

		self.tText.setText(
			"Throttle: {0:0.2f} | MdX: {1:0.2f}, MdY: {2:0.2f}".format(self.acceleration * 100, dxMouse, dyMouse))
		self.hprText.setText("Roll: {0:0.2f}, Pitch: {1:0.2f}, Yaw: {2:0.2f}".format(roll, pitch, yaw))
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
