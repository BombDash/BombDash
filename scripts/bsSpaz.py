# -*- coding: utf-8 -*-
import random
import weakref
import bs
import bsUtils
import bsInternal
import bdUtils
import settings
import bsVector


# list of defined spazzes
appearances = {}


def getAppearances(includeLocked=False):
    disallowed = []
    if not includeLocked:
        # hmm yeah this'll be tough to hack...
        if not bsInternal._getPurchased('characters.santa'):
            disallowed.append('Santa Claus')
        if not bsInternal._getPurchased('characters.frosty'):
            disallowed.append('Frosty')
        if not bsInternal._getPurchased('characters.bones'):
            disallowed.append('Bones')
        if not bsInternal._getPurchased('characters.bernard'):
            disallowed.append('Bernard')
        if not bsInternal._getPurchased('characters.pixie'):
            disallowed.append('Pixel')
        if not bsInternal._getPurchased('characters.pascal'):
            disallowed.append('Pascal')
        if not bsInternal._getPurchased('characters.actionhero'):
            disallowed.append('Todd McBurton')
        if not bsInternal._getPurchased('characters.taobaomascot'):
            disallowed.append('Taobao Mascot')
        if not bsInternal._getPurchased('characters.agent'):
            disallowed.append('Agent Johnson')
        if not bsInternal._getPurchased('characters.jumpsuit'):
            disallowed.append('Lee')
        if not bsInternal._getPurchased('characters.assassin'):
            disallowed.append('Zola')
        if not bsInternal._getPurchased('characters.wizard'):
            disallowed.append('Grumbledorf')
        if not bsInternal._getPurchased('characters.cowboy'):
            disallowed.append('Butch')
        if not bsInternal._getPurchased('characters.witch'):
            disallowed.append('Witch')
        if not bsInternal._getPurchased('characters.warrior'):
            disallowed.append('Warrior')
        if not bsInternal._getPurchased('characters.superhero'):
            disallowed.append('Middle-Man')
        if not bsInternal._getPurchased('characters.alien'):
            disallowed.append('Alien')
        if not bsInternal._getPurchased('characters.oldlady'):
            disallowed.append('OldLady')
        if not bsInternal._getPurchased('characters.gladiator'):
            disallowed.append('Gladiator')
        if not bsInternal._getPurchased('characters.wrestler'):
            disallowed.append('Wrestler')
        if not bsInternal._getPurchased('characters.operasinger'):
            disallowed.append('Gretel')
        if not bsInternal._getPurchased('characters.robot'):
            disallowed.append('Robot')
        if not bsInternal._getPurchased('characters.cyborg'):
            disallowed.append('B-9000')
        if not bsInternal._getPurchased('characters.bunny'):
            disallowed.append('Easter Bunny')
        if not bsInternal._getPurchased('characters.kronk'):
            disallowed.append('Kronk')
        if not bsInternal._getPurchased('characters.zoe'):
            disallowed.append('Zoe')
        if not bsInternal._getPurchased('characters.jackmorgan'):
            disallowed.append('Jack Morgan')
        if not bsInternal._getPurchased('characters.mel'):
            disallowed.append('Mel')
        if not bsInternal._getPurchased('characters.snakeshadow'):
            disallowed.append('Snake Shadow')

        # unique characters
        if not settings.bolt:
            disallowed.append('Bolt')

        if not settings.puppeteer:
            disallowed.append('Eric')

    return [s for s in appearances.keys() if s not in disallowed]


gPowerupWearOffTime = 20000
gBasePunchPowerScale = 1.2 # obsolete - just used for demo guy now
gBasePunchCooldown = 400
gLameBotColor = (1.2, 0.9, 0.2)
gLameBotHighlight = (1.0, 0.5, 0.6)
gDefaultBotColor = (0.6, 0.6, 0.6)
gDefaultBotHighlight = (0.1, 0.3, 0.1)
gProBotColor = (1.0, 0.2, 0.1)
gProBotHighlight = (0.6, 0.1, 0.05)
gLastTurboSpamWarningTime = -99999


class _PickupMessage(object):
    'We wanna pick something up'
    pass


class _PunchHitMessage(object):
    'Message saying an object was hit'
    pass


class _CurseExplodeMessage(object):
    'We are cursed and should blow up now.'
    pass


class _BombDiedMessage(object):
    "A bomb has died and thus can be recycled"
    pass


class _RailgunFiredMessage(object):
    """
    category: BombDash Classes

    This class is used railgun.
    """
    def __init__(self, srcNode=None, sourcePlayer=None):
        """
        Instantiate a message with various bits of information
        on the type of hit that occurred.
        """
        # convert None to empty node-ref/player-ref
        if srcNode is None:
            srcNode = bs.Node(None)

        if sourcePlayer is None:
            sourcePlayer = bs.Player(None)

        self.srcNode = srcNode
        self.sourcePlayer = sourcePlayer


class NewFly(object):
    """
    category: BombDash Classes

    This class is used by command /fly3d and gives new flight for the player
    (on X Y Z coordinates, unlike standard flight on X Y).
    """
    def __init__(self, owner=None):
        self.owner = owner
        if self.owner.exists():
            self.box = bs.SimpleBox(
                position=self.owner.actor.node.position).autoRetain()

            self.box.node.model = None
            self.owner.actor.node.holdNode = self.box.node
            self.owner.actor.node.holdBody = 1
            self.set_fly()
        else:
            bs.screenMessage(bs.Lstr(resource='errorText'))

    def move(self, type_name):
        """ Motion processing by type. """
        if self.box.exists():
            if type_name == 'up':
                self.box.node.extraAcceleration = (0, 45, 0)
            elif type_name == 'down':
                self.box.node.extraAcceleration = (0, 40, 0)
            elif type_name == 'go':
                self.box.node.velocity = (-50, 0, 0)
            elif type_name == 'back':
                self.box.node.velocity = (50, 0, 0)
            elif type_name == 'left':
                self.box.node.velocity = (0, 0, -50)
            elif type_name == 'right':
                self.box.node.velocity = (0, 0, 50)

    def reset_move(self):
        """
        Flight dumping, removal of a box
        and return of standard management.
        """
        if self.owner.exists() and self.box.exists():
            bs.PopupText(
                bs.Lstr(resource='flightModeDisabled'),
                color=(1, 1, 1),
                scale=1.0,
                position=self.owner.actor.node.position).autoRetain()

            self.owner.actor.node.holdBody = 0
            self.box.node.delete()
            self.owner.actor.connectControlsToPlayer()

        elif not self.owner.exists() and self.box.exists():
            self.box.node.delete()

        elif self.owner.exists() and not self.box.exists():
            self.owner.actor.node.holdBody = 0
            self.owner.actor.connectControlsToPlayer()

    def set_fly(self):
        """ Change of management of the player on function of new flight. """
        self.owner.assignInputCall('pickUpPress', bs.Call(self.move, 'up'))
        self.owner.assignInputCall('jumpPress', bs.Call(self.move, 'down'))
        self.owner.assignInputCall('leftPress', bs.Call(self.move, 'go'))
        self.owner.assignInputCall('rightPress', bs.Call(self.move, 'back'))
        self.owner.assignInputCall('upPress', bs.Call(self.move, 'left'))
        self.owner.assignInputCall('downPress', bs.Call(self.move, 'right'))
        self.owner.assignInputCall('punchPress', bs.Call(self.reset_move))
        self.owner.assignInputCall('bombPress', bs.Call(self.reset_move))


class PermissionEffect(object):
    """
    category: BombDash Classes

    This class is used for creation of a prefix over the player.
    The prefix is the status of the player (for example Admin or the VIP).
    """
    def __init__(self, position=(0, 1, 0), owner=None,
                 prefix='ADMIN', animate=True,
                 particlesType=1, emitType='spark',
                 prefixAnimation={0: (1, 1, 1), 500: (0.5, 0.5, 0.5)}):
        self.position = position
        self.owner = owner
        self.animate = animate
        self.animation = prefixAnimation
        self.particlesType = particlesType
        self.emitType = emitType
        self.offset = (0, 1.2, 0)
        self.timer = None
        self._Text = None
        self.m = None

        if self.particlesType != 0:
            self.timer = bs.Timer(
                60 if self.emitType in ['sweat', 'spark'] else 110,
                bs.Call(self.emit),
                repeat=True)

        self.m = bs.newNode('math', owner=self.owner, attrs={
            'input1': self.offset,
            'operation': 'add'})

        self.owner.connectAttr('torsoPosition', self.m, 'input2')

        self._Text = bs.newNode('text', owner=self.owner, attrs={
            'text': prefix,
            'inWorld': True,
            'shadow': 0.4,
            'flatness': 0,
            'scale': 0.01,
            'hAlign': 'center'})

        self.m.connectAttr('output', self._Text, 'position')

        if self.animate:
            bs.animateArray(self._Text, 'color', 3, self.animation, True)

    def emit(self):
        """ Create effect. """
        if self.owner is not None and self.owner.exists() \
                and not self.owner.dead:
            if self.particlesType == 1:
                bs.emitBGDynamics(
                    position=(self.owner.position[0],
                              self.owner.position[1]-0.25,
                              self.owner.position[2]),
                    velocity=(0, 0, 0),
                    count=10,
                    scale=0.1+random.random(),
                    spread=0.15,
                    chunkType=self.emitType)

            elif self.particlesType == 2:
                bs.emitBGDynamics(
                    position=(self.owner.position[0],
                              self.owner.position[1]-0.5,
                              self.owner.position[2]),
                    count=10,
                    scale=0.1+random.random(),
                    spread=0.001,
                    chunkType=self.emitType,
                    emitType='stickers')


class Appearance(object):
    """Create and fill out one of these suckers to define a spaz appearance"""
    def __init__(self, name):
        self.name = name
        if appearances.has_key(self.name):
            raise Exception("spaz appearance name \""
                            + self.name + "\" already exists.")
        appearances[self.name] = self
        self.colorTexture = ""
        self.headModel = ""
        self.torsoModel = ""
        self.pelvisModel = ""
        self.upperArmModel = ""
        self.foreArmModel = ""
        self.handModel = ""
        self.upperLegModel = ""
        self.lowerLegModel = ""
        self.toesModel = ""
        self.jumpSounds = []
        self.attackSounds = []
        self.impactSounds = []
        self.deathSounds = []
        self.pickupSounds = []
        self.fallSounds = []
        self.style = 'spaz'
        self.defaultColor = None
        self.defaultHighlight = None


class SpazFactory(object):
    """
    Category: Game Flow Classes

    Wraps up media and other resources used by bs.Spaz instances.
    Generally one of these is created per bs.Activity and shared
    between all spaz instances.  Use bs.Spaz.getFactory() to return
    the shared factory for the current activity.

    Attributes:

       impactSoundsMedium
          A tuple of bs.Sounds for when a bs.Spaz hits something kinda hard.

       impactSoundsHard
          A tuple of bs.Sounds for when a bs.Spaz hits something really hard.

       impactSoundsHarder
          A tuple of bs.Sounds for when a bs.Spaz hits something really
          really hard.

       singlePlayerDeathSound
          The sound that plays for an 'importan' spaz death such as in
          co-op games.

       punchSound
          A standard punch bs.Sound.

       punchSoundsStrong
          A tuple of stronger sounding punch bs.Sounds.

       punchSoundStronger
          A really really strong sounding punch bs.Sound.

       swishSound
          A punch swish bs.Sound.

       blockSound
          A bs.Sound for when an attack is blocked by invincibility.

       shatterSound
          A bs.Sound for when a frozen bs.Spaz shatters.

       splatterSound
          A bs.Sound for when a bs.Spaz blows up via curse.

       spazMaterial
          A bs.Material applied to all of parts of a bs.Spaz.

       rollerMaterial
          A bs.Material applied to the invisible roller ball body that a bs.Spaz
          uses for locomotion.

       punchMaterial
          A bs.Material applied to the 'fist' of a bs.Spaz.

       pickupMaterial
          A bs.Material applied to the 'grabber' body of a bs.Spaz.

       curseMaterial
          A bs.Material applied to a cursed bs.Spaz that triggers an explosion.
    """

    def _preload(self, character):
        """
        Preload media that will be needed for a given character.
        """
        self._getMedia(character)

    def __init__(self):
        """
        Instantiate a factory object.
        """
        self.railgunSound = bs.getSound('railgun')
        self.railgunChargeSound = bs.getSound('railgunCharge')
        self.impactSoundsMedium = (bs.getSound('impactMedium'),
                                bs.getSound('impactMedium2'))
        self.impactSoundsHard = (bs.getSound('impactHard'),
                                 bs.getSound('impactHard2'),
                                 bs.getSound('impactHard3'))
        self.impactSoundsHarder = (bs.getSound('bigImpact'),
                                   bs.getSound('bigImpact2'))
        self.singlePlayerDeathSound = bs.getSound('playerDeath')
        self.punchSound = bs.getSound('punch01')

        self.punchSoundsStrong = (bs.getSound('punchStrong01'),
                                  bs.getSound('punchStrong02'))

        self.punchSoundStronger = bs.getSound('superPunch')

        self.swishSound = bs.getSound('punchSwish')
        self.blockSound = bs.getSound('block')
        self.shatterSound = bs.getSound('shatter')
        self.splatterSound = bs.getSound('splatter')

        self.spazMaterial = bs.Material()
        self.rollerMaterial = bs.Material()
        self.punchMaterial = bs.Material()
        self.pickupMaterial = bs.Material()
        self.curseMaterial = bs.Material()

        footingMaterial = bs.getSharedObject('footingMaterial')
        objectMaterial = bs.getSharedObject('objectMaterial')
        playerMaterial = bs.getSharedObject('playerMaterial')
        regionMaterial = bs.getSharedObject('regionMaterial')

        # send footing messages to spazzes so they know when they're on solid
        # ground.
        # eww this should really just be built into the spaz node
        self.rollerMaterial.addActions(
            conditions=('theyHaveMaterial', footingMaterial),
            actions=(('message', 'ourNode', 'atConnect', 'footing', 1),
                     ('message', 'ourNode', 'atDisconnect', 'footing', -1)))

        self.spazMaterial.addActions(
            conditions=('theyHaveMaterial', footingMaterial),
            actions=(('message', 'ourNode', 'atConnect', 'footing', 1),
                     ('message', 'ourNode', 'atDisconnect', 'footing', -1)))
        # punches
        self.punchMaterial.addActions(
            conditions=('theyAreDifferentNodeThanUs',),
            actions=(('modifyPartCollision', 'collide', True),
                     ('modifyPartCollision', 'physical', False),
                     ('message', 'ourNode', 'atConnect', _PunchHitMessage())))
        # pickups
        self.pickupMaterial.addActions(
            conditions=(('theyAreDifferentNodeThanUs',),
                        'and', ('theyHaveMaterial', objectMaterial)),
            actions=(('modifyPartCollision', 'collide', True),
                     ('modifyPartCollision', 'physical', False),
                     ('message', 'ourNode', 'atConnect', _PickupMessage())))
        # curse
        self.curseMaterial.addActions(
            conditions=(('theyAreDifferentNodeThanUs',),
                        'and', ('theyHaveMaterial', playerMaterial)),
            actions=('message', 'ourNode', 'atConnect', _CurseExplodeMessage()))

        self.footImpactSounds = (bs.getSound('footImpact01'),
                                 bs.getSound('footImpact02'),
                                 bs.getSound('footImpact03'))

        self.footSkidSound = bs.getSound('skid01')
        self.footRollSound = bs.getSound('scamper01')

        self.rollerMaterial.addActions(
            conditions=('theyHaveMaterial', footingMaterial),
            actions=(('impactSound', self.footImpactSounds, 1, 0.2),
                     ('skidSound', self.footSkidSound, 20, 0.3),
                     ('rollSound', self.footRollSound, 20, 3.0)))

        self.skidSound = bs.getSound('gravelSkid')

        self.spazMaterial.addActions(
            conditions=('theyHaveMaterial', footingMaterial),
            actions=(('impactSound', self.footImpactSounds, 20, 6),
                     ('skidSound', self.skidSound, 2.0, 1),
                     ('rollSound', self.skidSound, 2.0, 1)))

        self.shieldUpSound = bs.getSound('shieldUp')
        self.shieldDownSound = bs.getSound('shieldDown')
        self.shieldHitSound = bs.getSound('shieldHit')

        # we dont want to collide with stuff we're initially overlapping
        # (unless its marked with a special region material)
        self.spazMaterial.addActions(
            conditions=((('weAreYoungerThan', 51),
                         'and', ('theyAreDifferentNodeThanUs',)),
                        'and', ('theyDontHaveMaterial', regionMaterial)),
            actions=(('modifyNodeCollision', 'collide', False)))

        self.spazMedia = {}

        # lets load some basic rules (allows them to be tweaked from the
        # master server)
        self.shieldDecayRate = bsInternal._getAccountMiscReadVal('rsdr', 10.0)
        self.punchCooldown = bsInternal._getAccountMiscReadVal('rpc', 400)
        self.punchCooldownGloves = \
            bsInternal._getAccountMiscReadVal('rpcg', 300)
        self.punchPowerScale = bsInternal._getAccountMiscReadVal('rpp', 1.2)
        self.punchPowerScaleGloves = \
            bsInternal._getAccountMiscReadVal('rppg', 1.4)
        self.maxShieldSpilloverDamage = \
            bsInternal._getAccountMiscReadVal('rsms', 500)

    def _getStyle(self, character):
        return appearances[character].style

    def _getMedia(self, character):
        t = appearances[character]
        if not self.spazMedia.has_key(character):
            m = self.spazMedia[character] = {
                'jumpSounds':[bs.getSound(s) for s in t.jumpSounds],
                'attackSounds':[bs.getSound(s) for s in t.attackSounds],
                'impactSounds':[bs.getSound(s) for s in t.impactSounds],
                'deathSounds':[bs.getSound(s) for s in t.deathSounds],
                'pickupSounds':[bs.getSound(s) for s in t.pickupSounds],
                'fallSounds':[bs.getSound(s) for s in t.fallSounds],
                'colorTexture':bs.getTexture(t.colorTexture),
                'colorMaskTexture':bs.getTexture(t.colorMaskTexture),
                'headModel':bs.getModel(t.headModel),
                'torsoModel':bs.getModel(t.torsoModel),
                'pelvisModel':bs.getModel(t.pelvisModel),
                'upperArmModel':bs.getModel(t.upperArmModel),
                'foreArmModel':bs.getModel(t.foreArmModel),
                'handModel':bs.getModel(t.handModel),
                'upperLegModel':bs.getModel(t.upperLegModel),
                'lowerLegModel':bs.getModel(t.lowerLegModel),
                'toesModel':bs.getModel(t.toesModel)
            }
        else:
            m = self.spazMedia[character]
        return m

