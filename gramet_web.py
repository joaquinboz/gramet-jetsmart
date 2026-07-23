#!/usr/bin/env python3
from flask import Flask, render_template_string, request, jsonify
import base64
import time

app = Flask(__name__)

# Ruta OACI para cada punto de cruce y dirección (del documento Cruces de Cordillera)
RUTAS_CRUCES = {
    ("GEKAL", "O→E"): "SCAT_SANC",
    ("GEKAL", "E→O"): "SANC_SCAT",
    ("MIBAS", "O→E"): "SCSE_SANU",
    ("MIBAS", "E→O"): "SANU_SCSE",
    ("GUVOL", "O→E"): "SCVM_SANU",
    ("ASIMO", "E→O"): "SANU_SCVM",
    ("UMKAL", "E→O"): "SAME_SCVM",
    ("NEBEG", "O→E"): "SCEL_SAMR",
    ("ALBAL", "O→E"): "SCRG_SAME",
    ("ANKON", "O→E"): "SCIC_SAMM",
    ("ANKON", "E→O"): "SAMM_SCIC",
}

@app.route('/')
def index():
    html = '''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GRAMET - JetSMART</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f5f5f5; padding: 20px; }
        .container { max-width: 900px; margin: 0 auto; }
        .header { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .header h1 { font-size: 24px; color: #0c7eb0; }
        .header p { color: #666; margin-top: 5px; }
        
        .zona { background: white; padding: 20px; margin-bottom: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .zona-title { font-size: 18px; font-weight: bold; color: #0c7eb0; margin-bottom: 15px; }
        
        .columnas { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        
        .columna.oe { border-left: 4px solid #0c7eb0; }
        .columna.eo { border-left: 4px solid #ff9800; }
        
        .columna-titulo { font-weight: bold; margin-bottom: 10px; padding-left: 10px; }
        .columna.oe .columna-titulo { color: #0c7eb0; }
        .columna.eo .columna-titulo { color: #ff9800; }
        
        .cruce-btn { width: 100%; padding: 12px; margin-bottom: 8px; border: 1px solid #ddd; border-radius: 4px; background: white; cursor: pointer; text-align: left; transition: all 0.2s; }
        .cruce-btn:hover { background: #f9f9f9; border-color: #999; }
        .columna.oe .cruce-btn.active { background: #0c7eb0; color: white; border-color: #0c7eb0; }
        .columna.eo .cruce-btn.active { background: #ff9800; color: white; border-color: #ff9800; }
        
        .controles { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }
        
        .horas-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 8px; margin-bottom: 15px; }
        .hora-btn { padding: 10px; border: 1px solid #ddd; border-radius: 4px; background: white; cursor: pointer; text-align: center; transition: all 0.2s; }
        .hora-btn:hover { border-color: #0c7eb0; }
        .hora-btn.active { background: #0c7eb0; color: white; border-color: #0c7eb0; }
        
        .btn-obtener { width: 100%; padding: 14px; background: #0c7eb0; color: white; border: none; border-radius: 4px; font-size: 16px; cursor: pointer; transition: all 0.2s; }
        .btn-obtener:hover { background: #0a5a8f; }
        .btn-obtener:disabled { background: #ccc; cursor: not-allowed; }
        
        .seleccionado { padding: 12px; background: #e3f2fd; border-left: 4px solid #0c7eb0; margin-bottom: 15px; border-radius: 4px; }
        .seleccionado strong { color: #0c7eb0; }
        
        .estado { text-align: center; margin-top: 10px; min-height: 30px; }
        .estado.success { color: #4caf50; }
        .estado.error { color: #f44336; }
        .estado.loading { color: #ff9800; }
        
        .resultados { margin-top: 20px; }
        .btn-pdf { width: 100%; padding: 14px; margin-top: 10px; background: #4caf50; color: white; border: none; border-radius: 4px; font-size: 16px; cursor: pointer; transition: all 0.2s; }
        .btn-pdf:hover { background: #3d8b40; }
        .btn-pdf:disabled { background: #ccc; cursor: not-allowed; }
        .resultado { background: white; padding: 15px; border-radius: 8px; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .resultado h3 { color: #0c7eb0; margin-bottom: 10px; }
        .resultado img { max-width: 100%; border: 1px solid #ddd; border-radius: 4px; cursor: pointer; }
        .resultado .hint { color: #999; font-size: 12px; margin-top: 5px; }
        
        @media (max-width: 600px) {
            .columnas { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✈️ GRAMET - JetSMART</h1>
            <p>Cruces de Cordillera | FL250</p>
        </div>
        
        <div class="zona">
            <div class="zona-title">🔼 ZONA NORTE</div>
            <div class="columnas">
                <div class="columna oe">
                    <div class="columna-titulo">→ O→E (Azul)</div>
                    <button class="cruce-btn" onclick="seleccionar(this, 'GEKAL', 'O→E')">GEKAL</button>
                    <button class="cruce-btn" onclick="seleccionar(this, 'MIBAS', 'O→E')">MIBAS</button>
                    <button class="cruce-btn" onclick="seleccionar(this, 'GUVOL', 'O→E')">GUVOL</button>
                </div>
                <div class="columna eo">
                    <div class="columna-titulo">← E→O (Naranja)</div>
                    <button class="cruce-btn" onclick="seleccionar(this, 'GEKAL', 'E→O')">GEKAL</button>
                    <button class="cruce-btn" onclick="seleccionar(this, 'MIBAS', 'E→O')">MIBAS</button>
                    <button class="cruce-btn" onclick="seleccionar(this, 'ASIMO', 'E→O')">ASIMO</button>
                    <button class="cruce-btn" onclick="seleccionar(this, 'UMKAL', 'E→O')">UMKAL</button>
                </div>
            </div>
        </div>
        
        <div class="zona">
            <div class="zona-title">🔽 ZONA SUR</div>
            <div class="columnas">
                <div class="columna oe">
                    <div class="columna-titulo">→ O→E (Azul)</div>
                    <button class="cruce-btn" onclick="seleccionar(this, 'NEBEG', 'O→E')">NEBEG</button>
                    <button class="cruce-btn" onclick="seleccionar(this, 'ALBAL', 'O→E')">ALBAL</button>
                    <button class="cruce-btn" onclick="seleccionar(this, 'ANKON', 'O→E')">ANKON</button>
                </div>
                <div class="columna eo">
                    <div class="columna-titulo">← E→O (Naranja)</div>
                    <button class="cruce-btn" onclick="seleccionar(this, 'ANKON', 'E→O')">ANKON</button>
                </div>
            </div>
        </div>
        
        <div class="controles">
            <div>
                <strong>⏰ Horas:</strong>
                <div class="horas-grid">
                    <button class="hora-btn" onclick="seleccionarHora(event, 0)">0</button>
                    <button class="hora-btn" onclick="seleccionarHora(event, 1)">1</button>
                    <button class="hora-btn" onclick="seleccionarHora(event, 2)">2</button>
                    <button class="hora-btn" onclick="seleccionarHora(event, 3)">3</button>
                    <button class="hora-btn" onclick="seleccionarHora(event, 4)">4</button>
                    <button class="hora-btn" onclick="seleccionarHora(event, 5)">5</button>
                    <button class="hora-btn" onclick="seleccionarHora(event, 6)">6</button>
                </div>
            </div>
            
            <div id="seleccionado" class="seleccionado" style="display: none;">
                <strong id="seleccionadoTexto"></strong>
            </div>
            
            <button class="btn-obtener" onclick="obtenerGramet()">🚀 Obtener GRAMET</button>
            
            <div id="estado" class="estado"></div>
        </div>
        
        <div id="resultados" class="resultados"></div>
        
        <div id="pdfContenedor" style="display: none;">
            <button class="btn-pdf" onclick="descargarPDF()">📥 Descargar PDF</button>
        </div>
    </div>
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
    <script>
        let crucesSeleccionados = {};
        let horasSeleccionadas = null;
        let grametsObtenidos = [];
        
        function seleccionar(btn, cruce, direccion) {
            const key = cruce + '_' + direccion;
            
            if (crucesSeleccionados[key]) {
                delete crucesSeleccionados[key];
                btn.classList.remove('active');
            } else {
                crucesSeleccionados[key] = { cruce, direccion };
                btn.classList.add('active');
            }
            
            actualizarSeleccionado();
        }
        
        function seleccionarHora(ev, hora) {
            horasSeleccionadas = hora;
            document.querySelectorAll('.hora-btn').forEach(btn => btn.classList.remove('active'));
            ev.target.classList.add('active');
            actualizarSeleccionado();
        }
        
        function actualizarSeleccionado() {
            const textos = Object.entries(crucesSeleccionados).map(([_, { cruce, direccion }]) => `${cruce} (${direccion})`);
            if (textos.length > 0 && horasSeleccionadas !== null) {
                document.getElementById('seleccionado').style.display = 'block';
                document.getElementById('seleccionadoTexto').textContent = `✓ Seleccionado: ${textos.join(', ')} | ${horasSeleccionadas}h`;
            } else {
                document.getElementById('seleccionado').style.display = 'none';
            }
        }
        
        async function obtenerGramet() {
            if (Object.keys(crucesSeleccionados).length === 0 || horasSeleccionadas === null) {
                document.getElementById('estado').className = 'estado error';
                document.getElementById('estado').textContent = '⚠️ Selecciona un cruce y horas';
                return;
            }
            
            const btn = document.querySelector('.btn-obtener');
            const estado = document.getElementById('estado');
            const resultados = document.getElementById('resultados');
            
            btn.disabled = true;
            resultados.innerHTML = '';
            grametsObtenidos = [];
            document.getElementById('pdfContenedor').style.display = 'none';
            
            const cruces = Object.values(crucesSeleccionados);
            let exitos = 0;
            
            for (let i = 0; i < cruces.length; i++) {
                const { cruce, direccion } = cruces[i];
                const nombre = cruce + ' (' + direccion + ')';
                
                estado.className = 'estado loading';
                estado.textContent = `⏳ Obteniendo ${nombre}... (${i+1}/${cruces.length}) - puede tardar ~30 seg`;
                
                try {
                    const resp = await fetch('/obtener-gramet', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            gramet: cruce,
                            direccion: direccion,
                            nombre: nombre,
                            horas: horasSeleccionadas
                        })
                    });
                    const data = await resp.json();
                    
                    if (data.success && data.imagen) {
                        exitos++;
                        grametsObtenidos.push({
                            titulo: `${nombre} | ${horasSeleccionadas}h | FL250`,
                            imagen: data.imagen
                        });
                        const div = document.createElement('div');
                        div.className = 'resultado';
                        div.innerHTML = `
                            <h3>📊 ${nombre} | ${horasSeleccionadas}h | FL250</h3>
                            <img src="data:image/png;base64,${data.imagen}" onclick="abrirImagen(this)" title="Click para ampliar">
                            <div class="hint">Click en la imagen para ampliar</div>
                        `;
                        resultados.appendChild(div);
                    } else {
                        const div = document.createElement('div');
                        div.className = 'resultado';
                        div.innerHTML = `<h3>❌ ${nombre}</h3><p>${data.message || 'Error desconocido'}</p>`;
                        resultados.appendChild(div);
                    }
                } catch (err) {
                    const div = document.createElement('div');
                    div.className = 'resultado';
                    div.innerHTML = `<h3>❌ ${nombre}</h3><p>${err.message}</p>`;
                    resultados.appendChild(div);
                }
            }
            
            estado.className = exitos > 0 ? 'estado success' : 'estado error';
            estado.textContent = exitos > 0 ? `✓ ${exitos}/${cruces.length} GRAMET obtenidos` : '❌ No se pudo obtener GRAMET';
            btn.disabled = false;
            
            // Mostrar botón de descarga PDF solo si hay al menos un GRAMET
            document.getElementById('pdfContenedor').style.display = exitos > 0 ? 'block' : 'none';
        }
        
        function abrirImagen(img) {
            const win = window.open('');
            win.document.write('<img src="' + img.src + '" style="max-width:100%">');
        }
        
        // Cargar una imagen base64 y devolver sus dimensiones reales
        function cargarImagen(base64) {
            return new Promise((resolve) => {
                const img = new Image();
                img.onload = () => resolve(img);
                img.src = 'data:image/png;base64,' + base64;
            });
        }
        
        async function descargarPDF() {
            if (grametsObtenidos.length === 0) return;
            
            const btnPdf = document.querySelector('.btn-pdf');
            btnPdf.disabled = true;
            const textoOriginal = btnPdf.textContent;
            btnPdf.textContent = '⏳ Generando PDF...';
            
            try {
                const { jsPDF } = window.jspdf;
                const pdf = new jsPDF({ orientation: 'landscape', unit: 'mm', format: 'a4' });
                
                const pageW = pdf.internal.pageSize.getWidth();
                const pageH = pdf.internal.pageSize.getHeight();
                const margin = 10;
                const maxW = pageW - margin * 2;
                let y = margin;
                let primera = true;
                
                for (const g of grametsObtenidos) {
                    const img = await cargarImagen(g.imagen);
                    // Ajustar al ancho de página, manteniendo proporción
                    const ratio = img.height / img.width;
                    const w = maxW;
                    const h = w * ratio;
                    
                    // Alto del título
                    const tituloH = 8;
                    const bloqueH = tituloH + h + 6;
                    
                    // Si no cabe en la página actual, crear una nueva
                    if (!primera && y + bloqueH > pageH - margin) {
                        pdf.addPage();
                        y = margin;
                    }
                    primera = false;
                    
                    // Título del cruce
                    pdf.setFontSize(11);
                    pdf.setTextColor(12, 126, 176);
                    pdf.text(g.titulo, margin, y + 5);
                    y += tituloH;
                    
                    // Imagen GRAMET ajustada al ancho
                    pdf.addImage(g.imagen, 'PNG', margin, y, w, h);
                    y += h + 6;
                }
                
                const fecha = new Date().toISOString().slice(0, 10);
                const nombreArchivo = `GRAMET_JetSMART_${fecha}.pdf`;
                
                // Detectar iOS (Safari bloquea descargas automáticas)
                const esIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
                if (esIOS) {
                    // Abrir en pestaña nueva para que el usuario lo guarde manualmente
                    window.open(pdf.output('bloburl'), '_blank');
                } else {
                    pdf.save(nombreArchivo);
                }
            } catch (err) {
                alert('Error al generar el PDF: ' + err.message);
            } finally {
                btnPdf.disabled = false;
                btnPdf.textContent = textoOriginal;
            }
        }
    </script>
</body>
</html>'''
    return render_template_string(html)

