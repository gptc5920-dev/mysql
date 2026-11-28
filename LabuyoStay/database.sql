
CREATE TABLE IF NOT EXISTS boarding_houses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    address TEXT NOT NULL,
    price REAL NOT NULL,
    capacity INTEGER NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'Available'
);

CREATE TABLE IF NOT EXISTS reservations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_name TEXT NOT NULL,
    contact TEXT NOT NULL,
    boarding_house_id INTEGER NOT NULL,
    reservation_date TEXT NOT NULL,
    status TEXT DEFAULT 'Pending',
    FOREIGN KEY (boarding_house_id)
        REFERENCES boarding_houses(id)
);