class Spaz(bs.Actor):
    """
    category: Game Flow Classes

    Base class for various Spazzes.
    A Spaz is the standard little humanoid character in the game.
    It can be controlled by a player or by AI, and can have
    various different appearances.  The name 'Spaz' is not to be
    confused with the 'Spaz' character in the game, which is just
    one of the skins available for instances of this class.

    Attributes:

       node
          The 'spaz' bs.Node.
    """
    pointsMult = 1
    curseTime = 5000
    defaultBombCount = 1
    defaultBombType = 'normal'
    defaultBoxingGloves = False
    defaultShields = False

    def __init__(self, color=(1, 1, 1), highlight=(0.5, 0.5, 0.5),
                 character="Spaz", sourcePlayer=None, startInvincible=True,
                 canAcceptPowerups=True, powerupsExpire=False, demoMode=False):
        """
        Create a new spaz with the requested color, character, etc.
        """

        bs.Actor.__init__(self)
        activity = self.getActivity()

        self.shovel = False
        self.character = character
        self.shovels = 0
        self.Railgun = False
        self.RailgunFired = 0

        factory = self.getFactory()

        # we need to behave slightly different in the tutorial
        self._demoMode = demoMode

        self.playBigDeathSound = False

        # translate None into empty player-ref
        if sourcePlayer is None: sourcePlayer = bs.Player(None)

        # scales how much impacts affect us (most damage calcs)
        self._impactScale = 1.0

        self.sourcePlayer = sourcePlayer
        self._dead = False
        if self._demoMode: # preserve old behavior
            self._punchPowerScale = gBasePunchPowerScale
        else:
            self._punchPowerScale = factory.punchPowerScale
        self.fly = bs.getSharedObject('globals').happyThoughtsMode
        self._hockey = activity._map.isHockey
        self._punchedNodes = set()
        self._cursed = False
        self._connectedToPlayer = None

        materials = [factory.spazMaterial,
                     bs.getSharedObject('objectMaterial'),
                     bs.getSharedObject('playerMaterial')]

        rollerMaterials = [factory.rollerMaterial,
                           bs.getSharedObject('playerMaterial')]

        extrasMaterials = []

        if canAcceptPowerups:
            pam = bs.Powerup.getFactory().powerupAcceptMaterial
            materials.append(pam)
            rollerMaterials.append(pam)
            extrasMaterials.append(pam)

        media = factory._getMedia(character)
        self.node = bs.newNode(
            type="spaz",
            delegate=self,
            attrs={'color':color,
                   'behaviorVersion':0 if demoMode else 1,
                   'demoMode':True if demoMode else False,
                   'highlight':highlight,
                   'jumpSounds':media['jumpSounds'],
                   'attackSounds':media['attackSounds'],
                   'impactSounds':media['impactSounds'],
                   'deathSounds':media['deathSounds'],
                   'pickupSounds':media['pickupSounds'],
                   'fallSounds':media['fallSounds'],
                   'colorTexture':media['colorTexture'],
                   'colorMaskTexture':media['colorMaskTexture'],
                   'headModel':media['headModel'],
                   'torsoModel':media['torsoModel'],
                   'pelvisModel':media['pelvisModel'],
                   'upperArmModel':media['upperArmModel'],
                   'foreArmModel':media['foreArmModel'],
                   'handModel':media['handModel'],
                   'upperLegModel':media['upperLegModel'],
                   'lowerLegModel':media['lowerLegModel'],
                   'toesModel':media['toesModel'],
                   'style':factory._getStyle(character),
                   'fly':self.fly,
                   'hockey':self._hockey,
                   'materials':materials,
                   'rollerMaterials':rollerMaterials,
                   'extrasMaterials':extrasMaterials,
                   'punchMaterials':(factory.punchMaterial,
                                     bs.getSharedObject('attackMaterial')),
                   'pickupMaterials':(factory.pickupMaterial,
                                      bs.getSharedObject('pickupMaterial')),
                   'invincible':startInvincible,
                   'sourcePlayer':sourcePlayer})

        self.shield = None
        self.shield2 = None
        self.shield3 = None
        self.fired = False
        self.shockText = None

        # punch power scale for show in shock info. Updates in def shock()
        self.pps0 = None
        # PermissionEffect
        self.pe = None

        if startInvincible:
            def _safeSetAttr(node, attr, val):
                if node.exists(): setattr(node, attr, val)
            bs.gameTimer(1000, bs.Call(_safeSetAttr, self.node,
                                       'invincible', False))
        self.hitPoints = 1000
        self.hitPointsMax = 1000
        self.bombCount = self.defaultBombCount
        self._maxBombCount = self.defaultBombCount
        self.bombTypeDefault = self.defaultBombType
        self.bombType = self.bombTypeDefault
        self.landMineCount = 0
        self.portalCount = 0
        self.elonMineCount = 0
        self.holyBombCount = 0
        self.airstrikeCount = 0
        self.toxicCount = 0
        self.bananCount = 0
        self.petardCount = 0
        self.dirtCount = 0
        self.molotovCount = 0
        self.poisonCount = 0
        self.slipperCount = 0
        if character == 'Bum':
            s = random.random()
            if s > 0.4:
                self.setSlipperCount(1)

        self.healBombCount = 0
        self.colorBombCount = 0
        self.forceBombCount = 0
        self.blastRadius = 2.0
        self.powerupsExpire = powerupsExpire
        if self._demoMode: # preserve old behavior
            self._punchCooldown = gBasePunchCooldown
        else:
            self._punchCooldown = factory.punchCooldown
        self._jumpCooldown = 250
        self._pickupCooldown = 0
        self._bombCooldown = 0
        self._hasBoxingGloves = False
        if self.defaultBoxingGloves: self.equipBoxingGloves()
        self.lastPunchTime = -9999
        self.lastJumpTime = -9999
        self.lastPickupTime = -9999
        self.lastRunTime = -9999
        self._lastRunValue = 0
        self.lastBombTime = -9999
        self._turboFilterTimes = {}
        self._turboFilterTimeBucket = 0
        self._turboFilterCounts = {}
        self.frozen = False
        self.shattered = False
        self._lastHitTime = None
        self._numTimesHit = 0
        self._bombHeld = False
        if self.defaultShields: self.equipShields()
        self._droppedBombCallbacks = []

        # deprecated stuff.. need to make these into lists
        self.punchCallback = None
        self.pickUpPowerupCallback = None

    def onFinalize(self):
        bs.Actor.onFinalize(self)

        # release callbacks/refs so we don't wind up with dependency loops..
        self._droppedBombCallbacks = []
        self.punchCallback = None
        self.pickUpPowerupCallback = None

    def addDroppedBombCallback(self, call):
        """
        Add a call to be run whenever this Spaz drops a bomb.
        The spaz and the newly-dropped bomb are passed as arguments.
        """
        self._droppedBombCallbacks.append(call)

    def isAlive(self):
        """
        Method override; returns whether ol' spaz is still kickin'.
        """
        return not self._dead

    @classmethod
    def getFactory(cls):
        """
        Returns the shared bs.SpazFactory object, creating it if necessary.
        """
        activity = bs.getActivity()
        if activity is None: raise Exception("no current activity")
        try: return activity._sharedSpazFactory
        except Exception:
            f = activity._sharedSpazFactory = SpazFactory()
            return f

    def exists(self):
        return self.node.exists()

    def _hideScoreText(self):
        if self._scoreText.exists():
            bs.animate(self._scoreText, 'scale',
                       {0:self._scoreText.scale, 200:0})

    def _turboFilterAddPress(self, source):
        """
        Can pass all button presses through here; if we see an obscene number
        of them in a short time let's shame/pushish this guy for using turbo
        """
        t = bs.getNetTime()
        tBucket = int(t/1000)
        if tBucket == self._turboFilterTimeBucket:
            # add only once per timestep (filter out buttons triggering
            # multiple actions)
            if t != self._turboFilterTimes.get(source, 0):
                self._turboFilterCounts[source] = \
                    self._turboFilterCounts.get(source, 0) + 1
                self._turboFilterTimes[source] = t
                # (uncomment to debug; prints what this count is at)
                # bs.screenMessage( str(source) + " "
                #                   + str(self._turboFilterCounts[source]))
                if self._turboFilterCounts[source] == 15:

                    # knock 'em out.  That'll learn 'em.
                    self.node.handleMessage("knockout", 500.0)

                    # also issue periodic notices about who is turbo-ing
                    realTime = bs.getRealTime()
                    global gLastTurboSpamWarningTime
                    if realTime > gLastTurboSpamWarningTime + 30000:
                        gLastTurboSpamWarningTime = realTime
                        bs.screenMessage(
                            bs.Lstr(translate=('statements',
                                               ('Warning to ${NAME}:  '
                                                'turbo / button-spamming knocks'
                                                ' you out.')),
                                    subs=[('${NAME}', self.node.name)]),
                            color=(1, 0.5, 0))
                        bs.playSound(bs.getSound('error'))
        else:
            self._turboFilterTimes = {}
            self._turboFilterTimeBucket = tBucket
            self._turboFilterCounts = {source:1}

    def setScoreText(self, t, color=(1, 1, 0.4), flash=False):
        """
        Utility func to show a message momentarily over our spaz that follows
        him around; Handy for score updates and things.
        """
        colorFin = bs.getSafeColor(color)[:3]
        if not self.node.exists(): return
        try: exists = self._scoreText.exists()
        except Exception: exists = False
        if not exists:
            startScale = 0.0
            m = bs.newNode('math', owner=self.node, attrs={ 'input1':(0, 1.4, 0),
                                                            'operation':'add' })
            self.node.connectAttr('torsoPosition', m, 'input2')
            self._scoreText = bs.newNode('text',
                                          owner=self.node,
                                          attrs={'text':t,
                                                 'inWorld':True,
                                                 'shadow':1.0,
                                                 'flatness':1.0,
                                                 'color':colorFin,
                                                 'scale':0.02,
                                                 'hAlign':'center'})
            m.connectAttr('output', self._scoreText, 'position')
        else:
            self._scoreText.color = colorFin
            startScale = self._scoreText.scale
            self._scoreText.text = t
        if flash:
            combine = bs.newNode("combine", owner=self._scoreText,
                                 attrs={'size':3})
            sc = 1.8
            offs = 0.5
            t = 300
            for i in range(3):
                c1 = offs+sc*colorFin[i]
                c2 = colorFin[i]
                bs.animate(combine, 'input'+str(i), {0.5*t:c2,
                                                   0.75*t:c1,
                                                   1.0*t:c2})
            combine.connectAttr('output', self._scoreText, 'color')

        bs.animate(self._scoreText, 'scale', {0:startScale, 200:0.02})
        self._scoreTextHideTimer = bs.Timer(1000,
                                            bs.WeakCall(self._hideScoreText))

    def onJumpPress(self):
        """
        Called to 'press jump' on this spaz;
        used by player or AI connections.
        """
        if not self.node.exists(): return
        t = bs.getGameTime()
        if t - self.lastJumpTime >= self._jumpCooldown:
            self.node.jumpPressed = True
            self.lastJumpTime = t
        self._turboFilterAddPress('jump')

    def onJumpRelease(self):
        """
        Called to 'release jump' on this spaz;
        used by player or AI connections.
        """
        if not self.node.exists(): return
        self.node.jumpPressed = False

    def onPickUpPress(self):
        """
        Called to 'press pick-up' on this spaz;
        used by player or AI connections.
        """
        if not self.node.exists(): return
        t = bs.getGameTime()
        if t - self.lastPickupTime >= self._pickupCooldown:
            self.node.pickUpPressed = True
            self.lastPickupTime = t
        self._turboFilterAddPress('pickup')

    def onPickUpRelease(self):
        """
        Called to 'release pick-up' on this spaz;
        used by player or AI connections.
        """
        if not self.node.exists(): return
        self.node.pickUpPressed = False

    def _onHoldPositionPress(self):
        """
        Called to 'press hold-position' on this spaz;
        used for player or AI connections.
        """
        if not self.node.exists(): return
        self.node.holdPositionPressed = True
        self._turboFilterAddPress('holdposition')

    def _onHoldPositionRelease(self):
        """
        Called to 'release hold-position' on this spaz;
        used for player or AI connections.
        """
        if not self.node.exists(): return
        self.node.holdPositionPressed = False

    def onPunchPress(self):
        """
        Called to 'press punch' on this spaz;
        used for player or AI connections.
        """
        if (not self.node.exists()
            or self.frozen
            or self.node.knockout > 0.0): return
        t = bs.getGameTime()
        if t - self.lastPunchTime >= self._punchCooldown:
            if self.punchCallback is not None:
                self.punchCallback(self)
            self._punchedNodes = set() # reset this..
            self.lastPunchTime = t
            self.node.punchPressed = True
            if not self.node.holdNode.exists():
                bs.gameTimer(100, bs.WeakCall(self._safePlaySound,
                                              self.getFactory().swishSound,
                                              0.8))
        self._turboFilterAddPress('punch')

    def _safePlaySound(self, sound, volume):
        """
        Plays a sound at our position if we exist.
        """
        if self.node.exists():
            bs.playSound(sound, volume, self.node.position)

    def onPunchRelease(self):
        """
        Called to 'release punch' on this spaz;
        used for player or AI connections.
        """
        if not self.node.exists(): return
        self.node.punchPressed = False

    def onBombPress(self):
        """
        Called to 'press bomb' on this spaz;
        used for player or AI connections.
        """
        if not self.node.exists(): return

        if self._dead or self.frozen: return
        if self.node.knockout > 0.0: return
        t = bs.getGameTime()
        if t - self.lastBombTime >= self._bombCooldown:
            self.lastBombTime = t
            self.node.bombPressed = True
            if not self.node.holdNode.exists():
                self.dropBomb()

        self._turboFilterAddPress('bomb')

    def onBombRelease(self):
        """
        Called to 'release bomb' on this spaz;
        used for player or AI connections.
        """
        if not self.node.exists(): return
        self.node.bombPressed = False

    def onRun(self, value):
        """
        Called to 'press run' on this spaz;
        used for player or AI connections.
        """
        if not self.node.exists(): return

        t = bs.getGameTime()
        self.lastRunTime = t
        self.node.run = value

        # filtering these events would be tough since its an analog
        # value, but lets still pass full 0-to-1 presses along to
        # the turbo filter to punish players if it looks like they're turbo-ing
        if self._lastRunValue < 0.01 and value > 0.99:
            self._turboFilterAddPress('run')

        self._lastRunValue = value


    def onFlyPress(self):
        """
        Called to 'press fly' on this spaz;
        used for player or AI connections.
        """
        if not self.node.exists(): return
        # not adding a cooldown time here for now; slightly worried
        # input events get clustered up during net-games and we'd wind up
        # killing a lot and making it hard to fly.. should look into this.
        self.node.flyPressed = True
        self._turboFilterAddPress('fly')

    def onFlyRelease(self):
        """
        Called to 'release fly' on this spaz;
        used for player or AI connections.
        """
        if not self.node.exists(): return
        self.node.flyPressed = False

    def onMove(self, x, y):
        """
        Called to set the joystick amount for this spaz;
        used for player or AI connections.
        """
        if not self.node.exists(): return
        self.node.handleMessage("move", x, y)

    def onMoveUpDown(self, value):
        """
        Called to set the up/down joystick amount on this spaz;
        used for player or AI connections.
        value will be between -32768 to 32767
        WARNING: deprecated; use onMove instead.
        """
        if not self.node.exists(): return
        self.node.moveUpDown = value

    def onMoveLeftRight(self, value):
        """
        Called to set the left/right joystick amount on this spaz;
        used for player or AI connections.
        value will be between -32768 to 32767
        WARNING: deprecated; use onMove instead.
        """
        if not self.node.exists(): return
        self.node.moveLeftRight = value

    def onPunched(self, damage):
        """
        Called when this spaz gets punched.
        """
        pass

    def shock(self):
        """
        category: BombDash Functions

        Special function of carrying out a shock therapy for a spaz :D
        """
        if self.pps0 is None:
            self.pps0 = self._punchPowerScale

        if self._punchPowerScale > 0.2:
            self._punchPowerScale -= 0.3

            # wtf, it sometimes happening?!
            if self._punchPowerScale < 0.2:
                self._punchPowerScale = 0.2

        factory = self.getFactory()

        m = bs.newNode('math', owner=self.node, attrs={
            'input1': (0, 1.2, 0),
            'operation': 'add'})

        self.node.connectAttr('position', m, 'input2')

        if self.shockText is None:
            self.shockText = bs.newNode('text', owner=self.node, attrs={
                'text': u'ϟ '+unicode(
                    self._punchPowerScale)+u'/'+unicode(self.pps0),
                'inWorld': True,
                'shadow': 1.2,
                'flatness': 1.0,
                'color': (0.5, 0.5, 1),
                'scale': 1.2,
                'hAlign': 'center'})

            bs.animate(self.shockText, 'scale', {0: 0.0, 300: 0.01})

            m.connectAttr('output', self.shockText, 'position')
        else:
            self.shockText.text = u'ϟ '+unicode(self._punchPowerScale)+u'/1.2'
            bs.animate(
                self.shockText, 'scale', {0: 0.01, 100: 0.015, 200: 0.01})

        def heal():
            self._punchPowerScale = factory.punchPowerScale
            self.shockText.delete()
            self.shockText = None

        self.shockTimer = bs.Timer(4500, heal)

    def getDeathPoints(self, how):
        'Get the points awarded for killing this spaz'
        numHits = float(max(1, self._numTimesHit))
        # base points is simply 10 for 1-hit-kills and 5 otherwise
        importance = 2 if numHits < 2 else 1
        return ((10 if numHits < 2 else 5) * self.pointsMult, importance)

    def curse(self):
        """
        Give this poor spaz a curse;
        he will explode in 5 seconds.
        """
        if not self._cursed:
            factory = self.getFactory()
            self._cursed = True
            # add the curse material..
            for attr in ['materials', 'rollerMaterials']:
                materials = getattr(self.node, attr)
                if not factory.curseMaterial in materials:
                    setattr(self.node, attr,
                            materials + (factory.curseMaterial,))

            # -1 specifies no time limit
            if self.curseTime == -1:
                self.node.curseDeathTime = -1
            else:
                self.node.curseDeathTime = bs.getGameTime()+5000
                bs.gameTimer(5000, bs.WeakCall(self.curseExplode))

    def fire(self):
        """
        category: BombDash Functions

        To set fire to a spaz.
        """
        self.fired = True
        sounds = [bs.getSound('fire1'), bs.getSound('fire2'),
                  bs.getSound('fire3')]

        screamSounds = SpazFactory()._getMedia(self.character)['jumpSounds'] \
            + SpazFactory()._getMedia(self.character)['impactSounds']

        time = random.randint(1000, 5000)
        self.node.handleMessage('celebrate', time)

        def off():
            self.fired = False
            if self.fireLight is not None:
                self.fireLight.delete()

        bs.gameTimer(time, off)

        def doFire():
            if self.node.exists():
                h = random.randint(1, 3)
                self.hitPoints -= h
                if self.hitPoints < 15:
                    self.fired = False
                    self.node.handleMessage(bs.DieMessage())

                self.node.hurt = 1.0 - float(self.hitPoints)/self.hitPointsMax
                pos = self.node.position

                bs.emitBGDynamics(
                    position=(pos[0]+random.uniform(-0.3, 0.3),
                              pos[1]+random.uniform(-0.3, 0.3),
                              pos[2]+random.uniform(-0.3, 0.3)),
                    velocity=(0, 7, 0),
                    count=int(5 + random.random()*5),
                    scale=random.random()*2,
                    spread=random.random()*0.2,
                    chunkType='sweat')

                if self.fired:
                    bs.gameTimer(5, bs.Call(doFire))

        def doSound():
            if self.node.exists():
                pos = self.node.position
                bs.playSound(
                    random.choice(sounds),
                    position=pos)

                if self.fired:
                    bs.gameTimer(480, bs.Call(doSound))

        def doScream():
            if self.node is not None and self.node.exists():
                bs.playSound(
                    random.choice(screamSounds),
                    position=self.node.position,
                    volume=0.6 + random.random()*0.3)

                if self.fired:
                    bs.gameTimer(random.randint(150, 500), doScream)

        self.fireLight = bs.newNode('light', attrs={
            'position': self.node.position,
            'color': (1, 0.4, 0),
            'volumeIntensityScale': 1.0,
            'intensity': 0.8,
            'radius': 0.1})

        self.node.connectAttr('position', self.fireLight, 'position')

        intensity = {
            0: random.uniform(0.8, 1.5), 100: random.uniform(0.8, 1.5),
            200: random.uniform(0.8, 1.5), 300: random.uniform(0.8, 1.5),
            400: random.uniform(0.8, 1.5), 500: random.uniform(0.8, 1.5),
            600: random.uniform(0.8, 1.5), 700: random.uniform(0.8, 1.5),
            800: random.uniform(0.8, 1.5), 900: random.uniform(0.8, 1.5),
            1000: random.uniform(0.8, 1.5), 1100: random.uniform(0.8, 1.5),
            1200: random.uniform(0.8, 1.5), 1300: random.uniform(0.8, 1.5)
        }

        colors = {
            0: (1, 0.4, 0), 100: (1, 0.3, 0), 200: (1, 0.6, 0),
            300: (1, 0.5, 0), 400: (1, 0.2, 0), 500: (1, 0.4, 0),
            600: (1, 0.3, 0)
        }

        self.c2 = bs.animate(self.fireLight, 'intensity', intensity, True)
        self.c3 = bs.animateArray(self.fireLight, 'color', 3, colors, True)

        doFire()
        doSound()
        doScream()

    def equipBoxingGloves(self):
        """
        Give this spaz some boxing gloves.
        """
        self.node.boxingGloves = 1
        if self._demoMode: # preserve old behavior
            self._punchPowerScale = 1.7
            self._punchCooldown = 300
        else:
            factory = self.getFactory()
            self._punchPowerScale = factory.punchPowerScaleGloves
            self._punchCooldown = factory.punchCooldownGloves

    def superHealth(self, tgl):
        """
        category: BombDash Functions

        Give this spaz more health and invincible.
        """
        if tgl:
            def _safeSetAttr(node, attr, val):
                if node.exists():
                    setattr(node, attr, val)

            bs.gameTimer(
                1, bs.Call(_safeSetAttr, self.node, 'invincible', True))

            self.invincibilityTimer = bs.Timer(
                3000, bs.Call(_safeSetAttr, self.node, 'invincible', False))

            self.node.hurt = 0
            self._lastHitTime = None
            self._numTimesHit = 0
            if self.hitPoints < 2500:
                self.hitPoints = self.hitPoints + 1500
            else:
                self.hitPoints = 2500

            self.equipBoxingGloves()
        else:
            self.node.hurt = 0
            self._lastHitTime = None
            self._numTimesHit = 0
            self.hitPoints = self.hitPointsMax
            self._glovesWearOff()

    def equipShields(self, decay=False):
        """
        Give this spaz a nice energy shield.
        """

        if not self.node.exists():
            bs.printError('Can\'t equip shields; no node.')
            return

        factory = self.getFactory()
        if self.shield is None:
            self.shield = bs.newNode('shield', owner=self.node, attrs={
                'color': (random.random()*2,
                          random.random()*2,
                          random.random()*2),
                'radius': 1.3})

            self.node.connectAttr('positionCenter', self.shield, 'position')

        self.shieldHitPoints = self.shieldHitPointsMax = 650
        self.shieldDecayRate = factory.shieldDecayRate if decay else 0
        self.shield.hurt = 0
        bs.playSound(factory.shieldUpSound, 1.0, position=self.node.position)

        if self.shieldDecayRate > 0:
            self.shieldDecayTimer = bs.Timer(500, bs.WeakCall(self.shieldDecay),
                                             repeat=True)

            self.shield.alwaysShowHealthBar = True # so user can see the decay

    def shieldDecay(self):
        'Called repeatedly to decay shield HP over time.'
        if self.shield is not None and self.shield.exists():
            self.shieldHitPoints = \
                max(0, self.shieldHitPoints - self.shieldDecayRate)
            self.shield.hurt = \
                1.0 - float(self.shieldHitPoints)/self.shieldHitPointsMax
            if self.shieldHitPoints <= 0:
                self.shield.delete()
                self.shield = None
                self.shieldDecayTimer = None
                bs.playSound(self.getFactory().shieldDownSound,
                             1.0, position=self.node.position)
        else:
            self.shieldDecayTimer = None

    def handleMessage(self, m):
        self._handleMessageSanityCheck()

        if isinstance(m, bs.PickedUpMessage):
            self.node.handleMessage('hurtSound')
            self.node.handleMessage('pickedUp')
            # this counts as a hit
            self._numTimesHit += 1

        elif isinstance(m, bs.ShouldShatterMessage):
            # eww; seems we have to do this in a timer or it wont work right
            # (since we're getting called from within update() perhaps?..)
            bs.gameTimer(1, bs.WeakCall(self.shatter))

        elif isinstance(m, bs.ImpactDamageMessage):
            # eww; seems we have to do this in a timer or it wont work right
            # (since we're getting called from within update() perhaps?..)
            bs.gameTimer(1, bs.WeakCall(self._hitSelf, m.intensity))

        elif isinstance(m, bs.PowerupMessage):
            if self._dead: return True
            if self.pickUpPowerupCallback is not None:
                self.pickUpPowerupCallback(self)

            if m.powerupType == 'shockwave':
                if bs.getConfig().get('Powerup Popups', True):
                    bsUtils.PopupText((bs.Lstr(
                        resource='descriptionShockwave')),
                        color=(1, 1, 1),
                        scale=1,
                        position=self.node.position).autoRetain()

                self.bombType = 'shockWave'
                tex = self._getBombTypeTex()
                self._flashBillboard(tex)
                if self.powerupsExpire:
                    self.node.miniBillboard2Texture = tex
                    t = bs.getGameTime()
                    self.node.miniBillboard2StartTime = t
                    self.node.miniBillboard2EndTime = t+gPowerupWearOffTime-7000
                    self._bombWearOffFlashTimer = \
                        bs.Timer(gPowerupWearOffTime-2000-7000,
                                 bs.WeakCall(self._bombWearOffFlash))

                    self._bombWearOffTimer = \
                        bs.Timer(gPowerupWearOffTime-7000,
                                 bs.WeakCall(self._bombWearOff))

            elif m.powerupType == 'extraAccelerator':
                if bs.getConfig().get('Powerup Popups', True):
                    bsUtils.PopupText((bs.Lstr(
                        resource='descriptionExtraAccelerator')),
                        color=(1, 1, 1),
                        scale=1,
                        position=self.node.position).autoRetain()

                bdUtils.cCube(
                    position=(self.node.position[0],
                              self.node.position[1]+3,
                              self.node.position[2]),
                    companion=True if random.random() > 0.5 else False).autoRetain().node.velocity = (0, 5, 0)

            elif m.powerupType == 'speed':
                if bs.getConfig().get('Powerup Popups', True):
                    bsUtils.PopupText((bs.Lstr(
                        resource='descriptionSpeed')),
                        color=(1, 1, 1),
                        scale=1,
                        position=self.node.position).autoRetain()

                tex = bs.Powerup.getFactory().texSpeed
                self._flashBillboard(tex)
                def setSpeed(val):
                    if self.node.exists():
                        setattr(self.node, 'hockey', val)

                setSpeed(True)
                if self.powerupsExpire:
                    self.node.miniBillboard2Texture = tex
                    t = bs.getGameTime()
                    self.node.miniBillboard2StartTime = t
                    self.node.miniBillboard2EndTime = t+gPowerupWearOffTime
                    self._speedWearOffTimer = \
                        bs.Timer(gPowerupWearOffTime,
                                 bs.Call(setSpeed, False))

            elif m.powerupType == 'lego':
                if bs.getConfig().get('Powerup Popups', True):
                    bsUtils.PopupText((bs.Lstr(
                        resource='descriptionLego')),
                        color=(1, 1, 1),
                        scale=1,
                        position=self.node.position).autoRetain()

                for i in xrange(int(1+random.random()*6)):
                    bdUtils.Lego(
                        position=(self.node.position[0]+random.uniform(-1, 1),
                                  self.node.position[1]+3,
                                  self.node.position[2]+random.uniform(-1, 1)),
                        num=int(random.random()*3),
                        colorNum=int(random.random()*3)).autoRetain()

            elif m.powerupType == 'artillery':
                if bs.getConfig().get('Powerup Popups', True):
                    bsUtils.PopupText((bs.Lstr(
                        resource='descriptionArtillery')),
                        color=(1, 1, 1),
                        scale=1,
                        position=self.node.position).autoRetain()

                bdUtils.Artillery(
                    position=self.node.position,
                    owner=self.node,
                    sourcePlayer=self.getPlayer())

            elif m.powerupType == 'cannon':
                if bs.getConfig().get('Powerup Popups', True):
                    bsUtils.PopupText((bs.Lstr(
                        resource='descriptionCannon')),
                        color=(1, 1, 1),
                        scale=1,
                        position=self.node.position).autoRetain()

                bdUtils.Cannon(
                    position=(self.node.position[0],
                              self.node.position[1]+3,
                              self.node.position[2])).autoRetain()

            elif m.powerupType == 'highJump':
                if bs.getConfig().get('Powerup Popups', True):
                    bsUtils.PopupText((bs.Lstr(
                        resource='descriptionHighJump')),
                        color=(1, 1, 1),
                        scale=1,
                        position=self.node.position).autoRetain()

                def onJumpPressSpec():
                    if not self.node.exists(): return

                    t = bs.getGameTime()
                    if t - self.lastJumpTime >= self._jumpCooldown \
                            and not (self.node.knockout > 0.0 or self.node.frozen > 0):
                        self.node.jumpPressed = True
                        self.lastJumpTime = t
                        self._jumpCooldown = 750
                        self.node.handleMessage(
                            'impulse',
                            self.node.position[0],
                            self.node.position[1],
                            self.node.position[2],
                            0, 0, 0, 200, 200, 0, 0, 0, 1, 0)

                    self._turboFilterAddPress('jump')

                self.node.getDelegate().getPlayer().assignInputCall('jumpPress', onJumpPressSpec)

            elif m.powerupType == 'blessing':
                if bs.getConfig().get('Powerup Popups', True):
                    bsUtils.PopupText((bs.Lstr(
                        resource='descriptionBlessing')),
                        color=(1, 1, 1),
                        scale=1,
                        position=self.node.position).autoRetain()

                pixel = bs.Spaz(
                    character='Pixel',
                    color=(1.0, 1.0, 1.0),
                    highlight=(1.0, 1.0, 1.0)).autoRetain()

                pixel.node.handleMessage(
                    bs.StandMessage(
                        position=(self.node.position[0]-0.5,
                                  self.node.position[1]+3,
                                  self.node.position[2])))

                box = bs.SimpleBox(
                    position=pixel.node.position).autoRetain()

                box.node.model = None
                pixel.node.holdNode = box.node
                pixel.node.holdBody = 1
                box.node.extraAcceleration = (2, 40, 1)
                def setFly():   
                    box.node.extraAcceleration = (-2, 63, -1)


                def deletePixel():
                    if pixel.exists():
                        pixel.node.delete()
                        box.node.delete()

                def spawnSpell():
                    bdUtils.MagicSpell(
                        position=(pixel.node.position[0],
                                  pixel.node.position[1]+1,
                                  pixel.node.position[2])).autoRetain()
                    bs.emitBGDynamics(
                        position=(pixel.node.position[0],
                                  pixel.node.position[1]+0.5,
                                  pixel.node.position[2]),
                        count=10,
                        emitType='tendrils',
                        tendrilType='smoke')
                
                bs.gameTimer(850, spawnSpell)
                bs.gameTimer(1450, setFly)
                bs.gameTimer(2550, deletePixel)

            elif m.powerupType == 'landMines':
                if bs.getConfig().get('Powerup Popups', True):
                    bsUtils.PopupText((bs.Lstr(
                        resource='descriptionLandMines')),
                        color=(1, 1, 1),
                        scale=1,
                        position=self.node.position).autoRetain()

                self.setLandMineCount(min(self.landMineCount+3, 3))

            elif m.powerupType == 'airstrike':
                if bs.getConfig().get('Powerup Popups', True):
                    bsUtils.PopupText((bs.Lstr(
                        resource='descriptionAirstrike')),
                        color=(1, 1, 1),
                        scale=1,
                        position=self.node.position).autoRetain()

                self.setAirstrikeCount(self.airstrikeCount+1)

            elif m.powerupType == 'holyBomb':
                if bs.getConfig().get('Powerup Popups', True):
                    bsUtils.PopupText((bs.Lstr(
                        resource='descriptionHolyBomb')),
                        color=(1, 1, 1),
                        scale=1,
                        position=self.node.position).autoRetain()

                self.setHolyBombCount(self.holyBombCount+1)

            elif m.powerupType == 'elonMine':
                if bs.getConfig().get('Powerup Popups', True):
                    bsUtils.PopupText((bs.Lstr(
                        resource='descriptionElonMine')),
                        color=(1, 1, 1),
                        scale=1,
                        position=self.node.position).autoRetain()

                self.setElonMineCount(self.elonMineCount+1)

            elif m.powerupType == 'portalBomb':
                if bs.getConfig().get('Powerup Popups', True):
                    bsUtils.PopupText((bs.Lstr(
                        resource='descriptionPortalBomb')),
                        color=(1, 1, 1),
                        scale=1,
                        position=self.node.position).autoRetain()

                self.setPortalCount(self.portalCount+1)

            elif m.powerupType == 'stickyForce':
                if bs.getConfig().get('Powerup Popups', True):
                    bsUtils.PopupText((bs.Lstr(
                        resource='descriptionStickyForce')),
                        color=(1, 1, 1),
                        scale=1,
                        position=self.node.position).autoRetain()

                self.setForceBombCount(self.forceBombCount+2)

            elif m.powerupType == 'toxic':
                if bs.getConfig().get('Powerup Popups', True):
                    bsUtils.PopupText((bs.Lstr(
                        resource='descriptionToxic')),
                        color=(1, 1, 1),
                        scale=1,
                        position=self.node.position).autoRetain()

                self.settoxicCount(self.toxicCount+1)

            elif m.powerupType == 'slipper':
                if bs.getConfig().get('Powerup Popups', True):
                    bsUtils.PopupText((bs.Lstr(
                        resource='descriptionSlipper')),
                        color=(1, 1, 1),
                        scale=1,
                        position=self.node.position).autoRetain()

                self.setSlipperCount(self.slipperCount+1)

            elif m.powerupType == 'healthBomb':
                if bs.getConfig().get('Powerup Popups', True):
                    bsUtils.PopupText((bs.Lstr(
                        resource='descriptionHealthBomb')),
                        color=(1, 1, 1),
                        scale=1,
                        position=self.node.position).autoRetain()

                self.setHealthBombCount(self.healBombCount+1)

            elif m.powerupType == 'colorBomb':
                if bs.getConfig().get('Powerup Popups', True):
                    bsUtils.PopupText((bs.Lstr(
                        resource='descriptionColorBomb')),
                        color=(1, 1, 1),
                        scale=1,
                        position=self.node.position).autoRetain()

                self.setColorBombCount(self.colorBombCount+1)

            elif m.powerupType == 'banana':
                if bs.getConfig().get('Powerup Popups', True):
                    bsUtils.PopupText((bs.Lstr(
                        resource='descriptionBanana')),
                        color=(1, 1, 1),
                        scale=1,
                        position=self.node.position).autoRetain()

                self.setBananCount(self.bananCount+1)

            elif m.powerupType == 'poison':
                if bs.getConfig().get('Powerup Popups', True):
                    bsUtils.PopupText((bs.Lstr(
                        resource='descriptionPoison')),
                        color=(1, 1, 1),
                        scale=1,
                        position=self.node.position).autoRetain()

                self.setPoisonCount(self.poisonCount+1)

            elif m.powerupType == 'dirt':
                if bs.getConfig().get('Powerup Popups', True):
                    bsUtils.PopupText((bs.Lstr(
                        resource='descriptionDirt')),
                        color=(1, 1, 1),
                        scale=1,
                        position=self.node.position).autoRetain()

                self.setDirtCount(self.dirtCount+1)

            elif m.powerupType == 'petard':
                if bs.getConfig().get('Powerup Popups', True):
                    bsUtils.PopupText((bs.Lstr(
                        resource='descriptionPetard')),
                        color=(1, 1, 1),
                        scale=1,
                        position=self.node.position).autoRetain()

                self.setPetardCount(self.petardCount+1)

            elif m.powerupType == 'molotov':
                if bs.getConfig().get('Powerup Popups', True):
                    bsUtils.PopupText((bs.Lstr(
                        resource='descriptionMolotov')),
                        color=(1, 1, 1),
                        scale=1,
                        position=self.node.position).autoRetain()

                self.setMolotovCount(self.molotovCount+1)

            elif m.powerupType == 'luckyBlock':
                if bs.getConfig().get('Powerup Popups', True):
                    bsUtils.PopupText((bs.Lstr(
                        resource='descriptionLuckyBlock')),
                        color=(1, 1, 1),
                        scale=1,
                        position=self.node.position).autoRetain()

                event = random.randint(1, 27)
                #event = 18

                if event in [1, 2, 3]:
                    import bsPowerup
                    self.node.handleMessage(
                        bs.PowerupMessage(
                            powerupType=bsPowerup.PowerupFactory().getRandomPowerupType()))

                elif event == 4:
                    import bsPowerup
                    bs.shakeCamera(1)
                    bs.emitBGDynamics(
                        position=(self.node.position[0],
                                  self.node.position[1]+4,
                                  self.node.position[2]),
                        velocity=(0, 0, 0),
                        count=700,
                        spread=0.7,
                        chunkType='spark')

                    bs.Powerup(
                        position=(self.node.position[0],
                                  self.node.position[1]+4,
                                  self.node.position[2]),
                        powerupType=bsPowerup.PowerupFactory().getRandomPowerupType(),
                        expire=True).autoRetain()

                    bs.Powerup(
                        position=(self.node.position[0],
                                  self.node.position[1]+4,
                                  self.node.position[2]),
                        powerupType=bsPowerup.PowerupFactory().getRandomPowerupType(),
                        expire=True).autoRetain()

                    bs.Powerup(
                        position=(self.node.position[0],
                                  self.node.position[1]+4,
                                  self.node.position[2]),
                        powerupType=bsPowerup.PowerupFactory().getRandomPowerupType(),
                        expire=True).autoRetain()

                elif event == 5:
                    bs.emitBGDynamics(
                        position=self.node.position,
                        velocity=(0, 0, 0),
                        count=600,
                        spread=0.7,
                        chunkType=random.choice([
                            'ice',
                            'rock',
                            'metal',
                            'spark',
                            'splinter',
                            'slime']))

                    bs.shakeCamera(0.5)

                elif event == 6:
                    bigBomb = bs.Bomb(
                        position=(self.node.position[0],
                                  self.node.position[1]+3,
                                  self.node.position[2]),
                        sourcePlayer=self.sourcePlayer,
                        owner=self.node,
                        modelSize=3,
                        blastRadius=6)

                    def size():
                        bigBomb.node.modelScale = 3

                    bs.gameTimer(300, size)
                    def boom():
                        if bigBomb.node.exists():
                            pos = bigBomb.node.position
                            bs.Blast(
                                blastType='giant',
                                position=pos,
                                blastRadius=6)
                            bs.Blast(
                                blastType='normal',
                                position=pos,
                                blastRadius=10)

                    bs.gameTimer(2000, bs.Call(boom))

                elif event == 7:
                    self.node.handleMessage(bs.FreezeMessage())

                elif event == 8:
                    bs.Blast(
                        position=self.node.position,
                        velocity=self.node.velocity,
                        blastRadius=1.0,
                        blastType='normal',
                        sourcePlayer=None,
                        hitType='punch',
                        hitSubType='normal')

                elif event == 9:
                    self.setLandMineCount(
                      min(self.landMineCount+10, 10))

                elif event == 10:
                    bs.Blast(
                        position=self.node.position,
                        velocity=self.node.velocity,
                        blastRadius=1.0,
                        blastType='normal',
                        sourcePlayer=None,
                        hitType='punch',
                        hitSubType='normal')

                    self.node.handleMessage(bs.FreezeMessage())
                    bs.Blast(
                        position=self.node.position,
                        velocity=self.node.velocity,
                        blastRadius=1.0,
                        blastType='normal',
                        sourcePlayer=None,
                        hitType='punch',
                        hitSubType='normal')

                    self.node.handleMessage(bs.FreezeMessage())
                    bs.Blast(
                        position=self.node.position,
                        velocity=self.node.velocity,
                        blastRadius=1.0,
                        blastType='normal',
                        sourcePlayer=None,
                        hitType='punch',
                        hitSubType='normal')

                elif event == 11:
                    light = bs.newNode('light', attrs={
                        'position': self.node.position,
                        'color': (0.2 ,0.2, 0.4),
                        'volumeIntensityScale': 1.0,
                        'radius': 1})

                    bsUtils.animate(light, 'intensity', {
                        0: 1, 50: 10, 150: 5, 250: 0,
                        260: 10, 410: 5, 510: 1})

                    bs.playSound(bs.getSound('grom2'))
                    self.node.connectAttr('positionCenter', light, 'position')

                elif event == 12:
                    self.node.color = (random.random()*2,
                                       random.random()*2,
                                       random.random()*2)

                elif event == 13:
                    wwwx = self.node.position[0] - 2
                    while wwwx < self.node.position[0] + 2:
                        wwwy = self.node.position[2] - 2
                        while wwwy < self.node.position[2] + 2:
                            bs.Blast(
                                position=(wwwx, self.node.position[1], wwwy),
                                velocity=(self.node.velocity[0],
                                          self.node.velocity[1]+10,
                                          self.node.velocity[2]),
                                blastRadius=0.5,
                                blastType='normal',
                                sourcePlayer=None,
                                hitType='punch',
                                hitSubType='normal')

                            wwwy +=1

                        wwwx +=1

                elif event == 14:
                    bpos = -15
                    while bpos < 15:
                        bdUtils.BadRock(
                            position=(-10, 6, bpos),
                            velocity=(12+random.random()*8, -0.1, 0)).autoRetain()

                        bpos = bpos + 1.5

                elif event == 15:
                    bs.animateArray(self.node, 'color', 3, {
                        0: (0, 0, 1.3), 500: (0, 1.3, 0),
                        1000: (1, 0, 0), 1500: (0, 0, 1.3)},
                        True)

                    self.node.handleMessage('celebrate', 100000000)

                elif event == 16:
                    bdUtils.Turret(
                        position=(self.node.position[0],
                                  self.node.position[1]+3,
                                  self.node.position[2]),
                        different=(random.random()>0.9)).autoRetain()

                elif event == 17:
                    bdUtils.cCube(
                        position=(self.node.position[0]+1,
                                  self.node.position[1],
                                  self.node.position[2]),
                        companion=True if random.random() > 0.5 else False) \
                        .autoRetain().node.velocity = (0, 0, 0)

                    bdUtils.cCube(
                        position=(self.node.position[0]+1,
                                  self.node.position[1]+1,
                                  self.node.position[2]),
                        companion=True if random.random() > 0.5 else False) \
                        .autoRetain().node.velocity = (0, 0, 0)

                    bdUtils.cCube(
                        position=(self.node.position[0]+1,
                                  self.node.position[1]+2,
                                  self.node.position[2]),
                        companion=True if random.random() > 0.5 else False) \
                        .autoRetain().node.velocity = (0, 3, 0)

                elif event == 18:
                    h = bs.getModel(random.choice([
                        'penguinHead',
                        'santaHead',
                        'bunnyHead',
                        'aliHead',
                        'cyborgHead',
                        'neoSpazHead',
                        'jackHead',
                        'agentHead',
                        'zoeHead',
                        'ninjaHead',
                        'bearHead',
                        'bonesHead',
                        'pixieHead',
                        'wizardHead'
                        ]))

                    t = bs.getModel(random.choice([
                        'penguinTorso',
                        'santaTorso',
                        'bunnyTorso',
                        'aliTorso',
                        'cyborgTorso',
                        'neoSpazTorso',
                        'jackTorso',
                        'agentTorso',
                        'zoeTorso',
                        'ninjaTorso',
                        'bearTorso',
                        'bonesTorso',
                        'pixieTorso',
                        'wizardTorso'
                        ]))

                    h2 = bs.getModel(random.choice([
                        'penguinHand',
                        'santaHand',
                        'bunnyHand',
                        'aliHand',
                        'cyborgHand',
                        'neoSpazHand',
                        'jackHand',
                        'agentHand',
                        'zoeHand',
                        'ninjaHand',
                        'bearHand',
                        'bonesHand',
                        'pixieHand',
                        'wizardHand'
                        ]))

                    c = (random.random(),
                         random.random(),
                         random.random())

                    self.node.headModel = h
                    self.node.torsoModel = t
                    self.node.handModel = h2
                    self.node.color = c

                elif event == 19:
                    self.rainaman = random.randint(1, 2)
                    if self.rainaman == 1:
                        nowTintr = \
                            bs.getSharedObject('globals').vignetteOuter

                        self.lightningBolt()
                        bs.getSharedObject('globals').vignetteOuter = (0.8, 0.8, 0.8)
                        bs.playSound(
                            bs.getSound('grom'),
                            volume=10,
                            position=(0, 10, 0))

                        bs.playSound(
                            bs.getSound('groza'),
                            volume=10,
                            position=(0, 10, 0))

                        bs.gameTimer(13150, bs.WeakCall(self.lightningBolt))

                        bs.getActivity()._rain = \
                            bs.Timer(300, bs.WeakCall(self.dropB), repeat=True)

                        def endRain():
                            bs.getActivity()._rain = None
                            bsUtils.animateArray(
                                bs.getSharedObject('globals'), 'vignetteOuter', 3, {
                                    0: bs.getSharedObject('globals').vignetteOuter,
                                    2500: nowTintr})

                        bs.gameTimer(25000, bs.Call(endRain))

                    elif self.rainaman == 2:
                        nowTint = \
                            bs.getSharedObject('globals').vignetteOuter

                        bs.getActivity().mBotSet = bs.BotSet()
                        self.lightningBolt()
                        self.node.handleMessage('celebrate', 20000)
                        bs.getSharedObject('globals').vignetteOuter = (1, 1, 1)
                        bs.playSound(
                            bs.getSound('rainaman') if bs.getLanguage() == 'Russian' \
                                else bs.getSound('rainamanEng'),
                            volume=10,
                            position=(0, 10, 0))

                        bs.getActivity()._rainAMan = \
                            bs.Timer(800, bs.WeakCall(self.dropM), repeat=True)

                        def endRain():
                            bs.getActivity()._rainAMan = None
                            bsUtils.animateArray(bs.getSharedObject('globals'), 'vignetteOuter', 3, {
                                0: bs.getSharedObject('globals').vignetteOuter,
                                2500: nowTint})

                        bs.gameTimer(15000, bs.Call(endRain))

                    else:
                        nowTintp = \
                            bs.getSharedObject('globals').vignetteOuter

                        self.lightningBolt()
                        bs.getSharedObject('globals').vignetteOuter = (0.8, 0.8, 0.8)
                        bs.playSound(
                            bs.getSound('grom'),
                            volume=10,
                            position=(0, 10, 0))

                        bs.gameTimer(15150, bs.WeakCall(self.lightningBolt))
                        bs.getActivity()._rainPTimer = \
                            bs.Timer(400, bs.WeakCall(self.dropP), repeat=True)

                        def endRain():
                            bs.getActivity()._rainPTimer = None
                            bsUtils.animateArray(bs.getSharedObject('globals'), 'vignetteOuter', 3, {
                                0: bs.getSharedObject('globals').vignetteOuter,
                                2500: nowTintp})

                        bs.gameTimer(25000, bs.Call(endRain))

                elif event == 20:
                    a = 0
                    while a < 80:
                        bdUtils.Clay(
                            position=(self.node.position[0]+random.random(),
                                      self.node.position[1]+random.random(),
                                      self.node.position[2]+random.random()),
                            velocity=(-5+(random.random()*30),
                                      -5+(random.random()*30),
                                      5+(random.random()*30))).autoRetain()

                        a += 1

                elif event == 21:
                    for i in xrange(int(1+random.random()*10)):
                        bdUtils.Lego(
                            position=(self.node.position[0]+random.uniform(-1, 1),
                                      self.node.position[1]+3,
                                      self.node.position[2]+random.uniform(-1.2, 1.2)),
                            velocity=(-6+random.random()*12,
                                      -6+random.random()*12,
                                      -6+random.random()*12),
                            num=int(random.random()*3),
                            colorNum=int(random.random()*3)).autoRetain()

                elif event == 22:
                    bs.getActivity()._bomzhSet = bs.BotSet()
                    bs.getActivity()._bomzhSet.spawnBot(
                        BomzhBot,
                        pos=self.node.position,
                        spawnTime=1000)

                elif event == 23:
                    bsInternal._getForegroundHostSession().narkomode = True
                    op = 0.05
                    std = bs.getSharedObject('globals').vignetteOuter

                    bsUtils.animateArray(bs.getSharedObject('globals'), 'vignetteOuter', 3, {
                        0: bs.getSharedObject('globals').vignetteOuter,
                        17000: (0, 1, 0)})

                    try:
                        bs.getActivity().getMap().node.opacity = op
                    except:
                        pass

                    try:
                        bs.getActivity().getMap().bg.opacity = op
                    except:
                        pass

                    try:
                        bs.getActivity().getMap().bg.node.opacity = op
                    except:
                        pass

                    try:
                        bs.getActivity().getMap().node1.opacity = op
                    except:
                        pass

                    try:
                        bs.getActivity().getMap().node2.opacity = op
                    except:
                        pass

                    try:
                        bs.getActivity().getMap().node3.opacity = op
                    except:
                        pass

                    try:
                        bs.getActivity().getMap().steps.opacity = op
                    except:
                        pass

                    try:
                        bs.getActivity().getMap().floor.opacity = op
                    except:
                        pass

                    try:
                        bs.getActivity().getMap().center.opacity = op
                    except:
                        pass

                    try:
                        bs.getActivity().getMap().node4.opacity = op
                    except:
                        pass

                    def off():
                        bsInternal._getForegroundHostSession().narkomode = False
                        op = 1
                        try:
                            bs.getActivity().getMap().node.opacity = op
                        except:
                            pass

                        try:
                            bs.getActivity().getMap().bg.opacity = op
                        except:
                            pass

                        try:
                            bs.getActivity().getMap().bg.node.opacity = op
                        except:
                            pass

                        try:
                            bs.getActivity().getMap().node1.opacity = op
                        except:
                            pass

                        try:
                            bs.getActivity().getMap().node2.opacity = op
                        except:
                            pass

                        try:
                            bs.getActivity().getMap().node3.opacity = op
                        except:
                            pass

                        try:
                            bs.getActivity().getMap().node4.opacity = op
                        except:
                            pass

                        try:
                            bs.getActivity().getMap().steps.opacity = op
                        except:
                            pass

                        try:
                            bs.getActivity().getMap().floor.opacity = op
                        except:
                            pass

                        try:
                            bs.getActivity().getMap().center.opacity = op
                        except:
                            pass

                        bsUtils.animateArray(bs.getSharedObject('globals'), 'vignetteOuter', 3, {
                            0: bs.getSharedObject('globals').vignetteOuter,
                            100: std})

                    bs.gameTimer(17000, bs.Call(off))

                elif event == 24:
                    bs.playSound(bs.getSound('nukeAlarm'))

                    def nuke():
                        bdUtils.Nuke(
                            position=(self.node.position[0],
                                      10,
                                      self.node.position[2])).autoRetain()

                    bs.gameTimer(11500, bs.Call(nuke))

                elif event == 25:
                    self._punchPowerScale = 1.9
                    if self.node.style == 'penguin':
                        self.node.upperArmModel = bs.getModel('penguinShovel')
                    else:
                        self.node.handModel = bs.getModel('shovel')

                    self.shovel = True

                elif event == 26:
                    self.setPetardCount(self.petardCount+1)

                elif event == 27:
                    bdUtils.BlackHole(
                        position=self.node.position,
                        owner=self.node)

            elif m.powerupType == 'railgun':
                    if self.node.style == 'penguin':
                        self.node.upperArmModel = bs.getModel('penguinBeam')
                    else:
                        self.node.handModel = bs.getModel('beam')
                    self.RailgunFired = 0
                    self.Railgun = True
                    bs.playSound(self.getFactory().railgunChargeSound, position=self.node.position)
                    def waitForCharge():
                        self.node.getDelegate().getPlayer().assignInputCall('punchPress', bs.Call(self.railgunChecker))
                    bs.gameTimer(1000, bs.Call(waitForCharge))

            elif m.powerupType == 'impactBombs':
                if bs.getConfig().get('Powerup Popups', True):
                    bsUtils.PopupText((bs.Lstr(
                        resource='descriptionImpactBombs')),
                        color=(1, 1, 1),
                        scale=1,
                        position=self.node.position).autoRetain()

                self.bombType = 'impact'
                tex = self._getBombTypeTex()
                self._flashBillboard(tex)
                if self.powerupsExpire:
                    self.node.miniBillboard2Texture = tex
                    t = bs.getGameTime()
                    self.node.miniBillboard2StartTime = t
                    self.node.miniBillboard2EndTime = t+gPowerupWearOffTime
                    self._bombWearOffFlashTimer = \
                        bs.Timer( gPowerupWearOffTime-2000,
                                  bs.WeakCall(self._bombWearOffFlash))
                    self._bombWearOffTimer = \
                        bs.Timer(gPowerupWearOffTime,
                                 bs.WeakCall(self._bombWearOff))

            elif m.powerupType == 'stickyBombs':
                if bs.getConfig().get('Powerup Popups', True):
                    bsUtils.PopupText((bs.Lstr(
                        resource='descriptionStickyBombs')),
                        color=(1, 1, 1),
                        scale=1,
                        position=self.node.position).autoRetain()

                self.bombType = 'sticky'
                tex = self._getBombTypeTex()
                self._flashBillboard(tex)
                if self.powerupsExpire:
                    self.node.miniBillboard2Texture = tex
                    t = bs.getGameTime()
                    self.node.miniBillboard2StartTime = t
                    self.node.miniBillboard2EndTime = t+gPowerupWearOffTime
                    self._bombWearOffFlashTimer = \
                        bs.Timer(gPowerupWearOffTime-2000,
                                 bs.WeakCall(self._bombWearOffFlash))
                    self._bombWearOffTimer = \
                        bs.Timer(gPowerupWearOffTime,
                                 bs.WeakCall(self._bombWearOff))

            elif m.powerupType == 'punch':
                if bs.getConfig().get('Powerup Popups', True):
                    bsUtils.PopupText((bs.Lstr(
                        resource='descriptionPunch')),
                        color=(1, 1, 1),
                        scale=1,
                        position=self.node.position).autoRetain()

                self._hasBoxingGloves = True
                tex = bs.Powerup.getFactory().texPunch
                self._flashBillboard(tex)
                self.equipBoxingGloves()
                if self.powerupsExpire:
                    self.node.boxingGlovesFlashing = 0
                    self.node.miniBillboard3Texture = tex
                    t = bs.getGameTime()
                    self.node.miniBillboard3StartTime = t
                    self.node.miniBillboard3EndTime = t+gPowerupWearOffTime
                    self._boxingGlovesWearOffFlashTimer = \
                        bs.Timer(gPowerupWearOffTime-2000,
                                 bs.WeakCall(self._glovesWearOffFlash))
                    self._boxingGlovesWearOffTimer = \
                        bs.Timer(gPowerupWearOffTime,
                                 bs.WeakCall(self._glovesWearOff))

            elif m.powerupType == 'shield':
                if bs.getConfig().get('Powerup Popups', True):
                    bsUtils.PopupText((bs.Lstr(
                        resource='descriptionShield')),
                        color=(1, 1, 1),
                        scale=1,
                        position=self.node.position).autoRetain()

                factory = self.getFactory()
                # let's allow powerup-equipped shields to lose hp over time
                self.equipShields(
                    decay=True if factory.shieldDecayRate > 0 else False)

            elif m.powerupType == 'curse':
                if bs.getConfig().get('Powerup Popups', True):
                    bsUtils.PopupText((bs.Lstr(
                        resource='descriptionCurse')),
                        color=(1, 1, 1),
                        scale=1,
                        position=self.node.position).autoRetain()

                self.curse()

            elif (m.powerupType == 'tripleBombs'):
                if bs.getConfig().get('Powerup Popups', True):
                    bsUtils.PopupText((bs.Lstr(
                        resource='descriptionTripleBombs')),
                        color=(1, 1, 1),
                        scale=1,
                        position=self.node.position).autoRetain()

                tex = bs.Powerup.getFactory().texBomb
                self._flashBillboard(tex)
                self.setBombCount(3)
                if self.powerupsExpire:
                    self.node.miniBillboard1Texture = tex
                    t = bs.getGameTime()
                    self.node.miniBillboard1StartTime = t
                    self.node.miniBillboard1EndTime = t+gPowerupWearOffTime
                    self._multiBombWearOffFlashTimer = \
                        bs.Timer(gPowerupWearOffTime-2000,
                                 bs.WeakCall(self._multiBombWearOffFlash))
                    self._multiBombWearOffTimer = \
                        bs.Timer(gPowerupWearOffTime,
                                 bs.WeakCall(self._multiBombWearOff))

            elif (m.powerupType == 'iceBombs'):
                if bs.getConfig().get('Powerup Popups', True):
                    bsUtils.PopupText((bs.Lstr(
                        resource='descriptionIceBombs')),
                        color=(1, 1, 1),
                        scale=1,
                        position=self.node.position).autoRetain()

                self.bombType = 'ice'
                tex = self._getBombTypeTex()
                self._flashBillboard(tex)
                if self.powerupsExpire:
                    self.node.miniBillboard2Texture = tex
                    t = bs.getGameTime()
                    self.node.miniBillboard2StartTime = t
                    self.node.miniBillboard2EndTime = t+gPowerupWearOffTime
                    self._bombWearOffFlashTimer = \
                        bs.Timer(gPowerupWearOffTime-2000,
                                 bs.WeakCall(self._bombWearOffFlash))
                    self._bombWearOffTimer = \
                        bs.Timer(gPowerupWearOffTime,
                                 bs.WeakCall(self._bombWearOff))

            elif (m.powerupType == 'health'):
                if bs.getConfig().get('Powerup Popups', True):
                    bsUtils.PopupText((bs.Lstr(
                        resource='descriptionHealth')),
                        color=(1, 1, 1),
                        scale=1,
                        position=self.node.position).autoRetain()

                if self._cursed:
                    self._cursed = False
                    # remove cursed material
                    factory = self.getFactory()
                    for attr in ['materials', 'rollerMaterials']:
                        materials = getattr(self.node, attr)
                        if factory.curseMaterial in materials:
                            setattr(self.node, attr,
                                    tuple(m for m in materials
                                          if m != factory.curseMaterial))
                    self.node.curseDeathTime = 0
                self.hitPoints = self.hitPointsMax
                self._flashBillboard(bs.Powerup.getFactory().texHealth)
                self.node.hurt = 0
                self._lastHitTime = None
                self._numTimesHit = 0

            self.node.handleMessage('flash')
            if m.sourceNode.exists():
                m.sourceNode.handleMessage(bs.PowerupAcceptMessage())

            return True

        elif isinstance(m, bs.FreezeMessage):
            if not self.node.exists(): return
            if self.node.invincible == True:
                bs.playSound(self.getFactory().blockSound, 1.0,
                             position=self.node.position)
                return
            if self.shield is not None: return
            if not self.frozen:
                self.frozen = True
                self.node.frozen = 1
                bs.gameTimer(5000, bs.WeakCall(self.handleMessage,
                                               bs.ThawMessage()))
                # instantly shatter if we're already dead
                # (otherwise its hard to tell we're dead)
                if self.hitPoints <= 0:
                    self.shatter()

        elif isinstance(m, bs.ThawMessage):
            if self.frozen and not self.shattered and self.node.exists():
                self.frozen = False
                self.node.frozen = 0

        elif isinstance(m, bs.HitMessage):
            if not self.node.exists(): return
            if self.node.invincible == True:
                bs.playSound(self.getFactory().blockSound,
                             1.0, position=self.node.position)
                return True

            if m.srcNode is not None and m.srcNode.exists() \
                    and m.srcNode.getNodeType() == 'spaz':
                d = m.srcNode.getDelegate()
                s = m.srcNode
                try:
                    if m.srcNode is not None and m.srcNode.exists():
                        if m.srcNode.getDelegate().shovel:
                            d = m.srcNode.getDelegate()
                            s = m.srcNode
                            if self.shovels == 0:
                                self.shovels+=1
                                bs.screenMessage(bs.Lstr(
                                    resource='shovelMsg',
                                    subs=[('${PLAYER}', self.getPlayer().getName().encode('utf-8'))]),
                                    color=(0.65, 0.83, 0.5))

                                s.upperArmModel = self.getFactory()._getMedia(
                                    self.character)['upperArmModel'] if not s.style == 'penguin' \
                                        else bs.getModel('penguinUpperArm')

                                s.handModel = self.getFactory()._getMedia(
                                    self.character)['handModel'] if not s.style == 'penguin' else None

                                d.shovel = False
                                d._punchPowerScale = gBasePunchPowerScale
                                bs.playSound(bs.getSound('shovel'))
                            else:
                                bs.screenMessage(bs.Lstr(
                                    resource='shovelMsg2',
                                    subs=[('${PLAYER}', self.getPlayer().getName().encode('utf-8'))]),
                                    color=(0.65, 0.83, 0.5))

                                s.upperArmModel = self.getFactory()._getMedia(
                                    self.character)['upperArmModel']

                                s.handModel = self.getFactory()._getMedia(
                                    self.character)['handModel']

                                d.curse()
                                d.shovel = False
                                d._punchPowerScale = gBasePunchPowerScale
                                bs.playSound(bs.getSound('shovel'))

                except:
                    s.upperArmModel = self.getFactory()._getMedia(
                        self.character)['upperArmModel']

                    s.handModel = self.getFactory()._getMedia(
                        self.character)['handModel']

                    d.shovel = False
                    d._punchPowerScale = gBasePunchPowerScale
                    bs.playSound(bs.getSound('shovel'))

            # if we were recently hit, don't count this as another
            # (so punch flurries and bomb pileups essentially count as 1 hit)
            gameTime = bs.getGameTime()
            if self._lastHitTime is None or gameTime-self._lastHitTime > 1000:
                self._numTimesHit += 1
                self._lastHitTime = gameTime

            mag = m.magnitude * self._impactScale
            velocityMag = m.velocityMagnitude * self._impactScale

            damageScale = 0.22

            # if they've got a shield, deliver it to that instead..
            if self.shield is not None:

                if m.flatDamage: damage = m.flatDamage * self._impactScale
                else:
                    # hit our spaz with an impulse but tell it to only return
                    # theoretical damage; not apply the impulse..
                    self.node.handleMessage(
                        "impulse", m.pos[0], m.pos[1], m.pos[2],
                        m.velocity[0], m.velocity[1], m.velocity[2],
                        mag , velocityMag, m.radius, 1,
                        m.forceDirection[0], m.forceDirection[1],
                        m.forceDirection[2])
                    damage = damageScale * self.node.damage

                self.shieldHitPoints -= damage

                self.shield.hurt = (1.0 - float(self.shieldHitPoints)
                                    /self.shieldHitPointsMax)
                # its a cleaner event if a hit just kills the shield
                # without damaging the player..
                # however, massive damage events should still be able to
                # damage the player.. this hopefully gives us a happy medium.
                maxSpillover = self.getFactory().maxShieldSpilloverDamage
                if self.shieldHitPoints <= 0:
                    # fixme - transition out perhaps?..
                    self.shield.delete()
                    self.shield = None
                    bs.playSound(self.getFactory().shieldDownSound, 1.0,
                                 position=self.node.position)
                    # emit some cool lookin sparks when the shield dies
                    t = self.node.position
                    bs.emitBGDynamics(position=(t[0], t[1]+0.9, t[2]),
                                      velocity=self.node.velocity,
                                      count=random.randrange(20, 30), scale=1.0,
                                      spread=0.6, chunkType='spark')

                else:
                    bs.playSound(self.getFactory().shieldHitSound, 0.5,
                                 position=self.node.position)

                # emit some cool lookin sparks on shield hit
                bs.emitBGDynamics(position=m.pos,
                                  velocity=(m.forceDirection[0]*1.0,
                                            m.forceDirection[1]*1.0,
                                            m.forceDirection[2]*1.0),
                                  count=min(30, 5+int(damage*0.005)),
                                  scale=0.5, spread=0.3, chunkType='spark')

                # if they passed our spillover threshold,
                # pass damage along to spaz
                if self.shieldHitPoints <= -maxSpillover:
                    leftoverDamage = -maxSpillover-self.shieldHitPoints
                    shieldLeftoverRatio = leftoverDamage/damage

                    # scale down the magnitudes applied to spaz accordingly..
                    mag *= shieldLeftoverRatio
                    velocityMag *= shieldLeftoverRatio
                else:
                    return True # good job shield!
            else: shieldLeftoverRatio = 1.0

            if m.flatDamage:
                damage = (m.flatDamage * self._impactScale
                          * shieldLeftoverRatio)
            else:
                # hit it with an impulse and get the resulting damage
                self.node.handleMessage(
                    "impulse", m.pos[0], m.pos[1], m.pos[2],
                    m.velocity[0], m.velocity[1], m.velocity[2],
                    mag, velocityMag, m.radius, 0,
                    m.forceDirection[0], m.forceDirection[1],
                    m.forceDirection[2])

                damage = damageScale * self.node.damage
            self.node.handleMessage("hurtSound")

            # play punch impact sound based on damage if it was a punch
            if m.hitType == 'punch':
                self.onPunched(damage)

                if damage > 999:
                    bs.addStats('Fatality hits')
                    bsUtils.PopupText(
                        'FATALITY!!!',
                        color=(1, 0,0 ),
                        scale=1.6,
                        position=self.node.position).autoRetain()

                    self.lightningBolt(
                        position=self.node.position,
                        radius=3)

                    if bs.getSharedObject('globals').slowMotion == False:
                        bs.getSharedObject('globals').slowMotion = True
                        def offSlowMo():
                            bs.getSharedObject('globals').slowMotion = False

                        bs.gameTimer(500, offSlowMo)

                    bs.emitBGDynamics(
                        position=m.pos,
                        chunkType='spark',
                        velocity=(m.forceDirection[0]*1.3,
                                  m.forceDirection[1]*1.3+5.0,
                                  m.forceDirection[2]*1.3),
                        count=45,
                        scale=1.0,
                        spread=1.0)

                elif damage > 800 and damage < 999:
                    bsUtils.PopupText(
                        'CRAZY!',
                        color=(0, 1, 0.3),
                        scale=1.6,
                        position=self.node.position).autoRetain()

                elif damage > 730 and damage < 800:
                    bsUtils.PopupText(
                        'AGRESSIVE!',
                        color=(1, 0, 0),
                        scale=1.6,
                        position=self.node.position).autoRetain()

                # if damage was significant, lets show it
                if damage > 350:
                    bsUtils.showDamageCount('-' + str(int(damage/10)) + "%",
                                            m.pos, m.forceDirection)

                # lets always add in a super-punch sound with boxing
                # gloves just to differentiate them
                if m.hitSubType == 'superPunch':
                    bs.playSound(self.getFactory().punchSoundStronger, 1.0,
                                 position=self.node.position)
                if damage > 500:
                    sounds = self.getFactory().punchSoundsStrong
                    sound = sounds[random.randrange(len(sounds))]
                else: sound = self.getFactory().punchSound
                bs.playSound(sound, 1.0, position=self.node.position)

                # throw up some chunks
                bs.emitBGDynamics(position=m.pos,
                                  velocity=(m.forceDirection[0]*0.5,
                                            m.forceDirection[1]*0.5,
                                            m.forceDirection[2]*0.5),
                                  count=min(10, 1+int(damage*0.0025)),
                                  scale=0.3, spread=0.03);

                bs.emitBGDynamics(position=m.pos,
                                  chunkType='sweat',
                                  velocity=(m.forceDirection[0]*1.3,
                                            m.forceDirection[1]*1.3+5.0,
                                            m.forceDirection[2]*1.3),
                                  count=min(30, 1+int(damage*0.04)),
                                  scale=0.9,
                                  spread=0.28);
                # momentary flash
                hurtiness = damage*0.003
                punchPos = (m.pos[0]+m.forceDirection[0]*0.02,
                            m.pos[1]+m.forceDirection[1]*0.02,
                            m.pos[2]+m.forceDirection[2]*0.02)
                flashColor = (1.0, 0.8, 0.4)
                light = bs.newNode("light",
                                   attrs={'position':punchPos,
                                          'radius':0.12+hurtiness*0.12,
                                          'intensity':0.3*(1.0+1.0*hurtiness),
                                          'heightAttenuated':False,
                                          'color':flashColor})
                bs.gameTimer(60, light.delete)


                flash = bs.newNode("flash",
                                   attrs={'position':punchPos,
                                          'size':0.17+0.17*hurtiness,
                                          'color':flashColor})
                bs.gameTimer(60, flash.delete)

            if m.hitType == 'impact':
                bs.emitBGDynamics(position=m.pos,
                                  velocity=(m.forceDirection[0]*2.0,
                                            m.forceDirection[1]*2.0,
                                            m.forceDirection[2]*2.0),
                                  count=min(10, 1+int(damage*0.01)),
                                  scale=0.4, spread=0.1);
            if self.hitPoints > 0:
                # its kinda crappy to die from impacts, so lets reduce
                # impact damage by a reasonable amount if it'll keep us alive
                if m.hitType == 'impact' and damage > self.hitPoints:
                    # drop damage to whatever puts us at 10 hit points,
                    # or 200 less than it used to be whichever is greater
                    # (so it *can* still kill us if its high enough)
                    newDamage = max(damage-200, self.hitPoints-10)
                    damage = newDamage
                self.node.handleMessage("flash")
                # if we're holding something, drop it
                if damage > 0.0 and self.node.holdNode.exists():
                    self.node.holdNode = bs.Node(None)
                self.hitPoints -= damage
                self.node.hurt = 1.0 - float(self.hitPoints)/self.hitPointsMax
                # if we're cursed, *any* damage blows us up
                if self._cursed and damage > 0:
                    bs.gameTimer(50, bs.WeakCall(self.curseExplode,
                                                 m.sourcePlayer))
                # if we're frozen, shatter.. otherwise die if we hit zero
                if self.frozen and (damage > 200 or self.hitPoints <= 0):
                    self.shatter()
                elif self.hitPoints <= 0:
                    self.node.handleMessage(bs.DieMessage(how='impact'))

            # if we're dead, take a look at the smoothed damage val
            # (which gives us a smoothed average of recent damage) and shatter
            # us if its grown high enough
            if self.hitPoints <= 0:
                damageAvg = self.node.damageSmoothed * damageScale
                if damageAvg > 1000:
                    self.shatter()

        elif isinstance(m, _BombDiedMessage):
            self.bombCount += 1

        elif isinstance(m, _RailgunFiredMessage):
            if m.srcNode is not None and m.srcNode.exists() \
                    and m.srcNode.getNodeType() == 'spaz':
                d = m.srcNode.getDelegate()
                s = m.srcNode

                try:
                    if m.srcNode is not None and m.srcNode.exists():
                        if m.srcNode.getDelegate().Railgun:
                            d = m.srcNode.getDelegate()
                            s = m.srcNode
                            if self.RailgunFired == 2:
                                if not s.style == 'penguin':
                                    s.upperArmModel = self.getFactory(
                                        )._getMedia(
                                            self.character)['upperArmModel']

                                    s.handModel = self.getFactory()._getMedia(
                                        self.character)['handModel']
                                else:
                                    s.upperArmModel = \
                                        bs.getModel('penguinUpperArm')

                                    s.handModel =  None

                                d.Railgun = False

                except:
                    if self.RailgunFired == 2:
                        if not s.style == 'penguin':
                            s.upperArmModel = self.getFactory()._getMedia(
                                self.character)['upperArmModel']

                            s.handModel = self.getFactory()._getMedia(
                                self.character)['handModel']
                        else:
                            s.upperArmModel = bs.getModel('penguinUpperArm')

                            s.handModel =  None

                        d.Railgun = False

        elif isinstance(m, bs.DieMessage):
            wasDead = self._dead
            self._dead = True
            self.hitPoints = 0
            if m.immediate:
                self.node.delete()
            elif self.node.exists():
                self.node.hurt = 1.0
                if self.playBigDeathSound and not wasDead:
                    bs.playSound(self.getFactory().singlePlayerDeathSound)
                self.node.dead = True
                bs.gameTimer(2000, self.node.delete)

        elif isinstance(m, bs.OutOfBoundsMessage):
            # by default we just die here
            self.handleMessage(bs.DieMessage(how='fall'))
        elif isinstance(m, bs.StandMessage):
            self._lastStandPos = (m.position[0], m.position[1],
                                  m.position[2])
            self.node.handleMessage("stand", m.position[0], m.position[1],
                                    m.position[2], m.angle)
        elif isinstance(m, _CurseExplodeMessage):
            self.curseExplode()
        elif isinstance(m, _PunchHitMessage):
            node = bs.getCollisionInfo("opposingNode")

            # only allow one hit per node per punch
            if (node is not None and node.exists()
                and not node in self._punchedNodes):

                punchMomentumAngular = (self.node.punchMomentumAngular
                                        * self._punchPowerScale)
                punchPower = self.node.punchPower * self._punchPowerScale

                # ok here's the deal:  we pass along our base velocity for use
                # in the impulse damage calculations since that is a more
                # predictable value than our fist velocity, which is rather
                # erratic. ...however we want to actually apply force in the
                # direction our fist is moving so it looks better.. so we still
                # pass that along as a direction ..perhaps a time-averaged
                # fist-velocity would work too?.. should try that.

                # if its something besides another spaz, just do a muffled punch
                # sound
                if node.getNodeType() != 'spaz':
                    sounds = self.getFactory().impactSoundsMedium
                    sound = sounds[random.randrange(len(sounds))]
                    bs.playSound(sound, 1.0, position=self.node.position)

                t = self.node.punchPosition
                punchDir = self.node.punchVelocity
                v = self.node.punchMomentumLinear

                self._punchedNodes.add(node)
                node.handleMessage(
                    bs.HitMessage(
                        pos=t,
                        velocity=v,
                        magnitude=punchPower*punchMomentumAngular*110.0,
                        velocityMagnitude=punchPower*40,
                        radius=0,
                        srcNode=self.node,
                        sourcePlayer=self.sourcePlayer,
                        forceDirection = punchDir,
                        hitType='punch',
                        hitSubType=('superPunch' if self._hasBoxingGloves
                                    else 'default')))

                # also apply opposite to ourself for the first punch only
                # ..this is given as a constant force so that it is more
                # noticable for slower punches where it matters.. for fast
                # awesome looking punches its ok if we punch 'through'
                # the target
                mag = -400.0
                if self._hockey: mag *= 0.5
                if len(self._punchedNodes) == 1:
                    self.node.handleMessage("kickBack", t[0], t[1], t[2],
                                            punchDir[0], punchDir[1],
                                            punchDir[2], mag)

        elif isinstance(m, _PickupMessage):
            opposingNode, opposingBody = bs.getCollisionInfo('opposingNode',
                                                            'opposingBody')

            if opposingNode is None or not opposingNode.exists(): return True

            # dont allow picking up of invincible dudes
            try:
                if opposingNode.invincible == True: return True
            except Exception: pass

            # if we're grabbing the pelvis of a non-shattered spaz, we wanna
            # grab the torso instead
            if (opposingNode.getNodeType() == 'spaz'
                and not opposingNode.shattered and opposingBody == 4):
                opposingBody = 1

            # special case - if we're holding a flag, dont replace it
            # ( hmm - should make this customizable or more low level )
            held = self.node.holdNode
            if (held is not None and held.exists()
                and held.getNodeType() == 'flag'): return True
            self.node.holdBody = opposingBody # needs to be set before holdNode
            self.node.holdNode = opposingNode
        else:
            bs.Actor.handleMessage(self, m)

    def theCakeIsALie(self):
        pos = (0, 7, -3.550)
        cake = bdUtils.Cake(
            position=pos).autoRetain()

        light = bs.newNode('light', attrs={
            'position': (0, 6, 0),
            'color': (0.2, 0.2, 0.4),
            'volumeIntensityScale': 1.0,
            'radius': 3,
            'intensity': 10})

        if cake.exists() == False:
            light.delete()
        else:
            cake.node.connectAttr('position',light,'position')

        bsUtils.animate(light, 'intensity', {0: 10, 5000: 1})

    def dropM(self):
        bs.getActivity().mBotSet.spawnBot(
            bs.ToughGuyBotLame,
            pos=(-7.3+15.3*random.random(),
                 8,
                 (random.random()*14)-7),
            spawnTime=0)

    def dropB(self):
        pos = (-7.3+15.3*random.random(),
               6,
               -5.5+2.1*random.random())

        vel = ((-5.0+random.random()*30.0)*(-1.0 if pos[0] > 0 else 1.0),
                -4.0,random.uniform(-20, 20))

        bs.Bomb(
            position=pos,
            velocity=vel,
            bombType='impact').autoRetain()

    def dropP(self):
        import bsPowerup
        pos = (-7.3+15.3*random.random(),
               6,
               -5.5+(14*random.random()))

        bs.Powerup(
            position=pos,
            powerupType=bsPowerup.PowerupFactory().getRandomPowerupType()).autoRetain()

    def lightningBolt(self, position=(0, 10, 0), radius=10):
        bs.shakeCamera(4)
        if bs.getActivity().stdTint is None:
            bs.getActivity().stdTint = bs.getSharedObject('globals').vignetteOuter
            vignetteOuter = bs.getSharedObject('globals').vignetteOuter
        else:
            vignetteOuter = bs.getActivity().stdTint

        light = bs.newNode('light', attrs={
            'position': position,
            'color': (0.4, 0.4, 0.8),
            'volumeIntensityScale': 1.0,
            'radius': radius})

        bs.animate(light, 'intensity', {
            0: 1, 50: radius, 150: radius/2,
            250: 0, 260: radius, 410: radius/2,
            510: 0})

        bs.animateArray(bs.getSharedObject('globals'), 'vignetteOuter', 3, {
            0: vignetteOuter, 200: (0.2, 0.2, 0.2), 510: vignetteOuter})

        bs.playSound(
            bs.getSound('grom'),
            volume=10,
            position=(0, 10, 0))

    def colorGen(self):
        if self.node.exists():
            self.node.color = (random.random(),
                               random.random(),
                               random.random())

    def railgunChecker(self):
        if self.Railgun == True and not self.RailgunFired == 2:
            if self.node is not None and self.node.exists():
                if self.node.getNodeType() == 'spaz':
                    p1 = self.node.positionCenter
                    p2 = self.node.positionForward

                direction = [p1[0]-p2[0], p2[1]-p1[1], p1[2]-p2[2]]
                direction[1] = 0.0
                mag = 10.0 / bsVector.Vector(*direction).length()
                self.vel = [v*mag for v in direction]

                b = bs.RailBullet(
                    position=(self.node.position[0],
                              self.node.position[1]+0.4,
                              self.node.position[2]),
                    velocity=(self.vel[0],0,self.vel[2])).autoRetain()

                b.node.modelScale = 0.05
                b.node.extraAcceleration = (self.vel[0]*900, -1000, self.vel[2]*900)

                self.node.handleMessage(
                    'kickBack', self.node.position[0], self.node.position[1],
                    self.node.position[2], -(self.vel[0])*2, self.vel[1]*1,
                    -(self.vel[2]*2), mag*20)

                bs.playSound(self.getFactory().railgunSound, position=self.node.position)
                self.RailgunFired+=1
                self.handleMessage(_RailgunFiredMessage(srcNode=self.node))


    def soulExtractor(self):
        if self.node.exists():
            bs.emitBGDynamics(
                position=self.node.position,
                velocity=(0, 18, 0),
                count=100,
                spread=0.1,
                scale=0.6,
                chunkType='spark')

            self.node.color = (self.node.color[0]-0.005,
                               self.node.color[1]-0.005,
                               self.node.color[2]-0.005)

            if self.node.color < (0, 0, 0):
                self.curse()
        else:
            self._soulSucker = None

    def dropBomb(self):
        """
        Tell the spaz to drop one of his bombs, and returns
        the resulting bomb object.
        If the spaz has no bombs or is otherwise unable to
        drop a bomb, returns None.
        """

        if (self.landMineCount <= 0 and self.bombCount <= 0) or self.frozen:
            return
        p = self.node.positionForward
        v = self.node.velocity

        if self.landMineCount > 0:
            droppingBomb = False
            self.setLandMineCount(self.landMineCount-1)
            bombType = 'landMine'
        elif self.forceBombCount > 0:
            droppingBomb = False
            self.setForceBombCount(self.forceBombCount-1)
            bombType = 'forceBomb'
        elif self.toxicCount > 0:
            droppingBomb = False
            self.settoxicCount(self.toxicCount-1)
            bombType = 'toxic'
        elif self.poisonCount > 0:
            droppingBomb = False
            self.setPoisonCount(self.poisonCount-1)
            bombType = 'poison'
        elif self.slipperCount > 0:
            droppingBomb = False
            self.setSlipperCount(self.slipperCount-1)
            bombType = 'slipper'
        elif self.healBombCount > 0:
            droppingBomb = False
            self.setHealthBombCount(self.healBombCount-1)
            bombType = 'heal'
        elif self.colorBombCount > 0:
            droppingBomb = False
            self.setColorBombCount(self.colorBombCount-1)
            bombType = 'colorBomb'
        elif self.dirtCount > 0:
            droppingBomb = False
            self.setDirtCount(self.dirtCount-1)
            bombType = 'dirtBomb'
        elif self.bananCount > 0:
            droppingBomb = False
            self.setBananCount(self.bananCount-1)
            bombType = 'banana'
        elif self.petardCount > 0:
            droppingBomb = False
            self.setPetardCount(self.petardCount-1)
            bombType = 'petard'
        elif self.molotovCount > 0:
            droppingBomb = False
            self.setMolotovCount(self.molotovCount-1)
            bombType = 'fireBottle'
        elif self.airstrikeCount > 0:
            droppingBomb = False
            self.setAirstrikeCount(self.airstrikeCount-1)
            bombType = 'airstrike'
        elif self.elonMineCount > 0:
            droppingBomb = False
            self.setElonMineCount(self.elonMineCount-1)
            bombType = 'elonMine'
        elif self.holyBombCount > 0:
            droppingBomb = False
            self.setHolyBombCount(self.holyBombCount-1)
            bombType = 'holy'
        elif self.portalCount > 0:
            droppingBomb = False
            self.setPortalCount(self.portalCount-1)
            bombType = 'portal'
        else:
            droppingBomb = True
            bombType = self.bombType

        bomb = bs.Bomb(position=(p[0], p[1] - 0.0, p[2]),
                       velocity=(v[0], v[1], v[2]),
                       bombType=bombType,
                       blastRadius=self.blastRadius,
                       sourcePlayer=self.sourcePlayer,
                       owner=self.node).autoRetain()

        if droppingBomb:
            self.bombCount -= 1
            bomb.node.addDeathAction(bs.WeakCall(self.handleMessage,
                                                 _BombDiedMessage()))
        self._pickUp(bomb.node)

        for c in self._droppedBombCallbacks: c(self, bomb)

        if self.character == 'Bombman' \
                and self.bombType == 'normal' \
                and bombType == 'normal' \
                and bomb is not None \
                and bomb.exists():
            self.node.headModel = None

        return bomb

    def _pickUp(self, node):
        if self.node.exists() and node.exists():
            self.node.holdBody = 0 # needs to be set before holdNode
            self.node.holdNode = node

    def setLandMineCount(self, count):
        """
        Set the number of land-mines this spaz is carrying.
        """
        self.landMineCount = count
        if self.node.exists():
            if self.landMineCount != 0:
                self.node.counterText = 'x' + str(self.landMineCount)
                self.node.counterTexture = bs.Powerup.getFactory().texLandMines
            else:
                self.node.counterText = ''

    def settoxicCount(self, count):
        self.toxicCount = count
        if self.node.exists():
            if self.toxicCount != 0:
                self.node.counterText = 'x' + str(self.toxicCount)
                self.node.counterTexture = bs.Powerup.getFactory().textoxic
            else:
                self.node.counterText = ''

    def setPetardCount(self, count):
        self.petardCount = count
        if self.node.exists():
            if self.petardCount != 0:
                self.node.counterText = 'x' + str(self.petardCount)
                self.node.counterTexture = bs.Powerup.getFactory().texPetard
            else:
                self.node.counterText = ''

    def setMolotovCount(self, count):
        self.molotovCount = count
        if self.node.exists():
            if self.molotovCount != 0:
                self.node.counterText = 'x' + str(self.molotovCount)
                self.node.counterTexture = bs.Powerup.getFactory().texMolotov
            else:
                self.node.counterText = ''

    def setBananCount(self, count):
        self.bananCount = count
        if self.node.exists():
            if self.bananCount != 0:
                self.node.counterText = 'x' + str(self.bananCount)
                self.node.counterTexture = bs.Powerup.getFactory().texBanana
            else:
                self.node.counterText = ''

    def setDirtCount(self, count):
        self.dirtCount = count
        if self.node.exists():
            if self.dirtCount != 0:
                self.node.counterText = 'x' + str(self.dirtCount)
                self.node.counterTexture = bs.Powerup.getFactory().texDirt
            else:
                self.node.counterText = ''

    def setSlipperCount(self, count):
        self.slipperCount = count
        if self.node.exists():
            if self.slipperCount != 0:
                self.node.counterText = 'x' + str(self.slipperCount)
                self.node.counterTexture = bs.Powerup.getFactory().texSlipper
            else:
                self.node.counterText = ''

    def setHealthBombCount(self, count):
        self.healBombCount = count
        if self.node.exists():
            if self.healBombCount != 0:
                self.node.counterText = 'x' + str(self.healBombCount)
                self.node.counterTexture = bs.Powerup.getFactory().texHealthBomb
            else:
                self.node.counterText = ''

    def setColorBombCount(self, count):
        self.colorBombCount = count
        if self.node.exists():
            if self.colorBombCount != 0:
                self.node.counterText = 'x' + str(self.colorBombCount)
                self.node.counterTexture = bs.Powerup.getFactory().texColorBomb
            else:
                self.node.counterText = ''

    def setPoisonCount(self, count):
        self.poisonCount = count
        if self.node.exists():
            if self.poisonCount != 0:
                self.node.counterText = 'x' + str(self.poisonCount)
                self.node.counterTexture = bs.Powerup.getFactory().texPoison
            else:
                self.node.counterText = ''

    def setForceBombCount(self, count):
        self.forceBombCount = count
        if self.node.exists():
            if self.forceBombCount != 0:
                self.node.counterText = 'x' + str(self.forceBombCount)
                self.node.counterTexture = bs.Powerup.getFactory().texStickyForce
            else:
                self.node.counterText = ''

    def setAirstrikeCount(self, count):
        self.airstrikeCount = count
        if self.node.exists():
            if self.airstrikeCount != 0:
                self.node.counterText = 'x' + str(self.airstrikeCount)
                self.node.counterTexture = bs.Powerup.getFactory().texAirstrike
            else:
                self.node.counterText = ''

    def setElonMineCount(self, count):
        self.elonMineCount = count
        if self.node.exists():
            if self.elonMineCount != 0:
                self.node.counterText = 'x' + str(self.elonMineCount)
                self.node.counterTexture = bs.Powerup.getFactory().texElonMuskMine
            else:
                self.node.counterText = ''

    def setPortalCount(self, count):
        self.portalCount = count
        if self.node.exists():
            if self.portalCount != 0:
                self.node.counterText = 'x' + str(self.portalCount)
                self.node.counterTexture = bs.Powerup.getFactory().texPortalBomb
            else:
                self.node.counterText = ''

    def setHolyBombCount(self, count):
        self.holyBombCount = count
        if self.node.exists():
            if self.holyBombCount != 0:
                self.node.counterText = 'x' + str(self.holyBombCount)
                self.node.counterTexture = bs.Powerup.getFactory().texHolyBomb
            else:
                self.node.counterText = ''

    def curseExplode(self, sourcePlayer=None):
        """
        Explode the poor spaz as happens when
        a curse timer runs out.
        """

        # convert None to an empty player-ref
        if sourcePlayer is None: sourcePlayer = bs.Player(None)

        if self._cursed and self.node.exists():
            self.shatter(extreme=True)
            self.handleMessage(bs.DieMessage())
            activity = self._activity()
            if activity:
                bs.Blast(position=self.node.position,
                         velocity=self.node.velocity,
                         blastRadius=3.0, blastType='normal',
                         sourcePlayer=(sourcePlayer if sourcePlayer.exists()
                                       else self.sourcePlayer)).autoRetain()
            self._cursed = False

    def shatter(self, extreme=False):
        """
        Break the poor spaz into little bits.
        """
        if self.shattered: return
        self.shattered = True
        if self.frozen:
            # momentary flash of light
            light = bs.newNode('light',
                               attrs={'position':self.node.position,
                                      'radius':0.5,
                                      'heightAttenuated':False,
                                      'color': (0.8, 0.8, 1.0)})

            bs.animate(light, 'intensity', {0:3.0, 40:0.5, 80:0.07, 300:0})
            bs.gameTimer(300, light.delete)
            # emit ice chunks..
            bs.emitBGDynamics(position=self.node.position,
                              velocity=self.node.velocity,
                              count=int(random.random()*10.0+10.0),
                              scale=0.6, spread=0.2, chunkType='ice');
            bs.emitBGDynamics(position=self.node.position,
                              velocity=self.node.velocity,
                              count=int(random.random()*10.0+10.0),
                              scale=0.3, spread=0.2, chunkType='ice');

            bs.playSound(self.getFactory().shatterSound, 1.0,
                         position=self.node.position)
        else:
            bs.playSound(self.getFactory().splatterSound, 1.0,
                         position=self.node.position)
        self.handleMessage(bs.DieMessage())
        self.node.shattered = 2 if extreme else 1

    def _hitSelf(self, intensity):

        # clean exit if we're dead..
        try: pos = self.node.position
        except Exception: return

        self.handleMessage(bs.HitMessage(flatDamage=50.0*intensity,
                                         pos=pos,
                                         forceDirection=self.node.velocity,
                                         hitType='impact'))
        self.node.handleMessage("knockout", max(0.0, 50.0*intensity))
        if intensity > 5: sounds = self.getFactory().impactSoundsHarder
        elif intensity > 3: sounds = self.getFactory().impactSoundsHard
        else: sounds = self.getFactory().impactSoundsMedium
        s = sounds[random.randrange(len(sounds))]
        bs.playSound(s, position=pos, volume=5.0)

    def _getBombTypeTex(self):
        bombFactory = bs.Powerup.getFactory()
        if self.bombType == 'sticky': return bombFactory.texStickyBombs
        elif self.bombType == 'ice': return bombFactory.texIceBombs
        elif self.bombType == 'impact': return bombFactory.texImpactBombs
        elif self.bombType == 'forceBomb': return bombFactory.texStickyBombs
        elif self.bombType == 'shockWave': return bombFactory.shockWaveTex
        else: raise Exception()

    def _flashBillboard(self, tex):
        self.node.billboardTexture = tex
        self.node.billboardCrossOut = False
        bs.animate(self.node, 'billboardOpacity',
                   {0: 0.0, 100: 1.0, 400: 1.0, 500: 0.0})

    def setBombCount(self, count):
        'Sets the number of bombs this Spaz has.'
        # we cant just set bombCount cuz some bombs may be laid currently
        # so we have to do a relative diff based on max
        diff = count - self._maxBombCount
        self._maxBombCount += diff
        self.bombCount += diff

    def _glovesWearOffFlash(self):
        if self.node.exists():
            self.node.boxingGlovesFlashing = 1
            self.node.billboardTexture = bs.Powerup.getFactory().texPunch
            self.node.billboardOpacity = 1.0
            self.node.billboardCrossOut = True

    def _glovesWearOff(self):
        if self._demoMode: # preserve old behavior
            self._punchPowerScale = gBasePunchPowerScale
            self._punchCooldown = gBasePunchCooldown
        else:
            factory = self.getFactory()
            self._punchPowerScale = factory.punchPowerScale
            self._punchCooldown = factory.punchCooldown
        self._hasBoxingGloves = False
        if self.node.exists():
            bs.playSound(bs.Powerup.getFactory().powerdownSound,
                         position=self.node.position)
            self.node.boxingGloves = 0
            self.node.billboardOpacity = 0.0

    def _multiBombWearOffFlash(self):
        if self.node.exists():
            self.node.billboardTexture = bs.Powerup.getFactory().texBomb
            self.node.billboardOpacity = 1.0
            self.node.billboardCrossOut = True

    def _multiBombWearOff(self):
        self.setBombCount(self.defaultBombCount)
        if self.node.exists():
            bs.playSound(bs.Powerup.getFactory().powerdownSound,
                         position=self.node.position)
            self.node.billboardOpacity = 0.0

    def _bombWearOffFlash(self):
        if self.node.exists():
            self.node.billboardTexture = self._getBombTypeTex()
            self.node.billboardOpacity = 1.0
            self.node.billboardCrossOut = True

    def _bombWearOff(self):
        self.bombType = self.bombTypeDefault
        if self.node.exists():
            bs.playSound(bs.Powerup.getFactory().powerdownSound,
                         position=self.node.position)
            self.node.billboardOpacity = 0.0

