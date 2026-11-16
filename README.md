# Programas de Tesis: Estudio Comparativo del Rendimiento de Paneles Solares Fijos y Móviles en Condiciones Reales

Todos los algoritmos desarrollados para esta tesis (sketches de Arduino, scripts de Google Apps Script y el análisis en Python) han sido documentados y alojados en un repositorio de GitHub con el fin de facilitar su consulta y asegurar la replicabilidad del proyecto.

El repositorio se encuentra disponible en el siguiente enlace:
[https://github.com/pramos73/Programas-Tesis/](https://github.com/pramos73/Programas-Tesis/)

**Nota:** Debido a que el repositorio es de carácter privado, el acceso debe ser solicitado a la autora a través del correo: pramos@unq.edu.ar

---

## A.1. Microcontrolador ESP32-01

En el repositorio, dentro de la carpeta `/Programas_Arduino`, se encuentra el archivo `2_grados_diciembre25.ino`. Este sketch fue desarrollado en la plataforma Arduino Cloud para el microcontrolador ESP32-01, el lenguaje de programación es C++.

El Programa ESP32-01 implementa el control de un seguidor solar de dos ejes, 2GDL (azimut y elevación) sobre un panel fotovoltaico. El sistema combina sensores de luz, sensores ambientales y un sensor de corriente/voltaje para registrar el desempeño del panel, y envía los datos a Google Sheets para su monitoreo remoto, cada 45 segundos.

### A.1.1. Qué mide y controla

* 2 servomotores (azimut y elevación) que orientan el panel solar de dos ejes.
* 4 LDR (Norte, Sur, Este y Oeste) utilizados para el seguimiento por luz.
* INA219 (dirección I2C 0x40) para medir el voltaje y la corriente del panel.
* SHT31 (temperatura y humedad local) y BH1750 (luz ambiental).
* 3 modos de seguimiento:
  1. Astronómico (modo 0).
  2. Control PI (modo 1).
  3. LDR Híbrido (modo 2).
* Envío a Google Sheets con los datos de los sensores y la posición solar calculada.

### A.1.2. Resumen de componentes

| Componente | Cantidad | Función |
| :--- | :---: | :--- |
| Servomotores | 2 | Azimut y elevación |
| LDR | 4 | Norte, Sur, Este, Oeste |
| INA219 (0x40) | 1 | Voltaje y corriente del panel |
| SHT31 | 1 | Temperatura y humedad local |
| BH1750 | 1 | Luz ambiental |

### A.1.3. Modos de seguimiento

* **Modo 0 — Astronómico:** Calcula la posición solar a partir de la fecha, hora y coordenadas geográficas, y orienta el panel en consecuencia.
* **Modo 1 — Control PI:** Ajusta la posición del panel según la diferencia de iluminación entre los LDR, usando un controlador proporcional-integral con zona muerta y anti-windup.
* **Modo 2 — LDR Híbrido:** Realiza correcciones por pasos discretos (fino, normal y rápido) en función de la magnitud de la diferencia entre LDR opuestos.

### A.1.4. Salida de datos

El programa envía periódicamente a Google Sheets un conjunto de datos que incluye:
* Lecturas de los 4 LDR.
* Voltaje, corriente y potencia del panel (INA219).
* Temperatura y humedad local (SHT31).
* Luz ambiental (BH1750).
* Posición de los servos (azimut y elevación).
* Azimut y elevación solar calculados.
* Modo de seguimiento activo y estado del sistema.

---

## A.2. Microcontrolador ESP32-02

En la carpeta `/Programas_Arduino` del repositorio se encuentra el archivo `SERVO-2LDRs.ino`. Este sketch fue desarrollado en la plataforma Arduino Cloud para el microcontrolador ESP32-02 y está escrito en C++. A diferencia del Programa 1, este dispositivo controla al seguidor solar 1GDL de un solo eje (azimut) y adquiere en forma simultánea las mediciones de cuatro paneles fotovoltaicos, panel fijo 2A y panel fijo Delta (3A+3B) mediante cuatro sensores INA219, además de datos meteorológicos externos obtenidos de la API de OpenWeather.

### A.2.1. Descripción general

El Programa ESP32-02 implementa el control de un seguidor solar de un eje sobre un panel móvil, complementado con la medición de voltaje, corriente y potencia de cuatro paneles (uno con seguimiento y tres fijos). El sistema combina sensores de luz, cuatro sensores de corriente/voltaje y una API meteorológica externa, y envía los datos a Google Sheets cada 15 segundos para su monitoreo remoto.

### A.2.2. Qué mide y controla

* 1 servomotor (azimut) que orienta el panel solar móvil.
* 2 LDR (Este y Oeste) utilizados para el seguimiento por luz.
* 4 sensores INA219 (direcciones I2C 0x40, 0x41, 0x44 y 0x45) para medir voltaje, corriente y potencia de cuatro paneles fotovoltaicos de forma simultánea.
* OpenWeather para obtener temperatura exterior, humedad, presión atmosférica, velocidad y dirección del viento, nubosidad y condición climática.
* Calidad del aire estimada a partir de las variables meteorológicas.
* 3 modos de seguimiento:
  1. Astronómico (modo 0).
  2. Control PI (modo 1).
  3. LDR Híbrido (modo 2).
* Envío a Google Sheets con los datos de los sensores, la posición del servo y los datos meteorológicos.

### A.2.3. Resumen de componentes

| Componente | Cantidad | Función |
| :--- | :---: | :--- |
| Servomotor | 1 | Azimut del panel móvil |
| LDR | 2 | Este, Oeste |
| INA219 (0x40) | 1 | Panel 1 (con seguimiento) |
| INA219 (0x41) | 1 | Panel 2 (fijo) |
| INA219 (0x44) | 1 | Panel 3 (fijo) |
| INA219 (0x45) | 1 | Panel 4 (fijo) |
| OpenWeather (API) | 1 | Datos meteorológicos externos |

### A.2.4. Modos de seguimiento

* **Modo 0 — Astronómico:** Calcula la posición solar a partir de la fecha, hora y coordenadas geográficas, y orienta el panel en consecuencia.
* **Modo 1 — Control PI:** Ajusta la posición del panel según la diferencia de iluminación entre los dos LDR, usando un controlador proporcional-integral con zona muerta, filtro pasa-bajos y anti-windup.
* **Modo 2 — LDR Híbrido:** Realiza correcciones por pasos discretos (fino, normal y rápido) en función de la magnitud de la diferencia entre los LDR Este y Oeste.

### A.2.5. Salida de datos

El programa envía periódicamente a Google Sheets (cada 15 segundos) un conjunto de datos que incluye:
* Lecturas de los 2 LDR (Este y Oeste) y su diferencia.
* Voltaje, corriente y potencia de los 4 paneles (INA219).
* Posición del servo (azimut) y azimut solar calculado.
* Modo de seguimiento activo.
* Temperatura, humedad, presión, velocidad y dirección del viento, nubosidad y condición climática (OpenWeather).
* Calidad del aire estimada.
* Fecha, hora, dirección IP y calidad de señal WiFi del dispositivo.

### A.2.6. Frecuencias de operación

A diferencia del Programa ESP32-01, el Programa ESP32-02 maneja tres intervalos temporales independientes:

| Tarea | Periodo |
| :--- | :--- |
| Lectura de LDR y seguimiento (PI / LDR) | ∼200 ms |
| Envío a Google Sheets | 15 s |
| Actualización de OpenWeather | 10 min |

### A.2.7. Diferencias respecto del Programa ESP32-01

* El Programa ESP32-01 controla un seguidor de dos ejes con 2 servos y 4 LDR; el Programa ESP32-02 controla un seguidor de un eje con 1 servo y 2 LDR.
* El Programa ESP32-01 mide un panel con un INA219; el Programa ESP32-02 mide cuatro paneles con cuatro INA219 en paralelo.
* El Programa ESP32-01 no consulta APIs externas; el Programa ESP32-02 integra OpenWeather para enriquecer los datos con variables meteorológicas.
* La frecuencia de envío a Google Sheets es de 45 s en el Programa ESP32-01 y de 15 s en el Programa ESP32-02.

---
## A.3. Scripts de Google Apps Script

En la carpeta `/Programas_Google_Apps_Script` del repositorio se encuentra el archivo `Código.gs` (escrito en JavaScript para el entorno de Google Cloud). Este script actúa como el servidor central del proyecto y se encarga de la recepción, el procesamiento y la organización de los datos enviados por ambos microcontroladores ESP32 a través de peticiones HTTP POST.

### A.3.1. Funcionalidades principales

* **Recepción de datos (doPost):** Actúa como un servidor web que recibe los paquetes de datos en formato JSON enviados por los microcontroladores y detecta automáticamente a cuál de los dos dispositivos (ESP32-01 o ESP32-02) pertenecen los datos.
* **Control de tiempo (Rate Limiting):** Utiliza las propiedades del script (`PropertiesService`) para almacenar la marca de tiempo (timestamp) del último guardado de cada dispositivo. Si un microcontrolador intenta guardar datos antes de los 15 segundos establecidos, el script rechaza la petición y le indica al dispositivo cuántos segundos debe esperar, evitando la saturación de la base de datos.
* **Creación automatizada de hojas (crearHojasUnaVez):** Verifica que el libro de cálculo contenga las hojas necesarias y, si no existen, las crea automáticamente con sus respectivos encabezados.
* **Organización visual:** Aplica colores distintivos a los encabezados de las hojas para facilitar la lectura de los datos (Azul para el Micro 01, Verde para el Micro 02 y Naranja para los datos climáticos de OpenWeather).
* **Combinación de datos (guardarEnHojaCombinada):** Dado que los datos de ambos microcontroladores llegan de forma asíncrona, el script busca la última fila registrada del dispositivo que no envió datos en ese instante y fusiona ambas mediciones en una sola fila dentro de la hoja `Datos_Combinados_2G_1G+FIJOS`, generando un registro unificado y cronológico para el análisis posterior.

### A.3.2. Estructura de las hojas en Google Sheets

El script gestiona tres hojas de cálculo principales:
1. `2G_Datos_crudos_Seguimiento_Solar`: Almacena las lecturas del seguidor solar de dos ejes (4 LDR, INA219, SHT31, BH1750 y posición de los servos).
2. `Datos_crudos_1G_+FIJOS`: Almacena las lecturas del seguidor de un eje (2 LDR), los cuatro paneles solares medidos simultáneamente y las condiciones climáticas externas.
3. `Datos_Combinados_2G_1G+FIJOS`: Es la base de datos final que utiliza el script de Python para el análisis estadístico. Sincroniza en una sola línea de tiempo los datos de todos los sensores y paneles.

---
## A.4. Código de análisis en Python

El archivo `analisis_python.py`, ubicado en la carpeta `/Programas_Python` del repositorio, contiene el script utilizado para el procesamiento de los datos de medición. A través de este código se realizaron los cálculos de energía diaria, la generación de gráficos y los análisis estadísticos de correlación presentados en los capítulos anteriores.