"""
In this script there are majority of the classes BombDash.
But nevertheless a smaller part of classes are in other scripts.

And also this script may contain some functions, constants, etc.
"""
import sys
import math
import random
import urllib
import bs
import bsUtils
import bsVector
import bsInternal
import settings


BD_INTERNAL_URL = 'http://bombdash.net/other/BombSquad/server/server/' \
    + 'internal.php'


class PortalFactory(object):

    def __init__(self):
        self.shitModel = bs.getModel('box')
        self.turretModel = bs.getModel('turret')
        self.badrockModel = bs.getModel('badrock')
        self.turretClosedModel = bs.getModel('turret_closed')
        self.companionCubeModel = bs.getModel('companionCube')

        self.weightCubeTex = bs.getTexture('weightCube')
        self.minecraftTex = bs.getTexture('MinecraftTex')
        self.companionCubeTex = bs.getTexture('companionCube')

        self.activateSound = bs.getSound('activateBeep')

        self.legoMaterial = bs.Material()
        self.legoMaterial.addActions(
            conditions=(('theyHaveMaterial', self.legoMaterial)),
            actions=('message', 'ourNode', 'atConnect', LegoConnect()))

        self.legoMaterial.addActions(
            conditions=(('theyHaveMaterial',
                         bs.getSharedObject('playerMaterial'))),
            actions=('message', 'ourNode', 'atConnect',
                     LegoMessage()))

        self.impactBlastMaterial = bs.Material()
        self.impactBlastMaterial.addActions(
            conditions=(('weAreOlderThan', 200),
                        'and', ('theyAreOlderThan', 200),
                        'and', ('evalColliding',),
                        'and', (('theyHaveMaterial',
                                 bs.getSharedObject('footingMaterial')),
                                'or', ('theyHaveMaterial',
                                       bs.getSharedObject('objectMaterial')))),
            actions=(('message', 'ourNode', 'atConnect', ImpactMessage())))


class SplatMessage(object):
    pass


class ImpactMessage(object):
    pass


class LegoConnect(object):
    pass


class LegoMessage(object):
    pass


class BlackHoleMessage(object):
    pass


class ParticlesCircle(object):
    pass


class TurretImpactMessage(object):
    pass


class dirtBombMessage(object):
    pass


class FireMessage(object):
    pass


class UltraPunch(bs.Actor):

    def __init__(self, radius=2, speed=500, position=(0, 0, 0)):
        bs.Actor.__init__(self)
        self.radius = radius
        self.position = position
        upim = bs.getSharedObject('upim')

        self.ultraPunchMaterial = bs.Material()
        self.ultraPunchMaterial.addActions(
            conditions=(('theyHaveMaterial', upim)),
            actions=(('modifyPartCollision', 'collide', True),
                     ('modifyPartCollision', 'physical', False)))

        self.ultraPunchMaterial.addActions(
            conditions=(('theyDontHaveMaterial', upim)),
            actions=(('modifyPartCollision', 'collide', True),
                     ('modifyPartCollision', 'physical', True)))

        self.node = bs.newNode('region', attrs={
            'position': (self.position[0],
                         self.position[1],
                         self.position[2]),
            'scale': (0.1, 0.1, 0.1),
            'type': 'sphere',
            'materials': [self.ultraPunchMaterial]})

        self.visualRadius = bs.newNode('shield', attrs={
            'position': self.position,
            'color': (0.3, 0, 0),
            'radius': 0.1})

        bs.animate(self.visualRadius, 'radius',
                   {0: 0, speed: self.radius*2})

        scale = {0: (0, 0, 0), speed: (self.radius, self.radius, self.radius)}
        bs.animateArray(self.node, 'scale', 3, scale, True)

        bs.gameTimer(speed+1, self.node.delete)
        bs.gameTimer(speed+1, self.visualRadius.delete)


class ShockWave(bs.Actor):

    def __init__(self, position=(0, 1, 0), radius=2, speed=100):
        bs.Actor.__init__(self)
        self.radius = radius
        self.position = position
        self.s = None

        self.shockWaveMaterial = bs.Material()
        self.shockWaveMaterial.addActions(
            conditions=(('theyHaveMaterial',
                         bs.getSharedObject('playerMaterial'))),
            actions=(('modifyPartCollision', 'collide', True),
                     ('modifyPartCollision', 'physical', False),
                     ('call', 'atConnect', self.touchedSpaz)))

        self.shockWaveMaterial.addActions(
            conditions=(('theyHaveMaterial',
                         bs.getSharedObject('objectMaterial')),
                        'and', ('theyDontHaveMaterial',
                                bs.getSharedObject('playerMaterial'))),
            actions=(('modifyPartCollision', 'collide', True),
                     ('modifyPartCollision', 'physical', False),
                     ('call', 'atConnect', self.touchedObj)))

        self.node = bs.newNode('region', attrs={
            'position': (self.position[0],
                         self.position[1],
                         self.position[2]),
            'scale': (0.1, 0.1, 0.1),
            'type': 'sphere',
            'materials': [self.shockWaveMaterial]})

        explosion = bs.newNode('explosion', attrs={
            'position': self.node.position,
            'radius': 1,
            'big': True,
            'color': (0.3, 0.3, 1.0)})

        def dowaves():
            self.visualRadius = bs.newNode('shield', attrs={
                'position': self.position,
                'color': (0.05, 0.05, 0.1),
                'radius': 0.05})

            bs.animate(self.visualRadius, 'radius',
                       {0: 0, speed: self.radius*2})

            bs.gameTimer(speed+1, self.visualRadius.delete)

        scale = {0: (0, 0, 0), speed: (self.radius, self.radius, self.radius)}
        bs.animateArray(self.node, 'scale', 3, scale, True)

        bs.Blast(
            position=self.position,
            blastRadius=1).autoRetain()

        bs.Call(dowaves)
        bs.gameTimer(100, bs.Call(dowaves))
        bs.gameTimer(200, bs.Call(dowaves))
        bs.gameTimer(250, explosion.delete)
        bs.gameTimer(300, bs.Call(dowaves))
        bs.gameTimer(700, self.node.delete)

    def re(self):
        try:
            self.node2.getDelegate()._punchPowerScale = self.s
        except StandardError:
            pass

    def touchedSpaz(self):
        self.node2 = bs.getCollisionInfo('opposingNode')

        def shockSpaz():
            self.node2.getDelegate().shock()

        bs.gameTimer(400, shockSpaz)

        self.s = self.node2.getDelegate()._punchPowerScale
        self.node2.getDelegate()._punchPowerScale -= 0.3

        bs.gameTimer(2000, bs.Call(self.re))

        bs.playSound(bs.getSound(random.choice(['electro1',
                                                'electro2',
                                                'electro3'])))

        self.node2.handleMessage(
            'impulse', self.node2.position[0], self.node2.position[1],
            self.node2.position[2], -self.node2.velocity[0],
            -self.node2.velocity[1], -self.node2.velocity[2],
            200, 200, 0, 0, -self.node2.velocity[0],
            -self.node2.velocity[1], -self.node2.velocity[2])

        flash = bs.newNode('flash', attrs={
            'position': self.node2.position,
            'size': 0.7,
            'color': (0, 0.4+random.random(), 1)})

        explosion = bs.newNode('explosion', attrs={
            'position': self.node2.position,
            'velocity': (self.node2.velocity[0],
                         max(-1.0, self.node2.velocity[1]),
                         self.node2.velocity[2]),
            'radius': 0.4,
            'big': True,
            'color': (0.3, 0.3, 1)})

        bs.gameTimer(400, explosion.delete)

        bs.emitBGDynamics(
            position=self.node2.position,
            count=20,
            scale=0.5,
            spread=0.5,
            chunkType='spark')

        bs.gameTimer(60, flash.delete)

    def touchedObj(self):
        node = bs.getCollisionInfo('opposingNode')
        bs.playSound(bs.getSound(random.choice(['electro1',
                                                'electro2',
                                                'electro3'])))

        node.handleMessage(
            'impulse', node.position[0]+random.uniform(-2, 2),
            node.position[1]+random.uniform(-2, 2),
            node.position[2]+random.uniform(-2, 2),
            -node.velocity[0]+random.uniform(-2, 2),
            -node.velocity[1]+random.uniform(-2, 2),
            -node.velocity[2]+random.uniform(-2, 2),
            100, 100, 0, 0, -node.velocity[0]+random.uniform(-2, 2),
            -node.velocity[1]+random.uniform(-2, 2),
            -node.velocity[2]+random.uniform(-2, 2))

        try:
            flash = bs.newNode('flash', attrs={
                'position': node.position,
                'size': 0.4,
                'color': (0, 0.4+random.random(), 1)})
        except AttributeError:
            pass

        try:
            explosion = bs.newNode('explosion', attrs={
                'position': node.position,
                'velocity': (node.velocity[0],
                             max(-1.0, node.velocity[1]),
                             node.velocity[2]),
                'radius': 0.4,
                'big': True,
                'color': (0.3, 0.3, 1)})
        except AttributeError:
            pass

        bs.gameTimer(400, explosion.delete)

        bs.emitBGDynamics(
            position=node.position,
            count=20,
            scale=0.5,
            spread=0.5,
            chunkType='spark')

        bs.gameTimer(60, flash.delete)

    def delete(self):
        self.node.delete()
        self.visualRadius.delete()


class Apple(bs.Actor):

    def __init__(self, position=(0, 6, 0)):
        bs.Actor.__init__(self)

        self.node = bs.newNode('prop', delegate=self, attrs={
            'position': position,
            'model': bs.getModel('apple'),
            'lightModel': bs.getModel('apple'),
            'body': 'box',
            'modelScale': 0.8,
            'shadowSize': 0.5,
            'reflection': 'soft',
            'colorTexture': bs.getTexture('apple'),
            'materials': (bs.getSharedObject('footingMaterial'),
                          bs.getSharedObject('objectMaterial'))})

    def handleMessage(self, m):
        if isinstance(m, bs.DieMessage):
            if self.node.exists():
                self.node.delete()

        elif isinstance(m, bs.OutOfBoundsMessage):
            self.node.handleMessage(bs.DieMessage())

        elif isinstance(m, bs.HitMessage):
            m.srcNode.handleMessage(
                'impulse', m.pos[0], m.pos[1], m.pos[2],
                m.velocity[0], m.velocity[1], m.velocity[2],
                m.magnitude, m.velocityMagnitude, m.radius, 0,
                m.velocity[0], m.velocity[1], m.velocity[2])


