# Vigilancia Normativa → Excel (OneDrive) → Power BI — versión local

Revisa 7 sitios de normativa gubernamental y guarda las novedades en un
Excel dentro de tu carpeta de OneDrive, para que Power BI lo lea.

## 1. Instalación (una sola vez)

Necesitas [Python](https://www.python.org/downloads/) instalado (marca la
casilla "Add Python to PATH" durante la instalación) y
[VS Code](https://code.visualstudio.com/) con la extensión de Python.

Abre esta carpeta en VS Code (`Archivo > Abrir carpeta...`), luego abre
una terminal dentro de VS Code (`Terminal > Nueva terminal`) y corre:

```bash
python -m venv venv
venv\Scripts\activate          # En Mac/Linux: source venv/bin/activate

pip install -r requirements.txt
playwright install chromium
```

## 2. Configurar la ruta de OneDrive

Abre `excel_writer.py` y ajusta la línea `RUTA_EXCEL` para que apunte a
una carpeta dentro de tu OneDrive local. Por ejemplo, en Windows:

```python
RUTA_EXCEL = Path(os.environ.get(
    "RUTA_EXCEL",
    r"C:\Users\TU_USUARIO\OneDrive - Asobancaria\VigilanciaNormativa\normativa.xlsx"
))
```

**Cómo encontrar tu ruta exacta de OneDrive:** abre el Explorador de
Windows, ve a tu carpeta de OneDrive, crea ahí una carpeta llamada
`VigilanciaNormativa`, haz clic derecho sobre ella → "Copiar como ruta
de acceso", y pega esa ruta (ajustando las `\` si hace falta) en el
código.

## 3. Primera corrida (prueba)

En la terminal de VS Code:

```bash
python main.py
```

La primera vez va a traer bastante contenido de golpe (todo lo que
encuentre con fecha reconocible). Es normal. Verifica que el archivo
`normativa.xlsx` haya aparecido en tu carpeta de OneDrive y que OneDrive
lo haya sincronizado (ícono de nube/check verde junto al archivo).

## 4. Automatizar (que corra solo, sin abrir VS Code)

Esto usa el Programador de tareas de Windows. **Tu computador tiene que
estar prendido y con sesión iniciada** a la hora programada — a
diferencia de una nube, aquí si el equipo está apagado, esa corrida no
sucede.

1. Abre el "Programador de tareas" de Windows (búscalo en el menú
   inicio).
2. Click en "Crear tarea básica..."
3. Nómbrala "Vigilancia Normativa", siguiente.
4. Desencadenador: "Diariamente", elige la hora (ej. 8:00 a.m.).
5. Acción: "Iniciar un programa".
6. En "Programa o script", busca el `python.exe` de tu entorno virtual,
   algo como:
   `C:\ruta\a\alerta-normativa\venv\Scripts\python.exe`
7. En "Agregar argumentos", escribe: `main.py`
8. En "Iniciar en", pon la ruta de la carpeta del proyecto:
   `C:\ruta\a\alerta-normativa`
9. Finalizar.

Puedes probarla de inmediato: busca la tarea en la lista del
Programador, clic derecho → "Ejecutar".

## 5. Conectar Power BI

1. Abre Power BI Desktop → **Obtener datos → Excel**.
2. Navega hasta el archivo `normativa.xlsx` en tu carpeta de OneDrive y
   ábrelo.
3. Selecciona la hoja "Normativa" y carga los datos.
4. Publica el reporte a Power BI Service.
5. En Power BI Service, conecta el dataset a la versión del archivo en
   **OneDrive - Business** (Power BI lo detecta automáticamente si el
   archivo está en tu OneDrive corporativo) y activa la actualización
   automática — esto usa tu sesión normal de Microsoft 365, sin
   necesidad de permisos especiales de Azure.

## 6. Agregar más sitios

Edita `sitios.yaml`, agregando un bloque nuevo:

```yaml
  - nombre: "Nombre de la entidad"
    url: "https://sitio.gov.co/normativa"
```

## 7. Notas importantes

- **Playwright debe reinstalarse** solo si borras el entorno virtual
  (`venv`) o cambias de computador — normalmente no hace falta repetirlo.
- **Ver errores:** si `python main.py` falla, el mensaje de error aparece
  directo en la terminal de VS Code.
- **Copia de seguridad:** como el archivo vive en OneDrive, ya tiene
  historial de versiones automático (clic derecho → "Ver versiones
  anteriores" en el Explorador de Windows) por si algo se corrompe.
