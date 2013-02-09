from unittest import TestCase
from mock import patch, call
from b3 import TEAM_BLUE, TEAM_RED
from b3.fake import FakeConsole, FakeClient
from b3.config import XmlConfigParser, CfgConfigParser
from killannouncerbf3 import Killannouncerbf3Plugin


class Test_first_kill_alert(TestCase):

    def setUp(self):
        """
        the setUp method is called before each test to prepare the SUT (System Under Test)
        """

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
        ''')
        self.p.onLoadConfig()
        self.p.onStartup()

        # assume a EVT_GAME_ROUND_STARTED event was fired and handled
        self.p._round_started = True

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
        with patch.object(self.p, "update_killstreaks") as update_killstreaks_mock:
            joe.kills(simon)
        # THEN
        self.assertTrue(update_killstreaks_mock.called)

    def test_teamkill_events_are_not_caught(self):
        # GIVEN
        joe = FakeClient(console=self.console, name="Joe", guid="joe_guid", team=TEAM_BLUE)
        simon = FakeClient(console=self.console, name="Simon", guid="simon_guid", team=TEAM_BLUE)
        assert joe.team == simon.team
        joe.connects(cid='1')
        simon.connects(cid='2')
        # WHEN
        with patch.object(self.p, "update_killstreaks") as update_killstreaks_mock:
            joe.kills(simon)
        # THEN
        self.assertFalse(update_killstreaks_mock.called)

    def test_first_kill_does_get_announced(self):
        # GIVEN
        jack = FakeClient(console=self.console, name="Jack", guid="jack_guid", team=TEAM_BLUE)
        simon = FakeClient(console=self.console, name="Simon", guid="simon_guid", team=TEAM_RED)
        jack.connects(cid='1')
        simon.connects(cid='2')
        # WHEN
        with patch.object(self.console, "saybig") as saybig_mock:
            jack.kills(simon)
        # THEN
        self.assertTrue(saybig_mock.called)
        self.assertListEqual([call('Jack takes first blood against Simon! The battle has just began!!!')],
                             saybig_mock.mock_calls)

    def test_second_kill_does_not_get_announced(self):
        # GIVEN
        jack = FakeClient(console=self.console, name="Jack", guid="jack_guid", team=TEAM_BLUE)
        simon = FakeClient(console=self.console, name="Simon", guid="simon_guid", team=TEAM_RED)
        jack.connects(cid='1')
        simon.connects(cid='2')
        # WHEN
        with patch.object(self.console, "saybig") as saybig_mock:
            jack.kills(simon)
            simon.kills(jack)
            # THEN
        self.assertTrue(saybig_mock.called)
        self.assertListEqual([call('Jack takes first blood against Simon! The battle has just began!!!')],
                             saybig_mock.mock_calls)