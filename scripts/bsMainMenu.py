import os
import sys
import json
import urllib2
import threading
import time
import random
import weakref
import datetime
import bs
import bsUI
import bsSpaz
import bsUtils
import bsPowerup
import bsInternal
import bdUtils
import settings


# import of values from theme...
themeValues = bs.GetThemeValues.values

for i in themeValues:
    exec('%s=themeValues["%s"]' % (i, i))
################################

gDidInitialTransition = False
gFirstRun = True
gStartTime = time.time()
gModPackServers = False

JRMPmode = False
firstApril = True if datetime.datetime.now().month == 4 \
    and datetime.datetime.now().day == 1 else False

random.seed()
if random.random() > 0.7 and firstApril:
    JRMPmode = True


class MainMenuActivity(bs.Activity):

    def __init__(self, settings={}, scene=None):
        bs.Activity.__init__(self, settings)
        self.scene = scene

    def onTransitionIn(self):
        import bsInternal
        bs.Activity.onTransitionIn(self)
        global gDidInitialTransition
        random.seed(123)

        # to put the name of a modpak and its version
        global JRMPmode
        jrmpModeText = 'joi ride madpacke'
        bdtext = '1.8 Release' if not JRMPmode else jrmpModeText
        bdtext2 = 'BombDash ModPack' if not JRMPmode else jrmpModeText
        bdtext3 = 'BombSquad: %s' % bdtext2

        self._logoNode = None
        self._customLogoTexName = None
        self._wordActorsCreated = False
        self._wordActors = []
        env = bs.getEnvironment()

        # FIXME - shouldn't be doing things conditionally based on whether
        # the host is vr mode or not (clients may not be or vice versa) -
        # any differences need to happen at the engine level
        # so everyone sees things in their own optimal way
        vrMode = bs.getEnvironment()['vrMode']

        if not bs.getEnvironment().get('toolbarTest', True):
            self.imgMenu = bs.NodeActor(bs.newNode('image', attrs={
                'texture': bs.getTexture('white'),
                'position': (-350, 0),
                'opacity': 0.7,
                'hostOnly': True,
                'color': menuImgMenuColor,
                'scale': (350, 2000)}))

            self.myName = bs.NodeActor(bs.newNode('text', attrs={
                'vAttach': 'bottom',
                'hAlign': 'center',
                'color': menuEricFroemlingMenuColor,
                'flatness': 1.0,
                'shadow': 1.0 if vrMode else 0.5,
                'scale': (0.9 if (env['interfaceType'] == 'small' or vrMode)
                          else 0.7),  # FIXME need a node attr for this
                'position': (0, 10),
                'vrDepth': -10,
                'text': u'\xa9 2019 Eric Froemling'}))

        # throw up some text that only clients can see so they know that the
        # host is navigating menus while they're just staring at an
        # empty-ish screen..
        self._hostIsNavigatingText = bs.NodeActor(bs.newNode('text', attrs={
            'text': bs.Lstr(resource='hostIsNavigatingMenusText',
                            subs=[('${HOST}',
                                   bsInternal._getAccountDisplayString())]),
            'clientOnly': True,
            'position': (0, -200),
            'flatness': 1.0,
            'hAlign': 'center'}))

        self._hostGameNameText = bs.NodeActor(bs.newNode('text', attrs={
            'text': bdtext3,
            'clientOnly': True,
            'position': (0, 0),
            'flatness': 1.0,
            'vAttach': 'top',
            'vAlign': 'top',
            'hAttach': 'left',
            'hAlign': 'left'}))

        if not gDidInitialTransition and hasattr(self, 'myName'):
            bs.animate(self.myName.node, 'opacity',
                       {2300: 0, 3000: 1.0})

        # FIXME - shouldn't be doing things conditionally based on whether
        # the host is vr mode or not (clients may not be or vice versa)
        # - any differences need to happen at the engine level
        # so everyone sees things in their own optimal way
        vrMode = env['vrMode']
        interfaceType = env['interfaceType']

        # in cases where we're doing lots of dev work lets
        # always show the build number
        forceShowBuildNumber = False

        if not bs.getEnvironment().get('toolbarTest', True):
            if env['debugBuild'] or env['testBuild'] or forceShowBuildNumber:
                if env['debugBuild']:
                    text = bs.Lstr(
                        value='${V} (${B}) (${D})',
                        subs=[('${V}', env['version']),
                              ('${B}', str(env['buildNumber'])),
                              ('${D}', bs.Lstr(resource='debugText'))])
                else:
                    text = bs.Lstr(value='${V} (${B})',
                                   subs=[('${V}', env['version']),
                                         ('${B}', str(env['buildNumber']))])
            else:
                text = bs.Lstr(value='${V}', subs=[('${V}', env['version'])])

            self.version = bs.NodeActor(bs.newNode('text', attrs={
                'vAttach': 'bottom',
                'hAttach': 'right',
                'hAlign': 'right',
                'flatness': 1.0,
                'vrDepth': -10,
                'shadow': 1.0 if vrMode else 0.5,
                'color': menuBDMPVersionMenuColor,
                'scale': 0.9 if (interfaceType == 'small' or vrMode) else 0.7,
                'position': (-260, 10) if vrMode else (-10, 10),
                'text': bdtext}))

            if not gDidInitialTransition:
                bs.animate(self.version.node, 'opacity',
                           {2300: 0, 3000: 1.0})

        self.betaInfo = self.betaInfo2 = None
        if env['testBuild'] and not env['kioskMode']:
            self.betaInfo = bs.NodeActor(bs.newNode('text', attrs={
                'vAttach': 'center',
                'hAlign': 'center',
                'color': menuBDMPMenuColor,
                'shadow': 0.5,
                'flatness': 0.5,
                'hostOnly': True,
                'scale': 1.0,
                'vrDepth': -60,
                'position': (230, 125) if env['kioskMode'] else (-350, 215),
                'text': bdtext2}))

            if not gDidInitialTransition:
                bs.animate(self.betaInfo.node, 'opacity',
                           {1300: 0, 1800: 1.0})

        # create dicts in cloud
        bombDashNotInBombSquadConfig = False
        if 'BombDash Privilege' not in bs.getConfig():
            bs.getConfig()['BombDash Privilege'] = {
                'admins': [],
                'vips': [],
                'bans': []
            }

            if not bombDashNotInBombSquadConfig:
                bombDashNotInBombSquadConfig = True

        if 'BombDash Stats' not in bs.getConfig():
            bs.getConfig()['BombDash Stats'] = {
                'Kills': 0,
                'Deaths': 0,
                'Suicides': 0,
                'Betrayals': 0,
                'Bomb explosions': 0,
                'Collected powerups': 0,
                'Fatality hits': 0
            }

            if not bombDashNotInBombSquadConfig:
                bombDashNotInBombSquadConfig = True

        if 'BombDash Favorites Servers' not in bs.getConfig():
            bs.getConfig()['BombDash Favorites Servers'] = []
            if not bombDashNotInBombSquadConfig:
                bombDashNotInBombSquadConfig = True

        if 'BombDash Last Server' not in bs.getConfig():
            bs.getConfig()['BombDash Last Server'] = []
            if not bombDashNotInBombSquadConfig:
                bombDashNotInBombSquadConfig = True

        if bombDashNotInBombSquadConfig:
            bs.writeConfig()

        model = bs.getModel('thePadLevel')
        treesModel = bs.getModel('trees')
        bottomModel = bs.getModel('thePadLevelBottom')
        turretsArray = bs.getModel('turretsArray')
        turretsArrayLow = bs.getModel('turretsArrayLowQuality')
        collide = bs.getCollideModel('thePadLevelCollide')
        treesTexture = bs.getTexture('treesColor')
        testColorTexture = bs.getTexture('thePadLevelColor')

        import bsMap
        self._map = bsMap.ThePadMap
        self._map.isHockey = False

        pumpkinsBottom = bs.getModel('pumpkinsBottom')
        pumkinsTex = bs.getTexture('pumpkins')
        pumkinsBottomTex = bs.getTexture('pumpkinsBottom')

        bgModel = bs.getModel('thePadBG')
        bgTex = bs.getTexture('menuBG')

        # (load these last since most platforms don't use them..)
        vrBottomFillModel = bs.getModel('thePadVRFillBottom')
        vrTopFillModel = bs.getModel('thePadVRFillTop')

        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.cameraMode = 'rotate'

        random.seed()

        # menu scenes code, oh yeah
        self.color = (0.92, 0.91, 0.9)  # bg color
        if self.scene is not None:
            startEvent = self.scene
        else:
            # do not needs to select special scenes,
            # if this is not their time
            m = settings.scenes
            if not bsUI.gNewYear and 15 in settings.scenes:
                m = list(set(m)-set([15]))

            if not bsUI.gHalloween and 14 in settings.scenes:
                m = list(set(m)-set([14]))

            if len(m) > 0 and not JRMPmode:
                startEvent = random.choice(m)
            elif JRMPmode:
                startEvent = 998  # JRMP mode
            else:
                startEvent = 999  # standart BombSquad menu

        # create data for a menu scene with Ricardo Milos
        milosModel = bs.getModel('milos')
        mil0 = pumkinsTex = bs.getTexture('mil0')
        mil1 = pumkinsTex = bs.getTexture('mil1')
        mil2 = pumkinsTex = bs.getTexture('mil2')
        mil3 = pumkinsTex = bs.getTexture('mil3')
        mil4 = pumkinsTex = bs.getTexture('mil4')
        mil5 = pumkinsTex = bs.getTexture('mil5')
        mil6 = pumkinsTex = bs.getTexture('mil6')
        mil7 = pumkinsTex = bs.getTexture('mil7')
        mil8 = pumkinsTex = bs.getTexture('mil8')
        mil9 = pumkinsTex = bs.getTexture('mil9')
        mil10 = pumkinsTex = bs.getTexture('mil10')
        mil11 = pumkinsTex = bs.getTexture('mil11')
        mil12 = pumkinsTex = bs.getTexture('mil12')
        mil13 = pumkinsTex = bs.getTexture('mil13')
        mil14 = pumkinsTex = bs.getTexture('mil14')
        mil15 = pumkinsTex = bs.getTexture('mil15')
        mil16 = pumkinsTex = bs.getTexture('mil16')
        mil17 = pumkinsTex = bs.getTexture('mil17')

        # start handle menu scenes
        if startEvent == 1:
            bsGlobals.vignetteOuter = (0.98, 0.98, 0.98)
            bsGlobals.vignetteInner = (1, 1, 1)
            tint = (0.45, 0.45, 0.45)

            # play music and send screenMessage about it
            musicName = 'The XX - Intro'
            bs.playMusic('intro')
            bs.screenMessage(bs.Lstr(
                resource='musicText').evaluate()+musicName)

            def dropBGD():
                pos = (-15 + (random.random()*30), 15,
                       -15 + (random.random()*30))

                vel1 = (-5.0 + random.random()*30.0) \
                    * (-1.0 if pos[0] > 0 else 1.0)

                vel = (vel1, -50.0, random.uniform(-20, 20))

                bs.emitBGDynamics(
                    position=pos,
                    velocity=vel,
                    count=10,
                    scale=1+random.random(),
                    spread=0,
                    chunkType='sweat')

            bs.gameTimer(20, bs.Call(dropBGD), repeat=True)

        elif startEvent == 2:
            bsGlobals.ambientColor = (0.1, 0.6, 1)
            bsGlobals.vignetteOuter = (0.45, 0.55, 0.54)
            bsGlobals.vignetteInner = (0.99, 0.98, 0.98)
            tint = (0.78, 0.78, 0.82)
            self.color = (0.92, 0.91, 0.93)

            # FOR ENGLISH: "grom" is "thunder" (on russian)
            gromLite = bs.getSound('grom3')
            groms = ['grom', 'grom2']
            rain = bs.getSound('rain')

            sound = bs.newNode('sound', attrs={
                'sound': rain,
                'volume': 0.4,
                'loop': True})

            bs.animate(sound, 'volume', {0: 0, 2000: 0.4})

            def dropB():
                pos = (-15 + random.random()*30, 15, -15 + random.random()*30)

                velB1 = (-5.0 + random.random()*30.0) \
                    * (-1.0 if pos[0] > 0 else 1.0)

                vel = (velB1, -4.0, 0)

                bs.Bomb(
                    position=pos,
                    velocity=vel,
                    bombType='normal',
                    notShake=True,
                    notSound=True).autoRetain()

                bs.gameTimer(random.randint(120, 400), dropB)

            def liteGrom():
                bs.playSound(
                    gromLite,
                    position=(0, 8+random.random()*4, 0),
                    volume=random.uniform(0.6, 1))

                bs.gameTimer(random.randint(5000, 30000), liteGrom)

            dropB()
            bs.gameTimer(random.randint(5000, 20000), liteGrom)

            def dropBGD():
                pos = (-15 + (random.random()*30), 15,
                       -15 + (random.random()*30))

                velB2 = (-5.0 + random.random()*30.0) \
                    * (-1.0 if pos[0] > 0 else 1.0)

                vel = (velB2, -120.0, random.uniform(-20, 20))

                bs.emitBGDynamics(
                    position=pos,
                    velocity=vel,
                    count=50,
                    scale=1+random.random(),
                    spread=2,
                    chunkType='sweat')

            if bs.getEnvironment()['platform'] != 'android':
                bs.gameTimer(2, bs.Call(dropBGD), repeat=True)

            bs.gameTimer(random.randint(5000, 40000), liteGrom)

        elif startEvent == 3:
            bsGlobals.ambientColor = (1.06, 1.04, 1.03)
            bsGlobals.vignetteOuter = (0.6, 0.6, 0.6)
            bsGlobals.vignetteInner = (0.99, 0.98, 0.98)
            tint = (0.3, 0.3, 0.3)
            self.color = (0.1, 0.1, 0.1)

            # send screenMessage about play music
            musicName = 'Portal 2 OST - Turrets opera'
            bs.screenMessage(bs.Lstr(
                resource='musicText').evaluate()+musicName)

            def turnLight1(on=True):
                bs.playSound(
                    bs.getSound('LightTurnOn'), 0.6, position=(3, 10, -5))

                if on:
                    self.light1 = bs.newNode('light', attrs={
                        'position': (3, 10, -5),
                        'color': (0.2, 0.2, 0.25),
                        'volumeIntensityScale': 1.0,
                        'radius': 0.5,
                        'intensity': 9})
                else:
                    if self.light1.exists():
                        self.light1.delete()

            def turnLight2(on=True):
                bs.playSound(
                    bs.getSound('LightTurnOn'), 0.6, position=(0, 10, 3))

                if on:
                    self.light2 = bs.newNode('light', attrs={
                        'position': (0, 10, 3),
                        'color': (0.2, 0.2, 0.25),
                        'volumeIntensityScale': 1.0,
                        'radius': 0.5,
                        'intensity': 9})
                else:
                    if self.light2.exists():
                        self.light2.delete()

            def turnLight3(on=True):
                bs.playSound(
                    bs.getSound('LightTurnOn'), 0.6, position=(-3, 10, -5))

                if on:
                    self.light3 = bs.newNode('light', attrs={
                        'position': (-3, 10, -5),
                        'color': (0.2, 0.2, 0.25),
                        'volumeIntensityScale': 1.0,
                        'radius': 0.5,
                        'intensity': 9})
                else:
                    if self.light3.exists():
                        self.light3.delete()

            def offmusic():
                bs.playMusic(None)

            def fadeOut():
                bs.animateArray(
                    bsGlobals, 'vignetteInner', 3,
                    {0: bsGlobals.vignetteInner, 7000: (0, 0, 0)})

                bs.animateArray(
                    bsGlobals, 'vignetteOuter', 3,
                    {0: bsGlobals.vignetteOuter, 7000: (0, 0, 0)})

            # define the platform and models
            if bs.getEnvironment()['platform'] != 'android':
                turretsArrayNodeModel = turretsArray
            else:
                turretsArrayNodeModel = turretsArrayLow

            self.turretsArrayNode = bs.NodeActor(bs.newNode('terrain', attrs={
                'model': turretsArrayNodeModel,
                'reflection': 'powerup',
                'reflectionScale': [0.9],
                'colorTexture': testColorTexture}))

            # enable lights
            bs.gameTimer(500+200, bs.Call(turnLight1))
            bs.gameTimer(700+200, bs.Call(turnLight2))
            bs.gameTimer(900+200, bs.Call(turnLight3))

            bs.gameTimer(1200, bs.Call(bs.playMusic, 'turretOpera'))

            bs.gameTimer(84000, offmusic)
            bs.gameTimer(2000+200+85000, fadeOut)

            # disable lights
            bs.gameTimer(60000+26000+500, bs.Call(turnLight1, on=False))
            bs.gameTimer(60000+26000+800, bs.Call(turnLight2, on=False))
            bs.gameTimer(60000+26000+100, bs.Call(turnLight3, on=False))

        elif startEvent == 4:
            bsGlobals.ambientColor = (1.06, 1.04, 1.03)
            bsGlobals.vignetteOuter = (0.45, 0.55, 0.54)
            bsGlobals.vignetteInner = (0.99, 0.98, 0.98)
            tint = (0.3, 0.3, 0.3)
            self.color = (0.1, 0.1, 0.5)

            # play music and send screenMessage about it
            musicName = 'Zack Hemsey - The Way (Instrumental)'
            bs.playMusic('menuScene4')
            bs.screenMessage(bs.Lstr(
                resource='musicText').evaluate()+musicName)

            def fireWork():
                if bs.getEnvironment()['platform'] != 'android':
                    bs.emitBGDynamics(
                        position=(-0.4, 4, -2),
                        velocity=(0, 10, 0),
                        count=10000,
                        scale=1.3,
                        spread=3.5,
                        chunkType='spark')
                else:
                    bs.emitBGDynamics(
                        position=(-0.4, 4, -2),
                        velocity=(0, 10, 0),
                        count=5000,
                        scale=1.5,
                        spread=3.5,
                        chunkType='spark')

            def stopTime():
                bs.getSharedObject('globals').paused = True

            delay = 4500

            # define the platform and a pause
            if bs.getEnvironment()['platform'] == 'android':
                pause = 1000
            else:
                pause = 340

            bs.gameTimer(delay, fireWork)
            bs.gameTimer(delay+pause, stopTime)

        elif startEvent == 5:
            bsGlobals.ambientColor = (0.8, 1.3, 0.8)
            bsGlobals.vignetteOuter = (0.8, 0.8, 0.8)
            bsGlobals.vignetteInner = (1, 1, 1)
            bsGlobals.cameraMode = 'follow'
            tint = (0.75, 0.75, 0.75)
            self.color = (1, 1, 1)

            # play standart music
            bs.playMusic('Menu')

            def spawnCCube():
                pos = (15, random.uniform(2, 8), random.uniform(4, -10))
                if not random.random() > 0.9997:
                    cC = bs.Powerup(
                        position=pos,
                        powerupType=bsPowerup.PowerupFactory(
                            ).getRandomPowerupType()).autoRetain()

                    cC.node.extraAcceleration = (0, 20, 0)
                    cC.node.velocity = (random.random()*-10,
                                        random.random()*3,
                                        random.random()*3)
                else:
                    cC = bdUtils.Turret(
                        position=pos,
                        hasLaser=False,
                        mute=True
                        ).autoRetain()

                    cC.node.extraAcceleration = (0, 20, 0)
                    cC.node.velocity = (random.random()*-10,
                                        random.random()*3,
                                        random.random()*3)

            bs.gameTimer(50, bs.Call(spawnCCube), repeat=True)

        elif startEvent == 6:
            bsGlobals.ambientColor = (1.06, 1.04, 1.03)
            bsGlobals.vignetteOuter = (0.45, 0.55, 0.54)
            bsGlobals.vignetteInner = (0.99, 0.98, 0.98)
            tint = (0.5, 0.5, 0.5)
            self.color = (0.1, 0.1, 0.5)
            self.step = 0

            def spawnDirt():
                pos = (-15 + random.random()*30,
                       -15 + random.random()*30,
                       -15 + random.random()*30)

                r = random.randint(1, 9)

                # define the platform and a count
                if bs.getEnvironment()['platform'] != 'android':
                    count = 10
                else:
                    count = 8

                if r in [1, 2, 3]:
                    for i in range(count):
                        bdUtils.Clay(
                            position=pos,
                            velocity=(-30+random.random()*60,
                                      -30+random.random()*60,
                                      -30+random.random()*60)).autoRetain()

                elif r == 4:
                    bdUtils.Turret(
                        position=pos,
                        hasLaser=False,
                        mute=True
                        ).autoRetain()

                elif r in [5, 6]:
                    p = bs.Powerup(
                        position=pos,
                        powerupType=bsPowerup.PowerupFactory(
                            ).getRandomPowerupType()).autoRetain()

                elif r == 7:
                    bdUtils.cCube(position=pos).autoRetain()

                elif r in [8, 9]:
                    bs.Bomb(
                        bombType=random.choice(['normal', 'ice',
                                                'tnt', 'sticky']),
                        position=pos).autoRetain()

            # define the platform and a time
            if bs.getEnvironment()['platform'] != 'android':
                time = 150
            else:
                time = 250

            bs.gameTimer(time, bs.Call(spawnDirt), repeat=True)

            bdUtils.BlackHole(
                position=(-0.4, 4, -2),
                scale=3,
                doNotRandomize=True,
                infinity=True)

        elif startEvent == 7:
            bsGlobals.ambientColor = (1.06, 1.04, 1.03)
            bsGlobals.vignetteOuter = (0.45, 0.55, 0.54)
            bsGlobals.vignetteInner = (0.99, 0.98, 0.98)
            tint = (1.14, 1.1, 1.0)
            rec = 0
            self._spazArray = []

            if bs.getEnvironment()['platform'] != 'android':
                count = 30
            else:
                count = 15

            for i in range(count):
                s = bs.Spaz(color=(random.random(), random.random(),
                                   random.random()))

                s.node.handleMessage(
                    bs.StandMessage(
                        position=(random.randint(-4, 4),
                                  3,
                                  random.randint(-7, 1)),
                        angle=int(random.random()*360)))

                s.node.handleMessage('celebrate', 5430000)
                self._spazArray.append(s)

            def lightningBolt():
                bs.shakeCamera(5)
                groms = ['grom', 'grom2']
                bs.playSound(bs.getSound(random.choice(groms)))

                light = bs.newNode('light', attrs={
                    'position': (0, 10, 0),
                    'color': (0.2, 0.2, 0.4),
                    'volumeIntensityScale': 1.0,
                    'radius': 10})

                bs.animate(
                    light, 'intensity',
                    {0: 1, 50: 10, 150: 5, 250: 0, 260: 10, 410: 5, 510: 0})

            def boom():
                lightningBolt()
                bs.animateArray(
                    bs.getSharedObject('globals'), 'tint', 3,
                    {0: bs.getSharedObject('globals').tint, 500: (0, 0, 0)})

            def reBoom():
                tints = {
                    0: bs.getSharedObject('globals').tint,
                    500: (0.4, 0.4, 0.5)
                }

                bs.animateArray(
                    bs.getSharedObject('globals'), 'tint', 3, tints)

                bs.getSharedObject('globals').cameraMode = 'follow'

                self.light = bs.newNode('light', attrs={
                    'position': (3, 10, -5),
                    'color': (1.2, 1.1, 0.1),
                    'volumeIntensityScale': 1.0,
                    'radius': 0.8,
                    'intensity': 1})

                intensity = {
                    0: 1, 100: 1.05, 110: 0.3,
                    120: 1, 800: 1.1, 900: 1,
                    910: 0.6, 930: 1.1, 1000: 1,
                    1500: 1, 1510: 0, 1520: 1,
                    3000: 0.6, 3300: 1, 4000: 1.1
                }

                bs.animate(self.light, 'intensity', intensity, True)

            def knockOut():
                for i in self._spazArray:
                    i.node.handleMessage('knockout', 5000)

                bs.gameTimer(500, bs.Call(knockOut))

            def jump():
                s = int(random.random() * len(self._spazArray))
                self._spazArray[s].onJumpPress()
                self._spazArray[s].onJumpRelease()
                if not s == 40:
                    bs.gameTimer(50, bs.Call(jump))

            jump()
            bs.gameTimer(5000, bs.Call(boom))
            bs.gameTimer(8000, bs.Call(reBoom))
            bs.gameTimer(6000, bs.Call(knockOut))

        elif startEvent == 8:
            bsGlobals.ambientColor = (1.06, 1.04, 1.03)
            bsGlobals.vignetteOuter = (0.65, 0.65, 0.65)
            bsGlobals.vignetteInner = (1, 1, 1)
            tint = (0.35, 0.35, 0.4)

            self._background = bsUtils.Background(
                fadeTime=500,
                startFaded=True,
                showLogo=False,
                customBackground=False)

            self._part = 1
            self._text = bsUtils.Text(
                '',
                maxWidth=2000,
                hAlign='center',
                vAlign='center',
                position=(0, 270),
                color=gHackBackgroundTextColor,
                transition='fadeIn')

            self.imgMenu.node.delete()
            self.betaInfo.node.delete()
            self.imgMenu = bs.NodeActor(bs.newNode('image', attrs={
                'texture': bs.getTexture('white'),
                'position': (-350, 0),
                'opacity': 0.7,
                'color': menuImgMenuColor,
                'scale': (350, 2000)})).autoRetain()

            self.betaInfo = bs.NodeActor(bs.newNode('text', attrs={
                'vAttach': 'center',
                'hAlign': 'center',
                'color': menuBDMPMenuColor,
                'shadow': 0.5,
                'flatness': 0.5,
                'scale': 1,
                'vrDepth': -60,
                'position': (230, 125) if env['kioskMode'] else (-350, 215),
                'text': bdtext2}))

            if not gDidInitialTransition:
                bs.animate(
                    self.betaInfo.node, 'opacity',
                    {1300: 0, 1800: 1.0})

            def lineGen():
                word = random.choice([
                    ' password ',
                    ' hack ',
                    ' login ',
                    ' int ',
                    ' str ',
                    ' if ',
                    ' long ',
                    ' python ',
                    ' C++ ',
                    ' math ',
                    ' matrix ',
                    ' compilation ',
                    ' array '])

                a = ''
                for i in range(90):
                    a += str(random.randint(0, 1))

                ch = random.random()
                if ch > 0.98:
                    a = a[8:]
                    s = random.randint(1, 80)
                    a = a[s:] + word + a[:s-len(a)]
                return a

            def addLine():
                self._text.node.text += '\n' + lineGen()
                if len(self._text.node.text) > 8000:
                    self._text.node.text = self._text.node.text[200:]

            for i in range(560):
                addLine()

            bs.animateArray(
                self._text.node, 'position', 2,
                {0: (0, 0), 10000: (0, 900), 20000: (0, 0)}, True)

        elif startEvent == 9:
            bsGlobals.vignetteOuter = (0.9, 0.9, 0.9)
            bsGlobals.vignetteInner = (0.99, 0.98, 0.98)
            tint = (0.3, 0.3, 0.3)

            # play music and send screenMessage about it
            musicName = 'Zack Hemsey - Mind Heist'
            bs.playMusic('MindHeist')
            bs.screenMessage(bs.Lstr(
                resource='musicText').evaluate()+musicName)

            def dropBGD():
                pos = (-10 + (random.random()*25), 3.2,
                       -15 + (random.random()*25))

                bs.emitBGDynamics(
                    position=pos,
                    count=int(30 + random.random()*70),
                    scale=1+random.random(),
                    spread=15,
                    chunkType='spark',
                    emitType='stickers')

            bs.gameTimer(10, dropBGD, True)

        elif startEvent == 10:
            bsGlobals.ambientColor = (1.06, 1.04, 1.03)
            bsGlobals.vignetteOuter = (0.45, 0.55, 0.54)
            bsGlobals.vignetteInner = (0.99, 0.98, 0.98)
            tint = (0.2, 0.2, 0.2)
            self.color = (0, 0, 0)

            # play standart music
            bs.playMusic('ForwardMarch')

            def dropB():
                    fwBomb = bs.Bomb(
                        position=(-10+(random.random()*25),
                                  1,
                                  -15+(random.random()*25)),
                        velocity=(0, 100, 0),
                        bombType='petard',
                        blastRadius=3,
                        notShake=True)

                    fwBomb.node.extraAcceleration = (
                        0, 50+random.randint(-8, 8), 0)

                    def expl():
                        if fwBomb.node.exists():
                            pos = fwBomb.node.position
                            fwBomb.node.delete()
                            bs.Blast(
                                blastType='normal',
                                position=pos,
                                blastRadius=4,
                                blastColor=(random.random()*2,
                                            random.random()*2,
                                            random.random()*2),
                                notScorch=True)

                            bs.emitBGDynamics(
                                position=pos,
                                velocity=(0, 10, 0),
                                count=random.randint(230, 500),
                                scale=0.4+random.random(),
                                spread=0.4+random.random()*0.7,
                                chunkType='spark')

                            ambientColors = {
                                0: (1.06, 1.04, 1.03), 120: (8, 8, 8),
                                280+random.randint(50, 220): (1.06, 1.04, 1.03)
                            }

                            bs.animateArray(
                                bs.getSharedObject('globals'), 'ambientColor',
                                3, ambientColors)

                    bs.gameTimer(500 + int(random.random()*300), bs.Call(expl))

            bs.gameTimer(800 + int(random.random()*350), bs.Call(dropB),
                         repeat=True)

        elif startEvent == 11:
            # play music and send screenMessage about it
            musicName = 'Undertale - Waterfall Remix'
            bs.playMusic('WaterFall')
            bs.screenMessage(bs.Lstr(
                resource='musicText').evaluate()+musicName)

            self.node1 = bs.newNode('terrain', delegate=self, attrs={
                'collideModel': bs.getCollideModel('AirlandsMapCollide'),
                'model': bs.getModel('AirlandsMap'),
                'colorTexture': bs.getTexture('Airlands'),
                'materials': [bs.getSharedObject('footingMaterial')]})

            self.light7 = bs.newNode('shield', attrs={
                'position': (13.226, 5.52338, -2.79737),
                'color': (0, 0, 0),
                'radius': 0.17})

            self.light7beam = bs.newNode('light', attrs={
                'position': (12.6541, 5.70633, -2.82949),
                'color': (0, 0, 0),
                'volumeIntensityScale': 1.0,
                'intensity': 0.4,
                'radius': 0.3})

            self.light6 = bs.newNode('shield', attrs={
                'position': (5.8959, 3.38269, -4.52155),
                'color': (0, 0, 0),
                'radius': 0.17})

            self.light6beam = bs.newNode('light', attrs={
                'position': (5.71476, 3.56564, -4.67895),
                'color': (0, 0, 0),
                'volumeIntensityScale': 1.0,
                'intensity': 0.4,
                'radius': 0.3})

            self.light5 = bs.newNode('shield', attrs={
                'position': (2.41188, 3.38269, -5.06093),
                'color': (0, 0, 0),
                'radius': 0.17})

            self.light5beam = bs.newNode('light', attrs={
                'position': (2.54669, 3.56564, -4.90273),
                'color': (0, 0, 0),
                'volumeIntensityScale': 1.0,
                'intensity': 0.4,
                'radius': 0.3})

            self.light4 = bs.newNode('shield', attrs={
                'position': (-1.47369, 3.55083, -5.0736),
                'color': (0, 0, 0),
                'radius': 0.17})

            self.light4beam = bs.newNode('light', attrs={
                'position': (-1.05831, 3.73378, -4.79628),
                'color': (0, 0, 0),
                'volumeIntensityScale': 1.0,
                'intensity': 0.4,
                'radius': 0.3})

            self.light3 = bs.newNode('shield', attrs={
                'position': (-5.47391, 3.4683, -4.69703),
                'color': (0, 0, 0),
                'radius': 0.17})

            self.light3beam = bs.newNode('light', attrs={
                'position': (-5.08333, 3.56, -4.723),
                'color': (0, 0, 0),
                'volumeIntensityScale': 1.0,
                'intensity': 0.4,
                'radius': 0.3})

            self.light2 = bs.newNode('shield', attrs={
                'position': (-8.79521, 3.47698, -4.07394),
                'color': (0, 0, 0),
                'radius': 0.17})

            self.light2beam = bs.newNode('light', attrs={
                'position': (-8.30038, 3.65992, -4.00626),
                'color': (0, 0, 0),
                'volumeIntensityScale': 1.0,
                'intensity': 0.4,
                'radius': 0.3})

            self.light1 = bs.newNode('shield', attrs={
                'position': (-12.9, 5.51386, -2.79103),
                'color': (0, 0, 0),
                'radius': 0.17})

            self.light1beam = bs.newNode('light', attrs={
                'position': (-12.2, 5.69681, -2.77537),
                'color': (0, 0, 0),
                'volumeIntensityScale': 1.0,
                'intensity': 0.4,
                'radius': 0.3})

            bsGlobals.ambientColor = (1, 1, 1)
            bsGlobals.vignetteOuter = (0.9, 0.9, 0.9)
            bsGlobals.vignetteInner = (0.99, 0.99, 0.99)
            bsGlobals.cameraMode = 'follow'
            tint = (0.2, 0.2, 0.4)
            lightsColor = (3*40, 2.82*40, 2.16*40)
            lightsBeamColor = (3, 2.82, 2.16)

            bs.animateArray(
                self.light1, 'color', 3,
                {0: (0, 0, 0), 3000: lightsColor})

            bs.animateArray(
                self.light2, 'color', 3,
                {0: (0, 0, 0), 3000: lightsColor})

            bs.animateArray(
                self.light3, 'color', 3,
                {0: (0, 0, 0), 3000: lightsColor})

            bs.animateArray(
                self.light4, 'color', 3,
                {0: (0, 0, 0), 3000: lightsColor})

            bs.animateArray(
                self.light5, 'color', 3,
                {0: (0, 0, 0), 3000: lightsColor})

            bs.animateArray(
                self.light6, 'color', 3,
                {0: (0, 0, 0), 3000: lightsColor})

            bs.animateArray(
                self.light7, 'color', 3,
                {0: (0, 0, 0), 3000: lightsColor})

            bs.animateArray(
                self.light1beam, 'color', 3,
                {0: (0, 0, 0), 3000: lightsBeamColor})

            bs.animateArray(
                self.light2beam, 'color', 3,
                {0: (0, 0, 0), 3000: lightsBeamColor})

            bs.animateArray(
                self.light3beam, 'color', 3,
                {0: (0, 0, 0), 3000: lightsBeamColor})

            bs.animateArray(
                self.light4beam, 'color', 3,
                {0: (0, 0, 0), 3000: lightsBeamColor})

            bs.animateArray(
                self.light5beam, 'color', 3,
                {0: (0, 0, 0), 3000: lightsBeamColor})

            bs.animateArray(
                self.light6beam, 'color', 3,
                {0: (0, 0, 0), 3000: lightsBeamColor})

            bs.animateArray(
                self.light7beam, 'color', 3,
                {0: (0, 0, 0), 3000: lightsBeamColor})

            def dropBGD():
                pos = (-15+(random.random()*30),
                       15,
                       -15+(random.random()*30))

                vel1 = (-5.0 + random.random()*30.0) \
                    * (-1.0 if pos[0] > 0 else 1.0)

                vel = (vel1,
                       -50.0,
                       random.uniform(-20, 20))

                bs.emitBGDynamics(
                    position=pos,
                    velocity=vel,
                    count=10,
                    scale=1+random.random(),
                    spread=0,
                    chunkType='sweat')

            bs.gameTimer(20, bs.Call(dropBGD), repeat=True)

        elif startEvent == 12:
            bsGlobals.ambientColor = (1.06, 1.04, 1.03)
            bsGlobals.vignetteOuter = (0.6, 0.6, 0.6)
            bsGlobals.vignetteInner = (0.99, 0.98, 0.98)
            tint = (0.3, 0.3, 0.3)
            self.color = (0.1, 0.1, 0.1)
            self._spazArray = []

            # play music and send screenMessage about it
            musicName = 'Georgi Kay - In My Mind (Axwell Mix)'
            bs.playMusic('InMyMind')
            bs.screenMessage(bs.Lstr(
                resource='musicText').evaluate()+musicName)

            # define the platform and a count
            if bs.getEnvironment()['platform'] != 'android':
                count = 30
            else:
                count = 15

            for i in range(count):
                s = bs.Spaz(
                    color=(random.random()*10,
                           random.random()*10,
                           random.random()*10),
                    character=random.choice([
                        'Spaz',
                        'Zoe',
                        'Snake Shadow',
                        'Kronk',
                        'Mel',
                        'Jack Morgan',
                        'Santa Claus',
                        'Frosty',
                        'Bones',
                        'Bernard',
                        'Pascal',
                        'Taobao Mascot',
                        'B-9000',
                        'Agent Johnson',
                        'Grumbledorf',
                        'Pixel',
                        'Easter Bunny']))

                s.node.handleMessage(
                    bs.StandMessage(
                        position=(random.randint(-4, 4),
                                  3,
                                  random.randint(-7, 1)),
                        angle=int(random.random()*360)))

                s.node.handleMessage('celebrate', 5430000)
                self._spazArray.append(s)

            def Lights1():
                self.light1 = bs.newNode('light', attrs={
                    'position': (random.randint(0, 9)-4,
                                 4.5,
                                 random.randint(0, 9)-2),
                    'color': (random.random(),
                              random.random(),
                              random.random()),
                    'volumeIntensityScale': 1.0,
                    'radius': 0.4,
                    'intensity': 9})

                bs.animate(
                    self.light1, 'intensity',
                    {0: self.light1.intensity, self.lightstimer: 0})

                def deleteLights():
                    if self.light1.exists():
                        self.light1.delete()

                bs.gameTimer(self.lightstimer, deleteLights)

            def Lights2():
                self.light2 = bs.newNode('light', attrs={
                    'position': (random.randint(0, 9)-4,
                                 4.5,
                                 random.randint(0, 9)-2),
                    'color': (random.random(),
                              random.random(),
                              random.random()),
                    'volumeIntensityScale': 1.0,
                    'radius': 0.4,
                    'intensity': 9})

                bs.animate(
                    self.light2, 'intensity',
                    {0: self.light2.intensity, self.lightstimer: 0})

                def deleteLights():
                    if self.light2.exists():
                        self.light2.delete()

                bs.gameTimer(self.lightstimer, deleteLights)

            def Lights3():
                self.light3 = bs.newNode('light', attrs={
                    'position': (random.randint(0, 9)-4,
                                 4.5,
                                 random.randint(0, 9)-2),
                    'color': (random.random(),
                              random.random(),
                              random.random()),
                    'volumeIntensityScale': 1.0,
                    'radius': 0.4,
                    'intensity': 9})

                bs.animate(
                    self.light3, 'intensity',
                    {0: self.light3.intensity, self.lightstimer: 0})

                def deleteLights():
                    if self.light3.exists():
                        self.light3.delete()

                bs.gameTimer(self.lightstimer, deleteLights)

            def LightsSlowshowTimer(on=True):
                if on:
                    self.lightstimer = 1000
                    self.lts1 = bs.gameTimer(1000, Lights1, repeat=True)

                    def light2timer():
                        self.lts2 = bs.gameTimer(1000, Lights2, repeat=True)

                    def light3timer():
                        self.lts3 = bs.gameTimer(1000, Lights3, repeat=True)

                    # start 2 light timer for look better
                    self.lts2t1 = bs.gameTimer(300, light2timer)
                    # start 3 light timer for look better
                    self.lts3t1 = bs.gameTimer(600, light3timer)
                else:
                    self.lts1 = None
                    self.lts2 = None
                    self.lts3 = None
                    self.lts2t1 = None
                    self.lts3t1 = None
                    if self.light1.exists():
                        self.light1.delete()

                    if self.light2.exists():
                        self.light2.delete()

                    if self.light3.exists():
                        self.light3.delete()

            def StrobeTimer(on=True):
                if on:
                    self.light4 = bs.newNode('light', attrs={
                        'position': (0, 4.5, 0),
                        'color': (1, 1, 2),
                        'volumeIntensityScale': 1.0,
                        'radius': 10,
                        'intensity': 0.3})

                    def switcher():
                        try:
                            self.light4.intensity = 0.3
                        except StandardError:
                            pass

                        def off():
                            try:
                                self.light4.intensity = 0
                            except StandardError:
                                pass

                        bs.gameTimer(40, off)

                    self.ltstrobe = bs.gameTimer(80, switcher, repeat=True)
                else:
                    self.ltstrobe = None
                    if self.light4.exists():
                        self.light4.delete()

            def LightsFastshowTimer(on=True):
                if on:
                    self.lightstimer = 400
                    self.lt1 = bs.gameTimer(469, Lights1, repeat=True)
                    self.lt2 = bs.gameTimer(469, Lights2, repeat=True)
                    self.lt3 = bs.gameTimer(469, Lights3, repeat=True)

                else:
                    self.lt1 = None
                    self.lt2 = None
                    self.lt3 = None
                    if self.light1.exists():
                        self.light1.delete()

                    if self.light2.exists():
                        self.light2.delete()

                    if self.light3.exists():
                        self.light3.delete()

            def offmusic():
                bs.playMusic(None)

            def fadeOut():
                bs.animateArray(
                    bsGlobals, 'vignetteInner', 3,
                    {0: bsGlobals.vignetteInner, 7000: (0, 0, 0)})

                bs.animateArray(
                    bsGlobals, 'vignetteOuter', 3,
                    {0: bsGlobals.vignetteOuter, 7000: (0, 0, 0)})

                bs.animateArray(
                    bsGlobals, 'tint', 3,
                    {0: bsGlobals.tint, 7000: (0, 0, 0)})

                self.lt1 = None
                self.lt2 = None
                self.lt3 = None
                self.lts1 = None
                self.lts2 = None
                self.lts3 = None
                self.lts2t1 = None
                self.lts3t1 = None
                if self.light1.exists():
                    self.light1.delete()

                if self.light2.exists():
                    self.light2.delete()

                if self.light3.exists():
                    self.light3.delete()

            def intro():
                LightsSlowshowTimer()

            def drop():
                self.jumping = True
                LightsSlowshowTimer(on=False)
                LightsFastshowTimer()
                StrobeTimer()

                def jump():
                    s = int(random.random() * len(self._spazArray))
                    self._spazArray[s].onJumpPress()
                    self._spazArray[s].onJumpRelease()
                    if self.jumping and not s == 40:
                        bs.gameTimer(50, bs.Call(jump))

                jump()

            def middle():
                self.jumping = False
                LightsSlowshowTimer()
                LightsFastshowTimer(on=False)
                StrobeTimer(on=False)

            intro()
            bs.gameTimer(35460, drop)
            bs.gameTimer(78620, middle)
            bs.gameTimer(128560, drop)
            bs.gameTimer(170000, middle)
            bs.gameTimer(174600, offmusic)
            bs.gameTimer(175000, fadeOut)

        elif startEvent == 13:
            bsGlobals.ambientColor = (1, 1, 1)
            bsGlobals.vignetteOuter = (0.9, 0.9, 0.9)
            bsGlobals.vignetteInner = (0.99, 0.99, 0.99)
            bsGlobals.cameraMode = 'follow'
            tint = (0.6, 0.6, 0.7)
            self.color = (0.1, 0.1, 0.1)

            # play music and send screenMessage about it
            musicName = 'Basshunter - Dota'
            bs.playMusic('BasshunterDota')
            bs.screenMessage(bs.Lstr(
                resource='musicText').evaluate()+musicName)

            def Slide0():
                self.slide0 = bs.newNode('terrain', delegate=self, attrs={
                    'model': milosModel,
                    'colorTexture': mil0})

            def Slide0off():
                if self.slide0.exists():
                    self.slide0.delete()

            def Slide1():
                self.slide1 = bs.newNode('terrain', delegate=self, attrs={
                    'model': milosModel,
                    'colorTexture': mil1})

            def Slide1off():
                if self.slide1.exists():
                    self.slide1.delete()

            def Slide2():
                self.slide2 = bs.newNode('terrain', delegate=self, attrs={
                    'model': milosModel,
                    'colorTexture': mil2})

            def Slide2off():
                if self.slide2.exists():
                    self.slide2.delete()

            def Slide3():
                self.slide3 = bs.newNode('terrain', delegate=self, attrs={
                    'model': milosModel,
                    'colorTexture': mil3})

            def Slide3off():
                if self.slide3.exists():
                    self.slide3.delete()

            def Slide4():
                self.slide4 = bs.newNode('terrain', delegate=self, attrs={
                    'model': milosModel,
                    'colorTexture': mil4})

            def Slide4off():
                if self.slide4.exists():
                    self.slide4.delete()

            def Slide5():
                self.slide5 = bs.newNode('terrain', delegate=self, attrs={
                    'model': milosModel,
                    'colorTexture': mil5})

            def Slide5off():
                if self.slide5.exists():
                    self.slide5.delete()

            def Slide6():
                self.slide6 = bs.newNode('terrain', delegate=self, attrs={
                    'model': milosModel,
                    'colorTexture': mil6})

            def Slide6off():
                if self.slide6.exists():
                    self.slide6.delete()

            def Slide7():
                self.slide7 = bs.newNode('terrain', delegate=self, attrs={
                    'model': milosModel,
                    'colorTexture': mil7})

            def Slide7off():
                if self.slide7.exists():
                    self.slide7.delete()

            def Slide8():
                self.slide8 = bs.newNode('terrain', delegate=self, attrs={
                    'model': milosModel,
                    'colorTexture': mil8})

            def Slide8off():
                if self.slide8.exists():
                    self.slide8.delete()

            def Slide9():
                self.slide9 = bs.newNode('terrain', delegate=self, attrs={
                    'model': milosModel,
                    'colorTexture': mil9})

            def Slide9off():
                if self.slide9.exists():
                    self.slide9.delete()

            def Slide10():
                self.slide10 = bs.newNode('terrain', delegate=self, attrs={
                    'model': milosModel,
                    'colorTexture': mil10})

            def Slide10off():
                if self.slide10.exists():
                    self.slide10.delete()

            def Slide11():
                self.slide11 = bs.newNode('terrain', delegate=self, attrs={
                    'model': milosModel,
                    'colorTexture': mil11})

            def Slide11off():
                if self.slide11.exists():
                    self.slide11.delete()

            def Slide12():
                self.slide12 = bs.newNode('terrain', delegate=self, attrs={
                    'model': milosModel,
                    'colorTexture': mil12})

            def Slide12off():
                if self.slide12.exists():
                    self.slide12.delete()

            def Slide13():
                self.slide13 = bs.newNode('terrain', delegate=self, attrs={
                    'model': milosModel,
                    'colorTexture': mil13})

            def Slide13off():
                if self.slide13.exists():
                    self.slide13.delete()

            def Slide14():
                self.slide14 = bs.newNode('terrain', delegate=self, attrs={
                    'model': milosModel,
                    'colorTexture': mil14})

            def Slide14off():
                if self.slide14.exists():
                    self.slide14.delete()

            def Slide15():
                self.slide15 = bs.newNode('terrain', delegate=self, attrs={
                    'model': milosModel,
                    'colorTexture': mil15})

            def Slide15off():
                if self.slide15.exists():
                    self.slide15.delete()

            def Slide16():
                self.slide16 = bs.newNode('terrain', delegate=self, attrs={
                    'model': milosModel,
                    'colorTexture': mil16})

            def Slide16off():
                if self.slide16.exists():
                    self.slide16.delete()

            def Slide17():
                self.slide17 = bs.newNode('terrain', delegate=self, attrs={
                    'model': milosModel,
                    'colorTexture': mil17})

            def Slide17off():
                if self.slide17.exists():
                    self.slide17.delete()

            def mover():
                Slide0()
                bs.gameTimer(100, bs.Call(Slide0off))
                bs.gameTimer(100, bs.Call(Slide1))
                bs.gameTimer(200, bs.Call(Slide1off))
                bs.gameTimer(200, bs.Call(Slide2))
                bs.gameTimer(300, bs.Call(Slide2off))
                bs.gameTimer(300, bs.Call(Slide3))
                bs.gameTimer(400, bs.Call(Slide3off))
                bs.gameTimer(400, bs.Call(Slide4))
                bs.gameTimer(500, bs.Call(Slide4off))
                bs.gameTimer(500, bs.Call(Slide5))
                bs.gameTimer(600, bs.Call(Slide5off))
                bs.gameTimer(600, bs.Call(Slide6))
                bs.gameTimer(700, bs.Call(Slide6off))
                bs.gameTimer(700, bs.Call(Slide7))
                bs.gameTimer(800, bs.Call(Slide7off))
                bs.gameTimer(800, bs.Call(Slide8))
                bs.gameTimer(900, bs.Call(Slide8off))
                bs.gameTimer(900, bs.Call(Slide9))
                bs.gameTimer(1000, bs.Call(Slide9off))
                bs.gameTimer(1000, bs.Call(Slide10))
                bs.gameTimer(1100, bs.Call(Slide10off))
                bs.gameTimer(1100, bs.Call(Slide11))
                bs.gameTimer(1200, bs.Call(Slide11off))
                bs.gameTimer(1200, bs.Call(Slide12))
                bs.gameTimer(1300, bs.Call(Slide12off))
                bs.gameTimer(1300, bs.Call(Slide13))
                bs.gameTimer(1400, bs.Call(Slide13off))
                bs.gameTimer(1400, bs.Call(Slide14))
                bs.gameTimer(1500, bs.Call(Slide14off))
                bs.gameTimer(1500, bs.Call(Slide15))
                bs.gameTimer(1600, bs.Call(Slide15off))
                bs.gameTimer(1600, bs.Call(Slide16))
                bs.gameTimer(1700, bs.Call(Slide16off))
                bs.gameTimer(1700, bs.Call(Slide17))
                bs.gameTimer(1800, bs.Call(Slide17off))

            bs.gameTimer(1800, bs.Call(mover), repeat=True)

        elif startEvent == 14:
            self.color = (0.2, 0.1, 0)
            bsGlobals.ambientColor = (1.06, 1.04, 1.03)
            bsGlobals.vignetteOuter = (0.7, 0.7, 0.7)
            bsGlobals.vignetteInner = (1.0, 0.98, 0.95)
            tint = (1.2, 1.1, 1)

            # play music and send screenMessage about it
            musicName = 'Zack Hemsey - Redemption'
            bs.playMusic('Redemption')
            bs.screenMessage(bs.Lstr(
                resource='musicText').evaluate()+musicName)

            self.bottom = bs.NodeActor(bs.newNode('terrain', attrs={
                'model': pumpkinsBottom,
                'colorTexture': pumkinsBottomTex}))

            self.pumpkins = bs.NodeActor(bs.newNode('terrain', attrs={
                'model': bs.getModel('pumpkins'),
                'colorTexture': pumkinsTex,
                'reflection': 'soft',
                'reflectionScale': [0.15],
                'materials': [bs.getSharedObject('footingMaterial')]}))

            self.pumpkinsInside = bs.NodeActor(bs.newNode('terrain', attrs={
                'model': bs.getModel('pumpkinsInside'),
                'colorTexture': pumkinsTex,
                'reflection': 'soft',
                'materials': [bs.getSharedObject('footingMaterial')]}))

        elif startEvent == 15:
            tint = (0.8, 0.8, 0.9)
            bsGlobals.ambientColor = (0.1, 0.1, 0.2)
            bsGlobals.vignetteOuter = (0.7, 0.5, 1)
            bsGlobals.vignetteInner = (1, 1, 1.1)
            self.color = (0.1, 0.1, 0.2)

            # play music
            bs.gameTimer(1000, bs.Call(bs.playMusic, 'JingleBells'))

            self.bottom = bs.NodeActor(bs.newNode('terrain', attrs={
                'model': bs.getModel('thePadLevelBottomNY'),
                'reflection': 'soft',
                'reflectionScale': [0.45],
                'collideModel': bs.getCollideModel('newYearScene'),
                'colorTexture': testColorTexture}))

            self.tree1 = bs.NodeActor(bs.newNode('terrain', attrs={
                'model': bs.getModel('newYearTree'),
                'colorTexture': bs.getTexture('newYearTree'),
                'reflection': 'soft',
                'materials': [bs.getSharedObject('footingMaterial')]}))

            self.snow = bs.NodeActor(bs.newNode('terrain', attrs={
                'model': bs.getModel('snow'),
                'colorTexture': bs.getTexture('snow'),
                'reflection': 'soft',
                'materials': [bs.getSharedObject('footingMaterial')]}))

            self.gifts = bs.NodeActor(bs.newNode('terrain', attrs={
                'model': bs.getModel('gifts'),
                'colorTexture': bs.getTexture('gifts'),
                'reflection': 'soft',
                'materials': [bs.getSharedObject('footingMaterial')]}))

            self.trees = bs.NodeActor(bs.newNode('terrain', attrs={
                'model': treesModel,
                'lighting': False,
                'reflection': 'char',
                'reflectionScale': [0.1],
                'colorTexture': treesTexture}))

            def snowGen():
                pos = (random.uniform(-7, 8),
                       random.uniform(8, 16),
                       random.uniform(4, -10))

                vel = (0, -pos[1]*2, 0)

                bs.emitBGDynamics(
                    position=pos,
                    velocity=(0, -5, 0),
                    count=5,
                    scale=0.8 + random.random()*0.5,
                    spread=0,
                    chunkType='spark')

                bs.gameTimer(40, snowGen)

            snowGen()

        elif startEvent == 998:  # JRMP mode
            tint = (0.8, 0.8, 1.14)
            bsGlobals.tint = tint

            bsGlobals.ambientColor = (1.0, 1.0, 1.1)
            bsGlobals.vignetteOuter = (0.55, 0.55, 0.62)
            bsGlobals.vignetteInner = (0.95, 0.9, 0.9)
            color = (0.23, 0.31, 0.48)

        else:  # standart BombSquad menu
            tint = (1.14, 1.1, 1.0)

            bsGlobals.ambientColor = (1.06, 1.04, 1.03)
            bsGlobals.vignetteOuter = (0.45, 0.55, 0.54)
            bsGlobals.vignetteInner = (0.99, 0.98, 0.98)

        bsGlobals.tint = tint

        if startEvent not in [4, 5, 6, 8, 11, 13, 14]:
            self.bottom = bs.NodeActor(bs.newNode('terrain', attrs={
                'model': bottomModel,
                'reflection': 'soft',
                'reflectionScale': [0.45],
                'colorTexture': testColorTexture}))

            self.vrBottomFill = bs.NodeActor(bs.newNode('terrain', attrs={
                'model': vrBottomFillModel,
                'lighting': False,
                'vrOnly': True,
                'colorTexture': testColorTexture}))

            self.vrTopFill = bs.NodeActor(bs.newNode('terrain', attrs={
                'model': vrTopFillModel,
                'vrOnly': True,
                'lighting': False,
                'colorTexture': bgTex}))

            self.terrain = bs.NodeActor(bs.newNode('terrain', attrs={
                'model': model,
                'collideModel': collide,
                'colorTexture': testColorTexture,
                'reflection': 'soft',
                'reflectionScale': [0.3],
                'materials': [bs.getSharedObject('footingMaterial')]}))

            self.trees = bs.NodeActor(bs.newNode('terrain', attrs={
                'model': treesModel,
                'lighting': False,
                'reflection': 'char',
                'reflectionScale': [0.1],
                'colorTexture': treesTexture}))

        if not startEvent == 5:
            if not startEvent == 11:
                self.bg = bs.NodeActor(bs.newNode('terrain', attrs={
                    'model': bgModel,
                    'color': self.color,
                    'lighting': False,
                    'background': True,
                    'colorTexture': bgTex}))
            else:
                self.bg = bs.NodeActor(bs.newNode('terrain', attrs={
                    'model': bs.getModel('roofBG'),
                    'color': (0.92, 0.91, 0.9),
                    'lighting': False,
                    'background': True,
                    'colorTexture': bs.getTexture('skyBG')}))
        else:
            self.bg = bs.NodeActor(bs.newNode('terrain', attrs={
                'model': bs.getModel('parkourBG'),
                'color': self.color,
                'lighting': False,
                'background': True,
                'colorTexture': bs.getTexture('parkourBG')}))

        textOffsetV = 0
        self._ts = 0.86

        self._language = None
        self._updateTimer = bs.Timer(1000, self._update, repeat=True)
        self._update()

        # hopefully this won't hitch but lets space these out anyway..
        # bsInternal._addCleanFrameCallback(bs.WeakCall(self._startPreloads))

        random.seed()

        # bring up the last place we were, or start at the main menu otherwise
        with bs.Context('UI'):
            try:
                mainWindow = bsUI.gMainWindow
            except Exception:
                mainWindow = None

            # when coming back from a kiosk-mode game, jump to
            # the kiosk start screen.. if bsUtils.gRunningKioskModeGame:
            if bs.getEnvironment()['kioskMode']:
                bsUI.uiGlobals['mainMenuWindow'] = \
                     bsUI.KioskWindow().getRootWidget()
            # ..or in normal cases go back to the main menu
            else:
                if mainWindow == 'Gather':
                    bsUI.uiGlobals['mainMenuWindow'] = \
                        bsUI.GatherWindow(transition=None).getRootWidget()
                elif mainWindow == 'Watch':
                    bsUI.uiGlobals['mainMenuWindow'] = \
                        bsUI.WatchWindow(transition=None).getRootWidget()
                elif mainWindow == 'Team Game Select':
                    bsUI.uiGlobals['mainMenuWindow'] = \
                        bsUI.TeamsWindow(sessionType=bs.TeamsSession,
                                         transition=None).getRootWidget()
                elif mainWindow == 'Free-for-All Game Select':
                    bsUI.uiGlobals['mainMenuWindow'] = \
                        bsUI.TeamsWindow(sessionType=bs.FreeForAllSession,
                                         transition=None).getRootWidget()
                elif mainWindow == 'Coop Select':
                    bsUI.uiGlobals['mainMenuWindow'] = \
                        bsUI.CoopWindow(transition=None).getRootWidget()
                else:
                    bsUI.uiGlobals['mainMenuWindow'] = \
                        bsUI.MainMenuWindow(transition=None).getRootWidget()

                # attempt to show any pending offers immediately.
                # If that doesn't work, try again in a few seconds
                # (we may not have heard back from the server)
                # ..if that doesn't work they'll just have to wait
                # until the next opportunity.
                if not bsUI._showOffer():
                    def tryAgain():
                        if not bsUI._showOffer():
                            # try one last time..
                            bs.realTimer(2000, bsUI._showOffer)

                    bs.realTimer(2000, tryAgain)

        gDidInitialTransition = True

    def getName(self):
        return 'MainMenuActivity'

    def _update(self):
        # update logo in case it changes..
        if self._logoNode is not None and self._logoNode.exists():
            customTexture = self._getCustomLogoTexName()
            if customTexture != self._customLogoTexName:
                self._customLogoTexName = customTexture
                self._logoNode.texture = bs.getTexture(
                    customTexture if customTexture is not None else 'logo')

                self._logoNode.modelOpaque = (
                    None if customTexture is not None else bs.getModel('logo'))

                self._logoNode.modelTransparent = (
                    None if customTexture is not None
                    else bs.getModel('logoTransparent'))

        if not self._wordActorsCreated:
            self._wordActorsCreated = True
            env = bs.getEnvironment()
            y = 20
            gScale = 1.1
            self._wordActors = []
            baseDelay = 1000
            delay = baseDelay
            delayInc = 20

            # come on faster after the first time
            if gDidInitialTransition:
                baseDelay = 0
                delay = baseDelay
                delayInc = 20

            # we draw higher in kiosk mode (make sure to test this
            # when making adjustments) for now we're hard-coded for
            # a few languages.. should maybe look into generalizing this?..
            baseX = -170
            x = baseX - 20
            spacing = 55 * gScale

            x1 = x
            delay1 = delay

            def createNameWithWords(shadow=False):
                x = x1
                delay = delay1
                self._makeWord('B', x-670, y+325, scale=0.60,
                               delay=delay, vrDepthOffset=3, shadow=shadow)

                x += spacing * 0.9
                delay += delayInc
                self._makeWord('m', x-590, y+325, delay=delay, scale=0.60,
                               shadow=shadow)

                x += spacing * 0.9
                delay += delayInc
                self._makeWord('b', x-570, y+325, delay=delay,
                               scale=0.60, vrDepthOffset=5, shadow=shadow)

                x += spacing * 0.9
                delay += delayInc
                self._makeWord('S', x-570, y+325, scale=0.60,
                               delay=delay, vrDepthOffset=14, shadow=shadow)

                x += spacing * 0.8
                delay += delayInc
                self._makeWord('q', x-570, y+325, delay=delay, scale=0.60,
                               shadow=shadow)

                x += spacing * 0.9
                delay += delayInc
                self._makeWord('u', x-570, y+325, delay=delay, scale=0.60,
                               vrDepthOffset=7, shadow=shadow)

                x += spacing * 0.9
                delay += delayInc
                self._makeWord('a', x-570, y+325, delay=delay, scale=0.60,
                               shadow=shadow)

                x += spacing * 0.9
                delay += delayInc
                self._makeWord('d', x-570, y+325, delay=delay,
                               scale=0.60, vrDepthOffset=6, shadow=shadow)

            createNameWithWords()

            self._makeLogo(-452.5, 290, 0.15,
                           delay=baseDelay)

    def _makeWord(self, word, x, y,
                  scale=1.0, delay=0, vrDepthOffset=0, shadow=False):
        if shadow:
            wordShadowObj = bs.NodeActor(bs.newNode('text', attrs={
                'position': (x, y),
                'big': True,
                'color': (0.0, 0.0, 0.2, 0.08),
                'tiltTranslate': 0.09,
                'opacityScalesShadow': False,
                'shadow': 0.2,
                'vrDepth': -130,
                'vAlign': 'center',
                'projectScale': 0.97*scale,
                'scale': 1.0,
                'text': word}))

            self._wordActors.append(wordShadowObj)
        else:
            wordObj = bs.NodeActor(bs.newNode('text', attrs={
                'position': (x, y),
                'big': True,
                'color': menuGameNameMenuColor,
                'tiltTranslate': 0.11,
                'shadow': 0.2,
                'vrDepth': -40+vrDepthOffset,
                'vAlign': 'center',
                'hostOnly': True,
                'projectScale': scale,
                'scale': 1.0,
                'text': word}))

            self._wordActors.append(wordObj)

        # add a bit of stop-motion-y jitter to the logo
        # (unless we're in VR mode in which case
        # its best to leave things still)
        if not bs.getEnvironment()['vrMode']:
            if not shadow:
                c = bs.newNode(
                    'combine', owner=wordObj.node, attrs={'size': 2})
            else:
                c = None

            if shadow:
                c2 = bs.newNode('combine', owner=wordShadowObj.node,
                                attrs={'size': 2})
            else:
                c2 = None

            if not shadow:
                c.connectAttr('output', wordObj.node, 'position')

            if shadow:
                c2.connectAttr('output', wordShadowObj.node, 'position')

            keys = {}
            keys2 = {}
            timeV = 0
            for i in range(10):
                val = x + (random.random()-0.5)*0.8
                val2 = x + (random.random()-0.5)*0.8
                keys[timeV*self._ts] = val
                keys2[timeV*self._ts] = val2 + 5
                timeV += random.random() * 100

            if c is not None:
                bs.animate(c, 'input0', keys, loop=True)

            if c2 is not None:
                bs.animate(c2, 'input0', keys2, loop=True)

            keys = {}
            keys2 = {}
            timeV = 0
            for i in range(10):
                val = y + (random.random()-0.5)*0.8
                val2 = y + (random.random()-0.5)*0.8
                keys[timeV*self._ts] = val
                keys2[timeV*self._ts] = val2 - 9
                timeV += random.random() * 100

            if c is not None:
                bs.animate(c, 'input1', keys, loop=True)

            if c2 is not None:
                bs.animate(c2, 'input1', keys2, loop=True)

        if not shadow:
            bs.animate(wordObj.node, 'projectScale',
                       {delay: 0.0, delay+100: scale*1.1, delay+200: scale})
        else:
            bs.animate(wordShadowObj.node, 'projectScale',
                       {delay: 0.0, delay+100: scale*1.1, delay+200: scale})

    def _getCustomLogoTexName(self):
        if bsInternal._getAccountMiscReadVal('easter', False):
            return 'logoEaster'
        elif firstApril:
            return 'logoLegacy' if not JRMPmode else 'logo'
        elif bsUtils.gVDV and bs.getLanguage() == 'Russian':
            return 'logoVDV'
        elif bsUtils.gNewYear:
            return 'logoNY'
        elif bsUtils.gWinter:
            return 'logoWinter'
        elif bsUtils.gMarch8:
            return 'logo'
        else:
            return None

    # pop the logo and menu in
    def _makeLogo(self, x, y,
                  scale, delay, customTexture=None,
                  jitterScale=1.0, rotate=0, vrDepthOffset=0):
        # temp easter googness
        if customTexture is None:
            customTexture = self._getCustomLogoTexName()

        self._customLogoTexName = customTexture
        logo = bs.NodeActor(bs.newNode('image', attrs={
            'texture': bs.getTexture(customTexture if customTexture is not None
                                     else 'logoBD'),
            'vrDepth': -10+vrDepthOffset,
            'rotate': rotate,
            'attach': 'center',
            'hostOnly': True,
            'tiltTranslate': 0.21,
            'absoluteScale': True}))

        self._logoNode = logo.node
        self._wordActors.append(logo)
        # add a bit of stop-motion-y jitter to the logo
        # (unless we're in VR mode in which case
        # its best to leave things still)
        if not bs.getEnvironment()['vrMode']:
            c = bs.newNode('combine', owner=logo.node, attrs={'size': 2})
            c.connectAttr('output', logo.node, 'position')
            keys = {}
            timeV = 0
            # gen some random keys for that stop-motion-y look
            for i in range(10):
                keys[timeV] = x + (random.random() - 0.5)*0.7*jitterScale
                timeV += random.random() * 100

            bs.animate(c, 'input0', keys, loop=True)
            keys = {}
            timeV = 0
            for i in range(10):
                keys[timeV*self._ts] = y + (random.random()-0.5)*0.7\
                    * jitterScale
                timeV += random.random() * 100

            bs.animate(c, 'input1', keys, loop=True)
        else:
            logo.node.position = (x, y)

        c = bs.newNode('combine', owner=logo.node, attrs={'size': 2})
        keys = {
            delay: 0, delay+100: 700*scale,
            delay+200: 600*scale
        }

        bs.animate(c, 'input0', keys)
        bs.animate(c, 'input1', keys)
        c.connectAttr('output', logo.node, 'scale')

    def _startPreloads(self):
        # FIXME - the func that calls us back doesn't save/restore state
        # or check for a dead activity so we have to do that ourself..
        if self.isFinalized():
            return

        with bs.Context(self):
            _preload1()

        bs.gameTimer(500, lambda: bs.playMusic('Menu'))


