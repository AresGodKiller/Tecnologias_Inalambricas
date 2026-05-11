-- Base de datos del sistema EcoPoints v2
-- Importar en Laragon: abre HeidiSQL o phpMyAdmin y ejecuta este archivo completo.

DROP DATABASE IF EXISTS `nfc_reciclaje`;

CREATE DATABASE `nfc_reciclaje`
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;

USE `nfc_reciclaje`;


-- Datos de cada participante del sistema.
-- La columna pin ya no se usa para el login, solo se conserva para no romper
-- compatibilidad con versiones anteriores.
CREATE TABLE `usuarios` (
  `id_usuario`     INT          NOT NULL AUTO_INCREMENT,
  `nombre`         VARCHAR(100) NOT NULL,
  `apellido`       VARCHAR(100) NOT NULL,
  `email`          VARCHAR(100) NOT NULL,
  `telefono`       VARCHAR(20)  DEFAULT NULL,
  `pin`            CHAR(4)      NOT NULL DEFAULT '0000'
                     COMMENT 'Ya no se usa para login. Se mantiene por compatibilidad.',
  `puntos_totales` INT          NOT NULL DEFAULT 0,
  `estado`         ENUM('activo','inactivo') DEFAULT 'activo',
  `fecha_registro` TIMESTAMP    NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_usuario`),
  UNIQUE KEY `email` (`email`),
  KEY `idx_estado` (`estado`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- Vincula cada tarjeta NFC con su usuario.
-- Un mismo usuario puede tener varias tarjetas, cada una en una fila distinta.
CREATE TABLE `usuarios_nfc` (
  `id`         INT         NOT NULL AUTO_INCREMENT,
  `id_usuario` INT         NOT NULL,
  `uid_nfc`    VARCHAR(50) NOT NULL
                 COMMENT 'UID hexadecimal de la tarjeta NFC, ej: 0D1B1207',
  `fecha_alta` TIMESTAMP   NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uid_nfc` (`uid_nfc`),
  KEY `idx_id_usuario` (`id_usuario`),
  CONSTRAINT `fk_nfc_usuario`
    FOREIGN KEY (`id_usuario`)
    REFERENCES `usuarios` (`id_usuario`)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- Catálogo de tipos de botella reconocidos por el sistema.
-- Con un solo botón, la app siempre usa id_tipo=1.
-- Si en el futuro se agregan dos botones, se usa también id_tipo=2.
CREATE TABLE `tipos_botella` (
  `id_tipo`         INT          NOT NULL AUTO_INCREMENT,
  `nombre`          VARCHAR(50)  NOT NULL,
  `capacidad_ml`    INT          NOT NULL,
  `puntos`          INT          NOT NULL DEFAULT 5,
  `descripcion`     VARCHAR(200) DEFAULT NULL,
  `color_ui`        VARCHAR(20)  DEFAULT '#2ecc71',
  PRIMARY KEY (`id_tipo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `tipos_botella`
  (`id_tipo`, `nombre`, `capacidad_ml`, `puntos`, `descripcion`, `color_ui`)
VALUES
  (1, 'Botella 600ml', 600,  5,  'Botella PET pequeña de 600 mililitros', '#2980b9'),
  (2, 'Botella 1L',    1000, 10, 'Botella PET grande de 1 litro',         '#27ae60');


-- Cada fila representa un evento de reciclaje: qué usuario recicló y cuántos puntos ganó.
-- uid_leido guarda 'BOTON' cuando el evento viene del botón físico.
CREATE TABLE `registro_reciclaje` (
  `id_registro`      INT         NOT NULL AUTO_INCREMENT,
  `id_usuario`       INT         NOT NULL,
  `id_tipo`          INT         NOT NULL,
  `uid_leido`        VARCHAR(50) NOT NULL
                       COMMENT 'UID de la tarjeta de botella, o BOTON si vino del pulsador',
  `puntos_otorgados` INT         NOT NULL,
  `fecha_hora`       TIMESTAMP   NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_registro`),
  KEY `idx_usuario` (`id_usuario`),
  KEY `idx_tipo`    (`id_tipo`),
  KEY `idx_fecha`   (`fecha_hora`),
  CONSTRAINT `fk_rr_usuario`
    FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`) ON DELETE CASCADE,
  CONSTRAINT `fk_rr_tipo`
    FOREIGN KEY (`id_tipo`)    REFERENCES `tipos_botella` (`id_tipo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- Usuarios de prueba. Se pueden borrar antes de pasar a producción.
INSERT INTO `usuarios`
  (`id_usuario`, `nombre`, `apellido`, `email`, `telefono`, `pin`, `puntos_totales`, `estado`)
VALUES
  (1, 'Juan',   'García',   'juan.garcia@empresa.com',    '5551234567', '0000', 0, 'activo'),
  (2, 'María',  'López',    'maria.lopez@empresa.com',    '5559876543', '0000', 0, 'activo'),
  (3, 'Carlos', 'Martínez', 'carlos.martinez@empresa.com','5552468135', '0000', 0, 'activo'),
  (4, 'Axel',   'Yoab',     'axel@gmail.com',             '4491234556', '0000', 0, 'activo'),
  (5, 'Damian', 'Piñata',   'dami@gmail.com',             '4491234566', '0000', 0, 'activo');

-- Tarjetas de prueba. Hay que reemplazar los UID con los de las tarjetas reales.
-- Para saber el UID: abrir el Monitor Serial del Arduino IDE a 115200 baud
-- y acercar la tarjeta. Aparecerá una línea como: UID CONCATENADO:0D1B1207
INSERT INTO `usuarios_nfc` (`id_usuario`, `uid_nfc`) VALUES
  (1, '0D1B1207'),   -- tarjeta de Juan
  (2, '491C3307');   -- tarjeta de María


-- Ranking de usuarios activos ordenado por puntos. También muestra cuántas
-- botellas de cada tipo ha reciclado cada quien.
CREATE OR REPLACE VIEW `vista_ranking` AS
  SELECT
    u.id_usuario,
    CONCAT(u.nombre, ' ', u.apellido)            AS nombre_completo,
    u.puntos_totales,
    COUNT(rr.id_registro)                         AS total_reciclajes,
    COALESCE(SUM(CASE WHEN tb.capacidad_ml = 600  THEN 1 ELSE 0 END), 0) AS botellas_600ml,
    COALESCE(SUM(CASE WHEN tb.capacidad_ml = 1000 THEN 1 ELSE 0 END), 0) AS botellas_1L
  FROM usuarios u
  LEFT JOIN registro_reciclaje rr ON u.id_usuario = rr.id_usuario
  LEFT JOIN tipos_botella tb       ON rr.id_tipo   = tb.id_tipo
  WHERE u.estado = 'activo'
  GROUP BY u.id_usuario, u.nombre, u.apellido, u.puntos_totales
  ORDER BY u.puntos_totales DESC;


-- Registra un reciclaje de forma segura en una sola operación.
-- Recibe el id del usuario y el tipo de botella, inserta el evento
-- y actualiza los puntos del usuario. Devuelve los puntos ganados y el nuevo total.
DELIMITER //
CREATE PROCEDURE `registrar_reciclaje` (
  IN  p_id_usuario INT,
  IN  p_id_tipo    INT
)
BEGIN
  DECLARE v_puntos      INT DEFAULT 0;
  DECLARE v_pts_totales INT DEFAULT 0;

  SELECT puntos INTO v_puntos
    FROM tipos_botella
   WHERE id_tipo = p_id_tipo
   LIMIT 1;

  IF v_puntos > 0 THEN
    INSERT INTO registro_reciclaje (id_usuario, id_tipo, uid_leido, puntos_otorgados)
    VALUES (p_id_usuario, p_id_tipo, 'BOTON', v_puntos);

    UPDATE usuarios
       SET puntos_totales = puntos_totales + v_puntos
     WHERE id_usuario = p_id_usuario;

    SELECT puntos_totales INTO v_pts_totales
      FROM usuarios
     WHERE id_usuario = p_id_usuario;

    SELECT v_puntos AS puntos_otorgados, v_pts_totales AS puntos_totales_nuevos;
  ELSE
    SELECT 0 AS puntos_otorgados, 0 AS puntos_totales_nuevos;
  END IF;
END//
DELIMITER ;


-- Asocia un UID NFC a un usuario que ya existe en la base de datos.
-- Útil para asignar tarjetas desde fuera de la app.
-- INSERT IGNORE evita errores si el UID ya estaba registrado.
DELIMITER //
CREATE PROCEDURE `vincular_tarjeta` (
  IN p_id_usuario INT,
  IN p_uid_nfc    VARCHAR(50)
)
BEGIN
  INSERT IGNORE INTO usuarios_nfc (id_usuario, uid_nfc)
  VALUES (p_id_usuario, p_uid_nfc);
  SELECT ROW_COUNT() AS vinculado;
END//
DELIMITER ;


-- Últimas 100 transacciones con el nombre del usuario, tipo de botella y puntos ganados.
CREATE OR REPLACE VIEW `vista_historial_reciente` AS
  SELECT
    rr.id_registro,
    rr.fecha_hora,
    CONCAT(u.nombre, ' ', u.apellido) AS usuario,
    tb.nombre                          AS tipo_botella,
    tb.capacidad_ml,
    rr.puntos_otorgados,
    rr.uid_leido
  FROM registro_reciclaje rr
  JOIN usuarios      u  ON rr.id_usuario = u.id_usuario
  JOIN tipos_botella tb ON rr.id_tipo    = tb.id_tipo
  ORDER BY rr.fecha_hora DESC
  LIMIT 100;
