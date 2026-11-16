// ===========================================
// CONFIGURACIÓN
// ===========================================
var SPREADSHEET_ID = '1oR6we60F2jPJ_4dd5jdmr_VAZsoxkrobbv18M0duhA4';

// ===========================================
// CREAR HOJAS (CON COLORES DIFERENCIADOS)
// ===========================================
function crearHojasUnaVez() {
  console.log("🚀 Verificando/Creando hojas...");
  
  try {
    var libro = SpreadsheetApp.openById(SPREADSHEET_ID);
    console.log("📚 Libro abierto:", libro.getName());
    
    // ===== HOJA 1: ESP32 01 (Seguimiento Solar) =====
    var hoja1 = libro.getSheetByName('2G_Datos_crudos_Seguimiento_Solar');
    if (!hoja1) {
      console.log("📄 Creando hoja para MICRO 01...");
      hoja1 = libro.insertSheet('2G_Datos_crudos_Seguimiento_Solar');
      
      var headers1 = [
        'Dispositivo_ID', 'Dispositivo_Nombre',
        'Fecha', 'Hora',
        'Modo: 0=Astron,1=PI,2=LDR', 'Pos_Elevacion (°)', 'Pos_Azimut (°)',
        'Temperatura_Local (°C)', 'Humedad_Local (%)', 'Luz_Local (Lux)',
        'Voltaje 2G (V)', 'Corriente 2G (A)', 'Potencia 2G (W)',
        'LDR_Norte', 'LDR_Sur', 'LDR_Este', 'LDR_Oeste',
        'Elevacion_Solar (°)', 'Azimut_Solar (°)',
        'IP_Dispositivo', 'RSSI_Wifi_dBm'
      ];
      
      hoja1.getRange(1, 1, 1, headers1.length).setValues([headers1]);
      hoja1.getRange(1, 1, 1, headers1.length)
        .setFontWeight('bold')
        .setBackground('#2196F3')  // Azul
        .setFontColor('white');
      hoja1.setFrozenRows(1);
      console.log("✅ Hoja 1 creada: 2G_Datos_crudos_Seguimiento_Solar");
    }
    
    // ===== HOJA 2: ESP32 02 (Paneles Solares) =====
    var hoja2 = libro.getSheetByName('Datos_crudos_1G_+FIJOS');
    if (!hoja2) {
      console.log("📄 Creando hoja para MICRO 02...");
      hoja2 = libro.insertSheet('Datos_crudos_1G_+FIJOS');
      
      var headers2 = [
        'Dispositivo_ID', 'Dispositivo_Nombre',
        'Fecha', 'Hora', 'Modo: 0=Astron,1=PI,2=LDR', 'Azimut_Servo (°)',
        'Azimut_Solar (°)',
        'LDR_Este', 'LDR_Oeste',
        'Panel1G_Voltaje (V)', 'Panel1G_Corriente (A)', 'Panel1G_Potencia (W)',
        'Panel2FIJO_Voltaje (V)', 'Panel2FIJO_Corriente (A)', 'Panel2FIJO_Potencia (W)',
        'Panel3FIJOA_Voltaje (V)', 'Panel3FIJOA_Corriente (A)', 'Panel3FIJOA_Potencia (W)',
        'Panel3FIJOB_Voltaje (V)', 'Panel3FIJOB_Corriente (A)', 'Panel3FIJOB_Potencia (W)',
        'Temperatura_Web (C°)', 'Humedad_Web (%)', 'Presion_Web (hPa)',
        'Velocidad_Viento (m/s)', 'Direccion_Viento (°)', 'Condicion_Clima',
        'Nubosidad', 'Calidad_Aire',
        'IP_Dispositivo', 'RSSI_Wifi'
      ];
      
      hoja2.getRange(1, 1, 1, headers2.length).setValues([headers2]);
      hoja2.getRange(1, 1, 1, headers2.length)
        .setFontWeight('bold')
        .setBackground('#4CAF50')  // Verde
        .setFontColor('white');
      hoja2.setFrozenRows(1);
      console.log("✅ Hoja 2 creada: Datos_crudos_1G_+FIJOS");
    }
    
    // ===== HOJA 3: DATOS COMBINADOS CON COLORES =====
    var hoja3 = libro.getSheetByName('Datos_Combinados_2G_1G+FIJOS');
    if (!hoja3) {
      console.log("📄 Creando hoja COMBINADA con colores...");
      hoja3 = libro.insertSheet('Datos_Combinados_2G_1G+FIJOS');
      
      var headers3 = [
        // TIMESTAMP (gris)
        'Timestamp_Unix', 'Fecha_Hora',
        
        // ===== MICRO 01 - AZUL =====
        '🔵 Micro01_Nombre', '🔵 Modo01: 0=Astron, 1=PI, 2=LDR', '🔵 Elevacion_Servo (°)', '🔵 Azimut_Servo (°)',
        '🔵 Temp_Local (°C)', '🔵 Hum_Local (%)', '🔵 Luz_Local (Lux)',
        '🔵 Voltaje_2G (V)', '🔵 Corriente_2G (A)', '🔵 Potencia_2G (W)',
        '🔵 Elevacion_Solar_Micro01 (°)', '🔵 Azimut_Solar_Micro01 (°)',
        
        // ===== MICRO 02 - VERDE =====
        '🟢 Micro02_Nombre', '🟢 Modo02: 0=Astron, 1=PI, 2=LDR', '🟢 Azimut_Servo_Micro02 (°)', '🟢 Azimut_Solar_Micro02 (°)',
        '🟢 Panel1G_Voltaje (V)', '🟢 Panel1G_Corriente (A)', '🟢 Panel1G_Potencia (W)',
        '🟢 Panel2FIJO_Voltaje (V)', '🟢 Panel2FIJO_Corriente (A)', '🟢 Panel2FIJO_Potencia (W)',
        '🟢 Panel3FIJOA_Voltaje (V)', '🟢 Panel3FIJOA_Corriente (A)', '🟢 Panel3FIJOA_Potencia (W)',
        '🟢 Panel3FIJOB_Voltaje (V)', '🟢 Panel3FIJOB_Corriente (A)', '🟢 Panel3FIJOB_Potencia (W)',
        
        // ===== DATOS CLIMÁTICOS - NARANJA =====
        '🟠 Temp_Externa (C°)', '🟠 Hum_Externa (%)', '🟠 Presion_Atm (hPa)',
        '🟠 Viento_Vel (m/s)', '🟠 Viento_Dir (°)', '🟠 Condicion_Clima',
        '🟠 Nubosidad', '🟠 Calidad_Aire'
      ];
      
      // ESTABLECER ENCABEZADOS
      hoja3.getRange(1, 1, 1, headers3.length).setValues([headers3]);
      
      // APLICAR COLORES POR SECCIÓN
      
      // TIMESTAMP (gris)
      hoja3.getRange(1, 1, 1, 2)
        .setBackground('#9E9E9E')  // Gris
        .setFontColor('white')
        .setFontWeight('bold');
      
      // MICRO 01 (azul)
      hoja3.getRange(1, 3, 1, 12)
        .setBackground('#2196F3')  // Azul
        .setFontColor('white')
        .setFontWeight('bold');
      
      // MICRO 02 (verde)
      hoja3.getRange(1, 15, 1, 16)
        .setBackground('#4CAF50')  // Verde
        .setFontColor('white')
        .setFontWeight('bold');
      
      // DATOS CLIMÁTICOS (naranja)
      hoja3.getRange(1, 31, 1, 8)
        .setBackground('#FF9800')  // Naranja
        .setFontColor('white')
        .setFontWeight('bold');
      
      hoja3.setFrozenRows(1);
      console.log("✅ Hoja 3 creada con colores: Datos_Combinados_2G_1G+FIJOS");
      console.log("   📊 Secciones:");
      console.log("      - Columnas 1-2:  Gris (Timestamp)");
      console.log("      - Columnas 3-14: Azul (Micro 01)");
      console.log("      - Columnas 15-30: Verde (Micro 02)");
      console.log("      - Columnas 31-39: Naranja (Clima)");
    }
    
    console.log("🎉 Todas las hojas listas");
    return true;
    
  } catch (error) {
    console.error("❌ Error creando hojas:", error);
    return false;
  }
}

