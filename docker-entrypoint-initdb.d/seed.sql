CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO users (name, email)
SELECT
    'user_' || gs AS name,
    'user_' || gs || '@example.test' AS email
FROM generate_series(1, 10000) AS gs
ON CONFLICT DO NOTHING;