class Napalm(bs.Actor):

    def __init__(self, position=(0, -0.1, 0), radius=1.2, time=5000):
        bs.Actor.__init__(self)
        self.radius = radius
        self.position = position if not position == (0, -0.1, 0) \
            else (random.uniform(-4, 4), 0.1, random.uniform(-4, 4))

        self.stop = False
        self.sounds = [bs.getSound('fire1'),
                       bs.getSound('fire2'),
                       bs.getSound('fire3')]

        self.spawnSmoke(pos=self.position)
        self.spawnFire(pos=self.position)
        self.doSound(pos=self.position)

        self.firem = bs.Material()
        self.firem.addActions(
            conditions=(('theyHaveMaterial',
                         bs.getSharedObject('playerMaterial'))),
            actions=(('modifyPartCollision', 'collide', True),
                     ('modifyPartCollision', 'physical', False),
                     ('call', 'atConnect', self.touchedSpaz)))

        self.firem.addActions(
            conditions=(('theyHaveMaterial',
                         bs.getSharedObject('objectMaterial')),
                        'and', ('theyDontHaveMaterial',
                                bs.getSharedObject('playerMaterial'))),
            actions=(('modifyPartCollision', 'collide', True),
                     ('modifyPartCollision', 'physical', False),
                     ('call', 'atConnect', self.touchedObj)))

        self.node = bs.newNode('region', attrs={
            'position': (self.position[0], self.position[1], self.position[2]),
            'scale': (0.1, 0.1, 0.1),
            'type': 'sphere',
            'materials': [self.firem]})

        scale = {
            0: (0, 0, 0),
            100: (self.radius/2, self.radius/2, self.radius/2)
        }

        bs.animateArray(self.node, 'scale', 3, scale, True)

        self.fireLight = bs.newNode('light', attrs={
            'position': self.position,
            'color': (1, 0.4, 0),
            'volumeIntensityScale': 0.1,
            'intensity': 0.8,
            'radius': radius/5})

        intensity = {
            0: random.uniform(0.8, 1.5), 100: random.uniform(0.8, 1.5),
            200: random.uniform(0.8, 1.5), 300: random.uniform(0.8, 1.5),
            400: random.uniform(0.8, 1.5), 500: random.uniform(0.8, 1.5),
            600: random.uniform(0.8, 1.5), 700: random.uniform(0.8, 1.5),
            800: random.uniform(0.8, 1.5), 900: random.uniform(0.8, 1.5),
            1000: random.uniform(0.8, 1.5), 1100: random.uniform(0.8, 1.5),
            1200: random.uniform(0.8, 1.5), 1300: random.uniform(0.8, 1.5)
        }

        self.c2 = bs.animate(self.fireLight, 'intensity', intensity, True)

        color = {
            0: (1, 0.4, 0), 100: (1, 0.3, 0),
            200: (1, 0.6, 0), 300: (1, 0.5, 0),
            400: (1, 0.2, 0), 500: (1, 0.4, 0),
            600: (1, 0.3, 0)
        }

        self.c3 = bs.animateArray(self.fireLight, 'color', 3, color, True)

        self.scorch = bs.newNode('scorch', attrs={
            'position': self.position,
            'size': radius,
            'big': True,
            'color': (0.1, 0.0, 0.0)})

        bs.gameTimer(time, bs.Call(self.handleMessage, bs.DieMessage()))

    def touchedSpaz(self):
        node = bs.getCollisionInfo('opposingNode')
        if node.getNodeType() == 'spaz':
            if not node.getDelegate().fired:
                node.getDelegate().fire()

    def touchedObj(self):
        node = bs.getCollisionInfo('opposingNode')
        if node.exists():
            try:
                node.getDelegate().explode()
            except:
                pass

    def spawnSmoke(self, pos):
        pos = (pos[0] + random.uniform(-self.radius/2, self.radius/2),
               pos[1]+0.2,
               pos[2] + random.uniform(-self.radius/2, self.radius/2))

        bs.emitBGDynamics(
            position=pos,
            velocity=(0, 0, 0),
            count=1,
            emitType='tendrils',
            tendrilType='smoke')

        if not self.stop:
            bs.gameTimer(1800, bs.Call(self.spawnSmoke, pos=self.position))

    def doSound(self, pos):
        bs.playSound(random.choice(self.sounds), position=pos)
        if not self.stop:
            bs.gameTimer(480, bs.Call(self.doSound, pos=self.position))

    def spawnFire(self, pos):
        pos = (pos[0]+random.uniform(-self.radius/2, self.radius/2),
               pos[1],
               pos[2]+random.uniform(-self.radius/2, self.radius/2))

        if random.random() < 0.08:
            bs.emitBGDynamics(
                position=pos,
                velocity=(0, 7, 0),
                count=int(10 + random.random()*8),
                scale=random.random()*0.4,
                spread=random.random()*0.2,
                chunkType='spark')
        else:
            bs.emitBGDynamics(
                position=pos,
                velocity=(0, 7, 0),
                count=int(5 + random.random()*5),
                scale=random.random()*2,
                spread=random.random()*0.2,
                chunkType='sweat')

        if not self.stop:
            bs.gameTimer(10, bs.Call(self.spawnFire, self.position))

    def handleMessage(self, m):
        if isinstance(m, bs.DieMessage):
            self.stop = True
            if self.c2 is not None:
                self.c2.delete()

            if self.c3 is not None:
                self.c3.delete()

            # self.c4.delete()
            if self.node is not None and self.node.exists():
                self.node.delete()

            if self.fireLight is not None and self.fireLight.exists():
                self.fireLight.delete()

            bs.animate(self.scorch, 'presence',
                       {0: self.scorch.presence, 8000: 0})

            bs.gameTimer(8001, self.scorch.delete)


class Shovel(bs.Actor):

    def __init__(self, position=(0, 1, 0), owner=None):
        bs.Actor.__init__(self)
        owner = bs.getActivity().players[0].actor.node

        self.node = bs.newNode('prop', delegate=self, attrs={
            'position': position,
            'model': bs.getModel('shovel'),
            'lightModel': bs.getModel('shovel'),
            'body': 'landMine',
            'shadowSize': 0.5,
            'reflection': 'soft',
            'colorTexture': bs.getTexture('shovel'),
            'materials': (bs.getSharedObject('footingMaterial'),
                          bs.getSharedObject('objectMaterial'))})

        m = bs.newNode('math', owner=self.node, attrs={
            'input1': (1, 0, 0),
            'operation': 'add'})

        owner.connectAttr('torsoPosition', m, 'input2')
        m.connectAttr('output', self.node, 'position')

    def handleMessage(self, m):
        if isinstance(m, bs.DieMessage):
            if self.node.exists():
                self.node.delete()

        elif isinstance(m, bs.OutOfBoundsMessage):
            self.node.handleMessage(bs.DieMessage())

        elif isinstance(m, bs.HitMessage):
            m.srcNode.handleMessage(
                'impulse', m.pos[0], m.pos[1], m.pos[2],
                m.velocity[0], m.velocity[1], m.velocity[2],
                m.magnitude, m.velocityMagnitude, m.radius,
                0, m.velocity[0], m.velocity[1], m.velocity[2])


class Nuke(bs.Actor):

    def __init__(self, position=(0, 10, 0)):
        bs.Actor.__init__(self)
        bs.getActivity().stdEpic = bs.getSharedObject('globals').slowMotion

        self.impactBlastMaterial = bs.Material()
        self.impactBlastMaterial.addActions(
            conditions=(('weAreOlderThan', 200),
                        'and', ('theyAreOlderThan', 200),
                        'and', ('evalColliding',),
                        'and', (('theyHaveMaterial',
                                 bs.getSharedObject('footingMaterial')),
                                'or', ('theyHaveMaterial',
                                       bs.getSharedObject('objectMaterial')))),
            actions=(('message', 'ourNode', 'atConnect', ImpactMessage())))

        self.node = bs.newNode('prop', delegate=self, attrs={
            'position': position,
            'model': bs.getModel('nuke'),
            'lightModel': bs.getModel('nuke'),
            'body': 'box',
            'modelScale': 1.4,
            'bodyScale': 1.4,
            'shadowSize': 0.5,
            'reflection': 'soft',
            'extraAcceleration': (0, 10, 0),
            'colorTexture': bs.getTexture('nuke'),
            'materials': (bs.getSharedObject('footingMaterial'),
                          bs.getSharedObject('objectMaterial'),
                          self.impactBlastMaterial)})

        bs.playSound(bs.getSound('nukeFalling'))
        bs.getSharedObject('globals').slowMotion = True
        bs.gameTimer(2000, self.off)

    def off(self):
        bs.getSharedObject('globals').slowMotion = bs.getActivity().stdEpic

    def handleMessage(self, m):
        if isinstance(m, bs.DieMessage):
            if self.node.exists():
                self.node.delete()

        elif isinstance(m, bs.OutOfBoundsMessage):
            self.node.handleMessage(bs.DieMessage())

        elif isinstance(m, ImpactMessage):
            bs.Blast(
                position=self.node.position,
                blastRadius=40).autoRetain()

            Toxic(
                position=self.node.position,
                radius=10,
                time=15000)

            self.node.handleMessage(bs.DieMessage())

        elif isinstance(m, bs.HitMessage):
            m.srcNode.handleMessage(
                'impulse', m.pos[0], m.pos[1], m.pos[2],
                m.velocity[0], m.velocity[1], m.velocity[2],
                m.magnitude, m.velocityMagnitude, m.radius,
                0, m.velocity[0], m.velocity[1], m.velocity[2])


class babyNuke(bs.Actor):

    def __init__(self, position=(0, 10, 0), velocity=(0, 0, 0)):
        bs.Actor.__init__(self)
        self.position = position
        self.velocity = velocity

        self.impactBlastMaterial = bs.Material()
        self.impactBlastMaterial.addActions(
            conditions=(('weAreOlderThan', 200),
                        'and', ('theyAreOlderThan', 200),
                        'and', ('evalColliding',),
                        'and', (('theyHaveMaterial',
                                 bs.getSharedObject('footingMaterial')),
                                'or', ('theyHaveMaterial',
                                       bs.getSharedObject('objectMaterial')))),
            actions=(('message', 'ourNode', 'atConnect', ImpactMessage())))

        self.node = bs.newNode('prop', delegate=self, attrs={
            'position': self.position,
            'model': bs.getModel('nuke'),
            'lightModel': bs.getModel('nuke'),
            'body': 'box',
            'velocity': self.velocity,
            'modelScale': 0.8,
            'bodyScale': 0.8,
            'shadowSize': 0.5,
            'reflection': 'soft',
            'extraAcceleration': (0, 10, 0),
            'colorTexture': bs.getTexture('black'),
            'materials': (bs.getSharedObject('footingMaterial'),
                          bs.getSharedObject('objectMaterial'),
                          self.impactBlastMaterial)})

        bs.playSound(bs.getSound('glass'))

    def handleMessage(self, m):
        if isinstance(m, bs.DieMessage):
            if self.node.exists():
                self.node.delete()

        elif isinstance(m, bs.OutOfBoundsMessage):
            self.node.handleMessage(bs.DieMessage())

        elif isinstance(m, ImpactMessage):
            bs.Blast(
                position=self.node.position,
                blastType='impact').autoRetain()

            bs.playSound(bs.getSound('bomb2'))
            self.node.handleMessage(bs.DieMessage())

        elif isinstance(m, bs.HitMessage):
            m.srcNode.handleMessage(
                'impulse', m.pos[0], m.pos[1], m.pos[2],
                m.velocity[0], m.velocity[1], m.velocity[2],
                m.magnitude, m.velocityMagnitude, m.radius, 0,
                m.velocity[0], m.velocity[1], m.velocity[2])


