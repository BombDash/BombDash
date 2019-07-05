#Made by Froshlee14
import bsPowerup
import bs
import random

def bsGetAPIVersion():
    return 4

def bsGetGames():
    return [PowerUpShowerGame]

class PowerUpShowerGame(bs.TeamGameActivity):

    @classmethod
    def getName(cls):
        return 'PowerUp Shower'

    @classmethod
    def getScoreInfo(cls):
        return {'scoreName':'Survived',
                'scoreType':'milliseconds',
                'scoreVersion':'B'}

    @classmethod
    def getDescription(cls,sessionType):
        return 'Becareful with the curse powerups.'
        

    @classmethod
    def getSupportedMaps(cls,sessionType):
        return ['Rampage']

    @classmethod
    def getSettings(cls,sessionType):
        return [("Epic Mode",{'default':False}),("Survive Mode",{'default':False})]

    @classmethod
    def supportsSessionType(cls,sessionType):
        return True if (issubclass(sessionType,bs.TeamsSession)
                        or issubclass(sessionType,bs.FreeForAllSession)
                        or issubclass(sessionType,bs.CoopSession)) else False

    def __init__(self,settings):
        bs.TeamGameActivity.__init__(self,settings)

        if self.settings['Epic Mode']: self._isSlowMotion = True

        self.announcePlayerDeaths = True

        self._lastPlayerDeathTime = None

    def onTransitionIn(self):
        bs.TeamGameActivity.onTransitionIn(self, music='Epic' if self.settings['Epic Mode'] else 'Survival')

    def onBegin(self):
        bs.TeamGameActivity.onBegin(self)
        self._meteorTime = 3000
        t = 7500 if len(self.players) > 2 else 4000
        if self.settings['Epic Mode']: t /= 4
        bs.gameTimer(t,self._decrementMeteorTime,repeat=True)

        t = 3000
        if self.settings['Epic Mode']: t /= 4
        bs.gameTimer(t,self._setMeteorTimer)

        self._timer = bs.OnScreenTimer()
        self._timer.start()

    def spawnPlayer(self,player):
        if self.settings['Survive Mode']:
         spaz = self.spawnPlayerSpaz(player)
         spaz.connectControlsToPlayer(enablePunch=False,
                                      enableBomb=False,
                                      enablePickUp=False)
        else:
         spaz = self.spawnPlayerSpaz(player)
         spaz.connectControlsToPlayer(enablePunch=False,
                                      enableBomb=True,
                                      enablePickUp=True)

        spaz.playBigDeathSound = True

    def handleMessage(self,m):

        if isinstance(m,bs.PlayerSpazDeathMessage):

            bs.TeamGameActivity.handleMessage(self,m)

            deathTime = bs.getGameTime()

            m.spaz.getPlayer().gameData['deathTime'] = deathTime

            if isinstance(self.getSession(),bs.CoopSession):
                bs.pushCall(self._checkEndGame)
                self._lastPlayerDeathTime = deathTime
            else:
                bs.gameTimer(1000,self._checkEndGame)

        else:
            bs.TeamGameActivity.handleMessage(self,m)

    def _checkEndGame(self):
        livingTeamCount = 0
        for team in self.teams:
            for player in team.players:
                if player.isAlive():
                    livingTeamCount += 1
                    break

        if isinstance(self.getSession(),bs.CoopSession):
            if livingTeamCount <= 0: self.endGame()
        else:
            if livingTeamCount <= 1: self.endGame()

    def _setMeteorTimer(self):
        bs.gameTimer(int((0.1+0.01*random.random())*self._meteorTime),self._dropBombCluster)

    def _dropBombCluster(self):

        if False:
            bs.newNode('locator',attrs={'position':(8,6,-5.5)})
            bs.newNode('locator',attrs={'position':(8,6,-2.3)})
            bs.newNode('locator',attrs={'position':(-7.3,6,-5.5)})
            bs.newNode('locator',attrs={'position':(-7.3,6,-2.3)})

        delay = 0
        for i in range(random.randrange(1,3)):
            if self.settings['Survive Mode']:
             types = [ "curse","health","curse","curse"]
            else:
             types = [ "curse","health","shield","punch","curse" ,"impactBombs","iceBombs","stickyBombs","landMines","tripleBombs"]
            magic = random.choice(types)
            pt = magic
            pos = (-7.3+15.3*random.random(),11,-5.5+2.1*random.random())
            bs.gameTimer(delay,bs.Call(self._dropPowerUp,pos,pt))
            delay += 100
        self._setMeteorTimer()

    def _dropPowerUp(self,position,powerupType):
        bsPowerup.Powerup(position=position, powerupType=powerupType,expire=True).autoRetain()

    def _decrementMeteorTime(self):
        self._meteorTime = max(10,int(self._meteorTime*0.9))

    def endGame(self):

        curTime = bs.getGameTime()

        for team in self.teams:
            for player in team.players:

                if 'deathTime' not in player.gameData: player.gameData['deathTime'] = curTime+1

                score = (player.gameData['deathTime']-self._timer.getStartTime())/1000
                if 'deathTime' not in player.gameData: score += 50
                self.scoreSet.playerScored(player,score,screenMessage=False)

        self._timer.stop(endTime=self._lastPlayerDeathTime)

        results = bs.TeamGameResults()

        for team in self.teams:

            longestLife = 0
            for player in team.players:
                longestLife = max(longestLife,(player.gameData['deathTime'] - self._timer.getStartTime()))
            results.setTeamScore(team,longestLife)

        self.end(results=results)