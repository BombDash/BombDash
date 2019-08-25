import sys
import time
import random
import bs
import bsUtils
import bsVector
import bdUtils
import settings


_maps = {}

def preloadPreviewMedia():
    bs.getModel('levelSelectButtonOpaque')
    bs.getModel('levelSelectButtonTransparent')
    for m in _maps.values():
        mapTexName = m.getPreviewTextureName()
        if mapTexName is not None: bs.getTexture(mapTexName)
    
def registerMap(m):
    """ Register a map class with the game. """
    if _maps.has_key(m.name):
        raise Exception("map \"" + m.name + "\" already registered")
    _maps[m.name] = m

def getFilteredMapName(name):
    """ filters a map name to account for name changes, etc
    so old configs still work """
    # some legacy name fallbacks... can remove these eventually
    if name == 'AlwaysLand' or name == 'Happy Land': name = u'Happy Thoughts'
    if name == 'Hockey Arena': name = u'Hockey Stadium'
    return name

def getMapDisplayString(name):
    return bs.Lstr(translate=('mapsNames', name))

def getMapsSupportingPlayType(playType):
    """
    category: Media Functions

    Return a list of bs.Map types supporting a specified play-type (a string).
    Maps supporting a given play-type must provide a particular set of
    features or lend themselves to a certain style of play.

    Play Types:
    
    'melee' - general fighting map - has 2+ 'spawn' pts, 1+ 'powerupSpawn' pts

    'teamFlag' - for CTF, etc - has 2+ 'spawn' pts,
                 2+ 'flag' pts, and 1+ 'powerupSpawn' pts

    'keepAway'- has 2+ 'spawn' pts, 1+ 'flagDefault' pts,
                and 1+ 'powerupSpawn' pts

    'conquest' - has 2+ 'flag' pts, 2+ 'spawnByFlag' pts,
                 and 1+ 'powerupSpawn' pts

    'kingOfTheHill' - has 2+ 'spawn' pts, 1+ 'flagDefault' pts,
                      and 1+ 'powerupSpawn' pts

    'hockey' - has 2 'goal' pts, 2+ 'spawn' pts, 1+ 'flagDefault' pts,
               1+ 'powerupSpawn' pts

    'football' - has 2 'goal' pts, 2+ 'spawn' pts, 1+ 'flagDefault' pts,
                 1+ 'powerupSpawn' pts
    
    'race' - has 2+ 'racePoint' pts
    """
    maps = [m[0] for m in _maps.items() if playType in m[1].playTypes]
    maps.sort()
    return maps

def _getUnOwnedMaps():
    import bsUI
    import bsInternal
    unOwnedMaps = set()
    if bs.getEnvironment()['subplatform'] != 'headless':
        for mapSection in bsUI._getStoreLayout()['maps']:
            for m in mapSection['items']:
                if not bsInternal._getPurchased(m):
                    mInfo = bsUI._getStoreItem(m)
                    unOwnedMaps.add(mInfo['mapType'].name)
    return unOwnedMaps

def getMapClass(name):
    """ return a map type given a name """
    name = getFilteredMapName(name)
    try: return _maps[name]
    except Exception: raise Exception("Map not found: '"+name+"'")
    
class Map(bs.Actor):
    """
    category: Game Flow Classes

    A collection of terrain nodes, metadata, and other
    functionality comprising a game map.
    """
    defs = None
    name = "Map"
    playTypes = []

    @classmethod
    def preload(cls,onDemand=False):
        """ Preload map media.
        This runs the class's onPreload function if need be to prep it to run.
        Preloading can be fired for a soon-needed map to speed its creation.
        This is a classmethod since it is not run on map instances but rather on
        the class as a whole before instances are made"""
        # store whether we're preloaded in the current activity
        activity = bs.getActivity()
        if activity is None: raise Exception("not in an activity")
        try: preloads = activity._mapPreloadData
        except Exception: preloads = activity._mapPreloadData = {}
        if not cls.name in preloads:
            if onDemand:
                print 'WARNING: map '+cls.name+(' was not preloaded; you can '
                                                'reduce hitches by preloading'
                                                ' your map.')
            preloads[cls.name] = cls.onPreload()
        return preloads[cls.name]

    @classmethod
    def getPreviewTextureName(cls):
        """
        Return the name of the preview texture for this map.
        """
        return None

    @classmethod
    def onPreload(cls):
        """
        Called when the map is being preloaded;
        it should load any media it requires to
        class attributes on itself.
        """
        pass

    @classmethod
    def getName(cls):
        """
        Return the unique name of this map, in English.
        """
        return cls.name

    @classmethod
    def getMusicType(cls):
        """
        Returns a particular music-type string that should be played on
        this map; or None if the default music should be used.
        """
        return None

    def __init__(self, vrOverlayCenterOffset=None):
        """
        Instantiate a map.
        """
        import bsInternal
        bs.Actor.__init__(self)
        self.preloadData = self.preload(onDemand=True)
        
        # set some defaults
        bsGlobals = bs.getSharedObject('globals')
        # area-of-interest bounds
        aoiBounds = self.getDefBoundBox("areaOfInterestBounds")
        if aoiBounds is None:
            print 'WARNING: no "aoiBounds" found for map:',self.getName()
            aoiBounds = (-1,-1,-1,1,1,1)
        bsGlobals.areaOfInterestBounds = aoiBounds
        # map bounds
        mapBounds = self.getDefBoundBox("levelBounds")
        if mapBounds is None:
            print 'WARNING: no "levelBounds" found for map:',self.getName()
            mapBounds = (-30,-10,-30,30,100,30)
        bsInternal._setMapBounds(mapBounds)
        # shadow ranges
        try: bsGlobals.shadowRange = [
                self.defs.points[v][1] for v in 
                ['shadowLowerBottom','shadowLowerTop',
                 'shadowUpperBottom','shadowUpperTop']]
        except Exception: pass
        # in vr, set a fixed point in space for the overlay to show up at..
        # by default we use the bounds center but allow the map to override it
        center = ((aoiBounds[0]+aoiBounds[3])*0.5,
                  (aoiBounds[1]+aoiBounds[4])*0.5,
                  (aoiBounds[2]+aoiBounds[5])*0.5)
        if vrOverlayCenterOffset is not None:
            center = (center[0]+vrOverlayCenterOffset[0],
                      center[1]+vrOverlayCenterOffset[1],
                      center[2]+vrOverlayCenterOffset[2])
        bsGlobals.vrOverlayCenter = center
        bsGlobals.vrOverlayCenterEnabled = True
        self.spawnPoints = self.getDefPoints("spawn") or [(0,0,0,0,0,0)]
        self.ffaSpawnPoints = self.getDefPoints("ffaSpawn") or [(0,0,0,0,0,0)]
        self.spawnByFlagPoints = (self.getDefPoints("spawnByFlag")
                                  or [(0,0,0,0,0,0)])
        self.flagPoints = self.getDefPoints("flag") or [(0,0,0)]
        self.flagPoints = [p[:3] for p in self.flagPoints] # just want points
        self.flagPointDefault = self.getDefPoint("flagDefault") or (0,1,0)
        self.powerupSpawnPoints = self.getDefPoints("powerupSpawn") or [(0,0,0)]
        self.powerupSpawnPoints = \
            [p[:3] for p in self.powerupSpawnPoints] # just want points
        self.tntPoints = self.getDefPoints("tnt") or []
        self.tntPoints = [p[:3] for p in self.tntPoints] # just want points
        self.isHockey = False
        self.isFlying = False
        self._nextFFAStartIndex = 0

    def _isPointNearEdge(self,p,running=False):
        "For bot purposes.."
        return False

    def getDefBoundBox(self,name):
        """Returns a 6 member bounds tuple or None if it is not defined."""
        try:
            b = self.defs.boxes[name]
            return (b[0]-b[6]/2.0,b[1]-b[7]/2.0,b[2]-b[8]/2.0,
                    b[0]+b[6]/2.0,b[1]+b[7]/2.0,b[2]+b[8]/2.0);
        except Exception:
            return None
        
    def getDefPoint(self,name):
        """Returns a single defined point or a default value in its absence."""
        try:
            return self.defs.points[name]
        except Exception:
            return None

    def getDefPoints(self,name):
        """
        Returns a list of points - as many sequential ones are defined
        (flag1, flag2, flag3), etc.
        """
        if self.defs and self.defs.points.has_key(name+"1"):
            pointList = []
            i = 1
            while self.defs.points.has_key(name+str(i)):
                p = self.defs.points[name+str(i)]
                if len(p) == 6:
                    pointList.append(p)
                else:
                    if len(p) != 3: raise Exception("invalid point")
                    pointList.append(p+(0,0,0))
                i += 1
            return pointList
        else:
            return None
        
    def getStartPosition(self,teamIndex):
        """
        Returns a random starting position in the map for the given team index.
        """
        pt = self.spawnPoints[teamIndex%len(self.spawnPoints)]
        xRange = (-0.5,0.5) if pt[3] == 0 else (-pt[3],pt[3])
        zRange = (-0.5,0.5) if pt[5] == 0 else (-pt[5],pt[5])
        pt = (pt[0]+random.uniform(*xRange),
              pt[1], pt[2]+random.uniform(*zRange))
        return pt

    def getFFAStartPosition(self,players):
        """
        Returns a random starting position in one of the FFA spawn areas.
        If a list of bs.Players is provided; the returned points will be
        as far from these players as possible.
        """
        # get positions for existing players
        playerPts = []
        for player in players:
            try:
                if player.actor is not None and player.actor.isAlive():
                    pt = bsVector.Vector(*player.actor.node.position)
                    playerPts.append(pt)
            except Exception,e:
                print 'EXC in getFFAStartPosition:',e

        def _getPt():
            pt = self.ffaSpawnPoints[self._nextFFAStartIndex]
            self._nextFFAStartIndex = ((self._nextFFAStartIndex+1)
                                       %len(self.ffaSpawnPoints))
            xRange = (-0.5, 0.5) if pt[3] == 0 else (-pt[3], pt[3])
            zRange = (-0.5, 0.5) if pt[5] == 0 else (-pt[5], pt[5])
            pt = (pt[0]+random.uniform(*xRange), pt[1],
                  pt[2]+random.uniform(*zRange))
            return pt

        if len(playerPts) == 0:
            return _getPt()
        else:
            # lets calc several start points and then pick whichever is
            # farthest from all existing players
            farthestPtDist = -1.0
            farthestPt = None
            for i in range(10):
                testPt = bsVector.Vector(*_getPt())
                closestPlayerDist = 9999.0
                closestPlayerPt = None
                for pp in playerPts:
                    dist = (pp-testPt).length()
                    if dist < closestPlayerDist:
                        closestPlayerDist = dist
                        closestPlayerPt = pp
                if closestPlayerDist > farthestPtDist:
                    farthestPtDist = closestPlayerDist
                    farthestPt = testPt
            return tuple(farthestPt.data)

    def getFlagPosition(self,teamIndex):
        """
        Return a flag position on the map for the given team index.
        Pass None to get the default flag point.
        (used for things such as king-of-the-hill)
        """
        if teamIndex is None:
            return self.flagPointDefault[:3]
        else:
            return self.flagPoints[teamIndex%len(self.flagPoints)][:3]

    def handleMessage(self, msg):
        if isinstance(msg, bs.DieMessage): self.node.delete()
        else: bs.Actor.handleMessage(self, msg)

######### now lets go ahead and register some maps #########

class PhoneMap(Map):
    import playgroundDefs as defs
    name = "Playground"

    playTypes = ['melee', 'football', 'teamFlag', 'keepAway']

    @classmethod
    def getPreviewTextureName(cls):
        return 'playgroundPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = [bs.getModel("phoneMap"),
                         bs.getModel("phoneScreen"),
                         bs.getModel("phoneBottom")]

        data['tex'] = [bs.getTexture("phoneMap"),
                       bs.getTexture('courtyardLevelColor'),
                       bs.getTexture('phoneScreen')]

        data['collideModel'] = bs.getCollideModel("phoneMap")
        data['bgmodel'] = [bs.getModel('thePadBG')]
        data['bgtex'] = [bs.getTexture('menuBG')]
        return data

    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain', delegate=self, attrs={
            'model': self.preloadData['model'][0],
            'collideModel': self.preloadData['collideModel'],
            'colorTexture': self.preloadData['tex'][0],
            'color': (1, 1, 1),
            'visibleInReflections': False,
            'materials': [bs.getSharedObject('footingMaterial')]})

        self.screen = bs.newNode('terrain', attrs={
            "model": self.preloadData['model'][1],
            "colorTexture": self.preloadData['tex'][0],
            "materials": [bs.getSharedObject('footingMaterial')]})

        self.bottom = bs.newNode('terrain', delegate=self, attrs={
            'model': self.preloadData['model'][2],
            'colorTexture': self.preloadData['tex'][1],
            'color': (2, 2, 2),
            'visibleInReflections': False,
            'background': True,
            'lighting': False,
            'materials': [bs.getSharedObject('footingMaterial')]})

        self.bg = bs.NodeActor(bs.newNode('terrain', attrs={
            'model': self.preloadData['bgmodel'][0],
            'color': (1, 0.6, 0.3),
            'lighting': False,
            'visibleInReflections': False,
            'background': True,
            'colorTexture': self.preloadData['bgtex'][0]}))

        g = bs.getSharedObject('globals')
        #g.floorReflection = True
        g.tint = (0.9, 0.9, 0.9)
        g.ambientColor = (1, 1, 1)
        g.vignetteOuter = (1, 1, 1)
        g.vignetteInner = (1, 1, 1)
        g.vrCameraOffset = (0, -4.2, -1.1)
        g.vrNearClip = 0.5

    def _isPointNearEdge(self, p, running=False):
        boxPosition = self.defs.boxes['edgeBox'][0:3]
        boxScale = self.defs.boxes['edgeBox'][6:9]
        x = (p.x()-boxPosition[0])/boxScale[0]
        z = (p.z()-boxPosition[2])/boxScale[2]
        return (x < -0.5 or x > 0.5 or z < -0.5 or z > 0.5)