class Number(bs.Actor):

    def __init__(self, position=(0, 1, 0), num=0, velocity=(0, 0, 0)):
        bs.Actor.__init__(self)

        if num == 1:
            self.node = bs.newNode('prop', delegate=self, attrs={
                'position': position,
                'model': bs.getModel('one'),
                'lightModel': bs.getModel('one'),
                'body': 'box',
                'velocity': velocity,
                'modelScale': 0.8,
                'bodyScale': 0.5,
                'shadowSize': 0.5,
                'reflection': 'soft',
                'colorTexture': bs.getTexture('greenTerminal'),
                'materials': (bs.getSharedObject('footingMaterial'),
                              bs.getSharedObject('objectMaterial'))})
        else:
            self.node = bs.newNode('prop', delegate=self, attrs={
                'position': position,
                'model': bs.getModel('zero'),
                'lightModel': bs.getModel('zero'),
                'body': 'box',
                'velocity': velocity,
                'modelScale': 0.8,
                'bodyScale': 0.5,
                'shadowSize': 0.5,
                'reflection': 'soft',
                'colorTexture': bs.getTexture('greenTerminal'),
                'materials': (bs.getSharedObject('footingMaterial'),
                              bs.getSharedObject('objectMaterial'))})

    def handleMessage(self, m):
        if isinstance(m, bs.DieMessage):
            if self.node.exists():
                self.node.delete()

        elif isinstance(m, bs.OutOfBoundsMessage):
            self.node.handleMessage(bs.DieMessage())

        elif isinstance(m, bs.HitMessage):
            m.srcNode.handleMessage(
                'impulse', m.pos[0], m.pos[1], m.pos[2],
                m.velocity[0], m.velocity[1], m.velocity[2],
                m.magnitude, m.velocityMagnitude, m.radius, 0,
                m.velocity[0], m.velocity[1], m.velocity[2])


class Artillery(object):

    def __init__(self, position=(0, 1, 0), target=None,
                 owner=None, bombType='impact', sourcePlayer=None):
        self.position = position
        self.owner = owner
        self.target = target
        self.bombType = bombType
        self.sourcePlayer = sourcePlayer
        self.radius = 60
        self.maxHeight = bs.getActivity().getMap().getDefBoundBox(
            'levelBounds')

        self.aimZone = bs.Material()
        self.aimZone.addActions(
            conditions=(('theyHaveMaterial',
                         bs.getSharedObject('playerMaterial'))),
            actions=(('modifyPartCollision', 'collide', True),
                     ('modifyPartCollision', 'physical', False),
                     ('call', 'atConnect', self.touchedSpaz)))

        self.node = bs.newNode('region', attrs={
            'position': self.position,
            'scale': (0.5, 0.5, 0.5),
            'type': 'sphere',
            'materials': [self.aimZone]})

        scale = {
            0: (0.5, 0.5, 0.5),
            100: (self.radius, self.radius, self.radius)
        }

        bs.animateArray(self.node, 'scale', 3, scale)

        bs.gameTimer(101, self.node.delete)
        bs.gameTimer(102, self.strike)

    def touchedSpaz(self):
        node = bs.getCollisionInfo('opposingNode')
        if self.owner is not None:
            if not node == self.owner:
                self.target = node
                self.node.materials = [bs.Material()]
                bs.gameTimer(300, self.node.delete)

    def strike(self):
        if self.target is not None:
            def launchBomb():
                if self.target is not None and self.target.exists():
                    self.pos = self.target.position
                    b = bs.Bomb(
                        position=self.position,
                        velocity=(0, 5, 0),
                        bombType=self.bombType,
                        napalm=True).autoRetain()

                    b.node.extraAcceleration = (0, 700, 0)
                    b.node.velocity = (
                        b.node.velocity[0]+(self.pos[0]-b.node.position[0]),
                        10,
                        b.node.velocity[2]+(self.pos[2]-b.node.position[2]))

                    bs.playSound(bs.getSound('Aim'))

            bs.gameTimer(100, bs.Call(launchBomb))
            bs.gameTimer(200, bs.Call(launchBomb))
            bs.gameTimer(300, bs.Call(launchBomb))
            bs.gameTimer(400, bs.Call(launchBomb))
            bs.gameTimer(500, bs.Call(launchBomb))
            bs.gameTimer(700, bs.Call(launchBomb))
            bs.gameTimer(900, bs.Call(self.drop))

    def drop(self):
        def launchBombDrop():
            bs.playSound(bs.getSound('Aim'))
            b = bs.Bomb(
                position=(self.pos[0]+(-2+random.random()*4),
                          self.maxHeight[4],
                          self.pos[2]+(-2+random.random()*4)),
                velocity=(0, -100, 0),
                bombType=self.bombType,
                sourcePlayer=self.sourcePlayer).autoRetain()

            b.node.extraAcceleration = (0, -100, 0)

        bs.gameTimer(100, bs.Call(launchBombDrop))
        bs.gameTimer(300, bs.Call(launchBombDrop))
        bs.gameTimer(500, bs.Call(launchBombDrop))
        bs.gameTimer(700, bs.Call(launchBombDrop))
        bs.gameTimer(900, bs.Call(launchBombDrop))
        bs.gameTimer(1000, bs.Call(launchBombDrop))


class Cannon(bs.Actor):

    def __init__(self, position=(0, 1, 0), velocity=(0, 0, 0), angle=0,
                 haveCharge=False, owner=None, sourcePlayer=None):
        bs.Actor.__init__(self)
        self.haveCharge = haveCharge
        self.bombType = None
        self.l = 10000
        self.bombCount = False
        self.ShotsHaveDone = 0
        self.angle = angle
        self.vel = velocity
        self.owner = owner
        self.cannonModel = bs.getModel('cannon')
        self.cannonTex = bs.getTexture('black')

        self.cannonMaterial = bs.Material()
        self.cannonMaterial.addActions(
            conditions=(('theyHaveMaterial',
                         bs.getSharedObject('objectMaterial'))),
            actions=(('call', 'atConnect', self.Charged)))

        self.node = bs.newNode('prop', delegate=self, attrs={
            'position': position,
            'velocity': velocity,
            'model': self.cannonModel,
            'body': 'crate',
            'bodyScale': 0.8,
            'shadowSize': 0.5,
            'colorTexture': self.cannonTex,
            'reflection': 'soft',
            'reflectionScale': [1.0],
            'materials': (bs.getSharedObject('footingMaterial'),
                          bs.getSharedObject('objectMaterial'),
                          self.cannonMaterial)})

    def handleMessage(self, m):
        if isinstance(m, bs.DieMessage):
            if self.node.exists():
                self.node.delete()

        elif isinstance(m, bs.OutOfBoundsMessage):
            if self.node.exists():
                self.node.delete()

        elif isinstance(m, bs.StandMessage):
            if m.node.getNodeType() == 'spaz':
                self.spazangle = m.node.angle
                self.node.handleMessage('stand', m.node.angle)

        elif isinstance(m, bs.PickedUpMessage):
            self.owner = m.node
            if m.node.getNodeType() == 'spaz':
                self.areaOfInterestRadius = m.node.areaOfInterestRadius
                m.node.areaOfInterestRadius = 13

                def off():
                    m.node.areaOfInterestRadius = self.areaOfInterestRadius

                bs.gameTimer(1000, bs.Call(off))

            if self.bombCount and not self.ShotsHaveDone == 3:
                self.shot()

            elif self.ShotsHaveDone == 3 or not self.bombCount:
                bsUtils.PopupText(
                    bs.Lstr(resource='cannonNotCharged'),
                    color=(1, 0, 0),
                    scale=1.0,
                    position=self.node.position).autoRetain()

                bs.gameTimer(2000, bs.Call(self.explode))

    def Charged(self):
        if not self.bombCount:
            node = bs.getCollisionInfo('opposingNode')
            if isinstance(node.getDelegate(), bs.Bomb):
                self.bombType = node.getDelegate().bombType

            if node is not None and self.bombType in ['impact',
                                                      'poison',
                                                      'slipper',
                                                      'dirtBomb',
                                                      'heal',
                                                      'banana',
                                                      'shockWave',
                                                      'fireBottle',
                                                      'ice',
                                                      'sticky',
                                                      'holy',
                                                      'normal']:

                if isinstance(node.getDelegate(), bs.Bomb):
                    node.handleMessage(bs.DieMessage())

                self.bombCount = True
                self.haveCharge = True
                bsUtils.PopupText(
                    bs.Lstr(resource='cannonReady'),
                    color=(0, 1, 0),
                    scale=1.0,
                    position=self.node.position).autoRetain()

    def explode(self):
        if self.node.exists():
            bs.Blast(
                position=self.node.position).autoRetain()

            self.node.handleMessage(bs.DieMessage())

    def shot(self):
        def boom():
            if self.owner is not None and self.owner.exists():
                if self.owner.getNodeType() == 'spaz':
                    p1 = self.owner.positionCenter
                    p2 = self.owner.positionForward

                direction = [p1[0]-p2[0], p2[1]-p1[1], p1[2]-p2[2]]
                direction[1] = 0.0

                mag = 10.0 / bsVector.Vector(*direction).length()
                self.vel = [v*mag for v in direction]

            self.owner.handleMessage(
                'kickBack', self.node.position[0], self.node.position[1],
                self.node.position[2], -(self.vel[0])*20, self.vel[1]*10,
                -(self.vel[2]*20), mag*20)

            b = bs.Bomb(
                position=(self.node.position[0],
                          self.node.position[1],
                          self.node.position[2]),
                velocity=(self.vel[0], 6, self.vel[2]),
                modelSize=0.5,
                bombType=self.bombType).autoRetain()

            b.node.modelScale = 0.5
            b.node.extraAcceleration = (self.vel[0]/3, 5, self.vel[2]/3)
            bsUtils.PopupText(
                bs.Lstr(resource='cannonShots', subs=[
                    ('${VALUE}', str(3-self.ShotsHaveDone))]),
                color=(1, 1, 0),
                scale=1.0,
                position=self.node.position).autoRetain()

        def shoot():
            bs.Blast(
                position=self.node.position,
                blastType='impact',
                blastRadius=0).autoRetain()

        self.ShotsHaveDone += 1
        bs.gameTimer(1050, bs.Call(shoot))
        bs.gameTimer(1000, bs.Call(boom))
        self.bombCount = False


