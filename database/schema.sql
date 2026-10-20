-- AI Placement Portal Database Schema
-- Compatible with MySQL 8.0+

CREATE DATABASE IF NOT EXISTS ai_placement_portal CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE ai_placement_portal;

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    email VARCHAR(191) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Technical Interview Practice Attempts Table
CREATE TABLE IF NOT EXISTS technical_attempts (
    attempt_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    job_role VARCHAR(100) NOT NULL,
    question_number INT DEFAULT 1,
    question_text TEXT NOT NULL,
    submitted_answer TEXT NOT NULL,
    score DECIMAL(3,1) NOT NULL,
    score_breakdown TEXT,
    feedback TEXT,
    strengths TEXT,
    missing_concepts TEXT,
    model_answer TEXT,
    suggestions TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_tech_user (user_id),
    INDEX idx_tech_created (created_at DESC),
    CONSTRAINT fk_tech_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. HR Behavioral Interview Practice Attempts Table
CREATE TABLE IF NOT EXISTS hr_attempts (
    attempt_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    question_text TEXT NOT NULL,
    submitted_answer TEXT NOT NULL,
    score DECIMAL(3,1) NOT NULL,
    score_breakdown TEXT,
    feedback TEXT,
    strengths TEXT,
    weaknesses TEXT,
    model_answer TEXT,
    suggestions TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_hr_user (user_id),
    INDEX idx_hr_created (created_at DESC),
    CONSTRAINT fk_hr_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Group Discussion Practice Attempts Table
CREATE TABLE IF NOT EXISTS gd_attempts (
    attempt_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    topic VARCHAR(255) NOT NULL,
    submitted_opinion TEXT NOT NULL,
    score DECIMAL(3,1) NOT NULL,
    score_breakdown TEXT,
    feedback TEXT,
    strengths TEXT,
    weaknesses TEXT,
    counterarguments TEXT,
    model_discussion TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_gd_user (user_id),
    INDEX idx_gd_created (created_at DESC),
    CONSTRAINT fk_gd_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. English Communication & Grammar Checker Attempts Table
CREATE TABLE IF NOT EXISTS english_attempts (
    attempt_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    input_text TEXT NOT NULL,
    score DECIMAL(3,1) NOT NULL,
    status_badge VARCHAR(20) NOT NULL,
    readiness_percentage INT NOT NULL,
    clarity_score DECIMAL(3,1),
    grammar_score DECIMAL(3,1),
    structure_score DECIMAL(3,1),
    tone_score DECIMAL(3,1),
    vocabulary_score DECIMAL(3,1),
    corrections TEXT,
    corrected_text TEXT,
    feedback TEXT,
    suggestions TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_english_user (user_id),
    INDEX idx_english_created (created_at DESC),
    CONSTRAINT fk_english_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