// ===========================================
// FUNCIÓN PARA GUARDAR EN HOJA COMBINADA
// ===========================================
function guardarEnHojaCombinada(datosMicro01, datosMicro02) {
  console.log("🔄 Guardando en hoja combinada...");
  
  try {
    var libro = SpreadsheetApp.openById(SPREADSHEET_ID);
    var hoja = libro.getSheetByName('Datos_Combinados_2G_1G+FIJOS');
    
    if (!hoja) {
      crearHojasUnaVez();
      hoja = libro.getSheetByName('Datos_Combinados_2G_1G+FIJOS');
    }
    
    var ahora = new Date();
    var fechaHora = Utilities.formatDate(ahora, Session.getScriptTimeZone(), 'dd/MM/yyyy HH:mm:ss');
    var timestamp = ahora.getTime();
    
    var nuevaFila = [
      // TIMESTAMP
      timestamp,
      fechaHora,
      
      // DATOS MICRO 01 (o valores por defecto)
      datosMicro01?.dispositivo_nombre || 'Seguimiento_Solar2G',
      datosMicro01?.modo_seguimiento || 0,
      datosMicro01?.elevacion_servo || 0,
      datosMicro01?.azimut_servo || 0,
      datosMicro01?.temp_local || 0,
      datosMicro01?.hum_local || 0,
      datosMicro01?.luz_local || 0,
      datosMicro01?.voltaje_5v || 0,
      datosMicro01?.corriente_5v || 0,
      datosMicro01?.potencia_5v || 0,
      datosMicro01?.elevacion_solar || 0,
      datosMicro01?.azimut_solar || 0,
      
      // DATOS MICRO 02 (o valores por defecto)
      datosMicro02?.dispositivo_nombre || 'Paneles_Solares_1G_y_Fijos',
      datosMicro02?.modo_seguimiento || 0,
      datosMicro02?.azimut_servo || 0,
      datosMicro02?.azimut_solar || 0,
      datosMicro02?.voltaje1G_V || 0,
      datosMicro02?.corriente1G_A || 0,
      datosMicro02?.potencia1G_W || 0,
      datosMicro02?.voltaje2FIJO_V || 0,
      datosMicro02?.corriente2FIJO_A || 0,
      datosMicro02?.potencia2FIJO_W || 0,
      datosMicro02?.voltaje3FIJOA_V || 0,
      datosMicro02?.corriente3FIJOA_A || 0,
      datosMicro02?.potencia3FIJOA_W || 0,
      datosMicro02?.voltaje3FIJOB_V || 0,
      datosMicro02?.corriente3FIJOB_A || 0,
      datosMicro02?.potencia3FIJOB_W || 0,
      
      // DATOS CLIMÁTICOS
      datosMicro02?.temperatura_externa || 0,
      datosMicro02?.humedad_externa || 0,
      datosMicro02?.presion_atmosferica_hPa || 0,
      datosMicro02?.velocidad_viento || 0,
      datosMicro02?.direccion_viento || 0,
      datosMicro02?.condicion_clima || 'No disponible',
      datosMicro02?.nubosidad || 0,
      datosMicro02?.calidad_aire || 0
    ];
    
    hoja.appendRow(nuevaFila);
    console.log("✅ Fila " + hoja.getLastRow() + " agregada a hoja combinada");
    return true;
    
  } catch (error) {
    console.error("❌ Error guardando en hoja combinada:", error);
    return false;
  }
}

