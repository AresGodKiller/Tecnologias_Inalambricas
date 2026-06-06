/**
 * server.js — Servidor puente del Arcade RFID
 * 
 *
 * Este archivo es el servidor Node.js que corre en la Mac del equipo
 * y actúa como intermediario entre el ESP32 y la base de datos SQL Server
 * que corre en Docker.
 *
 * Se encarga de tres cosas:
 *   1. Recibir el puntaje del jugador desde el ESP32 (POST) y acumularlo
 *      al total histórico que tiene en la base de datos
 *   2. Consultar si una tarjeta ya tiene un jugador registrado (GET)
 *      y devolver su saldo acumulado cuando el launcher lo pide
 *   3. Mantener un "buzón" en memoria con el último jugador escaneado
 *      para que Python pueda leerlo y saber cuándo arrancar el juego
 *
 * Flujo de datos:
 *   ESP32 detecta tarjeta  →  GET /api/puntuaciones/:rfid  →  server consulta BD
 *   Jugador termina partida →  Python manda score al ESP32 por Serial
 *   ESP32 recibe score      →  POST /api/puntuaciones       →  server actualiza BD
 *
 * Para arrancar este servidor:
 *   node server.js
 *
 * Dependencias (instalar con npm install):
 *   express     — framework para definir las rutas de la API
 *   cors        — permite peticiones desde otros dispositivos en la red
 *   body-parser — permite leer el body JSON de las peticiones POST
 *   mssql       — cliente para conectarse a SQL Server
 */

const express    = require('express');
const cors       = require('cors');
const bodyParser = require('body-parser');
const sql        = require('mssql');

const app = express();

// Middlewares que se aplican a todas las peticiones antes de llegar a las rutas:
//   cors:        permite que el ESP32 y Python hagan peticiones desde otros dispositivos
//   bodyParser:  convierte el body JSON de las peticiones a un objeto JavaScript
app.use(cors());
app.use(bodyParser.json());


// 
//  CONFIGURACIÓN DE LA BASE DE DATOS
// 

// Datos de conexión al contenedor Docker que corre en esta misma Mac.
// Si el contenedor cambia de contraseña o puerto, hay que actualizar estos valores.
const dbConfig = {
    user:     'sa',
    password: 'C0NTR453N1!4',      // Contraseña del usuario sa configurada al crear el contenedor
    server:   '127.0.0.1',          // La BD está en esta misma máquina dentro de Docker
    database: 'arcade_db',          // Nombre de la base de datos del proyecto
    port:     1433,                  // Puerto estándar de SQL Server mapeado en Docker
    options: {
        encrypt:               false,  // No se usa SSL porque es conexión local
        trustServerCertificate: true   // Necesario para evitar errores de certificado en local
    }
};


// 
//  BUZÓN EN MEMORIA
// 

// Variable global que guarda el estado del último jugador escaneado.
// Funciona como un buzón: el GET de la tarjeta lo llena con los datos
// del jugador, y el endpoint /api/ultimo-movimiento lo entrega a Python
// y lo vacía inmediatamente para que no se lea dos veces.
//
// El estado vacío usa "--------" como id_rfid para que Python pueda
// distinguir fácilmente entre "hay un jugador esperando" y "no hay nadie".
let ultimoEscaneo = {
    id_rfid:   "--------",
    usr:       "Esperando...",
    score:     0,
    name_disp: "Ninguno"
};


// 
//  RUTA 1 — POST /api/puntuaciones
//  Recibe el puntaje al terminar la partida y lo acumula al total
// 

/**
 * El ESP32 llama a esta ruta después de que Python le manda el puntaje
 * de la sesión por Serial. El servidor busca al jugador en la base de datos
 * por su id_rfid y suma los puntos nuevos a su acumulado histórico.
 *
 * Body esperado (JSON):
 *   {
 *     name_disp: "Nombre del jugador",
 *     usr:       "nombre_usuario",
 *     score:     150,
 *     id_rfid:   "AABB1122"
 *   }
 *
 * Respuesta exitosa (200):
 *   {
 *     status:      "success",
 *     action:      "update" | "insert",
 *     total_score: 350
 *   }
 */
