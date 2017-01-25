from direct.showbase.ShowBase import ShowBase
from direct.gui.OnscreenText import OnscreenText
from direct.task import Task
from panda3d.core import TextNode
import math


class Universe(ShowBase):
	def __init__(self):
		ShowBase.__init__(self)

		# Generate UI text
		self.instructions = list()
		self.instructions.append(self.genLabelText("Controls: Mouse | ESC to exit", 0))

		# self.hprText = self.genLabelText("", 9)
		# self.xyText = self.genLabelText("", 10)

		# Create some text environment (ground).
		self.ground = self.loader.loadModel("environment")
		self.ground.reparentTo(self.render)

		self.ground.setScale(1, 1, 1)
		self.ground.setPos(0, 0, 0)

		# Load model mesh
		self.model = self.loader.loadModel("model.egg")
		self.model.reparentTo(self.render)

		self.model.setScale(50, 50, 50)
		self.model.setPos(0, 0, 0)

		# Load model texture
		self.model.setTexture(self.loader.loadTexture("texture.png"))

		# Setup Keyboard
		'''
		self.keys = {}
		for key in ['a', 'd', 'w', 's']:
			self.keys[key] = 0
			self.accept(key, self.push_key, [key, 1])
			self.accept('%s-up' % key, self.push_key, [key, 0])
		'''
		self.accept('escape', __import__('sys').exit, [0])

	# Add the update task every frame.
	# self.taskMgr.add(self.update, "Main Task")

	def push_key(self, key, value):
		# Store the value for the key
		self.keys[key] = value

	'''
	def update(self, task):
		# Prepare camera variables
		currentPitch = self.camera.getP()
		currentYaw   = self.camera.getH()

		# Physically move the camera
		speed = 5
		dPitch = speed *  self.keys['w'] + speed * -self.keys['s']
		dYaw   = speed * -self.keys['a'] + speed *  self.keys['d']

		yaw   = currentYaw   + dYaw
		pitch = currentPitch + dPitch

		self.camera.setHpr(yaw, pitch, 0)

		self.hprText.setText("Pitch: {0:0.2f}, Yaw: {1:0.2f}".format(pitch, yaw))
		self.xyText.setText("Coordinates: ({0:0.2f}, {1:0.2f})".format(self.camera.getX(), self.camera.getY()))

		return Task.cont
	'''

	def genLabelText(self, text, i):
		text = OnscreenText(text=text, pos=(-1.3, .5 - .05 * i), fg=(0, 1, 0, 1), align=TextNode.ALeft, scale=.05)
		return text


if __name__ == "__main__":
	universe = Universe()
	universe.run()
