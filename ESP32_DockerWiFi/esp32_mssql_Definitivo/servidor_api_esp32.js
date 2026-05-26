// Servidor REST intermediario para ESP32 -> MSSQL
// npm install express sql mssql cors body-parser

const express = require('express');
const sql = require('mssql');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());

// Configuración de MSSQL
const config = {
  server: '192.168.100.145',  // Tu IP local ✓
  port: 1433,
  user: 'sa',
  password: 'C0NTR453N1!4',   // ← La que usaste al crear el contenedor
  database: 'basicos',         // ← La BD que creaste
  options: {
    encrypt: false,
    trustServerCertificate: true
  }
};

// Ruta para hacer INSERT
app.post('/api/insert', async (req, res) => {
  try {
    // Obtener datos del cuerpo de la petición
    const { nombre, valor, temperatura } = req.body;

    // Conectar a la BD
    let pool = await sql.connect(config);

    // Ejecutar INSERT
    let result = await pool.request()
      .input('nombre', sql.VarChar(50), nombre || 'ESP32')
      .input('valor', sql.Int, valor || Math.floor(Math.random() * 100))
      .input('temperatura', sql.Float, temperatura || 25.5)
      .query('INSERT INTO test (nombre, valor, temperatura) VALUES (@nombre, @valor, @temperatura)');

    // Cerrar conexión
    await pool.close();

    // Respuesta exitosa
    res.json({
      success: true,
      message: 'Datos insertados correctamente',
      rowsAffected: result.rowsAffected[0]
    });

  } catch (err) {
    console.error('Error:', err);
    res.status(500).json({
      success: false,
      message: 'Error al insertar datos',
      error: err.message
    });
  }
});

// Ruta de prueba de conexión
app.get('/api/test', async (req, res) => {
  try {
    let pool = await sql.connect(config);
    await pool.close();
    
    res.json({
      success: true,
      message: 'Conexión a MSSQL exitosa'
    });
  } catch (err) {
    res.status(500).json({
      success: false,
      message: 'Error de conexión a MSSQL',
      error: err.message
    });
  }
});

// Iniciar servidor
const PORT = 3000;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Servidor API corriendo en http://0.0.0.0:${PORT}`);
  console.log('Esperando conexiones de ESP32...');
});