class RailBullet(bs.Actor):

    def __init__(self, position=(0, 10, 0), velocity=(0, 0, 0)):
        bs.Actor.__init__(self)
        self.position = position
        self.velocity = velocity
        self.impactBlastMaterial = bs.Material()
        self.impactBlastMaterial.addActions(
            conditions=(('weAreOlderThan', 200),
                        'and', ('theyAreOlderThan', 200),
                        'and', ('evalColliding',),
                        'and', (('theyHaveMaterial',
                                 bs.getSharedObject('footingMaterial')),
                                'or', ('theyHaveMaterial',
                                       bs.getSharedObject('objectMaterial')))),
            actions=(('message', 'ourNode', 'atConnect', ImpactMessage()))
            )

        self.node = bs.newNode('prop', delegate=self, attrs={
            'position': self.position,
            'velocity': self.velocity,
            'model': bs.getModel('box'),
            'body': 'sphere',
            'bodyScale': 0.8,
            'modelScale': 0.8,
            'colorTexture': bs.getTexture('black'),
            'materials': (bs.getSharedObject('footingMaterial'),
                          bs.getSharedObject('objectMaterial'),
                          self.impactBlastMaterial)})

        def emitter():
            self._emit = bs.Timer(10, bs.WeakCall(self.emit), repeat=True)

        bs.gameTimer(5, emitter)

    def emit(self):
        bs.Blast(
            position=self.node.position,
            blastType='rail',
            blastRadius=1,
            notScorch=True,
            notShake=True).autoRetain()

    def handleMessage(self, m):
        if isinstance(m, bs.DieMessage):
            if self.node.exists():
                self.node.delete()
                self._emit = None

        elif isinstance(m, bs.OutOfBoundsMessage):
            if self.node.exists():
                self.node.delete()
                self._emit = None

        elif isinstance(m, ImpactMessage):
            bs.Blast(
                position=self.node.position,
                blastType='impact').autoRetain()

            self.node.handleMessage(bs.DieMessage())

    def boom(self):
        if self.owner is not None and self.owner.exists():
            if self.owner.getNodeType() == 'spaz':
                p1 = self.owner.positionCenter
                p2 = self.owner.positionForward

            direction = [p1[0]-p2[0], p2[1]-p1[1], p1[2]-p2[2]]
            direction[1] = 0.0
            mag = 10.0 / bsVector.Vector(*direction).length()
            self.vel = [v*mag for v in direction]

        b = RailBullet(
            position=(self.node.position[0],
                      self.node.position[1]-0.4,
                      self.node.position[2]),
            velocity=(self.vel[0], 0, self.vel[2])).autoRetain()

        b.node.modelScale = 0.05
        b.node.extraAcceleration = (self.vel[0]*900, -1000, self.vel[2]*900)


class MagicSpell(bs.Actor):

    def __init__(self, position=(0, 10, 0), velocity=(0, 0, 0), owner=None):
        bs.Actor.__init__(self)
        self.owner = owner
        self.position = position
        self.velocity = velocity
        self.lastJumpTime = -9999
        self._jumpCooldown = 250
        self.m = None
        self.x = None
        self.y = None
        self.z = None
        self.s = 0
        self.r = 0.2
        self.isItSpaz = False
        self.maxR = 0.2
        self.revers = False
        self.off = False

        self.impactBlastMaterial = bs.Material()
        self.impactBlastMaterial.addActions(
            conditions=(('weAreOlderThan', 200),
                        'and', ('theyAreOlderThan', 200),
                        'and', ('evalColliding',),
                        'and', (('theyHaveMaterial',
                                 bs.getSharedObject('footingMaterial')),
                                'or', ('theyHaveMaterial',
                                       bs.getSharedObject('objectMaterial')))),
            actions=(('message', 'ourNode', 'atConnect', ImpactMessage())))

        self.node = bs.newNode('prop', delegate=self, attrs={
            'position': self.position,
            'model': bs.getModel('shockWaveBomb'),
            'lightModel': bs.getModel('shockWaveBomb'),
            'body': 'capsule',
            'velocity': self.velocity,
            'modelScale': 0.6,
            'bodyScale': 0.9,
            'shadowSize': 0.1,
            'reflection': 'soft',
            'reflectionScale': [2.0],
            'extraAcceleration': (0, 18, 0),
            'colorTexture': bs.getTexture('lava'),
            'materials': (bs.getSharedObject('footingMaterial'),
                          bs.getSharedObject('objectMaterial'),
                          self.impactBlastMaterial)})

        self.lightNode = bs.newNode('light', attrs={
            'position': self.position,
            'color': (1, 0.8, 0),
            'radius': 0.1,
            'volumeIntensityScale': 15.0})

        self.node.connectAttr('position', self.lightNode, 'position')
        self._emit = bs.Timer(15, bs.WeakCall(self.emit), repeat=True)
        self._emit1 = bs.Timer(35, bs.WeakCall(self.spawnParticles),
                               repeat=True)

        

        bs.playSound(bs.getSound('spell'))

    def spawnParticles(self):
        self.x = self.node.position[0]
        self.y = self.node.position[1]
        self.z = self.node.position[2]
        sin = math.sin(self.s) * self.r
        cos = math.cos(self.s) * self.r
        self.s += 0.4

        if self.r < 0:
            self.revers = True
        elif self.r > self.maxR:
            self.revers = False

        bs.emitBGDynamics(
            position=(self.x+cos, self.y, self.z+sin),
            velocity=(0, 0, 0),
            count=5,
            scale=0.4,
            spread=0,
            chunkType='spark')

    def emit(self):
        bs.emitBGDynamics(
            position=self.node.position,
            velocity=self.node.velocity,
            count=10,
            scale=0.4,
            spread=0.01,
            chunkType='spark')

    def impactSpaz(self):
        node = bs.getCollisionInfo('opposingNode')
        if node is not None:
            if isinstance(node.getDelegate(), bs.Spaz):
                self.node.handleMessage(bs.DieMessage())

                def setSpeed(val):
                    if node.exists():
                        setattr(node, 'hockey', val)

                setSpeed(True)

                self.shield = bs.newNode('scorch', owner=node, attrs={
                    'color': (random.random()*20,
                              random.random()*20,
                              random.random()*20),
                    'size': 0.4})

                bs.animate(self.shield, 'size',
                           {0: 1, 760: 0.4, 1520: 1}, loop=True)

                bs.animate(self.shield, 'presence',
                           {0: 1, 260: 0.4, 520: 1}, loop=True)

                node.connectAttr('positionCenter', self.shield, 'position')

                self.shield1 = bs.newNode('scorch', owner=node, attrs={
                    'color': (random.random()*20,
                              random.random()*20,
                              random.random()*20),
                    'size': 0.4})

                bs.animate(self.shield1, 'size',
                           {0: 0.7, 380: 0.4, 760: 0.7, 1440: 1, 1520: 0.7},
                           loop=True)

                bs.animate(self.shield1, 'presence',
                           {0: 0.7, 130: 0.4, 260: 0.7, 390: 1, 520: 0.7},
                           loop=True)

                node.connectAttr('positionCenter', self.shield1, 'position')

                self.shield2 = bs.newNode('scorch', owner=node, attrs={
                    'color': (random.random()*20,
                              random.random()*20,
                              random.random()*20),
                    'size': 0.4})

                bs.animate(self.shield2, 'size',
                           {0: 0.4, 380: 0.7, 760: 1, 1440: 0.7, 1520: 0.4},
                           loop=True)

                bs.animate(self.shield2, 'presence',
                           {0: 0.4, 130: 0.7, 260: 1, 390: 0.7, 520: 0.4},
                           loop=True)

                node.connectAttr('positionCenter', self.shield2, 'position')

                def onJumpPressSpec():
                    if not node.exists():
                        return

                    t = bs.getGameTime()
                    if t - self.lastJumpTime >= self._jumpCooldown \
                            and not self.off \
                            and not (node.knockout > 0.0 or node.frozen > 0):
                        node.jumpPressed = True
                        self.lastJumpTime = t
                        self._jumpCooldown = 750
                        node.handleMessage(
                            'impulse', node.position[0], node.position[1],
                            node.position[2], 0, 0, 0, 200, 200, 0, 0, 0, 1, 0)

                node.getDelegate().getPlayer().assignInputCall(
                    'jumpPress', onJumpPressSpec)

                if node is not None and node.exists():
                    node.getDelegate().superHealth(True)

                def spazEmit():
                    try:
                        bs.emitBGDynamics(
                            position=(node.position[0],
                                      node.position[1]-0.3,
                                      node.position[2]),
                            velocity=node.velocity,
                            count=15,
                            scale=0.4,
                            spread=0.01,
                            chunkType='spark')
                    except:
                        pass

                self.spaz_emit = bs.Timer(15, bs.Call(spazEmit), repeat=True)

                def offAllEffects():
                    self.shield.delete()
                    self.shield = None
                    self.shield1.delete()
                    self.shield1 = None
                    self.shield2.delete()
                    self.shield2 = None
                    self.off = True
                    self.spaz_emit = None
                    setSpeed(False)
                    if node is not None and node.exists():
                        try:
                            node.getDelegate().connectControlsToPlayer()
                            node.getDelegate().superHealth(False)
                        except:
                            pass

                bs.gameTimer(15000, bs.Call(offAllEffects))
            else:
                self.node.handleMessage(bs.DieMessage())

    def handleMessage(self, m):
        if isinstance(m, bs.DieMessage):
            if self.node.exists():
                self.node.delete()
                self.lightNode.delete()
                self._emit = None
                self._emit1 = None

        elif isinstance(m, bs.OutOfBoundsMessage):
            self.node.handleMessage(bs.DieMessage())

        elif isinstance(m, bs.ImpactMessage):
            self.impactSpaz()

        elif isinstance(m, bs.HitMessage):
            self.impactSpaz()


