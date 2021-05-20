from panda3d.core import PandaNode, Vec3

from Enemy import ChasingEnemy
from GameObject import Walker, ArmedObject, GameObject, FRICTION
from Weapon import HitscanWeapon, ProjectileWeapon, Projectile

from CommonValues import *

import random

class MeleeEnemyBasic(ChasingEnemy, Walker):
    def __init__(self):
        ChasingEnemy.__init__(self, Vec3(0, 0, 0),
                       "Models/EnemyMeleeBasic/enemyMeleeBasic",
                       {
                        "stand" : "Models/EnemyMeleeBasic/enemyMeleeBasic-stand",
                        "walk" : "Models/EnemyMeleeBasic/enemyMeleeBasic-walk",
                        "attack" : "Models/EnemyMeleeBasic/enemyMeleeBasic-attack",
                        "die" : "Models/EnemyMeleeBasic/enemyMeleeBasic-die",
                        "spawn" : "Models/EnemyMeleeBasic/enemyMeleeBasic-spawn",
                        "flinch1" : "Models/EnemyMeleeBasic/enemyMeleeBasic-flinch"
                        },
                       50,
                       7.0,
                       "walkingEnemy",
                       1,
                        steeringFootHeight = 0.5)
        Walker.__init__(self)

        self.actor.setScale(0.6)

        weapon = HitscanWeapon(MASK_INTO_PLAYER, 15, 2.0, 0.75)
        weapon.setAvailable(True)
        self.addWeapon(weapon)
        self.setCurrentWeapon(0)

        self.attackAnimsPerWeapon[self.weapons[0]] = "attack"

        self.flinchAnims = [
            "flinch1"
        ]

        self.deathSound = loader.loadSfx("Sounds/enemyDie.ogg")
        self.attackSound = loader.loadSfx("Sounds/enemyAttack.ogg")

        self.weaponNP = self.actor.attachNewNode(PandaNode("weapon"))
        self.weaponNP.setZ(self.height*0.75)

    def update(self, player, dt):
        ChasingEnemy.update(self, player, dt)
        Walker.update(self, dt)

    def runLogic(self, player, dt):
        ChasingEnemy.runLogic(self, player, dt)

        spawnControl = self.actor.getAnimControl("spawn")
        if spawnControl is not None and spawnControl.isPlaying():
            return

    def cleanup(self):
        Walker.cleanup(self)
        ChasingEnemy.cleanup(self)

class RangedEnemyBasic(ChasingEnemy, Walker):
    def __init__(self):
        ChasingEnemy.__init__(self, Vec3(0, 0, 0),
                       "Models/EnemyRangedBasic/enemyRangedBasic",
                       {
                        "stand" : "Models/EnemyRangedBasic/enemyRangedBasic-stand",
                        "walk" : "Models/EnemyRangedBasic/enemyRangedBasic-walk",
                        "attack" : "Models/EnemyRangedBasic/enemyRangedBasic-attack",
                        "die" : "Models/EnemyRangedBasic/enemyRangedBasic-die",
                        "spawn" : "Models/EnemyRangedBasic/enemyRangedBasic-spawn",
                        "strafeLeft" : "Models/EnemyRangedBasic/enemyRangedBasic-strafeLeft",
                        "strafeRight" : "Models/EnemyRangedBasic/enemyRangedBasic-strafeRight",
                        "flinch1" : "Models/EnemyRangedBasic/enemyRangedBasic-flinch"
                        },
                       20,
                       5.0,
                       "walkingEnemy",
                       1,
                        steeringFootHeight = 0.5)
        Walker.__init__(self)

        self.movementNames.append("strafeLeft")
        self.movementNames.append("strafeRight")

        self.actor.setScale(0.6)

        projectile = Projectile("Models/EnemyRangedBasic/shot", MASK_INTO_PLAYER, 20, 10, 10, 0.3, 1.0, 0, 0)
        weapon = ProjectileWeapon(projectile)
        weapon.desiredRange = 15
        weapon.setAvailable(True)
        self.addWeapon(weapon)
        self.setCurrentWeapon(0)

        self.attackAnimsPerWeapon[self.weapons[0]] = "attack"

        self.flinchAnims = [
            "flinch1"
        ]

        self.deathSound = loader.loadSfx("Sounds/enemyDie.ogg")
        self.attackSound = loader.loadSfx("Sounds/enemyAttack.ogg")

        self.weaponNP = self.actor.attachNewNode(PandaNode("weapon"))
        self.weaponNP.setZ(self.height*0.75)

        self.minStrafeInterval = 3
        self.maxStrafeInterval = 7
        self.strafeSpeed = 10
        self.resetStrafeIntervalTimer()
        self.strafeDuration = 0.2
        self.strafeTimer = 0

    def resetStrafeIntervalTimer(self):
        self.strafeIntervalTimer = random.uniform(self.minStrafeInterval, self.maxStrafeInterval)

    def update(self, player, dt):
        ChasingEnemy.update(self, player, dt)
        Walker.update(self, dt)

        if not self.inControl:
            self.strafeTimer = 0

    def runLogic(self, player, dt):
        spawnControl = self.actor.getAnimControl("spawn")
        if spawnControl is not None and spawnControl.isPlaying():
            return

        if self.strafeTimer > 0:
            self.strafeTimer -= dt
            if self.strafeTimer <= 0:
                self.actor.loop("stand")
        else:
            ChasingEnemy.runLogic(self, player, dt)

            self.strafeIntervalTimer -= dt
            if self.strafeIntervalTimer <= 0:
                self.resetStrafeIntervalTimer()
                if random.choice([True, False]):
                    direction = 1
                    anim = "strafeRight"
                else:
                    direction = -1
                    anim = "strafeLeft"
                self.velocity = self.root.getQuat(render).getRight()*direction*self.strafeSpeed
                self.actor.loop(anim)
                self.walking = True
                self.strafeTimer = self.strafeDuration

    def cleanup(self):
        Walker.cleanup(self)
        ChasingEnemy.cleanup(self)