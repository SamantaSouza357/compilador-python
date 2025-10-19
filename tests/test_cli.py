import unittest
from pathlib import Path
import sys
from io import StringIO
from contextlib import redirect_stdout

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import main

class TestCLI(unittest.TestCase):
    def test_cli_prints_mepa_code(self):
        file_path = ROOT / "tests" / "files" / "exemplo_valido.txt"

        argv_backup = sys.argv[:]
        try:
            sys.argv = ["prog", "--file", str(file_path)]
            buf = StringIO()
            with redirect_stdout(buf):
                main.main()
        finally:
            sys.argv = argv_backup

        out = buf.getvalue()
        # Verifica se gerou MEPA válido
        self.assertIn("INPP", out)
        self.assertIn("PARA", out)
        self.assertIn("AMEM", out)

if __name__ == "__main__":
    unittest.main()