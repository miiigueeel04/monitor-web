"""Tests de guardar() con SQLite. Ejecutar con:  python -m unittest -v"""

import tempfile
import unittest
from pathlib import Path

from monitor import guardar, ultimas

OK = {"fecha": "2026-11-09T10:00:00", "url": "https://a.com",
      "estado": 200, "ok": True, "ms": 320, "error": ""}
CAIDA = {"fecha": "2026-11-09T10:05:00", "url": "https://b.com",
         "estado": "", "ok": False, "ms": "", "error": "ConnectionError"}


class TestGuardar(unittest.TestCase):
    def setUp(self):
        self.carpeta = tempfile.TemporaryDirectory()
        self.ruta = Path(self.carpeta.name) / "test.db"

    def tearDown(self):
        self.carpeta.cleanup()

    def test_guarda_filas(self):
        guardar([OK, CAIDA], self.ruta)
        self.assertEqual(len(ultimas(self.ruta, 10)), 2)

    def test_vacios_se_guardan_como_null(self):
        guardar([CAIDA], self.ruta)
        fecha, url, estado, ok, ms, error = ultimas(self.ruta, 1)[0]
        self.assertIsNone(estado)
        self.assertIsNone(ms)
        self.assertEqual(ok, 0)
        self.assertEqual(error, "ConnectionError")

    def test_no_borra_lo_anterior(self):
        guardar([OK], self.ruta)
        guardar([OK], self.ruta)  # segunda ejecución
        self.assertEqual(len(ultimas(self.ruta, 10)), 2)

    def test_ok_se_guarda_como_1(self):
        guardar([OK], self.ruta)
        self.assertEqual(ultimas(self.ruta, 1)[0][3], 1)


if __name__ == "__main__":
    unittest.main()