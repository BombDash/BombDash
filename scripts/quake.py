import random
import bs
import bsVector
import bsSpaz
import bsBomb
import bsUtils
import quakeBall

def bsGetAPIVersion():
    # see bombsquadgame.com/apichanges
    return 4

def bsGetGames():
    return [QuakeGame]

class QuakeGame(bs.TeamGameActivity):

    @classmethod
    def getName(cls):
        return 'Quake'

    @classmethod
    def getDescription(cls, sessionType):
        return 'Kill a set number of enemies to win.'

    @classmethod
    def supportsSessionType(cls, sessionType):
        return True if (issubclass(sessionType, bs.TeamsSession)
                        or issubclass(sessionType, bs.FreeForAllSession)) else False

    @classmethod
    def getSupportedMaps(cls, sessionType):
        return ['Football Stadium', 'Monkey Face', 'Doom Shroom']

    @classmethod
    def getSettings(cls, sessionType):
        settings = [
            ('Kills to Win Per Player', {'minValue': 1, 'default': 15, 'increment': 1}),
            ('Time Limit', {'choices': [('None',0), ('1 Minute', 60),
                                        ('2 Minutes', 120), ('5 Minutes', 300),
                                        ('10 Minutes', 600), ('20 Minutes', 1200)], 'default':0}),
            ('Graphics', {'choices': [('Normal', 1.0), ('High', 2.0)], 'default': 2.0}),
            ('Respawn Times', {'choices': [('At once', 0.0),
                                           ('Shorter', 0.25),
                                           ('Short', 0.5),
                                           ('Normal', 1.0),
                                           ('Long', 2.0),
                                           ('Longer', 4.0)], 'default': 1.0}),
            ('Speed', {'default': True}),
            ('Enable jump', {'default': True}),
            ('Enable pickup', {'default': True}),
            ('Enable bomb', {'default': False}),
            ('Obstacles', {'default': True}),
            ('Obstacles form', {'choices': [('Cube', 0.0),
                                            ('Sphere', 1.0),
                                            ('Random', 2.0)], 'default': 0.0}),
            ('Obstacles mirror shots', {'default': False}),
            ('Obstacles count', {'minValue': 0, 'default': 16, 'increment': 2}),
            ('Random obstacles color', {'default': True}),
            ('Epic Mode', {'default': False})]

        return settings

    def __init__(self, settings):
        bs.TeamGameActivity.__init__(self,settings)
        if self.settings['Epic Mode']: self._isSlowMotion = True

        self.announcePlayerDeaths = True
        self._scoreBoard = bs.ScoreBoard()

    def getInstanceDescription(self):
        return ('Kill ${ARG1} enemies.',self._scoreToWin)

    def getInstanceScoreBoardDescription(self):
        return ('kill ${ARG1} enemies',self._scoreToWin)

    def onTransitionIn(self):
        bs.TeamGameActivity.onTransitionIn(
            self, music='Epic' if self.settings['Epic Mode'] else 'GrandRomp')

    def onTeamJoin(self, team):
        team.gameData['score'] = 0
        if self.hasBegun(): self._updateScoreBoard()

    def onBegin(self):
        bs.TeamGameActivity.onBegin(self)
        self.dropShield()
        self._shieldDropper = bs.Timer(8001, bs.WeakCall(self.dropShield), repeat=True)
        self.setupStandardTimeLimit(self.settings['Time Limit'])
        bsGlobals = bs.getSharedObject('globals')
        if self.settings['Obstacles']:
            count = self.settings['Obstacles count']
            map = bs.getActivity()._map.getName()
            for i in range(count):
                if map == 'Football Stadium':
                    radius = (random.uniform(-10, 1),
                              6,
                              random.uniform(-4.5, 4.5)) \
                              if i > count/2 else (random.uniform(10, 1), 6, random.uniform(-4.5, 4.5))
                else:
                    radius = (random.uniform(-10,1),
                              6,
                              random.uniform(-8,8)) \
                              if i > count/2 else (random.uniform(10, 1), 6, random.uniform(-8, 8))

                Boxes(
                    position=radius,
                    graphics=self.settings['Graphics'],
                    randomColor=self.settings['Random obstacles color'],
                    mirror=self.settings['Obstacles mirror shots'],
                    form=self.settings['Obstacles form']).autoRetain()

        if self.settings['Graphics'] == 2:
            bsGlobals.tint = (bsGlobals.tint[0]-0.6, bsGlobals.tint[1]-0.6, bsGlobals.tint[2]-0.6)
            light = bs.newNode('light', attrs={
                'position': (9, 10, 0) if map == 'Football Stadium' else (6, 7, -2) \
                    if not map == 'Rampage' else (6, 11, -2) if not map == 'The Pad' else (6, 8.5, -2),
                'color': (0.4, 0.4, 0.45),
                'radius': 1,
                'intensity': 6,
                'volumeIntensityScale': 10.0})

            light2 = bs.newNode('light', attrs={
                'position': (-9, 10, 0) if map == 'Football Stadium' else (-6, 7, -2) \
                    if not map == 'Rampage' else (-6, 11, -2) if not map == 'The Pad' else (-6, 8.5, -2),
                'color': (0.4, 0.4, 0.45),
                'radius': 1,
                'intensity': 6,
                'volumeIntensityScale': 10.0})

        if len(self.teams) > 0:
            self._scoreToWin = self.settings['Kills to Win Per Player']*max(1, max(len(t.players) for t in self.teams))
        else: 
            self._scoreToWin = self.settings['Kills to Win Per Player']

        self._updateScoreBoard()
        self._dingSound = bs.getSound('dingSmall')

    def dropShield(self):
        p = bs.Powerup(
            powerupType='shield',
            position=(random.uniform(-10, 10), 6, random.uniform(-5, 5))).autoRetain()

        bs.playSound(bs.getSound('dingSmall'))

        pLight = bs.newNode('light', attrs={
            'position': (0, 0, 0),
            'color': (0.3, 0.0, 0.4),
            'radius': 0.3,
            'intensity': 2,
            'volumeIntensityScale': 10.0})

        p.node.connectAttr('position', pLight, 'position')

        bs.animate(pLight, 'intensity', {0: 2, 8000: 0})

        def checkExists():
            if p is None or p.node.exists() == False:
                deletepLight()
                delChecker()

        self._checker = bs.Timer(100,bs.Call(checkExists), repeat=True)

        def delChecker():
            if self._checker is not None:
                self._checker = None

        def deletepLight():
            if pLight.exists():
                pLight.delete()

        bs.gameTimer(6900, bs.Call(delChecker))
        bs.gameTimer(7000, bs.Call(deletepLight))

    def spawnPlayer(self,player):
        spaz = self.spawnPlayerSpaz(player)
        quakeBall.QuakeBallFactory().give(spaz)
        spaz.connectControlsToPlayer(
            enableJump=self.settings['Enable jump'],
            enablePunch=True,
            enablePickUp=self.settings['Enable pickup'],
            enableBomb=self.settings['Enable bomb'],
            enableRun=True,
            enableFly=False)

        if self.settings['Speed']: spaz.node.hockey = True
        spaz.spazLight = bs.newNode('light', attrs={
            'position': (0, 0, 0),
            'color': spaz.node.color,
            'radius': 0.12,
            'intensity': 1,
            'volumeIntensityScale': 10.0})

        spaz.node.connectAttr('position', spaz.spazLight, 'position')

        def checkExistsSpaz():
            if spaz.node.exists():
                bs.gameTimer(10, bs.Call(checkExistsSpaz))
            else:
                spaz.spazLight.delete()

        checkExistsSpaz()

    def handleMessage(self, m):
        if isinstance(m, bs.PlayerSpazDeathMessage):
            bs.TeamGameActivity.handleMessage(self, m) # augment standard behavior
            player = m.spaz.getPlayer()
            self.respawnPlayer(player)
            killer = m.killerPlayer
            if killer is None: return

            # handle team-kills
            if killer.getTeam() is player.getTeam():
                # in free-for-all, killing yourself loses you a point
                if isinstance(self.getSession(),bs.FreeForAllSession):
                    newScore = player.getTeam().gameData['score'] - 1
                    newScore = max(0, newScore)
                    player.getTeam().gameData['score'] = newScore
                # in teams-mode it gives a point to the other team
                else:
                    bs.playSound(self._dingSound)
                    for team in self.teams:
                        if team is not killer.getTeam():
                            team.gameData['score'] += 1
            # killing someone on another team nets a kill
            else:
                killer.getTeam().gameData['score'] += 1
                bs.playSound(self._dingSound)
                # in FFA show our score since its hard to find on the scoreboard
                try: killer.actor.setScoreText(
                    str(killer.getTeam().gameData['score'])+'/'+str(self._scoreToWin),
                    color=killer.getTeam().color,
                    flash=True)
                except Exception: pass

            self._updateScoreBoard()

            # if someone has won, set a timer to end shortly
            # (allows the dust to clear and draws to occur if deaths are close enough)
            if any(team.gameData['score'] >= self._scoreToWin for team in self.teams):
                bs.gameTimer(500, self.endGame)

        else: bs.TeamGameActivity.handleMessage(self, m)

    def _updateScoreBoard(self):
        for team in self.teams:
            self._scoreBoard.setTeamValue(
                team, team.gameData['score'], self._scoreToWin)

    def endGame(self):
        results = bs.TeamGameResults()
        for t in self.teams:
            results.setTeamScore(t, t.gameData['score'])

        self.end(results=results)

