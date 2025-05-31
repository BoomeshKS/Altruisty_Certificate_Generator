CREATE DATABASE IF NOT EXISTS certificate_system;

USE certificate_system;

-- Existing certificates table for offer letters
CREATE TABLE IF NOT EXISTS certificates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    certificate_number VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- New table for completed interns certificates
CREATE TABLE IF NOT EXISTS completed_interns (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    certificate_number VARCHAR(100) NOT NULL UNIQUE,
    domain VARCHAR(255),
    start_date VARCHAR(20),
    end_date VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
