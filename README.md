# Monitor de webs

Programa en Python que comprueba si unas webs están activas, mide cuánto tardan en responder y guarda el historial en una base de datos SQLite.

Lo creé para vigilar las webs que he desarrollado para negocios locales (alojadas en Netlify) y aprender conceptos de redes (HTTP, tiempos de respuesta, errores de conexión) y de bases de datos.

## Qué hace

- Lee una lista de URLs desde `urls.txt` (ignora líneas vacías y comentarios con `#`).
- Hace una petición HTTP a cada una con un tiempo máximo de espera (10 s).
- Registra el **código de estado**, el **tiempo de respuesta en milisegundos** y el tipo de error si la web no responde.
- Guarda cada comprobación como una fila nueva en `monitor.db` (SQLite), sin borrar el historial.
- Muestra un resumen por pantalla: `[OK]` o `[FALLO]` por cada web.

Ejemplo de salida:

```
[OK  ] https://reformas-demo.netlify.app -> 200 en 310 ms
[FALLO] https://esta-web-no-existe-12345.com -> ConnectionError
```

## Requisitos

- Python 3.10 o superior
- Librería `requests` (el resto de módulos vienen con Python)

## Instalación

```bash
git clone https://github.com/miiigueeel04/monitor-web.git
cd monitor-web
python -m venv venv
# Windows:      venv\Scripts\activate
# Mac / Linux:  source venv/bin/activate
pip install -r requirements.txt
```

## Uso

1. Edita `urls.txt` y pon una URL por línea.
2. Ejecuta:

```bash
python monitor.py
```

Cada ejecución añade las comprobaciones a la tabla `comprobaciones` de `monitor.db`. Se puede abrir con [DB Browser for SQLite](https://sqlitebrowser.org/) o consultar desde Python.

## Tests

```bash
python -m unittest -v
```

Los tests de `comprobar()` usan un servidor local, así que no dependen de Internet. Los de `guardar()` usan una base de datos temporal.

## Estructura

```
monitor-web/
├── monitor.py          # lógica principal (leer URLs, comprobar, guardar)
├── urls.txt            # webs a vigilar
├── test_monitor.py     # tests de comprobar()
├── test_guardar.py     # tests del guardado en SQLite
├── requirements.txt
└── README.md
```

## Estado del proyecto

- [x] Comprobación de estado y tiempo de respuesta
- [x] Lectura de URLs desde archivo
- [x] Historial en SQLite
- [x] Tests automáticos
- [ ] Ejecución periódica automática
- [ ] Avisos por Telegram cuando una web cae o se recupera
- [ ] Panel web con el estado y la latencia

## Notas

- Proyecto personal de aprendizaje. Las comprobaciones se hacen sobre webs propias.
- Si se añaden avisos por Telegram, el token se guardará en una variable de entorno y nunca en el código.