registerMap(PhoneMap)

class DuckMap(Map):
    import duckDefs as defs
    name = "Duck"

    playTypes = ['melee']

    @classmethod
    def getPreviewTextureName(cls):
        return 'duckPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = [bs.getModel("duckMain"),
                         bs.getModel("duckNotShadow"),
                         bs.getModel("duckReflection"),
                         bs.getModel("duckMirror")]

        data['collideModel'] = [bs.getCollideModel("duckCollide"),
                                bs.getCollideModel("duckCollideIce"),
                                bs.getCollideModel("duckCollideScreens")]

        data['tex'] = [bs.getTexture("duck")]
        data['bgmodel'] = [bs.getModel("serverBG")]
        data['bgtex'] = [bs.getTexture("serverBG")]

        m = bs.Material()
        m.addActions(actions=('modifyPartCollision', 'friction', 0.01))
        data['iceMaterial'] = m
        return data

    def __init__(self):
        Map.__init__(self)
        import bsSpaz
        self.screenMaterial = bs.Material()
        self.screenMaterial.addActions(
            conditions=(('theyHaveMaterial', 
                         bs.getSharedObject('objectMaterial'))),
            actions=(("call", "atConnect", self.krya)))

        self.node = bs.newNode('terrain', delegate=self, attrs={
            'model': self.preloadData['model'][0],
            'collideModel': self.preloadData['collideModel'][0],
            'colorTexture': self.preloadData['tex'][0],
            'materials': [bs.getSharedObject('footingMaterial')]})

        self.nodeNotShadow = bs.newNode('terrain', delegate=self, attrs={
            'model': self.preloadData['model'][1],
            'collideModel': self.preloadData['collideModel'][2],
            'lighting': False,
            'background': True,
            'colorTexture': self.preloadData['tex'][0],
            'materials': [bs.getSharedObject('footingMaterial'),
                          self.screenMaterial]})

        self.nodeReflection = bs.newNode('terrain', delegate=self, attrs={
            'model': self.preloadData['model'][2],
            'reflection': 'powerup',
            'reflectionScale': [0.4],
            'colorTexture': self.preloadData['tex'][0],
            'materials': [bs.getSharedObject('footingMaterial')]})

        self.bg = bs.NodeActor(bs.newNode('terrain', attrs={
            'model': self.preloadData['bgmodel'][0],
            'color': (0.92, 0.91, 0.9),
            'lighting': False,
            'background': True,
            'colorTexture': self.preloadData['bgtex'][0]}))

        self.floor = bs.newNode("terrain", attrs={
            "model": self.preloadData['model'][3],
            "colorTexture": self.preloadData['tex'][0],
            'reflection': 'powerup',
            'reflectionScale': [0.6],
            'collideModel': self.preloadData['collideModel'][1],
            "materials": [bs.getSharedObject('footingMaterial'),
                          self.preloadData['iceMaterial']]})

        g = bs.getSharedObject('globals')
        g.tint = (0.8, 0.8, 0.8)
        g.ambientColor = (1.0, 1.0, 1.0)
        g.vignetteOuter = (1, 1, 1)
        g.vignetteInner = (1, 1, 1)
        g.vrCameraOffset = (0, -4.2, -1.1)
        g.vrNearClip = 0.5

    def krya(self):
        bs.playSound(
            bs.getSound(random.choice([
                'duck01',
                'duck02',
                'duck03',
                'duck04'])),
            position=(0, 5, 0))

    def _isPointNearEdge(self, p, running=False):
        boxPosition = self.defs.boxes['edgeBox'][0:3]
        boxScale = self.defs.boxes['edgeBox'][6:9]
        x = (p.x()-boxPosition[0])/boxScale[0]
        z = (p.z()-boxPosition[2])/boxScale[2]
        return (x < -0.5 or x > 0.5 or z < -0.5 or z > 0.5)

registerMap(DuckMap)

class TubeMap(Map):
    import tutDefs as defs
    name = "Tubes"

    playTypes = ['melee', 'football', 'teamFlag', 'keepAway']

    @classmethod
    def getPreviewTextureName(cls):
        return 'tubePreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = [bs.getModel("tubeLevel"),
                         bs.getModel("tubeTubes")]

        data['collideModel'] = [bs.getCollideModel("tubeTubeCollide"),
                                bs.getCollideModel("tubeLevelCollide"),
                                bs.getCollideModel("tubeTubeCollide2")]

        data['tex'] = [bs.getTexture("tubeTubes"),
                       bs.getTexture("tubeLevel")]

        data['bgmodel'] = [bs.getModel("serverBG")]
        data['bgtex'] = [bs.getTexture("serverBG")]
        return data

    def __init__(self):
        Map.__init__(self)
        self.speedMaterialLeft = bs.Material()
        self.speedMaterialLeft.addActions(
            conditions=(('theyHaveMaterial',
                         bs.getSharedObject('playerMaterial'))),
            actions=(("modifyPartCollision", "collide", True),
                     ("modifyPartCollision", "physical", False),
                     ("call", "atConnect", self.touchSpeedLeft)))

        self.speedMaterialRight = bs.Material()
        self.speedMaterialRight.addActions(
            conditions=(('theyHaveMaterial',
                         bs.getSharedObject('playerMaterial'))),
            actions=(("modifyPartCollision", "collide", True),
                     ("modifyPartCollision", "physical", False),
                     ("call", "atConnect", self.touchSpeedRight)))

        self.node = bs.newNode('terrain', delegate=self, attrs={
            'model': self.preloadData['model'][0],
            'collideModel': self.preloadData['collideModel'][1],
            'colorTexture': self.preloadData['tex'][1],
            'materials': [bs.getSharedObject('footingMaterial')]})

        self.nodeTubes = bs.newNode('terrain', delegate=self, attrs={
            'model': self.preloadData['model'][1],
            'colorTexture': self.preloadData['tex'][0],
            'collideModel': self.preloadData['collideModel'][0],
            'reflection': 'soft',
            'reflectionScale': [0.78],
            'materials': [bs.getSharedObject('objectMaterial')]})

        self.nodeTubes2 = bs.newNode('terrain', delegate=self, attrs={
            'collideModel': self.preloadData['collideModel'][2],
            'materials': [bs.getSharedObject('footingMaterial')]})

        self.bg = bs.NodeActor(bs.newNode('terrain', attrs={
            'model': self.preloadData['bgmodel'][0],
            'color': (0.92, 0.91, 0.9),
            'lighting': False,
            'background': True,
            'colorTexture': self.preloadData['bgtex'][0]}))

        import tutDefs as defs                             
        self.speedRegionLeft = bs.NodeActor(bs.newNode("region", attrs={
            'position':defs.boxes["speedLeft"][0:3],
            'scale':defs.boxes["speedLeft"][6:9],
            'type':"box",
            'materials':[self.speedMaterialLeft]}))

        self.speedRegionRight = bs.NodeActor(bs.newNode("region", attrs={
            'position': defs.boxes["speedRight"][0:3],
            'scale': defs.boxes["speedRight"][6:9],
            'type': "box",
            'materials': [self.speedMaterialRight]}))

        self.light = bs.newNode('light', attrs={
            'position': (9, 8, 1),
            'color': (1.2,1.2,0.25),
            'volumeIntensityScale': 0.1,
            'radius': 2.5,
            'intensity': 0.65})

        self.light2 = bs.newNode('light', attrs={
            'position': (-9, 8, 1),
            'color': (1.2, 1.2, 0.25),
            'volumeIntensityScale': 0.1,
            'radius': 2.5,
            'intensity': 0.6})

        g = bs.getSharedObject('globals')
        g.tint = (0.5-0.1, 0.7-0.1, 1-0.15)
        g.ambientColor = (1.35, 1.3, 2.0)
        g.vignetteOuter = (0.9, 0.74, 0.9)
        g.vignetteInner = (1, 1, 1)
        g.vrCameraOffset = (0, -4.2, -1.1)
        g.vrNearClip = 0.5

    def touchSpeedLeft(self):
        node = bs.getCollisionInfo('opposingNode')
        s = node.holdNode
        node.holdNode = bs.Node(None)
        node.handleMessage(bs.StandMessage(position=(4.1, 5, -0.6)))

        node.handleMessage(
            "impulse", node.position[0], node.position[1], node.position[2],
            node.velocity[0]+10, node.velocity[1]+2, node.velocity[2]*5,
            100, 100, 0, 0, node.velocity[0]+5, node.velocity[1]+10, node.velocity[2])

        def bringBackHoldNode():
            if s is not None and s.exists():
                s.position = (node.position[0],
                              node.position[1]+1,
                              node.position[2])

                node.holdNode = s

        bs.gameTimer(300, bringBackHoldNode)

    def touchSpeedRight(self):
        node = bs.getCollisionInfo('opposingNode')
        s = node.holdNode
        node.holdNode = bs.Node(None)
        node.handleMessage(bs.StandMessage(position=(-3.7, 5, -0.6)))
        node.handleMessage(
            "impulse", node.position[0], node.position[1], node.position[2],
            node.velocity[0]-10, node.velocity[1]+2, node.velocity[2]*5,
            80, 80, 0, 0, node.velocity[0]-5, node.velocity[1]+10, node.velocity[2])

        def bringBackHoldNode():
            if s is not None and s.exists():
                s.position = (node.position[0],
                              node.position[1]+1,
                              node.position[2])

                node.holdNode = s

        bs.gameTimer(300, bringBackHoldNode)

    def _isPointNearEdge(self, p, running=False):
        boxPosition = self.defs.boxes['edgeBox'][0:3]
        boxScale = self.defs.boxes['edgeBox'][6:9]
        x = (p.x()-boxPosition[0])/boxScale[0]
        z = (p.z()-boxPosition[2])/boxScale[2]
        return (x < -0.5 or x > 0.5 or z < -0.5 or z > 0.5)

registerMap(TubeMap)

class CheezeMap(Map):
    import cheezeDefs as defs
    name = "Cheeze Island"

    playTypes = ['melee', 'football']

    @classmethod
    def getPreviewTextureName(cls):
        return 'cheezeMapPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = [bs.getModel("cheezeMap"),
                         bs.getModel("cheezeSea"),
                         bs.getModel("thePadBG"),
                         bs.getModel("cheezeSea2"),
                         bs.getModel("cheezeSea3"),
                         bs.getModel("dno")]

        data['collideModel'] = [bs.getCollideModel("cheezeMapCollide"),
                                bs.getCollideModel("cheezeSeaCollide"),
                                bs.getCollideModel("cheezeSeaCollide2"),
                                bs.getCollideModel("cheezeSeaCollide3")]

        data['tex'] = [bs.getTexture("challengeWater"),
                       bs.getTexture("cheezeMap"),
                       bs.getTexture("menuBG"),
                       bs.getTexture("dno")]
        return data

    def __init__(self):
        Map.__init__(self)
        bs.gameTimer(2, bs.Call(bs.playMusic, 'sea'))

        b = bs.Material()
        b.addActions(
            actions=(("modifyPartCollision", "collide", True),
                     ("modifyPartCollision", "physical", False),
                     ("call", "atConnect", self.emitWater)))

        a = bs.Material()
        a.addActions(
            actions=(("modifyPartCollision", "collide", True),
                     ("modifyPartCollision", "physical", False),
                     ("call", "atConnect", self.waterCollide)))

        self.node = bs.newNode('terrain', delegate=self, attrs={
            'model': self.preloadData['model'][0],
            'collideModel': self.preloadData['collideModel'][0],
            'colorTexture': self.preloadData['tex'][1],
            'materials': [bs.getSharedObject('footingMaterial')]})

        self.node2 = bs.newNode('terrain', delegate=self, attrs={
            'model': self.preloadData['model'][5],
            'colorTexture': self.preloadData['tex'][3],
            'materials': [bs.getSharedObject('footingMaterial')]})

        self.water = bs.newNode("terrain", attrs={
            "model": self.preloadData['model'][1],
            "colorTexture": self.preloadData['tex'][0],
            'reflection': 'powerup',
            'reflectionScale': [5],
            'collideModel': self.preloadData['collideModel'][1],
            "opacity": 0.92,
            'background': True,
            "materials": [b]})

        self.water2 = bs.newNode('terrain', delegate=self, attrs={
            'collideModel': self.preloadData['collideModel'][2],
            'materials': [a]})

        self.water3 = bs.newNode('terrain', delegate=self, attrs={
            'collideModel': self.preloadData['collideModel'][3],
            'materials': [a]})

        self.bg = bs.NodeActor(bs.newNode('terrain', attrs={
            'model': self.preloadData['model'][2],
            'color': (0.92, 0.91, 0.9),
            'lighting': False,
            'background': True,
            'colorTexture': self.preloadData['tex'][2]}))

        self._waterEmitter = bs.Timer(50, bs.WeakCall(self.emitWater2), repeat=True)

        g = bs.getSharedObject('globals')
        g.tint = (0.8, 0.8, 0.8)
        g.ambientColor = (1, 1, 1)
        g.vignetteOuter = (1, 1, 1)
        g.vignetteInner = (1, 1, 1)
        g.vrCameraOffset = (0, -4.2, -1.1)
        g.vrNearClip = 0.5

        def waterCycle():
            if self.water.model == self.preloadData['model'][1]:
                self.water.model = self.preloadData['model'][3]
            else:
                self.water.model = self.preloadData['model'][1]

        bs.gameTimer(800, waterCycle, True)

    def emitWater(self):
        node = bs.getCollisionInfo('opposingNode')
        if random.random() > 0.2:
            bs.playSound(
                bs.getSound(random.choice([
                    'water1',
                    'water2',
                    'water3',
                    'water4',
                    'water5'])),
                position=node.position)

        bs.emitBGDynamics(
            position=node.position,
            velocity=(0, 5, 0),
            count=int(10.0+random.random()*25),
            scale=1.3,
            spread=0.3,
            chunkType='sweat')

        if node.getNodeType() in ['bomb', 'prop']:
            node.extraAcceleration = (0, 21, 0)
            node.maxSpeed = 4
            bs.emitBGDynamics(
                position=node.position,
                velocity=(0, 5, 0),
                count=int(3.0+random.random()*5),
                scale=1.3,
                spread=0.3,
                chunkType='sweat')
        else:
            node.handleMessage(
                "impulse", node.position[0], node.position[1], node.position[2],
                0, 0.1, 0, 60.6, 0, 0, 0, 0, 0.1, 0)

    def emitWater2(self):
        bs.emitBGDynamics(
            position=(-15+random.random()*30,
                      random.random()*1.2,
                      -15+random.random()*30),
            count=int(5.0+random.random()*10),
            scale=1.1,
            spread=0.1,
            chunkType='sweat')

    def waterCollide(self):
        node = bs.getCollisionInfo('opposingNode')
        if node.getNodeType() in ['bomb', 'prop']:
            node.extraAcceleration = (0, 5, 0)

        if node.getNodeType() == 'prop':
            if node.bodyScale < 0.5:
                node.handleMessage(bs.DieMessage())

    def _isPointNearEdge(self, p, running=False):
        boxPosition = self.defs.boxes['edgeBox'][0:3]
        boxScale = self.defs.boxes['edgeBox'][6:9]
        x = (p.x()-boxPosition[0])/boxScale[0]
        z = (p.z()-boxPosition[2])/boxScale[2]
        return (x < -0.5 or x > 0.5 or z < -0.5 or z > 0.5)

