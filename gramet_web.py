#!/usr/bin/env python3
from flask import Flask, render_template_string, request, jsonify
import base64
import time

app = Flask(__name__)

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
    </div>
    
    <script>
        let crucesSeleccionados = {};
        let horasSeleccionadas = null;
        
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
                            nombre: nombre,
                            horas: horasSeleccionadas
                        })
                    });
                    const data = await resp.json();
                    
                    if (data.success && data.imagen) {
                        exitos++;
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
        }
        
        function abrirImagen(img) {
            const win = window.open('');
            win.document.write('<img src="' + img.src + '" style="max-width:100%">');
        }
    </script>
</body>
</html>'''
    return render_template_string(html)

@app.route('/obtener-gramet', methods=['POST'])
def obtener_gramet():
    try:
        from playwright.sync_api import sync_playwright
        
        data = request.json
        gramet = data.get('gramet')
        nombre = data.get('nombre')
        horas = str(data.get('horas'))
        
        print(f"\n[{time.strftime('%H:%M:%S')}] Solicitud: {nombre} - {horas}h")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage"])
            page = browser.new_page()
            
            try:
                # 1. Abrir formulario OGIMET
                page.goto("https://www.ogimet.com/gramet_aero.phtml", timeout=30000)
                page.wait_for_load_state("domcontentloaded")
                
                # 2. Rellenar campos (igual que la app desktop)
                inputs = page.query_selector_all("input[type='text']")
                print(f"Campos encontrados: {len(inputs)}")
                
                if len(inputs) < 3:
                    browser.close()
                    return jsonify({'success': False, 'message': 'Formulario OGIMET no cargó bien'})
                
                # Campo 1: Lugar (GRAMET)
                inputs[0].fill(gramet)
                # Campo 2: Hora inicio
                inputs[1].fill(horas)
                # Campo 3: Hora final
                inputs[2].fill(horas)
                
                # Nivel de vuelo -> 250
                for inp in inputs:
                    val = inp.get_attribute("value")
                    if val in ["100", "250"]:
                        inp.fill("250")
                        break
                
                # 3. Enviar formulario
                page.click("input[type='submit']")
                page.wait_for_load_state("load", timeout=60000)
                
                # 4. Buscar específicamente la imagen del GRAMET
                #    (su ruta contiene 'gramet' o '/tmp/', NO el logo del sitio)
                page.wait_for_selector("img", timeout=30000)
                
                gramet_src = None
                for intento in range(10):
                    for img in page.query_selector_all("img"):
                        src = img.get_attribute("src") or ""
                        if "gramet" in src.lower() or "/tmp/" in src.lower():
                            gramet_src = src
                            break
                    if gramet_src:
                        break
                    time.sleep(3)
                
                if not gramet_src:
                    browser.close()
                    return jsonify({'success': False, 'message': 'No se encontró la imagen GRAMET en la página de resultados'})
                
                from urllib.parse import urljoin
                abs_url = urljoin("https://www.ogimet.com/", gramet_src)
                print(f"Imagen GRAMET: {abs_url}")
                
                # 5. Descargar la imagen (OGIMET tarda en generarla,
                #    reintentar hasta ~2 minutos)
                img_bytes = None
                for intento in range(24):
                    try:
                        resp = page.context.request.get(abs_url)
                        content_type = resp.headers.get("content-type", "")
                        body = resp.body()
                        if resp.ok and "image" in content_type and len(body) > 10000:
                            img_bytes = body
                            break
                    except Exception:
                        pass
                    print(f"GRAMET aún generándose... {intento+1}/24")
                    time.sleep(5)
                
                if img_bytes is None:
                    browser.close()
                    return jsonify({'success': False, 'message': 'OGIMET no generó la imagen a tiempo. Intenta de nuevo en unos minutos.'})
                
                img_b64 = base64.b64encode(img_bytes).decode('utf-8')
                
                browser.close()
                print(f"✓ GRAMET obtenido: {nombre}")
                return jsonify({'success': True, 'message': nombre, 'imagen': img_b64})
                
            except Exception as e:
                browser.close()
                raise e
            
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Error: {error_msg}")
        return jsonify({'success': False, 'message': error_msg})

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    print(f"\n✈️ GRAMET Web - http://localhost:{port}\n")
    app.run(debug=False, host='0.0.0.0', port=port, threaded=True)
