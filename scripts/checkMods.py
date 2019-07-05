import os
import json
import urllib2
import threading
import bs
import bsUtils
import bsInternal

def start():
    print bs.Lstr(resource='checkMods').evaluate()
    if bsInternal._havePermission('storage'):
        if os.path.exists(bs.getEnvironment()['userScriptsDirectory']+'/snowyPowerup.py'):
            bs.screenMessage(
                bs.Lstr(
                    resource='scriptWasFound',
                    subs=[('${NAME}', '"snowyPowerup.py"')]),
                (1, 1, 0)
                )

            try:
                os.remove(bs.getEnvironment()['systemScriptsDirectory']+'/snowyPowerup.py')
                os.remove(bs.getEnvironment()['systemScriptsDirectory']+'/snowyPowerup.pyc')
                bs.screenMessage(
                    bs.Lstr(resource='needsRestart'),
                    (1, 1, 0)
                    )
            except:
                bs.screenMessage(
                    bs.Lstr(resource='magicError'),
                    (1, 0, 0)
                    )
        else:
            print bs.Lstr(
                resource='scriptNotFound',
                subs=[('${NAME}', '"snowyPowerup.py"')]
                ).evaluate()

        if os.path.exists(bs.getEnvironment()['systemScriptsDirectory']+'/settings_patcher.py'):
            bs.screenMessage(
                bs.Lstr(
                    resource='scriptWasFound',
                    subs=[('${NAME}', '"settings_patcher.py"')]),
                (1, 1, 0)
                )

            try:
                os.remove(bs.getEnvironment()['systemScriptsDirectory']+'/settings_patcher.py')
                os.remove(bs.getEnvironment()['systemScriptsDirectory']+'/settings_patcher.pyc')
                bs.screenMessage(
                    bs.Lstr(resource='needsRestart'),
                    (1, 1, 0)
                    )
            except:
                bs.screenMessage(
                    bs.Lstr(resource='magicError'),
                    (1, 0, 0)
                    )
        else:
            print bs.Lstr(
                resource='scriptNotFound',
                subs=[('${NAME}', '"settings_patcher.py"')]
                ).evaluate()

        if os.path.exists(bs.getEnvironment()['systemScriptsDirectory']+'/modManager.py'):
            bs.screenMessage(
                bs.Lstr(
                    resource='scriptWasFound',
                    subs=[('${NAME}', '"modManager.py"')]),
                (1, 1, 0)
                )

            try:
                os.remove(bs.getEnvironment()['systemScriptsDirectory']+'/modManager.py')
                os.remove(bs.getEnvironment()['systemScriptsDirectory']+'/modManager.pyc')
                bs.screenMessage(
                    bs.Lstr(resource='needsRestart'),
                    (1, 1, 0)
                    )
            except:
                bs.screenMessage(
                    bs.Lstr(resource='magicError'),
                    (1, 0, 0)
                    )
        else:
            print bs.Lstr(
                resource='scriptNotFound',
                subs=[('${NAME}', '"modManager.py"')]
                ).evaluate()
    else:
        print bs.Lstr(resource='storagePermissionAccessText').evaluate() + '!'

    print bs.Lstr(resource='complete').evaluate()

bs.realTimer(5000, start)