registerMap(CheezeMap)

class BPlantMap(Map):
    import bplantDefs as defs
    name = "B Plant"

    playTypes = ['melee', 'football', 'teamFlag', 'keepAway']

    @classmethod
    def getPreviewTextureName(cls):
        return 'bplantPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = [bs.getModel("bplant")]
        data['collideModel'] = [bs.getCollideModel("bplantCollide")]
        data['tex'] = [bs.getTexture("bplant")]
        return data

    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain', delegate=self, attrs={
            'model': self.preloadData['model'][0],
            'collideModel': self.preloadData['collideModel'][0],
            'colorTexture': self.preloadData['tex'][0],
            'materials': [bs.getSharedObject('footingMaterial')]})

        bs.Bomb(
            bombType='slipper',
            position=(3.13259, 1.50205, 8.59763)).autoRetain()

        g = bs.getSharedObject('globals')
        g.tint = (0.7, 0.7, 0.7)
        g.ambientColor = (1.0, 1.0, 1.0)
        g.vignetteOuter = (1, 1, 1)
        g.vignetteInner = (1, 1, 1)
        g.vrCameraOffset = (0, -4.2, -1.1)
        g.vrNearClip = 0.5

    def _isPointNearEdge(self, p, running=False):
        boxPosition = self.defs.boxes['edgeBox'][0:3]
        boxScale = self.defs.boxes['edgeBox'][6:9]
        x = (p.x()-boxPosition[0])/boxScale[0]
        z = (p.z()-boxPosition[2])/boxScale[2]
        return (x < -0.5 or x > 0.5 or z < -0.5 or z > 0.5)

registerMap(BPlantMap)

class ParkourMap(Map):
    import parkourDefs as defs
    name = "Parkour"

    playTypes = ['melee', 'football', 'teamFlag']

    @classmethod
    def getPreviewTextureName(cls):
        return 'parkourPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = [bs.getModel("parkour"),
                         bs.getModel("parkourLog"),
                         bs.getModel("parkourTop")]

        data['collideModel'] = [bs.getCollideModel("parkourCollide"),
                                bs.getCollideModel("parkourCollideBottom")]

        data['tex'] = [bs.getTexture("parkourTex"),
                       bs.getTexture('parkourLog'),
                       bs.getTexture('parkourTop')]

        data['bgModel'] = bs.getModel("parkourBG") 
        data['bgTex'] = bs.getTexture("parkourBG")
        return data

    def __init__(self):
        Map.__init__(self)
        # its bottom
        self.node = bs.newNode('terrain', delegate=self, attrs={
            'model': self.preloadData['model'][0],
            'collideModel': self.preloadData['collideModel'][0],
            'colorTexture': self.preloadData['tex'][0],
            'lighting': False,
            'background': True,
            'materials': [bs.getSharedObject('footingMaterial')]})

        self.bottomCollide = bs.newNode('terrain', delegate=self, attrs={
            'collideModel': self.preloadData['collideModel'][1],
            'materials': [bs.getSharedObject('deathMaterial')]})

        self.pol = bs.newNode('terrain', delegate=self, attrs={
            'model': self.preloadData['model'][2],
            'colorTexture': self.preloadData['tex'][2],
            'materials': [bs.getSharedObject('footingMaterial')]})

        self.node1 = bs.newNode('terrain', delegate=self, attrs={
            'model': self.preloadData['model'][1],
            'colorTexture': self.preloadData['tex'][1],
            'background': True,
            'lighting': False,
            'materials': [bs.getSharedObject('footingMaterial')]})

        self.bg = bs.NodeActor(bs.newNode('terrain', attrs={
            'model': self.preloadData['bgModel'],
            'color': (0.92, 0.91, 0.9),
            'lighting': False,
            'background': True,
            'colorTexture': self.preloadData['bgTex']}))

        g = bs.getSharedObject('globals')
        g.tint = (0.7, 0.72, 0.7)
        g.ambientColor = (0.8, 1.2, 0.8)
        g.vignetteOuter = (1, 1, 1)
        g.vignetteInner = (1, 1, 1)
        g.vrCameraOffset = (0, -4.2, -1.1)
        g.vrNearClip = 0.5

    def _isPointNearEdge(self, p, running=False):
        boxPosition = self.defs.boxes['edgeBox'][0:3]
        boxScale = self.defs.boxes['edgeBox'][6:9]
        x = (p.x()-boxPosition[0])/boxScale[0]
        z = (p.z()-boxPosition[2])/boxScale[2]
        return (x < -0.5 or x > 0.5 or z < -0.5 or z > 0.5)

registerMap(ParkourMap)

class Roof(Map):
    import roofDefs as defs
    name = "Roof"

    playTypes = ['melee', 'football', 'teamFlag']

    @classmethod
    def getPreviewTextureName(cls):
        return 'roofMapPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = [bs.getModel("home"),
                         bs.getModel("roofBG"),
                         bs.getModel("ant")]

        data['collideModel'] = [bs.getCollideModel("homeCollide"),
                                bs.getCollideModel("antCollide")]

        data['tex'] = [bs.getTexture("home"),
                       bs.getTexture("ant"),
                       bs.getTexture("skyBG")]
        return data

    def __init__(self):
        Map.__init__(self)
        self.antennMaterial = bs.Material()
        self.antennMaterial.addActions(
            conditions=(('theyHaveMaterial',
                         bs.getSharedObject('playerMaterial'))),
            actions=(("call", "atConnect", self.touchAntenn)))

        self.node = bs.newNode('terrain', delegate=self, attrs={
            'model': self.preloadData['model'][2],
            'collideModel': self.preloadData['collideModel'][1],
            'colorTexture': self.preloadData['tex'][1],
            'materials': [bs.getSharedObject('footingMaterial'),
                          self.antennMaterial,
                          bs.getSharedObject('pickupMaterial')]})

        self.center = bs.newNode('terrain', delegate=self, attrs={
            'model': self.preloadData['model'][0],
            'collideModel': self.preloadData['collideModel'][0],
            'colorTexture': self.preloadData['tex'][0],
            'materials': [bs.getSharedObject('footingMaterial')]})

        self.bg = bs.NodeActor(bs.newNode('terrain', attrs={
            'model': self.preloadData['model'][1],
            'color': (0.92, 0.91, 0.9),
            'lighting': False,
            'background': True,
            'colorTexture': self.preloadData['tex'][2]}))

        g = bs.getSharedObject('globals')
        g.tint = (0.7, 0.7, 0.7)
        g.ambientColor = (1, 1, 1)
        g.vignetteOuter = (0.9, 0.9, 0.9)
        g.vignetteInner = (0.99, 0.99, 0.99)
        g.vrCameraOffset = (0, -4.2, -1.1)
        g.vrNearClip = 0.5

    def touchAntenn(self):
        node = bs.getCollisionInfo('opposingNode')
        bs.playSound(bs.getSound(random.choice([
            'electro1',
            'electro2',
            'electro3'])))

        node.handleMessage("knockout", 3000)

        node.handleMessage(
            "impulse", node.position[0], node.position[1], node.position[2],
            -node.velocity[0], -node.velocity[1], -node.velocity[2],
            200, 200, 0, 0, -node.velocity[0], -node.velocity[1], -node.velocity[2])

        flash = bs.newNode("flash", attrs={
            'position': node.position,
            'size': 0.7,
            'color': (0, 0.4+random.random(), 1)})

        bs.emitBGDynamics(
            position=node.position,
            count=20,
            scale=0.5,
            spread=0.5,
            chunkType='spark')

        bs.gameTimer(60, flash.delete)

    def _isPointNearEdge(self, p, running=False):
        boxPosition = self.defs.boxes['edgeBox'][0:3]
        boxScale = self.defs.boxes['edgeBox'][6:9]
        x = (p.x()-boxPosition[0])/boxScale[0]
        z = (p.z()-boxPosition[2])/boxScale[2]
        return (x < -0.5 or x > 0.5 or z < -0.5 or z > 0.5)

registerMap(Roof)

class EshersWaterfall(Map):
    import waterfallDefs as defs
    name = "Esher's Waterfall"

    playTypes = ['melee', 'football', 'teamFlag', 'keepAway']

    @classmethod
    def getPreviewTextureName(cls):
        return 'ehsersWaterfallPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = [bs.getModel("waterfall"),
                         bs.getModel("waterfallLogMain"),
                         bs.getModel("waterfallLogBG"),
                         bs.getModel("waterfallBG"),
                         bs.getModel("waterfallNotShadow"),
                         bs.getModel("waterfallLogMainNotShadow")]

        data['tex'] = [bs.getTexture("waterfall"),
                       bs.getTexture("waterfallLogMain"),
                       bs.getTexture("waterfallLogBG"),
                       bs.getTexture("waterfallBG")]

        data['collideModel'] = bs.getCollideModel("waterfallCollide")
        return data

    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain', delegate=self, attrs={
            'model': self.preloadData['model'][0],
            'collideModel': self.preloadData['collideModel'],
            'colorTexture': self.preloadData['tex'][0],
            'materials': [bs.getSharedObject('footingMaterial')]})

        self.notShadow = bs.newNode('terrain', delegate=self, attrs={
            'model': self.preloadData['model'][4],
            'colorTexture': self.preloadData['tex'][0],
            'lighting': False,
            'background': True,
            'materials': [bs.getSharedObject('footingMaterial')]})

        self.logMain = bs.newNode('terrain', delegate=self, attrs={
            'model': self.preloadData['model'][1],
            'colorTexture': self.preloadData['tex'][1],
            'materials': [bs.getSharedObject('footingMaterial')]})

        self.logMainNotShadow = bs.newNode('terrain', delegate=self, attrs={
            'model': self.preloadData['model'][5],
            'colorTexture': self.preloadData['tex'][1],
            'lighting': False,
            'background': True,
            'materials': [bs.getSharedObject('footingMaterial')]})

        self.logBG = bs.newNode('terrain', delegate=self, attrs={
            'model': self.preloadData['model'][2],
            'colorTexture': self.preloadData['tex'][2],
            'materials': [bs.getSharedObject('footingMaterial')]})

        self.bg = bs.NodeActor(bs.newNode('terrain', attrs={
            'model': self.preloadData['model'][3],
            'color': (1, 1, 1),
            'lighting': False,
            'background': True,
            'colorTexture': self.preloadData['tex'][3]}))

        # Portals:
        # Purple
        bdUtils.Portal(
            position1=(-2.64, 3, 5.79),
            position2=(8, 6.2, -2.8),
            color=(3, 0, 9/2))

        # Yellow
        bdUtils.Portal(
            position1=(8.12, 2.17, -3.12),
            position2=(11.3, 11, 0),
            color=(9/2, 8/2, 0))

        # Red
        bdUtils.Portal(
            position1=(7.9, 11.3, -3.5),
            position2=(-2.7, 15.5, 0),
            color=(9/2, 0, 1))
       
        g = bs.getSharedObject('globals')
        g.tint = (0.65, 0.67, 0.65)
        g.ambientColor = (0.5, 1, 0.5)
        g.vignetteOuter = (1, 1, 1)
        g.vignetteInner = (1, 1, 1)
        g.vrCameraOffset = (0, -4.2, -1.1)
        g.vrNearClip = 0.5

    def _isPointNearEdge(self, p, running=False):
        boxPosition = self.defs.boxes['edgeBox'][0:3]
        boxScale = self.defs.boxes['edgeBox'][6:9]
        x = (p.x()-boxPosition[0])/boxScale[0]
        z = (p.z()-boxPosition[2])/boxScale[2]
        return (x < -0.5 or x > 0.5 or z < -0.5 or z > 0.5)

