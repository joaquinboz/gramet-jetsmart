# GRAMET Web - JetSMART

Aplicación web para consultar los **GRAMET** (meteogramas de ruta de OGIMET) de los cruces de cordillera de JetSMART, a FL250. Está pensada para usarse desde cualquier dispositivo con solo abrir una URL — no requiere instalar nada.

## Cómo funciona

La app está desplegada en **Railway** y se compone de:

- Una **interfaz de botones** (cruces agrupados en Zona Norte y Zona Sur, por sentido O→E / E→O) donde se eligen uno o varios cruces y las horas de referencia.
- Un backend **Flask + Playwright**: cuando se piden los GRAMET, el servidor navega a OGIMET (`display_gramet.php`) con la hora de referencia generada al momento, captura solo la imagen del gráfico y la devuelve. Así se evita el banner "Entendido" (nunca aparece, porque solo se captura la imagen) y no hay que rellenar formularios a mano.
- Los resultados se muestran **en la misma página**, agrupados Norte/Sur y en orden, cada uno rotulado con su punto de cruce y sentido.
- Botón **"Descargar PDF"** que arma, en el navegador, un PDF con los GRAMET generados (en orden, sin el panel de selección), más el texto legal y la firma.

## Archivos del proyecto

| Archivo | Función |
|---|---|
| `gramet_app.py` | La aplicación completa (UI + backend Flask/Playwright). |
| `Dockerfile` | Imagen de Playwright (con Chromium) que Railway usa para construir. |
| `requirements.txt` | Dependencias: Flask y Playwright. |
| `README.md` | Este archivo. |
| `.gitignore` | Evita subir archivos generados (venv, cache, restos de PyInstaller). |

## Despliegue

Railway construye automáticamente desde la rama `main` usando el `Dockerfile`. El flujo de trabajo es:

1. Modificar `gramet_app.py` (o el archivo que corresponda) en la carpeta local.
2. **Verificar** en PowerShell que el archivo copiado es el correcto antes de subir:
   ```powershell
   Get-Content gramet_app.py -TotalCount 3
   ```
3. Subir los cambios:
   ```powershell
   git add .
   git commit -m "descripcion del cambio"
   git push
   ```
4. Railway detecta el push y redespliega solo.

> Nota: la primera construcción tras cambiar el `Dockerfile` tarda más, porque descarga la imagen de Playwright con Chromium. Las siguientes son rápidas (queda cacheada).

## Versiones etiquetadas (puntos de retorno)

Para volver a una versión estable: `git checkout <tag>` (y `git checkout main` para regresar).

- **v1.0** — Un cruce a la vez; resultado en pestaña nueva.
- **v2.0** — Multi-selección; resultados agrupados Norte/Sur en la misma página.
- **v3.0** — Botón Descargar PDF (GRAMET generados + disclaimer + firma).

## Ejecutar localmente (opcional)

```powershell
pip install -r requirements.txt
python -m playwright install chromium
python gramet_app.py
```
Luego abrir http://localhost:8080

## Aviso

La información presentada es de carácter referencial. Es responsabilidad del piloto y del despachador verificar su vigencia y autenticidad en las fuentes oficiales antes de su uso operacional.
