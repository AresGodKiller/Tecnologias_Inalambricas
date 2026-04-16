-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Versión del servidor:         8.4.3 - MySQL Community Server - GPL
-- SO del servidor:              Win64
-- HeidiSQL Versión:             12.8.0.6908
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- Volcando estructura de base de datos para nfc_control_acceso
CREATE DATABASE IF NOT EXISTS `nfc_control_acceso` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `nfc_control_acceso`;

-- Volcando estructura para función nfc_control_acceso.obtener_usuario_por_uid
DELIMITER //
CREATE FUNCTION `obtener_usuario_por_uid`(uid_hex VARCHAR(50)) RETURNS int
    READS SQL DATA
    DETERMINISTIC
BEGIN
  DECLARE id_user INT;
  
  SELECT id_usuario INTO id_user
  FROM tarjetas_nfc
  WHERE uid_hexadecimal = uid_hex AND estado = 'activa'
  LIMIT 1;
  
  RETURN IFNULL(id_user, 0);
END//
DELIMITER ;

-- Volcando estructura para procedimiento nfc_control_acceso.registrar_acceso
DELIMITER //
CREATE PROCEDURE `registrar_acceso`(
  IN p_uid_leido VARCHAR(50),
  IN p_tipo_acceso VARCHAR(20)
)
BEGIN
  DECLARE v_id_usuario INT;
  DECLARE v_id_tarjeta INT;
  DECLARE v_estado_validacion VARCHAR(50);
  
  -- Obtener usuario y tarjeta por UID
  SELECT id_usuario, id_tarjeta INTO v_id_usuario, v_id_tarjeta
  FROM tarjetas_nfc
  WHERE uid_hexadecimal = p_uid_leido AND estado = 'activa'
  LIMIT 1;
  
  -- Determinar estado de validación
  IF v_id_usuario IS NOT NULL THEN
    SET v_estado_validacion = 'exitoso';
  ELSE
    SET v_estado_validacion = 'no_registrado';
  END IF;
  
  -- Insertar en registro de acceso
  INSERT INTO registro_acceso (
    id_usuario, 
    id_tarjeta, 
    uid_leido, 
    tipo_acceso, 
    estado_validacion
  ) VALUES (
    v_id_usuario,
    v_id_tarjeta,
    p_uid_leido,
    p_tipo_acceso,
    v_estado_validacion
  );
END//
DELIMITER ;

