-- 與 Demo API 對齊之 users 結構（資料庫：test）。若資料表已存在可略過。
CREATE TABLE IF NOT EXISTS users (
    id         SERIAL PRIMARY KEY,
    username   VARCHAR(50)  NOT NULL,
    email      VARCHAR(100) NULL,
    is_active  BOOLEAN      NULL DEFAULT true,
    created_at TIMESTAMP    NULL DEFAULT CURRENT_TIMESTAMP
);
