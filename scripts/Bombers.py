#Made by Froshlee14
import bs
import random

def bsGetAPIVersion():
    return 4

def bsGetGames():
    return [BombersGame] 

class BombersGame(bs.TeamGameActivity):

    @classmethod
    def getName(cls):
        return 'Bombers'

    @classmethod
    def getScoreInfo(cls):
        return {'scoreName':'Survived',
                'scoreType':'milliseconds',
                'scoreVersion':'B'}
    
    @classmethod
    def getDescription(cls,sessionType):
        return 'Move or die.'

    # we're currently hard-coded for one map..
    @classmethod
    def getSupportedMaps(cls,sessionType):
        return ['The Pad']

    @classmethod
    def getSettings(cls,sessionType):
        return [("Epic Mode",{'default':False}),("Bombers",{'minValue':4,'maxValue':20,'default':4,'increment':1})]
    
    # we support teams, free-for-all, and co-op sessions
    @classmethod
    def supportsSessionType(cls,sessionType):
        return True if (issubclass(sessionType,bs.TeamsSession)
                        or issubclass(sessionType,bs.FreeForAllSession)
                        or issubclass(sessionType,bs.CoopSession)) else False

    def __init__(self,settings):        
        bs.TeamGameActivity.__init__(self,settings)
        if self.settings['Epic Mode']: self._isSlowMotion=True
        self.announcePlayerDeaths = True
        self._lastPlayerDeathTime = None

        #A safe zone from player              
        self.safeRegionMaterial = bs.Material()
        self.safeRegionMaterial.addActions(
            conditions=("theyHaveMaterial",bs.getSharedObject('playerMaterial')),
            actions=(("modifyPartCollision","collide",True),
                     ("modifyPartCollision","physical",True)))

    def onTransitionIn(self):
        bs.TeamGameActivity.onTransitionIn(self, music='Epic' if self.settings['Epic Mode'] else 'Scary')

    # called when our game actually starts
    def onBegin(self):
        bs.TeamGameActivity.onBegin(self)
        self._bots = bs.BotSet()

        pt1 = (6.972673935, 4.380775486, -9.424407061)
        pt2 = (-6.972673935, 4.380775486, -9.424407061)
        pt3 = (6.972673935, 4.380775486, 3.424407061)
        pt4 = (-6.972673935, 4.380775486, 3.424407061)

        for i in range(self.settings['Bombers']):
         bs.gameTimer(1000,bs.Call(self._bots.spawnBot,bs.BomberBotStatic,pos=random.choice([pt1,pt2,pt3,pt4]),spawnTime=3000))

        self._scoreRegions = []
        self._scoreRegions.append(bs.NodeActor(bs.newNode('region',
                                                          attrs={'position':(0.3, 4.044276501, -2.9),
                                                                 'scale':(11.7,15,9.5),
                                                                 'type': 'box',
                                                                 'materials':(self.safeRegionMaterial,)})))
        self._timer = bs.OnScreenTimer()
        bs.gameTimer(4000,self._timer.start)
        self._updateTimer = bs.Timer(1000,self._onSpazBotDied,repeat=True)
        
    def spawnPlayer(self,player):
        pos = (0.4599593402, 4.044276501, -2.7)
        spaz = self.spawnPlayerSpaz(player,position=pos)
        spaz.connectControlsToPlayer(enablePunch=False,
                                     enableBomb=False,
                                     enablePickUp=False)
        spaz.playBigDeathSound = True

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
        pt1 = (6.972673935, 4.380775486, -9.424407061)
        pt2 = (-6.972673935, 4.380775486, -9.424407061)
        pt3 = (6.972673935, 4.380775486, 3.424407061)
        pt4 = (-6.972673935, 4.380775486, 3.424407061)
        bPos = random.choice([pt1,pt2,pt3,pt4])
        self._bots.spawnBot(bs.BomberBotStatic,pos=bPos,spawnTime=2000)

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
