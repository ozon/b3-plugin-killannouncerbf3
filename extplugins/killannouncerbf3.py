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

class PlayerKillTable(object):
    kills = 0
    losses = 0

    current_kills = 0
    current_losses = 0

    def kill(self):
        self.current_losses = 0
        self.current_kills += 1

    def get_kill(self):
        _finish_streak = None
        if self.current_kills >= 5:
            _finish_streak = self.current_kills

        self.current_kills = 0
        self.current_losses += 1
        return _finish_streak



class Killannouncerbf3Plugin(Plugin):
    _adminPlugin = None
    _clientvar_name = 'Killannouncerbf3Plugin'
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
            self.kill(event.client, event.target, event.data)

        elif event.type == b3.events.EVT_GAME_ROUND_START:
            self._round_started = True
            self._streak_table = {}

    def _get_PlayerKillTable(self, client):
        """Return PlayKillTable or init a new"""
        if not client.isvar(self, self._clientvar_name):
            client.setvar(self, self._clientvar_name, PlayerKillTable())

        return client.var(self, self._clientvar_name).value

    def kill(self, client, target, data):
        if client is None:
            self.debug('No Client found! ....return')
            return
        if target is None:
            self.debug('No Target found! ....return')
            return
        if data is None:
            self.debug('No data found! ....return')
            return

        _killer = client
        _victim = target
        _weapon = data[1]

        if _weapon in ('SoldierCollision', 'Death', 'DamageArea'):
            self.debug('Data: %s ....return' % _weapon)
            return

        _killer_data = self._get_PlayerKillTable(client)
        _victim_data = self._get_PlayerKillTable(_victim)


        # check for suicide before give points
        if _killer.name == _victim.name or _weapon == 'Suicide':
            # suicide detectet
            _killer_data.get_kill()
            self._sayBig( 'Suicide' , {'murderer': _killer.name,})
            # we can leave here
            return
        else:
            _killer_data.kill()
            _finish_streak = _victim_data.get_kill()

        # check for kill streak and handle
        if str(_killer_data.current_kills) in self.streak_messages['us'].keys():
            self._sayBig_killstreak( str(_killer_data.current_kills) , {'murderer': _killer.name, 'kill_streak_value': _killer_data.current_kills,})

        # is killstreak finish?
        if _finish_streak:
            self._sayBig( 'end kill streak alerts' , {'murderer': _victim.name, 'victim': _killer.name,'kill_streak_value':_finish_streak})

        # check for weapon action ( example: anounce msg on knifekill
        if _weapon in self._weaponlist:
            self._sayBig( _weapon , { 'murderer' : _killer.name, 'victim': _victim.name,})

        # check for firstkill and handle
        if self._handle_firstkill and self._round_started:
            self._sayBig( 'first kill alert' , {'murderer': _killer.name, 'victim': _victim.name})
            self._round_started = False

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
    