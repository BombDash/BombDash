import math
import random
import weakref
from math import cos
import bs
import bsVector
import bsBomb
import bsUtils

class QuakeBallFactory(object):

    def __init__(self):
        self.ballMaterial = bs.Material()

        self.ballMaterial.addActions(
            conditions=((('weAreYoungerThan', 5), 'or', ('theyAreYoungerThan', 50)),
                          'and', ('theyHaveMaterial', bs.getSharedObject('objectMaterial'))),
            actions=(('modifyNodeCollision', 'collide', False)))

        self.ballMaterial.addActions(
            conditions=('theyHaveMaterial', bs.getSharedObject('pickupMaterial')),
            actions=(('modifyPartCollision', 'useNodeCollide', False)))

        self.ballMaterial.addActions(
            actions=('modifyPartCollision', 'friction', 0))

        self.ballMaterial.addActions(
            conditions=('theyHaveMaterial', bs.getSharedObject('playerMaterial')),
            actions=(('modifyPartCollision', 'physical', False),
                     ('message', 'ourNode', 'atConnect', TouchedToSpaz())))

        self.ballMaterial.addActions(
            conditions=(('theyDontHaveMaterial', bs.getSharedObject('playerMaterial')), 'and',
                        ('theyHaveMaterial', bs.getSharedObject('objectMaterial'))),
            actions=('message', 'ourNode', 'atConnect', TouchedToAnything()))

        self.ballMaterial.addActions(
            conditions=(('theyDontHaveMaterial', bs.getSharedObject('playerMaterial')), 'and',
                        ('theyHaveMaterial', bs.getSharedObject('footingMaterial'))),
            actions=('message', 'ourNode', 'atConnect', TouchedToFootingMaterial())) 

    def give(self, spaz):
        spaz.punchCallback = self.shot
        self.lastShot = bs.getGameTime()

    def shot(self, spaz):
        time = bs.getGameTime()
        if time - self.lastShot > 600:
            self.lastShot = time
            p1 = spaz.node.positionCenter
            p2 = spaz.node.positionForward
            direction = [p1[0]-p2[0], p2[1]-p1[1], p1[2]-p2[2]]
            direction[1] = 0.0

            mag = 10.0/bsVector.Vector(*direction).length()
            vel = [v * mag for v in direction]
            QuakeBall(
                position=spaz.node.position,
                velocity=(vel[0]*2, vel[1]*2, vel[2]*2),
                owner=spaz.getPlayer(),
                sourcePlayer=spaz.getPlayer(),
                color=spaz.node.color).autoRetain()

class TouchedToSpaz(object):
    #ball touched the spaz.
    pass

class TouchedToAnything(object):
    #ball touched not the spaz.
    pass

class TouchedToFootingMaterial(object):
    #read name.
    pass

class QuakeBall(bs.Actor):

    def __init__(self, position=(0, 5, 0), velocity=(0, 2, 0), sourcePlayer=None,
                 owner=None, color=(random.random(), random.random(), random.random()),
                 lightRadius=0):
        bs.Actor.__init__(self)
        factory = self.getFactory()

        self.node = bs.newNode('prop', delegate=self, attrs={
            'position': position,
            'velocity': velocity,
            'model': bs.getModel('impactBomb'),
            'body': 'sphere',
            'colorTexture': bs.getTexture('bunnyColor'),
            'modelScale': 0.2,
            'isAreaOfInterest': True,
            'bodyScale': 0.8,
            'materials': [bs.getSharedObject('objectMaterial'),
                          factory.ballMaterial]})

        self.sourcePlayer = sourcePlayer
        self.owner = owner
        self._lifeTimer = bs.Timer(5000, bs.WeakCall(self.die))

        self.lightNode = bs.newNode('light', attrs={
            'position':position,
            'color': color,
            'radius': 0.1+lightRadius,
            'volumeIntensityScale': 15.0})

        self.node.connectAttr('position', self.lightNode, 'position')
        self._emit = bs.Timer(15, bs.WeakCall(self.emit), repeat=True)

    def emit(self):
        bs.emitBGDynamics(
            position=self.node.position,
            velocity=self.node.velocity,
            count=10,
            scale=0.4,
            spread=0.01,
            chunkType='spark');

    def die(self):
        self.node.handleMessage(bs.DieMessage())

    @classmethod
    def getFactory(cls):
        activity = bs.getActivity()
        if activity is None: raise Exception('no current activity')
        try: return activity._quakeBallFactory
        except Exception:
            f = activity._quakeBallFactory = QuakeBallFactory()
            return f

    def handleMessage(self, m):
        super(self.__class__, self).handleMessage(m)
        if isinstance(m, TouchedToAnything):
            node = bs.getCollisionInfo('opposingNode')
            if node is not None and node.exists():
                v = self.node.velocity
                t = self.node.position
                hitDir = self.node.velocity
                m = self.node
                node.handleMessage(
                    bs.HitMessage(
                        pos=t,
                        velocity=v,
                        magnitude=bsVector.Vector(*v).length()*40,
                        velocityMagnitude=bsVector.Vector(*v).length()*40,
                        radius=0,
                        srcNode=self.node,
                        sourcePlayer=self.sourcePlayer,
                        forceDirection=hitDir))

            self.node.handleMessage(bs.DieMessage())

        elif isinstance(m, bs.DieMessage):
            if self.node.exists():
                velocity = self.node.velocity
                explosion = bs.newNode('explosion', attrs={
                    'position': self.node.position,
                    'velocity': (velocity[0], max(-1.0,velocity[1]), velocity[2]),
                    'radius': 1,
                    'big': False})

                bs.playSound(
                    sound=bs.getSound(random.choice(['impactHard', 'impactHard2', 'impactHard3'])),
                    position=self.node.position)

                self.node.delete()
                self.lightNode.delete()
                self._emit = None

        elif isinstance(m, bs.OutOfBoundsMessage):
            self.handleMessage(bs.DieMessage())

        elif isinstance(m, bs.HitMessage):
            self.node.handleMessage('impulse', m.pos[0], m.pos[1], m.pos[2],
                                    m.velocity[0], m.velocity[1], m.velocity[2],
                                    1.0*m.magnitude, 1.0*m.velocityMagnitude, m.radius,0,
                                    m.forceDirection[0], m.forceDirection[1], m.forceDirection[2])

        elif isinstance(m, TouchedToSpaz):
            node = bs.getCollisionInfo('opposingNode')
            try:
                if node is not None and node.exists() and node != self.owner \
                        and node.getDelegate().getPlayer().getTeam() != self.owner.getTeam():
                    node.handleMessage(bs.FreezeMessage())
                    v = self.node.velocity
                    t = self.node.position
                    hitDir = self.node.velocity

                    node.handleMessage(
                        bs.HitMessage(
                            pos=t,
                            velocity=(10, 10, 10),
                            magnitude=50,
                            velocityMagnitude=50,
                            radius=0,
                            srcNode=self.node,
                            sourcePlayer=self.sourcePlayer,
                            forceDirection=hitDir))

                self.node.handleMessage(bs.DieMessage())
            except:
                pass

        elif isinstance(m, TouchedToFootingMaterial):
            bs.playSound(
                sound=bs.getSound('blip'),
                position=self.node.position)