CREATE DATABASE  IF NOT EXISTS `govt` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `govt`;
-- MySQL dump 10.13  Distrib 8.0.34, for Win64 (x86_64)
--
-- Host: localhost    Database: govt
-- ------------------------------------------------------
-- Server version	8.0.35

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `comments`
--

DROP TABLE IF EXISTS `comments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `comments` (
  `comment_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `policy_id` int DEFAULT NULL,
  `comment_text` text NOT NULL,
  `commented_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`comment_id`),
  KEY `user_id` (`user_id`),
  KEY `policy_id` (`policy_id`),
  CONSTRAINT `comments_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `comments_ibfk_2` FOREIGN KEY (`policy_id`) REFERENCES `policies` (`policy_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `comments`
--

LOCK TABLES `comments` WRITE;
/*!40000 ALTER TABLE `comments` DISABLE KEYS */;
INSERT INTO `comments` VALUES (1,2,1,'This policy is moderate.','2024-09-14 14:30:34'),(2,3,2,'This policy is moderate.','2024-09-14 14:32:27'),(3,3,1,'This policy is moderate.','2024-09-14 14:32:33');
/*!40000 ALTER TABLE `comments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `policies`
--

DROP TABLE IF EXISTS `policies`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `policies` (
  `policy_id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `description` text NOT NULL,
  `details_type` enum('manual','pdf') NOT NULL,
  `details` text,
  `authorities` text,
  `reference` text,
  `pdf_file_path` varchar(255) DEFAULT NULL,
  `created_by` int DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`policy_id`),
  KEY `created_by` (`created_by`),
  CONSTRAINT `policies_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `policies`
--

LOCK TABLES `policies` WRITE;
/*!40000 ALTER TABLE `policies` DISABLE KEYS */;
INSERT INTO `policies` VALUES (1,'New Environmental Policy','This policy addresses environmental protection guidelines.','manual','Detailed policy guidelines regarding environmental conservation and compliance.','[\'Ministry of Environment\', \'National Wildlife Fund\']','[\'Reference Document 1\', \'Environmental Act 2021\']',NULL,1,'2024-09-14 14:28:38'),(2,'New Environmental Policy 2','This policy addresses environmental protection guidelines.','manual','Detailed policy guidelines regarding environmental conservation and compliance.','[\'Ministry of Environment\', \'National Wildlife Fund\']','[\'Reference Document 1\', \'Environmental Act 2021\']',NULL,1,'2024-09-14 14:28:44'),(3,'New Environmental Policy 3','This policy addresses environmental protection guidelines.','manual','Detailed policy guidelines regarding environmental conservation and compliance.','[\'Ministry of Environment\', \'National Wildlife Fund\']','[\'Reference Document 1\', \'Environmental Act 2021\']',NULL,1,'2024-09-14 14:28:47'),(4,'New Environmental Policy 4','This policy addresses environmental protection guidelines.','manual','Detailed policy guidelines regarding environmental conservation and compliance.','[\'Ministry of Environment\', \'National Wildlife Fund\']','[\'Reference Document 1\', \'Environmental Act 2021\']',NULL,1,'2024-09-14 14:28:51'),(5,'New Environmental Policy 5','This policy addresses environmental protection guidelines.','manual','Detailed policy guidelines regarding environmental conservation and compliance.','[\'Ministry of Environment\', \'National Wildlife Fund\']','[\'Reference Document 1\', \'Environmental Act 2021\']',NULL,1,'2024-09-14 14:28:56');
/*!40000 ALTER TABLE `policies` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `saved_policies`
--

DROP TABLE IF EXISTS `saved_policies`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `saved_policies` (
  `saved_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `policy_id` int DEFAULT NULL,
  `saved_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`saved_id`),
  KEY `user_id` (`user_id`),
  KEY `policy_id` (`policy_id`),
  CONSTRAINT `saved_policies_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  CONSTRAINT `saved_policies_ibfk_2` FOREIGN KEY (`policy_id`) REFERENCES `policies` (`policy_id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `saved_policies`
--

LOCK TABLES `saved_policies` WRITE;
/*!40000 ALTER TABLE `saved_policies` DISABLE KEYS */;
INSERT INTO `saved_policies` VALUES (1,2,3,'2024-09-14 16:26:39'),(2,2,2,'2024-09-14 16:27:35'),(3,2,1,'2024-09-14 16:32:55'),(4,1,1,'2024-09-14 17:47:15'),(5,1,2,'2024-09-14 18:10:28');
/*!40000 ALTER TABLE `saved_policies` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `user_type` enum('Normal','Admin') NOT NULL,
  `ministry_name` varchar(255) DEFAULT NULL,
  `department_name` varchar(255) DEFAULT NULL,
  `department_description` text,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'gatij','gatij.shakya.29.11@gmail.com','$2b$10$eAH2LOERGwAPm5PkrSv.SuHzmYDR8VQPy7fp2t20iH0yvy.Pmjx/y','Admin','Ministry of AYUSH','Department 1','Department description'),(2,'user','user@gmail.com','$2b$10$HO/THmusoetduH63/2V/2uRH9K5JhJtC58Swz1M32KBMEVmZRvO6C','Normal',NULL,NULL,NULL),(3,'user2','user2@gmail.com','$2b$10$9iT7gQwFe6cqarWDD1duhOtj2a4JRsU.y0E4/9qr7b5vF71H4rVPO','Normal',NULL,NULL,NULL);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `votes`
--

DROP TABLE IF EXISTS `votes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `votes` (
  `user_id` int NOT NULL,
  `policy_id` int NOT NULL,
  `vote_type` enum('upvote','downvote') NOT NULL,
  `voted_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`,`policy_id`),
  KEY `policy_id` (`policy_id`),
  CONSTRAINT `votes_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `votes_ibfk_2` FOREIGN KEY (`policy_id`) REFERENCES `policies` (`policy_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `votes`
--

LOCK TABLES `votes` WRITE;
/*!40000 ALTER TABLE `votes` DISABLE KEYS */;
INSERT INTO `votes` VALUES (2,1,'upvote','2024-09-14 14:30:34'),(2,2,'downvote','2024-09-14 14:35:29'),(3,1,'upvote','2024-09-14 14:32:33'),(3,2,'upvote','2024-09-14 14:32:27');
/*!40000 ALTER TABLE `votes` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-09-15  1:31:29
