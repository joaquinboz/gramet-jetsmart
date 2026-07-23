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
        .columna-titulo { font-size: 12px; font-weight: bold; text-align: center; margin-bottom: 6px; padding-bottom: 4px; border-bottom: 1px solid #e0e0e0; display: flex; justify-content: center; align-items: center; gap: 8px; }
        .oe-titulo { color: #0c7eb0; }
        .eo-titulo { color: #ff9800; }
        .dir-arrow-big { font-size: 22px; font-weight: 900; line-height: 1; display: inline-block; transform: scaleX(1.5); }
        .cruce-btn { display: block; width: 100%; padding: 6px; margin-bottom: 4px; border: 1px solid #ddd; border-radius: 3px; background: white; cursor: pointer; font-size: 11px; font-weight: 500; transition: all 0.2s; }
        .cruce-btn:hover { border-color: #0c7eb0; background: #f0f7ff; }
        .cruce-btn.selected-oe { background: #0c7eb0 !important; color: white !important; border-color: #0c7eb0 !important; }
        .cruce-btn.selected-eo { background: #ff9800 !important; color: white !important; border-color: #ff9800 !important; }
        .controles { background: #e3f2fd; padding: 10px; border-radius: 6px; margin: 8px 0; }
        .control-label { font-size: 10px; font-weight: bold; color: #0c3c7d; margin-bottom: 4px; display: block; }
        .fila-top { display: flex; justify-content: flex-end; align-items: center; gap: 16px; margin-bottom: 8px; }
        .ctrl-grupo { display: flex; align-items: center; gap: 6px; }
        .ctrl-grupo .control-label { margin-bottom: 0; }
        .horas-botones { display: flex; gap: 4px; flex-wrap: wrap; align-items: center; margin-bottom: 8px; }
        .hora-btn { padding: 4px 8px; background: white; border: 1px solid #ddd; border-radius: 3px; cursor: pointer; font-size: 10px; font-weight: bold; color: #0c3c7d; }
        .hora-btn:hover { border-color: #0c7eb0; background: #f0f7ff; }
        .hora-btn.selected-hora { background: #0c7eb0 !important; color: white !important; border-color: #0c7eb0 !important; }
        .manual-input { width: 50px; padding: 4px; border: 1px solid #ddd; border-radius: 3px; font-size: 11px; text-align: center; }
        .fl-select { padding: 4px 8px; border: 1px solid #0c7eb0; border-radius: 3px; font-size: 12px; font-weight: bold; color: #0c3c7d; background: white; cursor: pointer; }
        .status { font-size: 10px; color: #666; margin-bottom: 6px; }
        .status.active { color: #0c7eb0; font-weight: bold; }
        .btn-obtener { width: 100%; padding: 8px; background: #0c7eb0; color: white; border: none; border-radius: 3px; font-size: 12px; font-weight: bold; cursor: pointer; }
        .footer { background: #e0e0e0; text-align: center; padding: 8px 10px; font-size: 8px; color: #666; margin-top: 8px; position: relative; }
        .footer .disclaimer { max-width: 700px; margin: 0 auto; line-height: 1.4; }
        .footer .firma { position: absolute; right: 6px; bottom: 3px; font-size: 8px; color: #bbb; letter-spacing: 1px; opacity: 0.6; }
        #resultados { margin-top: 6px; }
        .grupo { margin-bottom: 12px; }
        .grupo-titulo { font-size: 12px; font-weight: bold; color: #0c3c7d; margin: 12px 0 6px 0; border-bottom: 2px solid #0c3c7d; padding-bottom: 3px; }
        .resultado { background: white; border-radius: 6px; padding: 8px; margin-bottom: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .resultado-cap { font-size: 12px; font-weight: bold; margin-bottom: 6px; }
        .resultado-cap.oe { color: #0c7eb0; }
        .resultado-cap.eo { color: #ff9800; }
        .resultado-msg { font-size: 11px; color: #ff9800; padding: 18px; text-align: center; }
        .resultado img { width: 100%; height: auto; display: none; border-radius: 4px; }
        .btn-pdf { width: 100%; padding: 10px; margin: 4px 0 8px 0; background: #c0392b; color: white; border: none; border-radius: 3px; font-size: 12px; font-weight: bold; cursor: pointer; }
        .btn-pdf:hover { background: #a93226; }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
</head>
<body>
    <div class="header">
        <h1>GRAMET - JetSMART | Cruces de Cordillera | <span id="flHeader">FL250</span></h1>
    </div>

    <div class="container">
        <div class="zona-titulo">ZONA NORTE</div>
        <div class="zona-container">
            <div class="columna">
                <div class="columna-titulo oe-titulo"><span>O-E</span><span class="dir-arrow-big">&#8594;</span></div>
                <button class="cruce-btn" data-zona="Norte" data-codigo="SCAT_SANC" data-nombre="GEKAL (O-&gt;E)" onclick="seleccionar(this)">GEKAL</button>
                <button class="cruce-btn" data-zona="Norte" data-codigo="SCSE_SANU" data-nombre="MIBAS (O-&gt;E)" onclick="seleccionar(this)">MIBAS</button>
                <button class="cruce-btn" data-zona="Norte" data-codigo="SCVM_SANU" data-nombre="GUVOL (O-&gt;E)" onclick="seleccionar(this)">GUVOL</button>
            </div>
            <div class="columna">
                <div class="columna-titulo eo-titulo"><span class="dir-arrow-big">&#8592;</span><span>E-O</span></div>
                <button class="cruce-btn" data-zona="Norte" data-codigo="SANC_SCAT" data-nombre="GEKAL (E-&gt;O)" onclick="seleccionar(this)">GEKAL</button>
                <button class="cruce-btn" data-zona="Norte" data-codigo="SANU_SCSE" data-nombre="MIBAS (E-&gt;O)" onclick="seleccionar(this)">MIBAS</button>
                <button class="cruce-btn" data-zona="Norte" data-codigo="SANU_SCVM" data-nombre="ASIMO (E-&gt;O)" onclick="seleccionar(this)">ASIMO</button>
                <button class="cruce-btn" data-zona="Norte" data-codigo="SAME_SCVM" data-nombre="UMKAL (E-&gt;O)" onclick="seleccionar(this)">UMKAL</button>
            </div>
        </div>

        <div class="zona-titulo">ZONA SUR</div>
        <div class="zona-container">
            <div class="columna">
                <div class="columna-titulo oe-titulo"><span>O-E</span><span class="dir-arrow-big">&#8594;</span></div>
                <button class="cruce-btn" data-zona="Sur" data-codigo="SCEL_SAMR" data-nombre="NEBEG (O-&gt;E)" onclick="seleccionar(this)">NEBEG</button>
                <button class="cruce-btn" data-zona="Sur" data-codigo="SCRG_SAME" data-nombre="ALBAL (O-&gt;E)" onclick="seleccionar(this)">ALBAL</button>
                <button class="cruce-btn" data-zona="Sur" data-codigo="SCIC_SAMM" data-nombre="ANKON (O-&gt;E)" onclick="seleccionar(this)">ANKON</button>
            </div>
            <div class="columna">
                <div class="columna-titulo eo-titulo"><span class="dir-arrow-big">&#8592;</span><span>E-O</span></div>
                <button class="cruce-btn" data-zona="Sur" data-codigo="SAMM_SCIC" data-nombre="ANKON (E-&gt;O)" onclick="seleccionar(this)">ANKON</button>
            </div>
        </div>

        <div class="controles">
            <div class="fila-top">
                <div class="ctrl-grupo">
                    <span class="control-label">FL:</span>
                    <select id="flSelect" class="fl-select" onchange="setFL()"></select>
                </div>
                <div class="ctrl-grupo">
                    <span class="control-label">Manual:</span>
                    <input type="number" id="horasManual" class="manual-input" value="0" min="0" max="24">
                </div>
            </div>
            <label class="control-label">Horas:</label>
            <div class="horas-botones">
                <button class="hora-btn" onclick="setHoras(0)">0</button>
                <button class="hora-btn" onclick="setHoras(1)">1</button>
                <button class="hora-btn" onclick="setHoras(2)">2</button>
                <button class="hora-btn" onclick="setHoras(3)">3</button>
                <button class="hora-btn" onclick="setHoras(4)">4</button>
                <button class="hora-btn" onclick="setHoras(5)">5</button>
                <button class="hora-btn" onclick="setHoras(6)">6</button>
                <button class="hora-btn" onclick="setHoras(8)">8</button>
                <button class="hora-btn" onclick="setHoras(10)">10</button>
                <button class="hora-btn" onclick="setHoras(12)">12</button>
                <button class="hora-btn" onclick="setHoras(24)">24</button>
            </div>
            <div class="status" id="status">Selecciona uno o m&aacute;s cruces</div>
            <button class="btn-obtener" onclick="obtenerGramet()">Obtener GRAMET</button>
        </div>

        <div id="resultados"></div>

        <button class="btn-pdf" onclick="descargarPDF()">Descargar PDF</button>
    </div>

    <div class="footer">
        <div class="disclaimer">La informaci&oacute;n presentada es de car&aacute;cter referencial. Es responsabilidad del piloto y del despachador verificar su vigencia y autenticidad en las fuentes oficiales antes de su uso operacional.</div>
        <div class="firma">JBOZ</div>
    </div>

    <script>
    // Lista de cruces seleccionados: {codigo, nombre, zona, sentido, btn}
    var seleccionados = [];
    var cola = [];      // imagenes por cargar, en orden
    var idxCarga = 0;

    // Poblar el selector de nivel de vuelo (FL200 a FL400) y helpers
    (function initFL() {
        var sel = document.getElementById('flSelect');
        for (var fl = 200; fl <= 400; fl += 10) {
            var opt = document.createElement('option');
            opt.value = String(fl);
            opt.textContent = 'FL' + fl;
            if (fl === 250) opt.selected = true;
            sel.appendChild(opt);
        }
    })();

    function getFL() {
        return document.getElementById('flSelect').value;
    }

    function setFL() {
        document.getElementById('flHeader').textContent = 'FL' + getFL();
    }

    function seleccionar(btn) {
        var codigo = btn.getAttribute('data-codigo');
        var nombre = btn.getAttribute('data-nombre');
        var zona = btn.getAttribute('data-zona');
        var sentido = (nombre.indexOf('O->E') > -1) ? 'oe' : 'eo';

        // Buscar si ya estaba seleccionado
        var idx = -1;
        for (var i = 0; i < seleccionados.length; i++) {
            if (seleccionados[i].btn === btn) { idx = i; break; }
        }

        if (idx > -1) {
            // Deseleccionar
            seleccionados.splice(idx, 1);
            btn.classList.remove('selected-oe', 'selected-eo');
        } else {
            // Seleccionar
            seleccionados.push({codigo: codigo, nombre: nombre, zona: zona, sentido: sentido, btn: btn});
            btn.classList.add(sentido === 'oe' ? 'selected-oe' : 'selected-eo');
        }

        actualizarStatus();
    }

    function actualizarStatus() {
        var s = document.getElementById('status');
        if (seleccionados.length === 0) {
            s.textContent = 'Selecciona uno o más cruces';
            s.classList.remove('active');
        } else {
            s.textContent = seleccionados.length + ' cruce(s) seleccionado(s)';
            s.classList.add('active');
        }
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
        if (seleccionados.length === 0) {
            alert('Selecciona al menos un cruce');
            return;
        }
        var horas = document.getElementById('horasManual').value;
        var fl = getFL();
        var cont = document.getElementById('resultados');
        cont.innerHTML = '';
        cola = [];
        idxCarga = 0;

        // Agrupar por zona: Norte primero, luego Sur
        var orden = ['Norte', 'Sur'];
        for (var z = 0; z < orden.length; z++) {
            var zona = orden[z];
            var delZona = seleccionados.filter(function(x) { return x.zona === zona; });
            if (delZona.length === 0) continue;

            var grupo = document.createElement('div');
            grupo.className = 'grupo';

            var titulo = document.createElement('div');
            titulo.className = 'grupo-titulo';
            titulo.textContent = 'ZONA ' + zona.toUpperCase();
            grupo.appendChild(titulo);

            for (var i = 0; i < delZona.length; i++) {
                var it = delZona[i];

                var bloque = document.createElement('div');
                bloque.className = 'resultado';

                var cap = document.createElement('div');
                cap.className = 'resultado-cap ' + it.sentido;
                cap.textContent = it.nombre.replace('->', '\u2192') + '  ·  +' + horas + 'h  ·  FL' + fl;
                bloque.appendChild(cap);

                var msg = document.createElement('div');
                msg.className = 'resultado-msg';
                msg.textContent = 'En cola...';
                bloque.appendChild(msg);

                var img = document.createElement('img');
                img.setAttribute('data-src',
                    '/gramet?icao=' + encodeURIComponent(it.codigo) +
                    '&horas=' + encodeURIComponent(horas) +
                    '&fl=' + encodeURIComponent(fl));
                (function(imgEl, msgEl) {
                    imgEl.onload = function() {
                        msgEl.style.display = 'none';
                        imgEl.style.display = 'block';
                        cargarSiguiente();
                    };
                    imgEl.onerror = function() {
                        msgEl.textContent = 'No se pudo generar. Reintenta más tarde.';
                        cargarSiguiente();
                    };
                })(img, msg);
                bloque.appendChild(img);

                grupo.appendChild(bloque);
                cola.push({img: img, msg: msg});
            }
            cont.appendChild(grupo);
        }

        // Arrancar la carga secuencial
        cargarActual();
    }

    function cargarActual() {
        if (idxCarga >= cola.length) return;
        var item = cola[idxCarga];
        item.msg.textContent = 'Generando GRAMET... (OGIMET puede tardar unos segundos)';
        item.img.src = item.img.getAttribute('data-src');
    }

    function cargarSiguiente() {
        idxCarga++;
        cargarActual();
    }

    // ---- Descarga en PDF (client-side, funciona en PC y movil) ----
    function imgADataURL(img) {
        var canvas = document.createElement('canvas');
        canvas.width = img.naturalWidth;
        canvas.height = img.naturalHeight;
        var ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0);
        return canvas.toDataURL('image/png');
    }

    function descargarPDF() {
        var grupos = document.querySelectorAll('#resultados .grupo');
        if (grupos.length === 0) {
            alert('Primero genera al menos un GRAMET.');
            return;
        }

        // Verificar que no haya ninguno todavia generandose
        var pendiente = false;
        document.querySelectorAll('#resultados .resultado').forEach(function(res) {
            var img = res.querySelector('img');
            var msg = res.querySelector('.resultado-msg');
            var enProceso = msg && msg.style.display !== 'none' &&
                (msg.textContent.indexOf('Generando') > -1 || msg.textContent.indexOf('cola') > -1);
            if (enProceso && (!img || img.naturalWidth === 0)) pendiente = true;
        });
        if (pendiente) {
            alert('Espera a que terminen de generarse todos los GRAMET antes de descargar.');
            return;
        }

        var jsPDFctor = window.jspdf ? window.jspdf.jsPDF : null;
        if (!jsPDFctor) {
            alert('No se pudo cargar el generador de PDF. Revisa tu conexión e intenta de nuevo.');
            return;
        }

        // Recopilar los GRAMET generados, en orden, con su zona
        var items = [];
        grupos.forEach(function(grupo) {
            var gt = grupo.querySelector('.grupo-titulo');
            var zona = gt ? gt.textContent : '';
            grupo.querySelectorAll('.resultado').forEach(function(res) {
                var img = res.querySelector('img');
                if (img && img.naturalWidth > 0) {
                    var cap = res.querySelector('.resultado-cap');
                    items.push({
                        zona: zona,
                        // Fuente estandar del PDF: flecha unicode -> ASCII
                        texto: (cap ? cap.textContent : '').replace(/\u2192/g, '->'),
                        esOE: cap && cap.classList.contains('oe'),
                        img: img
                    });
                }
            });
        });
        if (items.length === 0) {
            alert('No hay GRAMET generados para exportar.');
            return;
        }

        var doc = new jsPDFctor({ orientation: 'landscape', unit: 'mm', format: 'a4' });
        var pageW = 297, pageH = 210, margin = 12;
        var contentW = pageW - margin * 2;
        var ahora = new Date();
        var y = 14;

        // ---- Encabezado en la PRIMERA hoja, unido a la primera imagen ----
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(13);
        doc.setTextColor(12, 60, 125);
        doc.text('GRAMET - JetSMART | Cruces de Cordillera', margin, y);
        y += 5;
        doc.setFont('helvetica', 'normal');
        doc.setFontSize(8);
        doc.setTextColor(120);
        doc.text('Generado: ' + ahora.toLocaleString(), margin, y);
        y += 8;

        // ---- Un GRAMET por hoja (el primero comparte hoja con el encabezado) ----
        items.forEach(function(it, idx) {
            if (idx > 0) { doc.addPage(); y = 14; }
            var esUltimo = (idx === items.length - 1);

            doc.setFont('helvetica', 'normal');
            doc.setFontSize(9);
            doc.setTextColor(12, 60, 125);
            doc.text(it.zona, margin, y);
            y += 6;

            doc.setFont('helvetica', 'bold');
            doc.setFontSize(12);
            if (it.esOE) doc.setTextColor(12, 126, 176); else doc.setTextColor(255, 152, 0);
            doc.text(it.texto, margin, y);
            y += 5;

            var w = contentW;
            var h = contentW * (it.img.naturalHeight / it.img.naturalWidth);
            // En el ultimo, reservar espacio abajo para el texto legal + firma
            var reserva = esUltimo ? 26 : 14;
            var maxH = pageH - y - reserva;
            if (h > maxH) { h = maxH; w = h * (it.img.naturalWidth / it.img.naturalHeight); }
            var x = margin + (contentW - w) / 2;
            doc.addImage(imgADataURL(it.img), 'PNG', x, y, w, h);
            y += h + 6;
        });

        // ---- Texto legal integrado tras el ultimo GRAMET, en la misma pagina ----
        var discEl = document.querySelector('.footer .disclaimer');
        var disc = discEl ? discEl.textContent : '';
        doc.setFont('helvetica', 'italic');
        doc.setFontSize(8);
        doc.setTextColor(120);
        var lineas = doc.splitTextToSize(disc, contentW);
        doc.text(lineas, margin, y);

        doc.setFont('helvetica', 'normal');
        doc.setFontSize(8);
        doc.setTextColor(180);
        doc.text('JBOZ', pageW - margin, pageH - 8, { align: 'right' });

        var f = ahora.getFullYear() +
                ('0' + (ahora.getMonth() + 1)).slice(-2) +
                ('0' + ahora.getDate()).slice(-2);
        doc.save('GRAMET_JetSMART_' + f + '.pdf');
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
    fl = request.args.get('fl', '250')
    # Validar nivel de vuelo: entero entre 200 y 400; si no, usar 250
    if not (fl.isdigit() and 200 <= int(fl) <= 400):
        fl = '250'

    if not icao:
        abort(400, "Falta el parametro icao")

    tref = int(time.time())  # hora de referencia = ahora (epoch UTC)
    ogimet_url = (
        "https://www.ogimet.com/display_gramet.php"
        f"?icao={icao}&hini={horas}&tref={tref}&hfin={horas}"
        f"&fl={fl}&enviar=Enviar"
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