registerMap(EshersWaterfall)

class BlenderMap(Map):
    import blenderMapDefs as defs
    name = "Blender"

    playTypes = ['melee', 'keepAway']

    @classmethod
    def getPreviewTextureName(cls):
        return 'blenderMapPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel("blenderMap")
        data['collideModel'] = bs.getCollideModel("blenderMap")
        data['tex'] = bs.getTexture("blenderMap")
        data['bgModel'] = bs.getModel("thePadBG") 
        data['bgTex'] = bs.getTexture("menuBG")
        return data

    def __init__(self):
        Map.__init__(self)

        self.batutMaterial = bs.Material()
        self.batutMaterial.addActions(
            conditions=(('theyHaveMaterial',
                         bs.getSharedObject('playerMaterial'))),
            actions=(("call", "atConnect", self.batutTouche)))

        self.node = bs.newNode('terrain', delegate=self, attrs={
            'model': self.preloadData['model'],
            'collideModel': self.preloadData['collideModel'],
            'colorTexture': self.preloadData['tex'],
            'materials': [bs.getSharedObject('footingMaterial')]})

        self.bg = bs.NodeActor(bs.newNode('terrain', attrs={
            'model': self.preloadData['bgModel'],
            'color': (0.92, 0.91, 0.9),
            'lighting': False,
            'background': True,
            'colorTexture': self.preloadData['bgTex']}))

        g = bs.getSharedObject('globals')
        g.tint = (0.67, 0.67, 0.7)
        g.ambientColor = (1.3, 1.1, 0.4)
        g.vignetteOuter = (0.9, 0.96, 0.9)
        g.vignetteInner = (1, 1, 1)
        g.vrCameraOffset = (0, -4.2, -1.1)
        g.vrNearClip = 0.5

        self._tntWind = bs.Timer(300, bs.WeakCall(self.tntWind), repeat=True)

    def tntWind(self):
        bs.Bomb(
            bombType='tnt',
            position=(-30,
                      -8+(random.random()*0.2),
                      random.uniform(10, -45)),
            velocity=(random.random()*10,
                      random.random()*0.1,
                      random.random())).autoRetain().node.extraAcceleration = (3, 20, 0)

    def batutTouche(self):
        node = bs.getCollisionInfo('opposingNode')

        node.handleMessage(
            "impulse", node.position[0], node.position[1], node.position[2],
            0, -node.velocity[1]*3, 0, 350, 0, 0, 0, node.velocity[0],
            -node.velocity[1]*3, node.velocity[2])

        bs.emitBGDynamics(
            position=node.position,
            count=int(7.0+random.random()*20),
            scale=0.4,
            spread=0.1,
            chunkType='spark')

    def _isPointNearEdge(self, p, running=False):
        boxPosition = self.defs.boxes['edgeBox'][0:3]
        boxScale = self.defs.boxes['edgeBox'][6:9]
        x = (p.x()-boxPosition[0])/boxScale[0]
        z = (p.z()-boxPosition[2])/boxScale[2]
        return (x < -0.5 or x > 0.5 or z < -0.5 or z > 0.5)

registerMap(BlenderMap)

class Minecraft(Map):
    import MinecraftDefs as defs
    name = "Minecraft"

    playTypes = ['melee', 'football', 'teamFlag', 'billiard']

    @classmethod
    def getPreviewTextureName(cls):
        return 'MinecraftPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['models'] = [bs.getModel("mcFloor1"),
                          bs.getModel("mcFloor2"),
                          bs.getModel("mcGrass"),
                          bs.getModel("mcDirt"),
                          bs.getModel("mcBuilds")]

        data['tex'] = [bs.getTexture('MinecraftTex'),
                       bs.getTexture('mcBuilds'),
                       bs.getTexture('mcFloor1'),
                       bs.getTexture('mcFloor2')]

        data['collideModel'] = bs.getCollideModel("mcCollide")
        data['bgmodel'] = [bs.getModel("thePadBG")]
        data['bgtex'] = [bs.getTexture("menuBG")]
        return data

    def __init__(self):
        Map.__init__(self)
        self.floor = bs.newNode('terrain', delegate=self, attrs={
            'model': self.preloadData['models'][0],
            'colorTexture': self.preloadData['tex'][2],
            'collideModel': self.preloadData['collideModel'],
            'materials': [bs.getSharedObject('footingMaterial')]})

        self.node2 = bs.newNode('terrain', delegate=self, attrs={
            'model': self.preloadData['models'][1],
            'colorTexture': self.preloadData['tex'][3],
            'materials': [bs.getSharedObject('footingMaterial')]})

        self.node3 = bs.newNode('terrain', delegate=self, attrs={
            'model': self.preloadData['models'][2],
            'colorTexture': self.preloadData['tex'][0],
            'materials': [bs.getSharedObject('footingMaterial')]})

        self.node4 = bs.newNode('terrain', delegate=self, attrs={
            'model': self.preloadData['models'][3],
            'colorTexture': self.preloadData['tex'][0],
            'materials': [bs.getSharedObject('footingMaterial')]})

        self.node = bs.newNode('terrain', delegate=self, attrs={
            'model': self.preloadData['models'][4],
            'colorTexture': self.preloadData['tex'][1],
            'materials': [bs.getSharedObject('footingMaterial')]})

        self.bg = bs.NodeActor(bs.newNode('terrain', attrs={
            'model': self.preloadData['bgmodel'][0],
            'color': (0.92, 0.91, 0.9),
            'lighting': False,
            'background': True,
            'colorTexture': self.preloadData['bgtex'][0]}))

        g = bs.getSharedObject('globals')
        g.tint = (0.9, 0.9, 0.8)
        g.ambientColor = (1, 1, 1)
        g.vignetteOuter = (0.8, 0.8, 0.8)
        g.vignetteInner = (1, 1, 1)
        g.vrCameraOffset = (0, 4.2, -1.1)
        g.vrNearClip = 0.5

    def _isPointNearEdge(self, p, running=False):
        boxPosition = self.defs.boxes['edgeBox'][0:3]
        boxScale = self.defs.boxes['edgeBox'][6:9]
        x = (p.x()-boxPosition[0])/boxScale[0]
        z = (p.z()-boxPosition[2])/boxScale[2]
        return (x < -0.5 or x > 0.5 or z < -0.5 or z > 0.5)

registerMap(Minecraft)

class BasketballStadium(Map):
    import basketStadiumDefs as defs
    name = "Basketball Stadium"

    playTypes = ['melee', 'football', 'teamFlag', 'keepAway', 'basketball']

    @classmethod
    def getPreviewTextureName(cls):
        return 'basketStadiumPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['modelPole'] = bs.getModel("basketPole")
        data['modelBack'] = bs.getModel("basketBack")
        data['modelRings'] = bs.getModel("basketRings")
        data['collideModel'] = bs.getCollideModel("basketCollide")
        data['texPole'] = bs.getTexture("basketPole")
        data['ringsTex'] = bs.getTexture("basketRings")
        data['backTex'] = bs.getTexture("basketBack")
        data['bgModel'] = bs.getModel("thePadBG") 
        data['bgTex'] = bs.getTexture("menuBG")
        return data

    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain', delegate=self, attrs={
            'model': self.preloadData['modelPole'],
            'collideModel': self.preloadData['collideModel'],
            'colorTexture': self.preloadData['texPole'],
            'materials': [bs.getSharedObject('footingMaterial')]})

        self.back = bs.newNode('terrain', delegate=self, attrs={
            'model': self.preloadData['modelBack'],
            'colorTexture': self.preloadData['backTex'],
            'materials': [bs.getSharedObject('footingMaterial')]})

        self.rings = bs.newNode('terrain', delegate=self, attrs={
            'model': self.preloadData['modelRings'],
            'colorTexture': self.preloadData['ringsTex'],
            'materials': [bs.getSharedObject('footingMaterial')]})

        self.bg = bs.newNode('terrain', attrs={
            'model': self.preloadData['bgModel'],
            'lighting': False,
            'background': True,
            'colorTexture': self.preloadData['bgTex']})

        g = bs.getSharedObject('globals')
        g.tint = (1, 1, 1)
        g.ambientColor = (1, 1, 1)
        g.vignetteOuter = (0.7, 0.7, 0.7)
        g.vignetteInner = (0.9, 0.9, 0.9)
        g.vrCameraOffset = (0, -4.2, -1.1)
        g.vrNearClip = 0.5

    def _isPointNearEdge(self, p, running=False):
        boxPosition = self.defs.boxes['edgeBox'][0:3]
        boxScale = self.defs.boxes['edgeBox'][6:9]
        x = (p.x()-boxPosition[0])/boxScale[0]
        z = (p.z()-boxPosition[2])/boxScale[2]
        return (x < -0.5 or x > 0.5 or z < -0.5 or z > 0.5)

registerMap(BasketballStadium)

class WWE(Map):
    import wweDefs as defs
    name = "Boxing ring"

    playTypes = ['melee']

    @classmethod
    def getPreviewTextureName(cls):
        return 'wwePreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = [bs.getModel("wweFloor"),
                         bs.getModel("wweLevel"),
                         bs.getModel("wweStairs"),
                         bs.getModel("wweString")]

        data['tex'] = [bs.getTexture("wweFloor"),
                       bs.getTexture("wweLevel"),
                       bs.getTexture("wweStairs"),
                       bs.getTexture("wweString")]

        data['collideModel'] = bs.getCollideModel("wwe")
        data['modelBGTex'] = bs.getTexture('menuBG')
        data['modelBG'] = bs.getModel('thePadBG')
        return data

    def __init__(self):
        Map.__init__(self)
        self.floor = bs.newNode('terrain', delegate=self, attrs={
            'model': self.preloadData['model'][0],
            'collideModel': self.preloadData['collideModel'],
            'colorTexture': self.preloadData['tex'][0],
            'materials': [bs.getSharedObject('footingMaterial')]})

        self.level = bs.newNode('terrain', delegate=self, attrs={
            'model': self.preloadData['model'][1],
            'colorTexture': self.preloadData['tex'][1],
            'materials': [bs.getSharedObject('footingMaterial')]})

        self.stairs = bs.newNode('terrain', delegate=self, attrs={
            'model': self.preloadData['model'][2],
            'colorTexture': self.preloadData['tex'][2],
            'materials': [bs.getSharedObject('footingMaterial')]})

        self.string = bs.newNode('terrain', delegate=self, attrs={
            'model': self.preloadData['model'][3],
            'colorTexture': self.preloadData['tex'][3],
            'materials': [bs.getSharedObject('footingMaterial')]})

        self.foo = bs.newNode('terrain', attrs={
            'model': self.preloadData['modelBG'],
            'lighting': False,
            'background': True,
            'color': (0, 0, 0),
            'colorTexture': self.preloadData['modelBGTex']})

        g = bs.getSharedObject('globals')
        g.tint = (1, 1, 1)
        g.ambientColor = (1,1,1)
        g.vignetteOuter = (0.7,0.7,0.7)
        g.vignetteInner = (0.9,0.9,0.9)
        g.vrCameraOffset = (0,-4.2,-1.1)
        g.vrNearClip = 0.5

    def _isPointNearEdge(self, p, running=False):
        boxPosition = self.defs.boxes['edgeBox'][0:3]
        boxScale = self.defs.boxes['edgeBox'][6:9]
        x = (p.x()-boxPosition[0])/boxScale[0]
        z = (p.z()-boxPosition[2])/boxScale[2]
        return (x < -0.5 or x > 0.5 or z < -0.5 or z > 0.5)

registerMap(WWE)

