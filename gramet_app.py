#!/usr/bin/env python3
"""
GRAMET Web - JetSMART (version Railway / nube)

Arquitectura Opcion A:
- La UI (botones de cruces) se sirve igual que antes.
- Al elegir un cruce + horas, el navegador abre una PESTANA NUEVA hacia /ver.
- /ver muestra "Generando..." y carga la imagen desde /gramet.
- /gramet corre Playwright EN EL SERVIDOR: navega directo a display_gramet.php
  con el tref (timestamp) generado al vuelo, y devuelve SOLO la imagen del
  grafico (screenshot del <img>), asi el banner "Entendido" nunca aparece.
"""

from flask import Flask, request, Response, abort
import time
from playwright.sync_api import sync_playwright

app = Flask(__name__)

OGIMET_FL = "250"  # Flight level fijo para cruces de cordillera


# ---------------------------------------------------------------------------
# UI principal
# ---------------------------------------------------------------------------
@app.route('/')
def index():
    return '''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GRAMET - JetSMART</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #f5f5f5; }
        .header { background: #0c3c7d; color: white; padding: 8px; text-align: center; }
        .header h1 { font-size: 16px; margin: 0; }
        .container { max-width: 900px; margin: 0 auto; padding: 0 10px; }
        .zona-titulo { font-size: 12px; font-weight: bold; color: #0c3c7d; margin: 8px 0 6px 0; }
        .zona-container { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 8px; }
        .columna { background: white; border-radius: 6px; padding: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .columna-titulo { font-size: 11px; font-weight: bold; text-align: center; margin-bottom: 6px; padding-bottom: 4px; border-bottom: 1px solid #e0e0e0; }
        .oe-titulo { color: #0c7eb0; }
        .eo-titulo { color: #ff9800; }
        .flecha { font-size: 16px; text-align: center; margin-bottom: 4px; font-weight: bold; }
        .oe-flecha { color: #0c7eb0; }
        .eo-flecha { color: #ff9800; }
        .cruce-btn { display: block; width: 100%; padding: 6px; margin-bottom: 4px; border: 1px solid #ddd; border-radius: 3px; background: white; cursor: pointer; font-size: 11px; font-weight: 500; transition: all 0.2s; }
        .cruce-btn:hover { border-color: #0c7eb0; background: #f0f7ff; }
        .cruce-btn.selected-oe { background: #0c7eb0 !important; color: white !important; border-color: #0c7eb0 !important; }
        .cruce-btn.selected-eo { background: #ff9800 !important; color: white !important; border-color: #ff9800 !important; }
        .controles { background: #e3f2fd; padding: 10px; border-radius: 6px; margin: 8px 0; }
        .control-label { font-size: 10px; font-weight: bold; color: #0c3c7d; margin-bottom: 4px; display: block; }
        .horas-botones { display: flex; gap: 4px; flex-wrap: wrap; margin-bottom: 8px; }
        .hora-btn { padding: 4px 8px; background: white; border: 1px solid #ddd; border-radius: 3px; cursor: pointer; font-size: 10px; font-weight: bold; color: #0c3c7d; }
        .hora-btn:hover { border-color: #0c7eb0; background: #f0f7ff; }
        .hora-btn.selected-hora { background: #0c7eb0 !important; color: white !important; border-color: #0c7eb0 !important; }
        .manual-input { width: 50px; padding: 4px; border: 1px solid #ddd; border-radius: 3px; font-size: 10px; text-align: center; }
        .status { font-size: 10px; color: #666; margin-bottom: 6px; }
        .status.active { color: #0c7eb0; font-weight: bold; }
        .btn-obtener { width: 100%; padding: 8px; background: #0c7eb0; color: white; border: none; border-radius: 3px; font-size: 12px; font-weight: bold; cursor: pointer; }
        .footer { background: #e0e0e0; text-align: center; padding: 8px; font-size: 8px; color: #666; margin-top: 8px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>GRAMET - JetSMART | Cruces de Cordillera | FL250</h1>
    </div>

    <div class="container">
        <div class="zona-titulo">ZONA NORTE</div>
        <div class="zona-container">
            <div class="columna">
                <div class="flecha oe-flecha">-&gt;</div>
                <div class="columna-titulo oe-titulo">O-&gt;E</div>
                <button class="cruce-btn" data-codigo="SCAT_SANC" data-nombre="GEKAL (O-&gt;E)" onclick="seleccionar(this)">GEKAL</button>
                <button class="cruce-btn" data-codigo="SCSE_SANU" data-nombre="MIBAS (O-&gt;E)" onclick="seleccionar(this)">MIBAS</button>
                <button class="cruce-btn" data-codigo="SCVM_SANU" data-nombre="GUVOL (O-&gt;E)" onclick="seleccionar(this)">GUVOL</button>
            </div>
            <div class="columna">
                <div class="flecha eo-flecha">&lt;-</div>
                <div class="columna-titulo eo-titulo">E-&gt;O</div>
                <button class="cruce-btn" data-codigo="SANC_SCAT" data-nombre="GEKAL (E-&gt;O)" onclick="seleccionar(this)">GEKAL</button>
                <button class="cruce-btn" data-codigo="SANU_SCSE" data-nombre="MIBAS (E-&gt;O)" onclick="seleccionar(this)">MIBAS</button>
                <button class="cruce-btn" data-codigo="SANU_SCVM" data-nombre="ASIMO (E-&gt;O)" onclick="seleccionar(this)">ASIMO</button>
                <button class="cruce-btn" data-codigo="SAME_SCVM" data-nombre="UMKAL (E-&gt;O)" onclick="seleccionar(this)">UMKAL</button>
            </div>
        </div>

        <div class="zona-titulo">ZONA SUR</div>
        <div class="zona-container">
            <div class="columna">
                <div class="flecha oe-flecha">-&gt;</div>
                <div class="columna-titulo oe-titulo">O-&gt;E</div>
                <button class="cruce-btn" data-codigo="SCEL_SAMR" data-nombre="NEBEG (O-&gt;E)" onclick="seleccionar(this)">NEBEG</button>
                <button class="cruce-btn" data-codigo="SCRG_SAME" data-nombre="ALBAL (O-&gt;E)" onclick="seleccionar(this)">ALBAL</button>
                <button class="cruce-btn" data-codigo="SCIC_SAMM" data-nombre="ANKON (O-&gt;E)" onclick="seleccionar(this)">ANKON</button>
            </div>
            <div class="columna">
                <div class="flecha eo-flecha">&lt;-</div>
                <div class="columna-titulo eo-titulo">E-&gt;O</div>
                <button class="cruce-btn" data-codigo="SAMM_SCIC" data-nombre="ANKON (E-&gt;O)" onclick="seleccionar(this)">ANKON</button>
            </div>
        </div>

        <div class="controles">
            <label class="control-label">Horas:</label>
            <div class="horas-botones">
                <button class="hora-btn" onclick="setHoras(0)">0</button>
                <button class="hora-btn" onclick="setHoras(1)">1</button>
                <button class="hora-btn" onclick="setHoras(2)">2</button>
                <button class="hora-btn" onclick="setHoras(3)">3</button>
                <button class="hora-btn" onclick="setHoras(4)">4</button>
                <button class="hora-btn" onclick="setHoras(5)">5</button>
                <button class="hora-btn" onclick="setHoras(6)">6</button>
                <label>Manual: <input type="number" id="horasManual" class="manual-input" value="0" min="0" max="23"></label>
            </div>
            <div class="status" id="status">Selecciona un cruce</div>
            <button class="btn-obtener" onclick="obtenerGramet()">Obtener GRAMET</button>
        </div>
    </div>

    <div class="footer">
        JetSMART Operations | OGIMET
    </div>

    <script>
    var cruce_seleccionado = '';
    var nombre_cruce = '';

    function seleccionar(btn) {
        var codigo = btn.getAttribute('data-codigo');
        var nombre = btn.getAttribute('data-nombre');

        var todos = document.querySelectorAll('.cruce-btn');
        for (var i = 0; i < todos.length; i++) {
            todos[i].classList.remove('selected-oe', 'selected-eo');
        }

        cruce_seleccionado = codigo;
        nombre_cruce = nombre;

        if (nombre.indexOf('O-&gt;E') > -1 || nombre.indexOf('O->E') > -1) {
            btn.classList.add('selected-oe');
        } else {
            btn.classList.add('selected-eo');
        }

        document.getElementById('status').textContent = 'OK: ' + nombre;
        document.getElementById('status').classList.add('active');
    }

    function setHoras(h) {
        document.getElementById('horasManual').value = h;
        var todos = document.querySelectorAll('.hora-btn');
        for (var i = 0; i < todos.length; i++) {
            todos[i].classList.remove('selected-hora');
        }
        event.target.classList.add('selected-hora');
    }

    function obtenerGramet() {
        if (!cruce_seleccionado) {
            alert('Selecciona un cruce');
            return;
        }
        var horas = document.getElementById('horasManual').value;
        // Abrir en PESTANA NUEVA el visor
        var url = '/ver?icao=' + encodeURIComponent(cruce_seleccionado) +
                  '&horas=' + encodeURIComponent(horas) +
                  '&nombre=' + encodeURIComponent(nombre_cruce);
        window.open(url, '_blank');
    }
    </script>
</body>
</html>'''