// ===========================================
// MODIFICAR doPost PARA GUARDAR TAMBIÉN EN COMBINADA
// ===========================================
function doPost(e) {
  console.log("=".repeat(50));
  console.log("📡 " + new Date().toLocaleString());
  
  try {
    // VERIFICAR DATOS
    if (!e || !e.postData || !e.postData.contents) {
      return responderError("No hay datos");
    }
    
    // PARSEAR JSON
    var data = JSON.parse(e.postData.contents);
    var dispositivoId = data.dispositivo_id || 'desconocido';
    console.log("📦 Dispositivo:", dispositivoId);
    
    // CREAR HOJAS SI NO EXISTEN
    crearHojasUnaVez();
    
    // CONTROL DE TIEMPO PERSISTENTE
    var ahora = new Date().getTime();
    var ultimoTimestamp = obtenerTimestamp(dispositivoId);
    
    if (ultimoTimestamp) {
      var tiempoTranscurrido = ahora - ultimoTimestamp;
      if (tiempoTranscurrido < 15000) {
        var segundosFaltantes = ((15000 - tiempoTranscurrido) / 1000).toFixed(1);
        return responderWaiting(dispositivoId, segundosFaltantes);
      }
    }
    
    // DETECTAR TIPO DE MICRO Y GUARDAR
    var guardadoExitoso = false;
    var datosMicro01 = null;
    var datosMicro02 = null;
    
    if (data.elevacion_servo !== undefined || data.ldr_norte !== undefined) {
      console.log("🎯 MICRO 01 (Seguimiento Solar)");
      guardadoExitoso = guardarDatosESP32_01(data);
      datosMicro01 = data;  // Guardar para combinada
      
      // Intentar obtener últimos datos del micro 02
      datosMicro02 = obtenerUltimosDatosMicro02();
      
    } 
    else if (data.voltaje1G_V !== undefined) {
      console.log("🎯 MICRO 02 (Paneles Solares)");
      guardadoExitoso = guardarDatosESP32_02(data);
      datosMicro02 = data;  // Guardar para combinada
      
      // Intentar obtener últimos datos del micro 01
      datosMicro01 = obtenerUltimosDatosMicro01();
    } 
    else {
      return responderError("Tipo de datos no reconocido");
    }
    
    // GUARDAR EN HOJA COMBINADA (si tenemos datos de ambos micros)
    if (guardadoExitoso && datosMicro01 && datosMicro02) {
      guardarEnHojaCombinada(datosMicro01, datosMicro02);
    } else if (guardadoExitoso) {
      console.log("⏳ Esperando datos del otro micro para combinada");
    }
    
    // ACTUALIZAR TIMESTAMP
    if (guardadoExitoso) {
      guardarTimestamp(dispositivoId, ahora);
      return responderOK(dispositivoId);
    } else {
      return responderError("Error al guardar");
    }
    
  } catch (error) {
    console.error("❌ ERROR:", error);
    return responderError(error.toString());
  }
}

