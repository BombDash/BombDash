# -*- coding: utf-8 -*-
import random
import bs
import bsGame
import bsSpaz
import bsUtils
import bsInternal
import bdUtils
import settings

class Commands(object):

    def __init__(self):
        self.tint = None
        self.all = settings.cmdForAll

    def checkPrivilege(self, privilege, nick):
        """ Check the player host or player privilege

        :param privilege: Privilege name to check
        :type privilege: str

        :param nick: Player nickname to check
        :type nick: str
        """
        data = bs.getConfig()['BombDash Privilege']

        # Doing a host check
        if privilege == 'device' and settings.cmdForMe:
            n = None
            s = nick

            for i in bsInternal._getForegroundHostActivity().players:
                if i.getName().encode('utf-8') == s:
                    n = i.getInputDevice()._getAccountName(False).encode('utf-8')

            return bsInternal._getAccountDisplayString(False).encode('utf-8') == n

        # Doing a admin check
        elif privilege == 'admin' and settings.cmdNew:
            for i in bsInternal._getForegroundHostActivity().players:
                if nick in i.getName().encode('utf-8'):
                    if i.get_account_id() in data['admins']:
                        return True

            return False

        # Doing a vip check
        elif privilege == 'vip' and settings.cmdNew:
            for i in bsInternal._getForegroundHostActivity().players:
                if nick in i.getName().encode('utf-8'):
                    if i.get_account_id() in data['vips']:
                        return True

            return False

    def handleCommand(self, nick, msg):
        """ Handle the command in the message text

        :param nick: Player nickname to check
        :type nick: str

        :param msg: Message text
        :type msg: str
        """
        admin = self.checkPrivilege('admin', nick)

        if (admin or self.checkPrivilege('vip', nick)
        	or self.checkPrivilege('device', nick) or self.all) \
                and bsInternal._getForegroundHostActivity().getName() != 'Boss Battle ':
            m = msg.split(' ')[0] # command
            a = msg.split(' ')[1:] # arguments
            activity = bsInternal._getForegroundHostActivity()

            with bs.Context(activity):
                if m == '/kick':
                    if not a:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='useKick').evaluate()
                            )
                    else:
                        try:
                            if int(a[0]) != -1:
                                bsInternal._disconnectClient(int(a[0]))
                            else:
                                bsInternal._chatMessage(
                                    bs.Lstr(resource='internal.cantKickHostError').evaluate()
                                    )
                        except:
                            bsInternal._chatMessage(
                                bs.Lstr(resource='errorText').evaluate()
                                )

                elif m in ['/list', '/l']:
                    bsInternal._chatMessage(
                        bs.Lstr(resource='forKick').evaluate()
                        )

                    for i in bsInternal._getGameRoster():
                        try:
                            bsInternal._chatMessage(
                                i['players'][0]['nameFull']+' (/kick '+str(i['clientID'])+')'
                                )
                        except:
                            pass

                    bsInternal._chatMessage('===================================')
                    bsInternal._chatMessage(
                        bs.Lstr(resource='forOtherCommands').evaluate()
                        )

                    for s in activity.players:
                        bsInternal._chatMessage(
                        	s.getName()+' - '+str(activity.players.index(s))
                            )

                elif m in ['/ooh', '/o']:
                    if a is not None and len(a) > 0:
                        s = int(a[0])
                        def oohRecurce(c):
                            bs.playSound(bs.getSound('ooh'), volume=2)
                            c -= 1
                            if c > 0:
                                bs.gameTimer(int(a[1]) if len(a) > 1 and a[1] is not None else 1000,
                                             bs.Call(oohRecurce, c=c))

                        oohRecurce(c=s)
                    else:
                        bs.playSound(bs.getSound('ooh'), volume=2)

                elif m in ['/playSound', '/ps']:
                    if a is not None and len(a) > 1:
                        s = int(a[1])
                        def oohRecurce(c):
                            bs.playSound(bs.getSound(str(a[0])), volume=2)
                            c -= 1
                            if c > 0:
                                bs.gameTimer(int(a[2]) if len(a) > 2 and a[2] is not None else 1000, 
                                             bs.Call(oohRecurce, c=c))

                        oohRecurce(c=s)
                    else:
                        bs.playSound(bs.getSound(str(a[0])), volume=2)

                elif m == '/quit':
                    if not admin and settings.cmdNew: return
                    bsInternal.quit()

                elif m == '/nv':
                    if self.tint is None:
                        self.tint = bs.getSharedObject('globals').tint

                    bs.getSharedObject('globals').tint = \
                        (0.5, 0.7, 1) if a == [] or not a[0] == u'off' else self.tint

                elif m == '/dv':
                    if self.tint is None:
                        self.tint = bs.getSharedObject('globals').tint

                    bs.getSharedObject('globals').tint = \
                        (1, 1, 1) if a == [] or not a[0] == u'off' else self.tint

                elif m == '/freeze':
                    if not admin and settings.cmdNew: return

                    if not a:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='useFreeze').evaluate()
                            )

                    elif a[0] == 'all':
                        for i in activity.players:
                            try:
                                i.actor.node.handleMessage(bs.FreezeMessage())
                            except:
                                pass

                    elif a[0] == 'device':
                        for i in activity.players:
                            if i.getInputDevice()._getAccountName(False).encode('utf-8') == a[1]:
                                try:
                                    i.actor.node.handleMessage(bs.FreezeMessage())
                                except:
                                    bsInternal._chatMessage(
                                        bs.Lstr(resource='useRemove').evaluate()
                                        )

                    else:
                        try:
                            activity.players[int(a[0])].actor.node.handleMessage(
                                bs.FreezeMessage()
                                )
                        except:
                            bsInternal._chatMessage(
                                bs.Lstr(resource='useRemove').evaluate()
                                )

                elif m == '/thaw':
                    if not a:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='useThaw').evaluate()
                            )

                    elif a[0] == 'all':
                        for i in activity.players:
                            try:
                                i.actor.node.handleMessage(bs.ThawMessage())
                            except:
                                pass

                    elif a[0] == 'device': 
                        for i in activity.players:
                            if i.getInputDevice()._getAccountName(False).encode('utf-8') == a[1]:
                                try:
                                    i.actor.node.handleMessage(bs.ThawMessage())
                                except:
                                    bsInternal._chatMessage(
                                        bs.Lstr(resource='useRemove').evaluate()
                                        )

                    else:
                        try:
                            activity.players[int(a[0])].actor.node.handleMessage(
                                bs.ThawMessage()
                                )
                        except:
                            bsInternal._chatMessage(
                                bs.Lstr(resource='useRemove').evaluate()
                                )

                elif m == '/kill':
                    if not admin and settings.cmdNew: return

                    if not a:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='useKill').evaluate()
                            )

                    elif a[0] == 'all':
                        for i in activity.players:
                            try:
                                i.actor.node.handleMessage(bs.DieMessage())
                            except:
                                pass

                    elif a[0] == 'device': 
                        for i in activity.players:
                            if i.getInputDevice()._getAccountName(False).encode('utf-8') == a[1]:
                                try:
                                    i.actor.node.handleMessage(bs.DieMessage())
                                except:
                                    bsInternal._chatMessage(
                                        bs.Lstr(resource='useRemove').evaluate()
                                        )

                    else:
                        try:
                            activity.players[int(a[0])].actor.node.handleMessage(
                                bs.DieMessage()
                                )
                        except:
                            bsInternal._chatMessage(
                                bs.Lstr(resource='useRemove').evaluate()
                                )

                elif m == '/curse':
                    if not admin and settings.cmdNew: return

                    if not a:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='useCurse').evaluate()
                            )

                    elif a[0] == 'all':
                        for i in activity.players:
                            try:
                                i.actor.curse()
                            except:
                                pass

                    elif a[0] == 'device': 
                        for i in activity.players:
                            if i.getInputDevice()._getAccountName(False).encode('utf-8') == a[1]:
                                try:
                                    i.actor.curse()
                                except:
                                    bsInternal._chatMessage(
                                        bs.Lstr(resource='useRemove').evaluate()
                                        )

                    else:
                        try:
                            activity.players[int(a[0])].actor.curse()
                        except:
                            bsInternal._chatMessage(
                                bs.Lstr(resource='useRemove').evaluate()
                                )

                elif m == '/box':
                    if not a:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='useBox').evaluate()
                            )

                    elif a[0] == 'all':
                        for i in activity.players:
                            try:
                                i.actor.node.torsoModel = bs.getModel('tnt')
                                i.actor.node.colorMaskTexture = bs.getTexture('tnt')
                                i.actor.node.colorTexture = bs.getTexture('tnt')
                                i.actor.node.highlight = (1, 1, 1)
                                i.actor.node.color = (1, 1, 1)
                                i.actor.node.headModel = None
                                i.actor.node.style = 'cyborg'
                            except:
                                pass

                    elif a[0] == 'device': 
                        for i in activity.players:
                            if i.getInputDevice()._getAccountName(False).encode('utf-8') == a[1]:
                                try:
                                    i.actor.node.torsoModel = bs.getModel('tnt')
                                    i.actor.node.colorMaskTexture = bs.getTexture('tnt')
                                    i.actor.node.colorTexture = bs.getTexture('tnt')
                                    i.actor.node.highlight = (1, 1, 1)
                                    i.actor.node.color = (1, 1, 1)
                                    i.actor.node.headModel = None
                                    i.actor.node.style = 'cyborg'
                                except:
                                    bsInternal._chatMessage(
                                        bs.Lstr(resource='errorText').evaluate()
                                        )

                    else:
                        try:
                            activity.players[int(a[0])].actor.node.torsoModel = bs.getModel('tnt')
                            activity.players[int(a[0])].actor.node.colorMaskTexture = bs.getTexture('tnt')
                            activity.players[int(a[0])].actor.node.colorTexture = bs.getTexture('tnt') 
                            activity.players[int(a[0])].actor.node.highlight = (1, 1, 1)
                            activity.players[int(a[0])].actor.node.color = (1, 1, 1)
                            activity.players[int(a[0])].actor.node.headModel = None
                            activity.players[int(a[0])].actor.node.style = 'cyborg'
                        except:
                            bsInternal._chatMessage(
                                bs.Lstr(resource='errorText').evaluate()
                                )

                elif m == '/remove':
                    if not a:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='useRemove').evaluate()
                            )

                    elif a[0] == 'all':
                        for i in activity.players:
                            try:
                                i.removeFromGame()
                            except:
                                pass

                    elif a[0] == 'device': 
                        for i in activity.players:
                            if i.getInputDevice()._getAccountName(False).encode('utf-8') == a[1]:
                                try:
                                    i.removeFromGame()
                                except:
                                    bsInternal._chatMessage(
                                        bs.Lstr(resource='errorText').evaluate()
                                        )

                    else:
                        try:
                            activity.players[int(a[0])].removeFromGame()
                        except:
                            bsInternal._chatMessage(
                                bs.Lstr(resource='errorText').evaluate()
                                )

                elif m == '/end':
                    try:
                        activity.endGame()
                    except:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='errorText').evaluate()
                            )

                elif m == '/hug':
                    if not a:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='useHug').evaluate()
                            )

                    elif a[0] == 'all':
                        try:
                            activity.players[0].actor.node.holdNode = \
                                activity.players[1].actor.node
                        except:
                            pass

                        try:
                            activity.players[1].actor.node.holdNode = \
                                activity.players[0].actor.node
                        except:
                            pass

                        try:
                            activity.players[2].actor.node.holdNode = \
                                activity.players[3].actor.node
                        except:
                            pass

                        try:
                            activity.players[3].actor.node.holdNode = \
                                activity.players[2].actor.node
                        except:
                            pass

                        try:
                            activity.players[4].actor.node.holdNode = \
                                activity.players[5].actor.node
                        except:
                            pass

                        try:
                            activity.players[5].actor.node.holdNode = \
                                activity.players[4].actor.node
                        except:
                            pass

                        try:
                            activity.players[6].actor.node.holdNode = \
                                activity.players[7].actor.node
                        except:
                            pass

                        try:
                            activity.players[7].actor.node.holdNode = \
                                activity.players[6].actor.node
                        except:
                            pass

                    else:
                        activity.players[int(a[0])].actor.node.holdNode = \
                            activity.players[int(a[1])].actor.node

                elif m == '/gm':
                    if not admin and settings.cmdNew: return

                    if not a:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='useGM').evaluate()
                            )

                    elif a[0] == 'all':
                        for i in activity.players:
                            try:
                                i.actor.node.hockey = \
                                    i.actor.node.hockey == False

                                i.actor.node.invincible = \
                                    i.actor.node.invincible == False

                                i.actor._punchPowerScale = 5 \
                                    if i.actor._punchPowerScale == 1.2 else 1.2
                            except:
                                pass

                    elif a[0] == 'device': 
                        for i in activity.players:
                            if i.getInputDevice()._getAccountName(False).encode('utf-8') == a[1]:
                                try:
                                    i.actor.node.hockey = \
                                        i.actor.node.hockey == False

                                    i.actor.node.invincible = \
                                        i.actor.node.invincible == False

                                    i.actor._punchPowerScale = 5 \
                                        if i.actor._punchPowerScale == 1.2 else 1.2
                                except:
                                    bsInternal._chatMessage(
                                        bs.Lstr(resource='errorText').evaluate()
                                        )

                    else:
                        try:
                            activity.players[int(a[0])].actor.node.hockey = \
                                activity.players[int(a[0])].actor.node.hockey == False

                            activity.players[int(a[0])].actor.node.invincible = \
                                activity.players[int(a[0])].actor.node.invincible == False

                            activity.players[int(a[0])].actor._punchPowerScale = 5 \
                                if activity.players[int(a[0])].actor._punchPowerScale == 1.2 else 1.2
                        except:
                            bsInternal._chatMessage(
                                bs.Lstr(resource='errorText').evaluate()
                                )

                elif m == '/tint':
                    if activity._map.getName() == 'Airlands':
                        bs.screenMessage(
                            bs.Lstr(resource='notnow'),
                            (1, 0.7, 0)
                            )

                        return

                    if not a:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='useTint').evaluate()
                            )
                    else:
                        if a[0] == 'r':
                            m = 1.3 if a[1] is None else float(a[1])
                            s = 1000 if a[2] is None else float(a[2])
                            bs.animateArray(bs.getSharedObject('globals'), 'tint', 3,
                                {0: (1*m, 0, 0), s: (0, 1*m, 0),
                                s*2: (0, 0, 1*m), s*3: (1*m, 0, 0)}, True
                                )
                        else:
                            try:
                                bs.getSharedObject('globals').tint = (float(a[0]),
                                                                      float(a[1]),
                                                                      float(a[2]))
                            except:
                                bsInternal._chatMessage(
                                    bs.Lstr(resource='errorText').evaluate()
                                    )

                elif m == '/pause':
                    if not admin and settings.cmdNew: return

                    bs.getSharedObject('globals').paused = \
                        bs.getSharedObject('globals').paused == False

                elif m == '/sm':
                    bs.getSharedObject('globals').slowMotion = \
                        bs.getSharedObject('globals').slowMotion == False

                elif m == '/bot':
                    if not admin and settings.cmdNew: return

                    if not a:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='useBot').evaluate()
                            )
                    else:
                        for i in xrange(int(a[0])):
                            p = bs.getSession().players[int(a[1])]
                            if not 'bunnies' in p.gameData:
                                p.gameData['bunnies'] = BuddyBunny.BunnyBotSet(p)

                            p.gameData['bunnies'].doBunny()

                elif m in ['/cameraMode', '/cam']:
                    if not admin and settings.cmdNew: return

                    try:
                        if bs.getSharedObject('globals').cameraMode == 'follow':
                            bs.getSharedObject('globals').cameraMode = 'rotate'
                        else:
                            bs.getSharedObject('globals').cameraMode = 'follow'
                    except:
                        pass

                elif m == '/lm':
                    arr = []
                    for i in xrange(100):
                        try:
                            arr.append(bsInternal._getChatMessages()[-1-i])
                        except:
                            pass

                    arr.reverse()
                    for i in arr:
                        bsInternal._chatMessage(i)

                elif m == '/gp':
                    if not a:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='useGP').evaluate()
                            )
                    else:
                        s = bsInternal._getForegroundHostSession()
                        for i in s.players[int(a[0])].getInputDevice()._getPlayerProfiles():
                            try:
                                if i.encode('utf-8') == '__account__':
                                    i = s.players[int(a[0])].getInputDevice()._getAccountName(False)

                                bsInternal._chatMessage(i)
                            except:
                                bsInternal._chatMessage(
                                    bs.Lstr(resource='errorText').evaluate()
                                    )

                elif m == '/icy':
                    if not admin and settings.cmdNew: return

                    if not a:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='useIcy').evaluate()
                            )

                    elif len(a) == 2:
                        try:
                            activity.players[int(a[0])].actor.node = \
                                activity.players[int(a[1])].actor.node

                            activity.players[int(a[1])].actor.node = \
                                activity.players[int(a[0])].actor.node
                        except:
                            bsInternal._chatMessage(
                                bs.Lstr(resource='errorText').evaluate()
                                )

                    else:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='useIcy').evaluate()
                            )

                elif m == '/fly':
                    if not a:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='useFly').evaluate()
                            )

                    elif a[0] == 'all':
                        for i in activity.players:
                            try:
                                i.actor.node.fly = True
                            except:
                                pass

                    elif a[0] == 'device':
                        for i in activity.players:
                            if i.getInputDevice()._getAccountName(False).encode('utf-8') == a[1]:
                                try:
                                    i.actor.node.fly = True
                                except:
                                    bsInternal._chatMessage(
                                        bs.Lstr(resource='errorText').evaluate()
                                        )

                    else:
                        try:
                            activity.players[int(a[0])].actor.node.fly = \
                                activity.players[int(a[0])].actor.node.fly == False
                        except:
                            bsInternal._chatMessage(
                                bs.Lstr(resource='errorText').evaluate()
                                )

                elif m == '/fly3d':
                    if not a:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='useFly3d').evaluate()
                            )

                    elif a[0] == 'all':
                        for i in activity.players:
                            try:
                                bsSpaz.NewFly(i)
                            except:
                                pass

                    elif a[0] == 'device':
                        for i in activity.players:
                            if i.getInputDevice()._getAccountName(False).encode('utf-8') == a[1]:
                                try:
                                    bsSpaz.NewFly(i)
                                except:
                                    bsInternal._chatMessage(
                                        bs.Lstr(resource='errorText').evaluate()
                                        )

                    else:
                        try:
                            bsSpaz.NewFly(activity.players[int(a[0])])
                        except:
                            bsInternal._chatMessage(
                                bs.Lstr(resource='errorText').evaluate()
                                )
                elif m in ['/floorReflection', '/fref']:
                    bs.getSharedObject('globals').floorReflection = \
                        bs.getSharedObject('globals').floorReflection == False

                elif m == '/ac':
                    if not a:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='useAC').evaluate()
                            )
                    else:
                        if a[0] == 'r':
                            m = 1.3 if a[1] is None else float(a[1])
                            s = 1000 if a[2] is None else float(a[2])
                            bs.animateArray(
                                bs.getSharedObject('globals'), 'ambientColor', 3,
                                {0: (1*m, 0, 0), s: (0, 1*m, 0),
                                s*2: (0, 0, 1*m), s*3: (1*m, 0, 0)}, True
                                )
                        else:
                            try:
                                bs.getSharedObject('globals').ambientColor = (float(a[0]),
                                                                              float(a[1]),
                                                                              float(a[2]))
                            except:
                                bsInternal._chatMessage(
                                    bs.Lstr(resource='errorText').evaluate()
                                    )

                elif m == ['/iceOff', '/io']:
                    try:
                        activity.getMap().node.materials = [bs.getSharedObject('footingMaterial')]
                        activity.getMap().isHockey = False
                    except:
                        pass

                    try:
                        activity.getMap().floor.materials = [bs.getSharedObject('footingMaterial')]
                        activity.getMap().isHockey = False
                    except:
                        pass

                    for i in activity.players:
                        i.actor.node.hockey = False

                elif m in ['/maxPlayers', '/mp']:
                    if not admin and settings.cmdNew: return

                    if not a:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='useMP').evaluate()
                            )
                    else:
                        try:
                            bsInternal._getForegroundHostSession()._maxPlayers = int(a[0])
                            bsInternal._setPublicPartyMaxSize(int(a[0]))
                            bsInternal._chatMessage('Players limit set to '+str(int(a[0])))
                        except:
                            bsInternal._chatMessage(
                                bs.Lstr(resource='errorText').evaluate()
                                )

                elif m == '/heal':
                    if not a:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='useHeal').evaluate()
                            )

                    elif a[0] == 'device': 
                        for i in activity.players:
                            if i.getInputDevice()._getAccountName(False).encode('utf-8') == a[1]:
                                try:
                                    i.actor.node.handleMessage(
                                        bs.PowerupMessage(powerupType='health')
                                        )
                                except:
                                    bsInternal._chatMessage(
                                        bs.Lstr(resource='errorText').evaluate()
                                        )

                    else:
                        try:
                            activity.players[int(a[0])].actor.node.handleMessage(
                                bs.PowerupMessage(powerupType='health')
                                )
                        except:
                            bsInternal._chatMessage(
                                bs.Lstr(resource='errorText').evaluate()
                                )

                elif m in ['/reflections', '/ref']:
                    if a == [] or len(a) < 2:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='useRef').evaluate()
                            )

                    rs = [int(a[1])]
                    type = 'soft' if int(a[0]) == 0 else 'powerup'
                    try:
                        activity.getMap().node.reflection = type
                        activity.getMap().node.reflectionScale = rs
                    except:
                        pass

                    try:
                        activity.getMap().bg.reflection = type
                        activity.getMap().bg.reflectionScale = rs
                    except:
                        pass

                    try:
                        activity.getMap().floor.reflection = type
                        activity.getMap().floor.reflectionScale = rs
                    except:
                        pass

                    try:
                        activity.getMap().center.reflection = type
                        activity.getMap().center.reflectionScale = rs
                    except:
                        pass

                elif m == '/shatter':
                    if not a:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='useShatter').evaluate()
                            )

                    elif a[0] == 'all':
                        for i in activity.players:
                            i.actor.node.shattered = int(a[1])

                    else:
                        activity.players[int(a[0])].actor.node.shattered = int(a[1])

                elif m == '/cm':
                    if not a:
                        time = 8000
                    else:
                        time = int(a[0])
                        op = 0.08
                        bsInternal._getForegroundHostSession().narkomode = True
                        std = bs.getSharedObject('globals').vignetteOuter
                        bs.animateArray(
                            bs.getSharedObject('globals'), 'vignetteOuter', 3,
                            {0: bs.getSharedObject('globals').vignetteOuter, 17000: (0, 1, 0)}
                            )
                        
                    try:
                        activity.getMap().node.opacity = op
                    except:
                        pass

                    try:
                        activity.getMap().bg.opacity = op
                    except:
                        pass

                    try:
                        activity.getMap().bg.node.opacity = op
                    except:
                        pass

                    try:
                        activity.getMap().node1.opacity = op
                    except:
                        pass

                    try:
                        activity.getMap().node2.opacity = op
                    except:
                        pass

                    try:
                        activity.getMap().node3.opacity = op
                    except:
                        pass

                    try:
                        activity.getMap().steps.opacity = op
                    except:
                        pass

                    try:
                        activity.getMap().floor.opacity = op
                    except:
                        pass

                    try:
                        activity.getMap().node4.opacity = op
                    except:
                        pass

                    try:
                        activity.getMap().center.opacity = op
                    except:
                        pass
                        
                    def off():
                        op = 1
                        bsInternal._getForegroundHostSession().narkomode = False
                        try:
                            activity.getMap().node.opacity = op
                        except:
                            pass

                        try:
                            activity.getMap().bg.opacity = op
                        except:
                            pass

                        try:
                            activity.getMap().bg.node.opacity = op
                        except:
                            pass

                        try:
                            activity.getMap().node1.opacity = op
                        except:
                            pass

                        try:
                            activity.getMap().node2.opacity = op
                        except:
                            pass

                        try:
                            activity.getMap().node3.opacity = op
                        except:
                            pass

                        try:
                            activity.getMap().node4.opacity = op
                        except:
                            pass

                        try:
                            activity.getMap().steps.opacity = op
                        except:
                            pass

                        try:
                            activity.getMap().floor.opacity = op
                        except:
                            pass

                        try:
                            activity.getMap().center.opacity = op
                        except:
                            pass

                        bs.animateArray(
                            bs.getSharedObject('globals'), 'vignetteOuter', 3,
                            {0: bs.getSharedObject('globals').vignetteOuter, 100: std}
                            )

                    bs.gameTimer(time, bs.Call(off))

                elif m == '/rise':
                    if not admin and settings.cmdNew: return

                    if not a:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='useRise').evaluate()
                            )

                    elif a[0] == 'all':
                        for i in activity.players:
                            activity.spawnPlayer(i)

                    elif a[0] == 'device': 
                        for i in activity.players:
                            if i.getInputDevice()._getAccountName(False).encode('utf-8') == a[1]:
                                activity.spawnPlayer(i)

                    else:
                        activity.spawnPlayer(activity.players[int(a[0])])

                elif m == '/ban':
                    if not admin and settings.cmdNew: return

                    try:
                        if not a:
                            bsInternal._chatMessage(
                                bs.Lstr(resource='useBan').evaluate()
                                )

                        elif len(a) == 1:
                            s = activity.players[int(a[0])]
                            name = s.get_account_id()
                            s.removeFromGame()

                            bs.getConfig()['BombDash Privilege']['bans'].append(name)
                            bs.writeConfig()

                        else:
                            bsInternal._chatMessage(
                                bs.Lstr(resource='useBan').evaluate()
                                )
                    except:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='errorText').evaluate()
                            )

                elif m == '/vip':
                    if not admin and settings.cmdNew: return

                    try:
                        if not a:
                            bsInternal._chatMessage(
                                bs.Lstr(resource='useVIP').evaluate()
                                )

                        elif len(a) == 1:
                            s = activity.players[int(a[0])]
                            name = s.get_account_id()
                            s.removeFromGame()

                            bs.getConfig()['BombDash Privilege']['vips'].append(name)
                            bs.writeConfig()

                        else:
                            bsInternal._chatMessage(
                                bs.Lstr(resource='useAdmin').evaluate()
                                )
                    except:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='errorVIP').evaluate()
                            )

                elif m == '/admin':
                    if not admin and settings.cmdNew: return

                    try:
                        if not a:
                            bsInternal._chatMessage(
                                bs.Lstr(resource='useAdmin').evaluate()
                                )

                        elif len(a) == 1:
                            s = activity.players[int(a[0])]
                            name = s.get_account_id()
                            s.removeFromGame()

                            bs.getConfig()['BombDash Privilege']['admins'].append(name)
                            bs.writeConfig()

                        else:
                            bsInternal._chatMessage(
                                bs.Lstr(resource='useAdmin').evaluate()
                                )
                    except:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='errorText').evaluate()
                            )

                elif m == '/tnt':
                    if not admin and settings.cmdNew: return

                    if not a:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='useTNT').evaluate()
                            )

                    elif a[2] == 'myPos':
                        try:
                            for i in activity.players:
                                if nick == i.getName().encode('utf-8'):
                                    pos = i.actor.node.position
                                    bs.Bomb(
                                        bombType='tnt',
                                        position=pos
                                        ).autoRetain()
                        except:
                            bsInternal._chatMessage(
                                bs.Lstr(resource='errorText').evaluate()
                                )

                    elif len(a) == 3:
                        try:
                            bs.Bomb(
                                bombType='tnt',
                                position=(float(a[0]),
                                          float(a[1]),
                                          float(a[2]))
                                ).autoRetain()
                        except:
                            bsInternal._chatMessage(
                                bs.Lstr(resource='errorText').evaluate()
                                )

                    else:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='useTNT').evaluate()
                            )


                elif m == '/bomb':
                    if not admin and settings.cmdNew: return

                    if not a:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='useBomb').evaluate()
                            )

                    elif a[0] == 'names':
                        bsInternal._chatMessage(
                            bs.Lstr(resource='bombNames').evaluate()+":"
                            )

                        for i in xrange(1, 13):
                            bsInternal._chatMessage(
                                bs.Lstr(resource='bombName'+str(i)).evaluate()
                                )

                        bsInternal._chatMessage('===================================')

                    elif a[2] == 'myPos':
                        try:
                            for i in activity.players:
                                if nick == i.getName().encode('utf-8'):
                                    pos = i.actor.node.position
                                    bs.Bomb(
                                        bombType=str(a[0]),
                                        blastRadius=float(a[1]),
                                        position=pos
                                        ).autoRetain()
                        except:
                            bsInternal._chatMessage(
                                bs.Lstr(resource='errorText').evaluate()
                                )

                    elif len(a) == 5:
                        try:
                            bs.Bomb(
                                bombType=str(a[0]),
                                blastRadius=float(a[1]),
                                position=(float(a[2]),
                                          float(a[3]),
                                          float(a[4]))
                                ).autoRetain()
                        except:
                            bsInternal._chatMessage(
                                bs.Lstr(resource='errorText').evaluate()
                                )

                    else:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='useBomb').evaluate()
                            )

                elif m == '/blast':
                    if not admin and settings.cmdNew: return

                    if not a:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='useBlast').evaluate()
                            )

                    elif a[1] == 'myPos':
                        try:
                            for i in activity.players:
                                if nick == i.getName().encode('utf-8'):
                                    pos = i.actor.node.position
                                    bs.Blast(
                                        blastRadius=float(a[0]),
                                        position=pos
                                        ).autoRetain()
                        except:
                            bsInternal._chatMessage(
                                bs.Lstr(resource='errorText').evaluate()
                                )

                    elif len(a) == 4:
                        try:
                            bs.Blast(
                                blastRadius=float(a[0]),
                                position=(float(a[1]),
                                          float(a[2]),
                                          float(a[3]))
                                ).autoRetain()
                        except:
                            bsInternal._chatMessage(
                                bs.Lstr(resource='errorText').evaluate()
                                )

                    else:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='useBlast').evaluate()
                            )

                elif m == '/powerup':
                    if not admin and settings.cmdNew: return

                    if not a:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='usePowerup').evaluate()
                            )

                    elif a[0] == 'names':
                        bsInternal._chatMessage(
                            bs.Lstr(resource='powerupNames'
                            ).evaluate()+':')

                        for i in xrange(1, 21):
                            bsInternal._chatMessage(
                                bs.Lstr(resource='powerupName'+str(i)).evaluate()
                                )

                        bsInternal._chatMessage('===================================')

                    elif a[1] == 'myPos':
                        try:
                            for i in activity.players:
                                if nick == i.getName().encode('utf-8'):
                                    pos = i.actor.node.position
                                    bs.Powerup(
                                        powerupType=str(a[0]),
                                        position=pos
                                        ).autoRetain()
                        except:
                            bsInternal._chatMessage(
                                bs.Lstr(resource='errorText').evaluate()
                                )

                    elif len(a) == 4:
                        try:
                            bs.Powerup(
                                powerupType=str(a[0]),
                                position=(float(a[1]),
                                          float(a[2]),
                                          float(a[3]))
                                ).autoRetain()
                        except:
                            bsInternal._chatMessage(
                                bs.Lstr(resource='errorText').evaluate()
                                )

                    else:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='usePowerup').evaluate()
                            )

                elif m == '/sleep':
                    if not a:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='useSleep').evaluate()
                            )

                    elif a[0] == 'all':
                        for i in activity.players:
                            try:
                                i.actor.node.handleMessage('knockout', 5000)
                            except:
                                pass

                    elif a[0] == 'device': 
                        for i in activity.players:
                            if i.getInputDevice()._getAccountName(False).encode('utf-8') == a[1]:
                                try:
                                    i.actor.node.handleMessage('knockout', 5000)
                                except:
                                    bsInternal._chatMessage(
                                        bs.Lstr(resource='errorText').evaluate()
                                        )

                    else:
                        try:
                            activity.players[int(a[0])].actor.node.handleMessage(
                                'knockout', 5000
                                )
                        except:
                            bsInternal._chatMessage(
                                bs.Lstr(resource='errorText').evaluate()
                                )

                elif m == '/inv':
                    if not admin and settings.cmdNew: return

                    if not a:
                        bsInternal._chatMessage(
                        	bs.Lstr(resource='useInv').evaluate()
                            )
                    else:
                        try:
                            if a[0] == 'all':
                                for i in bs.getSession().players:
                                    i.actor.node.name = ''
                                    i.actor.node.colorTexture = None
                                    i.actor.node.colorMaskTexture = None
                                    i.actor.node.headModel = None
                                    i.actor.node.torsoModel = None
                                    i.actor.node.pelvisModel = None
                                    i.actor.node.upperArmModel = None
                                    i.actor.node.foreArmModel = None
                                    i.actor.node.handModel = None
                                    i.actor.node.upperLegModel = None
                                    i.actor.node.lowerLegModel = None
                                    i.actor.node.toesModel = None
                                    i.actor.node.style = 'cyborg'

                            elif a[0] == 'device':
                                for i in bsInternal._getForegroundHostSession().players:
                                    if i.getInputDevice()._getAccountName(False).encode('utf-8') == a[1]:
                                        i.actor.node.name = ''
                                        i.actor.node.colorTexture = None
                                        i.actor.node.colorMaskTexture = None
                                        i.actor.node.headModel = None
                                        i.actor.node.torsoModel = None
                                        i.actor.node.pelvisModel = None
                                        i.actor.node.upperArmModel = None
                                        i.actor.node.foreArmModel = None
                                        i.actor.node.handModel = None
                                        i.actor.node.upperLegModel = None
                                        i.actor.node.lowerLegModel = None
                                        i.actor.node.toesModel = None
                                        i.actor.node.style = 'cyborg'

                            else:
                                n = int(a[0])
                                t = bs.getSession().players[n].actor.node

                                t.name = ''
                                t.colorTexture = None
                                t.colorMaskTexture = None
                                t.headModel = None
                                t.torsoModel = None
                                t.pelvisModel = None
                                t.upperArmModel = None
                                t.foreArmModel = None
                                t.handModel = None
                                t.upperLegModel = None
                                t.lowerLegModel = None
                                t.toesModel = None
                                t.style = 'cyborg'
                        except:
                            bsInternal._chatMessage(
                                bs.Lstr(resource='errorText').evaluate()
                                )

                elif m == '/rainbow':
                    if not a:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='useRainbow').evaluate()
                            )

                    elif a[0] == 'all':
                        for i in activity.players:
                            try:
                                bs.animateArray(i.actor.node, 'color', 3,
                                    {0: (0, 0, 3), 500: (0, 3, 0),
                                    1000: (3, 0, 0), 1500: (0, 0, 3)}, True
                                    )

                                bs.animateArray(i.actor.node, 'highlight', 3,
                                    {0: (3, 0, 0), 500: (0, 0, 0),
                                    1000: (0, 0, 3), 1500: (3, 0, 0)}, True
                                    )

                                i.actor.node.handleMessage('celebrate', 100000000)
                            except:
                                pass

                    elif a[0] == 'device': 
                        for i in activity.players:
                            if i.getInputDevice()._getAccountName(False).encode('utf-8') == a[1]:
                                try:
                                    bs.animateArray(i.actor.node, 'color', 3,
                                        {0: (0, 0, 3), 500: (0, 3, 0),
                                        1000: (3, 0, 0), 1500: (0, 0, 3)}, True
                                        )

                                    bs.animateArray(i.actor.node, 'highlight', 3,
                                        {0: (3, 0, 0), 500: (0, 0, 0),
                                        1000: (0, 0, 3), 1500: (3, 0, 0)}, True
                                        )

                                    i.actor.node.handleMessage('celebrate', 100000000)
                                except:
                                    bsInternal._chatMessage(
                                        bs.Lstr(resource='errorText').evaluate()
                                        )

                    else:
                        try:
                            bs.animateArray(activity.players[int(a[0])].actor.node, 'color', 3,
                                {0: (0, 0, 3), 500: (0, 3, 0),
                                1000: (3, 0, 0), 1500: (0, 0, 3)}, True
                                )

                            bs.animateArray(activity.players[int(a[0])].actor.node, 'highlight', 3,
                                {0: (3, 0, 0), 500: (0, 0, 0),
                                1000: (0, 0, 3), 1500: (3, 0, 0)}, True
                                )

                            activity.players[int(a[0])].actor.node.handleMessage(
                                'celebrate', 100000000
                                )
                        except:
                            bsInternal._chatMessage(
                                bs.Lstr(resource='errorText').evaluate()
                                )

                elif m == '/nuke':
                    bs.playSound(bs.getSound('nukeAlarm'))
                    def nuke():
                        bs.Nuke(
                            position=(self.node.position[0],
                                      10,
                                      self.node.position[2])
                            ).autoRetain()

                    bs.gameTimer(11500, bs.Nuke)
                    bs.screenMessage(
                        bs.Lstr(resource='nukeArrive').evaluate()
                        )

                elif m == '/help':
                    if not a:
                        bsInternal._chatMessage(
                            bs.Lstr(resource='useHelp').evaluate()
                            )

                    elif a[0] == '1':
                        bsInternal._chatMessage(
                            bs.Lstr(resource='helpPage1').evaluate()
                            )

                        for i in xrange(1, 15):
                            bsInternal._chatMessage(
                                bs.Lstr(resource='help'+str(i)).evaluate()
                                )

                        bsInternal._chatMessage('=====================================')

                    elif a[0] == '2':
                        bsInternal._chatMessage(
                            bs.Lstr(resource='helpPage2').evaluate()
                            )

                        for i in xrange(15, 29):
                            bsInternal._chatMessage(
                                bs.Lstr(resource='help'+str(i)).evaluate()
                                )

                        bsInternal._chatMessage('=====================================')

                    elif a[0] == '3':
                        if settings.cmdNew:
                            if admin:
                                bsInternal._chatMessage(
                                    bs.Lstr(resource='helpPage3').evaluate()
                                    )

                                for i in xrange(29, 48):
                                    bsInternal._chatMessage(
                                        bs.Lstr(resource='help'+str(i)).evaluate()
                                        )

                                bsInternal._chatMessage('=====================================')
                            else:
                                bsInternal._chatMessage(
                                    bs.Lstr(resource='helpOnlyAdmins').evaluate()
                                    )
                        else:
                            bsInternal._chatMessage(
                                bs.Lstr(resource='helpPage3').evaluate()
                                )

                            for i in xrange(29, 48):
                                bsInternal._chatMessage(
                                    bs.Lstr(resource='help'+str(i)).evaluate()
                                    )

                            bsInternal._chatMessage('=====================================')

        elif bsInternal._getForegroundHostActivity().getName() == 'Boss Battle ':
            bs.screenMessage(
                bs.Lstr(resource='notnow'),
                (1, 0.7, 0)
                )

c = Commands()

def chatOptions(msg):
    if bsInternal._getForegroundHostActivity() is not None:
        n = msg.split(': ')
        c.handleCommand(n[0], n[1])

bs.realTimer(
    5000,
    bs.Call(
        bsInternal._setPartyIconAlwaysVisible,
        True
        )
    )