class snowyMountlands(Map):
    import snowyMountlandsDefs as defs
    name = 'Snowy Mountlands'
    playTypes = ['melee', 'keepAway', 'teamFlag']

    @classmethod
    def getPreviewTextureName(cls):
        return 'snowyMountlandsPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('snowyMountlands')
        data['collideModel'] = bs.getCollideModel('snowyMountlandsMapCollide')
        data['collideRollModel'] = bs.getCollideModel('snowyMountlandsMapCollideRoll')
        data['collideDieModel'] = bs.getCollideModel('snowyMountlandsMapCollideDie')
        data['tex'] = bs.getTexture('snowyMountlandsLevelColor')
        data['bgTex'] = bs.getTexture('snowBG')
        data['bgModel'] = bs.getModel('snowyMountlandsBG')
        return data

    def __init__(self):
        Map.__init__(self)

        self.node1 = bs.newNode('terrain', delegate=self, attrs={
            'collideModel': self.preloadData['collideModel'],
            'model': self.preloadData['model'],
            'colorTexture': self.preloadData['tex'],
            'reflection': 'soft',
            'reflectionScale': [0.06],
            'materials': [bs.getSharedObject('footingMaterial')]})

        self.bg = bs.NodeActor(bs.newNode('terrain', attrs={
            'model': self.preloadData['bgModel'],
            'lighting': False,
            'color': (0.9, 0.9, 1.0),
            'background': True,
            'colorTexture': self.preloadData['bgTex']}))

        self.border = bs.newNode('terrain', attrs={
            'collideModel':self.preloadData['collideRollModel'],
            'materials': [bs.getSharedObject('objectMaterial')]})

        self.outOfBorder = bs.newNode('terrain', attrs={
            'collideModel':self.preloadData['collideDieModel'],
            'materials':[bs.getSharedObject('footingMaterial'),
                         bs.getSharedObject('deathMaterial')]})

        g = bs.getSharedObject('globals')
        g.tint = (0.74, 0.74, 0.78)
        g.ambientColor = (1, 1, 1)
        g.shadowOrtho = True
        g.vignetteOuter = (0.86, 0.86, 0.86)
        g.vignetteInner = (0.95, 0.95, 0.99)
        g.vrNearClip = 0.5
        self._emit = bs.Timer(15, bs.WeakCall(self.emit), repeat=True)

    def emit(self):
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
            count=5,
            scale=0.4+random.random(),
            spread=0,
            chunkType='spark')

    def _isPointNearEdge(self, p, running=False):
        boxPosition = self.defs.boxes['edgeBox'][0:3]
        boxScale = self.defs.boxes['edgeBox'][6:9]
        x = (p.x()-boxPosition[0])/boxScale[0]
        z = (p.z()-boxPosition[2])/boxScale[2]
        return (x < -0.5 or x > 0.5 or z < -0.5 or z > 0.5)

registerMap(snowyMountlands)

class Airlands(Map):
    import AirlandsDefs as defs
    name = 'Airlands'
    playTypes = ['melee', 'keepAway', 'teamFlag']

    @classmethod
    def getPreviewTextureName(cls):
        return 'AirlandsPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('AirlandsMap')
        data['collideModel'] = bs.getCollideModel('AirlandsMapCollide')
        data['tex'] = bs.getTexture('Airlands')
        data['bgTex'] = bs.getTexture('skyBG')
        data['bgModel'] = bs.getModel('roofBG')
        return data

    def __init__(self):
        Map.__init__(self)
        self.node1 = bs.newNode('terrain', delegate=self, attrs={
            'collideModel': self.preloadData['collideModel'],
            'model': self.preloadData['model'],
            'colorTexture': self.preloadData['tex'],
            'materials': [bs.getSharedObject('footingMaterial')]})

        self.bg = bs.NodeActor(bs.newNode('terrain', attrs={
            'model': self.preloadData['bgModel'],
            'color': (0.92, 0.91, 0.9),
            'lighting': False,
            'background': True,
            'colorTexture': self.preloadData['bgTex']}))

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
            'color': (0,0,0),
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
            'color': (0,0,0),
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

        g = bs.getSharedObject('globals')
        g.tint = (0.8, 0.8, 0.8)
        deftint = (0.8, 0.8, 0.8)
        deftint2 = (0.81, 0.81, 0.81)
        g.ambientColor = (1, 1, 1)
        g.vignetteOuter = (0.9, 0.9, 0.9)
        g.vignetteInner = (0.99, 0.99, 0.99)
        g.vrCameraOffset = (0, -4.2, -1.1)
        g.vrNearClip = 0.5
        lightsColor = (3*40, 2.82*40, 2.16*40)
        lightsBeamColor = (3, 2.82, 2.16)
        self.flag = True
        self.stdtint = deftint

        def lights_off():
            bsUtils.animateArray(self.light1, 'color', 3,
                {0: lightsColor, 3000: (0, 0, 0)})

            bsUtils.animateArray(self.light2, 'color', 3,
                {0: lightsColor, 3000: (0, 0, 0)})

            bsUtils.animateArray(self.light3, 'color', 3,
                {0: lightsColor, 3000: (0, 0, 0)})

            bsUtils.animateArray(self.light4, 'color', 3,
                {0: lightsColor, 3000: (0, 0, 0)})

            bsUtils.animateArray(self.light5, 'color', 3,
                {0: lightsColor, 3000: (0, 0, 0)})

            bsUtils.animateArray(self.light6, 'color', 3,
                {0: lightsColor, 3000: (0, 0, 0)})

            bsUtils.animateArray(self.light7, 'color', 3,
                {0: lightsColor, 3000: (0, 0, 0)})

            bsUtils.animateArray(self.light1beam, 'color', 3,
                {0: lightsBeamColor, 3000: (0, 0, 0)})

            bsUtils.animateArray(self.light2beam, 'color', 3,
                {0: lightsBeamColor, 3000: (0, 0, 0)})

            bsUtils.animateArray(self.light3beam, 'color', 3,
                {0: lightsBeamColor, 3000: (0, 0, 0)})

            bsUtils.animateArray(self.light4beam, 'color', 3,
                {0: lightsBeamColor, 3000: (0, 0, 0)})

            bsUtils.animateArray(self.light5beam, 'color', 3,
                {0: lightsBeamColor, 3000: (0, 0, 0)})

            bsUtils.animateArray(self.light6beam, 'color', 3,
                {0: lightsBeamColor, 3000: (0, 0, 0)})

            bsUtils.animateArray(self.light7beam, 'color', 3,
                {0: lightsBeamColor, 3000: (0, 0, 0)})

        def lights_on():
            if self.flag == True and self.stdtint[0] < 0.75:
                bsUtils.animateArray(self.light1, 'color', 3,
                    {0: (0, 0, 0), 3000: lightsColor})

                bsUtils.animateArray(self.light2, 'color', 3,
                    {0: (0, 0, 0), 3000: lightsColor})

                bsUtils.animateArray(self.light3, 'color', 3,
                    {0: (0, 0, 0), 3000: lightsColor})

                bsUtils.animateArray(self.light4, 'color', 3,
                    {0: (0, 0, 0), 3000: lightsColor})

                bsUtils.animateArray(self.light5, 'color', 3,
                    {0: (0, 0, 0), 3000: lightsColor})

                bsUtils.animateArray(self.light6, 'color', 3,
                    {0: (0, 0, 0), 3000: lightsColor})

                bsUtils.animateArray(self.light7, 'color', 3,
                    {0: (0, 0, 0), 3000: lightsColor})

                bsUtils.animateArray(self.light1beam, 'color', 3,
                    {0: (0, 0, 0), 3000: lightsBeamColor})

                bsUtils.animateArray(self.light2beam, 'color', 3,
                    {0: (0, 0, 0), 3000: lightsBeamColor})

                bsUtils.animateArray(self.light3beam, 'color', 3,
                    {0: (0, 0, 0), 3000: lightsBeamColor})

                bsUtils.animateArray(self.light4beam, 'color', 3,
                    {0: (0, 0, 0), 3000: lightsBeamColor})

                bsUtils.animateArray(self.light5beam, 'color', 3,
                    {0: (0, 0, 0), 3000: lightsBeamColor})

                bsUtils.animateArray(self.light6beam, 'color', 3,
                    {0: (0, 0, 0), 3000: lightsBeamColor})

                bsUtils.animateArray(self.light7beam, 'color', 3,
                    {0: (0, 0, 0), 3000: lightsBeamColor})

                self.flag = False
                def gvn():
                    self.flag = True

                bs.gameTimer(230100, gvn)
                bs.gameTimer(130000, bs.Call(lights_off))

            else: pass

        def chckr():
            if not self.stdtint == bs.getSharedObject('globals').tint:
                self.stdtint = bs.getSharedObject('globals').tint
            else:
                self.flag = True
                bs.Call(lights_off)
                self.a = 1
                bs.animateArray(bs.getSharedObject('globals'), 'tint', 3, {
                    0: deftint, 60000: deftint2, 90000: (0.6, 0.3, 0.3),
                    120000: (0.2, 0.2, 0.4), 180000: (0.21, 0.21, 0.41),
                    210000: (0.6, 0.3, 0.3), 240000: deftint
                    }, loop=True)

                self.a = bs.gameTimer(80000, bs.Call(lights_on), repeat=True)

        chckr()
        bs.gameTimer(500, bs.Call(chckr), repeat=True)

    def _isPointNearEdge(self, p, running=False):
        boxPosition = self.defs.boxes['edgeBox'][0:3]
        boxScale = self.defs.boxes['edgeBox'][6:9]
        x = (p.x()-boxPosition[0])/boxScale[0]
        z = (p.z()-boxPosition[2])/boxScale[2]
        return (x < -0.5 or x > 0.5 or z < -0.5 or z > 0.5)

registerMap(Airlands)

class HockeyStadium(Map):
    import hockeyStadiumDefs as defs
    name = "Hockey Stadium"
    playTypes = ['melee','hockey','teamFlag','keepAway']

    @classmethod
    def getPreviewTextureName(cls):
        return 'hockeyStadiumPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['models'] = (bs.getModel('hockeyStadiumOuter'),
                                       bs.getModel('hockeyStadiumInner'),
                                       bs.getModel('hockeyStadiumStands'))
        data['vrFillModel'] = bs.getModel('footballStadiumVRFill')
        data['collideModel'] = bs.getCollideModel('hockeyStadiumCollide')
        data['tex'] = bs.getTexture('hockeyStadium')
        data['standsTex'] = bs.getTexture('footballStadium')
        m = bs.Material()
        m.addActions(actions=('modifyPartCollision', 'friction',0.01))
        data['iceMaterial'] = m
        return data
    
    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode("terrain", delegate=self, attrs={
            'model':self.preloadData['models'][0],
            'collideModel':self.preloadData['collideModel'],
            'colorTexture':self.preloadData['tex'],
            'materials':[bs.getSharedObject('footingMaterial'),
                         self.preloadData['iceMaterial']]})
        bs.newNode('terrain', attrs={
            'model':self.preloadData['vrFillModel'],
            'vrOnly':True,
            'lighting':False,
            'background':True,
            'colorTexture':self.preloadData['standsTex']})
        self.floor = bs.newNode("terrain", attrs={
            "model":self.preloadData['models'][1],
            "colorTexture":self.preloadData['tex'],
            "opacity":0.92,
            "opacityInLowOrMediumQuality":1.0,
            "materials":[bs.getSharedObject('footingMaterial'),
                         self.preloadData['iceMaterial']]})
        self.stands = bs.newNode("terrain", attrs={
            "model":self.preloadData['models'][2],
            "visibleInReflections":False,
            "colorTexture":self.preloadData['standsTex']})
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.floorReflection = True
        bsGlobals.debrisFriction = 0.3
        bsGlobals.debrisKillHeight = -0.3
        bsGlobals.tint = (1.2,1.3,1.33)
        bsGlobals.ambientColor = (1.15,1.25,1.6)
        bsGlobals.vignetteOuter = (0.66,0.67,0.73)
        bsGlobals.vignetteInner = (0.93,0.93,0.95)
        bsGlobals.vrCameraOffset = (0,-0.8,-1.1)
        bsGlobals.vrNearClip = 0.5
        self.isHockey = True

registerMap(HockeyStadium)

class FootballStadium(Map):
    import footballStadiumDefs as defs
    name = "Football Stadium"
    playTypes = ['melee', 'football', 'teamFlag', 'keepAway']

    @classmethod
    def getPreviewTextureName(cls):
        return 'footballStadiumPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel("footballStadium")
        data['vrFillModel'] = bs.getModel('footballStadiumVRFill')
        data['collideModel'] = bs.getCollideModel("footballStadiumCollide")
        data['tex'] = bs.getTexture("footballStadium")
        return data

    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain', delegate=self, attrs={
            'model':self.preloadData['model'],
            'collideModel':self.preloadData['collideModel'],
            'colorTexture':self.preloadData['tex'],
            'materials':[bs.getSharedObject('footingMaterial')]})
        bs.newNode('terrain',
                   attrs={'model':self.preloadData['vrFillModel'],
                          'lighting':False,
                          'vrOnly':True,
                          'background':True,
                          'colorTexture':self.preloadData['tex']})
        g = bs.getSharedObject('globals')
        g.tint = (1.3, 1.2, 1.0)
        g.ambientColor = (1.3, 1.2, 1.0)
        g.vignetteOuter = (0.57, 0.57, 0.57)
        g.vignetteInner = (0.9, 0.9, 0.9)
        g.vrCameraOffset = (0, -0.8, -1.1)
        g.vrNearClip = 0.5

    def _isPointNearEdge(self,p,running=False):
        boxPosition = self.defs.boxes['edgeBox'][0:3]
        boxScale = self.defs.boxes['edgeBox'][6:9]
        x = (p.x() - boxPosition[0])/boxScale[0]
        z = (p.z() - boxPosition[2])/boxScale[2]
        return (x < -0.5 or x > 0.5 or z < -0.5 or z > 0.5)

registerMap(FootballStadium)

