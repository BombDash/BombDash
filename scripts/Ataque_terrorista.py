import bs
import random

def bsGetAPIVersion():
    return 4

def bsGetGames():
    return [AtaqueTerrorista]

class AtaqueTerrorista(bs.TeamGameActivity):

    @classmethod
    def getName(cls):
        return 'Ataque terrorista'

    @classmethod
    def getScoreInfo(cls):
        return {'scoreName':'Survived',
                'scoreType':'milliseconds',
                'scoreVersion':'B'}
    
    @classmethod
    def getDescription(cls,sessionType):
        return 'Corre por tu vida!'

    # we're currently hard-coded for one map..
    @classmethod
    def getSupportedMaps(cls,sessionType):
        return ['Courtyard','Doom Shroom']

    @classmethod
    def getSettings(cls,sessionType):
        return [("Epic Mode",{'default':False})]
    
    # we support teams, free-for-all, and co-op sessions
    @classmethod
    def supportsSessionType(cls,sessionType):
        return True if (issubclass(sessionType,bs.TeamsSession)
                        or issubclass(sessionType,bs.FreeForAllSession)
                        or issubclass(sessionType,bs.CoopSession)) else False

    def __init__(self,settings):
        bs.TeamGameActivity.__init__(self,settings)

        if self.settings['Epic Mode']: self._isSlowMotion = True
        
        # print messages when players die (since its meaningful in this game)
        self.announcePlayerDeaths = True

        self._lastPlayerDeathTime = None
        
    # called when our game is transitioning in but not ready to start..
    # ..we can go ahead and set our music and whatnot
    def onTransitionIn(self):
        bs.TeamGameActivity.onTransitionIn(self, music='Epic' if self.settings['Epic Mode'] else 'Survival')


    # called when our game actually starts
    def onBegin(self):

        bs.TeamGameActivity.onBegin(self)
        # drop a wave every few seconds.. and every so often drop the time between waves
        # ..lets have things increase faster if we have fewer players
        #self._meteorTime = 3000
        t = 7500 if len(self.players) > 2 else 4000
        if self.settings['Epic Mode']: t /= 4
        #bs.gameTimer(t,self._decrementMeteorTime,repeat=True)

        # kick off the first wave in a few seconds
        t = 3000
        if self.settings['Epic Mode']: t /= 4
        #bs.gameTimer(t,self._setMeteorTimer)
        bPos = self.getMap().defs.points['flagDefault'] #botSpawnTop
           # this wrangles our bots
        self._bots = bs.BotSet()

        # start some timers to spawn bots
        bs.gameTimer(1000,bs.Call(self._bots.spawnBot,bs.PirateBot,pos=bPos,spawnTime=3000))
        bs.gameTimer(1000,bs.Call(self._bots.spawnBot,bs.PirateBot,pos=bPos,spawnTime=5000))
        bs.gameTimer(1000,bs.Call(self._bots.spawnBot,bs.PirateBot,pos=bPos,spawnTime=7000))

        #bs.gameTimer(2000,bs.Call(self._bots.spawnBot,bs.PirateBot,pos=(-3,3,-2),spawnTime=3000))
        #bs.gameTimer(3000,bs.Call(self._bots.spawnBot,bs.NinjaBot,pos=(5,3,-2),spawnTime=3000))
        #bs.gameTimer(4000,bs.Call(self._bots.spawnBot,bs.NinjaBot,pos=(-5,3,-2),spawnTime=3000))

        # add a few extras for multiplayer
        if len(self.initialPlayerInfo) > 2:
            bs.gameTimer(1000,bs.Call(self._bots.spawnBot,bs.PirateBot,pos=bPos,spawnTime=9000))
            bs.gameTimer(1000,bs.Call(self._bots.spawnBot,bs.PirateBot,pos=bPos,spawnTime=11000))
        if len(self.initialPlayerInfo) > 5:
            bs.gameTimer(1000,bs.Call(self._bots.spawnBot,bs.PirateBot,pos=bPos,spawnTime=13000))
            bs.gameTimer(1000,bs.Call(self._bots.spawnBot,bs.PirateBot,pos=bPos,spawnTime=15000))

        # note: if spawns were spread out more we'd probably want to set some sort of flag on the
        # last spawn to ensure we don't inadvertantly allow a 'win' before every bot is spawned.
        # (ie: if bot 1, 2, and 3 got killed but 4 hadn't spawned yet, the game might end because
        # it sees no remaining bots.
        self._updateTimer = bs.Timer(1000,self._onSpazBotDied,repeat=True)
        
        self._timer = bs.OnScreenTimer()
        bs.gameTimer(4000,self._timer.start)
       
                
    # overriding the default character spawning..
    def spawnPlayer(self,player):
        pos = self.getMap().defs.points['flagDefault']
        spaz = self.spawnPlayerSpaz(player,position=pos)

        # lets reconnect this player's controls to this
        # spaz but *without* the ability to attack or pick stuff up
        spaz.connectControlsToPlayer(enablePunch=False,
                                     enableBomb=False,
                                     enablePickUp=False)

        # also lets have them make some noise when they die..
        spaz.playBigDeathSound = True

    # various high-level game events come through this method
    def handleMessage(self,m):

        if isinstance(m,bs.PlayerSpazDeathMessage):
            bs.TeamGameActivity.handleMessage(self,m) # (augment standard behavior)
            deathTime = bs.getGameTime()           
            # record the player's moment of death
            m.spaz.getPlayer().gameData['deathTime'] = deathTime
            # in co-op mode, end the game the instant everyone dies (more accurate looking)
            # in teams/ffa, allow a one-second fudge-factor so we can get more draws
            if isinstance(self.getSession(),bs.CoopSession):
                # teams will still show up if we check now.. check in the next cycle
                bs.pushCall(self._checkEndGame)
                self._lastPlayerDeathTime = deathTime # also record this for a final setting of the clock..
            else:
                bs.gameTimer(1000,self._checkEndGame)
        elif isinstance(m,bs.SpazBotDeathMessage):
            self._onSpazBotDied(m)
            bs.TeamGameActivity.handleMessage(self,m)
            #bs.PopupText("died",position=self._position,color=popupColor,scale=popupScale).autoRetain()  
        else:
            # default handler:
            bs.TeamGameActivity.handleMessage(self,m)

    def _onSpazBotDied(self,DeathMsg):
        x = random.uniform(-1.0,1.0)
        y = random.uniform(-1.0,1.0)
        self._bots.spawnBot(bs.PirateBot,pos=(8.0*x,3,5.0*y),spawnTime=1000)
        pos = DeathMsg.badGuy.node.position


    def _checkEndGame(self):
        livingTeamCount = 0
        for team in self.teams:
            for player in team.players:
                if player.isAlive():
                    livingTeamCount += 1
                    break

        # in co-op, we go till everyone is dead.. otherwise we go until one team remains
        if isinstance(self.getSession(),bs.CoopSession):
            if livingTeamCount <= 0: self.endGame()
        else:
            if livingTeamCount <= 1: self.endGame()
        
    def endGame(self):

        curTime = bs.getGameTime()
        
        # mark 'death-time' as now for any still-living players
        # and award players points for how long they lasted.
        # (these per-player scores are only meaningful in team-games)
        for team in self.teams:
            for player in team.players:

                # throw an extra fudge factor +1 in so teams that
                # didn't die come out ahead of teams that did
                if 'deathTime' not in player.gameData: player.gameData['deathTime'] = curTime+1
                    
                # award a per-player score depending on how many seconds they lasted
                # (per-player scores only affect teams mode; everywhere else just looks at the per-team score)
                score = (player.gameData['deathTime']-self._timer.getStartTime())/1000
                if 'deathTime' not in player.gameData: score += 50 # a bit extra for survivors
                self.scoreSet.playerScored(player,score,screenMessage=False)

        # stop updating our time text, and set the final time to match
        # exactly when our last guy died.
        self._timer.stop(endTime=self._lastPlayerDeathTime)
        
        # ok now calc game results: set a score for each team and then tell the game to end
        results = bs.TeamGameResults()

        # remember that 'free-for-all' mode is simply a special form of 'teams' mode
        # where each player gets their own team, so we can just always deal in teams
        # and have all cases covered
        for team in self.teams:

            # set the team score to the max time survived by any player on that team
            longestLife = 0
            for player in team.players:
                longestLife = max(longestLife,(player.gameData['deathTime'] - self._timer.getStartTime()))
            results.setTeamScore(team,longestLife)

        self.end(results=results)