# a second or two into the main menu is a good time to preload some stuff
# we'll need elsewhere to avoid hitches later on..
def _preload1():
    for m in ['plasticEyesTransparent', 'playerLineup1Transparent',
              'playerLineup2Transparent', 'playerLineup3Transparent',
              'playerLineup4Transparent', 'angryComputerTransparent',
              'scrollWidgetShort', 'windowBGBlotch']:
        bs.getModel(m)

    for t in ['playerLineup', 'lock']:
        bs.getTexture(t)

    for tex in ['iconRunaround', 'iconOnslaught', 'medalComplete',
                'medalBronze', 'medalSilver', 'medalGold',
                'characterIconMask']:
        bs.getTexture(tex)

    bs.getTexture('bg')
    bs.Powerup.getFactory()
    bs.gameTimer(100, _preload2)


def _preload2():
    # FIXME - could integrate these loads with the classes that use them
    # so they don't have to redundantly call the load
    # (even if the actual result is cached)
    for m in ['powerup', 'powerupSimple']:
        bs.getModel(m)

    for t in ['powerupBomb', 'powerupSpeed', 'powerupPunch',
              'powerupIceBombs', 'powerupStickyBombs', 'powerupShield',
              'powerupImpactBombs', 'powerupHealth']:
        bs.getTexture(t)

    for s in ['powerup01', 'boxDrop', 'boxingBell',
              'scoreHit01', 'scoreHit02', 'dripity',
              'spawn', 'gong']:
        bs.getSound(s)

    bs.Bomb.getFactory()
    bs.gameTimer(100, _preload3)


