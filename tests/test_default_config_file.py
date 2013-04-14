# -*- encoding: utf-8 -*-

# add extplugins to the Python sys.path
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../extplugins'))
import os
from unittest import TestCase
from b3.fake import FakeConsole
from b3.config import XmlConfigParser, CfgConfigParser
from killannouncerbf3 import Killannouncerbf3Plugin, __file__ as plugin__file__

DEFAULT_PLUGIN_CONFIG_FILE = os.path.join(os.path.dirname(plugin__file__), r'conf\plugin_killannouncerbf3.ini')


class Test_default_config_file(TestCase):

    def test_default_values(self):
        assert os.path.exists(DEFAULT_PLUGIN_CONFIG_FILE), "config file missing : %r" % DEFAULT_PLUGIN_CONFIG_FILE

        # create a B3 FakeConsole
        self.parser_conf = XmlConfigParser()
        self.parser_conf.loadFromString(r"""<configuration/>""")
        self.console = FakeConsole(self.parser_conf)

        # create our plugin instance
        self.plugin_conf = CfgConfigParser()
        self.p = Killannouncerbf3Plugin(self.console, self.plugin_conf)

        # load the plugin default config file
        self.plugin_conf.load(DEFAULT_PLUGIN_CONFIG_FILE)
        self.p.onLoadConfig()

        # now make our assertions
        self.assertTrue(self.p._handle_firstkill)