@app.route('/obtener-gramet', methods=['POST'])
def obtener_gramet():
    try:
        import requests
        from urllib.parse import quote

        data = request.json
        gramet = data.get('gramet')
        direccion = data.get('direccion')
        nombre = data.get('nombre')
        horas = str(data.get('horas'))

        # Convertir punto de cruce a ruta OACI (ej: MIBAS O→E -> "SCSE_SANU")
        ruta = RUTAS_CRUCES.get((gramet, direccion))
        if not ruta:
            return jsonify({'success': False, 'message': f'No hay ruta definida para {gramet} {direccion}'})

        # Endpoint directo de OGIMET: genera el GRAMET solo con parámetros en la URL.
        # icao=ruta, hini=hfin=horas seleccionadas, tref=momento actual (Unix), fl=250
        tref = int(time.time())
        ogimet_url = (
            "https://www.ogimet.com/display_gramet.php"
            f"?icao={quote(ruta)}&hini={horas}&tref={tref}&hfin={horas}&fl=250&enviar=Enviar"
        )
        print(f"\n[{time.strftime('%H:%M:%S')}] {nombre} -> {ruta} ({horas}h) | {ogimet_url}")

        # El servidor actúa de "puente": descarga la imagen desde OGIMET
        # (con reintentos, porque OGIMET tarda en generarla) y la reenvía en base64,
        # así el PDF funciona sin problemas de CORS.
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/120.0 Safari/537.36',
            'Referer': 'https://www.ogimet.com/gramet_aero.phtml'
        }

        img_bytes = None
        ultimo_error = ''
        for intento in range(20):
            try:
                resp = requests.get(ogimet_url, headers=headers, timeout=30)
                content_type = resp.headers.get('content-type', '')
                if resp.status_code == 200 and 'image' in content_type and len(resp.content) > 10000:
                    img_bytes = resp.content
                    break
                ultimo_error = f'HTTP {resp.status_code}, tipo {content_type}, {len(resp.content)} bytes'
            except Exception as e:
                ultimo_error = str(e)
            print(f"GRAMET aún generándose... {intento+1}/20 ({ultimo_error})")
            time.sleep(5)

        if img_bytes is None:
            return jsonify({'success': False, 'message': f'OGIMET no generó la imagen. {ultimo_error}'})

        img_b64 = base64.b64encode(img_bytes).decode('utf-8')
        print(f"✓ GRAMET obtenido: {nombre}")
        return jsonify({'success': True, 'message': nombre, 'imagen': img_b64})

    except Exception as e:
        error_msg = str(e)
        print(f"❌ Error: {error_msg}")
        return jsonify({'success': False, 'message': error_msg})

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    print(f"\n✈️ GRAMET Web - http://localhost:{port}\n")
    app.run(debug=False, host='0.0.0.0', port=port, threaded=True)
