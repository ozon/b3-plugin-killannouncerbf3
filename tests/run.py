#!/bin/python
"""
Script that runs the test suite
"""

if __name__ == '__main__':
    import os
    import sys

    # add extplugins to the Python sys.path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../extplugins'))

    # discover is the settings.ini file exits in the tests directory
    SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "settings.ini")
    if os.path.exists(SETTINGS_FILE):
        print "found config file at %r" % SETTINGS_FILE
        from ConfigParser import SafeConfigParser
        config = SafeConfigParser()
        config.read(SETTINGS_FILE)
        if config.has_option("settings", "B3_MODULE_PATH"):
            B3_PATH = os.path.expanduser(config.get("settings", "B3_MODULE_PATH"))
            if B3_PATH:
                if not os.path.exists(B3_PATH):
                    print "ERROR: path %r does not exists" % B3_PATH
                    sys.exit(1)
                if not os.path.exists(os.path.join(B3_PATH, "b3")):
                    print "ERROR: module b3 not found in %r" % B3_PATH
                    sys.exit(1)
                # add the b3 module path to the Python sys.path
                print "adding %r to Python sys.path" % B3_PATH
                sys.path.insert(0, B3_PATH)


    try:
        import b3
    except ImportError, err:
        if not os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "w") as f:
                f.write(r"""[settings]
    # B3_MODULE_PATH - the path where the 'b3' module can be found
    #
    # example:
    #   B3_MODULE_PATH: C:\\big-brother-bot\

    B3_MODULE_PATH:

    """)

        print """

    ERROR: Cannot find the b3 module in the python path.

        Make sure to have the b3 module in you python sys.path or in your PYTHONPATH environnement variable.
        Or set the path to your big-brother-bot directory in %r

    """ % SETTINGS_FILE
        raise err

    import nose
    nose.main()