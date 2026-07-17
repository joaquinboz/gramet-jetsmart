#!/usr/bin/env python3
from flask import Flask, render_template_string, request, jsonify
import requests
import time

app = Flask(__name__)

DATOS_CRUCES = {
    "GEKAL": {"O→E": "SCAT_SANC", "E→O": "SANC_SCAT", "zona": "ZONA NORTE"},
    "MIBAS": {"O→E": "SCSE_SANU", "E→O": "SANU_SCSE", "zona": "ZONA NORTE"},
    "GUVOL": {"O→E": "SCVM_SANU", "E→O": None, "zona": "ZONA NORTE"},
    "ASIMO": {"O→E": None, "E→O": "SANU_SCVM", "zona": "ZONA NORTE"},
    "UMKAL": {"O→E": None, "E→O": "SAME_SCVM", "zona": "ZONA NORTE"},
    "NEBEG": {"O→E": "SCEL_SAMR", "E→O": None, "zona": "ZONA SUR"},
    "ALBAL": {"O→E": "SCRG_SAME", "E→O": None, "zona": "ZONA SUR"},
    "ANKON": {"O→E": "SCIC_SAMM", "E→O": "SAMM_SCIC", "zona": "ZONA SUR"},
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
        
        .columna { }
        .columna.oe { border-left: 4px solid #0c7eb0; }
        .columna.eo { border-left: 4px solid #ff9800; }
        
        .columna-titulo { font-weight: bold; margin-bottom: 10px; padding-left: 10px; }
        .columna.oe .columna-titulo { color: #0c7eb0; }
        .columna.eo .columna-titulo { color: #ff9800; }
        
        .cruce-btn { width: 100%; padding: 12px; margin-bottom: 8px; border: 1px solid #ddd; border-radius: 4px; background: white; cursor: pointer; text-align: left; transition: all 0.2s; }
        .cruce-btn:hover { background: #f9f9f9; border-color: #999; }
        .cruce-btn.active { background: #0c7eb0; color: white; border-color: #0c7eb0; }
        .cruce-btn.active.eo { background: #ff9800; border-color: #ff9800; }
        
        .controles { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }
        
        .horas-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 8px; margin-bottom: 15px; }
        .hora-btn { padding: 10px; border: 1px solid #ddd; border-radius: 4px; background: white; cursor: pointer; text-align: center; transition: all 0.2s; }
        .hora-btn:hover { border-color: #0c7eb0; }
        .hora-btn.active { background: #0c7eb0; color: white; border-color: #0c7eb0; }
        
        .manual-input { display: flex; gap: 10px; align-items: center; margin-bottom: 15px; }
        .manual-input input { padding: 8px 12px; border: 1px solid #ddd; border-radius: 4px; width: 60px; }
        
        .btn-obtener { width: 100%; padding: 14px; background: #0c7eb0; color: white; border: none; border-radius: 4px; font-size: 16px; cursor: pointer; transition: all 0.2s; }
        .btn-obtener:hover { background: #0a5a8f; }
        .btn-obtener:disabled { background: #ccc; cursor: not-allowed; }
        
        .seleccionado { padding: 12px; background: #e3f2fd; border-left: 4px solid #0c7eb0; margin-bottom: 15px; border-radius: 4px; }
        .seleccionado strong { color: #0c7eb0; }
        
        .estado { text-align: center; margin-top: 10px; min-height: 30px; }
        .estado.success { color: #4caf50; }
        .estado.error { color: #f44336; }
        .estado.loading { color: #ff9800; }
        
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
                    <button class="cruce-btn" onclick="seleccionar('GEKAL', 'O→E')">GEKAL</button>
                    <button class="cruce-btn" onclick="seleccionar('MIBAS', 'O→E')">MIBAS</button>
                    <button class="cruce-btn" onclick="seleccionar('GUVOL', 'O→E')">GUVOL</button>
                </div>
                <div class="columna eo">
                    <div class="columna-titulo">← E→O (Naranja)</div>
                    <button class="cruce-btn" onclick="seleccionar('GEKAL', 'E→O')">GEKAL</button>
                    <button class="cruce-btn" onclick="seleccionar('MIBAS', 'E→O')">MIBAS</button>
                    <button class="cruce-btn" onclick="seleccionar('ASIMO', 'E→O')">ASIMO</button>
                    <button class="cruce-btn" onclick="seleccionar('UMKAL', 'E→O')">UMKAL</button>
                </div>
            </div>
        </div>
        
        <div class="zona">
            <div class="zona-title">🔽 ZONA SUR</div>
            <div class="columnas">
                <div class="columna oe">
                    <div class="columna-titulo">→ O→E (Azul)</div>
                    <button class="cruce-btn" onclick="seleccionar('NEBEG', 'O→E')">NEBEG</button>
                    <button class="cruce-btn" onclick="seleccionar('ALBAL', 'O→E')">ALBAL</button>
                    <button class="cruce-btn" onclick="seleccionar('ANKON', 'O→E')">ANKON</button>
                </div>
                <div class="columna eo">
                    <div class="columna-titulo">← E→O (Naranja)</div>
                    <button class="cruce-btn" onclick="seleccionar('ANKON', 'E→O')">ANKON</button>
                </div>
            </div>
        </div>
        
        <div class="controles">
            <div>
                <strong>⏰ Horas:</strong>
                <div class="horas-grid">
                    <button class="hora-btn" onclick="seleccionarHora(0)">0</button>
                    <button class="hora-btn" onclick="seleccionarHora(1)">1</button>
                    <button class="hora-btn" onclick="seleccionarHora(2)">2</button>
                    <button class="hora-btn" onclick="seleccionarHora(3)">3</button>
                    <button class="hora-btn" onclick="seleccionarHora(4)">4</button>
                    <button class="hora-btn" onclick="seleccionarHora(5)">5</button>
                    <button class="hora-btn" onclick="seleccionarHora(6)">6</button>
                </div>
            </div>
            
            <div class="manual-input">
                <label><strong>Manual:</strong></label>
                <input type="number" id="horasManual" min="0" max="24" value="3">
            </div>
            
            <div id="seleccionado" class="seleccionado" style="display: none;">
                <strong id="seleccionadoTexto"></strong>
            </div>
            
            <button class="btn-obtener" onclick="obtenerGramet()">🚀 Obtener GRAMET</button>
            
            <div id="estado" class="estado"></div>
        </div>
    </div>
    
    <script>
        let crucesSeleccionados = {};
        let horasSeleccionadas = null;
        
        function seleccionar(cruce, direccion) {
            const key = cruce + '_' + direccion;
            crucesSeleccionados[key] = { cruce, direccion };
            
            // Actualizar UI
            document.querySelectorAll('.cruce-btn').forEach(btn => btn.classList.remove('active'));
            Object.values(crucesSeleccionados).forEach(({ cruce: c, direccion: d }) => {
                document.querySelectorAll('.cruce-btn').forEach(btn => {
                    if (btn.textContent.trim() === c) {
                        btn.classList.add('active');
                    }
                });
            });
            
            actualizarSeleccionado();
        }
        
        function seleccionarHora(hora) {
            horasSeleccionadas = hora;
            document.querySelectorAll('.hora-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
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
        
        function obtenerGramet() {
            if (Object.keys(crucesSeleccionados).length === 0 || horasSeleccionadas === null) {
                alert('Selecciona un cruce y horas');
                return;
            }
            
            const btn = document.querySelector('.btn-obtener');
            btn.disabled = true;
            document.getElementById('estado').className = 'estado loading';
            document.getElementById('estado').textContent = '⏳ Obteniendo GRAMET...';
            
            const solicitudes = Object.values(crucesSeleccionados).map(({ cruce, direccion }) => {
                return fetch('/obtener-gramet', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        gramet: cruce,
                        nombre: cruce + ' (' + direccion + ')',
                        horas: horasSeleccionadas
                    })
                });
            });
            
            Promise.all(solicitudes)
                .then(responses => Promise.all(responses.map(r => r.json())))
                .then(datos => {
                    const exitos = datos.filter(d => d.success).length;
                    document.getElementById('estado').className = 'estado success';
                    document.getElementById('estado').textContent = `✓ ${exitos}/${datos.length} GRAMET obtenidos`;
                    btn.disabled = false;
                    setTimeout(() => { document.getElementById('estado').textContent = ''; }, 3000);
                })
                .catch(err => {
                    document.getElementById('estado').className = 'estado error';
                    document.getElementById('estado').textContent = '❌ Error: ' + err.message;
                    btn.disabled = false;
                });
        }
    </script>
</body>
</html>'''
    return render_template_string(html)

@app.route('/obtener-gramet', methods=['POST'])
def obtener_gramet():
    try:
        data = request.json
        gramet = data.get('gramet')
        nombre = data.get('nombre')
        horas = data.get('horas')
        
        print(f"\n[{time.strftime('%H:%M:%S')}] Solicitud GRAMET: {nombre}")
        
        # Hacer solicitud HTTP a OGIMET
        url = 'https://www.ogimet.com/cgi-bin/gramet_aero'
        params = {
            'stids': gramet,
            'hours': horas,
            'min': horas,
            'flevel': '250'
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            if response.status_code == 200:
                print(f"✓ GRAMET obtenido: {nombre}")
                return jsonify({'success': True, 'message': nombre, 'url': response.url})
            else:
                return jsonify({'success': False, 'message': f'Error HTTP {response.status_code}'})
        except requests.exceptions.RequestException as e:
            return jsonify({'success': False, 'message': f'Error: {str(e)}'})
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    print(f"\n✈️ GRAMET Web - http://localhost:{port}\n")
    app.run(debug=False, host='0.0.0.0', port=port, threaded=True)