def _preload3():
    for m in ['bomb', 'bombSticky', 'impactBomb']:
        bs.getModel(m)

    for t in ['bombColor', 'bombColorIce', 'bombStickyColor',
              'impactBombColor', 'impactBombColorLit']:
        bs.getTexture(t)

    for s in ['freeze', 'fuse01', 'activateBeep',
              'warnBeep']:
        bs.getSound(s)

    spazFactory = bs.Spaz.getFactory()

    # go through and load our existing spazzes and their icons
    # (spread these out quite a bit since theres lots of stuff for each)
    def _load(spaz):
        spazFactory._preload(spaz)
        # icons also..
        bs.getTexture(bsSpaz.appearances[spaz].iconTexture)
        bs.getTexture(bsSpaz.appearances[spaz].iconMaskTexture)

    # FIXME - need to come up with a standin texture mechanism or something
    # ..preloading won't scale too much farther..
    t = 50
    bs.gameTimer(200, _preload4)


def _preload4():
    for t in ['bar', 'meter', 'null', 'flagColor', 'achievementOutline']:
        bs.getTexture(t)

    for m in ['frameInset', 'meterTransparent', 'achievementOutline']:
        bs.getModel(m)

    for s in ['metalHit', 'metalSkid', 'refWhistle', 'achievement']:
        bs.getSound(s)

    bs.Flag.getFactory()
    bs.Powerup.getFactory()