class DirtRain(object):

    def __init__(self):
        x = -10
        while x < 10:
            z = -10
            x += 1
            while z < 10:
                z += 1
                Clay(
                    position=(x+random.random(),
                              1,
                              z+random.random()),
                    velocity=(random.random(),
                              random.random(),
                              random.random())).autoRetain()


class Portal(bs.Actor):

    def __init__(self, position1=(0, 1, 0), position2=(3, 1, 0),
                 color=(random.random(), random.random(), random.random()),
                 isBomb=False):
        bs.Actor.__init__(self)
        self.radius = 1.1
        self.position1 = position1
        self.position2 = position2
        self.cooldown = False
        self.alreadyTeleported = False

        self.portal1Material = bs.Material()
        self.portal1Material.addActions(
            conditions=(('theyHaveMaterial',
                         bs.getSharedObject('playerMaterial'))),
            actions=(('modifyPartCollision', 'collide', True),
                     ('modifyPartCollision', 'physical', False),
                     ('call', 'atConnect', self.Portal1)))

        self.portal2Material = bs.Material()
        self.portal2Material.addActions(
            conditions=(('theyHaveMaterial',
                         bs.getSharedObject('playerMaterial'))),
            actions=(('modifyPartCollision', 'collide', True),
                     ('modifyPartCollision', 'physical', False),
                     ('call', 'atConnect', self.Portal2)))

        self.portal1Material.addActions(
            conditions=(('theyHaveMaterial',
                         bs.getSharedObject('objectMaterial')),
                        'and', ('theyDontHaveMaterial',
                                bs.getSharedObject('playerMaterial'))),
            actions=(('modifyPartCollision', 'collide', True),
                     ('modifyPartCollision', 'physical', False),
                     ('call', 'atConnect', self.objPortal1)))

        self.portal2Material.addActions(
            conditions=(('theyHaveMaterial',
                         bs.getSharedObject('objectMaterial')),
                        'and', ('theyDontHaveMaterial',
                                bs.getSharedObject('playerMaterial'))),
            actions=(('modifyPartCollision', 'collide', True),
                     ('modifyPartCollision', 'physical', False),
                     ('call', 'atConnect', self.objPortal2)))

        self.node1 = bs.newNode('region', attrs={
            'position': (self.position1[0],
                         self.position1[1],
                         self.position1[2]),
            'scale': (0.1, 0.1, 0.1),
            'type': 'sphere',
            'materials': [self.portal1Material]})

        self.visualRadius1 = bs.newNode('shield', attrs={
            'position': self.position1,
            'color': color,
            'radius': 0.1})

        scale = {
            0: (0, 0, 0),
            500: (self.radius, self.radius, self.radius)
        }

        bs.animate(self.visualRadius1, 'radius', {0: 0, 500: self.radius*2})
        bs.animateArray(self.node1, 'scale', 3, scale)

        self.node2 = bs.newNode('region', attrs={
            'position': (self.position2[0],
                         self.position2[1],
                         self.position2[2]),
            'scale': (0.1, 0.1, 0.1),
            'type': 'sphere',
            'materials': [self.portal2Material]})

        self.visualRadius2 = bs.newNode('shield', attrs={
            'position': self.position2,
            'color': color,
            'radius': 0.1})

        scale = {
            0: (0, 0, 0),
            500: (self.radius, self.radius, self.radius)
        }

        bs.animate(self.visualRadius2, 'radius', {0: 0, 500: self.radius*2})
        bs.animateArray(self.node2, 'scale', 3, scale)

        if isBomb:
            bs.gameTimer(10000, self.node1.delete)
            bs.gameTimer(10000, self.visualRadius1.delete)
            bs.gameTimer(10000, self.node2.delete)
            bs.gameTimer(10000, self.visualRadius2.delete)

    def cooldown1(self, unique=False):
        self.cooldown = True

        def off():
            self.cooldown = False

        if unique:
            bs.gameTimer(1000, off)
        else:
            bs.gameTimer(10, off)

    def Portal1(self):
        node = bs.getCollisionInfo('opposingNode')

        def cooldown():
            self.alreadyTeleported = False

        if not self.alreadyTeleported:
            node.handleMessage(bs.StandMessage(
                position=self.node2.position))

            self.alreadyTeleported = True
            bs.gameTimer(1000, bs.Call(cooldown))

    def Portal2(self):
        node = bs.getCollisionInfo('opposingNode')

        def cooldown():
            self.alreadyTeleported = False

        if not self.alreadyTeleported:
            node.handleMessage(bs.StandMessage(
                position=self.node1.position))

            self.alreadyTeleported = True
            bs.gameTimer(1000, bs.Call(cooldown))

    def objPortal1(self):
        node = bs.getCollisionInfo('opposingNode')
        if not self.cooldown:
            try:
                a = [f.actor.node.holdNode for f in bs.getActivity().players]
            except:
                a = None

            self.cooldown1()
        else:
            a = None

        if a is not None and node not in a and node.exists():
            v = node.velocity
            if not self.cooldown and node.getNodeType() == 'spaz':
                node.position = self.position2
                self.cooldown1()
            else:
                node.position = self.position2
                self.cooldown1()

            def vel():
                if node.exists():
                    node.velocity = v

            bs.gameTimer(10, vel)

    def objPortal2(self):
        node = bs.getCollisionInfo('opposingNode')
        if not self.cooldown:
            try:
                a = [f.actor.node.holdNode for f in bs.getActivity().players]
            except:
                a = None

            self.cooldown1()
        else:
            a = None

        if a is not None and node not in a and node.exists():
            v = node.velocity
            if not self.cooldown and node.getNodeType() == 'spaz':
                node.position = self.position1
                self.cooldown1()
            else:
                node.position = self.position1
                self.cooldown1()

            def vel():
                if node.exists():
                    node.velocity = v

            bs.gameTimer(10, vel)


class Toxic(bs.Actor):

    def __init__(self, position=(0, 1, 0), radius=2.5, time=8000):
        bs.Actor.__init__(self)
        self.radius = radius
        self.position = position

        self.poisonMaterial = bs.Material()
        self.poisonMaterial.addActions(
            conditions=(('theyHaveMaterial',
                         bs.getSharedObject('playerMaterial'))),
            actions=(('modifyPartCollision', 'collide', True),
                     ('modifyPartCollision', 'physical', False),
                     ('call', 'atConnect', self.touchedSpaz)))

        self.node = bs.newNode('region', attrs={
            'position': (self.position[0],
                         self.position[1],
                         self.position[2]),
            'scale': (0.1, 0.1, 0.1),
            'type': 'sphere',
            'materials': [self.poisonMaterial]})

        self.visualRadius = bs.newNode('shield', attrs={
            'position': self.position,
            'color': (0.3, 1.2, 0.3),
            'radius': 0.1})

        scale = {
            0: (0, 0, 0),
            500: (self.radius, self.radius, self.radius)
        }

        bs.animate(self.visualRadius, 'radius', {0: 0, 500: self.radius*2})
        bs.animateArray(self.node, 'scale', 3, scale, True)

        bs.gameTimer(7700, bs.WeakCall(self.anim))
        bs.gameTimer(time, self.node.delete)
        bs.gameTimer(time, self.visualRadius.delete)

    def anim(self):
        scale = {
            0: (self.radius, self.radius, self.radius),
            200: (0, 0, 0)
        }

        bs.animate(self.visualRadius, 'radius', {0: self.radius*2, 200: 0})
        bs.animateArray(self.node, 'scale', 3, scale)

    def touchedSpaz(self):
        node = bs.getCollisionInfo('opposingNode')
        node.handleMessage('knockout', 5000)

    def delete(self):
        self.node.delete()
        self.visualRadius.delete()


class Poison(bs.Actor):

    def __init__(self, position=(0, 1, 0), radius=2.2, owner=None):
        ######################################
        # Dont ask me, how in works!         #
        # I am too lazy to use a factory!(2) #
        ######################################
        bs.Actor.__init__(self)
        self.radius = radius
        self.position = position

        self.poisonMaterial = bs.Material()
        self.poisonMaterial.addActions(
            conditions=(('theyHaveMaterial',
                         bs.getSharedObject('playerMaterial'))),
            actions=(('modifyPartCollision', 'collide', True),
                     ('modifyPartCollision', 'physical', False),
                     ('call', 'atConnect', self.touchedSpaz)))

        self.node = bs.newNode('region', owner=owner, attrs={
            'position': (self.position[0], self.position[1], self.position[2]),
            'scale': (0.1, 0.1, 0.1),
            'type': 'sphere',
            'materials': [self.poisonMaterial]})

        self.visualRadius = bs.newNode('shield', attrs={
            'position': self.position,
            'color': (0.3, 0.3, 0),
            'radius': 0.1})

        radius = {0: 0, 200: self.radius*2, 400: 0}
        scale = {
            0: (0, 0, 0), 200: (self.radius, self.radius, self.radius),
            400: (0, 0, 0)
        }

        bs.animate(self.visualRadius, 'radius', radius)
        bs.animateArray(self.node, 'scale', 3, scale)

        bs.gameTimer(250, self.node.delete)
        bs.gameTimer(250, self.visualRadius.delete)
        bs.emitBGDynamics(
            position=self.position,
            count=100,
            emitType='tendrils',
            tendrilType='smoke')

    def touchedSpaz(self):
        node = bs.getCollisionInfo('opposingNode')
        node.getDelegate().curse()

    def delete(self):
        self.node.delete()
        self.visualRadius.delete()


