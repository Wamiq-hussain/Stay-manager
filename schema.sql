-- Stay Manager: database design (SQLite)
-- Order matters: users -> rooms -> room_amenities -> bookings (foreign keys)

CREATE TABLE IF NOT EXISTS users (
    user_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name     TEXT NOT NULL,
    email         TEXT NOT NULL UNIQUE,
    phone_number  TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    role          TEXT NOT NULL DEFAULT 'guest' CHECK (role IN ('guest', 'owner')),
    created_at    TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS rooms (
    room_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    room_name   TEXT NOT NULL,
    description TEXT NOT NULL,
    room_type   TEXT NOT NULL CHECK (room_type IN ('single', 'double', 'family')),
    max_count   INTEGER NOT NULL DEFAULT 4,
    rent        REAL NOT NULL CHECK (rent > 0),
    image_url   TEXT,
    created_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS room_amenities (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id  INTEGER NOT NULL,
    amenity  TEXT NOT NULL,
    FOREIGN KEY (room_id) REFERENCES rooms(room_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS bookings (
    booking_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id      INTEGER NOT NULL,
    room_id      INTEGER NOT NULL,
    check_in     TEXT NOT NULL,   -- format YYYY-MM-DD
    check_out    TEXT NOT NULL,   -- format YYYY-MM-DD
    total_days   INTEGER NOT NULL,
    total_amount REAL NOT NULL,
    status       TEXT NOT NULL DEFAULT 'booked'
                 CHECK (status IN ('booked', 'confirmed', 'cancelled')),
    created_at   TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (check_out > check_in),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (room_id) REFERENCES rooms(room_id)
);
