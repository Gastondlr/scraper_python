# -*- coding: utf-8 -*-
"""
Editor de Spyder

Este es un archivo temporal.
"""

#%%

# Importo librerias
 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

juridiccion = "COM - Camara Nacional de Apelaciones en lo Comercial"
palabra_clave = "RESIDUOS"

def main():
    # Configuración del driver
    chrome_driver_path = r"D:\Users\Gaston\Desktop\gaston\chromedriver-win64\chromedriver.exe"
    service = Service(chrome_driver_path)
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(service=service, options=options)
    driver.get("https://scw.pjn.gov.ar/scw/home.seam")
    
    # 1. Selección de la sección "Por parte"
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "formPublica:porParte:header:inactive"))).click()
    
    # 2. Jurisdicción
    boton_juridiccion = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "formPublica:camaraPartes")))
    boton_juridiccion.click()
    boton_juridiccion.send_keys(juridiccion)
    time.sleep(2)

    # 3. Palabra clave
    input_parte = driver.find_element(By.ID, "formPublica:nomIntervParte")
    input_parte.send_keys(palabra_clave)
    time.sleep(2)
    
    # 4. Captcha manual
    driver.switch_to.frame(0)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="recaptcha-anchor"]'))).click()
    driver.switch_to.default_content()
    time.sleep(20)  # Espera para resolver el captcha manualmente
    
    # 5. Click en "Consultar"
    try:
        boton_consultar = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "formPublica:buscarPorParteButton")))
        driver.execute_script("arguments[0].click();", boton_consultar)  # Click con JavaScript
    except Exception as e:
        print("Error al hacer click en el botón Consultar:", e)
    
    # Crear un DataFrame vacío para almacenar todos los datos
    data_acumulada = []
    
    # 6. Click en icono del ojo 
    # Defino una funcion que me vaya haciendo click a cada icono y me extraiga la informacion  
    def extraer_datos():
        for i in range(15):  # Iterar sobre el número total de filas que se desea procesar
           # Localizo todos los íconos del ojo en la página actual
           iconos_ojo = WebDriverWait(driver, 10).until(
           EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.btn.btn-default.btn-sm.no-margin i.fa.fa-eye")))
           
           # Verifico que el indice sea válido
           if i < len(iconos_ojo):
               # clic en el ícono correspondiente
               driver.execute_script("arguments[0].click();", iconos_ojo[i])
               print(f"Clic realizado en el ícono {i+1} del ojo.")
               
                
               # Esperar y extraee la informacion
               wait = WebDriverWait(driver, 10)  # Creo una instancia de WebDriverWait
            
               try:
                   # Selecciono la seccion intervinente
                   boton_intervinentes = wait.until(EC.element_to_be_clickable((By.ID, "expediente:j_idt261:header:inactive")))
                   driver.execute_script("arguments[0].click();", boton_intervinentes)
                   # Selecciono en intervinentes para obtener demandado, actor y letrado patrocinante
                   button_intervinentes =  WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "expediente:j_idt261:header:inactive")))
                   driver.execute_script("arguments[0].click();", button_intervinentes)  # Click con JavaScript
                       
                   # Extrae cada campo utilizando sus etiquetas especificas
                   expediente = wait.until(EC.presence_of_element_located((By.XPATH, "//label[contains(text(),'Expediente')]/../following-sibling::div/span"))).text
                   jurisdiccion = wait.until(EC.presence_of_element_located((By.XPATH, "//label[contains(text(),'Jurisdicción')]/../following-sibling::div/span"))).text
                   dependencia = wait.until(EC.presence_of_element_located((By.XPATH, "//label[contains(text(),'Dependencia')]/../following-sibling::div/span"))).text 
                   sit_actual = wait.until(EC.presence_of_element_located((By.XPATH, "//label[contains(text(),'Sit. Actual')]/../following-sibling::div/span"))).text
                   caratula = wait.until(EC.presence_of_element_located((By.XPATH, "//label[contains(text(),'Carátula')]/../following-sibling::div/span"))).text

                   
                   from bs4 import BeautifulSoup

                   def obtener_partes_con_bs4(driver): # Funcion para poder obtener informacion de la tabla
                       try:
                           # Esperar hasta que la tabla este visible
                           wait = WebDriverWait(driver, 10)
                           tabla = wait.until(EC.presence_of_element_located((By.ID, "expediente:j_idt261")))
                       
                           # Desplazarse hasta la tabla para asegurar que este visible
                           driver.execute_script("arguments[0].scrollIntoView(true);", tabla)

                           # Extraer el HTML de la tabla
                           tabla_html = tabla.get_attribute("outerHTML")
                           soup = BeautifulSoup(tabla_html, "html.parser")

                           # Inicializar diccionario con los datos
                           datos_partes = {"DEMANDADO": "", "ACTOR": "", "LETRADO PATROCINANTE": ""}

                           # Iterar sobre filas de la tabla
                           filas = soup.find_all("tr")
                           for fila in filas:
                               columnas = fila.find_all("td")
                               if len(columnas) >= 2:# Asegurarse de tener suficientes columnas
                                   tipo = columnas[0].get_text(strip=True).replace("TIPO :", "").strip().upper()
                                   nombre = columnas[1].get_text(strip=True).replace("NOMBRE :", "").strip()
                               
                                   # Depuracion para verificar los valores obtenidos
                                   print(f"Tipo: {tipo}, Nombre: {nombre}")

                                   # Asignar valores al diccionario segun el tipo
                                   if tipo == "DEMANDADO":
                                       datos_partes["DEMANDADO"] = nombre
                                   elif tipo == "ACTOR":
                                       datos_partes["ACTOR"] = nombre
                                   elif "LETRADO" in tipo:
                                       datos_partes["LETRADO PATROCINANTE"] = nombre

                           return datos_partes["DEMANDADO"], datos_partes["ACTOR"], datos_partes["LETRADO PATROCINANTE"]

                       except Exception as e:
                           print("Error al obtener partes con BS4:", e)
                           return "", "", ""



                   demandado, actor, letrado_pat = obtener_partes_con_bs4(driver)
                   
                   # Selecciono en actuaciones para obtener la ultima actualizacion y su descripcion
                   boton_actuaciones =  WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "expediente:actuaciones:header:inactive")))
                   driver.execute_script("arguments[0].click();", boton_actuaciones)  # Click con JavaScript
                   
                   def obtener_primera_fila_expediente(driver):
                       try:
                           # Esperar hasta que la tabla este visible y obtener su HTML
                           tabla_html = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "expediente:action-table"))).get_attribute("outerHTML")

                           # Analizar el HTML de la tabla
                           soup = BeautifulSoup(tabla_html, "html.parser")
                           primera_fila = soup.find("tbody").find("tr")  # Obtener solo la primera fila

                           # Validar que se encontro la primera fila
                           if primera_fila is not None:
                               columnas = primera_fila.find_all("td")
                               if len(columnas) >= 5:
                                   # Validar que hay suficientes columnas
                                   # Retornar los datos desde la columna 1 en adelante, pues hay una columna 0 sin elementos
                                   return (columnas[1].get_text(strip=True),
                                           columnas[2].get_text(strip=True),
                                           columnas[3].get_text(strip=True),
                                           columnas[4].get_text(strip=True),)

                            # Si no hay filas o columnas suficientes, devolver valores vacíos
                           return None, None, None, None
                       except Exception as e:
                           # Manejar excepciones si la tabla no existe o no es accesible
                           print(f"Error al obtener la primera fila de la tabla de actuaciones: {e}")
                           return None, None, None, None

                   

                   oficina, fecha, tipo, descripcion = obtener_primera_fila_expediente(driver)

                   # Si no hay datos, asignar valores predeterminados (opcional)
                   if oficina is None:
                       oficina, fecha, tipo, descripcion = "", "", "", ""


                   # Crear un DataFrame con los datos extraidos
                   datos = {
                       "Expediente": [expediente],
                       "Jurisdicción": [jurisdiccion],
                       "Dependencia": [dependencia],
                       "Sit. Actual": [sit_actual],
                       "Carátula": [caratula],
                       "Demandado": [demandado],
                       "Actor": [actor],
                       "Letrado Patrocinante": [letrado_pat],
                       "Oficina": [oficina],
                       "Fecha":[fecha],
                       "Tipo":[tipo],
                       "Descripcion/detalle":[descripcion]}
                   
                   # Agrego los datos a la lista
                   data_acumulada.append(datos)
                                  
                   # Esperar hasta que la tabla este visible
               except Exception as e:
                print(f"Error al extraer información del expediente {i+1}: {e}")    
               # Volver a la pagina principal
               try:
                   boton_volver = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="expediente:j_idt78"]/div/a')))
                   driver.execute_script("arguments[0].click();", boton_volver)
                   time.sleep(2)  # Pequeña espera para asegurarte de que la pagina se recargue
               except Exception as e:
                   print(f"Error al volver a la página principal: {e}")
                   break  # Salir del bucle si no se puede volver
                   wait = WebDriverWait(driver, 10)
                   volver= wait.until(EC.presence_of_element_located((By.ID, "expediente:j_idt78")))
                       
                   # Desplazarse hasta la tabla para asegurar que este visible
                   driver.execute_script("arguments[0].scrollIntoView(true);", volver)
    
    # 7. Uso la funcion extraer datos y paso a la siguiente pagina 
    # Uso la funcion extrer datos 
    extraer_datos()   
    # Paso a la pagina siguiente 
    try:
        boton_siguiente = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "j_idt118:j_idt208:j_idt215")))
        driver.execute_script("arguments[0].click();", boton_siguiente)  # Click con JavaScript
        print("Paso a la siguiente pagina")
    except Exception as e:
        print("Error al hacer click en el botón Consultar:", e)
    time.sleep(2)
    extraer_datos()
     
    # 8. Convierto los datos en un DataFrame y los guardo en un archivo                               
    # Convertir la lista acumulada a un DataFrame
    df_final = pd.DataFrame(data_acumulada)
    
    # Mostrar el DataFrame en la consola
    print(df_final)    
    # Guardo un archivo CSV
    df_final.to_csv("expedientes_extraccion.csv", index=False, encoding="utf-8")
    print("Datos guardados en 'expedientes_extraccion.csv'.")
    
    time.sleep(5)  # Espera antes de cerrar
    driver.quit()

