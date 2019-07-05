import bs
import random

def bsGetAPIVersion():
    # see bombsquadgame.com/apichanges
    return 4

def bsGetGames():
    return [BasketballGame]

class PuckDeathMessage(object):
    def __init__(self,puck):
        self.puck = puck

class Ball(bs.Actor):

    def __init__(self,position=(0,1,0)):
        bs.Actor.__init__(self)

        activity = self.getActivity()
        
        # spawn just above the provided point
        self._spawnPos = (position[0],position[1]+1.0,position[2])
        self.lastPlayersToTouch = {}
        self.node = bs.newNode("prop",
                               attrs={'model': activity._puckModel,
                                      'colorTexture': activity._puckTex,
                                      'body':'sphere',
                                      'reflection':'soft',
                                      'reflectionScale':[0.2],
                                      'shadowSize': 0.6,
                                      'isAreaOfInterest':True,
                                      'position':self._spawnPos,
                                      'materials': [bs.getSharedObject('objectMaterial'),activity._puckMaterial]
                                      },
                               delegate=self)
                               
        self.shield = bs.newNode('shield',attrs={'color':(1+random.random()*3,1+random.random()*3,1+random.random()*3),'radius':0.6})
        self.node.connectAttr('position',self.shield,'position')

    def handleMessage(self,m):
        if isinstance(m,bs.DieMessage):
            self.node.delete()
            activity = self._activity()
            if activity and not m.immediate:
                activity.handleMessage(PuckDeathMessage(self))

        # if we go out of bounds, move back to where we started...
        elif isinstance(m,bs.OutOfBoundsMessage):
            self.node.handleMessage(bs.DieMessage())

        elif isinstance(m,bs.HitMessage):
            self.node.handleMessage("impulse",m.pos[0],m.pos[1],m.pos[2],
                                    m.velocity[0],m.velocity[1],m.velocity[2],
                                    1.0*m.magnitude,1.0*m.velocityMagnitude,m.radius,0,
                                    m.forceDirection[0],m.forceDirection[1],m.forceDirection[2])

            # if this hit came from a player, log them as the last to touch us
            if m.sourcePlayer is not None:
                activity = self._activity()
                if activity:
                    if m.sourcePlayer in activity.players:
                        self.lastPlayersToTouch[m.sourcePlayer.getTeam().getID()] = m.sourcePlayer
        else:
            bs.Actor.handleMessage(self,m)


