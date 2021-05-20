from panda3d.core import Shader

from GameObject import GameObject

from CommonValues import *

class Item(GameObject):
    def __init__(self, pos, auraModel, contents):
        GameObject.__init__(self, pos, auraModel, None, 100, 0, "item", 1, 0)

        self.actor.setBillboardAxis()
        self.actor.setTransparency(True)
        self.actor.setLightOff(1)

        self.weaponCollider.node().setFromCollideMask(0)
        self.weaponCollider.node().setIntoCollideMask(MASK_FROM_PLAYER)
        self.weaponCollider.node().modifySolid(0).setTangible(False)
        self.weaponCollider.setZ(-self.height*0.5)

        self.contents = contents
        self.contents.root.setPos(pos)

    def collected(self, collector):
        self.contents.root.detachNode()

        if hasattr(self.contents, "onCollection"):
            self.contents.onCollection(collector)

        self.health = 0

        if base.currentLevel is not None:
            if self in base.currentLevel.items:
                base.currentLevel.items.remove(self)

        self.cleanup()