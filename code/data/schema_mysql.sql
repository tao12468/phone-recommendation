CREATE DATABASE IF NOT EXISTS phone_recommender
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE phone_recommender;

CREATE TABLE IF NOT EXISTS phones_clean (
  source_id BIGINT NOT NULL,
  name VARCHAR(255) NOT NULL,
  brand VARCHAR(64) DEFAULT '',
  price DECIMAL(10, 2) DEFAULT NULL,
  screen_size DECIMAL(6, 2) DEFAULT NULL,
  resolution VARCHAR(100) DEFAULT '',
  battery DECIMAL(10, 1) DEFAULT NULL,
  core_count VARCHAR(50) DEFAULT '',
  camera TEXT,
  cpu VARCHAR(255) DEFAULT '',
  ram DECIMAL(6, 1) DEFAULT NULL,
  rom DECIMAL(10, 1) DEFAULT NULL,
  os VARCHAR(100) DEFAULT '',
  usage_scenes VARCHAR(500) DEFAULT '',
  release_date VARCHAR(50) DEFAULT '',
  source VARCHAR(32) DEFAULT 'ZOL',
  url VARCHAR(255) DEFAULT '',
  PRIMARY KEY (source_id),
  KEY idx_brand (brand),
  KEY idx_price (price)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
