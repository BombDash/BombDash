scenes = [14, 13]
fair = False
bolt = False
badWords = False
puppeteer = False
cmdForAll = False
cmdForMe = True
cmdNew = False
halloweenScene = False
duck = False
forcedUI = 0
theme = 'Default'

def saveSettings():
    import bs
    with open(bs.getEnvironment()['systemScriptsDirectory']+'/settings.py') as file:
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
        s[10] = 'forcedUI = ' + str(forcedUI) + '\n'
        s[11] = 'theme = ' + "'" + str(theme) + "'" + '\n'

    f = open(bs.getEnvironment()['systemScriptsDirectory']+'/settings.py', 'w')
    for i in s:
        f.write(i)

    f.close()