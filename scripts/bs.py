"""
This module is the public face of BombSquad. For most modding purposes,
the functionality exposed here is all you should need.
"""

# pull in our 'public' stuff
from bsInternal import *
from bsUtils import GetThemeValues, getLanguage, writeConfig, openURL, WeakCall, Call, \
    animate, animateArray, Lstr, uni, utf8, playMusic, PopupText, getConfig, \
    getNormalizedColor, isPointInBox, getTimeString, printError, \
    printErrorOnce, printException, getSharedObject, isBrowserLikelyAvailable, \
    OnScreenTimer, OnScreenCountdown, addStats
from bsGame import Team, OutOfBoundsMessage, DieMessage, StandMessage, \
    PickUpMessage, DropMessage, PickedUpMessage, DroppedMessage, \
    ShouldShatterMessage, ImpactDamageMessage, FreezeMessage, ThawMessage, \
    HitMessage, Actor, NodeActor, Session, Activity, GameActivity
from bsCoopGame import CoopSession, CoopGameActivity, Level
from bsTeamGame import TeamBaseSession, FreeForAllSession, TeamsSession, \
    TeamGameActivity, TeamGameResults
from bsBomb import Bomb, TNTSpawner, BombFactory, Blast
from bsPowerup import Powerup, PowerupMessage, PowerupAcceptMessage, \
    PowerupFactory
from bsMap import Map, getMapsSupportingPlayType
from bdUtils import *
from bsFlag import FlagFactory, Flag, FlagPickedUpMessage, FlagDeathMessage, \
    FlagDroppedMessage
from bsScoreBoard import ScoreBoard
from bsScoreSet import PlayerScoredMessage
from bsSpaz import *
from bsVector import Vector

# change everything's listed module to ours
import bs
for obj in [getattr(bs, attr) for attr in dir(bs) if not attr.startswith('_')]:
    if getattr(obj, '__module__', None) not in [None, 'bs']:
        obj.__module__ = 'bs'
del bs
del obj
del attr