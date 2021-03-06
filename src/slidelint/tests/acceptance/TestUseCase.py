import os
import unittest
import testfixtures
import tempdir
from fabric import api

here = os.path.dirname(os.path.abspath(__file__))
bad_presentation = os.path.join(here, 'bad_presentation.pdf')
not_so_bad_presentation = os.path.join(here, 'not_so_bad_presentation.pdf')
good_presentation = os.path.join(here, 'good_presentation.pdf')
config1 = os.path.join(here, 'config_detailed_optimized')
config2 = os.path.join(here, 'config_categories_only')
config3 = os.path.join(here, 'config_simple_sensitive')

REBASE = False


def run(*arg, **kwargs):
    kwargs['capture'] = True
    try:
        return api.local(*arg, **kwargs)
    except SystemExit, message:
        raise ValueError(
            "[%s] run() received nonzero return code 1 while executing "
            "%s:\n%s" % (api.env.host_string, repr(arg), message.message))


@unittest.skip("This testsuite depends on network access so we skip it"
               "by default")
class TestAcceptanceManual(unittest.TestCase):
    # this setUpClass and tearDownClass creating a new venv and install
    # slidelint with pip from your local copy of slidelint sources, so all
    # tests of this testsute will be executed inside this venv;

    def test_manual_run(self):
        with tempdir.TempDir() as tmp_folder:
            dir = tmp_folder.name
            package_location = os.getcwd()
            venv_location = os.path.join(package_location, 'bin', 'virtualenv')
            with api.lcd(dir):
                run("%s --no-site-packages ." % venv_location)
                run("bin/pip install %s" % package_location)
                rez_file = 'lintrez.txt'
                rez = run("bin/slidelint -f html --files-output=%s  "
                          "%s" % (rez_file, bad_presentation))
                testfixtures.compare(
                    rez,
                    "No config file found, using default configuration")
                rez = run("cat %s" % rez_file)
                rez_file = bad_presentation[:-3] + 'fileoutput_default.txt'
                if REBASE:
                    with open(rez_file, 'wb') as f:
                        f.write(rez)
                else:
                    testfixtures.compare(
                        rez,
                        open(rez_file, 'rb').read())


class TestAcceptance(unittest.TestCase):

    def setUp(self):
        self.dir = os.getcwd()

    def test_info_option(self):
        with api.lcd(self.dir):
            rez = run("bin/slidelint -i %s" % bad_presentation)
            rez_file = bad_presentation[:-3] + 'infooption_default.txt'
            if REBASE:
                with open(rez_file, 'wb') as f:
                    f.write(rez)
            else:
                testfixtures.compare(
                    rez,
                    open(rez_file, 'rb').read())

    def test_output_format(self):
        with api.lcd(self.dir):
            rez = run("bin/slidelint -f parseable %s" % bad_presentation)
            rez_file = bad_presentation[:-3] + 'parsableformat_default.txt'
            if REBASE:
                with open(rez_file, 'wb') as f:
                    f.write(rez)
            else:
                testfixtures.compare(
                    rez,
                    open(rez_file, 'rb').read())

    def test_enablind_disabling(self):
        with api.lcd(self.dir):
            rez = run("bin/slidelint -i -f colorized -d C1002,ContentQuality"
                      ",edges_danger_zone -e "
                      "language_tool_checker %s" % bad_presentation)
            rez_file =\
                bad_presentation[:-3] + 'cmdlineenablingdisabling_default.txt'
            if REBASE:
                with open(rez_file, 'wb') as f:
                    f.write(rez)
            else:
                testfixtures.compare(
                    rez,
                    open(rez_file, 'rb').read())

    def test_file_output_file(self):
        with api.lcd(self.dir):
            with tempdir.TempDir() as tmp_folder:
                rez_file = os.path.join(tmp_folder, 'lintrez.txt')
                rez = run("bin/slidelint -f html --files-output=%s  "
                          "%s" % (rez_file, bad_presentation))
                testfixtures.compare(
                    rez,
                    "No config file found, using default configuration")
                rez = run("cat %s" % rez_file)
            rez_file = bad_presentation[:-3] + 'fileoutput_default.txt'
            if REBASE:
                with open(rez_file, 'wb') as f:
                    f.write(rez)
            else:
                testfixtures.compare(
                    rez,
                    open(rez_file, 'rb').read())

    def test_custom_config_file(self):
        with api.lcd(self.dir):
            presentations = (
                good_presentation,
                not_so_bad_presentation,
                bad_presentation)
            configs = (config1, config2, config3)
            for presentation in presentations:
                for config in configs:
                    config_suf = config.rsplit(os.path.sep, 1)[1] + '.txt'
                    rez_file = presentation[:-3] + config_suf
                    rez = run("bin/slidelint --config=%s "
                              "%s" % (config, presentation))
                    if REBASE:
                        with open(rez_file, 'wb') as f:
                            f.write(rez)
                    else:
                        testfixtures.compare(
                            rez,
                            open(rez_file, 'rb').read())

if __name__ == '__main__':
    import sys
    if 'rebaseline' in sys.argv:
        del sys.argv[sys.argv.index('rebaseline')]
        REBASE = True
    unittest.main()