// ===========================================
// FUNCIONES PARA OBTENER ÚLTIMOS DATOS
// ===========================================
function obtenerUltimosDatosMicro01() {
  try {
    var libro = SpreadsheetApp.openById(SPREADSHEET_ID);
    var hoja = libro.getSheetByName('2G_Datos_crudos_Seguimiento_Solar');
    
    if (!hoja || hoja.getLastRow() < 2) return null;
    
    var ultimaFila = hoja.getLastRow();
    var datos = hoja.getRange(ultimaFila, 1, 1, hoja.getLastColumn()).getValues()[0];
    
    return {
      dispositivo_nombre: datos[1],
      modo_seguimiento: datos[4],
      elevacion_servo: datos[5],
      azimut_servo: datos[6],
      temp_local: datos[7],
      hum_local: datos[8],
      luz_local: datos[9],
      voltaje_5v: datos[10],
      corriente_5v: datos[11],
      potencia_5v: datos[12],
      elevacion_solar: datos[17],
      azimut_solar: datos[18]
    };
  } catch (error) {
    console.error("❌ Error obteniendo datos micro 01:", error);
    return null;
  }
}

function obtenerUltimosDatosMicro02() {
  try {
    var libro = SpreadsheetApp.openById(SPREADSHEET_ID);
    var hoja = libro.getSheetByName('Datos_crudos_1G_+FIJOS');
    
    if (!hoja || hoja.getLastRow() < 2) return null;
    
    var ultimaFila = hoja.getLastRow();
    var datos = hoja.getRange(ultimaFila, 1, 1, hoja.getLastColumn()).getValues()[0];
    
    return {
      dispositivo_nombre: datos[1],
      modo_seguimiento: datos[4],
      azimut_servo: datos[5],
      azimut_solar: datos[6],
      voltaje1G_V: datos[9],
      corriente1G_A: datos[10],
      potencia1G_W: datos[11],
      voltaje2FIJO_V: datos[12],
      corriente2FIJO_A: datos[13],
      potencia2FIJO_W: datos[14],
      voltaje3FIJOA_V: datos[15],
      corriente3FIJOA_A: datos[16],
      potencia3FIJOA_W: datos[17],
      voltaje3FIJOB_V: datos[18],
      corriente3FIJOB_A: datos[19],
      potencia3FIJOB_W: datos[20],
      temperatura_externa: datos[21],
      humedad_externa: datos[22],
      presion_atmosferica_hPa: datos[23],
      velocidad_viento: datos[24],
      direccion_viento: datos[25],
      condicion_clima: datos[26],
      nubosidad: datos[27],
      calidad_aire: datos[28]
    };
  } catch (error) {
    console.error("❌ Error obteniendo datos micro 02:", error);
    return null;
  }
}