class Boxes(bs.Actor):

    def __init__(self, position=(0, 1, 0), graphics=2,
                 randomColor=True, mirror=False, form=0):
        bs.Actor.__init__(self)

        if form == 0:
            model = 'tnt'
            body = 'crate'
        elif form == 1:
            model = 'bomb'
            body = 'sphere'
        elif form == 2:
            model = random.choice(['tnt', 'bomb'])
            body = 'sphere' if model == 'bomb' else 'crate'

        self.node = bs.newNode('prop', delegate=self, attrs={
            'position': position,
            'model': bs.getModel(model),
            'body': body,
            'bodyScale': 1.3,
            'modelScale': 1.3,
            'reflection': 'powerup',
            'reflectionScale': [0.7],
            'colorTexture': bs.getTexture('bunnyColor'),
            'materials': [bs.getSharedObject('footingMaterial')] if mirror else [bs.getSharedObject('objectMaterial'),
                          bs.getSharedObject('footingMaterial')]})

        if graphics == 2:             
            self.lightNode = bs.newNode('light', attrs={
                'position': (0, 0, 0),
                'color': ((0.8, 0.2, 0.2) if i < count/2 else (0.2, 0.2, 0.8)) \
                    if not randomColor else ((random.random(), random.random(), random.random())),
                'radius': 0.2,
                'intensity': 1,
                'volumeIntensityScale': 10.0})

            self.node.connectAttr('position', self.lightNode, 'position')

    def handleMessage(self, m):
        if isinstance(m, bs.DieMessage):
            if self.node.exists():
                self.node.delete()
                self.lightNode.delete()

        elif isinstance(m, bs.OutOfBoundsMessage):
            if self.node.exists():
                self.handleMessage(bs.DieMessage())

        elif isinstance(m, bs.HitMessage):
            self.node.handleMessage('impulse', m.pos[0], m.pos[1], m.pos[2],
                                    m.velocity[0], m.velocity[1], m.velocity[2],
                                    m.magnitude, m.velocityMagnitude, m.radius,0,
                                    m.velocity[0], m.velocity[1], m.velocity[2])