app.post('/api/puntuaciones', async (req, res) => {
    const { name_disp, usr, score, id_rfid } = req.body;

    console.log(`\n[API POST] Procesando puntos -> RFID: ${id_rfid} | Puntos a reportar: ${score}`);

    try {
        let pool = await sql.connect(dbConfig);

        // Buscar si ya existe un registro para esta tarjeta en la base de datos
        let resultado = await pool.request()
            .input('id_rfid', sql.VarChar, id_rfid)
            .query(`SELECT SCORE FROM puntuaciones WHERE ID_RFID = @id_rfid`);

        let nuevoTotal = score;

        if (resultado.recordset.length > 0) {
            // El jugador ya existe: sumar los puntos nuevos a su acumulado histórico
            let puntosActuales = resultado.recordset[0].SCORE;
            nuevoTotal = puntosActuales + score;

            await pool.request()
                .input('nuevo_score', sql.Int,     nuevoTotal)
                .input('name_disp',   sql.VarChar, name_disp)
                .input('usr',         sql.VarChar, usr)
                .input('id_rfid',     sql.VarChar, id_rfid)
                .query(`UPDATE puntuaciones 
                        SET SCORE = @nuevo_score, NAME_DISP = @name_disp, USR = @usr, LAST_GAME = GETDATE()
                        WHERE ID_RFID = @id_rfid`);

            console.log(`[SQL] Puntos acumulados. Total anterior: ${puntosActuales} | Nuevo total: ${nuevoTotal}`);

        } else {
            // Jugador nuevo: crear su primera fila con los puntos de esta sesión
            await pool.request()
                .input('name_disp', sql.VarChar, name_disp)
                .input('usr',       sql.VarChar, usr)
                .input('score',     sql.Int,     score)
                .input('id_rfid',   sql.VarChar, id_rfid)
                .query(`INSERT INTO puntuaciones (NAME_DISP, USR, SCORE, ID_RFID) 
                        VALUES (@name_disp, @usr, @score, @id_rfid)`);

            console.log("[SQL] Jugador nuevo registrado en la base de datos.");
        }

        // Vaciar el buzón después de guardar la partida.
        // Esto es importante: si el buzón quedara con datos del jugador que
        // acaba de terminar, Python lo leería de nuevo y arrancaría el juego
        // otra vez sin esperar una nueva tarjeta.
        ultimoEscaneo = {
            id_rfid:   "--------",
            usr:       "Esperando...",
            score:     0,
            name_disp: "Ninguno"
        };

        res.status(200).json({
            status:      "success",
            action:      resultado.recordset.length > 0 ? "update" : "insert",
            total_score: nuevoTotal
        });

    } catch (err) {
        console.error("[ERROR SQL POST]", err.message);
        res.status(500).json({ status: "error", message: err.message });
    }
});


// 
//  RUTA 2 — GET /api/puntuaciones/:rfid
//  Consulta el saldo acumulado de un jugador por su UID de tarjeta
// 

/**
 * Python llama a esta ruta cuando el ESP32 le manda un UID por Serial.
 * El servidor busca ese UID en la base de datos y devuelve si el jugador
 * existe y cuántos puntos acumulados tiene.
 *
 * También llena el buzón (ultimoEscaneo) con los datos del jugador
 * para que el endpoint /api/ultimo-movimiento los pueda entregar.
 *
 * Parámetros de URL:
 *   :rfid — el UID de la tarjeta en formato hexadecimal (ejemplo: AABB1122)
 *
 * Respuesta si el jugador existe (200):
 *   { existe: true, score: 350, usr: "nombre_usuario" }
 *
 * Respuesta si es tarjeta nueva (200):
 *   { existe: false, score: 0, usr: "User_AABB" }
 */