// ===========================================
// FUNCIÓN PARA COMBINAR MANUALMENTE (OPCIONAL)
// ===========================================
function combinarDatosManualmente() {
  console.log("🔄 Combinando últimos datos manualmente...");
  
  var datosMicro01 = obtenerUltimosDatosMicro01();
  var datosMicro02 = obtenerUltimosDatosMicro02();
  
  if (datosMicro01 && datosMicro02) {
    guardarEnHojaCombinada(datosMicro01, datosMicro02);
    console.log("✅ Datos combinados guardados");
  } else {
    console.log("⚠️ No hay suficientes datos para combinar");
    console.log("Micro 01:", datosMicro01 ? "OK" : "No disponible");
    console.log("Micro 02:", datosMicro02 ? "OK" : "No disponible");
  }
}

// ===========================================
// FUNCIONES DE TIMESTAMP PERSISTENTE
// ===========================================
function guardarTimestamp(dispositivoId, timestamp) {
  var properties = PropertiesService.getScriptProperties();
  var todosLosTimestamps = properties.getProperty('ULTIMOS_TIMESTAMPS');
  
  var timestamps = {};
  if (todosLosTimestamps) {
    timestamps = JSON.parse(todosLosTimestamps);
  }
  
  timestamps[dispositivoId] = timestamp;
  properties.setProperty('ULTIMOS_TIMESTAMPS', JSON.stringify(timestamps));
}

function obtenerTimestamp(dispositivoId) {
  var properties = PropertiesService.getScriptProperties();
  var todosLosTimestamps = properties.getProperty('ULTIMOS_TIMESTAMPS');
  
  if (!todosLosTimestamps) return null;
  
  var timestamps = JSON.parse(todosLosTimestamps);
  return timestamps[dispositivoId] || null;
}

// ===========================================
// FUNCIONES DE RESPUESTA
// ===========================================
function responderOK(dispositivoId) {
  return ContentService
    .createTextOutput(JSON.stringify({
      status: "SAVED",
      message: "Datos guardados (cada 15s)",
      dispositivo: dispositivoId,
      next_save_in: "15",
      timestamp: new Date().toLocaleString()
    }))
    .setMimeType(ContentService.MimeType.JSON);
}

function responderWaiting(dispositivoId, segundos) {
  return ContentService
    .createTextOutput(JSON.stringify({
      status: "WAITING",
      message: "Esperando " + segundos + "s",
      dispositivo: dispositivoId,
      next_save_in: segundos,
      timestamp: new Date().toLocaleString()
    }))
    .setMimeType(ContentService.MimeType.JSON);
}

function responderError(mensaje) {
  return ContentService
    .createTextOutput(JSON.stringify({
      status: "ERROR",
      message: mensaje,
      timestamp: new Date().toLocaleString()
    }))
    .setMimeType(ContentService.MimeType.JSON);
}

