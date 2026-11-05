import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from inventory.cli import main


class CliTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = str(Path(self.tmp.name) / "inventory.json")

    def tearDown(self):
        self.tmp.cleanup()

    def run_cli(self, *args):
        out = io.StringIO()
        with contextlib.redirect_stderr(io.StringIO()):
            code = main(["--db", self.db] + list(args), out=out)
        return code, out.getvalue()

    def test_list_output_format(self):
        self.run_cli("add", "A-1", "Bolt", "4")
        self.run_cli("add", "B-2", "Nut", "10")
        code, output = self.run_cli("list")
        self.assertEqual(code, 0)
        self.assertEqual(output, "A-1\tBolt\t4\nB-2\tNut\t10\n")

    def test_remove_unknown_sku_fails(self):
        code, _ = self.run_cli("remove", "Z-9", "1")
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
