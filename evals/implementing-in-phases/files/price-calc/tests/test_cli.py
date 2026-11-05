import io
import unittest

from price_calc.cli import main


class CliTest(unittest.TestCase):
    def test_quote(self):
        out = io.StringIO()
        self.assertEqual(main(["quote", "1200", "3"], out=out), 0)
        self.assertEqual(out.getvalue(), "¥3,600\n")


if __name__ == "__main__":
    unittest.main()