class BridgitMap(Map):
    import bridgitLevelDefs as defs
    name = "Bridgit"
    playTypes = ["melee","teamFlag",'keepAway']

    @classmethod
    def getPreviewTextureName(cls):
        return 'bridgitPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['modelTop'] = bs.getModel("bridgitLevelTop")
        data['modelBottom'] = bs.getModel("bridgitLevelBottom")
        data['modelBG'] = bs.getModel("natureBackground")
        data['bgVRFillModel'] = bs.getModel('natureBackgroundVRFill')
        data['collideModel'] = bs.getCollideModel("bridgitLevelCollide")
        data['tex'] = bs.getTexture("bridgitLevelColor")
        data['modelBGTex'] = bs.getTexture("natureBackgroundColor")
        data['collideBG'] = bs.getCollideModel("natureBackgroundCollide")
        data['railingCollideModel'] = \
            bs.getCollideModel("bridgitLevelRailingCollide")
        data['bgMaterial'] = bs.Material()
        data['bgMaterial'].addActions(actions=('modifyPartCollision',
                                               'friction', 10.0))
        return data

    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain', delegate=self, attrs={
            'collideModel':self.preloadData['collideModel'],
            'model':self.preloadData['modelTop'],
            'colorTexture':self.preloadData['tex'],
            'materials':[bs.getSharedObject('footingMaterial')]})
        self.bottom = bs.newNode('terrain', attrs={
            'model':self.preloadData['modelBottom'],
            'lighting':False,
            'colorTexture':self.preloadData['tex']})
        self.foo = bs.newNode('terrain', attrs={
            'model':self.preloadData['modelBG'],
            'lighting':False,
            'background':True,
            'colorTexture':self.preloadData['modelBGTex']})
        bs.newNode('terrain', attrs={
            'model':self.preloadData['bgVRFillModel'],
            'lighting':False,
            'vrOnly':True,
            'background':True,
            'colorTexture':self.preloadData['modelBGTex']})
        self.railing = bs.newNode('terrain', attrs={
            'collideModel':self.preloadData['railingCollideModel'],
            'materials':[bs.getSharedObject('railingMaterial')],
            'bumper':True})
        self.bgCollide = bs.newNode('terrain', attrs={
            'collideModel':self.preloadData['collideBG'],
            'materials':[bs.getSharedObject('footingMaterial'),
                         self.preloadData['bgMaterial'],
                         bs.getSharedObject('deathMaterial')]})
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.tint = (1.1, 1.2, 1.3)
        bsGlobals.ambientColor = (1.1, 1.2, 1.3)
        bsGlobals.vignetteOuter = (0.65, 0.6, 0.55)
        bsGlobals.vignetteInner = (0.9, 0.9, 0.93)

registerMap(BridgitMap)

class BigGMap(Map):
    import bigGDefs as defs
    name = 'Big G'
    playTypes = ['race', 'melee', 'keepAway', 'teamFlag',
                 'kingOfTheHill', 'conquest']

    @classmethod
    def getPreviewTextureName(cls):
        return 'bigGPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['modelTop'] = bs.getModel('bigG')
        data['modelBottom'] = bs.getModel('bigGBottom')
        data['modelBG'] = bs.getModel('natureBackground')
        data['bgVRFillModel'] = bs.getModel('natureBackgroundVRFill')
        data['collideModel'] = bs.getCollideModel('bigGCollide')
        data['tex'] = bs.getTexture('bigG')
        data['modelBGTex'] = bs.getTexture('natureBackgroundColor')
        data['collideBG'] = bs.getCollideModel('natureBackgroundCollide')
        data['bumperCollideModel'] = bs.getCollideModel('bigGBumper')
        data['bgMaterial'] = bs.Material()
        data['bgMaterial'].addActions(actions=('modifyPartCollision',
                                               'friction', 10.0))
        return data

    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain', delegate=self, attrs={
            'collideModel':self.preloadData['collideModel'],
            'color':(0.7,0.7,0.7),
            'model':self.preloadData['modelTop'],
            'colorTexture':self.preloadData['tex'],
            'materials':[bs.getSharedObject('footingMaterial')]})
        self.bottom = bs.newNode('terrain', attrs={
            'model':self.preloadData['modelBottom'],
            'color':(0.7,0.7,0.7),
            'lighting':False,
            'colorTexture':self.preloadData['tex']})
        self.foo = bs.newNode('terrain', attrs={
            'model':self.preloadData['modelBG'],
            'lighting':False,
            'background':True,
            'colorTexture':self.preloadData['modelBGTex']})
        bs.newNode('terrain', attrs={
            'model':self.preloadData['bgVRFillModel'],
            'lighting':False,
            'vrOnly':True,
            'background':True,
            'colorTexture':self.preloadData['modelBGTex']})
        self.railing = bs.newNode('terrain', attrs={
            'collideModel':self.preloadData['bumperCollideModel'],
            'materials':[bs.getSharedObject('railingMaterial')],
            'bumper':True})
        self.bgCollide = bs.newNode('terrain', attrs={
            'collideModel':self.preloadData['collideBG'],
            'materials':[bs.getSharedObject('footingMaterial'),
                         self.preloadData['bgMaterial'],
                         bs.getSharedObject('deathMaterial')]})
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.tint = (1.1, 1.2, 1.3)
        bsGlobals.ambientColor = (1.1, 1.2, 1.3)
        bsGlobals.vignetteOuter = (0.65, 0.6, 0.55)
        bsGlobals.vignetteInner = (0.9, 0.9, 0.93)

registerMap(BigGMap)

class RoundaboutMap(Map):
    import roundaboutLevelDefs as defs
    name = 'Roundabout'
    playTypes = ['melee','keepAway','teamFlag']

    @classmethod
    def getPreviewTextureName(cls):
        return 'roundaboutPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('roundaboutLevel')
        data['modelBottom'] = bs.getModel('roundaboutLevelBottom')
        data['modelBG'] = bs.getModel('natureBackground')
        data['bgVRFillModel'] = bs.getModel('natureBackgroundVRFill')
        data['collideModel'] = bs.getCollideModel('roundaboutLevelCollide')
        data['tex'] = bs.getTexture('roundaboutLevelColor')
        data['modelBGTex'] = bs.getTexture('natureBackgroundColor')
        data['collideBG'] = bs.getCollideModel('natureBackgroundCollide')
        data['railingCollideModel'] = \
            bs.getCollideModel('roundaboutLevelBumper')
        data['bgMaterial'] = bs.Material()
        data['bgMaterial'].addActions(actions=('modifyPartCollision',
                                               'friction', 10.0))
        return data
    
    def __init__(self):
        Map.__init__(self,vrOverlayCenterOffset=(0,-1,1))
        self.node = bs.newNode('terrain', delegate=self, attrs={
            'collideModel':self.preloadData['collideModel'],
            'model':self.preloadData['model'],
            'colorTexture':self.preloadData['tex'],
            'materials':[bs.getSharedObject('footingMaterial')]})
        self.bottom = bs.newNode('terrain', attrs={
            'model':self.preloadData['modelBottom'],
            'lighting':False,
            'colorTexture':self.preloadData['tex']})
        self.bg = bs.newNode('terrain', attrs={
            'model':self.preloadData['modelBG'],
            'lighting':False,
            'background':True,
            'colorTexture':self.preloadData['modelBGTex']})
        bs.newNode('terrain', attrs={
            'model':self.preloadData['bgVRFillModel'],
            'lighting':False,
            'vrOnly':True,
            'background':True,
            'colorTexture':self.preloadData['modelBGTex']})
        self.bgCollide = bs.newNode('terrain', attrs={
            'collideModel':self.preloadData['collideBG'],
            'materials':[bs.getSharedObject('footingMaterial'),
                         self.preloadData['bgMaterial'],
                         bs.getSharedObject('deathMaterial')]})
        self.railing = bs.newNode('terrain', attrs={
            'collideModel':self.preloadData['railingCollideModel'],
            'materials':[bs.getSharedObject('railingMaterial')],
            'bumper':True})
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.tint = (1.0, 1.05, 1.1)
        bsGlobals.ambientColor = (1.0, 1.05, 1.1)
        bsGlobals.shadowOrtho = True
        bsGlobals.vignetteOuter = (0.63, 0.65, 0.7)
        bsGlobals.vignetteInner = (0.97, 0.95, 0.93)

registerMap(RoundaboutMap)

class MonkeyFaceMap(Map):
    import monkeyFaceLevelDefs as defs
    name = 'Monkey Face'
    playTypes = ['melee','keepAway','teamFlag']

    @classmethod
    def getPreviewTextureName(cls):
        return 'monkeyFacePreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('monkeyFaceLevel')
        data['bottomModel'] = bs.getModel('monkeyFaceLevelBottom')
        data['modelBG'] = bs.getModel('natureBackground')
        data['bgVRFillModel'] = bs.getModel('natureBackgroundVRFill')
        data['collideModel'] = bs.getCollideModel('monkeyFaceLevelCollide')
        data['tex'] = bs.getTexture('monkeyFaceLevelColor')
        data['modelBGTex'] = bs.getTexture('natureBackgroundColor')
        data['collideBG'] = bs.getCollideModel('natureBackgroundCollide')
        data['railingCollideModel'] = \
            bs.getCollideModel('monkeyFaceLevelBumper')
        data['bgMaterial'] = bs.Material()
        data['bgMaterial'].addActions(actions=('modifyPartCollision',
                                               'friction', 10.0))
        return data
    
    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain', delegate=self, attrs={
            'collideModel':self.preloadData['collideModel'],
            'model':self.preloadData['model'],
            'colorTexture':self.preloadData['tex'],
            'materials':[bs.getSharedObject('footingMaterial')]})
        self.bottom = bs.newNode('terrain', attrs={
            'model':self.preloadData['bottomModel'],
            'lighting':False,
            'colorTexture':self.preloadData['tex']})
        self.foo = bs.newNode('terrain', attrs={
            'model':self.preloadData['modelBG'],
            'lighting':False,
            'background':True,
            'colorTexture':self.preloadData['modelBGTex']})
        bs.newNode('terrain', attrs={
            'model':self.preloadData['bgVRFillModel'],
            'lighting':False,
            'vrOnly':True,
            'background':True,
            'colorTexture':self.preloadData['modelBGTex']})
        self.bgCollide = bs.newNode('terrain', attrs={
            'collideModel':self.preloadData['collideBG'],
            'materials':[bs.getSharedObject('footingMaterial'),
                         self.preloadData['bgMaterial'],
                         bs.getSharedObject('deathMaterial')]})
        self.railing = bs.newNode('terrain', attrs={
            'collideModel':self.preloadData['railingCollideModel'],
            'materials':[bs.getSharedObject('railingMaterial')],
            'bumper':True})
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.tint = (1.1, 1.2, 1.2)
        bsGlobals.ambientColor = (1.2, 1.3, 1.3)
        bsGlobals.vignetteOuter = (0.60, 0.62, 0.66)
        bsGlobals.vignetteInner = (0.97, 0.95, 0.93)
        bsGlobals.vrCameraOffset = (-1.4, 0, 0)

registerMap(MonkeyFaceMap)

class ZigZagMap(Map):
    import zigZagLevelDefs as defs
    name = 'Zigzag'
    playTypes = ['melee', 'keepAway', 'teamFlag', 'conquest', 'kingOfTheHill']

    @classmethod
    def getPreviewTextureName(cls):
        return 'zigzagPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('zigZagLevel')
        data['modelBottom'] = bs.getModel('zigZagLevelBottom')
        data['modelBG'] = bs.getModel('natureBackground')
        data['bgVRFillModel'] = bs.getModel('natureBackgroundVRFill')
        data['collideModel'] = bs.getCollideModel('zigZagLevelCollide')
        data['tex'] = bs.getTexture('zigZagLevelColor')
        data['modelBGTex'] = bs.getTexture('natureBackgroundColor')
        data['collideBG'] = bs.getCollideModel('natureBackgroundCollide')
        data['railingCollideModel'] = bs.getCollideModel('zigZagLevelBumper')
        data['bgMaterial'] = bs.Material()
        data['bgMaterial'].addActions(actions=('modifyPartCollision',
                                               'friction', 10.0))
        return data
    
    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain', delegate=self, attrs={
            'collideModel':self.preloadData['collideModel'],
            'model':self.preloadData['model'],
            'colorTexture':self.preloadData['tex'],
            'materials':[bs.getSharedObject('footingMaterial')]})
        self.foo = bs.newNode('terrain', attrs={
            'model':self.preloadData['modelBG'],
            'lighting':False,
            'colorTexture':self.preloadData['modelBGTex']})
        self.bottom = bs.newNode('terrain', attrs={
            'model':self.preloadData['modelBottom'],
            'lighting':False,
            'colorTexture':self.preloadData['tex']})
        bs.newNode('terrain', attrs={
            'model':self.preloadData['bgVRFillModel'],
            'lighting':False,
            'vrOnly':True,
            'background':True,
            'colorTexture':self.preloadData['modelBGTex']})
        self.bgCollide = bs.newNode('terrain', attrs={
            'collideModel':self.preloadData['collideBG'],
            'materials':[bs.getSharedObject('footingMaterial'),
                         self.preloadData['bgMaterial'],
                         bs.getSharedObject('deathMaterial')]})
        self.railing = bs.newNode('terrain', attrs={
            'collideModel':self.preloadData['railingCollideModel'],
            'materials':[bs.getSharedObject('railingMaterial')],
            'bumper':True})
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.tint = (1.0, 1.15, 1.15)
        bsGlobals.ambientColor = (1.0, 1.15, 1.15)
        bsGlobals.vignetteOuter = (0.57, 0.59, 0.63)
        bsGlobals.vignetteInner = (0.97, 0.95, 0.93)
        bsGlobals.vrCameraOffset = (-1.5, 0, 0)

registerMap(ZigZagMap)