// ===========================================
// GUARDAR DATOS ESP32 01 
// ===========================================
function guardarDatosESP32_01(data) {
  console.log("💾 Guardando ESP32 01...");
  try {
    var libro = SpreadsheetApp.openById(SPREADSHEET_ID);
    var hoja = libro.getSheetByName('2G_Datos_crudos_Seguimiento_Solar');
    
    var ahora = new Date();
    var fecha = Utilities.formatDate(ahora, Session.getScriptTimeZone(), 'dd/MM/yyyy');
    var hora = Utilities.formatDate(ahora, Session.getScriptTimeZone(), 'HH:mm:ss');
    
    var fila = [
      data.dispositivo_id || 'ESP32-SOLAR-01',
      data.dispositivo_nombre || 'Seguimiento_Solar2G',
      fecha,
      hora,
      data.modo_seguimiento || 0,
      data.elevacion_servo || 0,
      data.azimut_servo || 0,
      data.temp_local || 0,
      data.hum_local || 0,
      data.luz_local || 0,
      data.voltaje_5v || 0,
      data.corriente_5v || 0,
      data.potencia_5v || 0,
      data.ldr_norte || 0,
      data.ldr_sur || 0,
      data.ldr_este || 0,
      data.ldr_oeste || 0,
      data.elevacion_solar || 0,
      data.azimut_solar || 0,
      data.ip_dispositivo || '',
      data.rssi_wifi || 0
    ];
    
    hoja.appendRow(fila);
    console.log("✅ Fila " + hoja.getLastRow());
    return true;
  } catch (error) {
    console.error("❌ Error:", error);
    return false;
  }
}

// ===========================================
// GUARDAR DATOS ESP32 02 
// ===========================================
function guardarDatosESP32_02(data) {
  console.log("💾 Guardando ESP32 02...");
  try {
    var libro = SpreadsheetApp.openById(SPREADSHEET_ID);
    var hoja = libro.getSheetByName('Datos_crudos_1G_+FIJOS');
    
    var ahora = new Date();
    var fecha = Utilities.formatDate(ahora, Session.getScriptTimeZone(), 'dd/MM/yyyy');
    var hora = Utilities.formatDate(ahora, Session.getScriptTimeZone(), 'HH:mm:ss');
    
    var fila = [
      data.dispositivo_id || 'ESP32-PANELES-02',
      data.dispositivo_nombre || 'Paneles_Solares_1G_y_Fijos',
      fecha,
      hora,
      data.modo_seguimiento || 0,
      data.azimut_servo || 0,
      data.azimut_solar || 0,
      data.ldr_este || 0,
      data.ldr_oeste || 0,
      data.voltaje1G_V || 0,
      data.corriente1G_A || 0,
      data.potencia1G_W || 0,
      data.voltaje2FIJO_V || 0,
      data.corriente2FIJO_A || 0,
      data.potencia2FIJO_W || 0,
      data.voltaje3FIJOA_V || 0,
      data.corriente3FIJOA_A || 0,
      data.potencia3FIJOA_W || 0,
      data.voltaje3FIJOB_V || 0,
      data.corriente3FIJOB_A || 0,
      data.potencia3FIJOB_W || 0,
      data.temperatura_externa || 0,
      data.humedad_externa || 0,
      data.presion_atmosferica_hPa || 0,
      data.velocidad_viento || 0,
      data.direccion_viento || 0,
      data.condicion_clima || 'No disponible',
      data.nubosidad || 0,
      data.calidad_aire || 0,
      data.ip_dispositivo || '',
      data.rssi_wifi || 0
    ];
    
    hoja.appendRow(fila);
    console.log("✅ Fila " + hoja.getLastRow());
    return true;
  } catch (error) {
    console.error("❌ Error:", error);
    return false;
  }
}

// ===========================================
// DOGET PARA VERIFICAR
// ===========================================
function doGet() {
  crearHojasUnaVez();
  
  return ContentService
    .createTextOutput(JSON.stringify({
      status: "ready",
      service: "Solar Tracker API",
      hojas: [
        "2G_Datos_crudos_Seguimiento_Solar",
        "Datos_crudos_1G_+FIJOS",
        "Datos_Combinados_2G_1G+FIJOS (NUEVA)"
      ],
      timestamp: new Date().toLocaleString()
    }))
    .setMimeType(ContentService.MimeType.JSON);
}