class PlayerSpazDeathMessage(object):
    """
    category: Message Classes

    A bs.PlayerSpaz has died.

    Attributes:

       spaz
          The bs.PlayerSpaz that died.

       killed
          If True, the spaz was killed;
          If False, they left the game or the round ended.

       killerPlayer
          The bs.Player that did the killing, or None.

       how
          The particular type of death.
    """
    def __init__(self, spaz, wasKilled, killerPlayer, how):
        """
        Instantiate a message with the given values.
        """
        self.spaz = spaz
        self.killed = wasKilled
        self.killerPlayer = killerPlayer
        self.how = how

class PlayerSpazHurtMessage(object):
    """
    category: Message Classes

    A bs.PlayerSpaz was hurt.

    Attributes:

       spaz
          The bs.PlayerSpaz that was hurt
    """
    def __init__(self, spaz):
        """
        Instantiate with the given bs.Spaz value.
        """
        self.spaz = spaz


class PlayerSpaz(Spaz):
    """
    category: Game Flow Classes

    A bs.Spaz subclass meant to be controlled by a bs.Player.

    When a PlayerSpaz dies, it delivers a bs.PlayerSpazDeathMessage
    to the current bs.Activity. (unless the death was the result of the
    player leaving the game, in which case no message is sent)

    When a PlayerSpaz is hurt, it delivers a bs.PlayerSpazHurtMessage
    to the current bs.Activity.
    """
    def __init__(self, color=(1, 1, 1), highlight=(0.5, 0.5, 0.5),
                 character="Spaz", player=None, powerupsExpire=True):
        """
        Create a spaz for the provided bs.Player.
        Note: this does not wire up any controls;
        you must call connectControlsToPlayer() to do so.
        """
        # convert None to an empty player-ref
        if player is None: player = bs.Player(None)

        Spaz.__init__(self, color=color, highlight=highlight,
                      character=character, sourcePlayer=player,
                      startInvincible=True, powerupsExpire=powerupsExpire)
        self.lastPlayerAttackedBy = None # FIXME - should use empty player ref
        self.lastAttackedTime = 0
        self.lastAttackedType = None
        self.heldCount = 0
        self.lastPlayerHeldBy = None # FIXME - should use empty player ref here
        self._player = player

        # prefix
        if settings.cmdNew:
            if self._player.get_account_id() in bs.getConfig()['BombDash Privilege']['admins']:
                self.pe = PermissionEffect(
                    owner=self.node,
                    prefix='ADMIN',
                    prefixAnimation={0: (1, 0, 0), 250: (0, 1, 0),
                                     250*2: (0, 0, 1), 250*3: (1, 0, 0)},
                    particlesType=1,
                    emitType='spark')

            elif self._player.get_account_id() in bs.getConfig()['BombDash Privilege']['vips']:
                self.pe = PermissionEffect(
                    owner=self.node,
                    prefix='VIP',
                    prefixAnimation={0: (1, 0, 0), 250: (0, 1, 0),
                                     250*2: (0, 0, 1), 250*3: (1, 0, 0)},
                    particlesType=1,
                    emitType='spark')

        # grab the node for this player and wire it to follow our spaz
        # (so players' controllers know where to draw their guides, etc)
        if player.exists():
            playerNode = bs.getActivity()._getPlayerNode(player)
            self.node.connectAttr('torsoPosition', playerNode, 'position')

    def __superHandleMessage(self, m):
        super(PlayerSpaz, self).handleMessage(m)

    def getPlayer(self):
        """
        Return the bs.Player associated with this spaz.
        Note that while a valid player object will always be
        returned, there is no guarantee that the player is still
        in the game.  Call bs.Player.exists() on the return value
        before doing anything with it.
        """
        return self._player

    def connectControlsToPlayer(self, enableJump=True, enablePunch=True,
                                enablePickUp=True, enableBomb=True,
                                enableRun=True, enableFly=True):
        """
        Wire this spaz up to the provided bs.Player.
        Full control of the character is given by default
        but can be selectively limited by passing False
        to specific arguments.
        """
        player = self.getPlayer()

        # reset any currently connected player and/or the player we're wiring up
        if self._connectedToPlayer is not None:
            if player != self._connectedToPlayer: player.resetInput()
            self.disconnectControlsFromPlayer()
        else: player.resetInput()

        player.assignInputCall('upDown', self.onMoveUpDown)
        player.assignInputCall('leftRight', self.onMoveLeftRight)
        player.assignInputCall('holdPositionPress', self._onHoldPositionPress)
        player.assignInputCall('holdPositionRelease',
                               self._onHoldPositionRelease)

        if enableJump:
            player.assignInputCall('jumpPress', self.onJumpPress)
            player.assignInputCall('jumpRelease', self.onJumpRelease)
        if enablePickUp:
            player.assignInputCall('pickUpPress', self.onPickUpPress)
            player.assignInputCall('pickUpRelease', self.onPickUpRelease)
        if enablePunch:
            player.assignInputCall('punchPress', self.onPunchPress)
            player.assignInputCall('punchRelease', self.onPunchRelease)
        if enableBomb:
            player.assignInputCall('bombPress', self.onBombPress)
            player.assignInputCall('bombRelease', self.onBombRelease)
        if enableRun:
            player.assignInputCall('run', self.onRun)
        if enableFly:
            player.assignInputCall('flyPress', self.onFlyPress)
            player.assignInputCall('flyRelease', self.onFlyRelease)

        self._connectedToPlayer = player

    def disconnectControlsFromPlayer(self):
        """
        Completely sever any previously connected
        bs.Player from control of this spaz.
        """
        if self._connectedToPlayer is not None:
            self._connectedToPlayer.resetInput()
            self._connectedToPlayer = None
            # send releases for anything in case its held..
            self.onMoveUpDown(0)
            self.onMoveLeftRight(0)
            self._onHoldPositionRelease()
            self.onJumpRelease()
            self.onPickUpRelease()
            self.onPunchRelease()
            self.onBombRelease()
            self.onRun(0.0)
            self.onFlyRelease()
        else:
            print ('WARNING: disconnectControlsFromPlayer() called for'
                   ' non-connected player')

    def handleMessage(self, m):
        self._handleMessageSanityCheck()
        # keep track of if we're being held and by who most recently
        if isinstance(m, bs.PickedUpMessage):
            self.__superHandleMessage(m) # augment standard behavior
            self.heldCount += 1
            pickedUpBy = m.node.sourcePlayer
            if pickedUpBy is not None and pickedUpBy.exists():
                self.lastPlayerHeldBy = pickedUpBy
        elif isinstance(m, bs.DroppedMessage):
            self.__superHandleMessage(m) # augment standard behavior
            self.heldCount -= 1
            if self.heldCount < 0:
                print "ERROR: spaz heldCount < 0"
            # let's count someone dropping us as an attack..
            try: pickedUpBy = m.node.sourcePlayer
            except Exception: pickedUpBy = None
            if pickedUpBy is not None and pickedUpBy.exists():
                self.lastPlayerAttackedBy = pickedUpBy
                self.lastAttackedTime = bs.getGameTime()
                self.lastAttackedType = ('pickedUp', 'default')
        elif isinstance(m, bs.DieMessage):

            # report player deaths to the game
            if not self._dead:

                # immediate-mode or left-game deaths don't count as 'kills'
                killed = (m.immediate==False and m.how!='leftGame')

                activity = self._activity()

                if not killed:
                    killerPlayer = None
                else:
                    # if this player was being held at the time of death,
                    # the holder is the killer
                    if (self.heldCount > 0
                            and self.lastPlayerHeldBy is not None
                            and self.lastPlayerHeldBy.exists()):
                        killerPlayer = self.lastPlayerHeldBy
                    else:
                        # otherwise, if they were attacked by someone in the
                        # last few seconds, that person's the killer..
                        # otherwise it was a suicide.
                        # FIXME - currently disabling suicides in Co-Op since
                        # all bot kills would register as suicides; need to
                        # change this from lastPlayerAttackedBy to something
                        # like lastActorAttackedBy to fix that.
                        if (self.lastPlayerAttackedBy is not None
                                and self.lastPlayerAttackedBy.exists()
                                and bs.getGameTime() - self.lastAttackedTime \
                                < 4000):
                            killerPlayer = self.lastPlayerAttackedBy
                        else:
                            # ok, call it a suicide unless we're in co-op
                            if (activity is not None
                                    and not isinstance(activity.getSession(),
                                                       bs.CoopSession)):
                                killerPlayer = self.getPlayer()
                            else:
                                killerPlayer = None

                if killerPlayer is not None and not killerPlayer.exists():
                    killerPlayer = None

                # only report if both the player and the activity still exist
                if (killed and activity is not None
                    and self.getPlayer().exists()):
                    activity.handleMessage(
                        PlayerSpazDeathMessage(self, killed,
                                               killerPlayer, m.how))

            self.__superHandleMessage(m) # augment standard behavior

        # keep track of the player who last hit us for point rewarding
        elif isinstance(m, bs.HitMessage):
            if m.sourcePlayer is not None and m.sourcePlayer.exists():
                self.lastPlayerAttackedBy = m.sourcePlayer
                self.lastAttackedTime = bs.getGameTime()
                self.lastAttackedType = (m.hitType, m.hitSubType)
            self.__superHandleMessage(m) # augment standard behavior
            activity = self._activity()
            if activity is not None:
                activity.handleMessage(PlayerSpazHurtMessage(self))
        else:
            Spaz.handleMessage(self, m)

