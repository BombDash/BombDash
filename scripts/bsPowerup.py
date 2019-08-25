# -*- coding: utf-8 -*-
import sys
import random
import weakref
import bs
import bsUI
import bsUtils
import BuddyBunny
import settings


defaultPowerupInterval = 8000


class PowerupMessage(object):
    """
    category: Message Classes

    Tell something to get a powerup.
    This message is normally recieved by touching
    a bs.Powerup box.

    Attributes:

       powerupType
          The type of powerup to be granted (a string).
          See bs.Powerup.powerupType for available type values.

       sourceNode
          The node the powerup game from, or an empty bs.Node ref otherwise.
          If a powerup is accepted, a bs.PowerupAcceptMessage should be sent
          back to the sourceNode to inform it of the fact. This will generally
          cause the powerup box to make a sound and disappear or whatnot.
    """
    def __init__(self, powerupType, sourceNode=bs.Node(None)):
        """
        Instantiate with given values.
        See bs.Powerup.powerupType for available type values.
        """
        self.powerupType = powerupType
        self.sourceNode = sourceNode


class PowerupAcceptMessage(object):
    """
    category: Message Classes

    Inform a bs.Powerup that it was accepted.
    This is generally sent in response to a bs.PowerupMessage
    to inform the box (or whoever granted it) that it can go away.
    """
    pass


class _TouchedMessage(object):
    pass


class PowerupFactory(object):
    """
    category: Game Flow Classes

    Wraps up media and other resources used by bs.Powerups.
    A single instance of this is shared between all powerups
    and can be retrieved via bs.Powerup.getFactory().

    Attributes:

       model
          The bs.Model of the powerup box.

       modelSimple
          A simpler bs.Model of the powerup box, for use in shadows, etc.

       texBox
          Triple-bomb powerup bs.Texture.

       texPunch
          Punch powerup bs.Texture.

       texIceBombs
          Ice bomb powerup bs.Texture.

       texStickyBombs
          Sticky bomb powerup bs.Texture.

       texShield
          Shield powerup bs.Texture.

       texImpactBombs
          Impact-bomb powerup bs.Texture.

       texHealth
          Health powerup bs.Texture.

       texLandMines
          Land-mine powerup bs.Texture.

       texCurse
          Curse powerup bs.Texture.

       healthPowerupSound
          bs.Sound played when a health powerup is accepted.

       powerupSound
          bs.Sound played when a powerup is accepted.

       powerdownSound
          bs.Sound that can be used when powerups wear off.

       powerupMaterial
          bs.Material applied to powerup boxes.

       powerupAcceptMaterial
          Powerups will send a bs.PowerupMessage to anything they touch
          that has this bs.Material applied.
    """

    def __init__(self):
        """
        Instantiate a PowerupFactory.
        You shouldn't need to do this; call bs.Powerup.getFactory()
        to get a shared instance.
        """
        self._lastPowerupType = None

        self.model = bs.getModel('powerup')
        self.modelSimple = bs.getModel('powerupSimple')
        self.snoModel = bs.getModel('frostyPelvis')

        self.texBomb = bs.getTexture('powerupBomb')
        self.texPunch = bs.getTexture('powerupPunch')
        self.texIceBombs = bs.getTexture('powerupIceBombs')
        self.texStickyBombs = bs.getTexture('powerupStickyBombs')
        self.texShield = bs.getTexture('powerupShield')
        self.texImpactBombs = bs.getTexture('powerupImpactBombs')
        self.texHealth = bs.getTexture('powerupHealth')
        self.texLandMines = bs.getTexture('powerupLandMines')
        self.texCurse = bs.getTexture('powerupCurse')
        self.texLuckyBlock = bs.getTexture('powerupLuckyBlock')
        self.texExtraAccelerator = bs.getTexture('powerupExtraAccelerator')
        self.texStickyForce = bs.getTexture('powerupStickyForce')
        self.texDirt = bs.getTexture('powerupDirt')
        self.texSpeed = bs.getTexture('powerupSpeed')
        self.texLego = bs.getTexture('powerupLego')
        self.texCannon = bs.getTexture('powerupCannon')
        self.textoxic = bs.getTexture('powerupToxic')
        self.texPoison = bs.getTexture('powerupPoison')
        self.texSlipper = bs.getTexture('powerupSlipper')
        self.texArtillery = bs.getTexture('powerupArtillery')
        self.texHealthBomb = bs.getTexture('powerupHealthBomb')
        self.texBanana = bs.getTexture('powerupBanana')
        self.shockWaveTex = bs.getTexture('powerupShockwave')
        self.texMolotov = bs.getTexture('powerupMolotov')
        self.texPetard = bs.getTexture('powerupPetard')
        self.texHolyBomb = bs.getTexture('powerupHolyBomb')
        self.texPortalBomb = bs.getTexture('powerupPortalBomb')
        self.texElonMuskMine = bs.getTexture('powerupElonMine')
        self.texAirstrike = bs.getTexture('powerupAirstrike')
        self.texColorBomb = bs.getTexture('powerupPaintBomb')
        self.texHighJump = bs.getTexture('powerupJump')
        self.texBot = bs.getTexture('neoSpazIcon')
        self.texSno = bs.getTexture('bunnyColor')
        self.texBlessing = bs.getTexture('powerupBlessing')
        self.texRailgun = bs.getTexture('powerupRailgun')

        self.healthPowerupSound = bs.getSound('healthPowerup')
        self.powerupSound = bs.getSound('powerup01')
        self.powerdownSound = bs.getSound('powerdown01')
        self.dropSound = bs.getSound('boxDrop')

        # material for powerups
        self.powerupMaterial = bs.Material()

        # material for anyone wanting to accept powerups
        self.powerupAcceptMaterial = bs.Material()

        # pass a powerup-touched message to applicable stuff
        self.powerupMaterial.addActions(
            conditions=(('theyHaveMaterial', self.powerupAcceptMaterial)),
            actions=(('modifyPartCollision', 'collide', True),
                     ('modifyPartCollision', 'physical', False),
                     ('message', 'ourNode', 'atConnect', _TouchedMessage())))

        # we dont wanna be picked up
        self.powerupMaterial.addActions(
            conditions=('theyHaveMaterial',
                        bs.getSharedObject('pickupMaterial')),
            actions=(('modifyPartCollision', 'collide', False)))

        self.powerupMaterial.addActions(
            conditions=('theyHaveMaterial',
                        bs.getSharedObject('footingMaterial')),
            actions=(('impactSound', self.dropSound, 0.5, 0.1)))

        self._powerupDist = []
        for p, freq in getDefaultPowerupDistribution():
            for i in range(int(freq)):
                self._powerupDist.append(p)

    def getRandomPowerupType(self, forceType=None, excludeTypes=[]):
        """
        Returns a random powerup type (string).
        See bs.Powerup.powerupType for available type values.

        There are certain non-random aspects to this; a 'curse' powerup,
        for instance, is always followed by a 'health' powerup (to keep things
        interesting). Passing 'forceType' forces a given returned type while
        still properly interacting with the non-random aspects of the system
        (ie: forcing a 'curse' powerup will result
        in the next powerup being health).
        """
        if forceType:
            t = forceType
        else:
            # if the last one was a curse, make this one a health to
            # provide some hope
            if self._lastPowerupType == 'curse':
                t = 'health'
            else:
                while True:
                    t = self._powerupDist[
                        random.randint(0, len(self._powerupDist)-1)]

                    if t not in excludeTypes:
                        break

        self._lastPowerupType = t
        return t


