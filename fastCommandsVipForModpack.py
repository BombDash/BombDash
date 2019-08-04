# -*- coding: utf-8 -*-
import bs
import bsUI
import bsInternal

print 'Fast Commands v1.1'

def _onPartyMemberPress(self, clientID, isHost, widget):
    # if we're the host, pop up 'kick' options for all non-host members
    if bsInternal._getForegroundHostSession() is not None:
        kickHost = True
    else:
        # kick-votes appeared in build 14248
        if bsInternal._getConnectionToHostInfo().get(
                'buildNumber', 0) < 14248:
            return

        kickHost = False

    if bs.getLanguage() == 'Russian':
        choicesList = [
            'Изгнать' if kickHost else 'Голосовать за вылет',
            'Вылет без голосования',
            'Убрать из игры',
            'Полет',
            'Новый полет',
            'Вылечить',
            'Усыпить',
            'Разморозить',
            'Превратить в коробку',
            'Радужный скин',
            'Профиль аккаунта'
            ]
    else:
        choicesList = [
            'Kick' if kickHost else 'Vote to Kick',
            'Departure without a vote',
            'Remove from game',
            'Fly',
            'New fly',
            'Cure',
            'Put to sleep',
            'Defrost',
            'Turn into box',
            'Rainbow skin',
            'Account profile'
            ]

    bsUI.PopupMenuWindow(
        position=widget.getScreenSpaceCenter(),
        scale=2.3 if bsUI.gSmallUI else 1.65 if bsUI.gMedUI else 1.23,
        choices=choicesList,
        currentChoice='kick',
        delegate=self)

    self._popupType = 'partyMemberPress'
    self._popupPartyMemberClientID = clientID
    self._popupPartyMemberIsHost = isHost

def popupMenuSelectedChoice(self, popupWindow, choice):
    def getIndex():
        for i in bsInternal._getGameRoster():
            if i['clientID'] == self._popupPartyMemberClientID:
                return bsInternal._getGameRoster().index(i)

    if self._popupType == 'partyMemberPress':
        if choice in ['Kick', 'Vote to Kick', 'Изгнать', 'Голосовать за вылет']:
            if self._popupPartyMemberIsHost:
                bs.playSound(bs.getSound('error'))
                bs.screenMessage(
                    bs.Lstr(resource='internal.cantKickHostError'),
                    color=(1, 0, 0))
            else:
                result = bsInternal._disconnectClient(
                    self._popupPartyMemberClientID)
                if not result:
                    bs.playSound(bs.getSound('error'))
                    bs.screenMessage(
                        bs.Lstr(
                            resource='getTicketsWindow.unavailableText'),
                        color=(1, 0, 0))

        elif choice in ['Departure without a vote', 'Вылет без голосования']:
            bsInternal._chatMessage(
                '/kick '+str(self._popupPartyMemberClientID))

        elif choice in ['Account profile', 'Профиль аккаунта']:
            for i in bsInternal._getGameRoster():
                if i['clientID'] == self._popupPartyMemberClientID:
                    bs.screenMessage(i['displayString'])

        else:
            if choice in ['Defrost', 'Разморозить']:
                _choice = 'thaw'
            elif choice in ['Turn into box', 'Превратить в коробку']:
                _choice = 'box'
            elif choice in ['Remove from game', 'Убрать из игры']:
                _choice = 'remove'
            elif choice in ['Cure', 'Вылечить']:
                _choice = 'heal'
            elif choice in ['Rainbow skin', 'Радужный скин']:
                _choice = 'rainbow'
            elif choice in ['Put to sleep', 'Усыпить']:
                _choice = 'sleep'
            elif choice in ['Fly', 'Полет']:
                _choice = 'fly'
            elif choice in ['New fly', 'Новый полет']:
                _choice = 'fly3d'

            bsInternal._chatMessage(
                '/'+_choice+' device '+eval(
                    bsInternal._getGameRoster()[getIndex()]['specString'])['n'])

    elif self._popupType == 'menu':
        if choice in ('mute', 'unmute'):
            bsConfig = bs.getConfig()
            bsConfig['Chat Muted'] = (choice == 'mute')
            bs.writeConfig()
            bs.applySettings()
            self._update()
        elif choice == 'favoritesChatMenuAddButton':
            configLastServer = bs.getConfig()['BombDash Last Server']
            configFavoritesServers = bs.getConfig()['BombDash Favorites Servers']
            if not configLastServer:
                bs.screenMessage(
                    bs.Lstr(resource='favoritesLastServerNone'),
                    (1, 0, 0))
            elif configLastServer in configFavoritesServers:
                bs.screenMessage(
                    bs.Lstr(resource='favoritesLastServerInFavorites'),
                    (1, 0, 0))
            else:
                bs.getConfig()['BombDash Favorites Servers'].append(configLastServer)
                bs.writeConfig()
                bs.screenMessage(
                    bs.Lstr(resource='favoritesLastServerAdded'),
                    (0, 1, 0))

    else:
        print 'unhandled popup type: '+str(self._popupType)

bsUI.PartyWindow._onPartyMemberPress = _onPartyMemberPress
bsUI.PartyWindow.popupMenuSelectedChoice = popupMenuSelectedChoice