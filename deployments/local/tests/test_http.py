"""Optional live proxy checks: PLANE_SMOKE_URL=http://localhost:17239."""

import http.client
import os
import unittest
from urllib.parse import urlsplit


@unittest.skipUnless(os.environ.get("PLANE_SMOKE_URL"), "Set PLANE_SMOKE_URL to test a running stack")
class LocalHTTPTests(unittest.TestCase):
    def test_frontend_asset_bursts_do_not_lock_out_the_browser(self):
        origin = urlsplit(os.environ["PLANE_SMOKE_URL"])
        self.assertEqual(origin.scheme, "http")
        connection = http.client.HTTPConnection(origin.hostname, origin.port, timeout=10)
        try:
            # A browser can load hundreds of chunks while moving between apps.
            # Exercise both the app entry points and deep-link SPA fallback.
            for path in ("/", "/god-mode/general/"):
                for index in range(350):
                    connection.request("GET", path)
                    response = connection.getresponse()
                    response.read()
                    self.assertEqual(response.status, 200, f"{path}: request {index + 1}")
        finally:
            connection.close()


if __name__ == "__main__":
    unittest.main()
