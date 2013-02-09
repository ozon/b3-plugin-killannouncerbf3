from unittest import TestCase
from b3.fake import FakeConsole
from b3.config import XmlConfigParser, CfgConfigParser
from killannouncerbf3 import Killannouncerbf3Plugin


class Test_onLoadConfig(TestCase):

    def setUp(self):

        # create a B3 FakeConsole
        self.parser_conf = XmlConfigParser()
        self.parser_conf.loadFromString(r"""<configuration/>""")
        self.console = FakeConsole(self.parser_conf)

        # create our plugin instance
        self.plugin_conf = CfgConfigParser()
        self.p = Killannouncerbf3Plugin(self.console, self.plugin_conf)

    def test_announce_first_kill_yes(self):
        # GIVEN
        self.plugin_conf.loadFromString(r'''
[settings]
announce first kill: yes
''')
        # WHEN
        self.p.onLoadConfig()
        # THEN
        self.assertTrue(self.p._handle_firstkill)

    def test_announce_first_kill_no(self):
        # GIVEN
        self.plugin_conf.loadFromString(r'''
[settings]
announce first kill: no
''')
        # WHEN
        self.p.onLoadConfig()
        # THEN
        self.assertFalse(self.p._handle_firstkill)

    def test_announce_first_kill_junk(self):
        # GIVEN
        self.plugin_conf.loadFromString(r'''
[settings]
announce first kill: qsdfqsdfqsdf
''')
        # WHEN
        self.p.onLoadConfig()
        # THEN
        self.assertTrue(self.p._handle_firstkill)

    def test_announce_first_kill_on(self):
        # GIVEN
        self.plugin_conf.loadFromString(r'''
[settings]
announce first kill: on
''')
        # WHEN
        self.p.onLoadConfig()
        # THEN
        self.assertTrue(self.p._handle_firstkill)

    def test_announce_first_kill_off(self):
        # GIVEN
        self.plugin_conf.loadFromString(r'''
[settings]
announce first kill:off
''')
        # WHEN
        self.p.onLoadConfig()
        # THEN
        self.assertFalse(self.p._handle_firstkill)