main()

#%%


csv_file = "expedientes_extraccion.csv"
data = pd.read_csv(csv_file)

print(data['Fecha'].head(10))  # Inspecciona los primeros 10 valores
print(data['Fecha'].dtype)    # Tipo de dato detectado

# Acomodo las fechas para poder pasar a MySQL
def normalize_fecha(fecha):
    try:
        # Eliminar corchetes si existen (convertir lista a cadena)
        if isinstance(fecha, str) and fecha.startswith("[") and fecha.endswith("]"):
            fecha = fecha.strip("[]").replace("'", "").strip()

        # Remover prefijo "Fecha:" si existe
        if "Fecha:" in fecha:
            fecha = fecha.replace("Fecha:", "").strip()

        # Ignorar valores vacíos
        if fecha == '':
            return None

        # Convertir al formato YYYY-MM-DD
        return pd.to_datetime(fecha, dayfirst=True).strftime('%Y-%m-%d')
    except Exception as e:
        print(f"Error al formatear la fecha: {fecha} - {e}")
        return None

# Aplicar la normalizacion a la columna Fecha
data['Fecha'] = data['Fecha'].apply(normalize_fecha)

data = data.dropna(subset=['Fecha'])
print(data['Fecha'].head(10))
 
print(data.head())
#%%

