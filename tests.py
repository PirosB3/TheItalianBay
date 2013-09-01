import os
import sys
import unittest
import yaml

class PirateBayTestCase(unittest.TestCase):

    def test_top_100_work(self):
        result = PirateBayAPI.requestResultsforTop100(disable_cache=True)
        self.assertEqual(100, len(result))

    def test_has_se_and_le(self):
        results = PirateBayAPI.requestResultsforTop100(disable_cache=True)
        for result in results:
            for key in ['title', 'href', 'size', 'SE', 'LE']:
                self.assertTrue(result[key])

    def test_has_magnet_links(self):
        results = PirateBayAPI.requestResultsforTop100(disable_cache=True)
        for result in results:
            self.assertEqual(result['href'][:7], 'magnet:')

    def test_recent_word(self):
        result = PirateBayAPI.requestResultsforRecentUploads(disable_cache=True)
        self.assertEqual(29, len(result))


if __name__ == '__main__':

    # Fix GAE path
    import dev_appserver
    dev_appserver.fix_sys_path()
    from google.appengine.ext.remote_api import remote_api_stub

    # Add TheItalianBay path
    this_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, this_dir)
    from libs import PirateBayAPI

    # Load YAML configuration file, import and initialize remote API
    config_file = yaml.load(open(sys.argv.pop(1)))
    env_variables = config_file['env_variables']
    remote_api_stub.ConfigureRemoteApi(None, '/_ah/remote_api', 
        lambda: (env_variables['TIB_USERNAME'], env_variables['TIB_PASSWORD']), 'theitalianbay.appspot.com')

    # Run tests
    unittest.main()