gFirstRun = True


class SplashScreenActivity(bs.Activity):

    def __init__(self, settings={}):
        bs.Activity.__init__(self, settings)
        
    def onTransitionIn(self):
        import bsInternal
        bs.Activity.onTransitionIn(self)

        self._background = bsUtils.Background(
            fadeTime=500,
            startFaded=True,
            showLogo=False)

        bsInternal._unlockAllInput()
        with bs.Context('UI'):
            bsUI.AgreementWindow()
        
    def onSomethingPressed(self):
        self.end()


class MainMenuSession(bs.Session):

    def __init__(self):
        global gFirstRun
        bs.Session.__init__(self)
        permissionReceiverTimer = None
        self._locked = False

        if not settings.agreement:
            bsInternal._lockAllInput()
            self._locked = True
            self.setActivity(bs.newActivity(SplashScreenActivity))
            gFirstRun = False
        else:
            self.setActivity(bs.newActivity(MainMenuActivity))

    def onActivityEnd(self, activity, results):
        if self._locked:
            bsInternal._unlockAllInput()

        # any ending activity leads us into the main menu one..
        self.setActivity(bs.newActivity(MainMenuActivity))

    def onPlayerRequest(self, player):
        # reject player requests, but if we're in a splash-screen, take the
        # opportunity to tell it to leave
        # FIXME - should add a blanket way to capture all input for
        # cases like this
        activity = self.getActivity()
        if isinstance(activity, SplashScreenActivity):
            with bs.Context(activity): activity.onSomethingPressed()

        return False