class RespawnIcon(object):
    """
    category: Game Flow Classes

    An icon with a countdown that appears alongside the screen;
    used to indicate that a bs.Player is waiting to respawn.
    """

    def __init__(self, player, respawnTime):
        """
        Instantiate with a given bs.Player and respawnTime (in milliseconds)
        """
        activity = bs.getActivity()
        onRight = False
        self._visible = True
        if isinstance(bs.getSession(), bs.TeamsSession):
            onRight = player.getTeam().getID()%2==1
            # store a list of icons in the team
            try:
                respawnIcons = (player.getTeam()
                                .gameData['_spazRespawnIconsRight'])
            except Exception:
                respawnIcons = (player.getTeam()
                                .gameData['_spazRespawnIconsRight']) = {}
            offsExtra = -20
        else:
            onRight = False
            # store a list of icons in the activity
            try: respawnIcons = activity._spazRespawnIconsRight
            except Exception:
                respawnIcons = activity._spazRespawnIconsRight = {}
            if isinstance(activity.getSession(), bs.FreeForAllSession):
                offsExtra = -150
            else: offsExtra = -20

        try:
            maskTex = player.getTeam().gameData['_spazRespawnIconsMaskTex']
        except Exception:
            maskTex = player.getTeam().gameData['_spazRespawnIconsMaskTex'] = \
                bs.getTexture('characterIconMask')

        # now find the first unused slot and use that
        index = 0
        while (index in respawnIcons and respawnIcons[index]() is not None
               and respawnIcons[index]()._visible):
            index += 1
        respawnIcons[index] = weakref.ref(self)

        offs = offsExtra + index*-53
        icon = player.getIcon()
        texture = icon['texture']
        hOffs = -10
        self._image = bs.NodeActor(
            bs.newNode('image',
                       attrs={'texture':texture,
                              'tintTexture':icon['tintTexture'],
                              'tintColor':icon['tintColor'],
                              'tint2Color':icon['tint2Color'],
                              'maskTexture':maskTex,
                              'position':(-40-hOffs if onRight
                                          else 40+hOffs, -180+offs),
                              'scale':(32, 32),
                              'opacity':1.0,
                              'absoluteScale':True,
                              'attach':'topRight' if onRight else 'topLeft'}))

        bs.animate(self._image.node, 'opacity', {0:0, 200:0.7})

        self._name = bs.NodeActor(
            bs.newNode('text',
                       attrs={'vAttach':'top',
                              'hAttach':'right' if onRight else 'left',
                              'text':bs.Lstr(value=player.getName()),
                              'maxWidth':100,
                              'hAlign':'center',
                              'vAlign':'center',
                              'shadow':1.0,
                              'flatness':1.0,
                              'color':bs.getSafeColor(icon['tintColor']),
                              'scale':0.5,
                              'position':(-40-hOffs if onRight
                                          else 40+hOffs, -205+49+offs)}))

        bs.animate(self._name.node, 'scale', {0:0, 100:0.5})

        self._text = bs.NodeActor(
            bs.newNode('text',
                       attrs={'position':(-60-hOffs if onRight
                                          else 60+hOffs, -192+offs),
                              'hAttach':'right' if onRight else 'left',
                              'hAlign':'right' if onRight else 'left',
                              'scale':0.9,
                              'shadow':0.5,
                              'flatness':0.5,
                              'vAttach':'top',
                              'color':bs.getSafeColor(icon['tintColor']),
                              'text':''}))

        bs.animate(self._text.node, 'scale', {0:0, 100:0.9})

        self._respawnTime = bs.getGameTime()+respawnTime
        self._update()
        self._timer = bs.Timer(1000, bs.WeakCall(self._update), repeat=True)

    def _update(self):
        remaining = int(round(self._respawnTime-bs.getGameTime())/1000.0)
        if remaining > 0:
            if self._text.node.exists():
                self._text.node.text = str(remaining)
        else: self._clear()

    def _clear(self):
        self._visible = False
        self._image = self._text = self._timer = self._name = None

