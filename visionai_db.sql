CREATE TABLE emotion_class (
    emotion_id SERIAL PRIMARY KEY,
    emotion_name VARCHAR(50) UNIQUE NOT NULL,
    emotion_desc TEXT
);

CREATE TABLE model_version (
    model_id SERIAL PRIMARY KEY,
    model_version_tag VARCHAR(100) UNIQUE NOT NULL,
    model_filename VARCHAR(255) NOT NULL,      
    model_status VARCHAR(2)NOT NULL,  
    creation_date TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE predictions_log (
    predic_id BIGSERIAL PRIMARY KEY,
    emotion_id BIGINT NOT NULL,
    confidence FLOAT NOT NULL,
    model_id BIGINT NOT NULL,
    processing_time_ms INTEGER,
	source_ip INET,
	timestamp TIMESTAMPTZ DEFAULT NOW()
);

alter table predictions_log 
	add constraint fk_prections_emotion
	foreign key (emotion_id)
	references emotion_class(emotion_id);
alter table predictions_log 
	add constraint fk_prections_model
	foreign key (model_id)
	references model_version(model_id);

# Tabla de Usuarios
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX ix_users_username ON users(username);