# ---------------------------------------------------------------------------
# Visor: se abre al instante en la pestana nueva y carga la imagen
# ---------------------------------------------------------------------------
@app.route('/ver')
def ver():
    icao = request.args.get('icao', '')
    horas = request.args.get('horas', '0')
    nombre = request.args.get('nombre', icao)
    img_url = f"/gramet?icao={icao}&horas={horas}"
    return f'''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>GRAMET {nombre}</title>
    <style>
        body {{ font-family: Arial, sans-serif; background: #111; color: #eee; text-align: center; margin: 0; padding: 0; }}
        .barra {{ background: #0c3c7d; color: #fff; padding: 8px; font-size: 14px; font-weight: bold; }}
        #msg {{ padding: 30px; font-size: 14px; color: #ccc; }}
        img {{ max-width: 100%; height: auto; display: none; margin: 0 auto; }}
    </style>
</head>
<body>
    <div class="barra">GRAMET - {nombre} | FL250</div>
    <div id="msg">Generando GRAMET... (OGIMET puede tardar unos segundos)</div>
    <img id="gramet" alt="GRAMET">
    <script>
        var img = document.getElementById('gramet');
        img.onload = function() {{
            document.getElementById('msg').style.display = 'none';
            img.style.display = 'block';
        }};
        img.onerror = function() {{
            document.getElementById('msg').textContent =
                'No se pudo generar el GRAMET. Intenta de nuevo en unos segundos.';
        }};
        img.src = "{img_url}";
    </script>
</body>
</html>'''


