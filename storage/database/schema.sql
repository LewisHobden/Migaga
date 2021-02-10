-- phpMyAdmin SQL Dump
-- version 5.0.2
-- https://www.phpmyadmin.net/
--
-- Host: production-do-user-6925309-0.a.db.ondigitalocean.com:25060
-- Generation Time: Feb 10, 2021 at 08:40 PM
-- Server version: 8.0.20
-- PHP Version: 7.4.8

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `discord`
--

-- --------------------------------------------------------

--
-- Table structure for table `discord_commands`
--

CREATE TABLE `discord_commands` (
  `id` int UNSIGNED NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `response` varchar(2000) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` varchar(2000) COLLATE utf8mb4_unicode_ci NOT NULL,
  `server_id` bigint NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `discord_flair_message_reactions`
--

CREATE TABLE `discord_flair_message_reactions` (
  `reference` varchar(8) COLLATE utf8mb4_unicode_ci NOT NULL,
  `discord_message_id` bigint NOT NULL,
  `emoji_id` bigint NOT NULL,
  `role_id` bigint NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `discord_guild_configs`
--

CREATE TABLE `discord_guild_configs` (
  `id` int NOT NULL,
  `guild_id` bigint NOT NULL,
  `server_logs_channel_id` bigint DEFAULT NULL,
  `points_name` text COLLATE utf8mb4_unicode_ci,
  `points_emoji` text COLLATE utf8mb4_unicode_ci,
  `starboard_emoji_id` bigint DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `discord_point_transactions`
--

CREATE TABLE `discord_point_transactions` (
  `id` int NOT NULL,
  `guild_id` bigint NOT NULL,
  `recipient_user_id` bigint DEFAULT NULL,
  `sender_user_id` bigint DEFAULT NULL,
  `amount` decimal(10,5) DEFAULT NULL,
  `timestamp` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `discord_profiles`
--

CREATE TABLE `discord_profiles` (
  `discord_user_id` bigint NOT NULL,
  `colour` int NOT NULL,
  `tag` varchar(256) COLLATE utf8mb4_unicode_ci NOT NULL,
  `bio` varchar(2048) COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `discord_profile_fields`
--

CREATE TABLE `discord_profile_fields` (
  `id` int NOT NULL,
  `discord_user_id` bigint NOT NULL,
  `key` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `value` varchar(1024) COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `discord_reminders`
--

CREATE TABLE `discord_reminders` (
  `id` int NOT NULL,
  `creator_discord_id` bigint NOT NULL,
  `datetime` datetime NOT NULL,
  `reminder` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `has_reminded` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `discord_reminder_destinations`
--

CREATE TABLE `discord_reminder_destinations` (
  `id` int NOT NULL,
  `reminder_id` int NOT NULL,
  `destination_type` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `destination_id` bigint NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `discord_role_aliases`
--

CREATE TABLE `discord_role_aliases` (
  `id` int UNSIGNED NOT NULL,
  `alias` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `role_id` bigint UNSIGNED NOT NULL,
  `server_id` bigint UNSIGNED NOT NULL,
  `is_admin_only` tinyint UNSIGNED NOT NULL DEFAULT '0',
  `uses` int UNSIGNED DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `discord_role_overwrites`
--

CREATE TABLE `discord_role_overwrites` (
  `id` int UNSIGNED NOT NULL,
  `role_id` bigint UNSIGNED NOT NULL,
  `overwrite_role_id` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `server_id` bigint UNSIGNED NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `discord_starboard`
--

CREATE TABLE `discord_starboard` (
  `id` int NOT NULL,
  `guild_id` bigint NOT NULL,
  `channel_id` bigint NOT NULL,
  `is_locked` tinyint(1) NOT NULL,
  `star_threshold` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `discord_starboard_messages`
--

CREATE TABLE `discord_starboard_messages` (
  `message_id` bigint NOT NULL,
  `starboard_id` int NOT NULL,
  `embed_message_id` bigint DEFAULT NULL,
  `datetime_added` datetime NOT NULL,
  `user_id` bigint NOT NULL,
  `is_muted` tinyint(1) NOT NULL,
  `message_channel_id` bigint DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `discord_starboard_message_starrers`
--

CREATE TABLE `discord_starboard_message_starrers` (
  `id` int NOT NULL,
  `message_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  `datetime_starred` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `discord_welcome_messages`
--

CREATE TABLE `discord_welcome_messages` (
  `id` mediumint UNSIGNED NOT NULL,
  `message` varchar(2000) COLLATE utf8mb4_unicode_ci NOT NULL,
  `server_id` bigint UNSIGNED NOT NULL,
  `channel_id` bigint UNSIGNED NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `discord_commands`
--
ALTER TABLE `discord_commands`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `discord_flair_message_reactions`
--
ALTER TABLE `discord_flair_message_reactions`
  ADD PRIMARY KEY (`reference`);

--
-- Indexes for table `discord_guild_configs`
--
ALTER TABLE `discord_guild_configs`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `discord_point_transactions`
--
ALTER TABLE `discord_point_transactions`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `discord_profiles`
--
ALTER TABLE `discord_profiles`
  ADD PRIMARY KEY (`discord_user_id`);

--
-- Indexes for table `discord_profile_fields`
--
ALTER TABLE `discord_profile_fields`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `profilefieldmodel_discord_user_id_key` (`discord_user_id`,`key`),
  ADD KEY `profilefieldmodel_discord_user_id` (`discord_user_id`);

--
-- Indexes for table `discord_reminders`
--
ALTER TABLE `discord_reminders`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `discord_reminder_destinations`
--
ALTER TABLE `discord_reminder_destinations`
  ADD PRIMARY KEY (`id`),
  ADD KEY `reminderdestination_reminder_id` (`reminder_id`);

--
-- Indexes for table `discord_role_aliases`
--
ALTER TABLE `discord_role_aliases`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `discord_role_overwrites`
--
ALTER TABLE `discord_role_overwrites`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `discord_starboard`
--
ALTER TABLE `discord_starboard`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `starboardmodel_guild_id` (`guild_id`),
  ADD UNIQUE KEY `starboardmodel_channel_id` (`channel_id`);

--
-- Indexes for table `discord_starboard_messages`
--
ALTER TABLE `discord_starboard_messages`
  ADD PRIMARY KEY (`message_id`),
  ADD UNIQUE KEY `starredmessagemodel_embed_message_id` (`embed_message_id`),
  ADD KEY `starredmessagemodel_starboard_id` (`starboard_id`);

--
-- Indexes for table `discord_starboard_message_starrers`
--
ALTER TABLE `discord_starboard_message_starrers`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `messagestarrermodel_user_id_message_id` (`user_id`,`message_id`),
  ADD KEY `messagestarrermodel_message_id` (`message_id`);

--
-- Indexes for table `discord_welcome_messages`
--
ALTER TABLE `discord_welcome_messages`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `discord_commands`
--
ALTER TABLE `discord_commands`
  MODIFY `id` int UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `discord_guild_configs`
--
ALTER TABLE `discord_guild_configs`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `discord_point_transactions`
--
ALTER TABLE `discord_point_transactions`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `discord_profile_fields`
--
ALTER TABLE `discord_profile_fields`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `discord_reminders`
--
ALTER TABLE `discord_reminders`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `discord_reminder_destinations`
--
ALTER TABLE `discord_reminder_destinations`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `discord_role_aliases`
--
ALTER TABLE `discord_role_aliases`
  MODIFY `id` int UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `discord_role_overwrites`
--
ALTER TABLE `discord_role_overwrites`
  MODIFY `id` int UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `discord_starboard`
--
ALTER TABLE `discord_starboard`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `discord_starboard_message_starrers`
--
ALTER TABLE `discord_starboard_message_starrers`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `discord_welcome_messages`
--
ALTER TABLE `discord_welcome_messages`
  MODIFY `id` mediumint UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `discord_profile_fields`
--
ALTER TABLE `discord_profile_fields`
  ADD CONSTRAINT `discord_profile_fields_ibfk_1` FOREIGN KEY (`discord_user_id`) REFERENCES `discord_profiles` (`discord_user_id`);

--
-- Constraints for table `discord_reminder_destinations`
--
ALTER TABLE `discord_reminder_destinations`
  ADD CONSTRAINT `discord_reminder_destinations_ibfk_1` FOREIGN KEY (`reminder_id`) REFERENCES `discord_reminders` (`id`);

--
-- Constraints for table `discord_starboard_messages`
--
ALTER TABLE `discord_starboard_messages`
  ADD CONSTRAINT `discord_starboard_messages_ibfk_1` FOREIGN KEY (`starboard_id`) REFERENCES `discord_starboard` (`id`);

--
-- Constraints for table `discord_starboard_message_starrers`
--
ALTER TABLE `discord_starboard_message_starrers`
  ADD CONSTRAINT `discord_starboard_message_starrers_ibfk_1` FOREIGN KEY (`message_id`) REFERENCES `discord_starboard_messages` (`message_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