class BlackHole(bs.Actor):

    def __init__(self, position=(0, 1, 0), autoExpand=True, scale=1,
                 doNotRandomize=False, infinity=False, owner=None):
        bs.Actor.__init__(self)
        self.shields = []
        if not doNotRandomize:
            self.position = (position[0] - 2 + random.random()*4,
                             position[1] + random.random()*2,
                             position[2] - 2 + random.random()*4)
        else:
            self.position = position

        self.scale = scale
        self.suckObjects = []
        self.owner = owner

        self.blackHoleMaterial = bs.Material()
        self.blackHoleMaterial.addActions(
            conditions=(('theyDontHaveMaterial',
                         bs.getSharedObject('objectMaterial')),
                        'and', ('theyHaveMaterial',
                                bs.getSharedObject('playerMaterial'))),
            actions=(('modifyPartCollision', 'collide', True),
                     ('modifyPartCollision', 'physical', False),
                     ('call', 'atConnect', self.touchedSpaz)))

        self.blackHoleMaterial.addActions(
            conditions=(('theyDontHaveMaterial',
                         bs.getSharedObject('playerMaterial')),
                        'and', ('theyHaveMaterial',
                                bs.getSharedObject('objectMaterial'))),
            actions=(('modifyPartCollision', 'collide', True),
                     ('modifyPartCollision', 'physical', False),
                     ('call', 'atConnect', self.touchedObj)))

        self.suckMaterial = bs.Material()
        self.suckMaterial.addActions(
            conditions=(('theyHaveMaterial',
                         bs.getSharedObject('objectMaterial'))),
            actions=(('modifyPartCollision', 'collide', True),
                     ('modifyPartCollision', 'physical', False),
                     ('call', 'atConnect', self.touchedObjSuck)))

        self.node = bs.newNode('region', attrs={
            'position': (self.position[0], self.position[1], self.position[2]),
            'scale': (scale, scale, scale),
            'type': 'sphere',
            'materials': [self.blackHoleMaterial]})

        self.suckRadius = bs.newNode('region', attrs={
            'position': (self.position[0], self.position[1], self.position[2]),
            'scale': (scale, scale, scale),
            'type': 'sphere',
            'materials': [self.suckMaterial]})

        def dist():
            bs.emitBGDynamics(
                position=self.position,
                emitType='distortion',
                spread=6,
                count=100)

            if self.node.exists():
                bs.gameTimer(1000, dist)

        dist()
        if not infinity:
            self._dieTimer = bs.Timer(25000, bs.WeakCall(self.explode))

        scale1 = {
            0: (0, 0, 0),
            300: (self.scale, self.scale, self.scale)
        }

        scale2 = {
            0: (0, 0, 0),
            300: (self.scale*8, self.scale*8, self.scale*8)
        }

        bs.animateArray(self.node, 'scale', 3, scale1, True)
        bs.animateArray(self.suckRadius, 'scale', 3, scale2, True)

        for i in range(20):
            self.shields.append(
                bs.newNode('shield', attrs={
                    'color': (random.random(),
                              random.random(),
                              random.random()),
                    'radius': self.scale*2,
                    'position': self.position}))

        def sound():
            bs.playSound(bs.getSound('blackHole'))

        sound()
        if infinity:
            self.sound2 = bs.Timer(25000, bs.Call(sound), repeat=infinity)

    def addMass(self):
        self.scale += 0.15
        self.node.scale = (self.scale, self.scale, self.scale)
        for i in range(2):
            self.shields.append(
                bs.newNode('shield', attrs={
                    'color': (random.random(),
                              random.random(),
                              random.random()),
                    'radius': self.scale+0.15,
                    'position': self.position}))

    def explode(self):
        bs.emitBGDynamics(
            position=self.position,
            count=500,
            scale=1,
            spread=1.5,
            chunkType='spark')

        for i in self.shields:
            bs.animate(i, 'radius',
                       {0: 0, 200: i.radius*5})

        bs.Blast(
            position=self.position,
            blastRadius=10).autoRetain()

        for i in self.shields:
            i.delete()

        self.node.delete()
        self.suckRadius.delete()
        self.node.handleMessage(bs.DieMessage())
        self.suckRadius.handleMessage(bs.DieMessage())

    def touchedSpaz(self):
        node = bs.getCollisionInfo('opposingNode')
        bs.Blast(
            position=node.position,
            blastType='turret').autoRetain()

        if node.exists():
            if self.owner.exists():
                node.handleMessage(
                    bs.HitMessage(
                        magnitude=1000.0,
                        sourcePlayer=self.owner.getDelegate().getPlayer()))

                try:
                    node.handleMessage(bs.DieMessage())
                except:
                    pass

                bs.shakeCamera(2)
            else:
                node.handleMessage(bs.DieMessage())

        self.addMass()

    def touchedObj(self):
        node = bs.getCollisionInfo('opposingNode')
        bs.Blast(
            position=node.position,
            blastType='turret').autoRetain()

        if node.exists():
            node.handleMessage(bs.DieMessage())

    def touchedObjSuck(self):
        node = bs.getCollisionInfo('opposingNode')
        if node.getNodeType() in ['prop', 'bomb']:
            self.suckObjects.append(node)

        for i in self.suckObjects:
            if i.exists():
                if i.sticky:
                    i.sticky = False
                    i.extraAcceleration = (0, 10, 0)
                else:
                    i.extraAcceleration = (
                        (self.position[0] - i.position[0])*8,
                        (self.position[1] - i.position[1])*25,
                        (self.position[2] - i.position[2])*8)

    def handleMessage(self, m):
        if isinstance(m, bs.DieMessage):
            if self.node.exists():
                self.node.delete()

            if self.suckRadius.exists():
                self.suckRadius.delete()

            self._updTimer = None
            self._suckTimer = None
            self.sound2 = None
            self.suckObjects = []

        elif isinstance(m, bs.OutOfBoundsMessage):
            self.node.handleMessage(bs.DieMessage())

        elif isinstance(m, BlackHoleMessage):
            node = bs.getCollisionInfo('opposingNode')
            bs.Blast(
                position=self.position,
                blastType='turret').autoRetain()

            if not node.invincible:
                node.shattered = 2


class Lego(bs.Actor):

    def __init__(self, position=(0, 1, 0), num=int(random.random()*3),
                 colorNum=int(random.random()*3), velocity=(0, 0, 0)):
        factory = self.getFactory()
        bs.Actor.__init__(self)

        if num == 1:
            model = bs.getModel('lego1')
        elif num == 2:
            model = bs.getModel('lego2')
        else:
            model = bs.getModel('lego3')

        if colorNum == 1:
            colorTexture = bs.getTexture('yellow')
        elif colorNum == 2:
            colorTexture = bs.getTexture('blue')
        else:
            colorTexture = bs.getTexture('red')

        self.node = bs.newNode('prop', delegate=self, attrs={
            'position': position,
            'model': model,
            'lightModel': model,
            'body': 'landMine',
            'velocity': velocity,
            'modelScale': 0.8,
            'bodyScale': 0.8,
            'shadowSize': 0.5,
            'colorTexture': colorTexture,
            'reflection': 'powerup',
            'reflectionScale': [1.0],
            'materials': (factory.legoMaterial,
                          bs.getSharedObject('footingMaterial'),
                          bs.getSharedObject('objectMaterial'))})

    @classmethod
    def getFactory(cls):
        activity = bs.getActivity()
        try:
            return activity._sharedPortalFactory
        except Exception:
            f = activity._sharedPortalFactory = PortalFactory()
            return f

    def handleMessage(self, m):
        if isinstance(m, bs.DieMessage):
            if self.node.exists():
                self.node.delete()

        elif isinstance(m, bs.OutOfBoundsMessage):
            self.node.handleMessage(bs.DieMessage())

        elif isinstance(m, bs.PickedUpMessage):
            self.node.sticky = False

        elif isinstance(m, bs.DroppedMessage):
            self.node.sticky = False

        elif isinstance(m, LegoConnect):
            self.node.sticky = True

        elif isinstance(m, LegoMessage):
            self.node.sticky = False
            node = bs.getCollisionInfo('opposingNode')
            node.handleMessage(
                'impulse', node.position[0], node.position[1],
                node.position[2], node.velocity[0], 3, node.velocity[2],
                45, 45, 0, 0, node.velocity[0], 3, node.velocity[2])

        elif isinstance(m, bs.HitMessage):
            m.srcNode.handleMessage(
                'impulse', m.pos[0], m.pos[1], m.pos[2],
                m.velocity[0], m.velocity[1], m.velocity[2],
                m.magnitude, m.velocityMagnitude, m.radius,
                0, m.velocity[0], m.velocity[1], m.velocity[2])


class cCube(bs.Actor):

    def __init__(self, position=(0, 1, 0), velocity=(0, 0, 0),
                 companion=False):
        bs.Actor.__init__(self)
        self.companion = companion
        self.light = None
        self.uptimer = None
        self.pickuped = None
        self.regenTimer = None
        self.checkerTimer = None

        factory = self.getFactory()

        self.cubeMaterial = bs.Material()
        self.cubeMaterial.addActions(
            conditions=(('theyHaveMaterial',
                         bs.getSharedObject('dirtMaterial'))),
            actions=(('call', 'atConnect', self.shitHitsTheCube)))

        if companion:
            self.node = bs.newNode('prop', delegate=self, attrs={
                'position': position,
                'velocity': velocity,
                'model': factory.companionCubeModel,
                'lightModel': factory.companionCubeModel,
                'body': 'crate',
                'shadowSize': 0.5,
                'colorTexture': factory.companionCubeTex,
                'reflection': 'soft',
                'reflectionScale': [0.3],
                'materials': (bs.getSharedObject('objectMaterial'),
                              bs.getSharedObject('footingMaterial'),
                              self.cubeMaterial)})
        else:
            self.node = bs.newNode('prop', delegate=self, attrs={
                'position': position,
                'velocity': velocity,
                'model': factory.companionCubeModel,
                'lightModel': factory.companionCubeModel,
                'body': 'crate',
                'shadowSize': 0.5,
                'colorTexture': factory.weightCubeTex,
                'reflection': 'soft',
                'reflectionScale': [0.3],
                'materials': (bs.getSharedObject('objectMaterial'),
                              bs.getSharedObject('footingMaterial'),
                              self.cubeMaterial)})

        def textSender():
            if self.node.exists():
                if self.companion and self.pickuped \
                        and bsInternal._getForegroundHostSession().narkomode:
                    bsUtils.PopupText(
                        random.choice([
                            'I love you',
                            'Hi',
                            'How are you?',
                            'I am alive',
                            'Now you can hear me',
                            'Dont forget me',
                            'BombDash forever',
                            'Nama come back',
                            'Do you know Chell?',
                            'GLaDOS kill my brothers',
                            'PLEASE DONT FIRE ME',
                            'Eric bring back the light',
                            'The cake is a lie',
                            'If life gives you lemons\ndont make the lemonade',
                            '09 Tartaros',
                            'Prometheus']),
                        color=(1, 0.1, 1),
                        scale=0.8,
                        position=self.node.position).autoRetain()

        bs.gameTimer(2000+random.randint(0, 3000), textSender, repeat=True)

    @classmethod
    def getFactory(cls):
        activity = bs.getActivity()
        try:
            return activity._sharedPortalFactory
        except Exception:
            f = activity._sharedPortalFactory = PortalFactory()
            return f

    def shitHitsTheCube(self):
        node = bs.getCollisionInfo('opposingNode')
        bs.emitBGDynamics(
            position=node.position,
            count=30,
            scale=1.3,
            spread=0.1,
            chunkType='sweat')

        node.handleMessage(bs.DieMessage())

    def handleMessage(self, m):
        if isinstance(m, bs.DieMessage):
            if self.node.exists():
                self.node.delete()

        elif isinstance(m, bs.OutOfBoundsMessage):
            if self.node.exists():
                self.node.delete()

        elif isinstance(m, bs.PickedUpMessage):
            self.pickuped = True
            self.node.extraAcceleration = (0, 25, 0)

            def up():
                self.node.extraAcceleration = (0, 40, 0)

            self.uptimer = bs.Timer(330, up)

            def checker():
                if self.node.exists() and \
                        (m is None or not m.node.exists()
                         or m.node.holdNode != self.node):
                    self.node.extraAcceleration = (0, 0, 0)
                    self.pickuped = False
                    self.checkerTimer = None

            self.checkerTimer = bs.gameTimer(100, checker, repeat=True)
            self.spazNode = m.node
            delegate = m.node.getDelegate()

            self.light = bs.newNode('light', attrs={
                'position': self.node.position,
                'color': (0, 1, 0),
                'volumeIntensityScale': 1.0,
                'intensity': 0.1,
                'radius': 0.6})

            m.node.connectAttr('position', self.light, 'position')

            def regen():
                if m is not None and m.node.exists() \
                        and m.node.getDelegate().hitPoints \
                        < m.node.getDelegate().hitPointsMax \
                        and self.pickuped:
                    delegate.hitPoints += 1
                    delegate._lastHitTime = None
                    delegate._numTimesHit = 0
                    m.node.hurt -= 0.001
                    bs.emitBGDynamics(
                        position=m.node.position,
                        velocity=(0, 3, 0),
                        count=int(3.0+random.random()*5),
                        scale=1.5,
                        spread=0.3,
                        chunkType='sweat')
                else:
                    if self.light is not None and self.light.exists():
                        self.light.delete()
                        self.regenTimer = None

            self.regenTimer = bs.Timer(10, regen, repeat=True)

        elif isinstance(m, bs.DroppedMessage):
            self.pickuped = False
            self.uptimer = None
            self.spazNode = None
            self.regenTimer = None
            self.checkerTimer = None
            self.node.extraAcceleration = (0, 0, 0)
            if self.light is not None and self.light.exists():
                self.light.delete()

        elif isinstance(m, bs.HitMessage):
            self.node.handleMessage(
                'impulse', m.pos[0], m.pos[1], m.pos[2],
                m.velocity[0], m.velocity[1], m.velocity[2],
                m.magnitude, m.velocityMagnitude, m.radius,
                0, m.velocity[0], m.velocity[1], m.velocity[2])