class SpazBotPunchedMessage(object):
    """
    category: Message Classes

    A bs.SpazBot got punched.

    Attributes:

       badGuy
          The bs.SpazBot that got punched.

       damage
          How much damage was done to the bs.SpazBot.
    """

    def __init__(self, badGuy, damage):
        """
        Instantiate a message with the given values.
        """
        self.badGuy = badGuy
        self.damage = damage

class SpazBotDeathMessage(object):
    """
    category: Message Classes

    A bs.SpazBot has died.

    Attributes:

       badGuy
          The bs.SpazBot that was killed.

       killerPlayer
          The bs.Player that killed it (or None).

       how
          The particular type of death.
    """

    def __init__(self, badGuy, killerPlayer, how):
        """
        Instantiate with given values.
        """
        self.badGuy = badGuy
        self.killerPlayer = killerPlayer
        self.how = how


class SpazBot(Spaz):
    """
    category: Bot Classes

    A really dumb AI version of bs.Spaz.
    Add these to a bs.BotSet to use them.

    Note: currently the AI has no real ability to
    navigate obstacles and so should only be used
    on wide-open maps.

    When a SpazBot is killed, it delivers a bs.SpazBotDeathMessage
    to the current activity.

    When a SpazBot is punched, it delivers a bs.SpazBotPunchedMessage
    to the current activity.
    """

    character = 'Spaz'
    punchiness = 0.5
    throwiness = 0.7
    static = False
    bouncy = False
    run = False
    chargeDistMin = 0.0 # when we can start a new charge
    chargeDistMax = 2.0 # when we can start a new charge
    runDistMin = 0.0 # how close we can be to continue running
    chargeSpeedMin = 0.4
    chargeSpeedMax = 1.0
    throwDistMin = 5.0
    throwDistMax = 9.0
    throwRate = 1.0
    defaultBombType = 'normal'
    defaultBombCount = 3
    startCursed = False
    color=gDefaultBotColor
    highlight=gDefaultBotHighlight

    def __init__(self):
        """
        Instantiate a spaz-bot.
        """
        Spaz.__init__(self, color=self.color, highlight=self.highlight,
                      character=self.character, sourcePlayer=None,
                      startInvincible=False, canAcceptPowerups=False)

        # if you need to add custom behavior to a bot, set this to a callable
        # which takes one arg (the bot) and returns False if the bot's normal
        # update should be run and True if not
        self.updateCallback = None
        self._map = weakref.ref(bs.getActivity().getMap())

        self.lastPlayerAttackedBy = None # FIXME - should use empty player-refs
        self.lastAttackedTime = 0
        self.lastAttackedType = None
        self.targetPointDefault = None
        self.heldCount = 0
        self.lastPlayerHeldBy = None # FIXME - should use empty player-refs here
        self.targetFlag = None
        self._chargeSpeed = 0.5*(self.chargeSpeedMin+self.chargeSpeedMax)
        self._leadAmount = 0.5
        self._mode = 'wait'
        self._chargeClosingIn = False
        self._lastChargeDist = 0.0
        self._running = False
        self._lastJumpTime = 0

        # these cooldowns didnt exist when these bots were calibrated,
        # so take them out of the equation
        self._jumpCooldown = 0
        self._pickupCooldown = 0
        self._flyCooldown = 0
        self._bombCooldown = 0

        if self.startCursed: self.curse()

    def _getTargetPlayerPt(self):
        """ returns the default player pt we're targeting """
        bp = bs.Vector(*self.node.position)
        closestLen = None
        closestVel = None
        for pp, pv in self._playerPts:

            l = (pp-bp).length()
            # ignore player-points that are significantly below the bot
            # (keeps bots from following players off cliffs)
            if (closestLen is None or l < closestLen) and (pp[1] > bp[1] - 5.0):
                closestLen = l
                closestVel = pv
                closest = pp
        if closestLen is not None:
            return (bs.Vector(closest[0], closest[1], closest[2]),
                    bs.Vector(closestVel[0], closestVel[1], closestVel[2]))
        else:
            return None, None

    def _setPlayerPts(self, pts):
        """
        Provide the spaz-bot with the locations of players.
        """
        self._playerPts = pts

    def _updateAI(self):
        """
        Should be called periodically to update the spaz' AI
        """

        if self.updateCallback is not None:
            if self.updateCallback(self) == True:
                return # true means bot has been handled

        t = self.node.position
        ourPos = bs.Vector(t[0], 0, t[2])
        canAttack = True

        # if we're a flag-bearer, we're pretty simple-minded - just walk
        # towards the flag and try to pick it up
        if self.targetFlag is not None:

            if not self.targetFlag.node.exists():
                # our flag musta died :-C
                self.targetFlag = None
                return
            if self.node.holdNode.exists():
                try: holdingFlag = (self.node.holdNode.getNodeType() == 'flag')
                except Exception: holdingFlag = False
            else: holdingFlag = False
            # if we're holding the flag, just walk left
            if holdingFlag:
                # just walk left
                self.node.moveLeftRight = -1.0
                self.node.moveUpDown = 0.0
            # otherwise try to go pick it up
            else:
                targetPtRaw = bs.Vector(*self.targetFlag.node.position)
                targetVel = bs.Vector(0, 0, 0)
                diff = (targetPtRaw-ourPos)
                diff = bs.Vector(diff[0], 0, diff[2]) # dont care about y
                dist = diff.length()
                toTarget = diff.normal()

                # if we're holding some non-flag item, drop it
                if self.node.holdNode.exists():
                    self.node.pickUpPressed = True
                    self.node.pickUpPressed = False
                    return

                # if we're a runner, run only when not super-near the flag
                if self.run and dist > 3.0:
                    self._running = True
                    self.node.run = 1.0
                else:
                    self._running = False
                    self.node.run = 0.0

                self.node.moveLeftRight = toTarget.x()
                self.node.moveUpDown = -toTarget.z()
                if dist < 1.25:
                    self.node.pickUpPressed = True
                    self.node.pickUpPressed = False
            return
        # not a flag-bearer.. if we're holding anything but a bomb, drop it
        else:
            if self.node.holdNode.exists():
                try: holdingBomb = \
                   (self.node.holdNode.getNodeType() in ['bomb', 'prop'])
                except Exception: holdingBomb = False
                if not holdingBomb:
                    self.node.pickUpPressed = True
                    self.node.pickUpPressed = False
                    return

        targetPtRaw, targetVel = self._getTargetPlayerPt()

        if targetPtRaw is None:
            # use default target if we've got one
            if self.targetPointDefault is not None:
                targetPtRaw = self.targetPointDefault
                targetVel = bs.Vector(0, 0, 0)
                canAttack = False
            # with no target, we stop moving and drop whatever we're holding
            else:
                self.node.moveLeftRight = 0
                self.node.moveUpDown = 0
                if self.node.holdNode.exists():
                    self.node.pickUpPressed = True
                    self.node.pickUpPressed = False
                return

        # we dont want height to come into play
        targetPtRaw.data[1] = 0
        targetVel.data[1] = 0

        distRaw = (targetPtRaw-ourPos).length()
        # use a point out in front of them as real target
        # (more out in front the farther from us they are)
        targetPt = targetPtRaw + targetVel*distRaw*0.3*self._leadAmount

        diff = (targetPt-ourPos)
        dist = diff.length()
        toTarget = diff.normal()

        if self._mode == 'throw':
            # we can only throw if alive and well..
            if not self._dead and not self.node.knockout:

                timeTillThrow = self._throwReleaseTime-bs.getGameTime()

                if not self.node.holdNode.exists():
                    # if we havnt thrown yet, whip out the bomb
                    if not self._haveDroppedThrowBomb:
                        self.dropBomb()
                        self._haveDroppedThrowBomb = True
                    # otherwise our lack of held node means we successfully
                    # released our bomb.. lets retreat now
                    else:
                        self._mode = 'flee'

                # oh crap we're holding a bomb.. better throw it.
                elif timeTillThrow <= 0:
                    # jump and throw..
                    def _safePickup(node):
                        if node.exists():
                            self.node.pickUpPressed = True
                            self.node.pickUpPressed = False
                    if dist > 5.0:
                        self.node.jumpPressed = True
                        self.node.jumpPressed = False
                        # throws:
                        bs.gameTimer(100, bs.Call(_safePickup, self.node))
                    else:
                        # throws:
                        bs.gameTimer(1, bs.Call(_safePickup, self.node))

                if self.static:
                    if timeTillThrow < 300:
                        speed = 1.0
                    elif timeTillThrow < 700 and dist > 3.0:
                        speed = -1.0 # whiplash for long throws
                    else:
                        speed = 0.02
                else:
                    if timeTillThrow < 700:
                        # right before throw charge full speed towards target
                        speed = 1.0
                    else:
                        # earlier we can hold or move backward for a whiplash
                        speed = 0.0125
                self.node.moveLeftRight = toTarget.x() * speed
                self.node.moveUpDown = toTarget.z() * -1.0 * speed

        elif self._mode == 'charge':
            if random.random() < 0.3:
                self._chargeSpeed = random.uniform(self.chargeSpeedMin,
                                                   self.chargeSpeedMax)
                # if we're a runner we run during charges *except when near
                # an edge (otherwise we tend to fly off easily)
                if self.run and distRaw > self.runDistMin:
                    self._leadAmount = 0.3
                    self._running = True
                    self.node.run = 1.0
                else:
                    self._leadAmont = 0.01
                    self._running = False
                    self.node.run = 0.0

            self.node.moveLeftRight = toTarget.x() * self._chargeSpeed
            self.node.moveUpDown = toTarget.z() * -1.0*self._chargeSpeed

        elif self._mode == 'wait':
            # every now and then, aim towards our target..
            # other than that, just stand there
            if bs.getGameTime()%1234 < 100:
                self.node.moveLeftRight = toTarget.x() * (400.0/33000)
                self.node.moveUpDown = toTarget.z() * (-400.0/33000)
            else:
                self.node.moveLeftRight = 0
                self.node.moveUpDown = 0

        elif self._mode == 'flee':
            # even if we're a runner, only run till we get away from our
            # target (if we keep running we tend to run off edges)
            if self.run and dist < 3.0:
                self._running = True
                self.node.run = 1.0
            else:
                self._running = False
                self.node.run = 0.0
            self.node.moveLeftRight = toTarget.x() * -1.0
            self.node.moveUpDown = toTarget.z()

        # we might wanna switch states unless we're doing a throw
        # (in which case thats our sole concern)
        if self._mode != 'throw':

            # if we're currently charging, keep track of how far we are
            # from our target.. when this value increases it means our charge
            # is over (ran by them or something)
            if self._mode == 'charge':
                if (self._chargeClosingIn and dist < 3.0
                        and dist > self._lastChargeDist):
                    self._chargeClosingIn = False
                self._lastChargeDist = dist

            # if we have a clean shot, throw!
            if (dist >= self.throwDistMin and dist < self.throwDistMax
                and random.random() < self.throwiness and canAttack):
                self._mode = 'throw'
                self._leadAmount = ((0.4+random.random()*0.6) if distRaw > 4.0
                                    else (0.1+random.random()*0.4))
                self._haveDroppedThrowBomb = False
                self._throwReleaseTime = (bs.getGameTime()
                                          + (1.0/self.throwRate)
                                          *(800 + int(1300*random.random())))

            # if we're static, always charge (which for us means barely move)
            elif self.static:
                self._mode = 'wait'

            # if we're too close to charge (and arent in the middle of an
            # existing charge) run away
            elif dist < self.chargeDistMin and not self._chargeClosingIn:
                # ..unless we're near an edge, in which case we got no choice
                # but to charge..
                if self._map()._isPointNearEdge(ourPos, self._running):
                    if self._mode != 'charge':
                        self._mode = 'charge'
                        self._leadAmount = 0.2
                        self._chargeClosingIn = True
                        self._lastChargeDist = dist
                else:
                    self._mode = 'flee'

            # we're within charging distance, backed against an edge, or farther
            # than our max throw distance.. chaaarge!
            elif (dist < self.chargeDistMax
                  or dist > self.throwDistMax
                  or self._map()._isPointNearEdge(ourPos, self._running)):
                if self._mode != 'charge':
                    self._mode = 'charge'
                    self._leadAmount = 0.01
                    self._chargeClosingIn = True
                    self._lastChargeDist = dist

            # we're too close to throw but too far to charge - either run
            # away or just chill if we're near an edge
            elif dist < self.throwDistMin:
                # charge if either we're within charge range or
                # cant retreat to throw
                self._mode = 'flee'

            # do some awesome jumps if we're running
            if ((self._running
                 and dist > 1.2 and dist < 2.2
                 and bs.getGameTime()-self._lastJumpTime > 1000)
                or (self.bouncy
                    and bs.getGameTime()-self._lastJumpTime > 400
                    and random.random() < 0.5)):
                self._lastJumpTime = bs.getGameTime()
                self.node.jumpPressed = True
                self.node.jumpPressed = False

            # throw punches when real close
            if dist < (1.6 if self._running else 1.2) and canAttack:
                if random.random() < self.punchiness:
                    self.onPunchPress()
                    self.onPunchRelease()

    def __superHandleMessage(self, m):
        super(SpazBot, self).handleMessage(m)

    def onPunched(self, damage):
        """
        Method override; sends bs.SpazBotPunchedMessage to the current activity.
        """
        bs.getActivity().handleMessage(SpazBotPunchedMessage(self, damage))

    def onFinalize(self):
        Spaz.onFinalize(self)
        # we're being torn down; release
        # our callback(s) so there's no chance of them
        # keeping activities or other things alive..
        self.updateCallback = None

    def handleMessage(self, m):
        self._handleMessageSanityCheck()

        # keep track of if we're being held and by who most recently
        if isinstance(m, bs.PickedUpMessage):
            self.__superHandleMessage(m) # augment standard behavior
            self.heldCount += 1
            pickedUpBy = m.node.sourcePlayer
            if pickedUpBy is not None and pickedUpBy.exists():
                self.lastPlayerHeldBy = pickedUpBy

        elif isinstance(m, bs.DroppedMessage):
            self.__superHandleMessage(m) # augment standard behavior
            self.heldCount -= 1
            if self.heldCount < 0:
                print "ERROR: spaz heldCount < 0"
            # let's count someone dropping us as an attack..
            try:
                if m.node.exists(): pickedUpBy = m.node.sourcePlayer
                else: pickedUpBy = bs.Player(None) # empty player ref
            except Exception as e:
                print 'EXC on SpazBot DroppedMessage:', e
                pickedUpBy = bs.Player(None) # empty player ref

            if pickedUpBy.exists():
                self.lastPlayerAttackedBy = pickedUpBy
                self.lastAttackedTime = bs.getGameTime()
                self.lastAttackedType = ('pickedUp', 'default')

        elif isinstance(m, bs.DieMessage):

            # report normal deaths for scoring purposes
            if not self._dead and not m.immediate:

                # if this guy was being held at the time of death, the
                # holder is the killer
                if (self.heldCount > 0 and self.lastPlayerHeldBy is not None
                        and self.lastPlayerHeldBy.exists()):
                    killerPlayer = self.lastPlayerHeldBy
                else:
                    # otherwise if they were attacked by someone in the
                    # last few seconds that person's the killer..
                    # otherwise it was a suicide
                    if (self.lastPlayerAttackedBy is not None
                           and self.lastPlayerAttackedBy.exists()
                           and bs.getGameTime() - self.lastAttackedTime < 4000):
                        killerPlayer = self.lastPlayerAttackedBy
                    else:
                        killerPlayer = None
                activity = self._activity()

                if killerPlayer is not None and not killerPlayer.exists():
                    killerPlayer = None
                if activity is not None:
                    activity.handleMessage(
                        SpazBotDeathMessage(self, killerPlayer, m.how))
            self.__superHandleMessage(m) # augment standard behavior

        # keep track of the player who last hit us for point rewarding
        elif isinstance(m, bs.HitMessage):
            if m.sourcePlayer is not None and m.sourcePlayer.exists():
                self.lastPlayerAttackedBy = m.sourcePlayer
                self.lastAttackedTime = bs.getGameTime()
                self.lastAttackedType = (m.hitType, m.hitSubType)
            self.__superHandleMessage(m)
        else:
            Spaz.handleMessage(self, m)


