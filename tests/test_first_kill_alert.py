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
us1 #7: Killing Spree! %(murderer)s is dominating on a %(kill_streak_value)s kill streak!
        ''')
        self.p.onLoadConfig()
        self.p.onStartup()

        # assume a EVT_GAME_ROUND_STARTED event was fired and handled
        self.p._round_started = True

        # prepare a few players
        self.joe = FakeClient(self.console, name="Joe", exactName="Joe", guid="zaerezarezar", groupBits=1, country='de',)
        self.simon = FakeClient(self.console, name="Simon", exactName="Simon", guid="qsdfdsqfdsqf", groupBits=0, country='us',)
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


    def test_first_kill_does_get_announced(self):
        # WHEN
        with patch(target='b3.fake.FakeClient.message') as saybig_mock:
            self.joe.kills(self.simon)
        # THEN
        self.assertTrue(saybig_mock.called)
        self.assertListEqual([call('Joe hat das erste Blut von Simon genommen! Die Schlacht hat begonnen!!!'),
                              call('Joe takes first blood against Simon! The battle has just began!!!')], saybig_mock.mock_calls)

    def test_second_kill_does_not_get_announced(self):
        with patch(target='b3.fake.FakeClient.message') as saybig_mock:
            self.joe.kills(self.simon)
            self.simon.kills(self.joe)
        # THEN
        self.assertTrue(saybig_mock.called)
        self.assertListEqual([call('Joe hat das erste Blut von Simon genommen! Die Schlacht hat begonnen!!!'),
                              call('Joe takes first blood against Simon! The battle has just began!!!')], saybig_mock.mock_calls)