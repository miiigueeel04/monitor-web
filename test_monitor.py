"""Tests del monitor. Ejecutar con:  python -m unittest -v"""

import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer

from monitor import comprobar


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/ok":
            self.send_response(200)
        else:
            self.send_response(404)
        self.end_headers()
        self.wfile.write(b"hola")

    def log_message(self, *args):  # silencia los logs del servidor de prueba
        pass


class TestComprobar(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.servidor = HTTPServer(("127.0.0.1", 0), Handler)
        cls.puerto = cls.servidor.server_address[1]
        threading.Thread(target=cls.servidor.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.servidor.shutdown()

    def test_web_activa(self):
        r = comprobar(f"http://127.0.0.1:{self.puerto}/ok")
        self.assertTrue(r["ok"])
        self.assertEqual(r["estado"], 200)
        self.assertIsInstance(r["ms"], int)

    def test_error_404(self):
        r = comprobar(f"http://127.0.0.1:{self.puerto}/no-existe")
        self.assertFalse(r["ok"])
        self.assertEqual(r["estado"], 404)

    def test_web_caida(self):
        r = comprobar("http://127.0.0.1:9", timeout=2)  # puerto cerrado
        self.assertFalse(r["ok"])
        self.assertEqual(r["estado"], "")
        self.assertNotEqual(r["error"], "")


if __name__ == "__main__":
    unittest.main()