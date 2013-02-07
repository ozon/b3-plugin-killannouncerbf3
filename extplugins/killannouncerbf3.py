# -*- coding: utf-8 -*-

# Killannouncer Plugin for BigBrotherBot(B3)
# Copyright (c) 2012 Harry Gabriel <rootdesign@gmail.com>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import b3
import b3.events
from b3.plugin import Plugin
from random import choice

__version__ = '0.1'
__author__ = 'ozon'


class Killannouncerbf3Plugin(Plugin):
    _adminPlugin = None
    _streak_table = {}
    _handle_firstkill = False
    _weaponlist = None


    def onLoadConfig(self):
        #check for settings section in config
        remove_sections = ['settings', 'first kill alert', 'losing streak alerts','kill streak alerts', 'end kill streak alerts',]
        if self.config.has_section('settings'):
            #load all section names
            all_sections = self.config.sections()
            #remove known section names
            for i in remove_sections:
                all_sections.remove(i)

            self._weaponlist = all_sections
        else:
            self.error('[settings] section missing in config')


    def onStartup(self):
        self._adminPlugin = self.console.getPlugin('admin')
        if not self._adminPlugin:
            # something is wrong, can't start without admin plugin
            self.error('Could not find admin plugin')
            return False
            # register on events
        self._streak_table = {}
        self.registerEvent(b3.events.EVT_CLIENT_KILL)
        self.registerEvent(b3.events.EVT_GAME_ROUND_START)


    def onEvent(self, event):
        """ Handle CLIENT_KILL and GAME_EXIT events """
        if event.type == b3.events.EVT_CLIENT_KILL:
            self.update_killstreaks(event.client, weapon=event.data[1], victim=event.target)
        elif event.type == b3.events.EVT_GAME_ROUND_START:
            self._handle_firstkill = True
            self._streak_table = {}

    def update_killstreaks(self, client, weapon=None, victim=None):
        """ Update kill streaks table """
        # handle win for client
        if client:
            killstreak = 1
            if client.name in self._streak_table.keys():
                current_kills = self._streak_table[client.name]['kills']
                if current_kills >= 0:
                    killstreak = current_kills + 1
            self._streak_table.update({client.name: {'kills': killstreak}, })

        # handle loss for victim
        if victim:
            lossstreak = -1
            if victim.name in self._streak_table.keys():
                current_kills = self._streak_table[victim.name]['kills']
                if current_kills <= 0:
                    lossstreak = current_kills - 1
                elif current_kills >= 5:
                    msg_template = choice([ item[1] for item in self.config.items('end kill streak alerts',raw=True) if item[0].startswith("us")])
                    self.console.saybig( msg_template % {'murderer': victim.name, 'victim': client.name,'kill_streak_value':str(current_kills)})

            self._streak_table.update({victim.name: {'kills': lossstreak}, })

        # actions
        if self._handle_firstkill:
            self._handle_firstkill=False

        if weapon in self._weaponlist:
            msg_template = choice([ item[1] for item in self.config.items(weapon,raw=True) if item[0].startswith("us")])
            self.console.saybig( msg_template % {'murderer': client.name, 'victim': victim.name,})

        if str(killstreak) in self.config.options('kill streak alerts'):
            msg_template = self.config.getTextTemplate('kill streak alerts', str(killstreak))
            self.console.saybig( msg_template % {'murderer': client.name, 'kill_streak_value': killstreak,})

        lossstreak_str =  '%d' % lossstreak
        if lossstreak_str[1:] in self.config.options('losing streak alerts'):
            msg_template = self.config.getTextTemplate('losing streak alerts', lossstreak_str[1:])
            self.console.saybig( msg_template % {'victim': victim.name, 'losstreak': lossstreak_str[1:],})

if __name__ == '__main__':
    # create a fake console which emulates B3
    from b3.fake import fakeConsole, joe, superadmin, simon

    p = Killannouncerbf3Plugin(fakeConsole, 'conf/plugin_killannouncerbf3.ini')
    # call onStartup() as the real B3 would do
    p.onStartup()
    # make superadmin connect to the fake game server on slot 0
    superadmin.connects(cid=0)
    # make joe connect to the fake game server on slot 1
    joe.connects(cid=1)
    # make joe connect to the fake game server on slot 2
    simon.connects(cid=2)
    # superadmin put joe in group user
    superadmin.says('!putgroup joe user')
    #superadmin.says('!putgroup simon user')

    #fire some kills
    #joe.kills(simon)
    #joe.kills(superadmin)
    #joe.kills(superadmin)
    