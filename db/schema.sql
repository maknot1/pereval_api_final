CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    fam VARCHAR(100) NOT NULL,
    name VARCHAR(100) NOT NULL,
    otc VARCHAR(100),
    phone VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS coords (
    id SERIAL PRIMARY KEY,
    latitude NUMERIC(10, 7) NOT NULL,
    longitude NUMERIC(10, 7) NOT NULL,
    height INTEGER NOT NULL CHECK (height >= 0)
);

CREATE TABLE IF NOT EXISTS levels (
    id SERIAL PRIMARY KEY,
    winter VARCHAR(20),
    summer VARCHAR(20),
    autumn VARCHAR(20),
    spring VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS perevals (
    id SERIAL PRIMARY KEY,
    beauty_title VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    other_titles VARCHAR(255),
    connect TEXT,
    add_time TIMESTAMP,
    user_id INTEGER NOT NULL REFERENCES users(id),
    coords_id INTEGER NOT NULL REFERENCES coords(id),
    level_id INTEGER NOT NULL REFERENCES levels(id),
    status VARCHAR(20) NOT NULL DEFAULT 'new',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT perevals_status_check CHECK (status IN ('new', 'pending', 'accepted', 'rejected'))
);

CREATE TABLE IF NOT EXISTS images (
    id SERIAL PRIMARY KEY,
    pereval_id INTEGER NOT NULL REFERENCES perevals(id) ON DELETE CASCADE,
    data TEXT NOT NULL,
    title VARCHAR(255) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_perevals_user_id ON perevals(user_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(LOWER(email));
CREATE INDEX IF NOT EXISTS idx_images_pereval_id ON images(pereval_id);
