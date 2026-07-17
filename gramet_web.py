#!/usr/bin/env python3
from flask import Flask, render_template_string, request, jsonify
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager

app = Flask(__name__)

# Driver global que se reutiliza entre solicitudes
driver_global = None

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
        .btn-obtener:disabled { background: #999; cursor: not-allowed; }
        .progress { font-size: 10px; color: #ff9800; margin-top: 6px; text-align: center; }
        .progress.success { color: #66b147; }
        .footer { background: #e0e0e0; text-align: center; padding: 8px; font-size: 8px; color: #666; margin-top: 8px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>GRAMET - JetSMART | Cruces de Cordillera | FL250</h1>
    </div>
    
    <div class="container">
        <div class="zona-titulo">🔼 ZONA NORTE</div>
        <div class="zona-container">
            <div class="columna">
                <div class="flecha oe-flecha">→</div>
                <div class="columna-titulo oe-titulo">O→E</div>
                <button class="cruce-btn" data-codigo="SCAT_SANC" data-nombre="GEKAL (O→E)" onclick="seleccionar(this)">GEKAL</button>
                <button class="cruce-btn" data-codigo="SCSE_SANU" data-nombre="MIBAS (O→E)" onclick="seleccionar(this)">MIBAS</button>
                <button class="cruce-btn" data-codigo="SCVM_SANU" data-nombre="GUVOL (O→E)" onclick="seleccionar(this)">GUVOL</button>
            </div>
            <div class="columna">
                <div class="flecha eo-flecha">←</div>
                <div class="columna-titulo eo-titulo">E→O</div>
                <button class="cruce-btn" data-codigo="SANC_SCAT" data-nombre="GEKAL (E→O)" onclick="seleccionar(this)">GEKAL</button>
                <button class="cruce-btn" data-codigo="SANU_SCSE" data-nombre="MIBAS (E→O)" onclick="seleccionar(this)">MIBAS</button>
                <button class="cruce-btn" data-codigo="SANU_SCVM" data-nombre="ASIMO (E→O)" onclick="seleccionar(this)">ASIMO</button>
                <button class="cruce-btn" data-codigo="SAME_SCVM" data-nombre="UMKAL (E→O)" onclick="seleccionar(this)">UMKAL</button>
            </div>
        </div>
        
        <div class="zona-titulo">🔽 ZONA SUR</div>
        <div class="zona-container">
            <div class="columna">
                <div class="flecha oe-flecha">→</div>
                <div class="columna-titulo oe-titulo">O→E</div>
                <button class="cruce-btn" data-codigo="SCEL_SAMR" data-nombre="NEBEG (O→E)" onclick="seleccionar(this)">NEBEG</button>
                <button class="cruce-btn" data-codigo="SCRG_SAME" data-nombre="ALBAL (O→E)" onclick="seleccionar(this)">ALBAL</button>
                <button class="cruce-btn" data-codigo="SCIC_SAMM" data-nombre="ANKON (O→E)" onclick="seleccionar(this)">ANKON</button>
            </div>
            <div class="columna">
                <div class="flecha eo-flecha">←</div>
                <div class="columna-titulo eo-titulo">E→O</div>
                <button class="cruce-btn" data-codigo="SAMM_SCIC" data-nombre="ANKON (E→O)" onclick="seleccionar(this)">ANKON</button>
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
            <button class="btn-obtener" id="btnObtener" onclick="obtenerGramet()">Obtener GRAMET</button>
            <div class="progress" id="progress"></div>
        </div>
    </div>
    
    <div class="footer">
        JetSMART Operations | Auto-relleno OGIMET
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
        
        // Detectar dirección: buscar el patrón específico
        // "E→O" o "E->O" va de Este a Oeste (naranja)
        // "O→E" o "O->E" va de Oeste a Este (azul)
        if (nombre.indexOf('O→E') > -1 || nombre.indexOf('O->E') > -1) {
            btn.classList.add('selected-oe');  // Azul para O→E
        } else if (nombre.indexOf('E→O') > -1 || nombre.indexOf('E->O') > -1) {
            btn.classList.add('selected-eo');  // Naranja para E→O
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
        var btn = document.getElementById('btnObtener');
        var progress = document.getElementById('progress');
        
        btn.disabled = true;
        progress.textContent = 'Cargando...';
        progress.classList.remove('success');
        
        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/obtener-gramet', true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.onload = function() {
            try {
                var data = JSON.parse(xhr.responseText);
                if (data.success) {
                    progress.textContent = '✅ GRAMET obtenido';
                    progress.classList.add('success');
                } else {
                    progress.textContent = 'Error: ' + data.message;
                }
            } catch(e) {
                progress.textContent = 'Error de conexion';
            }
            btn.disabled = false;
        };
        xhr.send(JSON.stringify({
            gramet: cruce_seleccionado,
            nombre: nombre_cruce,
            horas: horas
        }));
    }
    </script>
</body>
</html>'''
    return html

@app.route('/obtener-gramet', methods=['POST'])
def obtener_gramet():
    global driver_global
    try:
        data = request.json
        gramet = data.get('gramet')
        nombre = data.get('nombre')
        horas = data.get('horas')
        
        print(f"\n[{time.strftime('%H:%M:%S')}] {nombre}")
        
        # Crear driver solo si no existe
        if driver_global is None:
            options = webdriver.EdgeOptions()
            options.add_experimental_option("detach", True)
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            driver_global = webdriver.Edge(
                service=Service(EdgeChromiumDriverManager().install()),
                options=options
            )
        
        driver = driver_global
        
        # Abrir OGIMET en nueva pestaña
        driver.execute_script("window.open('https://www.ogimet.com/gramet_aero.phtml');")
        
        # Cambiar a la nueva pestaña
        driver.switch_to.window(driver.window_handles[-1])
        
        # Esperar a que cargue el formulario (sin cerrar popup)
        time.sleep(1)
        
        wait = WebDriverWait(driver, 10)
        inputs = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "input[type='text']")))
        
        if len(inputs) > 0:
            inputs[0].clear()
            inputs[0].send_keys(gramet)
        if len(inputs) > 1:
            inputs[1].clear()
            inputs[1].send_keys(horas)
        if len(inputs) > 2:
            inputs[2].clear()
            inputs[2].send_keys(horas)
        
        for inp in inputs:
            if inp.get_attribute("value") in ["100", "250"]:
                inp.clear()
                inp.send_keys("250")
                break
        
        submit_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='submit'] | //button[contains(text(), 'Enviar')]")))
        submit_btn.click()
        
        # Esperar a que cargue el GRAMET y aparezca el popup
        time.sleep(1)  # Reducido a 1 segundo
        
        # Intento 1: Click directo en el botón
        try:
            driver.execute_script("""
                var buttons = document.querySelectorAll('button');
                for (var btn of buttons) {
                    if (btn.textContent.includes('Entendido')) {
                        btn.dispatchEvent(new MouseEvent('click', {bubbles: true}));
                    }
                }
            """)
        except:
            pass
        
        time.sleep(1)
        
        # Intento 2: Click con trigger
        try:
            driver.execute_script("""
                var buttons = document.querySelectorAll('button');
                for (var btn of buttons) {
                    if (btn.textContent.includes('Entendido')) {
                        btn.click();
                        btn.click();
                        btn.click();
                    }
                }
            """)
        except:
            pass
        
        time.sleep(1)
        
        # Intento 3: Buscar por clase o ID
        try:
            driver.execute_script("""
                // Buscar cualquier elemento que pueda cerrar el popup
                var allElements = document.querySelectorAll('*');
                for (var el of allElements) {
                    if ((el.textContent === 'Entendido' || el.textContent.includes('Entendido')) && 
                        (el.tagName === 'BUTTON' || el.className.includes('btn'))) {
                        el.click();
                    }
                }
            """)
        except:
            pass
        
        return jsonify({'success': True, 'message': nombre})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    print(f"\nGRAMET Web - http://localhost:{port}\n")
    app.run(debug=False, host='0.0.0.0', port=port, threaded=True)