app.get('/api/puntuaciones/:rfid', async (req, res) => {
    const rfidConsultado = req.params.rfid;
    console.log(`\n[API GET] Consultando puntos del RFID: ${rfidConsultado}`);

    try {
        let pool = await sql.connect(dbConfig);
        let resultado = await pool.request()
            .input('id_rfid', sql.VarChar, rfidConsultado)
            .query(`SELECT SCORE, USR FROM puntuaciones WHERE ID_RFID = @id_rfid`);

        if (resultado.recordset.length > 0) {
            // Jugador conocido: devolver su saldo y llenar el buzón con sus datos
            console.log(`[SQL] Tarjeta encontrada. Saldo actual: ${resultado.recordset[0].SCORE} pts.`);

            ultimoEscaneo = {
                id_rfid:   rfidConsultado,
                usr:       resultado.recordset[0].USR,
                score:     resultado.recordset[0].SCORE,
                name_disp: "Arcade_ESP32_WiFi"
            };

            res.status(200).json({
                existe: true,
                score:  resultado.recordset[0].SCORE,
                usr:    resultado.recordset[0].USR
            });

        } else {
            // Tarjeta nueva: generar un nombre de usuario genérico basado en los
            // primeros 4 caracteres del UID y llenar el buzón con score en 0
            console.log(`[SQL] Tarjeta nueva. Iniciando cuenta en 0 pts.`);

            ultimoEscaneo = {
                id_rfid:   rfidConsultado,
                usr:       `User_${rfidConsultado.substring(0, 4)}`,
                score:     0,
                name_disp: "Arcade_ESP32_WiFi"
            };

            res.status(200).json({
                existe: false,
                score:  0,
                usr:    `User_${rfidConsultado.substring(0, 4)}`
            });
        }

    } catch (err) {
        console.error("[ERROR SQL GET]", err.message);
        res.status(500).json({ error: err.message });
    }
});


// 
//  RUTA 3 — GET /api/ultimo-movimiento
//  Entrega el último escaneo a Python y vacía el buzón
// 

/**
 * Python llama a esta ruta periódicamente para saber si hay un jugador
 * esperando iniciar una partida. El launcher también la usa al arrancar
 * para verificar que el servidor está corriendo (si responde, el servidor
 * está activo).
 *
 * Esta ruta siempre responde con el estado actual del buzón y lo vacía
 * inmediatamente después de enviarlo. De esta forma Python no puede leer
 * el mismo escaneo dos veces aunque haga múltiples peticiones seguidas.
 *
 * Respuesta (200):
 *   {
 *     id_rfid:   "AABB1122" | "--------",
 *     usr:       "nombre_usuario" | "Esperando...",
 *     score:     350 | 0,
 *     name_disp: "Nombre" | "Ninguno"
 *   }
 *
 * Python sabe que hay un jugador si id_rfid != "--------".
 */
app.get('/api/ultimo-movimiento', (req, res) => {
    // Entregar el estado actual del buzón a Python
    res.status(200).json(ultimoEscaneo);

    // Vaciar el buzón inmediatamente después de enviarlo.
    // Si no se vaciara aquí, Python leería los mismos datos en la siguiente
    // petición y lanzaría el juego dos veces con el mismo jugador.
    ultimoEscaneo = {
        id_rfid:   "--------",
        usr:       "Esperando...",
        score:     0,
        name_disp: "Ninguno"
    };
});


// 
//  ARRANQUE DEL SERVIDOR
// 

const PORT = 3000;

app.listen(PORT, () => {
    console.log(`====================================================================`);
    console.log(`  Servidor Arcade corriendo en el puerto ${PORT}`);
    console.log(`  Esperando peticiones del ESP32 y del launcher de Python...`);
    console.log(`====================================================================`);
});
