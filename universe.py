'''
Created on Apr 16, 2016

@author: matiasbarcenas
'''
from direct.showbase.ShowBase import ShowBase
from direct.gui.OnscreenText import OnscreenText
from direct.task import Task
from panda3d.core import WindowProperties, TextNode, TransparencyAttrib#, CollideMask, Material, Fog
import math, Queue, time, random

import universal
from utilities import Vector

# from starlit import Client
from direct.gui.OnscreenImage import OnscreenImage
#from direct.gui.DirectLabel import DirectLabel

NetAddress = ("localhost", 5000)

PlayerBaseSpeed = 10
UniverseBound = 750 # Remember, this affects respawn

FreeFly = False

FullScreen = False
HDResolution = True

global globalClock
global base


class Universe(ShowBase):
	def __init__(self, radialBound = UniverseBound):
		ShowBase.__init__(self)

		self.delegate = None

		self.__finishedEntities = Queue.Queue()

		self.setBackgroundColor(0, 0, 0)
		
		# Default camera mouse control behavior will be disabled
		self.disableMouse()
		wp = WindowProperties()
		wp.setMouseMode(WindowProperties.M_confined)  # Keep the mouse in the window (OS X & Linux)
		wp.setCursorHidden(True)
		if HDResolution: wp.setSize(3200, 1800)
		if HDResolution: wp.setOrigin(0,0)
		if FullScreen: wp.setFullscreen(True)
		wp.setTitle("[Alpha] Starlit")
		self.win.requestProperties(wp)

		# Preset camera
		self.camera.setPos(0, 0, 0) #-450, 320, 30)  # (40, -150, 50)
		

		# Generate UI text
		self.instructions = list()
		self.instructions.append(self.genLabelText("Controls: WASD & Mouse | ESC to exit", 0))
		self.instructions.append(self.genLabelText("Mouse Controls", 1))
		self.instructions.append(self.genLabelText("> Left-Right: Ailerons (Roll)", 2))
		self.instructions.append(self.genLabelText("> Up-Down: Elevators (Pitch)", 3))
		self.instructions.append(self.genLabelText("Keyboard Controls", 4))
		self.instructions.append(self.genLabelText("> W & S: Throttle", 5))
		self.instructions.append(self.genLabelText("> A & D: Rudder (Yaw)", 6))
		#self.instructions.append(self.genLabelText("< FU*K GIMAL LOCK! >", 7))

		self.tText = self.genLabelText("", 8)
		self.hprText = self.genLabelText("", 9)
		self.xyText = self.genLabelText("", 10)
		
		self._bound = dict()
		self._bound["universe"] = radialBound
		
		self._interface = dict()
		
		'''
		self._interface["message-box"] = DirectScrolledList( \
															borderWidth = (0,0),
															frameColor=(0, 0, 0, 0.75), \
															frameSize=(-0.56, 0.5, -0.32, 0.1), \
															pos=(-1.16, 0, -0.62), \
															numItemsVisible = 5)
														
		self._interface["message-box"].incButton['frameSize'] = (0, 0, 0, 0)
		self._interface["message-box"].decButton['frameSize'] = (0, 0, 0, 0)
		'''
		
		self._interface["hud"] = dict()
		self._interface["hud"]["message"] = dict()
		self._interface["hud"]["message"]["element"] = OnscreenText(text="", pos=(0,0.65,0), fg=(1, 1, 1, 1), align=TextNode.ACenter, scale=.08)
		self._interface["hud"]["message"]["timeout"] = 0
		
		self._interface["hud"]["score"] = dict()
		self._interface["hud"]["score"]["element"] = OnscreenText(text="-", pos=(1.5,-0.88,0), fg=(1, 1, 1, 1), align=TextNode.ACenter, scale=0.2)
		self._interface["hud"]["score"]["postfix"] = ["st", "nd", "rd", "th"]

		self._interface["hud"]["health"] = dict()
		self._interface["hud"]["health"]["element"] = OnscreenImage(image = "textures/interface/damage-effect.png", pos = (0,0,0), scale=(1.78, 0, 1))
		self._interface["hud"]["health"]["element"].setTransparency(TransparencyAttrib.MAlpha)
		self.setHUDHealth(100)
				
		

		# Shader configuration
		# render.clearShader()
		self.environment = dict()

		space = self.loader.loadModel("models/environment/ambient.egg")
		spaceTexture = self.loader.loadTexture("models/environment/ambient-texture.jpg")
		space.setTexture(spaceTexture)
		space.reparentTo(self.render)
		space.setScale(150, 150, 150)

		self.environment["space"] = space
		self.environment["spaceTexture"] = spaceTexture

		self.environment["planet"] = list()

		planetConfig = [ \
			{"color": "orange", "scale": 50, "pos": (5000, 5000, 5000), "rotation": (2, 11, 1)}, \
			{"color": "blue", "scale": 90, "pos": (4000, -9000, -4000), "rotation": (12, 3, 5)}, \
			{"color": "orange", "scale": 60, "pos": (-6000, 2000, 5000), "rotation": (23, 8, 3)}, \
			{"color": "blue", "scale": 100, "pos": (2000, -3000, 4000), "rotation": (10, 3, 11)}, \
			{"color": "orange", "scale": 80, "pos": (1000, 2000, -1000), "rotation": (4, 10, 9)}, \
			{"color": "blue", "scale": 70, "pos": (-6000, 10000, -8000), "rotation": (4, 4, 4)}, \
			{"color": "orange", "scale": 60, "pos": (9000, -3000, 5000), "rotation": (5, 8, 3)}, \
			{"color": "blue", "scale": 90, "pos": (-2000, 6000, 7000), "rotation": (2, 5, 6)},
			{"color": "orange", "scale": 60, "pos": (1000, 6000, 1000), "rotation": (3, 7, 8)},
			{"color": "blue", "scale": 80, "pos": (0, 30000, 0), "rotation": (3, 10, 9)}]

		for config in planetConfig:
			planet = self.loader.loadModel("models/planet/model.obj")
			planetTexture = self.loader.loadTexture("models/planet/" + config["color"] + "-texture.jpg")
			planet.setTexture(planetTexture)
			planet.setPos(config["pos"])
			planet.setScale(config["scale"])
			planet.reparentTo(self.render)
			config["model"] = planet
			self.environment["planet"].append(config)

		# self.reticle = OnscreenImage(image = "reticle.png", pos = (base.win.getXSize()/2, 0, base.win.getYSize()/2))
		self.reticle = OnscreenImage(image="textures/reticle.png", pos=(0, 0, 0), scale=(0.1, 0.1, 0.05))
		self.reticle.setTransparency(TransparencyAttrib.MAlpha)

		# Setup Keyboard
		self.keys = {}
		for key in ['a', 'd', 'w', 's']:
			self.keys[key] = 0
			self.accept(key, self.__controlKeyboardEvent, [key, 1])
			# self.accept('shift-%s' % key, self.push_key, [key, 1])
			self.accept('%s-up' % key, self.__controlKeyboardEvent, [key, 0])

		self.accept('escape', __import__('sys').exit, [0])

		# Setup Mouse
		self.mouse = {'dx': 0, 'dy': 0, "left": 0, "right": 0}  # {'x' : None, 'y': None, 'dx': 0, 'dy': 0}

		# self.mouse_button = {"left": 0, "right": 0}
		self.accept('mouse1', self.__controlMouseEvent, ['left', 1])
		self.accept('mouse1-up', self.__controlMouseEvent, ['left', 0])
		self.accept('mouse3', self.__controlMouseEvent, ['right', 1])
		self.accept('mouse3-up', self.__controlMouseEvent, ['right', 0])



		# Add the update task every frame.
		self.taskMgr.add(self.__unloadUpdateTask, "Unloads Task")
		self.taskMgr.add(self.__controlUpdateTask, "Control Task")
		self.taskMgr.add(self.__backgroundUpdateTaks, "Background Task")
		self.taskMgr.add(self.__foregroundUpdateTaks, "Foreground Task")
		self.taskMgr.add(self.__delegateUpdateTask, "Delegate Task")
		self.taskMgr.add(self.__hudUpdateTask, "HUD Task")
		self.taskMgr.add(self.update, "Main Task")

		self.acceleration = 0
		



	def unloadModelEntity(self, modelEntity):
		if not isinstance(modelEntity, universal.Model): return
		self.__finishedEntities.put(modelEntity)
		
	#def addMessage(self, message):
	#	label = DirectLabel(text = message, text_scale=0.08, text_fg = (1,1,1,1), frameColor = (0,0,0,0))
		
	def setHUDMessage(self, message, color = (1, 0.1, 0, 1), timeout = 3):
		self._interface["hud"]["message"]["element"].setFg(color)
		self._interface["hud"]["message"]["element"].setText(message)
		self._interface["hud"]["message"]["timeout"] = time.time() + timeout
		
	def setHUDRank(self, score):
		color = (1,0,1,1) if score <= 3 else (1,1,1,0.5)
		self._interface["hud"]["score"]["element"].setFg(color)
			
		postfix = self._interface["hud"]["score"]["postfix"][score-1 if score <= 4 else 3]
		
		postfix = postfix if score <= 20 else "/"
		score = str(score) if score <= 20 else ">="
			
		self._interface["hud"]["score"]["element"].setText(str(score) + postfix)
		
	def setHUDHealth(self, health):
		self._interface["hud"]["health"]["element"].setAlphaScale((100-health) / 100.0)

		
	def respawn(self, position = None, message = None):
		if message: self.setHUDMessage(message, (1,1,1,1))
		
		while True:
			respawnPoint = Vector((random.random() * UniverseBound, \
								random.random() * UniverseBound, \
								random.random() * UniverseBound))
			if respawnPoint.magnitude() <= UniverseBound: break
			
		self.camera.setPos(respawnPoint.component())

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
		baseSpeed = PlayerBaseSpeed
		# We need to limit the turning when going fast
		turnSpeed = 10 * (1.50 - self.acceleration)
		rollSpeed = 20 * (1.50 - self.acceleration)

		# Physically move the camera
		offset = delta * baseSpeed + delta * speed * self.acceleration
		if FreeFly: offset = -self.keys["s"] + self.keys["w"]

		cameraPosition = Vector(tuple(self.camera.getPos()))
		
		if cameraPosition.magnitude() > self._bound["universe"]:
			cameraPosition = cameraPosition.scale(-1)
			self.camera.setPos(cameraPosition.component())

		self.camera.setPos(self.camera, 0, offset, 0)

		horizon = delta * turnSpeed * (self.keys['a'] - self.keys['d'])
		if FreeFly: horizon = self.keys["a"] - self.keys["d"]

		# The roll of the camera directly translate from the offset of the mouse
		# to the camera's roll.
		roll = currentRoll + rollSpeed * dxMouse

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
		self.xyText.setText(
			"Coordinates: ({0:03.2f}, {1:03.2f}, {2:03.2f})".format(self.camera.getX(), self.camera.getY(),
			                                                        self.camera.getZ()))

		return Task.cont

	def __hudUpdateTask(self, task):
		#delta = globalClock.getDt()
		
		interfaceMessageAlpha = int(self._interface["hud"]["message"]["timeout"] > time.time())
		self._interface["hud"]["message"]["element"].setAlphaScale(interfaceMessageAlpha)
		
		return Task.cont

	def __unloadUpdateTask(self, task):
		# Delete all entity models in the queue
		while not self.__finishedEntities.empty():
			entity = self.__finishedEntities.get()
			if entity.model:
				entity.model.removeNode()
				entity.model = None
		return Task.cont

	def __controlKeyboardEvent(self, key, value):
		self.keys[key] = value

	def __controlMouseEvent(self, button, value):
		self.mouse[button] = value

	def __controlUpdateTask(self, task):
		mw = self.mouseWatcherNode

		# Get the new coordinates; that's the offset
		self.mouse['dx'] = mw.getMouseX() if mw.hasMouse() else 0
		self.mouse['dy'] = mw.getMouseY() if mw.hasMouse() else 0

		base.win.movePointer(0, int(base.win.getXSize() / 2), int(base.win.getYSize() / 2))

		return Task.cont

	def __delegateUpdateTask(self, task):
		if self.delegate and hasattr(self.delegate, "_universeFrameUpdate"):
			self.delegate._universeFrameUpdate()
		return Task.cont

	def __backgroundUpdateTaks(self, task):
		delta = globalClock.getDt()

		self.environment["space"].setPos(self.camera.getPos())

		for planet in self.environment["planet"]:
			(h, p, r) = planet["model"].getHpr()
			(dh, dp, dr) = tuple(x * delta for x in planet["rotation"])

			planet["model"].setHpr((h + dh, p + dp, r + dr))
			position = tuple(i + j for i, j in zip(self.camera.getPos(), planet["pos"]))

			planet["model"].setPos(position)

		return Task.cont

	def __foregroundUpdateTaks(self, task):
		pass

	def genLabelText(self, text, i):
		text = OnscreenText(text=text, pos=(-1.65, .5 - .05 * i), fg=(0, 1, 0, 1), align=TextNode.ALeft, scale=.05)
		return text
