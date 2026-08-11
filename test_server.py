import os
import tempfile
import threading
import unittest
import urllib.error
import urllib.request

from server import ThreadedUploadServer, UploadHandler


class UploadServerTest(unittest.TestCase):
    def setUp(self):
        self.upload_dir = tempfile.mkdtemp()
        self.server = ThreadedUploadServer(("127.0.0.1", 0), UploadHandler, self.upload_dir)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base = f"http://127.0.0.1:{self.server.server_address[1]}"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()

    def test_upload_creates_subdirectories(self):
        body = b"hello log"
        request = urllib.request.Request(
            f"{self.base}/upload",
            data=body,
            headers={"X-File-Path": "device-01/logs/app.log"},
            method="POST",
        )
        with urllib.request.urlopen(request) as response:
            self.assertEqual(response.status, 200)

        target = os.path.join(self.upload_dir, "device-01", "logs", "app.log")
        self.assertTrue(os.path.isfile(target))
        with open(target, "rb") as fh:
            self.assertEqual(fh.read(), body)

    def test_upload_rejects_path_traversal(self):
        request = urllib.request.Request(
            f"{self.base}/upload",
            data=b"bad",
            headers={"X-File-Path": "../escape.log"},
            method="POST",
        )
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(request)
        self.assertEqual(ctx.exception.code, 400)


if __name__ == "__main__":
    unittest.main()