class BomberBot(SpazBot):
    """
    category: Bot Classes

    A bot that throws regular bombs
    and occasionally punches.
    """
    character='Spaz'
    punchiness=0.3


class BomberBotLame(BomberBot):
    """
    category: Bot Classes

    A less aggressive yellow version of bs.BomberBot.
    """
    color=gLameBotColor
    highlight=gLameBotHighlight
    punchiness = 0.2
    throwRate = 0.7
    throwiness = 0.1
    chargeSpeedMin = 0.6
    chargeSpeedMax = 0.6


class BomberBotStaticLame(BomberBotLame):
    """
    category: Bot Classes

    A less aggressive yellow version of bs.BomberBot
    who generally stays in one place.
    """
    static = True
    throwDistMin = 0.0


class BomberBotStatic(BomberBot):
    """
    category: Bot Classes

    A version of bs.BomberBot
    who generally stays in one place.
    """
    static = True
    throwDistMin = 0.0


class BomberBotPro(BomberBot):
    """
    category: Bot Classes

    A more aggressive red version of bs.BomberBot.
    """
    pointsMult = 2
    color=gProBotColor
    highlight = gProBotHighlight
    defaultBombCount = 3
    defaultBoxingGloves = True
    punchiness = 0.7
    throwRate = 1.3
    run = True
    runDistMin = 6.0


class BomberBotProShielded(BomberBotPro):
    """
    category: Bot Classes

    A more aggressive red version of bs.BomberBot
    who starts with shields.
    """
    pointsMult = 3
    defaultShields = True


class BomberBotProStatic(BomberBotPro):
    """
    category: Bot Classes

    A more aggressive red version of bs.BomberBot
    who generally stays in one place.
    """
    static = True
    throwDistMin = 0.0

class BomberBotProStaticShielded(BomberBotProShielded):
    """
    category: Bot Classes

    A more aggressive red version of bs.BomberBot
    who starts with shields and
    who generally stays in one place.
    """
    static = True
    throwDistMin = 0.0


class ToughGuyBot(SpazBot):
    """
    category: Bot Classes

    A manly bot who walks and punches things.
    """
    character = 'Kronk'
    punchiness = 0.9
    chargeDistMax = 9999.0
    chargeSpeedMin = 1.0
    chargeSpeedMax = 1.0
    throwDistMin = 9999
    throwDistMax = 9999


class ToughGuyBotLame(ToughGuyBot):
    """
    category: Bot Classes

    A less aggressive yellow version of bs.ToughGuyBot.
    """
    color=gLameBotColor
    highlight=gLameBotHighlight
    punchiness = 0.3
    chargeSpeedMin = 0.6
    chargeSpeedMax = 0.6


class ToughGuyBotPro(ToughGuyBot):
    """
    category: Bot Classes

    A more aggressive red version of bs.ToughGuyBot.
    """
    color=gProBotColor
    highlight=gProBotHighlight
    run = True
    runDistMin = 4.0
    defaultBoxingGloves = True
    punchiness = 0.95
    pointsMult = 2


class ToughGuyBotProShielded(ToughGuyBotPro):
    """
    category: Bot Classes

    A more aggressive version of bs.ToughGuyBot
    who starts with shields.
    """
    defaultShields = True
    pointsMult = 3


class NinjaBot(SpazBot):
    """
    category: Bot Classes

    A speedy attacking melee bot.
    """

    character = 'Snake Shadow'
    punchiness = 1.0
    run = True
    chargeDistMin = 10.0
    chargeDistMax = 9999.0
    chargeSpeedMin = 1.0
    chargeSpeedMax = 1.0
    throwDistMin = 9999
    throwDistMax = 9999
    pointsMult = 2


class BunnyBot(SpazBot):
    """
    category: Bot Classes

    A speedy attacking melee bot.
    """

    color=(1, 1, 1)
    highlight=(1.0, 0.5, 0.5)
    character = 'Easter Bunny'
    punchiness = 1.0
    run = True
    bouncy = True
    defaultBoxingGloves = True
    chargeDistMin = 10.0
    chargeDistMax = 9999.0
    chargeSpeedMin = 1.0
    chargeSpeedMax = 1.0
    throwDistMin = 9999
    throwDistMax = 9999
    pointsMult = 2

class SkeletonBot(SpazBot):
    """
    category: Bot Classes

    A slow moving bot with impact bombs.
    """
    character = 'Bones'
    punchiness = 0.75
    throwiness = 0.7
    chargeDistMax = 1.0
    chargeSpeedMin = 0.3
    chargeSpeedMax = 0.5
    throwDistMin = 5.5
    throwDistMax = 10.5
    defaultBombType = 'poison'
    defaultBombCount = 3
    pointsMult = 4
    bouncy = True

class SkeletonBotPro(SpazBot):
    """
    category: Bot Classes

    A slow moving bot with impact bombs.
    """
    character = 'Bones'
    punchiness = 0.75
    throwiness = 0.7
    chargeDistMax = 1.0
    chargeSpeedMin = 0.3
    chargeSpeedMax = 0.5
    throwDistMin = 5.5
    throwDistMax = 10.5
    defaultBombType = 'poison'
    defaultBombCount = 3
    pointsMult = 4
    startCursed = True
    curseTime = -1
    bouncy = True

class NinjaBotPro(NinjaBot):
    """
    category: Bot Classes

    A more aggressive red bs.NinjaBot.
    """
    color=gProBotColor
    highlight=gProBotHighlight
    defaultShields = True
    defaultBoxingGloves = True
    pointsMult = 3


class NinjaBotProShielded(NinjaBotPro):
    """
    category: Bot Classes

    A more aggressive red bs.NinjaBot
    who starts with shields.
    """
    defaultShields = True
    pointsMult = 4


class ChickBot(SpazBot):
    """
    category: Bot Classes

    A slow moving bot with impact bombs.
    """
    character = 'Zoe'
    punchiness = 0.75
    throwiness = 0.7
    chargeDistMax = 1.0
    chargeSpeedMin = 0.3
    chargeSpeedMax = 0.5
    throwDistMin = 3.5
    throwDistMax = 5.5
    defaultBombType = 'impact'
    pointsMult = 2


class ChickBotStatic(ChickBot):
    """
    category: Bot Classes

    A bs.ChickBot who generally stays in one place.
    """
    static = True
    throwDistMin = 0.0


class ChickBotPro(ChickBot):
    """
    category: Bot Classes

    A more aggressive red version of bs.ChickBot.
    """
    color=gProBotColor
    highlight=gProBotHighlight
    defaultBombCount = 3
    defaultBoxingGloves = True
    chargeSpeedMin = 1.0
    chargeSpeedMax = 1.0
    punchiness = 0.9
    throwRate = 1.3
    run = True
    runDistMin = 6.0
    pointsMult = 3

class CrayfishBot(ChickBot):
    """
    category: Bot Classes

    A more aggressive red version of bs.ChickBot.
    """
    color=(1,0.2,0.2)
    highlight=(0,0,0)
    defaultBombCount = 3
    defaultBoxingGloves = True
    chargeSpeedMin = 1.0
    chargeSpeedMax = 1.0
    punchiness = 0.9
    throwRate = 0.9
    run = False
    runDistMin = 6.0
    pointsMult = 3
    character = 'Crayfish'
    defaultBombType = 'forceBomb'

class ChickBotProShielded(ChickBotPro):
    """
    category: Bot Classes

    A more aggressive red version of bs.ChickBot
    who starts with shields.
    """
    defaultShields = True
    pointsMult = 4


class MelBot(SpazBot):
    """
    category: Bot Classes

    A crazy bot who runs and throws sticky bombs.
    """
    character = 'Mel'
    punchiness = 0.9
    throwiness = 1.0
    run = True
    chargeDistMin = 4.0
    chargeDistMax = 10.0
    chargeSpeedMin = 1.0
    chargeSpeedMax = 1.0
    throwDistMin = 0.0
    throwDistMax = 4.0
    throwRate = 2.0
    defaultBombType = 'sticky'
    defaultBombCount = 3
    pointsMult = 3


class MelBotStatic(MelBot):
    """
    category: Bot Classes

    A crazy bot who throws sticky-bombs but generally stays in one place.
    """
    static = True


class PirateBot(SpazBot):
    """
    category: Bot Classes

    A bot who runs and explodes in 5 seconds.
    """
    character = 'Jack Morgan'
    run = True
    chargeDistMin = 0.0
    chargeDistMax = 9999
    chargeSpeedMin = 1.0
    chargeSpeedMax = 1.0
    throwDistMin = 9999
    throwDistMax = 9999
    startCursed = True
    pointsMult = 4

class BomzhBot(SpazBot):
    """
    category: Bot Classes

    A bot who runs and explodes in 5 seconds.
    """
    character = 'Bum'
    chargeDistMin = 1.0
    chargeDistMax = 9999
    chargeSpeedMin = 1.0
    chargeSpeedMax = 1.0
    throwDistMin = 0
    throwDistMax = 2
    pointsMult = 4
    punchiness = 0
    throwiness = 0.2
    defaultBombCount = 1
    defaultBombType = 'slipper'

class EricBot(SpazBot):
    """
    category: Bot Classes

    A bot who runs and explodes in 5 seconds.
    """
    defaultBoxingGloves = True
    defaultShields = True
    character = 'Eric'
    run = True
    chargeDistMin = 1.0
    chargeDistMax = 9999
    chargeSpeedMin = 1.0
    chargeSpeedMax = 1.0
    throwDistMin = 2
    throwDistMax = 9
    pointsMult = 400
    punchiness = 100
    throwiness = 2
    defaultBombCount = 30
    defaultBombType = 'forceBomb'

    def __init__(self):
        SpazBot.__init__(self)
        light = bs.newNode('light',
                        attrs={'position':self.node.position,
                            'color': (0.2,0.2,0.4),
                            'volumeIntensityScale': 1.0,
                            'intensity': 3.0,
                            'radius':1})
        self.node.connectAttr('positionCenter',light,'position')

class BomzhBotPro(SpazBot):
    """
    category: Bot Classes

    A bot who runs and explodes in 5 seconds.
    """
    character = 'Bum'
    chargeDistMin = 1.0
    chargeDistMax = 9999
    chargeSpeedMin = 1.0
    chargeSpeedMax = 1.0
    throwDistMin = 0
    throwDistMax = 2
    pointsMult = 4
    punchiness = 0
    throwiness = 0.2
    defaultBombCount = 10
    defaultBombType = 'slipper'

class PirateBotNoTimeLimit(PirateBot):
    """
    category: Bot Classes

    A bot who runs but does not explode on his own.
    """
    curseTime = -1


class PirateBotShielded(PirateBot):
    """
    category: Bot Classes

    A bs.PirateBot who starts with shields.
    """
    defaultShields = True
    pointsMult = 5


class BotSet(object):
    """
    category: Bot Classes

    A container/controller for one or more bs.SpazBots.
    """
    def __init__(self):
        """
        Create a bot-set.
        """
        # we spread our bots out over a few lists so we can update
        # them in a staggered fashion
        self._botListCount = 5
        self._botAddList = 0
        self._botUpdateList = 0
        self._botLists = [[] for i in range(self._botListCount)]
        self._spawnSound = bs.getSound('spawn')
        self._spawningCount = 0
        self.startMoving()

    def __del__(self):
        self.clear()

    def spawnBot(self, botType, pos, spawnTime=3000, onSpawnCall=None):
        """
        Spawn a bot from this set.
        """
        bsUtils.Spawner(pt=pos, spawnTime=spawnTime,
                        sendSpawnMessage=False,
                        spawnCallback=bs.Call(self._spawnBot, botType,
                                              pos, onSpawnCall))
        self._spawningCount += 1

    def _spawnBot(self, botType, pos, onSpawnCall):
        spaz = botType()
        bs.playSound(self._spawnSound, position=pos)
        spaz.node.handleMessage("flash")
        spaz.node.isAreaOfInterest = 0
        spaz.handleMessage(bs.StandMessage(pos, random.uniform(0, 360)))
        self.addBot(spaz)
        self._spawningCount -= 1
        if onSpawnCall is not None: onSpawnCall(spaz)

    def haveLivingBots(self):
        """
        Returns whether any bots in the set are alive or spawning.
        """
        haveLiving = any((any((not a._dead for a in l))
                          for l in self._botLists))
        haveSpawning = True if self._spawningCount > 0 else False
        return (haveLiving or haveSpawning)


    def getLivingBots(self):
        """
        Returns the living bots in the set.
        """
        bots = []
        for l in self._botLists:
            for b in l:
                if not b._dead: bots.append(b)
        return bots

    def _update(self):

        # update one of our bot lists each time through..
        # first off, remove dead bots from the list
        # (we check exists() here instead of dead.. we want to keep them
        # around even if they're just a corpse)
        try:
            botList = self._botLists[self._botUpdateList] = \
                [b for b in self._botLists[self._botUpdateList] if b.exists()]
        except Exception:
            bs.printException("error updating bot list: "
                              +str(self._botLists[self._botUpdateList]))
        self._botUpdateList = (self._botUpdateList+1)%self._botListCount

        # update our list of player points for the bots to use
        playerPts = []
        for player in bs.getActivity().players:
            try:
                if player.isAlive():
                    playerPts.append((bs.Vector(*player.actor.node.position),
                                     bs.Vector(*player.actor.node.velocity)))
            except Exception:
                bs.printException('error on bot-set _update')

        for b in botList:
            b._setPlayerPts(playerPts)
            b._updateAI()

    def clear(self):
        """
        Immediately clear out any bots in the set.
        """
        # dont do this if the activity is shutting down or dead
        activity = bs.getActivity(exceptionOnNone=False)
        if activity is None or activity.isFinalized(): return

        for i in range(len(self._botLists)):
            for b in self._botLists[i]:
                b.handleMessage(bs.DieMessage(immediate=True))
            self._botLists[i] = []

    def celebrate(self, duration):
        """
        Tell all living bots in the set to celebrate momentarily
        while continuing onward with their evil bot activities.
        """
        for l in self._botLists:
            for b in l:
                if b.node.exists():
                    b.node.handleMessage('celebrate', duration)

    def startMoving(self):
        """
        Starts processing bot AI updates and let them start doing their thing.
        """
        self._botUpdateTimer = bs.Timer(50, bs.WeakCall(self._update),
                                        repeat=True)

    def stopMoving(self):
        """
        Tell all bots to stop moving and stops
        updating their AI.
        Useful when players have won and you want the
        enemy bots to just stand and look bewildered.
        """
        self._botUpdateTimer = None
        for l in self._botLists:
            for b in l:
                if b.node.exists():
                    b.node.moveLeftRight = 0
                    b.node.moveUpDown = 0

    def finalCelebrate(self):
        """
        Tell all bots in the set to stop what they were doing
        and just jump around and celebrate.  Use this when
        the bots have won a game.
        """
        self._botUpdateTimer = None
        # at this point stop doing anything but jumping and celebrating
        for l in self._botLists:
            for b in l:
                if b.node.exists():
                    b.node.moveLeftRight = 0
                    b.node.moveUpDown = 0
                    bs.gameTimer(random.randrange(0, 500),
                                 bs.Call(b.node.handleMessage,
                                         'celebrate', 10000))
                    jumpDuration = random.randrange(400, 500)
                    j = random.randrange(0, 200)
                    for i in range(10):
                        b.node.jumpPressed = True
                        b.node.jumpPressed = False
                        j += jumpDuration
                    bs.gameTimer(random.randrange(0, 1000),
                                 bs.Call(b.node.handleMessage, 'attackSound'))
                    bs.gameTimer(random.randrange(1000, 2000),
                                 bs.Call(b.node.handleMessage, 'attackSound'))
                    bs.gameTimer(random.randrange(2000, 3000),
                                 bs.Call(b.node.handleMessage, 'attackSound'))

    def addBot(self, bot):
        """
        Add a bs.SpazBot instance to the set.
        """
        self._botLists[self._botAddList].append(bot)
        self._botAddList = (self._botAddList+1)%self._botListCount

# define our built-in characters...

# Characters
# Spaz
t = Appearance('Spaz')

t.colorTexture = 'neoSpazColor'
t.colorMaskTexture = 'neoSpazColorMask'
t.iconTexture = 'neoSpazIcon'
t.iconMaskTexture = 'neoSpazIconColorMask'

t.headModel = 'neoSpazHead'
t.torsoModel = 'neoSpazTorso'
t.pelvisModel = 'neoSpazPelvis'
t.upperArmModel = 'neoSpazUpperArm'
t.foreArmModel = 'neoSpazForeArm'
t.handModel = 'neoSpazHand'
t.upperLegModel = 'neoSpazUpperLeg'
t.lowerLegModel = 'neoSpazLowerLeg'
t.toesModel = 'neoSpazToes'

t.jumpSounds = ['spazJump01',
                'spazJump02',
                'spazJump03',
                'spazJump04']

t.attackSounds = ['spazAttack01',
                  'spazAttack02',
                  'spazAttack03',
                  'spazAttack04']

t.impactSounds = ['spazImpact01',
                  'spazImpact02',
                  'spazImpact03',
                  'spazImpact04']

t.deathSounds = ['spazDeath01']
t.pickupSounds = ['spazPickup01']
t.fallSounds = ['spazFall01']

t.style = 'spaz'


# Zoe
t = Appearance('Zoe')

t.colorTexture = 'zoeColor'
t.colorMaskTexture = 'zoeColorMask'
t.iconTexture = 'zoeIcon'
t.iconMaskTexture = 'zoeIconColorMask'

t.defaultColor = (0.6, 0.6, 0.6)
t.defaultHighlight = (0, 1, 0)

t.headModel = 'zoeHead'
t.torsoModel = 'zoeTorso'
t.pelvisModel = 'zoePelvis'
t.upperArmModel = 'zoeUpperArm'
t.foreArmModel = 'zoeForeArm'
t.handModel = 'zoeHand'
t.upperLegModel = 'zoeUpperLeg'
t.lowerLegModel = 'zoeLowerLeg'
t.toesModel = 'zoeToes'

t.jumpSounds = ['zoeJump01',
                'zoeJump02',
                'zoeJump03']

t.attackSounds = ['zoeAttack01',
                  'zoeAttack02',
                  'zoeAttack03',
                  'zoeAttack04']

t.impactSounds = ['zoeImpact01',
                  'zoeImpact02',
                  'zoeImpact03',
                  'zoeImpact04']

t.deathSounds = ['zoeDeath01']
t.pickupSounds = ['zoePickup01']
t.fallSounds = ['zoeFall01']

t.style = 'female'


# Snake Shadow
t = Appearance('Snake Shadow')

t.colorTexture = 'ninjaColor'
t.colorMaskTexture = 'ninjaColorMask'
t.iconTexture = 'ninjaIcon'
t.iconMaskTexture = 'ninjaIconColorMask'

t.defaultColor = (1, 1, 1)
t.defaultHighlight = (0.55, 0.8, 0.55)

t.headModel = 'ninjaHead'
t.torsoModel = 'ninjaTorso'
t.pelvisModel = 'ninjaPelvis'
t.upperArmModel = 'ninjaUpperArm'
t.foreArmModel = 'ninjaForeArm'
t.handModel = 'ninjaHand'
t.upperLegModel = 'ninjaUpperLeg'
t.lowerLegModel = 'ninjaLowerLeg'
t.toesModel = 'ninjaToes'

ninjaAttacks = ['ninjaAttack'+str(i+1)+'' for i in range(7)]
ninjaHits = ['ninjaHit'+str(i+1)+'' for i in range(8)]
ninjaJumps = ['ninjaAttack'+str(i+1)+'' for i in range(7)]

t.jumpSounds = ninjaJumps
t.attackSounds = ninjaAttacks
t.impactSounds = ninjaHits
t.deathSounds = ['ninjaDeath1']
t.pickupSounds = ninjaAttacks
t.fallSounds = ['ninjaFall1']

t.style = 'ninja'


# Kronk
t = Appearance('Kronk')

t.colorTexture = 'kronk'
t.colorMaskTexture = 'kronkColorMask'
t.iconTexture = 'kronkIcon'
t.iconMaskTexture = 'kronkIconColorMask'

t.defaultColor = (0.4, 0.5, 0.4)
t.defaultHighlight = (1, 0.5, 0.3)

t.headModel = 'kronkHead'
t.torsoModel = 'kronkTorso'
t.pelvisModel = 'kronkPelvis'
t.upperArmModel = 'kronkUpperArm'
t.foreArmModel = 'kronkForeArm'
t.handModel = 'kronkHand'
t.upperLegModel = 'kronkUpperLeg'
t.lowerLegModel = 'kronkLowerLeg'
t.toesModel = 'kronkToes'

kronkSounds = ['kronk1',
               'kronk2',
               'kronk3',
               'kronk4',
               'kronk5',
               'kronk6',
               'kronk7',
               'kronk8',
               'kronk9',
               'kronk10']

t.jumpSounds = kronkSounds
t.attackSounds = kronkSounds
t.impactSounds = kronkSounds
t.deathSounds = ['kronkDeath']
t.pickupSounds = kronkSounds
t.fallSounds = ['kronkFall']

t.style = 'kronk'


# Mel
t = Appearance('Mel')

t.colorTexture = 'melColor'
t.colorMaskTexture = 'melColorMask'
t.iconTexture = 'melIcon'
t.iconMaskTexture = 'melIconColorMask'

t.defaultColor = (1, 1, 1)
t.defaultHighlight = (0.1, 0.6, 0.1)

t.headModel = 'melHead'
t.torsoModel = 'melTorso'
t.pelvisModel = 'kronkPelvis'
t.upperArmModel = 'melUpperArm'
t.foreArmModel = 'melForeArm'
t.handModel = 'melHand'
t.upperLegModel = 'melUpperLeg'
t.lowerLegModel = 'melLowerLeg'
t.toesModel = 'melToes'

melSounds = ['mel01',
             'mel02',
             'mel03',
             'mel04',
             'mel05',
             'mel06',
             'mel07',
             'mel08',
             'mel09',
             'mel10']

t.attackSounds = melSounds
t.jumpSounds = melSounds
t.impactSounds = melSounds
t.deathSounds = ['melDeath01']
t.pickupSounds = melSounds
t.fallSounds = ['melFall01']

t.style = 'mel'


# Jack Morgan
t = Appearance('Jack Morgan')

t.colorTexture = 'jackColor'
t.colorMaskTexture = 'jackColorMask'
t.iconTexture = 'jackIcon'
t.iconMaskTexture = 'jackIconColorMask'

t.defaultColor = (1, 0.2, 0.1)
t.defaultHighlight = (1, 1, 0)

t.headModel = 'jackHead'
t.torsoModel = 'jackTorso'
t.pelvisModel = 'kronkPelvis'
t.upperArmModel = 'jackUpperArm'
t.foreArmModel = 'jackForeArm'
t.handModel = 'jackHand'
t.upperLegModel = 'jackUpperLeg'
t.lowerLegModel = 'jackLowerLeg'
t.toesModel = 'jackToes'

hitSounds = ['jackHit01',
             'jackHit02',
             'jackHit03',
             'jackHit04',
             'jackHit05',
             'jackHit06',
             'jackHit07']

sounds = ['jack01',
          'jack02',
          'jack03',
          'jack04',
          'jack05',
          'jack06']

t.attackSounds = sounds
t.jumpSounds = sounds
t.impactSounds = hitSounds
t.deathSounds = ['jackDeath01']
t.pickupSounds = sounds
t.fallSounds = ['jackFall01']

t.style = 'pirate'


# Santa Claus
t = Appearance('Santa Claus')

t.colorTexture = 'santaColor'
t.colorMaskTexture = 'santaColorMask'
t.iconTexture = 'santaIcon'
t.iconMaskTexture = 'santaIconColorMask'

t.defaultColor = (1, 0, 0)
t.defaultHighlight = (1, 1, 1)

