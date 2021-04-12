-- Adminer 4.7.8 MySQL dump

SET NAMES utf8;
SET time_zone = '+00:00';
SET foreign_key_checks = 0;

SET NAMES utf8mb4;

DROP TABLE IF EXISTS `discord_commands`;
CREATE TABLE `discord_commands` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `response` varchar(2000) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` varchar(2000) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `server_id` bigint NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


DROP TABLE IF EXISTS `discord_flair_message_reactions`;
CREATE TABLE `discord_flair_message_reactions` (
  `reference` varchar(8) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `discord_message_id` bigint NOT NULL,
  `emoji_id` bigint NOT NULL,
  `role_id` bigint NOT NULL,
  PRIMARY KEY (`reference`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


DROP TABLE IF EXISTS `discord_guild_configs`;
CREATE TABLE `discord_guild_configs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `guild_id` bigint NOT NULL,
  `server_logs_channel_id` bigint DEFAULT NULL,
  `points_name` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `points_emoji` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `config_data` json DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


DROP TABLE IF EXISTS `discord_point_transactions`;
CREATE TABLE `discord_point_transactions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `guild_id` bigint NOT NULL,
  `recipient_user_id` bigint DEFAULT NULL,
  `sender_user_id` bigint DEFAULT NULL,
  `amount` decimal(10,5) DEFAULT NULL,
  `timestamp` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


DROP TABLE IF EXISTS `discord_profile_fields`;
CREATE TABLE `discord_profile_fields` (
  `id` int NOT NULL AUTO_INCREMENT,
  `discord_user_id` bigint NOT NULL,
  `key` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `value` varchar(1024) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `profilefieldmodel_discord_user_id_key` (`discord_user_id`,`key`),
  KEY `profilefieldmodel_discord_user_id` (`discord_user_id`),
  CONSTRAINT `discord_profile_fields_ibfk_1` FOREIGN KEY (`discord_user_id`) REFERENCES `discord_profiles` (`discord_user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


DROP TABLE IF EXISTS `discord_profiles`;
CREATE TABLE `discord_profiles` (
  `discord_user_id` bigint NOT NULL,
  `colour` int NOT NULL,
  `tag` varchar(256) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `bio` varchar(2048) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`discord_user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


DROP TABLE IF EXISTS `discord_reminder_destinations`;
CREATE TABLE `discord_reminder_destinations` (
  `id` int NOT NULL AUTO_INCREMENT,
  `reminder_id` int NOT NULL,
  `destination_type` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `destination_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `reminderdestination_reminder_id` (`reminder_id`),
  CONSTRAINT `discord_reminder_destinations_ibfk_1` FOREIGN KEY (`reminder_id`) REFERENCES `discord_reminders` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


DROP TABLE IF EXISTS `discord_reminders`;
CREATE TABLE `discord_reminders` (
  `id` int NOT NULL AUTO_INCREMENT,
  `creator_discord_id` bigint NOT NULL,
  `datetime` datetime NOT NULL,
  `reminder` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `has_reminded` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


DROP TABLE IF EXISTS `discord_role_aliases`;
CREATE TABLE `discord_role_aliases` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `alias` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `role_id` bigint unsigned NOT NULL,
  `server_id` bigint unsigned NOT NULL,
  `is_admin_only` tinyint unsigned NOT NULL DEFAULT '0',
  `uses` int unsigned DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


DROP TABLE IF EXISTS `discord_role_overwrites`;
CREATE TABLE `discord_role_overwrites` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `role_id` bigint unsigned NOT NULL,
  `overwrite_role_id` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `server_id` bigint unsigned NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


DROP TABLE IF EXISTS `discord_starboard`;
CREATE TABLE `discord_starboard` (
  `id` int NOT NULL AUTO_INCREMENT,
  `guild_id` bigint NOT NULL,
  `channel_id` bigint NOT NULL,
  `is_locked` tinyint(1) NOT NULL,
  `star_threshold` int NOT NULL,
  `emoji` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `starboardmodel_channel_id` (`channel_id`),
  KEY `discord_starboard_emoji` (`emoji`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


DROP TABLE IF EXISTS `discord_starboard_message_starrers`;
CREATE TABLE `discord_starboard_message_starrers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `datetime_starred` datetime NOT NULL,
  `starred_message_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `discord_starboard_message_starrers_starred_message_id` (`starred_message_id`),
  CONSTRAINT `fk_discord_starboard_message_starrers_starred_message_id_c736874` FOREIGN KEY (`starred_message_id`) REFERENCES `discord_starboard_messages` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


DROP TABLE IF EXISTS `discord_starboard_messages`;
CREATE TABLE `discord_starboard_messages` (
  `message_id` bigint NOT NULL,
  `starboard_id` int NOT NULL,
  `embed_message_id` bigint DEFAULT NULL,
  `datetime_added` datetime NOT NULL,
  `user_id` bigint NOT NULL,
  `is_muted` tinyint(1) NOT NULL,
  `message_channel_id` bigint DEFAULT NULL,
  `id` int NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`),
  UNIQUE KEY `starredmessagemodel_embed_message_id` (`embed_message_id`),
  KEY `starredmessagemodel_starboard_id` (`starboard_id`),
  CONSTRAINT `discord_starboard_messages_ibfk_1` FOREIGN KEY (`starboard_id`) REFERENCES `discord_starboard` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


DROP TABLE IF EXISTS `discord_welcome_messages`;
CREATE TABLE `discord_welcome_messages` (
  `id` mediumint unsigned NOT NULL AUTO_INCREMENT,
  `message` varchar(2000) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `server_id` bigint unsigned NOT NULL,
  `channel_id` bigint unsigned NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- 2021-04-12 15:41:24
