#!/usr/bin/env python3
"""
GRAMET App Desktop - Igual a la versión web
"""

import tkinter as tk
from tkinter import messagebox
import threading
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class GrametApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GRAMET - JetSMART")
        self.root.geometry("800x550")
        self.root.configure(bg="#f5f5f5")
        
        self.driver = None  # Driver reutilizable
        
        self.primary_color = "#0c3c7d"
        self.secondary_color = "#0c7eb0"
        self.accent_color = "#66b147"
        self.color_oe = "#0c7eb0"
        self.color_eo = "#ff9800"
        
        self.cruces_norte_oe = {
            "GEKAL": "SCAT_SANC",
            "MIBAS": "SCSE_SANU",
            "GUVOL": "SCVM_SANU",
        }
        
        self.cruces_norte_eo = {
            "GEKAL": "SANC_SCAT",
            "MIBAS": "SANU_SCSE",
            "ASIMO": "SANU_SCVM",
            "UMKAL": "SAME_SCVM",
        }
        
        self.cruces_sur_oe = {
            "NEBEG": "SCEL_SAMR",
            "ALBAL": "SCRG_SAME",
            "ANKON": "SCIC_SAMM",
        }
        
        self.cruces_sur_eo = {
            "ANKON": "SAMM_SCIC",
        }
        
        self.cruce_seleccionado = tk.StringVar(value="")
        self.horas_var = tk.StringVar(value="0")
        self.driver = None
        self.botones_cruces = {}
        self.botones_horas = {}
        self.nombre_cruce = ""
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz"""
        
        # Header comprimido
        header = tk.Frame(self.root, bg=self.primary_color, height=35)
        header.pack(fill=tk.X)
        
        title = tk.Label(
            header,
            text="GRAMET - JetSMART | Cruces de Cordillera | FL250",
            font=("Arial", 12, "bold"),
            bg=self.primary_color,
            fg="white"
        )
        title.pack(pady=4)
        
        # Frame principal con scroll
        main_frame = tk.Frame(self.root, bg="#f5f5f5")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas y scrollbar
        canvas = tk.Canvas(main_frame, bg="#f5f5f5", highlightthickness=0)
        scrollbar = tk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#f5f5f5")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # ZONA NORTE
        titulo_norte = tk.Label(
            scrollable_frame,
            text="🔼 ZONA NORTE",
            font=("Arial", 10, "bold"),
            bg="#f5f5f5",
            fg=self.primary_color
        )
        titulo_norte.pack(pady=(4, 3))
        
        norte_container = tk.Frame(scrollable_frame, bg="#f5f5f5")
        norte_container.pack(fill=tk.X, padx=8, pady=(0, 4))
        
        self.create_columna_oe(norte_container, self.cruces_norte_oe)
        self.create_columna_eo(norte_container, self.cruces_norte_eo)
        
        # ZONA SUR
        titulo_sur = tk.Label(
            scrollable_frame,
            text="🔽 ZONA SUR",
            font=("Arial", 10, "bold"),
            bg="#f5f5f5",
            fg=self.primary_color
        )
        titulo_sur.pack(pady=(3, 3))
        
        sur_container = tk.Frame(scrollable_frame, bg="#f5f5f5")
        sur_container.pack(fill=tk.X, padx=8, pady=(0, 4))
        
        self.create_columna_oe(sur_container, self.cruces_sur_oe)
        self.create_columna_eo(sur_container, self.cruces_sur_eo)
        
        # CONTROLES
        self.create_controles(scrollable_frame)
        
        # Footer
        footer = tk.Frame(self.root, bg="#e0e0e0", height=25)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        
        footer_text = tk.Label(
            footer,
            text="JetSMART Operations | Auto-relleno OGIMET",
            font=("Arial", 7),
            bg="#e0e0e0",
            fg="#666"
        )
        footer_text.pack(pady=2)
    
    def create_columna_oe(self, parent, cruces_dict):
        """Columna O→E (Azul)"""
        
        frame = tk.Frame(parent, bg="#f5f5f5")
        frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        arrow = tk.Label(
            frame,
            text="→",
            font=("Arial", 12, "bold"),
            bg="#f5f5f5",
            fg=self.color_oe
        )
        arrow.pack(pady=(0, 2))
        
        title = tk.Label(
            frame,
            text="O→E",
            font=("Arial", 9, "bold"),
            bg="#e3f2fd",
            fg=self.color_oe,
            padx=6,
            pady=3
        )
        title.pack(fill=tk.X, pady=(0, 4))
        
        for nombre, codigo in cruces_dict.items():
            btn = tk.Button(
                frame,
                text=nombre,
                font=("Arial", 8),
                bg="white",
                fg=self.color_oe,
                relief=tk.FLAT,
                bd=1,
                padx=8,
                pady=4,
                cursor="hand2"
            )
            btn.config(command=lambda c=codigo, n=f"{nombre} (O→E)", b=btn: self.seleccionar_cruce(c, n, b))
            btn.pack(fill=tk.X, pady=2)
            self.botones_cruces[codigo] = btn
    
    def create_columna_eo(self, parent, cruces_dict):
        """Columna E→O (Naranja)"""
        
        frame = tk.Frame(parent, bg="#f5f5f5")
        frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        arrow = tk.Label(
            frame,
            text="←",
            font=("Arial", 12, "bold"),
            bg="#f5f5f5",
            fg=self.color_eo
        )
        arrow.pack(pady=(0, 2))
        
        title = tk.Label(
            frame,
            text="E→O",
            font=("Arial", 9, "bold"),
            bg="#fff3cd",
            fg=self.color_eo,
            padx=6,
            pady=3
        )
        title.pack(fill=tk.X, pady=(0, 4))
        
        for nombre, codigo in cruces_dict.items():
            btn = tk.Button(
                frame,
                text=nombre,
                font=("Arial", 8),
                bg="white",
                fg=self.color_eo,
                relief=tk.FLAT,
                bd=1,
                padx=8,
                pady=4,
                cursor="hand2"
            )
            btn.config(command=lambda c=codigo, n=f"{nombre} (E→O)", b=btn: self.seleccionar_cruce(c, n, b))
            btn.pack(fill=tk.X, pady=2)
            self.botones_cruces[codigo] = btn
    
    def seleccionar_cruce(self, codigo, nombre, btn):
        """Selecciona un cruce"""
        
        for b in self.botones_cruces.values():
            b.config(relief=tk.FLAT, bd=1, bg="white")
        
        # Detectar si es O→E (azul) o E→O (naranja)
        if "(O→E)" in nombre or "(O->E)" in nombre:
            btn.config(relief=tk.SUNKEN, bd=2, bg="#0c7eb0", fg="white")  # Azul
        elif "(E→O)" in nombre or "(E->O)" in nombre:
            btn.config(relief=tk.SUNKEN, bd=2, bg="#ff9800", fg="white")  # Naranja
        
        self.cruce_seleccionado.set(codigo)
        self.nombre_cruce = nombre
        self.status_label.config(
            text=f"✓ {nombre}",
            fg=self.secondary_color,
            font=("Arial", 8, "bold")
        )
    
    def create_controles(self, parent):
        """Controles de horas y botón"""
        
        control_frame = tk.Frame(parent, bg="#e3f2fd")
        control_frame.pack(fill=tk.X, padx=8, pady=6)
        
        content = tk.Frame(control_frame, bg="#e3f2fd")
        content.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)
        
        # Fila 1: Horas
        horas_frame = tk.Frame(content, bg="#e3f2fd")
        horas_frame.pack(fill=tk.X, pady=(0, 6))
        
        horas_label = tk.Label(
            horas_frame,
            text="⏰ Horas:",
            font=("Arial", 8, "bold"),
            bg="#e3f2fd",
            fg=self.primary_color
        )
        horas_label.pack(side=tk.LEFT, padx=(0, 6))
        
        # Botones 0-6
        for i in range(0, 7):
            btn = tk.Button(
                horas_frame,
                text=str(i),
                font=("Arial", 7, "bold"),
                bg="white",
                fg=self.primary_color,
                width=2,
                relief=tk.FLAT,
                bd=1,
                cursor="hand2",
                command=lambda h=i: self.set_horas(h)
            )
            btn.pack(side=tk.LEFT, padx=2)
            self.botones_horas[i] = btn
        
        tk.Label(horas_frame, text="Manual:", font=("Arial", 7), bg="#e3f2fd").pack(side=tk.LEFT, padx=(6, 2))
        
        manual_input = tk.Spinbox(
            horas_frame,
            from_=0,
            to=23,
            textvariable=self.horas_var,
            width=3,
            font=("Arial", 7),
            justify="center"
        )
        manual_input.pack(side=tk.LEFT, padx=2)
        
        # Fila 2: Estado
        status_frame = tk.Frame(content, bg="#e3f2fd")
        status_frame.pack(fill=tk.X, pady=(0, 6))
        
        self.status_label = tk.Label(
            status_frame,
            text="Selecciona un cruce",
            font=("Arial", 7),
            bg="#e3f2fd",
            fg="#666"
        )
        self.status_label.pack(side=tk.LEFT)
        
        # Fila 3: Botón
        btn_frame = tk.Frame(content, bg="#e3f2fd")
        btn_frame.pack(fill=tk.X)
        
        self.btn_obtener = tk.Button(
            btn_frame,
            text="🚀 OBTENER GRAMET",
            font=("Arial", 9, "bold"),
            bg=self.secondary_color,
            fg="white",
            padx=15,
            pady=6,
            relief=tk.FLAT,
            cursor="hand2",
            command=self.obtener_gramet
        )
        self.btn_obtener.pack(side=tk.LEFT)
        
        self.progress_label = tk.Label(
            btn_frame,
            text="",
            font=("Arial", 7),
            bg="#e3f2fd",
            fg=self.secondary_color
        )
        self.progress_label.pack(side=tk.LEFT, padx=8)
    
    def set_horas(self, horas):
        """Establece horas y sombrrea el botón"""
        self.horas_var.set(str(horas))
        
        # Deseleccionar todos
        for btn in self.botones_horas.values():
            btn.config(relief=tk.FLAT, bd=1, bg="white", fg=self.primary_color)
        
        # Seleccionar este
        self.botones_horas[horas].config(relief=tk.SUNKEN, bd=2, bg=self.secondary_color, fg="white")
    
    def obtener_gramet(self):
        """Obtiene GRAMET"""
        
        if not self.cruce_seleccionado.get():
            messagebox.showwarning("Error", "Selecciona un cruce")
            return
        
        gramet = self.cruce_seleccionado.get()
        nombre = self.nombre_cruce
        horas = self.horas_var.get()
        
        self.btn_obtener.config(state=tk.DISABLED, bg="#999")
        self.progress_label.config(text="⏳ Cargando...", fg="#ff9800")
        
        thread = threading.Thread(
            target=self._ejecutar_selenium,
            args=(gramet, nombre, horas)
        )
        thread.daemon = True
        thread.start()
    
    def _ejecutar_selenium(self, gramet, nombre, horas):
        """Ejecuta Selenium en nueva pestaña"""
        try:
            self.progress_label.config(text="🌐 Abriendo...", fg="#ff9800")
            self.root.update()
            
            # Crear driver solo si no existe
            if self.driver is None:
                options = webdriver.ChromeOptions()
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_experimental_option("detach", True)
                options.add_argument("--disable-blink-features=AutomationControlled")
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                options.add_experimental_option('useAutomationExtension', False)
                
                self.driver = webdriver.Chrome(
                    service=Service(ChromeDriverManager().install()),
                    options=options
                )
            
            self.progress_label.config(text="📡 Conectando...", fg="#ff9800")
            self.root.update()
            
            # Abrir OGIMET en nueva pestaña
            self.driver.execute_script("window.open('https://www.ogimet.com/gramet_aero.phtml');")
            
            # Cambiar a la nueva pestaña
            self.driver.switch_to.window(self.driver.window_handles[-1])
            
            time.sleep(1)
            
            self.progress_label.config(text="🔧 Rellenando...", fg="#ff9800")
            self.root.update()
            
            wait = WebDriverWait(self.driver, 10)
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
            
            self.progress_label.config(text="📤 Enviando...", fg="#ff9800")
            self.root.update()
            
            submit_btn = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//input[@type='submit'] | //button[contains(text(), 'Enviar')]"))
            )
            
            submit_btn.click()
            
            self.progress_label.config(text="📤 Enviando...", fg="#ff9800")
            self.root.update()
            
            # Esperar a que cargue el GRAMET y aparezca el popup
            time.sleep(1)  # Reducido a 1 segundo
            
            # Intento 1: Click directo
            try:
                self.driver.execute_script("""
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
            
            # Intento 2: Click múltiple
            try:
                self.driver.execute_script("""
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
            
            # Intento 3: Búsqueda más amplia
            try:
                self.driver.execute_script("""
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
            
            self.progress_label.config(text="✅ Listo", fg=self.accent_color)
            
        except Exception as e:
            self.progress_label.config(text=f"❌ Error", fg="#f44336")
        
        finally:
            self.root.after(0, lambda: self.btn_obtener.config(state=tk.NORMAL, bg=self.secondary_color))


def main():
    root = tk.Tk()
    app = GrametApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
