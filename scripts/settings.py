scenes = [1, 2, 3, 5, 7, 8, 9, 10, 11, 12, 13]
fair = False
bolt = False
badWords = False
puppeteer = False
cmdForAll = False
cmdForMe = True
cmdNew = False
halloweenScene = False
duck = False
showServerData = False
writeServerData = False
agreement = False
forcedUI = 0
theme = 'Default'


def saveSettings():
    import bs
    with open(bs.getEnvironment()[
            'systemScriptsDirectory']+'/settings.py') as file:
        s = [row for row in file]
        s[0] = 'scenes = ' + str(scenes) + '\n'
        s[1] = 'fair = ' + str(fair) + '\n'
        s[2] = 'bolt = ' + str(bolt) + '\n'
        s[3] = 'badWords = ' + str(badWords) + '\n'
        s[4] = 'puppeteer = ' + str(puppeteer) + '\n'
        s[5] = 'cmdForAll = ' + str(cmdForAll) + '\n'
        s[6] = 'cmdForMe = ' + str(cmdForMe) + '\n'
        s[7] = 'cmdNew = ' + str(cmdNew) + '\n'
        s[8] = 'halloweenScene = ' + str(halloweenScene) + '\n'
        s[9] = 'duck = ' + str(duck) + '\n'
        s[10] = 'showServerData = ' + str(showServerData) + '\n'
        s[11] = 'writeServerData = ' + str(writeServerData) + '\n'
        s[12] = 'agreement = ' + str(agreement) + '\n'
        s[13] = 'forcedUI = ' + str(forcedUI) + '\n'
        s[14] = 'theme = ' + "'" + str(theme) + "'" + '\n'

    f = open(
        bs.getEnvironment()['systemScriptsDirectory']+'/settings.py', 'w')

    for i in s:
        f.write(i)

    f.close()
