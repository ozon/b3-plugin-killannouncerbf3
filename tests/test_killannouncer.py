# -*- encoding: utf-8 -*-

# add extplugins to the Python sys.path
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../extplugins'))

from unittest import TestCase
from mock import patch, call, Mock
from b3 import TEAM_BLUE, TEAM_RED
from b3.fake import FakeConsole, FakeClient
from b3.config import XmlConfigParser, CfgConfigParser
from b3.clients import Client
from killannouncerbf3 import Killannouncerbf3Plugin


class Test_first_kill_alert(TestCase):

    def setUp(self):
        # create a B3 FakeConsole
        self.parser_conf = XmlConfigParser()
        self.parser_conf.loadFromString(r"""<configuration/>""")
        self.console = FakeConsole(self.parser_conf)
        # create our plugin instance
        self.plugin_conf = CfgConfigParser()
        self.p = Killannouncerbf3Plugin(self.console, self.plugin_conf)
        # initialise the plugin
        self.plugin_conf.loadFromString(r'''
[settings]
announce first kill: yes
[first kill alert]
us1: %(murderer)s takes first blood against %(victim)s! The battle has just began!!!
de1: %(murderer)s hat das erste Blut von %(victim)s genommen! Die Schlacht hat begonnen!!!
[kill streak alerts]
us1 #5: Killing Spree! %(murderer)s is dominating on a %(kill_streak_value)s kill streak!
us2 #10: Killing Spree! %(murderer)s is dominating on a %(kill_streak_value)s kill streak!
[end kill streak alerts]
us1: %(murderer)s has ended %(murderer)s kill streak at %(kill_streak_value)s kills!

        ''')
        # Plugin ipinfodb is required. We trick and set county property later.
        self.p.console._plugins['ipinfodb'] = ''

        self.p.onLoadConfig()
        self.p.onStartup()
        # prepare a few players
        self.joe = FakeClient(self.console, name="Joe", exactName="Joe", guid="zaerezarezar", groupBits=1, country='de',team=TEAM_RED)
        self.simon = FakeClient(self.console, name="Simon", exactName="Simon", guid="qsdfdsqfdsqf", groupBits=0, country='us',team=TEAM_BLUE)
        self.admin = FakeClient(self.console, name="Level-40-Admin", exactName="Level-40-Admin", guid="875sasda", groupBits=16, country='ch',)
        self.superadmin = FakeClient(self.console, name="God", exactName="God", guid="f4qfer654r", groupBits=128, country='fr',)

        self.joe.connects(cid='1')
        self.simon.connects(cid='2')

    def test_kill_events_are_caught(self):
        # GIVEN
        joe = FakeClient(console=self.console, name="Joe", guid="joe_guid", team=TEAM_BLUE)
        simon = FakeClient(console=self.console, name="Simon", guid="simon_guid", team=TEAM_RED)
        assert joe.team != simon.team
        joe.connects(cid='1')
        simon.connects(cid='2')
        # WHEN
        # patch.object will replace the "update_killstreaks" property from object self.p with a mock object that does
        # nothing but allows us to assert if it was called or not.
        with patch.object(self.p, "kill") as update_killstreaks_mock:
            joe.kills(simon)
        # THEN
        self.assertTrue(update_killstreaks_mock.called)

    #
    # Test announcement on first kill
    #
    def test_first_kill_does_get_announced(self):
        # assume a EVT_GAME_ROUND_STARTED event was fired and handled
        self.p._round_started = True
        # WHEN
        with patch(target='b3.fake.FakeClient.message') as saybig_mock:
            self.joe.kills(self.simon)
        # THEN
        self.assertTrue(saybig_mock.called)
        self.assertListEqual([call('Joe hat das erste Blut von Simon genommen! Die Schlacht hat begonnen!!!'),
                              call('Joe takes first blood against Simon! The battle has just began!!!')], saybig_mock.mock_calls)

    def test_second_kill_does_not_get_announced(self):
        # assume a EVT_GAME_ROUND_STARTED event was fired and handled
        self.p._round_started = True

        with patch(target='b3.fake.FakeClient.message') as saybig_mock:
            self.joe.kills(self.simon)
            self.simon.kills(self.joe)
        # THEN
        self.assertTrue(saybig_mock.called)
        self.assertListEqual([call('Joe hat das erste Blut von Simon genommen! Die Schlacht hat begonnen!!!'),
                              call('Joe takes first blood against Simon! The battle has just began!!!')], saybig_mock.mock_calls)

    #
    # Streak tests
    #
    def test_kill_streak(self):
        with patch(target='b3.fake.FakeClient.message') as announce_kill_streak_mock:
            # Joe kills Simon 5 times:
            _count = 0
            while _count < 5 :
                _count += 1
                self.joe.kills(self.simon)
        self.assertTrue(announce_kill_streak_mock.called)
        self.assertListEqual([call('Killing Spree! Joe is dominating on a 5 kill streak!'),
                              call('Killing Spree! Joe is dominating on a 5 kill streak!')], announce_kill_streak_mock.mock_calls)
        # and kill himm again - 10 kills
        with patch(target='b3.fake.FakeClient.message') as announce_kill_streak_mock:
            # Joe kills Simon 5 times again:
            _count = 0
            while _count < 5 :
                _count += 1
                self.joe.kills(self.simon)
        self.assertTrue(announce_kill_streak_mock.called)
        self.assertListEqual([call('Killing Spree! Joe is dominating on a 10 kill streak!'),
                              call('Killing Spree! Joe is dominating on a 10 kill streak!')], announce_kill_streak_mock.mock_calls)

