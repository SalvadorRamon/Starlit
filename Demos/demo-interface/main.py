from direct.showbase.ShowBase import ShowBase
from direct.gui.OnscreenText import OnscreenText
from direct.task import Task
from panda3d.core import TextNode, WindowProperties
import math, time


from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectLabel import DirectLabel
from direct.gui.DirectScrolledList import DirectScrolledList

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
		
		#self.disableMouse()
		wp = WindowProperties()
		#wp.setMouseMode(WindowProperties.M_confined)  # Keep the mouse in the window (OS X & Linux)
		#wp.setCursorHidden(True)
		wp.setSize(1920, 1080)
		wp.setOrigin(0,0)
		wp.setFullscreen(True)
		self.win.requestProperties(wp)
		
		
		
		self._interface = dict()
		
		# L R B T
		#self._interface["message-box"] = dict()
		'''
		self._interface["message-box"] = DirectScrolledList( \
															borderWidth = (0,0),
															frameColor=(0, 0, 0, 0.75), \
															frameSize=(-0.56, 0.5, -0.32, 0.1), \
															pos=(-1.16, 0, -0.62), \
															numItemsVisible = 5)#, \
															#itemFrame_frameSize = (-0.54, 0.48, -0.01, 0.05), \
															#itemFrame_pos = (0, 0, 0.03))
															#itemFrame_borderWidth = (0.1, 0.1))
														
		self._interface["message-box"].incButton['frameSize'] = (0,0,0,0)#(-0.1, 0.1, -0.1, 0.1)
		self._interface["message-box"].decButton['frameSize'] = (0,0,0,0)#(-0.1, 0.1, -0.1, 0.1)
		
		for msg in ['apple', 'pear', 'banana', 'orange', "alpha", "beta", "gamma"]:
			label = DirectLabel(text = msg, text_scale=0.08, text_fg = (1,1,1,1), frameColor = (0,0,0,0))
			self._interface["message-box"].addItem(label)
			iCount = len(self._interface["message-box"].items)
			self._interface["message-box"].scrollTo(self, iCount, False)
		'''
			
		
		
		
		self._interface["hud"] = dict()
		self._interface["hud"]["message"] = dict()
		self._interface["hud"]["message"]["element"] = OnscreenText(text="", pos=(0,0.65,0), fg=(1, 0.1, 0, 1), align=TextNode.ACenter, scale=0.1)
		
		
		self._interface["hud"]["score"] = dict()
		self._interface["hud"]["score"]["element"] = OnscreenText(text="5th", pos=(1.5,-0.88,0), fg=(1, 1, 1, 1), align=TextNode.ACenter, scale=0.2)
		self._interface["hud"]["score"]["postfix"] = ["st", "nd", "rd", "th"]
		
		#DirectFrame(frameColor=(0, 0, 0, 0.75), \
		#														frameSize=(-0.56, 0.5, -0.32, 0.1), \
		#														pos=(-1.16, 0, -0.62))
		
		#self._interface["message-box"]["line"] = DirectLabel()
		'''
		l1 = DirectLabel(text = "Test1", text_scale=0.08, text_fg = (1,1,1,1), frameColor = (0,0,0,0))#, borderWidth = (0.01, 0.01))
	
		l2 = DirectLabel(text = "Test2", text_scale=0.08)#, borderWidth = (0.01, 0.01))
		l3 = DirectLabel(text = "Test3", text_scale=0.08)#, borderWidth = (0.01, 0.01))
		l4 = DirectLabel(text = "Test4", text_scale=0.08)#, borderWidth = (0.01, 0.01))
		l5 = DirectLabel(text = "Test5", text_scale=0.08)#, borderWidth = (0.01, 0.01))
		
		self._interface["message-box"].addItem(l1)
		self._interface["message-box"].addItem(l2)
		self._interface["message-box"].addItem(l3)
		self._interface["message-box"].addItem(l4)
		self._interface["message-box"].addItem(l5)
		'''
		
		self.setHUDMessage("This is a test message", (1,0,1,1), 3)
		self.setHUDScore(20)
	# Add the update task every frame.
		self.taskMgr.add(self.__hudUpdate, "HUD Task")

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
	
	def setHUDMessage(self, message, color = (1, 0.1, 0, 1), timeout = 3):
		self._interface["hud"]["message"]["element"].setFg(color)
		self._interface["hud"]["message"]["element"].setText(message)
		self._interface["hud"]["message"]["timeout"] = time.time() + timeout
		
	def setHUDScore(self, score):
		color = (1,0,1,1) if score <= 3 else (1,1,1,0.5)
		self._interface["hud"]["score"]["element"].setFg(color)
			
		postfix = self._interface["hud"]["score"]["postfix"][score-1 if score <= 4 else 3]
		
		postfix = postfix if score <= 20 else "/"
		score = str(score) if score <= 20 else ">="
			
		self._interface["hud"]["score"]["element"].setText(str(score) + postfix)
	
	def __hudUpdate(self, task):
		delta = globalClock.getDt()
		
		interfaceMessageAlpha = int(self._interface["hud"]["message"]["timeout"] > time.time())
		self._interface["hud"]["message"]["element"].setAlphaScale(interfaceMessageAlpha)
		
		return Task.cont


if __name__ == "__main__":
	universe = Universe()
	universe.run()