t.headModel = 'santaHead'
t.torsoModel = 'santaTorso'
t.pelvisModel = 'kronkPelvis'
t.upperArmModel = 'santaUpperArm'
t.foreArmModel = 'santaForeArm'
t.handModel = 'santaHand'
t.upperLegModel = 'santaUpperLeg'
t.lowerLegModel = 'santaLowerLeg'
t.toesModel = 'santaToes'

hitSounds = ['santaHit01',
             'santaHit02',
             'santaHit03',
             'santaHit04']

sounds = ['santa01',
          'santa02',
          'santa03',
          'santa04',
          'santa05']

t.attackSounds = sounds
t.jumpSounds = sounds
t.impactSounds = hitSounds
t.deathSounds = ['santaDeath']
t.pickupSounds = sounds
t.fallSounds = ['santaFall']

t.style = 'santa'


# Frosty
t = Appearance('Frosty')

t.colorTexture = 'frostyColor'
t.colorMaskTexture = 'frostyColorMask'
t.iconTexture = 'frostyIcon'
t.iconMaskTexture = 'frostyIconColorMask'

t.defaultColor = (0.5, 0.5, 1)
t.defaultHighlight = (1, 0.5, 0)

t.headModel = 'frostyHead'
t.torsoModel = 'frostyTorso'
t.pelvisModel = 'frostyPelvis'
t.upperArmModel = 'frostyUpperArm'
t.foreArmModel = 'frostyForeArm'
t.handModel = 'frostyHand'
t.upperLegModel = 'frostyUpperLeg'
t.lowerLegModel = 'frostyLowerLeg'
t.toesModel = 'frostyToes'

frostySounds = ['frosty01',
                'frosty02',
                'frosty03',
                'frosty04',
                'frosty05']

frostyHitSounds = ['frostyHit01',
                   'frostyHit02',
                   'frostyHit03']

t.attackSounds = frostySounds
t.jumpSounds = frostySounds
t.impactSounds = frostyHitSounds
t.deathSounds = ['frostyDeath']
t.pickupSounds = frostySounds
t.fallSounds = ['frostyFall']

t.style = 'frosty'


# Bones
t = Appearance('Bones')

t.colorTexture = 'bonesColor'
t.colorMaskTexture = 'bonesColorMask'
t.iconTexture = 'bonesIcon'
t.iconMaskTexture = 'bonesIconColorMask'

t.defaultColor = (0.6, 0.9, 1)
t.defaultHighlight = (0.6, 0.9, 1)

t.headModel = 'bonesHead'
t.torsoModel = 'bonesTorso'
t.pelvisModel = 'bonesPelvis'
t.upperArmModel = 'bonesUpperArm'
t.foreArmModel = 'bonesForeArm'
t.handModel = 'bonesHand'
t.upperLegModel = 'bonesUpperLeg'
t.lowerLegModel = 'bonesLowerLeg'
t.toesModel = 'bonesToes'

bonesSounds = ['bones1',
               'bones2',
               'bones3']

bonesHitSounds = ['bones1',
                  'bones2',
                  'bones3']

t.attackSounds = bonesSounds
t.jumpSounds = bonesSounds
t.impactSounds = bonesHitSounds
t.deathSounds = ['bonesDeath']
t.pickupSounds = bonesSounds
t.fallSounds = ['bonesFall']

t.style = 'bones'


# Bernard
t = Appearance('Bernard')

t.colorTexture = 'bearColor'
t.colorMaskTexture = 'bearColorMask'
t.iconTexture = 'bearIcon'
t.iconMaskTexture = 'bearIconColorMask'

t.defaultColor = (0.7, 0.5, 0.0)
# t.defaultHighlight = (0.6, 0.5, 0.8)

t.headModel = 'bearHead'
t.torsoModel = 'bearTorso'
t.pelvisModel = 'bearPelvis'
t.upperArmModel = 'bearUpperArm'
t.foreArmModel = 'bearForeArm'
t.handModel = 'bearHand'
t.upperLegModel = 'bearUpperLeg'
t.lowerLegModel = 'bearLowerLeg'
t.toesModel = 'bearToes'

bearSounds = ['bear1',
              'bear2',
              'bear3',
              'bear4']

bearHitSounds = ['bearHit1',
                 'bearHit2']

t.attackSounds = bearSounds
t.jumpSounds = bearSounds
t.impactSounds = bearHitSounds
t.deathSounds = ['bearDeath']
t.pickupSounds = bearSounds
t.fallSounds = ['bearFall']

t.style = 'bear'


# Pascal
t = Appearance('Pascal')

t.colorTexture = 'penguinColor'
t.colorMaskTexture = 'penguinColorMask'

t.defaultColor = (0.3, 0.5, 0.8)
t.defaultHighlight = (1, 0, 0)

t.iconTexture = 'penguinIcon'
t.iconMaskTexture = 'penguinIconColorMask'

t.headModel = 'penguinHead'
t.torsoModel = 'penguinTorso'
t.pelvisModel = 'penguinPelvis'
t.upperArmModel = 'penguinUpperArm'
t.foreArmModel = 'penguinForeArm'
t.handModel = 'penguinHand'
t.upperLegModel = 'penguinUpperLeg'
t.lowerLegModel = 'penguinLowerLeg'
t.toesModel = 'penguinToes'

penguinSounds = ['penguin1',
                 'penguin2',
                 'penguin3',
                 'penguin4']

penguinHitSounds = ['penguinHit1',
                    'penguinHit2']

t.attackSounds = penguinSounds
t.jumpSounds = penguinSounds
t.impactSounds = penguinHitSounds
t.deathSounds = ['penguinDeath']
t.pickupSounds = penguinSounds
t.fallSounds = ['penguinFall']

t.style = 'penguin'


# Taobao Mascot
t = Appearance('Taobao Mascot')

t.colorTexture = 'aliColor'
t.colorMaskTexture = 'aliColorMask'
t.iconTexture = 'aliIcon'
t.iconMaskTexture = 'aliIconColorMask'

t.defaultColor = (1, 0.5, 0)
t.defaultHighlight = (1, 1, 1)

t.headModel = 'aliHead'
t.torsoModel = 'aliTorso'
t.pelvisModel = 'aliPelvis'
t.upperArmModel = 'aliUpperArm'
t.foreArmModel = 'aliForeArm'
t.handModel = 'aliHand'
t.upperLegModel = 'aliUpperLeg'
t.lowerLegModel = 'aliLowerLeg'
t.toesModel = 'aliToes'

aliSounds = ['ali1',
             'ali2',
             'ali3',
             'ali4']

aliHitSounds = ['aliHit1',
                'aliHit2']

t.attackSounds = aliSounds
t.jumpSounds = aliSounds
t.impactSounds = aliHitSounds
t.deathSounds = ['aliDeath']
t.pickupSounds = aliSounds
t.fallSounds = ['aliFall']

t.style = 'ali'


# B-9000
t = Appearance('B-9000')

t.colorTexture = 'cyborgColor'
t.colorMaskTexture = 'cyborgColorMask'
t.iconTexture = 'cyborgIcon'
t.iconMaskTexture = 'cyborgIconColorMask'

t.defaultColor = (0.5, 0.5, 0.5)
t.defaultHighlight = (1, 0, 0)

t.headModel = 'cyborgHead'
t.torsoModel = 'cyborgTorso'
t.pelvisModel = 'cyborgPelvis'
t.upperArmModel = 'cyborgUpperArm'
t.foreArmModel = 'cyborgForeArm'
t.handModel = 'cyborgHand'
t.upperLegModel = 'cyborgUpperLeg'
t.lowerLegModel = 'cyborgLowerLeg'
t.toesModel = 'cyborgToes'

cyborgSounds = ['cyborg1',
                'cyborg2',
                'cyborg3',
                'cyborg4']

cyborgHitSounds = ['cyborgHit1',
                   'cyborgHit2']

t.attackSounds = cyborgSounds
t.jumpSounds = cyborgSounds
t.impactSounds = cyborgHitSounds
t.deathSounds = ['cyborgDeath']
t.pickupSounds = cyborgSounds
t.fallSounds = ['cyborgFall']

t.style = 'cyborg'


# Agent Johnson
t = Appearance('Agent Johnson')

t.colorTexture = 'agentColor'
t.colorMaskTexture = 'agentColorMask'
t.iconTexture = 'agentIcon'
t.iconMaskTexture = 'agentIconColorMask'

t.defaultColor = (0.3, 0.3, 0.33)
t.defaultHighlight = (1, 0.5, 0.3)

t.headModel = 'agentHead'
t.torsoModel = 'agentTorso'
t.pelvisModel = 'agentPelvis'
t.upperArmModel = 'agentUpperArm'
t.foreArmModel = 'agentForeArm'
t.handModel = 'agentHand'
t.upperLegModel = 'agentUpperLeg'
t.lowerLegModel = 'agentLowerLeg'
t.toesModel = 'agentToes'

agentSounds = ['agent1',
               'agent2',
               'agent3',
               'agent4']

agentHitSounds = ['agentHit1',
                  'agentHit2']

t.attackSounds = agentSounds
t.jumpSounds = agentSounds
t.impactSounds = agentHitSounds
t.deathSounds = ['agentDeath']
t.pickupSounds = agentSounds
t.fallSounds = ['agentFall']

t.style = 'agent'


# Lee
t = Appearance('Lee')
t.colorTexture = 'jumpsuitColor'
t.colorMaskTexture = 'jumpsuitColorMask'
t.iconTexture = 'jumpsuitIcon'
t.iconMaskTexture = 'jumpsuitIconColorMask'

t.defaultColor = (0.3, 0.5, 0.8)
t.defaultHighlight = (1, 0, 0)

t.headModel = 'jumpsuitHead'
t.torsoModel = 'jumpsuitTorso'
t.pelvisModel = 'jumpsuitPelvis'
t.upperArmModel = 'jumpsuitUpperArm'
t.foreArmModel = 'jumpsuitForeArm'
t.handModel = 'jumpsuitHand'
t.upperLegModel = 'jumpsuitUpperLeg'
t.lowerLegModel = 'jumpsuitLowerLeg'
t.toesModel = 'jumpsuitToes'

jumpsuitSounds = ['jumpsuit1',
                  'jumpsuit2',
                  'jumpsuit3',
                  'jumpsuit4']

jumpsuitHitSounds = ['jumpsuitHit1',
                     'jumpsuitHit2']

t.attackSounds = jumpsuitSounds
t.jumpSounds = jumpsuitSounds
t.impactSounds = jumpsuitHitSounds
t.deathSounds = ['jumpsuitDeath']
t.pickupSounds = jumpsuitSounds
t.fallSounds = ['jumpsuitFall']

t.style = 'spaz'


# Todd McBurton
t = Appearance('Todd McBurton')

t.colorTexture = 'actionHeroColor'
t.colorMaskTexture = 'actionHeroColorMask'
t.iconTexture = 'actionHeroIcon'
t.iconMaskTexture = 'actionHeroIconColorMask'

t.defaultColor = (0.3, 0.5, 0.8)
t.defaultHighlight = (1, 0, 0)

t.headModel = 'actionHeroHead'
t.torsoModel = 'actionHeroTorso'
t.pelvisModel = 'actionHeroPelvis'
t.upperArmModel = 'actionHeroUpperArm'
t.foreArmModel = 'actionHeroForeArm'
t.handModel = 'actionHeroHand'
t.upperLegModel = 'actionHeroUpperLeg'
t.lowerLegModel = 'actionHeroLowerLeg'
t.toesModel = 'actionHeroToes'

actionHeroSounds = ['actionHero1',
                    'actionHero2',
                    'actionHero3',
                    'actionHero4']

actionHeroHitSounds = ['actionHeroHit1',
                       'actionHeroHit2']

t.attackSounds = actionHeroSounds
t.jumpSounds = actionHeroSounds
t.impactSounds = actionHeroHitSounds
t.deathSounds = ['actionHeroDeath']
t.pickupSounds = actionHeroSounds
t.fallSounds = ['actionHeroFall']

t.style = 'spaz'


# Zola
t = Appearance('Zola')

t.colorTexture = 'assassinColor'
t.colorMaskTexture = 'assassinColorMask'
t.iconTexture = 'assassinIcon'
t.iconMaskTexture = 'assassinIconColorMask'

t.defaultColor = (0.3, 0.5, 0.8)
t.defaultHighlight = (1, 0, 0)

t.headModel = 'assassinHead'
t.torsoModel = 'assassinTorso'
t.pelvisModel = 'assassinPelvis'
t.upperArmModel = 'assassinUpperArm'
t.foreArmModel = 'assassinForeArm'
t.handModel = 'assassinHand'
t.upperLegModel = 'assassinUpperLeg'
t.lowerLegModel = 'assassinLowerLeg'
t.toesModel = 'assassinToes'

assassinSounds = ['assassin1',
                  'assassin2',
                  'assassin3',
                  'assassin4']

assassinHitSounds = ['assassinHit1',
                     'assassinHit2']

t.attackSounds = assassinSounds
t.jumpSounds = assassinSounds
t.impactSounds = assassinHitSounds
t.deathSounds = ['assassinDeath']
t.pickupSounds = assassinSounds
t.fallSounds = ['assassinFall']

t.style = 'spaz'


# Grumbledorf
t = Appearance('Grumbledorf')

t.colorTexture = 'wizardColor'
t.colorMaskTexture = 'wizardColorMask'
t.iconTexture = 'wizardIcon'
t.iconMaskTexture = 'wizardIconColorMask'

t.defaultColor = (0.2, 0.4, 1.0)
t.defaultHighlight = (0.06, 0.15, 0.4)

t.headModel = 'wizardHead'
t.torsoModel = 'wizardTorso'
t.pelvisModel = 'wizardPelvis'
t.upperArmModel = 'wizardUpperArm'
t.foreArmModel = 'wizardForeArm'
t.handModel = 'wizardHand'
t.upperLegModel = 'wizardUpperLeg'
t.lowerLegModel = 'wizardLowerLeg'
t.toesModel = 'wizardToes'

wizardSounds = ['wizard1',
                'wizard2',
                'wizard3',
                'wizard4']

wizardHitSounds = ['wizardHit1',
                   'wizardHit2']

t.attackSounds = wizardSounds
t.jumpSounds = wizardSounds
t.impactSounds = wizardHitSounds
t.deathSounds = ['wizardDeath']
t.pickupSounds = wizardSounds
t.fallSounds = ['wizardFall']

t.style = 'spaz'


# Butch
t = Appearance('Butch')

t.colorTexture = 'cowboyColor'
t.colorMaskTexture = 'cowboyColorMask'
t.iconTexture = 'cowboyIcon'
t.iconMaskTexture = 'cowboyIconColorMask'

t.defaultColor = (0.3, 0.5, 0.8)
t.defaultHighlight = (1, 0, 0)

t.headModel = 'cowboyHead'
t.torsoModel = 'cowboyTorso'
t.pelvisModel = 'cowboyPelvis'
t.upperArmModel = 'cowboyUpperArm'
t.foreArmModel = 'cowboyForeArm'
t.handModel = 'cowboyHand'
t.upperLegModel = 'cowboyUpperLeg'
t.lowerLegModel = 'cowboyLowerLeg'
t.toesModel = 'cowboyToes'

cowboySounds = ['cowboy1',
                'cowboy2',
                'cowboy3',
                'cowboy4']

cowboyHitSounds = ['cowboyHit1',
                   'cowboyHit2']

t.attackSounds = cowboySounds
t.jumpSounds = cowboySounds
t.impactSounds = cowboyHitSounds
t.deathSounds = ['cowboyDeath']
t.pickupSounds = cowboySounds
t.fallSounds = ['cowboyFall']

t.style = 'spaz'


# Witch
t = Appearance('Witch')

t.colorTexture = 'witchColor'
t.colorMaskTexture = 'witchColorMask'
t.iconTexture = 'witchIcon'
t.iconMaskTexture = 'witchIconColorMask'

t.defaultColor = (0.3, 0.5, 0.8)
t.defaultHighlight = (1, 0, 0)

t.headModel = 'witchHead'
t.torsoModel = 'witchTorso'
t.pelvisModel = 'witchPelvis'
t.upperArmModel = 'witchUpperArm'
t.foreArmModel = 'witchForeArm'
t.handModel = 'witchHand'
t.upperLegModel = 'witchUpperLeg'
t.lowerLegModel = 'witchLowerLeg'
t.toesModel = 'witchToes'

witchSounds = ['witch1',
               'witch2',
               'witch3',
               'witch4']

witchHitSounds = ['witchHit1',
                  'witchHit2']

t.attackSounds = witchSounds
t.jumpSounds = witchSounds
t.impactSounds = witchHitSounds
t.deathSounds = ['witchDeath']
t.pickupSounds = witchSounds
t.fallSounds = ['witchFall']

t.style = 'spaz'


# Warrior
t = Appearance('Warrior')

t.colorTexture = 'warriorColor'
t.colorMaskTexture = 'warriorColorMask'
t.iconTexture = 'warriorIcon'
t.iconMaskTexture = 'warriorIconColorMask'

t.defaultColor = (0.3, 0.5, 0.8)
t.defaultHighlight = (1, 0, 0)

t.headModel = 'warriorHead'
t.torsoModel = 'warriorTorso'
t.pelvisModel = 'warriorPelvis'
t.upperArmModel = 'warriorUpperArm'
t.foreArmModel = 'warriorForeArm'
t.handModel = 'warriorHand'
t.upperLegModel = 'warriorUpperLeg'
t.lowerLegModel = 'warriorLowerLeg'
t.toesModel = 'warriorToes'

warriorSounds = ['warrior1',
                 'warrior2',
                 'warrior3',
                 'warrior4']

warriorHitSounds = ['warriorHit1',
                    'warriorHit2']

t.attackSounds = warriorSounds
t.jumpSounds = warriorSounds
t.impactSounds = warriorHitSounds
t.deathSounds = ['warriorDeath']
t.pickupSounds = warriorSounds
t.fallSounds = ['warriorFall']

t.style = 'spaz'


# Middle-Man
t = Appearance('Middle-Man')

t.colorTexture = 'superheroColor'
t.colorMaskTexture = 'superheroColorMask'
t.iconTexture = 'superheroIcon'
t.iconMaskTexture = 'superheroIconColorMask'

t.defaultColor = (0.3, 0.5, 0.8)
t.defaultHighlight = (1, 0, 0)

t.headModel = 'superheroHead'
t.torsoModel = 'superheroTorso'
t.pelvisModel = 'superheroPelvis'
t.upperArmModel = 'superheroUpperArm'
t.foreArmModel = 'superheroForeArm'
t.handModel = 'superheroHand'
t.upperLegModel = 'superheroUpperLeg'
t.lowerLegModel = 'superheroLowerLeg'
t.toesModel = 'superheroToes'

superheroSounds = ['superhero1',
                   'superhero2',
                   'superhero3',
                   'superhero4']

superheroHitSounds = ['superheroHit1',
                      'superheroHit2']

t.attackSounds = superheroSounds
t.jumpSounds = superheroSounds
t.impactSounds = superheroHitSounds
t.deathSounds = ['superheroDeath']
t.pickupSounds = superheroSounds
t.fallSounds = ['superheroFall']

t.style = 'spaz'


# Alien
t = Appearance('Alien')

t.colorTexture = 'alienColor'
t.colorMaskTexture = 'alienColorMask'
t.iconTexture = 'alienIcon'
t.iconMaskTexture = 'alienIconColorMask'

t.defaultColor = (0.3, 0.5, 0.8)
t.defaultHighlight = (1, 0, 0)

t.headModel = 'alienHead'
t.torsoModel = 'alienTorso'
t.pelvisModel = 'alienPelvis'
t.upperArmModel = 'alienUpperArm'
t.foreArmModel = 'alienForeArm'
t.handModel = 'alienHand'
t.upperLegModel = 'alienUpperLeg'
t.lowerLegModel = 'alienLowerLeg'
t.toesModel = 'alienToes'

alienSounds = ['alien1',
               'alien2',
               'alien3',
               'alien4']

alienHitSounds = ['alienHit1',
                  'alienHit2']

t.attackSounds = alienSounds
t.jumpSounds = alienSounds
t.impactSounds = alienHitSounds
t.deathSounds = ['alienDeath']
t.pickupSounds = alienSounds
t.fallSounds = ['alienFall']

t.style = 'spaz'


# OldLady
t = Appearance('OldLady')

t.colorTexture = 'oldLadyColor'
t.colorMaskTexture = 'oldLadyColorMask'
t.iconTexture = 'oldLadyIcon'
t.iconMaskTexture = 'oldLadyIconColorMask'

t.defaultColor = (0.3, 0.5, 0.8)
t.defaultHighlight = (1, 0, 0)

t.headModel = 'oldLadyHead'
t.torsoModel = 'oldLadyTorso'
t.pelvisModel = 'oldLadyPelvis'
t.upperArmModel = 'oldLadyUpperArm'
t.foreArmModel = 'oldLadyForeArm'
t.handModel = 'oldLadyHand'
t.upperLegModel = 'oldLadyUpperLeg'
t.lowerLegModel = 'oldLadyLowerLeg'
t.toesModel = 'oldLadyToes'

oldLadySounds = ['oldLady1',
                 'oldLady2',
                 'oldLady3',
                 'oldLady4']

oldLadyHitSounds = ['oldLadyHit1',
                    'oldLadyHit2']

t.attackSounds = oldLadySounds
t.jumpSounds = oldLadySounds
t.impactSounds = oldLadyHitSounds
t.deathSounds = ['oldLadyDeath']
t.pickupSounds = oldLadySounds
t.fallSounds = ['oldLadyFall']

t.style = 'spaz'


# Gladiator
t = Appearance('Gladiator')

t.colorTexture = 'gladiatorColor'
t.colorMaskTexture = 'gladiatorColorMask'
t.iconTexture = 'gladiatorIcon'
t.iconMaskTexture = 'gladiatorIconColorMask'

t.defaultColor = (0.3, 0.5, 0.8)
t.defaultHighlight = (1, 0, 0)

t.headModel = 'gladiatorHead'
t.torsoModel = 'gladiatorTorso'
t.pelvisModel = 'gladiatorPelvis'
t.upperArmModel = 'gladiatorUpperArm'
t.foreArmModel = 'gladiatorForeArm'
t.handModel = 'gladiatorHand'
t.upperLegModel = 'gladiatorUpperLeg'
t.lowerLegModel = 'gladiatorLowerLeg'
t.toesModel = 'gladiatorToes'

gladiatorSounds = ['gladiator1',
                   'gladiator2',
                   'gladiator3',
                   'gladiator4']

gladiatorHitSounds = ['gladiatorHit1',
                      'gladiatorHit2']

t.attackSounds = gladiatorSounds
t.jumpSounds = gladiatorSounds
t.impactSounds = gladiatorHitSounds
t.deathSounds = ['gladiatorDeath']
t.pickupSounds = gladiatorSounds
t.fallSounds = ['gladiatorFall']

t.style = 'spaz'


# Wrestler
t = Appearance('Wrestler')

t.colorTexture = 'wrestlerColor'
t.colorMaskTexture = 'wrestlerColorMask'
t.iconTexture = 'wrestlerIcon'
t.iconMaskTexture = 'wrestlerIconColorMask'

t.defaultColor = (0.3, 0.5, 0.8)
t.defaultHighlight = (1, 0, 0)

t.headModel = 'wrestlerHead'
t.torsoModel = 'wrestlerTorso'
t.pelvisModel = 'wrestlerPelvis'
t.upperArmModel = 'wrestlerUpperArm'
t.foreArmModel = 'wrestlerForeArm'
t.handModel = 'wrestlerHand'
t.upperLegModel = 'wrestlerUpperLeg'
t.lowerLegModel = 'wrestlerLowerLeg'
t.toesModel = 'wrestlerToes'

wrestlerSounds = ['wrestler1',
                  'wrestler2',
                  'wrestler3',
                  'wrestler4']

wrestlerHitSounds = ['wrestlerHit1',
                     'wrestlerHit2']

t.attackSounds = wrestlerSounds
t.jumpSounds = wrestlerSounds
t.impactSounds = wrestlerHitSounds
t.deathSounds = ['wrestlerDeath']
t.pickupSounds = wrestlerSounds
t.fallSounds = ['wrestlerFall']

t.style = 'spaz'


# Gretel
t = Appearance('Gretel')

t.colorTexture = 'operaSingerColor'
t.colorMaskTexture = 'operaSingerColorMask'
t.iconTexture = 'operaSingerIcon'
t.iconMaskTexture = 'operaSingerIconColorMask'

t.defaultColor = (0.3, 0.5, 0.8)
t.defaultHighlight = (1, 0, 0)

t.headModel = 'operaSingerHead'
t.torsoModel = 'operaSingerTorso'
t.pelvisModel = 'operaSingerPelvis'
t.upperArmModel = 'operaSingerUpperArm'
t.foreArmModel = 'operaSingerForeArm'
t.handModel = 'operaSingerHand'
t.upperLegModel = 'operaSingerUpperLeg'
t.lowerLegModel = 'operaSingerLowerLeg'
t.toesModel = 'operaSingerToes'

operaSingerSounds = ['operaSinger1',
                     'operaSinger2',
                     'operaSinger3',
                     'operaSinger4']

operaSingerHitSounds = ['operaSingerHit1',
                        'operaSingerHit2']

t.attackSounds = operaSingerSounds
t.jumpSounds = operaSingerSounds
t.impactSounds = operaSingerHitSounds
t.deathSounds = ['operaSingerDeath']
t.pickupSounds = operaSingerSounds
t.fallSounds = ['operaSingerFall']

t.style = 'spaz'


# Pixel
t = Appearance('Pixel')

t.colorTexture = 'pixieColor'
t.colorMaskTexture = 'pixieColorMask'
t.iconTexture = 'pixieIcon'
t.iconMaskTexture = 'pixieIconColorMask'

t.defaultColor = (0, 1, 0.7)
t.defaultHighlight = (0.65, 0.35, 0.75)

t.headModel = 'pixieHead'
t.torsoModel = 'pixieTorso'
t.pelvisModel = 'pixiePelvis'
t.upperArmModel = 'pixieUpperArm'
t.foreArmModel = 'pixieForeArm'
t.handModel = 'pixieHand'
t.upperLegModel = 'pixieUpperLeg'
t.lowerLegModel = 'pixieLowerLeg'
t.toesModel = 'pixieToes'

pixieSounds = ['pixie1',
               'pixie2',
               'pixie3',
               'pixie4']

pixieHitSounds = ['pixieHit1',
                  'pixieHit2']

t.attackSounds = pixieSounds
t.jumpSounds = pixieSounds
t.impactSounds = pixieHitSounds
t.deathSounds = ['pixieDeath']
t.pickupSounds = pixieSounds
t.fallSounds = ['pixieFall']

t.style = 'pixie'


# Robot
t = Appearance('Robot')

t.colorTexture = 'robotColor'
t.colorMaskTexture = 'robotColorMask'
t.iconTexture = 'robotIcon'
t.iconMaskTexture = 'robotIconColorMask'

t.defaultColor = (0.3, 0.5, 0.8)
t.defaultHighlight = (1, 0, 0)

t.headModel = 'robotHead'
t.torsoModel = 'robotTorso'
t.pelvisModel = 'robotPelvis'
t.upperArmModel = 'robotUpperArm'
t.foreArmModel = 'robotForeArm'
t.handModel = 'robotHand'
t.upperLegModel = 'robotUpperLeg'
t.lowerLegModel = 'robotLowerLeg'
t.toesModel = 'robotToes'

robotSounds = ['robot1',
               'robot2',
               'robot3',
               'robot4']

robotHitSounds = ['robotHit1',
                  'robotHit2']