# ---------------------------------------------------------------------------
# Genera el GRAMET server-side y devuelve SOLO la imagen (PNG)
# ---------------------------------------------------------------------------
@app.route('/gramet')
def gramet():
    icao = request.args.get('icao', '')
    horas = request.args.get('horas', '0')

    if not icao:
        abort(400, "Falta el parametro icao")

    tref = int(time.time())  # hora de referencia = ahora (epoch UTC)
    ogimet_url = (
        "https://www.ogimet.com/display_gramet.php"
        f"?icao={icao}&hini={horas}&tref={tref}&hfin={horas}"
        f"&fl={OGIMET_FL}&enviar=Enviar"
    )

    print(f"[{time.strftime('%H:%M:%S')}] {icao} -> {ogimet_url}")

    try:
        png = capturar_gramet(ogimet_url)
    except Exception as e:
        print(f"  ERROR: {e}")
        abort(502, f"Error generando GRAMET: {e}")

    return Response(png, mimetype='image/png')


def capturar_gramet(url):
    """Abre la URL en Playwright y devuelve el PNG del grafico (bytes)."""
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        page = browser.new_page(viewport={"width": 1400, "height": 900})
        try:
            page.goto(url, wait_until="networkidle", timeout=90000)

            # Intento (best-effort) de cerrar el banner "Entendido".
            # No es critico: igual capturamos solo la imagen, no la pagina.
            for sel in ["text=Entendido",
                        "button:has-text('Entendido')",
                        "input[value*='Entendido']"]:
                try:
                    page.click(sel, timeout=1500)
                    break
                except Exception:
                    pass

            # Esperar a que la imagen del grafico cargue de verdad
            try:
                page.wait_for_function(
                    "() => Array.from(document.images)"
                    ".some(i => i.naturalWidth > 300)",
                    timeout=60000
                )
            except Exception:
                pass

            # Marcar la imagen mas grande (= el GRAMET) y capturarla sola
            encontrada = page.evaluate("""() => {
                const imgs = Array.from(document.images)
                    .filter(i => i.naturalWidth > 200 && i.naturalHeight > 100);
                if (!imgs.length) return false;
                imgs.sort((a, b) =>
                    b.naturalWidth * b.naturalHeight - a.naturalWidth * a.naturalHeight);
                imgs[0].setAttribute('data-gramet-target', '1');
                return true;
            }""")

            if encontrada:
                elemento = page.query_selector('[data-gramet-target="1"]')
                png = elemento.screenshot()
            else:
                # Fallback: captura de toda la pagina
                png = page.screenshot(full_page=True)

            return png
        finally:
            browser.close()


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8080))
    print(f"\nGRAMET Web (Railway) - http://localhost:{port}\n")
    app.run(debug=False, host='0.0.0.0', port=port, threaded=True)
