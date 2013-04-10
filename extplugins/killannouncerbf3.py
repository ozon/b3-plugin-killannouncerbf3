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
from ConfigParser import NoOptionError
from random import choice
from weapondef import WEAPON_NAMES_BY_ID

__version__ = '0.1'
__author__ = 'ozon'


class Killannouncerbf3Plugin(Plugin):
    _adminPlugin = None
    _streak_table = {}
    _handle_firstkill = False
    _round_started = False
    _weaponlist = None

    streak_messages = dict()


    def onLoadConfig(self):
        #load settings
        self._load_settings()

        #check for settings section in config
        remove_sections = ['settings', 'first kill alert', 'losing streak alerts','kill streak alerts', 'end kill streak alerts',]
        if self.config.has_section('settings'):
            #load all section names
            all_sections = self.config.sections()
            #remove known section names
            for i in remove_sections:
                if i in all_sections:
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

        self._streak_table = {}

        self._load_streak_messages()
        # register on events
        self.registerEvent(b3.events.EVT_CLIENT_KILL)
        self.registerEvent(b3.events.EVT_GAME_ROUND_START)


    def onEvent(self, event):
        """ Handle CLIENT_KILL and GAME_EXIT events """
        if event.type == b3.events.EVT_CLIENT_KILL:
            self.update_killstreaks(event.client, weapon=event.data[1], victim=event.target)
        elif event.type == b3.events.EVT_GAME_ROUND_START:
            self._round_started = True
            self._streak_table = {}

    def update_killstreaks(self, client, weapon=None, victim=None):
        """ Update kill streaks table """

        self.debug('Attacker: %s, Victim: %s, Weapon: %s' % (client.name, victim.name, weapon))

        #handle other types of kills
        if weapon in ('SoldierCollision', 'Death', 'DamageArea', 'RoadKill'):
            #self._streak_table.update({client.name: {'kills': 0}, })
            return

        #handle Suicide
        if client.name == victim.name or weapon == 'Suicide':
            self._sayBig( 'Suicide' , {'murderer': client.name,})
            self._streak_table.update({client.name: {'kills': 0}, })
            return

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
                    self._sayBig( 'end kill streak alerts' , {'murderer': victim.name, 'victim': client.name,'kill_streak_value':str(current_kills)})

            self._streak_table.update({victim.name: {'kills': lossstreak}, })

        # actions
        if self._handle_firstkill and self._round_started:
            self.debug('Handle first kill')
            #msg_template = choice([ item[1] for item in self.config.items('first kill alert',raw=True) if item[0].startswith("us")])
            self._sayBig( 'first kill alert' , {'murderer': client.name, 'victim': victim.name})
            self._round_started = False

        if weapon in self._weaponlist:
            ##msg_template = choice([ item[1] for item in self.config.items(weapon,raw=True) if item[0].startswith("us")])
            self._sayBig( weapon , { 'murderer' : client.name, 'victim': victim.name,})

        if str(killstreak) in self.streak_messages['us'].keys():
            #msg_template = self.config.getTextTemplate('kill streak alerts', str(killstreak))
            self._sayBig_killstreak( str(killstreak) , {'murderer': client.name, 'kill_streak_value': killstreak,})

        lossstreak_str =  '%d' % lossstreak
        if lossstreak_str[1:] in self.config.options('losing streak alerts'):
            ##msg_template = self.config.getTextTemplate('losing streak alerts', lossstreak_str[1:])
            self._sayBig( 'losing streak alerts' , {'victim': victim.name, 'losstreak': lossstreak_str[1:],})


    def _sayBig_killstreak(self, streak_count, formatvalues=None):
        clients = self.console.clients.getList()
        for c in clients:
            if c.country.lower() in self.streak_messages:
                c.message(self.streak_messages[c.country.lower()][streak_count] % (formatvalues))
            else:
                c.message(self.streak_messages['us'][streak_count] % (formatvalues))


    def _get_random_langmsg_dict(self, section):
        _msgitems = self.config.items(section, raw=True)
        _msgdict = dict().fromkeys( [i[:2] for i in  self.config.options(section) ] )
        for l in _msgdict.iterkeys():
            _msgdict[l] = choice( [v for k,v in _msgitems if k.startswith(l)] )

        return _msgdict

    def _sayBig(self, message_section, formatvalues=None):
        _msgdict = self._get_random_langmsg_dict(message_section)
        if len(_msgdict) <= 1:
            self.console.saybig(_msgdict.values() % (formatvalues))
        else:
            clients = self.console.clients.getList()
            for c in clients:
                if c.country.lower() in _msgdict:
                    c.message(_msgdict[c.country.lower()] % (formatvalues))
                else:
                    c.message(_msgdict['us'] % (formatvalues))

    def _load_streak_messages(self):
        _streak_items = self.config.items('kill streak alerts', raw=True)

        self.streak_messages = dict().fromkeys( [i[:2] for i in  self.config.options('kill streak alerts') ])
        for i in self.streak_messages:
            self.streak_messages[i] = dict( [(k[k.rfind('#')+1:],v)for k,v in _streak_items if k.startswith(i)] )



    def _load_settings(self):
        try:
            self._handle_firstkill = self.config.getboolean('settings','announce first kill')
        except NoOptionError:
            self.warning('conf "announce first kill" not found, using default : yes')
            self._handle_firstkill = True
        except ValueError:
            self.warning('conf "announce first kill" allow only yes or no as value')
            self._handle_firstkill = True

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
    superadmin.says('!putgroup simon user')

    joe.country = 'DE'
    simon.country = 'DE'
    superadmin.country = 'US'

    #fire some kills
    #joe.kills(simon)
    #joe.kills(superadmin)
    #joe.kills(superadmin)
    