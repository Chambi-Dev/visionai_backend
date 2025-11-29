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