class ThePadMap(Map):
    import thePadLevelDefs as defs
    name = 'The Pad'
    playTypes = ['melee','keepAway','teamFlag','kingOfTheHill']

    @classmethod
    def getPreviewTextureName(cls):
        return 'thePadPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('thePadLevel')
        data['bottomModel'] = bs.getModel('thePadLevelBottom')
        data['collideModel'] = bs.getCollideModel('thePadLevelCollide')
        data['tex'] = bs.getTexture('thePadLevelColor')
        data['bgTex'] = bs.getTexture('menuBG')
        # fixme should chop this into vr/non-vr sections for efficiency
        data['bgModel'] = bs.getModel('thePadBG')
        data['railingCollideModel'] = bs.getCollideModel('thePadLevelBumper')
        data['vrFillMoundModel'] = bs.getModel('thePadVRFillMound')
        data['vrFillMoundTex'] = bs.getTexture('vrFillMound')
        return data

    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain', delegate=self, attrs={
            'collideModel':self.preloadData['collideModel'],
            'model':self.preloadData['model'],
            'colorTexture':self.preloadData['tex'],
            'materials':[bs.getSharedObject('footingMaterial')]})
        self.bottom = bs.newNode('terrain', attrs={
            'model':self.preloadData['bottomModel'],
            'lighting':False,
            'colorTexture':self.preloadData['tex']})
        self.foo = bs.newNode('terrain', attrs={
            'model':self.preloadData['bgModel'],
            'lighting':False,
            'background':True,
            'colorTexture':self.preloadData['bgTex']})
        self.railing = bs.newNode('terrain', attrs={
            'collideModel':self.preloadData['railingCollideModel'],
            'materials':[bs.getSharedObject('railingMaterial')],
            'bumper':True})
        bs.newNode('terrain', attrs={
            'model':self.preloadData['vrFillMoundModel'],
            'lighting':False,
            'vrOnly':True,
            'color':(0.56,0.55,0.47),
            'background':True,
            'colorTexture':self.preloadData['vrFillMoundTex']})
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.tint = (1.1, 1.1, 1.0)
        bsGlobals.ambientColor = (1.1, 1.1, 1.0)
        bsGlobals.vignetteOuter = (0.7, 0.65, 0.75)
        bsGlobals.vignetteInner = (0.95, 0.95, 0.93)

registerMap(ThePadMap)

class DoomShroomMap(Map):
    import doomShroomLevelDefs as defs
    name = 'Doom Shroom'
    playTypes = ['melee', 'keepAway', 'teamFlag']

    @classmethod
    def getPreviewTextureName(cls):
        return 'doomShroomPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('doomShroomLevel')
        data['collideModel'] = bs.getCollideModel('doomShroomLevelCollide')
        data['tex'] = bs.getTexture('doomShroomLevelColor')
        data['bgTex'] = bs.getTexture('doomShroomBGColor')
        data['bgModel'] = bs.getModel('doomShroomBG')
        data['vrFillModel'] = bs.getModel('doomShroomVRFill')
        data['stemModel'] = bs.getModel('doomShroomStem')
        data['collideBG'] = bs.getCollideModel('doomShroomStemCollide')
        return data
    
    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain', delegate=self, attrs={
            'collideModel':self.preloadData['collideModel'],
            'model':self.preloadData['model'],
            'colorTexture':self.preloadData['tex'],
            'materials':[bs.getSharedObject('footingMaterial')]})
        self.foo = bs.newNode('terrain', attrs={
            'model':self.preloadData['bgModel'],
            'lighting':False,
            'background':True,
            'colorTexture':self.preloadData['bgTex']})
        bs.newNode('terrain', attrs={
            'model':self.preloadData['vrFillModel'],
            'lighting':False,
            'vrOnly':True,
            'background':True,
            'colorTexture':self.preloadData['bgTex']})
        self.stem = bs.newNode('terrain', attrs={
            'model':self.preloadData['stemModel'],
            'lighting':False,
            'colorTexture':self.preloadData['tex']})
        self.bgCollide = bs.newNode('terrain', attrs={
            'collideModel':self.preloadData['collideBG'],
            'materials':[bs.getSharedObject('footingMaterial'),
                         bs.getSharedObject('deathMaterial')]})
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.tint = (0.82, 1.10, 1.15)
        bsGlobals.ambientColor = (0.9, 1.3, 1.1)
        bsGlobals.shadowOrtho = False
        bsGlobals.vignetteOuter = (0.76, 0.76, 0.76)
        bsGlobals.vignetteInner = (0.95, 0.95, 0.99)

    def _isPointNearEdge(self,p,running=False):
        x = p.x()
        z = p.z()
        xAdj = x*0.125
        zAdj = (z+3.7)*0.2
        if running:
            xAdj *= 1.4
            zAdj *= 1.4
        return (xAdj*xAdj+zAdj*zAdj > 1.0)

registerMap(DoomShroomMap)

class LakeFrigidMap(Map):
    import lakeFrigidDefs as defs
    name = 'Lake Frigid'
    playTypes = ['melee', 'keepAway', 'teamFlag', 'race']

    @classmethod
    def getPreviewTextureName(cls):
        return 'lakeFrigidPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('lakeFrigid')
        data['modelTop'] = bs.getModel('lakeFrigidTop')
        data['modelReflections'] = bs.getModel('lakeFrigidReflections')
        data['collideModel'] = bs.getCollideModel('lakeFrigidCollide')
        data['tex'] = bs.getTexture('lakeFrigid')
        data['texReflections'] = bs.getTexture('lakeFrigidReflections')
        data['vrFillModel'] = bs.getModel('lakeFrigidVRFill')
        m = bs.Material()
        m.addActions(actions=('modifyPartCollision','friction',0.01))
        data['iceMaterial'] = m
        return data

    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain', delegate=self, attrs={
            'collideModel':self.preloadData['collideModel'],
            'model':self.preloadData['model'],
            'colorTexture':self.preloadData['tex'],
            'materials':[bs.getSharedObject('footingMaterial'),
                         self.preloadData['iceMaterial']]})
        bs.newNode('terrain', attrs={
            'model':self.preloadData['modelTop'],
            'lighting':False,
            'colorTexture':self.preloadData['tex']})
        bs.newNode('terrain', attrs={
            'model':self.preloadData['modelReflections'],
            'lighting':False,
            'overlay':True,
            'opacity':0.15,
            'colorTexture':self.preloadData['texReflections']})
        bs.newNode('terrain', attrs={
            'model':self.preloadData['vrFillModel'],
            'lighting':False,
            'vrOnly':True,
            'background':True,
            'colorTexture':self.preloadData['tex']})
        g = bs.getSharedObject('globals')
        g.tint = (1, 1, 1)
        g.ambientColor = (1, 1, 1)
        g.shadowOrtho = True
        g.vignetteOuter = (0.86, 0.86, 0.86)
        g.vignetteInner = (0.95, 0.95, 0.99)
        g.vrNearClip = 0.5
        self.isHockey = True

registerMap(LakeFrigidMap)

class TipTopMap(Map):
    import tipTopLevelDefs as defs
    name = 'Tip Top'
    playTypes = ['melee', 'keepAway', 'teamFlag', 'kingOfTheHill']

    @classmethod
    def getPreviewTextureName(cls):
        return 'tipTopPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('tipTopLevel')
        data['bottomModel'] = bs.getModel('tipTopLevelBottom')
        data['collideModel'] = bs.getCollideModel('tipTopLevelCollide')
        data['tex'] = bs.getTexture('tipTopLevelColor')
        data['bgTex'] = bs.getTexture('tipTopBGColor')
        data['bgModel'] = bs.getModel('tipTopBG')
        data['railingCollideModel'] = bs.getCollideModel('tipTopLevelBumper')
        return data
    
    def __init__(self):
        Map.__init__(self,vrOverlayCenterOffset=(0,-0.2,2.5))
        self.node = bs.newNode('terrain', delegate=self, attrs={
            'collideModel':self.preloadData['collideModel'],
            'model':self.preloadData['model'],
            'colorTexture':self.preloadData['tex'],
            'color':(0.7,0.7,0.7),
            'materials':[bs.getSharedObject('footingMaterial')]})
        self.bottom = bs.newNode('terrain', attrs={
            'model':self.preloadData['bottomModel'],
            'lighting':False,
            'color':(0.7,0.7,0.7),
            'colorTexture':self.preloadData['tex']})
        self.bg = bs.newNode('terrain', attrs={
            'model':self.preloadData['bgModel'],
            'lighting':False,
            'color':(0.4,0.4,0.4),
            'background':True,
            'colorTexture':self.preloadData['bgTex']})
        self.railing = bs.newNode('terrain', attrs={
            'collideModel':self.preloadData['railingCollideModel'],
            'materials':[bs.getSharedObject('railingMaterial')],
            'bumper':True})
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.tint = (0.8, 0.9, 1.3)
        bsGlobals.ambientColor = (0.8, 0.9, 1.3)
        bsGlobals.vignetteOuter = (0.79, 0.79, 0.69)
        bsGlobals.vignetteInner = (0.97, 0.97, 0.99)

registerMap(TipTopMap)


class CragCastleMap(Map):
    import cragCastleDefs as defs
    name = 'Crag Castle'
    playTypes = ['melee','keepAway','teamFlag','conquest']

    @classmethod
    def getPreviewTextureName(cls):
        return 'cragCastlePreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('cragCastleLevel')
        data['bottomModel'] = bs.getModel('cragCastleLevelBottom')
        data['collideModel'] = bs.getCollideModel('cragCastleLevelCollide')
        data['tex'] = bs.getTexture('cragCastleLevelColor')
        data['bgTex'] = bs.getTexture('menuBG')
        # fixme should chop this into vr/non-vr sections
        data['bgModel'] = bs.getModel('thePadBG')
        data['railingCollideModel'] = \
            bs.getCollideModel('cragCastleLevelBumper')
        data['vrFillMoundModel'] = bs.getModel('cragCastleVRFillMound')
        data['vrFillMoundTex'] = bs.getTexture('vrFillMound')
        return data
    
    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain', delegate=self, attrs={
            'collideModel':self.preloadData['collideModel'],
            'model':self.preloadData['model'],
            'colorTexture':self.preloadData['tex'],
            'materials':[bs.getSharedObject('footingMaterial')]})
        self.bottom = bs.newNode('terrain', attrs={
            'model':self.preloadData['bottomModel'],
            'lighting':False,
            'colorTexture':self.preloadData['tex']})
        self.bg = bs.newNode('terrain', attrs={
            'model':self.preloadData['bgModel'],
            'lighting':False,
            'background':True,
            'colorTexture':self.preloadData['bgTex']})
        self.railing = bs.newNode('terrain', attrs={
            'collideModel':self.preloadData['railingCollideModel'],
            'materials':[bs.getSharedObject('railingMaterial')],
            'bumper':True})
        bs.newNode('terrain', attrs={
            'model':self.preloadData['vrFillMoundModel'],
            'lighting':False,
            'vrOnly':True,
            'color':(0.2,0.25,0.2),
            'background':True,
            'colorTexture':self.preloadData['vrFillMoundTex']})
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.shadowOrtho = True
        bsGlobals.shadowOffset = (0,0, -5.0)
        bsGlobals.tint = (1.15, 1.05, 0.75)
        bsGlobals.ambientColor = (1.15,1.05,0.75)
        bsGlobals.vignetteOuter = (0.6, 0.65, 0.6)
        bsGlobals.vignetteInner = (0.95, 0.95, 0.95)
        bsGlobals.vrNearClip = 1.0

registerMap(CragCastleMap)

class TowerDMap(Map):
    import towerDLevelDefs as defs
    name = 'Tower D'
    playTypes = []

    @classmethod
    def getPreviewTextureName(cls):
        return 'towerDPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('towerDLevel')
        data['modelBottom'] = bs.getModel('towerDLevelBottom')
        data['collideModel'] = bs.getCollideModel('towerDLevelCollide')
        data['tex'] = bs.getTexture('towerDLevelColor')
        data['bgTex'] = bs.getTexture('menuBG')
        # fixme should chop this into vr/non-vr sections
        data['bgModel'] = bs.getModel('thePadBG')
        data['playerWallCollideModel'] = bs.getCollideModel('towerDPlayerWall')
        data['playerWallMaterial'] = bs.Material()
        data['playerWallMaterial'].addActions(actions=(('modifyPartCollision',
                                                        'friction', 0.0)))
        # anything that needs to hit the wall can apply this material
        data['collideWithWallMaterial'] = bs.Material()
        data['playerWallMaterial'].addActions(
            conditions=('theyDontHaveMaterial',data['collideWithWallMaterial']),
            actions=(('modifyPartCollision','collide',False)))
        data['vrFillMoundModel'] = bs.getModel('stepRightUpVRFillMound')
        data['vrFillMoundTex'] = bs.getTexture('vrFillMound')
        return data

    def __init__(self):
        Map.__init__(self,vrOverlayCenterOffset=(0,1,1))
        self.node = bs.newNode('terrain', delegate=self, attrs={
            'collideModel':self.preloadData['collideModel'],
            'model':self.preloadData['model'],
            'colorTexture':self.preloadData['tex'],
            'materials':[bs.getSharedObject('footingMaterial')]})
        self.nodeBottom = bs.newNode('terrain', delegate=self, attrs={
            'model':self.preloadData['modelBottom'],
            'lighting':False,
            'colorTexture':self.preloadData['tex']})
        bs.newNode('terrain', attrs={
            'model':self.preloadData['vrFillMoundModel'],
            'lighting':False,
            'vrOnly':True,
            'color':(0.53,0.57,0.5),
            'background':True,
            'colorTexture':self.preloadData['vrFillMoundTex']})
        self.bg = bs.newNode('terrain', attrs={
            'model':self.preloadData['bgModel'],
            'lighting':False,
            'background':True,
            'colorTexture':self.preloadData['bgTex']})
        self.playerWall = bs.newNode('terrain', attrs={
            'collideModel':self.preloadData['playerWallCollideModel'],
            'affectBGDynamics':False,
            'materials':[self.preloadData['playerWallMaterial']]})
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.tint = (1.15, 1.11, 1.03)
        bsGlobals.ambientColor = (1.2, 1.1, 1.0)
        bsGlobals.vignetteOuter = (0.7, 0.73, 0.7)
        bsGlobals.vignetteInner = (0.95, 0.95, 0.95)

    def _isPointNearEdge(self,p,running=False):
        # see if we're within edgeBox
        boxes = self.defs.boxes
        boxPosition = boxes['edgeBox'][0:3]
        boxScale = boxes['edgeBox'][6:9]
        boxPosition2 = boxes['edgeBox2'][0:3]
        boxScale2 = boxes['edgeBox2'][6:9]
        x = (p.x() - boxPosition[0])/boxScale[0]
        z = (p.z() - boxPosition[2])/boxScale[2]
        x2 = (p.x() - boxPosition2[0])/boxScale2[0]
        z2 = (p.z() - boxPosition2[2])/boxScale2[2]
        # if we're outside of *both* boxes we're near the edge
        return ((x < -0.5 or x > 0.5 or z < -0.5 or z > 0.5)
                and (x2 < -0.5 or x2 > 0.5 or z2 < -0.5 or z2 > 0.5))