class Clay(bs.Actor):

    def __init__(self, position=(0, 1, 0), velocity=(0, 0, 0),
                 bomb=False, banana=False, owner=None):
        bs.Actor.__init__(self)
        self.bomb = bomb
        self.owner = owner
        self.banana = banana

        self.dirtDieMaterial = bs.Material()
        self.dirtDieMaterial.addActions(
            conditions=(('weAreOlderThan', 2000)),
            actions=(('message', 'ourNode', 'atConnect', bs.DieMessage())))

        self.dirtDieMaterial.addActions(
            conditions=(('theyHaveMaterial',
                         bs.getSharedObject('playerMaterial')),
                        'and', ('weAreYoungerThan', 2000)),
            actions=(('message', 'ourNode', 'atConnect', dirtBombMessage())))

        self.dirtDieMaterial.addActions(
            conditions=(('theyHaveMaterial',
                         bs.getSharedObject('footingMaterial')),
                        'and', ('weAreYoungerThan', 2000)),
            actions=(('message', 'ourNode', 'atConnect', bs.DieMessage())))

        if not banana:
            self.node = bs.newNode('prop', delegate=self, attrs={
                'position': position,
                'velocity': velocity,
                'model': bs.getModel('box'),
                'body': 'sphere',
                'bodyScale': 0.3,
                'modelScale': 0.15,
                'sticky': False,
                'colorTexture': bs.getTexture('dirt'),
                'materials': (bs.getSharedObject('objectMaterial'),
                              bs.getSharedObject('dirtMaterial'))})
        else:
            self.node = bs.newNode('prop', delegate=self, attrs={
                'position': position,
                'velocity': velocity,
                'model': bs.getModel('slice'),
                'body': 'sphere',
                'bodyScale': 0.3,
                'modelScale': 0.4,
                'sticky': False,
                'colorTexture': bs.getTexture('yellow'),
                'materials': (bs.getSharedObject('objectMaterial'),
                              bs.getSharedObject('dirtMaterial'))})

        if bomb and not banana:
            self.node.materials = self.node.materials + (self.dirtDieMaterial,)

        if banana:
            bs.gameTimer(1000+random.randint(0, 500), bs.Call(self.explode))

        def stick():
            if self.node.exists():
                self.node.sticky = True

        bs.gameTimer(100, bs.Call(stick))

    def explode(self):
        if self.node.exists():
            bs.Blast(
                position=self.node.position,
                sourcePlayer=self.owner,
                notShake=True,
                blastRadius=0.8,
                notScorch=True).autoRetain()

            self.node.handleMessage(bs.DieMessage())

    def handleMessage(self, m):
        if isinstance(m, bs.DieMessage):
            if self.node.exists():
                self.node.delete()

        elif isinstance(m, bs.OutOfBoundsMessage):
            if self.node.exists():
                self.node.delete()

        elif isinstance(m, dirtBombMessage):
            if not self.banana:
                bs.Blast(
                    position=self.node.position,
                    hitType='punch',
                    sourcePlayer=self.owner,
                    notShake=True,
                    blastRadius=0.5).autoRetain()

                self.node.handleMessage(bs.DieMessage())

        elif isinstance(m, bs.HitMessage):
            self.node.handleMessage(
                'impulse', m.pos[0], m.pos[1], m.pos[2],
                m.velocity[0], m.velocity[1], m.velocity[2],
                m.magnitude, m.velocityMagnitude, m.radius, 0,
                m.velocity[0], m.velocity[1], m.velocity[2])


class BadRock(bs.Actor):

    def __init__(self, position=(0, 1, 0), velocity=(0, 0, 0), owner=None,
                 sourcePlayer=None, expire=True, hit=True):
        bs.Actor.__init__(self)
        factory = self.getFactory()
        self.hit = hit

        self.node = bs.newNode('prop', delegate=self, attrs={
            'position': position,
            'velocity': velocity,
            'model': factory.badrockModel,
            'lightModel': factory.badrockModel,
            'body': 'crate',
            'bodyScale': 1.09,
            'shadowSize': 0.5,
            'colorTexture': factory.minecraftTex,
            'reflection': 'soft',
            'reflectionScale': [0.23],
            'materials': (factory.impactBlastMaterial,
                          bs.getSharedObject('footingMaterial'),
                          bs.getSharedObject('objectMaterial'))})

        self.expire = expire

    @classmethod
    def getFactory(cls):
        """
        Returns a shared bs.FlagFactory object, creating it if necessary.
        """
        activity = bs.getActivity()
        try:
            return activity._sharedPortalFactory
        except Exception:
            f = activity._sharedPortalFactory = PortalFactory()
            return f

    def handleMessage(self, m):
        if isinstance(m, bs.DieMessage):
            if self.node.exists():
                self.node.delete()

        if isinstance(m, bs.OutOfBoundsMessage):
            if self.node.exists():
                self.node.delete()

        if isinstance(m, ImpactMessage):
            if self.hit:
                bs.Blast(
                    position=self.node.position,
                    hitType='punch',
                    blastRadius=1).autoRetain()

            if self.expire:
                if self.node.exists():
                    self._lifeTime = bs.Timer(5000, bs.WeakCall(self.animBR))
                    self._clrTime = bs.Timer(5310, bs.WeakCall(self.clrBR))

    def animBR(self):
        if self.node.exists():
            bs.animate(self.node, 'modelScale', {0: 1, 200: 0})

    def clrBR(self):
        if self.node.exists():
            self.node.delete()


class Turret(bs.Actor):

    def __init__(self, position=(0, 2, 0), velocity=(0, 0, 0),
                 different=False, hasLaser=True, mute=False):
        # hasLaser used in older versions
        bs.Actor.__init__(self)
        self.turretModel = bs.getModel('turret')
        self.turretClosedModel = bs.getModel('turret_closed')
        self.turretTex = bs.getTexture('turretTex')
        self.mute = mute
        self.closed = True
        self.activated = False
        self.phrase = 1
        self.different = different

        self.turretMaterial = bs.Material()
        self.turretMaterial.addActions(
            conditions=(('weAreOlderThan', 200),
                        'and', ('theyAreOlderThan', 200),
                        'and', ('evalColliding',),
                        'and', (('theyHaveMaterial',
                                 bs.getSharedObject('footingMaterial')),
                                'or', ('theyHaveMaterial',
                                       bs.getSharedObject('objectMaterial')))),
            actions=(('message', 'ourNode', 'atConnect',
                      TurretImpactMessage())))

        self.node = bs.newNode('prop', delegate=self, attrs={
            'position': position,
            'velocity': velocity,
            'model': self.turretClosedModel,
            'lightModel': self.turretClosedModel,
            'body': 'crate',
            'shadowSize': 0.5,
            'colorTexture': self.turretTex,
            'reflection': 'soft',
            'reflectionScale': [0.7],
            'materials': (bs.getSharedObject('footingMaterial'),
                          bs.getSharedObject('objectMaterial'))})

        if not mute and not self.different:  # for scene in main menu
            bs.playSound(
                bs.getSound(random.choice(['turret_activation',
                                           'turret_autosearch',
                                           'turret_hi',
                                           'turret_see_you'])),
                position=self.node.position)

    def shot(self):
        if self.node.exists():
            bs.Blast(
                position=(self.node.position[0]+random.uniform(-2, 2),
                          self.node.position[1]+random.uniform(-0.5, 0.5),
                          self.node.position[2]+random.uniform(-2, 2)),
                blastType='turret',
                hitType='punch').autoRetain()

    def activate(self):
        if not self.mute:
            if not self.different:
                self.openTurret()
                if not self.activated:
                    self.activated = True
                    bs.playSound(
                        bs.getSound(random.choice([
                            'turret_die1',
                            'turret_die2',
                            'turret_die3'])),
                        position=self.node.position)

                    self._shotTimer = bs.Timer(50, bs.Call(self.shot),
                                               repeat=True)

                    def brokeTimer():
                        self._shotTimer = None
                        self.broke()

                    bs.gameTimer(2000, bs.Call(brokeTimer))

    def broke(self):
        def effect():
            if self.node.exists():
                bs.emitBGDynamics(
                    position=self.node.position,
                    count=int(2.0+random.random()*40),
                    scale=0.5,
                    spread=0.1,
                    chunkType='spark')

        self._brokeTimer = bs.Timer(200, bs.Call(effect), repeat=True)
        self._explodeTimer = bs.Timer(8000, bs.WeakCall(self.explode))

    def openTurret(self):
        if self.node.exists():
            if not self.mute:
                if self.closed:
                    self.node.model = self.turretModel
                    bs.playSound(
                        bs.getSound('servomotor'),
                        position=self.node.position)

                    self.closed = False

    def explode(self):
        if self.node.exists():
            bs.Blast(
                position=self.node.position).autoRetain()

            self._brokeTimer = None
            self.node.handleMessage(bs.DieMessage())

    def handleMessage(self, m):
        if isinstance(m, bs.DieMessage):
            if self.node.exists():
                self.node.delete()

        elif isinstance(m, bs.OutOfBoundsMessage):
            self.node.handleMessage(bs.DieMessage())

        elif isinstance(m, TurretImpactMessage):
            if not self.different:
                self.activate()

        elif isinstance(m, bs.PickedUpMessage):
            if not self.different and not self.mute:
                if not self.activated and not self.mute:
                    bs.playSound(
                        bs.getSound(random.choice(['turret_pickup1',
                                                   'turret_pickup2',
                                                   'turret_pickup3'])),
                        position=self.node.position)

                self.openTurret()
            else:
                if self.phrase < 12:
                    bs.playSound(bs.getSound(
                        'turret_different_'+str(self.phrase)),
                        position=self.node.position)

                    self.phrase += 1

        elif isinstance(m, bs.DroppedMessage):
            def addMaterial():
                self.node.materials = self.node.materials \
                    + (self.turretMaterial)

            bs.gameTimer(50, bs.Call(addMaterial))

        elif isinstance(m, bs.HitMessage):
            if not self.different:
                self.activate()


