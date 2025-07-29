CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    is_admin INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS parking_lots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prime_location_name TEXT NOT NULL,
    price REAL NOT NULL,
    address TEXT NOT NULL,
    pin_code TEXT NOT NULL,
    maximum_number_of_spots INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS parking_spots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lot_id INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'A',
    FOREIGN KEY (lot_id) REFERENCES parking_lots(id)
);

CREATE TABLE IF NOT EXISTS reservations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    spot_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    parking_timestamp TEXT NOT NULL,
    leaving_timestamp TEXT,
    parking_cost REAL,
    FOREIGN KEY (spot_id) REFERENCES parking_spots(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