registerMap(TowerDMap)

class AlwaysLandMap(Map):
    import alwaysLandLevelDefs as defs
    name = 'Happy Thoughts'
    playTypes = ['melee', 'keepAway', 'teamFlag', 'conquest', 'kingOfTheHill']

    @classmethod
    def getPreviewTextureName(cls):
        return 'alwaysLandPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('alwaysLandLevel')
        data['bottomModel'] = bs.getModel('alwaysLandLevelBottom')
        data['bgModel'] = bs.getModel('alwaysLandBG')
        data['collideModel'] = bs.getCollideModel('alwaysLandLevelCollide')
        data['tex'] = bs.getTexture('alwaysLandLevelColor')
        data['bgTex'] = bs.getTexture('alwaysLandBGColor')
        data['vrFillMoundModel'] = bs.getModel('alwaysLandVRFillMound')
        data['vrFillMoundTex'] = bs.getTexture('vrFillMound')
        return data

    @classmethod
    def getMusicType(cls):
        return 'Flying'
    
    def __init__(self):
        Map.__init__(self,vrOverlayCenterOffset=(0,-3.7,2.5))
        self.node = bs.newNode('terrain', delegate=self, attrs={
            'collideModel':self.preloadData['collideModel'],
            'model':self.preloadData['model'],
            'colorTexture':self.preloadData['tex'],
            'materials':[bs.getSharedObject('footingMaterial')]})
        self.bottom = bs.newNode('terrain', attrs={
            'model':self.preloadData['bottomModel'],
            'lighting':False,
            'colorTexture':self.preloadData['tex']})
        self.foo = bs.newNode('terrain', attrs={
            'model':self.preloadData['bgModel'],
            'lighting':False,
            'background':True,
            'colorTexture':self.preloadData['bgTex']})
        bs.newNode('terrain', attrs={
            'model':self.preloadData['vrFillMoundModel'],
            'lighting':False,
            'vrOnly':True,
            'color':(0.2,0.25,0.2),
            'background':True,
            'colorTexture':self.preloadData['vrFillMoundTex']})
        g = bs.getSharedObject('globals')
        g.happyThoughtsMode = True
        g.shadowOffset = (0.0, 8.0, 5.0)
        g.tint = (1.3, 1.23, 1.0)
        g.ambientColor = (1.3, 1.23, 1.0)
        g.vignetteOuter = (0.64, 0.59, 0.69)
        g.vignetteInner = (0.95, 0.95, 0.93)
        g.vrNearClip = 1.0
        self.isFlying = True

        # throw out some tips on flying
        t = bs.newNode('text', attrs={
            'text':bs.Lstr(resource='pressJumpToFlyText'),
            'scale':1.2,
            'maxWidth':800,
            'position':(0,200),
            'shadow':0.5,
            'flatness':0.5,
            'hAlign':'center',
            'vAttach':'bottom'})
        c = bs.newNode('combine', owner=t, attrs={
            'size':4,
            'input0':0.3,
            'input1':0.9,
            'input2':0.0})
        bsUtils.animate(c, 'input3', {3000:0, 4000:1, 9000:1, 10000:0})
        c.connectAttr('output', t, 'color')
        bs.gameTimer(10000, t.delete)
        
registerMap(AlwaysLandMap)

class StepRightUpMap(Map):
    import stepRightUpLevelDefs as defs
    name = 'Step Right Up'
    playTypes = ['melee', 'keepAway', 'teamFlag', 'conquest']

    @classmethod
    def getPreviewTextureName(cls):
        return 'stepRightUpPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('stepRightUpLevel')
        data['modelBottom'] = bs.getModel('stepRightUpLevelBottom')
        data['collideModel'] = bs.getCollideModel('stepRightUpLevelCollide')
        data['tex'] = bs.getTexture('stepRightUpLevelColor')
        data['bgTex'] = bs.getTexture('menuBG')
        # fixme should chop this into vr/non-vr chunks
        data['bgModel'] = bs.getModel('thePadBG')
        data['vrFillMoundModel'] = bs.getModel('stepRightUpVRFillMound')
        data['vrFillMoundTex'] = bs.getTexture('vrFillMound')
        return data
    
    def __init__(self):
        Map.__init__(self,vrOverlayCenterOffset=(0,-1,2))
        self.node = bs.newNode('terrain', delegate=self, attrs={
            'collideModel':self.preloadData['collideModel'],
            'model':self.preloadData['model'],
            'colorTexture':self.preloadData['tex'],
            'materials':[bs.getSharedObject('footingMaterial')]})
        self.nodeBottom = bs.newNode('terrain', delegate=self, attrs={
            'model':self.preloadData['modelBottom'],
            'lighting':False,
            'colorTexture':self.preloadData['tex']})
        bs.newNode('terrain', attrs={
            'model':self.preloadData['vrFillMoundModel'],
            'lighting':False,
            'vrOnly':True,
            'color':(0.53,0.57,0.5),
            'background':True,
            'colorTexture':self.preloadData['vrFillMoundTex']})
        self.bg = bs.newNode('terrain', attrs={
            'model':self.preloadData['bgModel'],
            'lighting':False,
            'background':True,
            'colorTexture':self.preloadData['bgTex']})
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.tint = (1.2, 1.1, 1.0)
        bsGlobals.ambientColor = (1.2, 1.1, 1.0)
        bsGlobals.vignetteOuter = (0.7, 0.65, 0.75)
        bsGlobals.vignetteInner = (0.95, 0.95, 0.93)

registerMap(StepRightUpMap)

class CourtyardMap(Map):
    import courtyardLevelDefs as defs
    name = 'Courtyard'
    playTypes = ['melee', 'keepAway', 'teamFlag']

    @classmethod
    def getPreviewTextureName(cls):
        return 'courtyardPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('courtyardLevel')
        data['modelBottom'] = bs.getModel('courtyardLevelBottom')
        data['collideModel'] = bs.getCollideModel('courtyardLevelCollide')
        data['tex'] = bs.getTexture('courtyardLevelColor')
        data['bgTex'] = bs.getTexture('menuBG')
        # fixme - chop this into vr and non-vr chunks
        data['bgModel'] = bs.getModel('thePadBG')
        data['playerWallCollideModel'] = \
            bs.getCollideModel('courtyardPlayerWall')
        data['playerWallMaterial'] = bs.Material()
        data['playerWallMaterial'].addActions(actions=(('modifyPartCollision',
                                                        'friction', 0.0)))
        # anything that needs to hit the wall should apply this.
        data['collideWithWallMaterial'] = bs.Material()
        data['playerWallMaterial'].addActions(
            conditions=('theyDontHaveMaterial',
                        data['collideWithWallMaterial']),
            actions=('modifyPartCollision', 'collide', False))
        data['vrFillMoundModel'] = bs.getModel('stepRightUpVRFillMound')
        data['vrFillMoundTex'] = bs.getTexture('vrFillMound')
        return data

    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain', delegate=self, attrs={
            'collideModel':self.preloadData['collideModel'],
            'model':self.preloadData['model'],
            'colorTexture':self.preloadData['tex'],
            'materials':[bs.getSharedObject('footingMaterial')]})
        self.bg = bs.newNode('terrain', attrs={
            'model':self.preloadData['bgModel'],
            'lighting':False,
            'background':True,
            'colorTexture':self.preloadData['bgTex']})
        self.bottom = bs.newNode('terrain', attrs={
            'model':self.preloadData['modelBottom'],
            'lighting':False,
            'colorTexture':self.preloadData['tex']})
        bs.newNode('terrain', attrs={
            'model':self.preloadData['vrFillMoundModel'],
            'lighting':False,
            'vrOnly':True,
            'color':(0.53,0.57,0.5),
            'background':True,
            'colorTexture':self.preloadData['vrFillMoundTex']})
        # in co-op mode games, put up a wall to prevent players
        # from getting in the turrets (that would foil our brilliant AI)
        if isinstance(bs.getSession(), bs.CoopSession):
            self.playerWall = bs.newNode('terrain', attrs={
                'collideModel':self.preloadData['playerWallCollideModel'],
                'affectBGDynamics':False,
                'materials':[self.preloadData['playerWallMaterial']]})
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.tint = (1.2, 1.17, 1.1)
        bsGlobals.ambientColor = (1.2, 1.17, 1.1)
        bsGlobals.vignetteOuter = (0.6, 0.6, 0.64)
        bsGlobals.vignetteInner = (0.95, 0.95, 0.93)

    def _isPointNearEdge(self, p, running=False):
        # count anything off our ground level as safe (for our platforms)
        # see if we're within edgeBox
        boxPosition = self.defs.boxes['edgeBox'][0:3]
        boxScale = self.defs.boxes['edgeBox'][6:9]
        x = (p.x() - boxPosition[0])/boxScale[0]
        z = (p.z() - boxPosition[2])/boxScale[2]
        return (x < -0.5 or x > 0.5 or z < -0.5 or z > 0.5)

registerMap(CourtyardMap)

class RampageMap(Map):
    import rampageLevelDefs as defs
    name = 'Rampage'
    playTypes = ['melee', 'keepAway', 'teamFlag']

    @classmethod
    def getPreviewTextureName(cls):
        return 'rampagePreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('rampageLevel')
        data['bottomModel'] = bs.getModel('rampageLevelBottom')
        data['collideModel'] = bs.getCollideModel('rampageLevelCollide')
        data['tex'] = bs.getTexture('rampageLevelColor')
        data['bgTex'] = bs.getTexture('rampageBGColor')
        data['bgTex2'] = bs.getTexture('rampageBGColor2')
        data['bgModel'] = bs.getModel('rampageBG')
        data['bgModel2'] = bs.getModel('rampageBG2')
        data['vrFillModel'] = bs.getModel('rampageVRFill')
        data['railingCollideModel'] = bs.getCollideModel('rampageBumper')
        return data
    
    def __init__(self):
        Map.__init__(self, vrOverlayCenterOffset=(0,0,2))
        self.node = bs.newNode('terrain', delegate=self, attrs={
            'collideModel':self.preloadData['collideModel'],
            'model':self.preloadData['model'],
            'colorTexture':self.preloadData['tex'],
            'materials':[bs.getSharedObject('footingMaterial')]})
        self.bg = bs.newNode('terrain', attrs={
            'model':self.preloadData['bgModel'],
            'lighting':False,
            'background':True,
            'colorTexture':self.preloadData['bgTex']})
        self.bottom = bs.newNode('terrain', attrs={
            'model':self.preloadData['bottomModel'],
            'lighting':False,
            'colorTexture':self.preloadData['tex']})
        self.bg2 = bs.newNode('terrain', attrs={
            'model':self.preloadData['bgModel2'],
            'lighting':False,
            'background':True,
            'colorTexture':self.preloadData['bgTex2']})
        bs.newNode('terrain', attrs={
            'model':self.preloadData['vrFillModel'],
            'lighting':False,
            'vrOnly':True,
            'background':True,
            'colorTexture':self.preloadData['bgTex2']})
        self.railing = bs.newNode('terrain', attrs={
            'collideModel':self.preloadData['railingCollideModel'],
            'materials':[bs.getSharedObject('railingMaterial')],
            'bumper':True})
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.tint = (1.2, 1.1, 0.97)
        bsGlobals.ambientColor = (1.3, 1.2, 1.03)
        bsGlobals.vignetteOuter = (0.62, 0.64, 0.69)
        bsGlobals.vignetteInner = (0.97, 0.95, 0.93)

    def _isPointNearEdge(self,p,running=False):
        boxPosition = self.defs.boxes['edgeBox'][0:3]
        boxScale = self.defs.boxes['edgeBox'][6:9]
        x = (p.x() - boxPosition[0])/boxScale[0]
        z = (p.z() - boxPosition[2])/boxScale[2]
        return (x < -0.5 or x > 0.5 or z < -0.5 or z > 0.5)

registerMap(RampageMap)