def getDefaultPowerupDistribution():
    return (
            ('tripleBombs', 3),
            ('iceBombs', 3),
            ('punch', 3),
            ('impactBombs', 3),
            ('stickyBombs', 3),
            ('luckyBlock', 3),
            ('extraAccelerator', 3),
            ('bot', 3),
            ('colorBomb', 2),
            ('landMines', 2),
            ('shield', 2),
            ('stickyForce', 2),
            ('dirt', 2),
            ('speed', 2),
            ('lego', 2),
            ('toxic', 2),
            ('slipper', 2),
            ('portalBomb', 2),
            ('elonMine', 2),
            ('airstrike', 2),
            ('shockwave', 2),
            ('banana', 2),
            ('artillery', 2),
            ('highJump', 2),
            ('petard', 2 if bsUI.gNewYear else 0),
            ('railgun', 1),
            ('blessing', 1),
            ('poison', 1),
            ('healthBomb', 1),
            ('molotov', 1),
            ('holyBomb', 1),
            ('cannon', 1),
            ('health', 1),
            ('curse', 1)
            )


class Powerup(bs.Actor):
    """
    category: Game Flow Classes

    A powerup box.
    This will deliver a bs.PowerupMessage to anything that touches it
    which has the bs.PowerupFactory.powerupAcceptMaterial applied.

    Attributes:

       powerupType
          The string powerup type.  This can be 'tripleBombs', 'punch',
          'iceBombs', 'impactBombs', 'landMines', 'stickyBombs', 'shield',
          'health', or 'curse'.

       node
          The 'prop' bs.Node representing this box.
    """
    def __init__(self, position=(0, 1, 0), powerupType='tripleBombs',
                 expire=True):
        """
        Create a powerup-box of the requested type at the requested position.

        see bs.Powerup.powerupType for valid type strings.
        """

        bs.Actor.__init__(self)
        factory = self.getFactory()
        self.powerupType = powerupType
        self._powersGiven = False

        mod = factory.model
        color = (1.0, 1.0, 1.0)

        if powerupType == 'tripleBombs':
            tex = factory.texBomb
            color = (1.0, 0.6, 0.0)

        elif powerupType == 'punch':
            tex = factory.texPunch
            color = (0.9, 0.2, 0.2)

        elif powerupType == 'blessing':
            tex = factory.texBlessing
            color = (0.2, 0.2, 1.0)

        elif powerupType == 'railgun':
            tex = factory.texRailgun
            color = (1, 0.4, 0.0)

        elif powerupType == 'iceBombs':
            tex = factory.texIceBombs
            color = (0.3, 0.5, 0.1)

        elif powerupType == 'impactBombs':
            tex = factory.texImpactBombs
            color = (1.0, 1.0, 1.0)

        elif powerupType == 'landMines':
            tex = factory.texLandMines
            color = (0.0, 0.6, 0.3)

        elif powerupType == 'stickyBombs':
            tex = factory.texStickyBombs
            color = (0.0, 1.0, 0.0)

        elif powerupType == 'shield':
            tex = factory.texShield
            color = (0.5, 0.1, 1.0)

        elif powerupType == 'health':
            tex = factory.texHealth
            color = (1.0, 1.0, 1.0)

        elif powerupType == 'curse':
            tex = factory.texCurse
            color = (0.1, 0.1, 1.0)

        elif powerupType == 'extraAccelerator':
            tex = factory.texExtraAccelerator
            color = (0.5, 0.1, 1.0)

        elif powerupType == 'luckyBlock':
            tex = factory.texLuckyBlock
            color = (1.0, 1.0, 0.0)

        elif powerupType == 'speed':
            tex = factory.texSpeed
            color = (0.0, 1.0, 0.0)

        elif powerupType == 'stickyForce':
            tex = factory.texStickyForce
            color = (0.1, 0.8, 0.9)

        elif powerupType == 'dirt':
            tex = factory.texDirt
            color = (0.9, 0.4, 0.0)

        elif powerupType == 'lego':
            tex = factory.texLego
            color = (1.0, 0.0, 0.0)

        elif powerupType == 'cannon':
            tex = factory.texCannon
            color = (0.0, 0.0, 1.0)

        elif powerupType == 'toxic':
            tex = factory.textoxic
            color = (1.0, 1.0, 0.0)

        elif powerupType == 'poison':
            tex = factory.texPoison
            color = (1.0, 0.0, 0.0)

        elif powerupType == 'slipper':
            tex = factory.texSlipper
            color = (0.0, 0.5, 1.0)

        elif powerupType == 'bot':
            tex = factory.texBot
            color = (1.0, 0.9, 0.3)

        elif powerupType == 'artillery':
            tex = factory.texArtillery
            color = (1.0, 0.1, 0.8)

        elif powerupType == 'healthBomb':
            tex = factory.texHealthBomb
            color = (1.0, 1.0, 1.0)

        elif powerupType == 'banana':
            tex = factory.texBanana
            color = (1.0, 1.0, 0.0)

        elif powerupType == 'shockwave':
            tex = factory.shockWaveTex
            color = (0.3, 0.3, 1.0)

        elif powerupType == 'petard':
            tex = factory.texPetard
            color = (1.0, 0.4, 0.4)

        elif powerupType == 'molotov':
            tex = factory.texMolotov
            color = (0.3, 0.3, 1.0)

        elif powerupType == 'holyBomb':
            tex = factory.texHolyBomb
            color = (1.0, 0.6, 0.0)

        elif powerupType == 'elonMine':
            tex = factory.texElonMuskMine
            color = (1.0, 1.0, 0.0)

        elif powerupType == 'airstrike':
            tex = factory.texAirstrike
            color = (1.0, 0.2, 0.2)

        elif powerupType == 'portalBomb':
            tex = factory.texPortalBomb
            color = (0.5, 0.1, 1.0)

        elif powerupType == 'highJump':
            tex = factory.texHighJump
            color = (0.5, 0.5, 0.5)

        elif powerupType == 'colorBomb':
            tex = factory.texColorBomb
            color = (0.5, 0.5, 0.5)

        else:
            raise Exception('invalid powerupType: '+str(powerupType))

        if len(position) != 3:
            raise Exception('expected 3 floats for position')

        self.node = bs.newNode('prop', delegate=self, attrs={
            'body': 'box',
            'position': position,
            'model': mod,
            'lightModel': mod,
            'shadowSize': 0.5,
            'colorTexture': tex,
            'reflection': 'powerup',
            'reflectionScale': [1.0],
            'materials': (factory.powerupMaterial,
                          bs.getSharedObject('objectMaterial'))})

        if powerupType == 'luckyBlock':
            self.light = bs.newNode('light', attrs={
                'position': self.node.position,
                'color': color,
                'volumeIntensityScale': 1.0,
                'intensity': 0.0,
                'radius': 0.2})

            self.node.connectAttr('position', self.light, 'position')

            curveS = bs.animate(self.light, 'intensity',
                                {0: 0, 500: 1.0, 1000: 0}, True)
        else:
            self.light = bs.newNode('light', attrs={
                'position': self.node.position,
                'color': color,
                'volumeIntensityScale': 1.0,
                'intensity': 0.4,
                'radius': 1})

            self.node.connectAttr('position', self.light, 'position')

            curveS = bs.animate(self.light, 'radius',
                                {0: 0, 140: 0.4, 200: 0.2})
            bs.gameTimer(200, curveS.delete)

        # animate in..
        curve = bs.animate(self.node, 'modelScale', {0: 0, 140: 1.6, 200: 1})
        bs.gameTimer(200, curve.delete)

        if expire:
            bs.gameTimer(defaultPowerupInterval-2500,
                         bs.WeakCall(self._startFlashing))

            bs.gameTimer(defaultPowerupInterval-1000,
                         bs.WeakCall(self.handleMessage, bs.DieMessage()))

    @classmethod
    def getFactory(cls):
        """
        Returns a shared bs.PowerupFactory object, creating it if necessary.
        """
        activity = bs.getActivity()
        if activity is None:
            raise Exception('no current activity')

        try:
            return activity._sharedPowerupFactory
        except Exception:
            f = activity._sharedPowerupFactory = PowerupFactory()
            return f

    def _startFlashing(self):
        if self.node.exists():
            self.node.flashing = True

    def handleMessage(self, m):
        self._handleMessageSanityCheck()
        if isinstance(m, PowerupAcceptMessage):
            factory = self.getFactory()
            if self.powerupType == 'health':
                bs.playSound(factory.healthPowerupSound, 3,
                             position=self.node.position)

            bs.playSound(factory.powerupSound, 3,
                         position=self.node.position)
            self._powersGiven = True
            bs.addStats('Collected powerups')
            self.handleMessage(bs.DieMessage())

        elif isinstance(m, _TouchedMessage):
            if not self._powersGiven:
                node = bs.getCollisionInfo('opposingNode')
                if node is not None and node.exists():
                    if self.powerupType == 'bot':
                        bsUtils.PopupText((bs.Lstr(
                            resource='descriptionBot')),
                            color=(1, 1, 1),
                            scale=1,
                            position=self.node.position).autoRetain()

                        p = node.getDelegate().getPlayer()
                        if 'bunnies' not in p.gameData:
                            p.gameData['bunnies'] = BuddyBunny.BunnyBotSet(p)

                        p.gameData['bunnies'].doBunny()
                        self._powersGiven = True
                        self.handleMessage(bs.DieMessage())
                    else:
                        node.handleMessage(
                            PowerupMessage(self.powerupType,
                                           sourceNode=self.node))

        elif isinstance(m, bs.DieMessage):
            if self.node.exists():
                if (m.immediate):
                    self.node.delete()
                    self.light.delete()
                else:
                    curve = bs.animate(self.node, 'modelScale', {0: 1, 100: 0})
                    bs.gameTimer(100, self.node.delete)

                    curveS = bs.animate(self.light, 'radius',
                                        {0: self.light.radius, 400: 0})
                    bs.gameTimer(401, curveS.delete)
                    bs.gameTimer(402, self.light.delete)

        elif isinstance(m, bs.OutOfBoundsMessage):
            self.handleMessage(bs.DieMessage())

        elif isinstance(m, bs.HitMessage):
            # dont die on punches (thats annoying)
            if m.hitType != 'punch':
                self.handleMessage(bs.DieMessage())
        else:
            bs.Actor.handleMessage(self, m)
