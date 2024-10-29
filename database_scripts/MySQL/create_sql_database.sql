-- Make sure that auto-increment values continue incrementing after deletions
-- This setting is typically enabled by default in MySQL, but we can explicitly set it here.
SET SESSION sql_mode = '';

CREATE DATABASE law_firm;
GRANT ALL PRIVILEGES ON law_firm.* TO 'your_username'@'127.0.0.1';

USE law_firm;

-- Create the workers table
CREATE TABLE workers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    second_name VARCHAR(100),
    last_name VARCHAR(100) NOT NULL,
    second_last_name VARCHAR(100),
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(25) UNIQUE NOT NULL,
    role VARCHAR(50) NOT NULL,
    company_id VARCHAR(20) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    two_fa_secret VARCHAR(100),
    two_fa_enabled BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create the clients table
CREATE TABLE clients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    second_name VARCHAR(100),
    last_name VARCHAR(100) NOT NULL,
    second_last_name VARCHAR(100),
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(25) UNIQUE NOT NULL,
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create the cases table
CREATE TABLE cases (
    id INT AUTO_INCREMENT PRIMARY KEY,
    client_id INT NOT NULL,
    worker_id INT NOT NULL,
    case_title VARCHAR(255) NOT NULL,
    case_description TEXT,
    case_status VARCHAR(50),
    case_type VARCHAR(50) NOT NULL,
    court_date DATE,
    judge_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE,
    FOREIGN KEY (worker_id) REFERENCES workers(id) ON DELETE CASCADE
);

-- Create the case_history table
CREATE TABLE case_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT,
    worker_id INT,
    update_description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE,
    FOREIGN KEY (worker_id) REFERENCES workers(id) ON DELETE SET NULL
);