t.attackSounds = robotSounds
t.jumpSounds = robotSounds
t.impactSounds = robotHitSounds
t.deathSounds = ['robotDeath']
t.pickupSounds = robotSounds
t.fallSounds = ['robotFall']

t.style = 'spaz'


# Easter Bunny
t = Appearance('Easter Bunny')

t.colorTexture = 'bunnyColor'
t.colorMaskTexture = 'bunnyColorMask'
t.iconTexture = 'bunnyIcon'
t.iconMaskTexture = 'bunnyIconColorMask'

t.defaultColor = (1, 1, 1)
t.defaultHighlight = (1, 0.5, 0.5)

t.headModel = 'bunnyHead'
t.torsoModel = 'bunnyTorso'
t.pelvisModel = 'bunnyPelvis'
t.upperArmModel = 'bunnyUpperArm'
t.foreArmModel = 'bunnyForeArm'
t.handModel = 'bunnyHand'
t.upperLegModel = 'bunnyUpperLeg'
t.lowerLegModel = 'bunnyLowerLeg'
t.toesModel = 'bunnyToes'

bunnySounds = ['bunny1',
               'bunny2',
               'bunny3',
               'bunny4']

bunnyHitSounds = ['bunnyHit1',
                  'bunnyHit2']

t.attackSounds = bunnySounds
t.jumpSounds = ['bunnyJump']
t.impactSounds = bunnyHitSounds
t.deathSounds = ['bunnyDeath']
t.pickupSounds = bunnySounds
t.fallSounds = ['bunnyFall']

t.style = 'bunny'


# BombDash characters
# Deadpool
t = Appearance('Deadpool')

t.colorTexture = 'DPColor'
t.colorMaskTexture = 'DPColorMask'
t.iconTexture = 'DPIconColor'
t.iconMaskTexture = 'DPIconColorMask'

t.defaultColor = (1, 0.1, 0.1)
t.defaultHighlight = (0.1, 0.1, 0.1)

t.headModel = 'DPHead'
t.torsoModel = 'DPTorso'
t.pelvisModel = 'DPPelvis'
t.upperArmModel = 'DPUpperArm'
t.foreArmModel = 'DPForeArm'
t.handModel = 'DPHand'
t.upperLegModel = 'DPUpperLeg'
t.lowerLegModel = 'DPLowerLeg'
t.toesModel = 'DPToes'

DPSounds = ['DP1',
            'DP2',
            'DP3',
            'DP4']

DPHitSounds = ['DPHit1',
               'DPHit2']

t.attackSounds = DPSounds
t.jumpSounds = ['DP1']
t.impactSounds = DPSounds
t.deathSounds = ['DPDeath']
t.pickupSounds = DPSounds
t.fallSounds = ['DPFall']

t.style = 'agent'


# Bombman
t = Appearance('Bombman')

t.colorTexture = 'BombmanColor'
t.colorMaskTexture = 'BombmanColorMask'
t.iconTexture = 'BombmanIcon'
t.iconMaskTexture = 'BombmanIconMask'

t.defaultColor = (1, 1, 1)
t.defaultHighlight = (1, 0.5, 0.5)

t.headModel = 'BombmanHead'
t.torsoModel = 'BombmanTorso'
t.pelvisModel = 'BombmanPelvis'
t.upperArmModel = 'BombmanUpperArm'
t.foreArmModel = 'BombmanForeArm'
t.handModel = 'BombmanHand'
t.upperLegModel = 'BombmanUpperLeg'
t.lowerLegModel = 'BombmanLowerLeg'
t.toesModel = 'BombmanToes'

BombmanSounds = ['Bombman1',
                 'Bombman2',
                 'Bombman3',
                 'Bombman4']

BombmanHitSounds = ['BombmanHit1',
                    'BombmanHit2']

t.attackSounds = BombmanHitSounds
t.jumpSounds = BombmanSounds
t.impactSounds = BombmanSounds
t.deathSounds = ['BombmanDeath']
t.pickupSounds = BombmanSounds
t.fallSounds = ['BombmanFall']

t.style = 'agent'


# Impact
t = Appearance('Impact')

t.colorTexture = 'zoeColor'
t.colorMaskTexture = 'impactBombColorLit'
t.iconTexture = 'powerupImpactBombs'
t.iconMaskTexture = 'powerupImpactBombs'

t.defaultColor = (0.6, 0.6, 0.6)
t.defaultHighlight = (0, 1, 0)

t.headModel = 'impactBomb'
t.torsoModel = 'impactTorso'
t.pelvisModel = 'impactPelvis'
t.upperArmModel = 'impactUpperArm'
t.foreArmModel = 'impactForeArm'
t.handModel = 'impactHand'
t.upperLegModel = 'impactUpperLeg'
t.lowerLegModel = 'impactLowerLeg'
t.toesModel = 'impactToes'

t.jumpSounds = ['activateBeep']
t.attackSounds = ['LightTurnOn']
t.impactSounds = ['activateBeep']
t.deathSounds = ['impactHard']
t.fallSounds = ['laser']

t.style = 'cyborg'


# Zombie
t = Appearance('Zombie')

t.colorTexture = 'agentColor'
t.colorMaskTexture = 'pixieColorMask'
t.iconTexture = 'powerupCurse'
t.iconMaskTexture = 'powerupCurse'

t.defaultColor = (0.6, 0.6, 0.6)
t.defaultHighlight = (0, 1, 0)

t.headModel = 'zoeHead'
t.torsoModel = 'bonesTorso'
t.pelvisModel = 'pixiePelvis'
t.upperArmModel = 'frostyUpperArm'
t.foreArmModel = 'frostyForeArm'
t.handModel = 'bonesHand'
t.upperLegModel = 'bonesUpperLeg'
t.lowerLegModel = 'pixieLowerLeg'
t.toesModel = 'bonesToes'

kronkSounds = ['kronk1',
               'kronk2',
               'kronk3',
               'kronk4',
               'kronk5',
               'kronk6',
               'kronk7',
               'kronk8',
               'kronk9',
               'kronk10']

t.jumpSounds = kronkSounds
t.attackSounds = kronkSounds
t.impactSounds = kronkSounds
t.deathSounds = ['kronkDeath']
t.pickupSounds = kronkSounds
t.fallSounds = ['kronkFall']

t.style = 'spaz'


# Monkey
t = Appearance('Monkey')

t.colorTexture = 'monkeyColor'
t.colorMaskTexture = 'monkeyColorMask'
t.iconTexture = 'monkeyIcon'
t.iconMaskTexture = 'monkeyIconColorMask'

t.defaultColor = (0.6, 0.6, 0.6)
t.defaultHighlight = (0, 1, 0)

t.headModel = 'monkeyHead'
t.torsoModel = 'monkeyTorso'
t.pelvisModel = 'monkeyPelvis'
t.upperArmModel = 'monkeyUpperArm'
t.foreArmModel = 'monkeyForeArm'
t.handModel = 'monkeyHand'
t.upperLegModel = 'monkeyUpperLeg'
t.lowerLegModel = 'monkeyLowerLeg'
t.toesModel = 'monkeyToes'

monkeySounds = ['monkey1']
t.jumpSounds = monkeySounds
t.attackSounds = ['monkeyHit']
t.impactSounds = monkeySounds
t.deathSounds = ['monkeyDeath']
t.fallSounds = ['monkeyFall']

t.pickupSounds = ['kukuPickup01',
                  'kukuPickup02']

t.style = 'agent'


# Kukusik
t = Appearance('Kukusik')

t.colorTexture = 'kukusikColor'
t.colorMaskTexture = 'kukusikColorMask'
t.iconTexture = 'kukusikIcon'
t.iconMaskTexture = 'kukusikIconColorMask'

t.defaultColor = (0.6, 0.6, 0.6)
t.defaultHighlight = (0, 1, 0)

t.headModel = 'empty'
t.torsoModel = 'kukusikTorso'
t.pelvisModel = 'empty'
t.upperArmModel = 'empty'
t.foreArmModel = 'empty'
t.handModel = 'monkeyHand'
t.upperLegModel = 'empty'
t.lowerLegModel = 'empty'
t.toesModel = 'monkeyToes'

kukuSounds = ['kukuHit01',
              'kukuHit02',
              'kukuHit03',
              'kukuHit04']

t.jumpSounds = kukuSounds
t.attackSounds = kukuSounds
t.impactSounds = kukuSounds
t.deathSounds = ['kukuDeath']
t.fallSounds = ['kukuDeath']

t.style = 'agent'


# Eric by TROLLMAN
t = Appearance('Eric')

t.colorTexture = 'ericColor'
t.colorMaskTexture = 'black'
t.iconTexture = 'ericAva'
t.iconMaskTexture = 'black'

t.defaultColor = (0.3, 0.3, 0.33)
t.defaultHighlight = (1, 0.5, 0.3)

t.headModel = 'ericHead'
t.torsoModel = 'ericTorso'
t.pelvisModel = 'ericPelvis'
t.upperArmModel = 'ericUpperArm'
t.foreArmModel = 'ericForeArm'
t.handModel = 'ericHand'
t.upperLegModel = 'ericUpperLeg'
t.lowerLegModel = 'ericLowerLeg'
t.toesModel = 'ericToes'

ericSounds = ['eric1',
              'eric2',
              'eric3']

ericHitSounds = ['ericHit1',
                 'ericHit2']

t.attackSounds = ericSounds
t.jumpSounds = ericSounds
t.impactSounds = ericHitSounds
t.deathSounds = ['ericDeath']
t.pickupSounds = ericSounds
t.fallSounds = ['ericFall']

t.style = 'agent'


# Pikachu by Fearless Cuber
t = Appearance('Pikachu')

t.colorTexture = 'pikatex'
t.colorMaskTexture = 'pikamasktex'
t.iconTexture = 'pikachuicon'
t.iconMaskTexture = 'pikaiconmask2'

t.defaultColor = (1, 0.3, 0.3)
t.defaultHighlight = (1, 0.3, 0.3)

t.headModel = 'pikachuHead'
t.torsoModel = 'pikachuTorso'
t.pelvisModel = 'pikachuPelvis'
t.upperArmModel = 'pikachuUpperArm'
t.foreArmModel = 'pikachuForeArm'
t.handModel = 'pikachuHand'
t.upperLegModel = 'pikachuUpperLeg'
t.lowerLegModel = 'pikachuLowerLeg'
t.toesModel = 'pikachuToes'

pikachuSounds = ['pikachu_1',
                 'pikachu_2',
                 'pikachu_3',
                 'pikachu_4']

pikachuHitSounds = ['pikachuhit',
                    'pikachuhit2']

t.attackSounds = pikachuSounds
t.jumpSounds = pikachuSounds
t.impactSounds = pikachuHitSounds
t.deathSounds = ['pikachudeath']
t.pickupSounds = pikachuSounds
t.fallSounds = ['pikachufall']

t.style = 'agent'


# Pig by TROLLMAN
t = Appearance('Hrundel')

t.colorTexture = 'pigColor'
t.colorMaskTexture = 'pigColorMask'
t.iconTexture = 'pigIcon'
t.iconMaskTexture = 'pigIconColorMask'

t.defaultColor = (1, 1, 1)
t.defaultHighlight = (1, 0.5, 0.5)

t.headModel = 'pigHead'
t.torsoModel = 'pigTorso'
t.pelvisModel = 'pigPelvis'
t.upperArmModel = 'pigUpperArm'
t.foreArmModel = 'pigForeArm'
t.handModel = 'pigHand'
t.upperLegModel = 'pigUpperLeg'
t.lowerLegModel = 'pigLowerLeg'
t.toesModel = 'pigToes'

pigSounds = ['pig1',
             'pig2',
             'pig3',
             'pig4']

pigHitSounds = ['pigHit1',
                'pigHit2']

t.attackSounds = pigHitSounds
t.jumpSounds = pigSounds
t.impactSounds = pigHitSounds
t.deathSounds = ['pigDeath']
t.pickupSounds = pigSounds
t.fallSounds = ['pigFall']

t.style = 'bear'


# Bolt
t = Appearance('Bolt')

t.colorTexture = 'bolt'
t.colorMaskTexture = 'black'
t.iconTexture = 'boltIcon'
t.iconMaskTexture = 'black'

t.defaultColor = (1, 1, 1)
t.defaultHighlight = (1, 0.5, 0.5)

t.headModel = 'boltHead'
t.torsoModel = 'boltTorso'
t.pelvisModel = 'empty'
t.upperArmModel = 'empty'
t.foreArmModel = 'empty'
t.handModel = 'pigHand'
t.upperLegModel = 'empty'
t.lowerLegModel = 'empty'
t.toesModel = 'neoSpazToes'

boltSounds = ['boltHit1',
              'boltHit2',
              'boltHit3']

t.attackSounds = boltSounds
t.jumpSounds = ['boltJump2']
t.impactSounds = boltSounds
t.deathSounds = ['boltDeath']
t.pickupSounds = boltSounds
t.fallSounds = ['boltFall']

t.style = 'spaz'


# Jack The Bum (rus Dimon) by TROLLMAN
t = Appearance('Bum')

t.colorTexture = 'bomzhColor'
t.colorMaskTexture = 'black'
t.iconTexture = 'bumIcon'
t.iconMaskTexture = 'black'

t.defaultColor = (1, 0.2, 0.3)
t.defaultHighlight = (1, 1, 0.2)

t.headModel = 'jackHead'
t.torsoModel = 'jackTorso'
t.pelvisModel = 'pixiePelvis'
t.upperArmModel = 'jackUpperArm'
t.foreArmModel = 'jackForeArm'
t.handModel = 'jackHand'
t.upperLegModel = 'jackUpperLeg'
t.lowerLegModel = 'jackLowerLeg'
t.toesModel = 'kronkToes'

if settings.badWords:
    t.attackSounds = ['bumHit1',
                      'bumHit2',
                      'bumHit3',
                      'bumHit4',
                      'bumHit5']

    t.jumpSounds = ['bumHit2',
                    'bumJump',
                    'bumHit4',
                    'bumHit5',
                    'bumHit6']

    t.impactSounds = ['bumHit2',
                      'bumJump',
                      'bumHit6',
                      'bumImpact1',
                      'bumImpact2']

    t.deathSounds = ['bumDeath1',
                     'bumDeath2',
                     'bumDeath3',
                     'bumDeath4',
                     'bumDeath6']

    t.pickupSounds = ['bumPickup2',
                      'bumPickup1',
                      'bumPickup3']

    t.fallSounds = ['bumDeath1',
                    'bumDeath2',
                    'bumDeath3',
                    'bumDeath4',
                    'bumDeath6']
else:
    hitSounds = ['jackHit01',
                 'jackHit02',
                 'jackHit03',
                 'jackHit04',
                 'jackHit05',
                 'jackHit06',
                 'jackHit07']

    sounds = ['jack01',
              'jack02',
              'jack03',
              'jack04',
              'jack05',
              'jack06']

    t.attackSounds = sounds
    t.jumpSounds = sounds
    t.impactSounds = hitSounds
    t.deathSounds = ['jackDeath01']
    t.pickupSounds = sounds
    t.fallSounds = ['jackFall01']

t.style = 'pirate'


# Elf by TROLLMAN
t = Appearance('Elf')

t.colorTexture = 'elfColor'
t.colorMaskTexture = 'elfColorMask'
t.iconTexture = 'elfPreviev'
t.iconMaskTexture = 'elfIconColorMask'

t.defaultColor = (0.1, 0.6, 0.33)
t.defaultHighlight = (0.7, 0.1, 0.1)

t.headModel = 'elfHead'
t.torsoModel = 'elfTorso'
t.pelvisModel = 'elfPelvis'
t.upperArmModel = 'elfUpperArm'
t.foreArmModel = 'elfForeArm'
t.handModel = 'elfHand'
t.upperLegModel = 'elfUpperLeg'
t.lowerLegModel = 'elfLowerLeg'
t.toesModel = 'elfToes'

elfSounds = ['elf1',
             'elf2',
             'elf3',
             'elf4']

elfHitSounds = ['elfHit1',
                'elfHit2']

t.attackSounds = elfSounds
t.jumpSounds = elfSounds
t.impactSounds = elfHitSounds
t.deathSounds = ['elfDeath']
t.pickupSounds = elfSounds
t.fallSounds = ['elfFall']

t.style = 'santa'


# Android by TROLLMAN
t = Appearance('Android')

t.colorTexture = 'androidColor'
t.colorMaskTexture = 'androidColorMask'
t.iconTexture = 'androidIcon'
t.iconMaskTexture = 'androidIconMask'

t.defaultColor = (0.732, 1.13, 0.08)
t.defaultHighlight = (-1, -1, -1)

t.headModel = 'androidHead'
t.torsoModel = 'androidTorso'
t.pelvisModel = 'empty'
t.upperArmModel = 'androidUpperArm'
t.foreArmModel = 'empty'
t.handModel = 'empty'
t.upperLegModel = 'androidUpperLeg'
t.lowerLegModel = 'empty'
t.toesModel = 'empty'

androidSounds = ['android1',
                 'android2',
                 'android3',
                 'android4']

androidHitSounds = ['androidHit1',
                    'androidHit2']

t.attackSounds = androidSounds
t.jumpSounds = androidSounds
t.impactSounds = androidHitSounds
t.deathSounds = ['androidDeath']
t.pickupSounds = androidSounds
t.fallSounds = ['androidFall']

t.style = 'cyborg'


# S-117 by Plasma Boson
t = Appearance('S-117')

t.colorTexture = 'warriorColor'
t.colorMaskTexture = 'warriorColorMask'
t.iconTexture = 'warriorIcon'
t.iconMaskTexture = 'warriorIconColorMask'

t.defaultColor = (0.55, 0.55, 0.55)
t.defaultHighlight = (0.5, 0.5, 0.5)

t.headModel = 'warriorHead'
t.torsoModel = 'warriorTorso'
t.pelvisModel = 'empty'
t.upperArmModel = 'warriorUpperArm'
t.foreArmModel = 'warriorForeArm'
t.handModel = 'warriorHand'
t.upperLegModel = 'warriorUpperLeg'
t.lowerLegModel = 'warriorLowerLeg'
t.toesModel = 'warriorToes'

t.jumpSounds = ['warrior1',
                'warrior2',
                'warrior3']

t.attackSounds = ['warrior1',
                  'warrior2',
                  'warrior3']

t.impactSounds = ['warriorHit1',
                  'warriorHit2']

t.deathSounds = ['warriorDeath',
                 'warrior4']

t.pickupSounds = ['warrior3']

t.fallSounds = ['warriorDeath',
                'warrior4',
                'warriorFall']

t.style = 'agent'


# Knuckles
t = Appearance('Knuckles')

t.colorTexture = 'knucklesColor'
t.colorMaskTexture = 'black'
t.iconTexture = 'knucklesIcon'
t.iconMaskTexture = 'black'

t.defaultColor = (1, 0.1, 0.1)
t.defaultHighlight = (1, 1, 1)

t.headModel = 'knucklesHead'
t.torsoModel = 'knucklesTorso'
t.pelvisModel = 'empty'
t.upperArmModel = 'empty'
t.foreArmModel = 'empty'
t.handModel = 'empty'
t.upperLegModel = 'empty'
t.lowerLegModel = 'empty'
t.toesModel = 'empty'

t.jumpSounds = ['knuckles1',
                'knuckles2',
                'knuckles3']

t.attackSounds = ['knuckles1',
                  'knuckles2',
                  'knuckles3']

t.impactSounds = ['knuckleshit1',
                  'knuckleshit2']

t.deathSounds = ['knucklesDeath']
t.pickupSounds = ['knuckles1']
t.fallSounds = ['knucklesFall']

t.style = 'agent'


# Jason Voorhees by TROLLMAN
t = Appearance('Jason Voorhees')

t.colorTexture = 'JasonColor'
t.colorMaskTexture = 'JasonColorMask'
t.iconTexture = 'jasonIcon'
t.iconMaskTexture = 'jasonIconColorMask'

t.defaultColor = (0.45, 0.35, 0.34)
t.defaultHighlight = (0.16, 0.13, 0.32)

t.headModel = 'JasonHead'
t.torsoModel = 'jasonTorso'
t.pelvisModel = 'agentPelvis'
t.upperArmModel = 'jasonUpperArm'
t.foreArmModel = 'jasonForeArm'
t.handModel = 'agentHand'
t.upperLegModel = 'agentUpperLeg'
t.lowerLegModel = 'agentLowerLeg'
t.toesModel = 'agentToes'

agentSounds = ['Jason1',
               'Jason2',
               'Jason3']

agentSoundsAttack = ['Jason4',
                     'Jason5']

agentHitSounds = ['JasonHit1',
                  'JasonHit2']

t.attackSounds = agentSoundsAttack
t.jumpSounds = agentSounds
t.impactSounds = agentHitSounds
t.deathSounds = ['JasonDeath']
t.pickupSounds = agentSounds
t.fallSounds = ['JasonFall']

t.style = 'agent'


# Carl Jonhson by TROLLMAN
t = Appearance('Carl Jonhson')

t.colorTexture = 'cjColor'
t.colorMaskTexture = 'cjColorMask'
t.iconTexture = 'cjIconColor'
t.iconMaskTexture = 'cjIconColorMask'

t.defaultColor = (0.5, 0.5, 0.5)
t.defaultHighlight = (0.1, 0.1, 0.5)

t.headModel = 'cjHead'
t.torsoModel = 'cjTorso'
t.pelvisModel = 'cjPelvis'
t.upperArmModel = 'cjUpperArm'
t.foreArmModel = 'cjForeArm'
t.handModel = 'cjHand'
t.upperLegModel = 'cjUpperLeg'
t.lowerLegModel = 'cjLowerLeg'
t.toesModel = 'cjToes'

cjSounds = ['cj1',
            'cj2',
            'cj3']

cjHitSounds = ['cjHit1',
               'cjHit2',
               'cjHit3',
               'cjHit4',
               'cjHit5',
               'cjHit6',
               'cjHit7',
               'cjHit8']

t.attackSounds = cjSounds
t.jumpSounds = ['cjJump']
t.impactSounds = cjHitSounds
t.deathSounds = ['cjDeath']
t.pickupSounds = cjSounds
t.fallSounds = ['cjFall']

t.style = 'agent'


# Antoshko Gavriluk by TROLLMAN
t = Appearance('Antoshko Gavriluk')

t.colorTexture = 'antoshkoColor'
t.colorMaskTexture = 'antoshkoColorMask'
t.iconTexture = 'antoshkoIcon'
t.iconMaskTexture = 'antoshkoIconColorMask'

t.defaultColor = (0.4, 0.57, 0.2)
t.defaultHighlight = (1, 0.1, 0.1)

t.headModel = 'antoshkoHead'
t.torsoModel = 'antoshkoTorso'
t.pelvisModel = 'empty'
t.upperArmModel = 'antoshkoUpperArm'
t.foreArmModel = 'antoshkoForeArm'
t.handModel = 'antoshkoHand'
t.upperLegModel = 'antoshkoUpperLeg'
t.lowerLegModel = 'antoshkoLowerLeg'
t.toesModel = 'antoshkoToes'

agentSounds = ['antoshko1',
               'antoshko2',
               'antoshko3',
               'antoshko4']

agentHitSounds = ['antoshkoHit1',
                  'antoshkoHit2']

t.attackSounds = agentSounds
t.jumpSounds = agentSounds
t.impactSounds = agentHitSounds
t.deathSounds = ['antoshkoDeath']
t.pickupSounds = agentSounds
t.fallSounds = ['antoshkoFall']

t.style = 'agent'


# Dart Vader by TROLLMAN
t = Appearance('Dart Vader')

t.colorTexture = 'vaderColor'
t.colorMaskTexture = 'vaderColorMask'
t.iconTexture = 'vaderIcon'
t.iconMaskTexture = 'vaderIconColorMask'

t.defaultColor = (0.05, 0.05, 0.05)
t.defaultHighlight = (1, 0, 0)

t.headModel = 'vaderHead'
t.torsoModel = 'vaderTorso'
t.pelvisModel = 'cyborgPelvis'
t.upperArmModel = 'vaderUpperArm'
t.foreArmModel = 'vaderForeArm'
t.handModel = 'cyborgHand'
t.upperLegModel = 'cyborgUpperLeg'
t.lowerLegModel = 'cyborgLowerLeg'
t.toesModel = 'cyborgToes'

cyborgSounds = ['vader1',
                'vader2',
                'vader3',
                'vader4']

cyborgHitSounds = ['vaderHit1',
                   'vaderHit2']

t.attackSounds = cyborgSounds
t.jumpSounds = cyborgSounds
t.impactSounds = cyborgHitSounds
t.deathSounds = ['vaderDeath']
t.pickupSounds = cyborgSounds
t.fallSounds = ['vaderFall']

t.style = 'cyborg'


# Gambol
t = Appearance('Gambol')

t.colorTexture = 'gumdarColor'
t.colorMaskTexture = 'gumdarColorMask'
t.iconTexture = 'gumbolIcon'
t.iconMaskTexture = 'gumbolIconColorMask'

t.defaultColor = (0.06, 0.65, 0.78)
t.defaultHighlight = (0.66, 0.58, 0.47)

t.headModel = 'gambolHead'
t.torsoModel = 'gambolTorso'
t.pelvisModel = 'gambolPelvis'
t.upperArmModel = 'gambolUpperArm'
t.foreArmModel = 'gambolForeArm'
t.handModel = 'gambolHand'
t.upperLegModel = 'gambolUpperLeg'
t.lowerLegModel = 'gambolLowerLeg'
t.toesModel = 'gambolToes'

gambolSounds = ['gambol1',
                'gambol2',
                'gambol3']

gambolHitSounds = ['gambolHit1',
                   'gambolHit2']

t.attackSounds = gambolSounds
t.jumpSounds = gambolSounds
t.impactSounds = gambolHitSounds
t.deathSounds = ['gambolDeath',
                 'gambolDeath2']
t.pickupSounds = ['gambolPickedup']
t.fallSounds = ['gambolFall']

t.style = 'agent'

# Russian tramp
t = Appearance('Russian tramp')

t.colorTexture = 'gopnikColor'
t.colorMaskTexture = 'gopnikColorMask'
t.iconTexture = 'gopnikIcon'
t.iconMaskTexture = 'gopnikIconColorMask'

t.defaultColor = (0.40, 0.44, 0.55)
t.defaultHighlight = (0.50, 0.48, 0.44)

t.headModel = 'gopnikHead'
t.torsoModel = 'gopnikTorso'
t.pelvisModel = 'gopnikPelvis'
t.upperArmModel = 'gopnikUpperArm'
t.foreArmModel = 'gopnikForeArm'
t.handModel = 'gopnikHand'
t.upperLegModel = 'gopnikUpperLeg'
t.lowerLegModel = 'gopnikLowerLeg'
t.toesModel = 'agentToes'

if settings.badWords:
    t.attackSounds = ['gopnikHit1',
                      'gopnikHit2']

    t.jumpSounds = ['gopnik1',
                    'gopnik2',
                    'gopnik4',
                    'gopnik3']

    t.impactSounds = ['gopnikHit2',
                      'gopnikHit1',
                      'gopnik2',
                      'gopnik1',
                      'gopnik4']

    t.deathSounds = ['gopnikDeath']

    t.pickupSounds = ['gopnik1',
                      'gopnik2',
                      'gopnik4',
                      'gopnik3']

    t.fallSounds = ['gopnikFall']
else:
    sounds = ['agent1',
              'agent2',
              'agent3',
              'agent4']

    hitSounds = ['agentHit1',
                 'agentHit2']

    t.attackSounds = sounds
    t.jumpSounds = sounds
    t.impactSounds = hitSounds
    t.deathSounds = ['agentDeath']
    t.pickupSounds = sounds
    t.fallSounds = ['agentFall']

t.style = 'agent'