-- Volcando estructura para tabla nfc_control_acceso.registro_acceso
CREATE TABLE IF NOT EXISTS `registro_acceso` (
  `id_acceso` int NOT NULL AUTO_INCREMENT,
  `id_usuario` int DEFAULT NULL,
  `id_tarjeta` int DEFAULT NULL,
  `uid_leido` varchar(50) DEFAULT NULL,
  `tipo_acceso` enum('entrada','salida','intento_fallido') DEFAULT 'entrada',
  `estado_validacion` enum('exitoso','fallido','no_registrado') DEFAULT 'exitoso',
  `fecha_hora` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `detalles` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id_acceso`),
  KEY `id_tarjeta` (`id_tarjeta`),
  KEY `idx_fecha_hora` (`fecha_hora`),
  KEY `idx_usuario` (`id_usuario`),
  KEY `idx_uid_leido` (`uid_leido`),
  KEY `idx_validacion` (`estado_validacion`),
  CONSTRAINT `registro_acceso_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`) ON DELETE SET NULL,
  CONSTRAINT `registro_acceso_ibfk_2` FOREIGN KEY (`id_tarjeta`) REFERENCES `tarjetas_nfc` (`id_tarjeta`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=91 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla nfc_control_acceso.registro_acceso: ~32 rows (aproximadamente)
DELETE FROM `registro_acceso`;
INSERT INTO `registro_acceso` (`id_acceso`, `id_usuario`, `id_tarjeta`, `uid_leido`, `tipo_acceso`, `estado_validacion`, `fecha_hora`, `detalles`) VALUES
	(1, 4, NULL, '0D1B1207', 'entrada', 'exitoso', '2026-04-09 17:36:13', NULL),
	(2, 4, NULL, '0D1B1207', 'entrada', 'exitoso', '2026-04-09 17:36:22', NULL),
	(3, NULL, NULL, '491C3307', 'entrada', 'no_registrado', '2026-04-09 17:36:25', NULL),
	(4, NULL, NULL, '491C3307', 'entrada', 'no_registrado', '2026-04-09 17:36:27', NULL),
	(5, 4, NULL, '0D1B1207', 'entrada', 'exitoso', '2026-04-09 17:36:35', NULL),
	(6, NULL, NULL, '491C3307', 'entrada', 'no_registrado', '2026-04-09 17:36:46', NULL),
	(7, NULL, NULL, '491C3307', 'entrada', 'no_registrado', '2026-04-09 17:36:48', NULL),
	(8, NULL, NULL, '491C3307', 'entrada', 'no_registrado', '2026-04-09 17:36:58', NULL),
	(9, 4, NULL, '0D1B1207', 'entrada', 'exitoso', '2026-04-09 17:37:00', NULL),
	(10, 4, NULL, '0D1B1207', 'entrada', 'exitoso', '2026-04-09 17:42:16', NULL),
	(11, 4, NULL, '0D1B1207', 'entrada', 'exitoso', '2026-04-09 17:42:28', NULL),
	(12, 4, NULL, '0D1B1207', 'entrada', 'exitoso', '2026-04-09 17:42:29', NULL),
	(13, 4, NULL, '0D1B1207', 'entrada', 'exitoso', '2026-04-09 17:42:30', NULL),
	(14, 4, NULL, '0D1B1207', 'entrada', 'exitoso', '2026-04-09 17:42:32', NULL),
	(15, 4, NULL, '0D1B1207', 'entrada', 'exitoso', '2026-04-09 17:42:33', NULL),
	(16, 4, NULL, '0D1B1207', 'entrada', 'exitoso', '2026-04-09 17:42:35', NULL),
	(17, 4, NULL, '0D1B1207', 'entrada', 'exitoso', '2026-04-09 18:07:28', NULL);

-- Volcando estructura para tabla nfc_control_acceso.roles
CREATE TABLE IF NOT EXISTS `roles` (
  `id_rol` int NOT NULL AUTO_INCREMENT,
  `nombre_rol` varchar(50) NOT NULL,
  `descripcion` varchar(200) DEFAULT NULL,
  `permisos_json` json DEFAULT NULL,
  PRIMARY KEY (`id_rol`),
  UNIQUE KEY `nombre_rol` (`nombre_rol`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla nfc_control_acceso.roles: ~3 rows (aproximadamente)
DELETE FROM `roles`;
INSERT INTO `roles` (`id_rol`, `nombre_rol`, `descripcion`, `permisos_json`) VALUES
	(1, 'Administrador', 'Acceso total al sistema', NULL),
	(2, 'Usuario Normal', 'Acceso básico', NULL),
	(3, 'Visitante', 'Acceso limitado temporal', NULL);

-- Volcando estructura para tabla nfc_control_acceso.tarjetas_nfc
CREATE TABLE IF NOT EXISTS `tarjetas_nfc` (
  `id_tarjeta` int NOT NULL AUTO_INCREMENT,
  `id_usuario` int NOT NULL,
  `uid_hexadecimal` varchar(50) NOT NULL,
  `uid_decimal` varchar(50) DEFAULT NULL,
  `uid_binario` varchar(200) DEFAULT NULL,
  `descripcion` varchar(200) DEFAULT NULL,
  `fecha_registro` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_vencimiento` date DEFAULT NULL,
  `estado` enum('activa','inactiva') DEFAULT 'activa',
  PRIMARY KEY (`id_tarjeta`),
  UNIQUE KEY `uid_hexadecimal` (`uid_hexadecimal`),
  KEY `idx_uid_hex` (`uid_hexadecimal`),
  KEY `idx_usuario` (`id_usuario`),
  KEY `idx_estado_tarjeta` (`estado`),
  CONSTRAINT `tarjetas_nfc_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla nfc_control_acceso.tarjetas_nfc: ~4 rows (aproximadamente)
DELETE FROM `tarjetas_nfc`;
INSERT INTO `tarjetas_nfc` (`id_tarjeta`, `id_usuario`, `uid_hexadecimal`, `uid_decimal`, `uid_binario`, `descripcion`, `fecha_registro`, `fecha_vencimiento`, `estado`) VALUES
	(1, 1, '3AB42DF1', '58:180:45:241', NULL, 'Tarjeta NFC de Juan García - Acceso principal', '2026-04-09 14:57:22', NULL, 'activa'),
	(2, 1, 'A7F8C2E4', '167:248:194:228', NULL, 'Tarjeta NFC de Juan García - Acceso secundario', '2026-04-09 14:57:22', NULL, 'activa'),
	(3, 2, '5C1D9B6E', '92:29:155:110', NULL, 'Tarjeta NFC de María López', '2026-04-09 14:57:22', NULL, 'activa'),
	(4, 3, '8E4A7D2C', '142:74:125:44', NULL, 'Tarjeta NFC de Carlos Martínez', '2026-04-09 14:57:22', NULL, 'activa'),
	(5, 4, '0D1B1207', '13:27:18:7', '00001101:00011011:00010010:00000111', 'Tarjeta NFC de Axel Yoab', '2026-04-09 15:39:06', '2026-04-09', 'activa'),
	(6, 5, '491C3307', '73:28:51:7', ' 01001001:00011100:00110011:00000111', 'Tarjeta NFC de DamianTron', '2026-04-15 17:27:10', '2026-04-15', 'activa');

-- Volcando estructura para tabla nfc_control_acceso.usuarios
CREATE TABLE IF NOT EXISTS `usuarios` (
  `id_usuario` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `apellido` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `ruta_imagen` varchar(255) DEFAULT NULL,
  `estado` enum('activo','inactivo') DEFAULT 'activo',
  `fecha_registro` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_usuario`),
  UNIQUE KEY `email` (`email`),
  KEY `idx_email` (`email`),
  KEY `idx_estado_usuario` (`estado`),
  FULLTEXT KEY `idx_nombre_apellido` (`nombre`,`apellido`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla nfc_control_acceso.usuarios: ~4 rows (aproximadamente)
DELETE FROM `usuarios`;
INSERT INTO `usuarios` (`id_usuario`, `nombre`, `apellido`, `email`, `telefono`, `ruta_imagen`, `estado`, `fecha_registro`) VALUES
	(1, 'Juan', 'García', 'juan.garcia@empresa.com', '5551234567', NULL, 'activo', '2026-04-09 14:57:22'),
	(2, 'María', 'López', 'maria.lopez@empresa.com', '5559876543', NULL, 'activo', '2026-04-09 14:57:22'),
	(3, 'Carlos', 'Martínez', 'carlos.martinez@empresa.com', '5552468135', NULL, 'activo', '2026-04-09 14:57:22'),
	(4, 'Axel', 'Yoab', 'Axel@gmail.com', '4491234556', 'C:\\\\Users\\\\Lalo\\\\Downloads\\\\Inalambricas\\\\PracticasNFC\\\\didpod.jpeg', 'activo', '2026-04-09 15:37:51'),
	(5, 'Damian', 'Piñata', 'Dami@gmail.com', '4491234566', 'C:\\\\Users\\\\Lalo\\\\Downloads\\\\Inalambricas\\\\PracticasNFC\\\\damianpod.jpeg', 'inactivo', '2026-04-15 17:22:12');

-- Volcando estructura para tabla nfc_control_acceso.usuario_roles
CREATE TABLE IF NOT EXISTS `usuario_roles` (
  `id_usuario` int NOT NULL,
  `id_rol` int NOT NULL,
  `fecha_asignacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_usuario`,`id_rol`),
  KEY `id_rol` (`id_rol`),
  CONSTRAINT `usuario_roles_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`) ON DELETE CASCADE,
  CONSTRAINT `usuario_roles_ibfk_2` FOREIGN KEY (`id_rol`) REFERENCES `roles` (`id_rol`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla nfc_control_acceso.usuario_roles: ~3 rows (aproximadamente)
DELETE FROM `usuario_roles`;
INSERT INTO `usuario_roles` (`id_usuario`, `id_rol`, `fecha_asignacion`) VALUES
	(1, 1, '2026-04-09 14:57:22'),
	(2, 2, '2026-04-09 14:57:22'),
	(3, 2, '2026-04-09 14:57:22');

-- Volcando estructura para función nfc_control_acceso.validar_uid
DELIMITER //
CREATE FUNCTION `validar_uid`(uid_hex VARCHAR(50)) RETURNS int
    READS SQL DATA
    DETERMINISTIC
BEGIN
  DECLARE resultado INT;
  
  SELECT COUNT(*) INTO resultado
  FROM tarjetas_nfc
  WHERE uid_hexadecimal = uid_hex AND estado = 'activa';
  
  RETURN resultado;
END//
DELIMITER ;

-- Volcando estructura para vista nfc_control_acceso.vista_acceso_usuarios
-- Creando tabla temporal para superar errores de dependencia de VIEW
CREATE TABLE `vista_acceso_usuarios` (
	`id_acceso` INT NOT NULL,
	`nombre` VARCHAR(1) NULL COLLATE 'utf8mb4_0900_ai_ci',
	`apellido` VARCHAR(1) NULL COLLATE 'utf8mb4_0900_ai_ci',
	`email` VARCHAR(1) NULL COLLATE 'utf8mb4_0900_ai_ci',
	`uid_hexadecimal` VARCHAR(1) NULL COLLATE 'utf8mb4_0900_ai_ci',
	`tipo_acceso` ENUM('entrada','salida','intento_fallido') NULL COLLATE 'utf8mb4_0900_ai_ci',
	`estado_validacion` ENUM('exitoso','fallido','no_registrado') NULL COLLATE 'utf8mb4_0900_ai_ci',
	`fecha_hora` TIMESTAMP NULL,
	`nombre_rol` VARCHAR(1) NULL COLLATE 'utf8mb4_0900_ai_ci'
) ENGINE=MyISAM;

-- Eliminando tabla temporal y crear estructura final de VIEW
DROP TABLE IF EXISTS `vista_acceso_usuarios`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `vista_acceso_usuarios` AS select `ra`.`id_acceso` AS `id_acceso`,`u`.`nombre` AS `nombre`,`u`.`apellido` AS `apellido`,`u`.`email` AS `email`,`tn`.`uid_hexadecimal` AS `uid_hexadecimal`,`ra`.`tipo_acceso` AS `tipo_acceso`,`ra`.`estado_validacion` AS `estado_validacion`,`ra`.`fecha_hora` AS `fecha_hora`,`r`.`nombre_rol` AS `nombre_rol` from ((((`registro_acceso` `ra` left join `usuarios` `u` on((`ra`.`id_usuario` = `u`.`id_usuario`))) left join `tarjetas_nfc` `tn` on((`ra`.`id_tarjeta` = `tn`.`id_tarjeta`))) left join `usuario_roles` `ur` on((`u`.`id_usuario` = `ur`.`id_usuario`))) left join `roles` `r` on((`ur`.`id_rol` = `r`.`id_rol`))) order by `ra`.`fecha_hora` desc;

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
