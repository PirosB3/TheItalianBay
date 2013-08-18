import os
import sys
import unittest


class PirateBayTestCase(unittest.TestCase):

    def test_top_100_work(self):
        result = PirateBayAPI.requestResultsforTop100(disable_cache=True)
        self.assertEqual(100, len(result))

    def test_recent_word(self):
        result = PirateBayAPI.requestResultsforRecentUploads(disable_cache=True)
        self.assertEqual(30, len(result))



if __name__ == '__main__':

    # Fix GAE path
    import dev_appserver
    dev_appserver.fix_sys_path()

    # Add TheItalianBay path
    this_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, this_dir)
    from libs import PirateBayAPI

    # Import and initialize remote API
    from google.appengine.ext.remote_api import remote_api_stub
    remote_api_stub.ConfigureRemoteApi(None, '/_ah/remote_api', 
        lambda: ('pirosb3@gmail.com', os.environ['TIB_PASSWORD']), 'theitalianbay.appspot.com')

    # Run tests
    unittest.main()
