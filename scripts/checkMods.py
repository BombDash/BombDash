import os
import json
import urllib2
import threading
import bs
import bsUtils
import bsInternal


def start():
    path = bs.getEnvironment()['userScriptsDirectory']
    print bs.Lstr(resource='checkMods').evaluate()
    if bsInternal._havePermission('storage'):
        if os.path.exists(path+'/snowyPowerup.py'):
            bs.screenMessage(
                bs.Lstr(
                    resource='scriptWasFound',
                    subs=[('${NAME}', '"snowyPowerup.py"')]),
                (1, 1, 0))

            try:
                os.remove(path+'/snowyPowerup.py')
                os.remove(path+'/snowyPowerup.pyc')
                bs.screenMessage(
                    bs.Lstr(resource='needsRestart'),
                    (1, 1, 0))
            except:
                bs.screenMessage(
                    bs.Lstr(resource='errorText'),
                    (1, 0, 0))
        else:
            print bs.Lstr(
                resource='scriptNotFound',
                subs=[('${NAME}', '"snowyPowerup.py"')]).evaluate()

        if os.path.exists(path+'/settings_patcher.py'):
            bs.screenMessage(
                bs.Lstr(
                    resource='scriptWasFound',
                    subs=[('${NAME}', '"settings_patcher.py"')]),
                (1, 1, 0))

            try:
                os.remove(path+'/settings_patcher.py')
                os.remove(path+'/settings_patcher.pyc')
                bs.screenMessage(
                    bs.Lstr(resource='needsRestart'),
                    (1, 1, 0))
            except:
                bs.screenMessage(
                    bs.Lstr(resource='errorText'),
                    (1, 0, 0))
        else:
            print bs.Lstr(
                resource='scriptNotFound',
                subs=[('${NAME}', '"settings_patcher.py"')]).evaluate()

        if os.path.exists(path+'/modManager.py'):
            bs.screenMessage(
                bs.Lstr(
                    resource='scriptWasFound',
                    subs=[('${NAME}', '"modManager.py"')]),
                (1, 1, 0))

            try:
                os.remove(path+'/modManager.py')
                os.remove(path+'/modManager.pyc')
                bs.screenMessage(
                    bs.Lstr(resource='needsRestart'),
                    (1, 1, 0))
            except:
                bs.screenMessage(
                    bs.Lstr(resource='errorText'),
                    (1, 0, 0))
        else:
            print bs.Lstr(
                resource='scriptNotFound',
                subs=[('${NAME}', '"modManager.py"')]).evaluate()
    else:
        print bs.Lstr(resource='storagePermissionAccessText').evaluate() + '!'

    print bs.Lstr(resource='complete').evaluate()


bs.realTimer(5000, start)