class AutoAim(object):

    def __init__(self, whoControl, owner):
        self.whoControl = whoControl
        self.owner = owner
        self.target = None
        self.node = None
        self.aimZoneSpaz = bs.Material()
        self.aimZoneSpaz.addActions(
            conditions=(('theyHaveMaterial',
                         bs.getSharedObject('playerMaterial'))),
            actions=(('modifyPartCollision', 'collide', True),
                     ('modifyPartCollision', 'physical', False),
                     ('call', 'atConnect', self.touchedSpaz)))

        self.whoControl.extraAcceleration = (0, 20, 0)

        if self.whoControl.exists():
            self.node = bs.newNode('region', attrs={
                'position': (self.whoControl.position[0],
                             self.whoControl.position[1],
                             self.whoControl.position[2]),
                'scale': (0.1, 0.1, 0.1),
                'type': 'sphere',
                'materials': [self.aimZoneSpaz]})
        else:
            self.node = bs.newNode('region', attrs={
                'position': (0, 0, 0),
                'scale': (0.1, 0.1, 0.1),
                'type': 'sphere',
                'materials': [self.aimZoneSpaz]})

        bs.animateArray(self.node, 'scale', 3,
                        {0: (0.1, 0.1, 0.1), 1200: (60, 60, 60)})

    def go(self):
        if self.target is not None \
                and self.whoControl is not None \
                and self.whoControl.exists():
            self.whoControl.velocity = \
                (self.whoControl.velocity[0]+(
                    self.target.position[0]-self.whoControl.position[0]),
                 self.whoControl.velocity[1]+(
                    self.target.position[1]-self.whoControl.position[1]),
                 self.whoControl.velocity[2]+(
                    self.target.position[2]-self.whoControl.position[2]))

            bs.gameTimer(1, self.go)

    def touchedSpaz(self):
        node = bs.getCollisionInfo('opposingNode')
        try:
            if node is not None \
                    and node.exists() \
                    and node != self.owner \
                    and node.getDelegate().isAlive() \
                    and node.getDelegate().getPlayer().getTeam() \
                    != self.owner.getDelegate().getPlayer().getTeam():
                self.target = node
                self.node.delete()
                self.whoControl.extraAcceleration = (0, 20, 0)
                self.go()
        except:
            if node is not None \
                    and node.exists() \
                    and node != self.owner \
                    and node.getDelegate().isAlive():
                self.target = node
                self.node.delete()
                self.whoControl.extraAcceleration = (0, 20, 0)
                self.go()

    def off(self):
        def sa():
            self.target = None

        bs.gameTimer(100, sa)


class Airstrike(bs.Actor):

    def __init__(self, position=(0, 1, 0)):
        self.position = position
        bs.Actor.__init__(self)

        self.target = bs.newNode('light', attrs={
            'position': (self.position[0],
                         self.position[1],
                         self.position[2]),
            'color': (1, 0, 0),
            'volumeIntensityScale': 1.0})

        bs.animate(self.target, 'intensity', {
            0: 0, 500: 0.5, 1000: 1.0, 1500: 0.5, 2000: 0},
            loop=True)

        bs.gameTimer(5000, self.target.delete)

        self._rain = bs.gameTimer(300, bs.Call(self.dropBombs), repeat=True)
        self._stopper = True
        self._endRain = bs.gameTimer(5000, bs.Call(self.endRain))

    def dropBombs(self):
        if self._stopper is not None:
            pos = (self.position[0]+random.uniform(1.5, -1.5),
                   self.position[1]+3,
                   self.position[2]+random.uniform(1.5, -1.5))

            babyNuke(position=pos, velocity=(1, 1, 0)).autoRetain()
        else:
            self._stopper = None

    def endRain(self):
        self._stopper = None


class HealBomb(bs.Actor):

    def __init__(self, position=(0, 1, 0), radius=2, time=100):
        bs.Actor.__init__(self)
        self.position = position
        self.radius = radius

        self.poisonMaterial = bs.Material()
        self.poisonMaterial.addActions(
            conditions=(('theyHaveMaterial',
                         bs.getSharedObject('playerMaterial'))),
            actions=(('modifyPartCollision', 'collide', True),
                     ('modifyPartCollision', 'physical', False),
                     ('call', 'atConnect', self.touchedSpaz)))

        self.node = bs.newNode('region', attrs={
            'position': (self.position[0], self.position[1], self.position[2]),
            'scale': (radius, radius, radius),
            'type': 'sphere',
            'materials': [self.poisonMaterial]})

        bs.gameTimer(time, self.node.delete)

        self.light = bs.newNode('light', attrs={
            'position': (self.position[0], self.position[1], self.position[2]),
            'volumeIntensityScale': 10.0,
            'radius': 0.25,
            'intensity': 0,
            'color': (1, 1, 1)})

        bs.animate(self.light, 'intensity', {0: 0, 100: 1.0, 500: 0})

    def touchedSpaz(self):
        node = bs.getCollisionInfo('opposingNode')
        node.handleMessage(bs.PowerupMessage(powerupType='health'))

    def delete(self):
        self.node.delete()


class SimpleBox(bs.Actor):

    def __init__(self, position=(0, 1, 0), velocity=(0, 0, 0)):
        bs.Actor.__init__(self)

        self.bombMaterial = bs.Material()
        self.bombMaterial.addActions(
            conditions=((('weAreYoungerThan', 100),
                         'or', ('theyAreYoungerThan', 100)),
                        'and', ('theyHaveMaterial',
                                bs.getSharedObject('objectMaterial'))),
            actions=(('modifyNodeCollision', 'collide', False)))

        # we want pickup materials to always hit us even if we're currently not
        # colliding with their node (generally due to the above rule)
        self.bombMaterial.addActions(
            conditions=('theyHaveMaterial',
                        bs.getSharedObject('pickupMaterial')),
            actions=(('modifyPartCollision', 'useNodeCollide', False)))

        self.bombMaterial.addActions(actions=('modifyPartCollision',
                                              'friction', 0.3))

        self.node = bs.newNode('prop', delegate=self, attrs={
            'position': position,
            'velocity': velocity,
            'model': bs.getModel('tnt'),
            'lightModel': bs.getModel('tnt'),
            'body': 'crate',
            'shadowSize': 0.5,
            'colorTexture': bs.getTexture('tnt'),
            'reflection': 'soft',
            'reflectionScale': [0.23],
            'materials': [self.bombMaterial,
                          bs.getSharedObject('objectMaterial'),
                          bs.getSharedObject('footingMaterial')]})

        bsUtils.animate(self.node, 'modelScale', {0: 0, 200: 1.3, 260: 1})

    def handleMessage(self, m):
        if isinstance(m, bs.DieMessage):
            if self.node.exists():
                self.node.delete()

        elif isinstance(m, bs.OutOfBoundsMessage):
            if self.node.exists():
                self.node.delete()


class ColorBomb(bs.Actor):

    def __init__(self, position=(0, 1, 0), radius=2, time=1000,
                 color=(random.uniform(0.1, 2.5),
                        random.uniform(0.1, 2.5),
                        random.uniform(0.1, 2.5))):
        bs.Actor.__init__(self)
        self.position = position
        self.radius = radius
        self.color = color

        self.poisonMaterial = bs.Material()
        self.poisonMaterial.addActions(
            conditions=(('theyHaveMaterial',
                         bs.getSharedObject('playerMaterial'))),
            actions=(('modifyPartCollision', 'collide', True),
                     ('modifyPartCollision', 'physical', False),
                     ('call', 'atConnect', self.touchedSpaz)))

        self.node = bs.newNode('region', attrs={
            'position': (self.position[0], self.position[1], self.position[2]),
            'scale': (radius, radius, radius),
            'type': 'sphere',
            'materials': [self.poisonMaterial]})

        bs.gameTimer(time, self.node.delete)

        self.light = bs.newNode('light', attrs={
            'position': (self.position[0], self.position[1], self.position[2]),
            'volumeIntensityScale': 10.0,
            'radius': 0.25,
            'intensity': 0,
            'color': self.color})

        bs.animate(self.light, 'intensity', {0: 0, 100: 5.0, 1500: 0})

    def touchedSpaz(self):
        node = bs.getCollisionInfo('opposingNode')
        bs.animateArray(node, 'color', 3, {0: node.color, 1000: self.color})
        bs.animateArray(node, 'highlight', 3,
                        {0: node.color, 1000: self.color})

        bs.animateArray(node, 'nameColor', 3,
                        {0: node.color, 1000: self.color})

    def delete(self):
        self.node.delete()
