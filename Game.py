from direct.showbase.ShowBase import ShowBase

from direct.actor.Actor import Actor
from direct.task import Task
from panda3d.core import CollisionTraverser, CollisionHandlerPusher, CollisionSphere, CollisionTube, CollisionNode
from panda3d.core import Vec4, Vec3, Vec2
from panda3d.core import WindowProperties
from panda3d.core import Shader
from panda3d.core import ClockObject

from direct.gui.DirectGui import *

from GameObject import *
from Player import *
from Enemy import *
from Level import Level

from Common import Common

import random

class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        #globalClock.setMode(ClockObject.M_limited)
        #globalClock.setFrameRate(60)

        self.disableMouse()

        Common.initialise()
        Common.framework = self

        properties = WindowProperties()
        properties.setSize(1000, 750)
        self.win.requestProperties(properties)

        self.exitFunc = self.cleanup

        render.setShaderAuto()

        self.keyMap = {
            "up" : False,
            "down" : False,
            "left" : False,
            "right" : False,
            "shoot" : False,
            "activateItem" : False,
            "invLeft" : False,
            "invRight" : False
        }

        self.accept("w", self.updateKeyMap, ["up", True])
        self.accept("w-up", self.updateKeyMap, ["up", False])
        self.accept("s", self.updateKeyMap, ["down", True])
        self.accept("s-up", self.updateKeyMap, ["down", False])
        self.accept("a", self.updateKeyMap, ["left", True])
        self.accept("a-up", self.updateKeyMap, ["left", False])
        self.accept("d", self.updateKeyMap, ["right", True])
        self.accept("d-up", self.updateKeyMap, ["right", False])
        self.accept("mouse1", self.updateKeyMap, ["shoot", True])
        self.accept("mouse1-up", self.updateKeyMap, ["shoot", False])
        self.accept("wheel_up", self.onMouseWheel, [1])
        self.accept("wheel_down", self.onMouseWheel, [-1])
        self.accept("space-up", self.interact)
        self.accept("1", self.selectWeapon, [0])
        self.accept("2", self.selectWeapon, [1])

        self.accept("f", self.toggleFrameRateMeter)
        self.showFrameRateMeter = False

        self.pusher = CollisionHandlerPusher()
        self.traverser = CollisionTraverser()
        self.traverser.setRespectPrevTransform(True)

        self.pusher.setHorizontal(True)

        self.pusher.add_in_pattern("%fn-into-%in")
        self.pusher.add_in_pattern("%fn-into")
        self.pusher.add_again_pattern("%fn-again-into")
        #self.accept("trapEnemy-into-wall", self.stopTrap)
        self.accept("projectile-into", self.projectileImpact)
        self.accept("projectile-again-into", self.projectileImpact)
        self.accept("playerWallCollider-into-item", self.itemCollected)
        self.accept("playerWallCollider-into-trigger", self.triggerActivated)

        self.updateTask = taskMgr.add(self.update, "update")

        self.player = None
        self.currentLevel = None

        self.gameOverScreen = DirectDialog(frameSize = (-0.7, 0.7, -0.7, 0.7),
                                           fadeScreen = 0.4,
                                           relief = DGG.FLAT)
        self.gameOverScreen.hide()

        label = DirectLabel(text = "Game Over!",
                            parent = self.gameOverScreen,
                            scale = 0.1,
                            pos = (0, 0, 0.2),
                            #text_font = self.font,
                            relief = None)

        self.finalScoreLabel = DirectLabel(text = "",
                                           parent = self.gameOverScreen,
                                           scale = 0.07,
                                           pos = (0, 0, 0),
                                           #text_font = self.font,
                                           relief = None)

        btn = DirectButton(text = "Restart",
                           command = self.startGame,
                           pos = (-0.3, 0, -0.2),
                           parent = self.gameOverScreen,
                           scale = 0.07,
                           #text_font = self.font,
                           frameSize = (-4, 4, -1, 1),
                           text_scale = 0.75,
                           relief = DGG.FLAT,
                           text_pos = (0, -0.2))
        btn.setTransparency(True)

        btn = DirectButton(text = "Quit",
                           command = self.quit,
                           pos = (0.3, 0, -0.2),
                           parent = self.gameOverScreen,
                           scale = 0.07,
                           #text_font = self.font,
                           frameSize = (-4, 4, -1, 1),
                           text_scale = 0.75,
                           relief = DGG.FLAT,
                           text_pos = (0, -0.2))
        btn.setTransparency(True)

        render.setShaderAuto()

        self.startGame()

    def toggleFrameRateMeter(self):
        self.showFrameRateMeter = not self.showFrameRateMeter

        self.setFrameRateMeter(self.showFrameRateMeter)

    def startGame(self):
        self.gameOverScreen.hide()

        self.cleanup()

        self.player = Player()

        self.currentLevel = Level("testLevel")

    def selectWeapon(self, index):
        if self.player is not None:
            self.player.setCurrentWeapon(index)

    def interact(self):
        if self.player is not None:
            self.player.interact()

    def onMouseWheel(self, dir):
        if self.player is not None:
            self.player.scrollWeapons(dir)

    def updateKeyMap(self, controlName, controlState, callback = None):
        self.keyMap[controlName] = controlState

        if callback is not None:
            callback(controlName, controlState)

    def update(self, task):
        dt = globalClock.getDt()

        if self.currentLevel is not None:
            self.currentLevel.update(self.player, self.keyMap, dt)

            if self.player is not None and self.player.health <= 0:
                if self.gameOverScreen.isHidden():
                    self.gameOverScreen.show()
                    #self.finalScoreLabel["text"] = "Final score: " + str(self.player.score)
                    #self.finalScoreLabel.setText()

            self.traverser.traverse(render)

            if self.player is not None and self.player.health > 0:
                self.player.postTraversalUpdate(dt)

        return Task.cont

    def projectileImpact(self, entry):
        fromNP = entry.getFromNodePath()
        proj = fromNP.getPythonTag(TAG_OWNER)

        intoNP = entry.getIntoNodePath()
        if intoNP.hasPythonTag(TAG_OWNER):
            intoObj = intoNP.getPythonTag(TAG_OWNER)
            proj.impact(intoObj)
        else:
            proj.impact(None)

    def itemCollected(self, entry):
        fromNP = entry.getFromNodePath()
        player = fromNP.getPythonTag(TAG_OWNER)

        intoNP = entry.getIntoNodePath()
        item = intoNP.getPythonTag(TAG_OWNER)

        item.collected(player)

    def triggerActivated(self, entry):
        intoNP = entry.getIntoNodePath()
        trigger = intoNP.getPythonTag(TAG_OWNER)

        if self.currentLevel is not None:
            self.currentLevel.triggerActivated(trigger)

    def cleanup(self):
        if self.currentLevel is not None:
            self.currentLevel.cleanup()
            self.currentLevel = None

        if self.player is not None:
            self.player.cleanup()
            self.player = None

    def quit(self):
        self.cleanup()

        base.userExit()

game = Game()
game.run()