class BasketballGame(bs.TeamGameActivity):

    @classmethod
    def getName(cls):
        return 'Basketball'

    @classmethod
    def getDescription(cls,sessionType):
        return 'Throw the ball in ring!'

    @classmethod
    def supportsSessionType(cls,sessionType):
        return True if issubclass(sessionType,bs.TeamsSession) else False

    @classmethod
    def getSupportedMaps(cls,sessionType):
        return bs.getMapsSupportingPlayType('basketball')

    @classmethod
    def getSettings(cls,sessionType):
        return [("Time Limit",{'choices':[('None',0),('1 Minute',60),
                                          ('2 Minutes',120),('5 Minutes',300),
                                          ('10 Minutes',600),('20 Minutes',1200)],'default':0}),
                ("Respawn Times",{'choices':[('Shorter',0.25),('Short',0.5),('Normal',1.0),('Long',2.0),('Longer',4.0)],'default':1.0})]

    def __init__(self,settings):
        bs.TeamGameActivity.__init__(self,settings)
        self._scoreBoard = bs.ScoreBoard()

        self._cheerSound = bs.getSound("cheer")
        self._chantSound = bs.getSound("crowdChant")
        self._foghornSound = bs.getSound("foghorn")
        self._swipSound = bs.getSound("swip")
        self._whistleSound = bs.getSound("refWhistle")
        self._puckModel = None
        self._puckTex = bs.getTexture("basketballball")
        self._puckSound = bs.getSound("glass")

        self._puckMaterial = bs.Material()
        self._puckMaterial.addActions(conditions=("theyHaveMaterial",bs.getSharedObject('pickupMaterial')),
                                      actions=( ("modifyPartCollision","collide",True) ) )
        self._puckMaterial.addActions(conditions=( ("weAreYoungerThan",100),'and',
                                                   ("theyHaveMaterial",bs.getSharedObject('objectMaterial')) ),
                                      actions=( ("modifyNodeCollision","collide",True) ) )
        self._puckMaterial.addActions(actions=(("impactSound",self._puckSound,0.2,1)))
        # keep track of which player last touched the puck
        self._puckMaterial.addActions(conditions=("theyHaveMaterial",bs.getSharedObject('playerMaterial')),
                                      actions=(("call","atConnect",self._handlePuckPlayerCollide),))
        # we want the puck to kill powerups; not get stopped by them
        self._puckMaterial.addActions(conditions=("theyHaveMaterial",bs.Powerup.getFactory().powerupMaterial),
                                      actions=(("modifyPartCollision","physical",True),
                                               ("message","theirNode","atConnect",bs.DieMessage())))
        self._scoreRegionMaterial = bs.Material()
        self._scoreRegionMaterial.addActions(conditions=("theyHaveMaterial",self._puckMaterial),
                                             actions=(("modifyPartCollision","collide",True),
                                                      ("modifyPartCollision","physical",False),
                                                      ("call","atConnect",self._handleScore)))

    def getInstanceDescription(self):
        return 'Score as many goals!'

    def getInstanceScoreBoardDescription(self):
        return 'Score as many goals!'
        # return 'score '+ str(s)+' goal'+('s' if s > 1 else '')

    def onTransitionIn(self):
        bs.TeamGameActivity.onTransitionIn(self, music='Hockey')

    def onBegin(self):
        bs.TeamGameActivity.onBegin(self)

        self.setupStandardTimeLimit(self.settings['Time Limit'])
        self.setupStandardPowerupDrops()

        self._puckSpawnPos = self.getMap().getFlagPosition(None)
        self._spawnPuck()

        # set up the two score regions
        defs = self.getMap().defs
        self._scoreRegions = []
        self._scoreRegions.append(bs.NodeActor(bs.newNode("region",
                                                          attrs={'position':defs.boxes["goal1"][0:3],
                                                                 'scale':defs.boxes["goal1"][6:9],
                                                                 'type':"box",
                                                                 'materials':[self._scoreRegionMaterial]})))
        
        self._scoreRegions.append(bs.NodeActor(bs.newNode("region",
                                                          attrs={'position':defs.boxes["goal2"][0:3],
                                                                 'scale':defs.boxes["goal2"][6:9],
                                                                 'type':"box",
                                                                 'materials':[self._scoreRegionMaterial]})))
        self._updateScoreBoard()

        bs.playSound(self._chantSound)

    def onTeamJoin(self,team):
        team.gameData['score'] = 0
        self._updateScoreBoard()

    def _handlePuckPlayerCollide(self):
        try:
            puckNode,playerNode = bs.getCollisionInfo('sourceNode','opposingNode')
            puck = puckNode.getDelegate()
            player = playerNode.getDelegate().getPlayer()
        except Exception: player = puck = None

        if player is not None and player.exists() and puck is not None: puck.lastPlayersToTouch[player.getTeam().getID()] = player

    def _killPuck(self):
        self._puck = None

    def _handleScore(self):
        """ a point has been scored """

        # our puck might stick around for a second or two
        # we dont want it to be able to score again
        if self._puck.scored: return

        region = bs.getCollisionInfo("sourceNode")
        for i in range(len(self._scoreRegions)):
            if region == self._scoreRegions[i].node:
                break;

        scoringTeam = None
        for team in self.teams:
            if team.getID() == i:
                scoringTeam = team
                team.gameData['score'] += 1

                # tell all players to celebrate
                for player in team.players:
                    try: player.actor.node.handleMessage('celebrate',2000)
                    except Exception: pass

                # if weve got the player from the scoring team that last touched us, give them points
                if scoringTeam.getID() in self._puck.lastPlayersToTouch and self._puck.lastPlayersToTouch[scoringTeam.getID()].exists():
                    self.scoreSet.playerScored(self._puck.lastPlayersToTouch[scoringTeam.getID()],100,bigMessage=True)

                # end game if we won
                    

        bs.playSound(self._foghornSound)
        bs.playSound(self._cheerSound)

        self._puck.scored = True

        bs.gameTimer(1000,self._reactivatePuck)

        light = bs.newNode('light',
                           attrs={'position': bs.getCollisionInfo('position'),
                                  'heightAttenuated':False,
                                  'color': (1,0,0)})
        bs.animate(light,'intensity',{0:0,500:1,1000:0},loop=True)
        bs.gameTimer(1000,light.delete)

        self.cameraFlash(duration=10)
        self._updateScoreBoard()
    
    def _reactivatePuck(self):
        self._puck.scored = False

    def endGame(self):
        results = bs.TeamGameResults()
        for t in self.teams: results.setTeamScore(t,t.gameData['score'])
        self.end(results=results)

    def _updateScoreBoard(self):
        """ update scoreboard and check for winners """
        winScore = 1
        for team in self.teams:
            self._scoreBoard.setTeamValue(team,team.gameData['score'])

    def handleMessage(self,m):

        # respawn dead players if they're still in the game
        if isinstance(m,bs.PlayerSpazDeathMessage):
            bs.TeamGameActivity.handleMessage(self,m) # augment standard behavior
            self.respawnPlayer(m.spaz.getPlayer())
        # respawn dead pucks
        elif isinstance(m,PuckDeathMessage):
            if not self.hasEnded():
                bs.gameTimer(3000,self._spawnPuck)
        else:
            bs.TeamGameActivity.handleMessage(self,m)

    def _flashPuckSpawn(self):
        light = bs.newNode('light',
                           attrs={'position': self._puckSpawnPos,
                                  'heightAttenuated':False,
                                  'color': (1,0,0)})
        bs.animate(light,'intensity',{0:0,250:1,500:0},loop=True)
        bs.gameTimer(1000,light.delete)

    def _spawnPuck(self):
        bs.playSound(self._swipSound)
        bs.playSound(self._whistleSound)
        self._flashPuckSpawn()

        self._puck = Ball(position=self._puckSpawnPos)
        self._puck.scored = False
        self._puck.lastHoldingPlayer = None
        self._puck.light = bs.newNode('light',
                                      owner=self._puck.node,
                                      attrs={'intensity':0.3,
                                             'heightAttenuated':False,
                                             'radius':0.2,
                                             'color': (0.3,0.0,1.0)})
        self._puck.node.connectAttr('position',self._puck.light,'position')

