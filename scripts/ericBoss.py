import random
import bs
import bsUtils
import bsAchievement
import settings

def bsGetAPIVersion():
    # see bombsquadgame.com/apichanges
    return 4

def bsGetGames():
    return [BossBattleGame2] # "2" to reset scores

def bsGetLevels():
    return [bs.Level('Boss Battle ',
            displayName='${GAME}',
            gameType=BossBattleGame2,
            settings={},
            previewTexName='roofMapPreview')]

class BossBattleGame2(bs.CoopGameActivity):

    @classmethod
    def getName(cls):
        return 'Boss Battle '

    @classmethod
    def getDescription(cls, sessionType):
        return 'Fight with creator!'

    @classmethod
    def getSupportedMaps(cls, sessionType):
        return ['Roof']

    @classmethod
    def supportsSessionType(cls, sessionType):
        return True if issubclass(sessionType,bs.CoopSession) else False

    def __init__(self, settings):
        bs.CoopGameActivity.__init__(self, settings)

    def onTransitionIn(self):
        bs.CoopGameActivity.onTransitionIn(self, music='menuScene4')
        self._scoreBoard = bs.ScoreBoard(
            label=bs.Lstr(resource='scoreText'), scoreSplit=0.5)

    def onBegin(self):
        bs.CoopGameActivity.onBegin(self)
        self.getMap().bg.color = (1, 0, 0)
        self.num = 1
        self.stop = False
        self.killed = 0

        self._bots = bs.BotSet()

        self._score2 = 0
        self.score = 0

        self.pos1 = (3*1.4, 3*1.4, -3*1.4)
        self.pos2 = (5*1.4, 3*1.4, -5*1.4)
        self.pos3 = (5*1.4, 3*1.4, -1*1.4)
        self.pos4 = (-5*1.4, 3*1.4, -3*1.4)
        self.pos5 = (0*1.4, 3*1.4, -7*1.4)
        self.pos6 = (0*1.4, 3*1.4, 0*1.4)
        self.pos7 = (-7*1.4, 3*1.4, -3*1.4)
        self.pos8 = (3*1.4, 3*1.4, -3*1.4)
        self.pos9 = (3*1.4, 3*1.4, -3*1.4)
        self.pos10 = (3*1.4, 3*1.4, -3*1.4)

        globals = bs.getSharedObject('globals')

        globals.tint = (1.1, 1, 1)

        globals.vignetteOuter = (0.6, 0.6, 0.6)
        globals.vignetteInner = (0.8, 0.8, 0.8)

        bs.gameTimer(2000, bs.Call(self.dropPowerup))

        self.waves = {
            1:[bs.NinjaBot,
               bs.MelBot,
               bs.NinjaBot],

            2:[bs.BunnyBot,
               bs.MelBot,
               bs.ChickBot],

            3:[bs.ChickBotPro,
               bs.SpazBot,
               bs.BunnyBot],

            4:[bs.SpazBot,
               bs.BunnyBot,
               bs.BunnyBot,
               bs.SpazBot],

            5:[bs.ChickBot,
               bs.PirateBot,
               bs.BunnyBot,
               bs.BunnyBot],

            6:[bs.ChickBot,
               bs.SkeletonBot,
               bs.BunnyBot],

            7:[bs.SpazBot,
               bs.SpazBot,
               bs.ChickBot,
               bs.SpazBot],

            8:[bs.NinjaBotPro,
               bs.SpazBot,
               bs.SpazBot,
               bs.CrayfishBot],

            9:[bs.NinjaBotPro,
               bs.NinjaBotPro,
               bs.CrayfishBot],

            10:[bs.BomzhBotPro,
                bs.BomzhBotPro,
                bs.BomzhBotPro,
                bs.BomzhBotPro,
                bs.BomzhBotPro,
                bs.BomzhBotPro,
                bs.BomzhBotPro,
                bs.BomzhBotPro,
                bs.BomzhBotPro,
                bs.BomzhBotPro],

            11:[bs.EricBot,
                bs.BomzhBotPro,
                bs.BomzhBotPro,
                bs.BomzhBotPro,
                bs.SpazBot]}

    def dropPowerup(self):
        self._powerupMaterial = bs.Material()
        self._powerupMaterial.addActions(
            conditions=('theyHaveMaterial',
                        bs.getSharedObject('playerMaterial')),
            actions=(("modifyPartCollision", "collide", True),
                     ("modifyPartCollision", "physical", True),
                     ("call", "atConnect", self.powerupAccepted)))

        bs.playSound(bs.getSound('dingSmallHigh'))
        self.p = bs.Powerup(
            powerupType='health',
            position=self.pos1,
            expire=False).autoRetain()

        self.p.node.materials = [self._powerupMaterial]

    def spawnPlayer(self, player):
        pos = (-7+random.uniform(-2, 2), 3, -3+random.uniform(-2, 2))
        self.spaz = self.spawnPlayerSpaz(player, position=pos)
        self.spaz.connectControlsToPlayer()

    def cheat(self):
        self.spaz.node.invincible = True
        self.spaz.node.hockey = True
        self.spaz._punchPowerScale = 11
        self.spaz.defaultBombType = 'forceBomb'
        self.spaz.bombType = 'forceBomb'
        self.spaz.bombCount = 100000
        self.spaz.node.handleMessage(
            bs.PowerupMessage(powerupType='health'))

        bs.gameTimer(10, bs.Call(bs.Blast, blastRadius=10000))

    def getRandomPos(self):
        return (-9+random.random()*18, 2.7*1.5, -8+random.random()*9)

    def getRandomPosV(self):
        return (-9+random.random()*18, 7, -8+random.random()*9)

    def lightningBolt(self, position=(0, 10, 0), radius=10):
        bs.shakeCamera(3)
        self.tint = bs.getSharedObject('globals').tint

        light = bs.newNode('light', attrs={
            'position': position,
            'color': (0.2, 0.2, 0.4),
            'volumeIntensityScale': 1.0,
            'radius': radius})

        bsUtils.animate(light, 'intensity', {
            0: 1, 50: radius, 150: radius/2,
            250: 0, 260: radius, 410: radius/2,
            510: 0})

        bsUtils.animateArray(bs.getSharedObject('globals'), 'tint', 3,
            {0: self.tint, 200: (0.2, 0.2, 0.2), 510: self.tint})

        bs.playSound(bs.getSound('grom'), volume=10, position=(0, 10, 0))

    def powerupAccepted(self):
        self.setupStandardPowerupDrops()
        self.p.node.delete()
        bs.playMusic('doomsday')
        self.lightningBolt()
        self.updateScore()

        bs.gameTimer(1000, bs.Call(self.startNextWave, self.num))

    def waveDelay(self):
        bs.playSound(bs.getSound('gong'))
        globals = bs.getSharedObject('globals')
        tint = globals.tint
        bsUtils.animateArray(bs.getSharedObject('globals'), "tint", 3, {
            0: tint, 1000: (0.2, 0.2, 0.2),
            2500: (1.2, 1.2, 1.2), 4000: (1.3, 1.3, 1.3),
            5000: tint})

        bs.Powerup(
            powerupType=random.choice(['health', 'shield', 'punch', 'impactBombs', 'curse']),
            position=self.getRandomPosV(),
            expire=False).autoRetain()

        if random.random() > 0.3:
            bs.gameTimer(200, bs.Call(
                bs.Powerup,
                powerupType=random.choice(['health', 'shield', 'punch', 'impactBombs']),
                position=self.getRandomPosV(),
                expire=False))

            bs.Powerup(
                powerupType=random.choice(['health', 'shield', 'punch', 'impactBombs', 'curse']),
                position=self.getRandomPosV(),
                expire=False).autoRetain()

        if random.random() > 0.6:
            bs.gameTimer(400, bs.Call(
                bs.Powerup,
                powerupType=random.choice(['health', 'shield', 'punch', 'impactBombs']),
                position=self.getRandomPosV(),
                expire=False))

        bs.gameTimer(5000, bs.Call(self.startNextWave, self.num))

    def registerBotDie(self, m):
        self.killed += 1
        self._score2 += 1
        self.updateScore()

        if len(self._bots.getLivingBots()) == 0 and not self.stop:
            self.stop = True
            self.num += 1
            self.killed = 0
            bs.PopupText(
                bs.Lstr(value='+${A} ${B}', subs=[
                    ('${A}', str(int(bs.getGameTime()-self.time)/1000)),
                    ('${B}', bs.Lstr(resource='timeBonusText'))]),
                color=(1, 1, 0.5, 1),
                scale=1.0,
                position=self.spaz.node.position if self.spaz is not None \
                    and self.spaz.node.exists() else (0, 5, 0)).autoRetain()

            self._score2 += int((bs.getGameTime()-self.time)/1000)
            self.updateScore()
            self.waveDelay()

            def offstop():
                self.stop = False

            bs.gameTimer(1000, offstop)

        if str(m.badGuy).lower().find('eric') != -1: # Warning! shit code!
            self.doEnd(outcome='victory') # But works - not touch.

    def startNextWave(self, num):
        self.killed = 0
        self.time = bs.getGameTime()
        for i in range(len(self.waves[self.num])):
            bs.gameTimer(i*100, bs.Call(self._bots.spawnBot, self.waves[self.num][i],
                pos=self.getRandomPos() if not self.waves[self.num][i] == bs.EricBot else (9, 5 ,-5),
                spawnTime=1000))

        self.showZoomMessage(
            bs.Lstr(value='${A} ${B}', subs=[
                ('${A}', bs.Lstr(resource='waveText')),
                ('${B}', str(self.num))]),
            scale=1.0,
            duration=1000,
            trail=True)

        self._waveText = bs.NodeActor(bs.newNode('text', attrs={
            'vAttach': 'top',
            'hAttach': 'center',
            'hAlign': 'center',
            'vrDepth': -10,
            'color': (1, 1, 1, 1) if True else (0.7, 0.7, 0.7, 1.0),
            'shadow': 1.0 if True else 0.7,
            'flatness': 1.0 if True else 0.5,
            'position': (0, -40),
            'scale': 1.3 if True else 1.1,
            'text': bs.Lstr(value='${A} ${B}', subs=[
                ('${A}', bs.Lstr(resource='waveText')),
                ('${B}', str(self.num))])}))

    def handleMessage(self, m):
        if isinstance(m, bs.PlayerSpazDeathMessage):
            bs.CoopGameActivity.handleMessage(self, m)
            bs.gameTimer(100, self.kostyl)

        elif isinstance(m, bs.SpazBotDeathMessage):
            bs.CoopGameActivity.handleMessage(self, m)
            bs.gameTimer(10, bs.Call(self.registerBotDie,m))

        else:
            bs.CoopGameActivity.handleMessage(self, m)

    def updateScore(self):
        self._scoreBoard.setTeamValue(self.teams[0], self._score2, maxScore=None)

    def kostyl(self):
        if not any(player.isAlive() for player in self.teams[0].players):
            self.doEnd('defeat')

    def doEnd(self, outcome):
        bs.playMusic(None)
        if self._score2 > 500:
            outcome = 'defeat'
            self._score2 = 0

        self.end(
            results={'outcome': outcome,
                     'score': self._score2,
                     'playerInfo': self.initialPlayerInfo},
            delay=3000)

        if outcome == 'defeat':
            self._bots.finalCelebrate()
            self.fadeToRed()

        elif outcome == 'victory':
            tint = bs.getSharedObject('globals').tint
            bsUtils.animateArray(bs.getSharedObject('globals'), 'tint', 3,
                {0: tint, 1000: (1.4, 1.4, 1.4)})

            self.cameraFlash()
            bsAchievement._awardLocalAchievement('Boss')
            settings.bolt = True
            settings.duck = True
            settings.saveSettings()