import mysql.connector

# Configuración de la conexiOn a MySQL
config = {
    'user': "root",
    'password': '12345678',
    'host': 'localhost',
    'database': 'ServidorLocal'
}


# Crear conexión a MySQL
try:
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()

    # Crear tabla si no existe
    create_table_query = """
    CREATE TABLE IF NOT EXISTS expedientes (
        Expediente VARCHAR(50),
        Jurisdiccion VARCHAR(100),
        Dependencia VARCHAR(100),
        Sit_Actual VARCHAR(50),
        Caratula TEXT,
        Demandado TEXT,
        Actor TEXT,
        Letrado_Patrocinante TEXT,
        Oficina VARCHAR(50),
        Fecha DATE,
        Tipo VARCHAR(50),
        Descripcion_Detalle TEXT
    );
    """
    cursor.execute(create_table_query)

    # Insertar datos en la tabla
    for _, row in data.iterrows():
        insert_query = """
        INSERT INTO expedientes (
            Expediente, Jurisdiccion, Dependencia, Sit_Actual, Caratula,
            Demandado, Actor, Letrado_Patrocinante, Oficina, Fecha, Tipo, Descripcion_Detalle
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        cursor.execute(insert_query, tuple(row))

    conn.commit()
    print("Datos insertados exitosamente en la tabla 'expedientes'.")

except mysql.connector.Error as err:
    print(f"Error: {err}")

finally:
    if conn.is_connected():
        cursor.close()
        conn.close()




