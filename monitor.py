"""Monitor de webs.

Lee las URLs de urls.txt, comprueba cada una (estado HTTP y tiempo de
respuesta) y guarda el resultado en una base de datos SQLite (monitor.db).

Uso:
    python monitor.py
"""

import sqlite3
import time
from datetime import datetime
from pathlib import Path

import requests

BASE_DIR = Path(__file__).parent  # carpeta del proyecto, ejecutes desde donde ejecutes
URLS_FILE = BASE_DIR / "urls.txt"
DB_FILE = BASE_DIR / "monitor.db"
TIMEOUT = 10  # segundos


def leer_urls(ruta: Path) -> list[str]:
    """Lee las URLs ignorando líneas vacías y comentarios."""
    urls = []
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if linea and not linea.startswith("#"):
            urls.append(linea)
    return urls


def comprobar(url: str, timeout: int = TIMEOUT) -> dict:
    """Comprueba el estado de una URL y devuelve su estado y tiempo de respuesta en ms."""
    inicio = time.perf_counter()
    try:
        respuesta = requests.get(url, timeout=timeout)
        ms = round((time.perf_counter() - inicio) * 1000)
        return {
            "fecha": datetime.now().isoformat(timespec="seconds"),
            "url": url,
            "estado": respuesta.status_code,
            "ok": respuesta.ok,
            "ms": ms,
            "error": "",
        }
    except requests.RequestException as error:
        return {
            "fecha": datetime.now().isoformat(timespec="seconds"),
            "url": url,
            "estado": "",
            "ok": False,
            "ms": "",
            "error": type(error).__name__,
        }


def crear_tabla(ruta: Path) -> None:
    """Crea la tabla de comprobaciones si todavía no existe."""
    conexion = sqlite3.connect(ruta)
    try:
        with conexion:  # confirma (commit) al salir, o deshace si hay un error
            conexion.execute(
                """
                CREATE TABLE IF NOT EXISTS comprobaciones (
                    id     INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha  TEXT    NOT NULL,
                    url    TEXT    NOT NULL,
                    estado INTEGER,
                    ok     INTEGER NOT NULL,
                    ms     INTEGER,
                    error  TEXT
                )
                """
            )
    finally:
        conexion.close()


def _vacio_a_none(valor):
    """Los '' de comprobar() se guardan como NULL (None) en la base de datos."""
    return None if valor == "" else valor


def guardar(resultados: list[dict], ruta: Path) -> None:
    """Añade cada resultado como una fila nueva (nunca borra lo anterior)."""
    crear_tabla(ruta)
    filas = [
        (
            r["fecha"],
            r["url"],
            _vacio_a_none(r["estado"]),
            int(r["ok"]),  # True/False -> 1/0
            _vacio_a_none(r["ms"]),
            _vacio_a_none(r["error"]),
        )
        for r in resultados
    ]
    conexion = sqlite3.connect(ruta)
    try:
        with conexion:
            conexion.executemany(
                """
                INSERT INTO comprobaciones (fecha, url, estado, ok, ms, error)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                filas,
            )
    finally:
        conexion.close()


def ultimas(ruta: Path, n: int = 5) -> list[tuple]:
    """Devuelve las n últimas comprobaciones (útil para verificar el guardado)."""
    conexion = sqlite3.connect(ruta)
    try:
        cursor = conexion.execute(
            "SELECT fecha, url, estado, ok, ms, error "
            "FROM comprobaciones ORDER BY id DESC LIMIT ?",
            (n,),
        )
        return cursor.fetchall()
    finally:
        conexion.close()


def main() -> None:
    urls = leer_urls(URLS_FILE)
    resultados = [comprobar(url) for url in urls]
    guardar(resultados, DB_FILE)

    for r in resultados:
        estado = "OK  " if r["ok"] else "FALLO"
        detalle = f"{r['estado']} en {r['ms']} ms" if r["ms"] != "" else r["error"]
        print(f"[{estado}] {r['url']} -> {detalle}")


if __name__ == "__main__":
    main()