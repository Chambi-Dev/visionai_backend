DROP TABLE IF EXISTS emotion_class;
CREATE TABLE emotion_class (
    emotion_id SERIAL PRIMARY KEY,
    emotion_name VARCHAR(50) UNIQUE NOT NULL,
    emotion_desc TEXT
);

DROP TABLE IF EXISTS model_version;
CREATE TABLE model_version (
    model_id SERIAL PRIMARY KEY,
    model_version_tag VARCHAR(100) UNIQUE NOT NULL,
    model_filename VARCHAR(255) NOT NULL,      
    model_status VARCHAR(2) NOT NULL,  
    creation_date TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla de Usuarios
DROP TABLE IF EXISTS users;
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

DROP TABLE IF EXISTS predictions_log;
CREATE TABLE predictions_log (
    predic_id BIGSERIAL PRIMARY KEY,
    emotion_id BIGINT NOT NULL REFERENCES emotion_class(emotion_id),
    confidence FLOAT NOT NULL,
    model_id BIGINT NOT NULL REFERENCES model_version(model_id),
    processing_time_ms INTEGER,
    source_ip INET,
    user_id INTEGER REFERENCES users(user_id),
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX ix_users_username ON users(username);

-- ============================================
-- Insert Initial Data (Required for FK Constraints)
-- ============================================

-- Insert emotion classes (required for predictions_log FK)
INSERT INTO emotion_class (emotion_id, emotion_name, emotion_desc) VALUES
(1, 'angry', 'Enojado'),
(2, 'disgust', 'Disgustado'),
(3, 'fear', 'Miedo'),
(4, 'happy', 'Feliz'),
(5, 'neutral', 'Neutral'),
(6, 'sad', 'Triste'),
(7, 'surprise', 'Sorprendido');

-- Reset sequence for emotion_class to avoid conflicts
SELECT setval('emotion_class_emotion_id_seq', (SELECT MAX(emotion_id) FROM emotion_class));

-- Insert default model version (required for predictions_log FK)
INSERT INTO model_version (model_id, model_version_tag, model_filename, model_status) VALUES
(1, 'v1.0.0', 'modelo_emociones.h5', '01');

-- Reset sequence for model_version to avoid conflicts
SELECT setval('model_version_model_id_seq', (SELECT MAX(model_id) FROM model_version));

-- ============================================
-- Database Setup Complete
-- ============================================
-- Emotion classes: 7 emotions ready for predictions
-- Model version: v1.0.0 (active)
-- Users table: Empty (users register via API)
-- Predictions log: Empty (ready to receive predictions)
-- ============================================