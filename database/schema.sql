-- Smart Society Security System SQLite Schema Initialization
PRAGMA foreign_keys = ON;

-- 1. Administrators Table
CREATE TABLE IF NOT EXISTS admins (
    admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE COLLATE NOCASE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('admin', 'operator')),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 2. Residents Table
CREATE TABLE IF NOT EXISTS residents (
    resident_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    flat_number TEXT NOT NULL,
    contact_number TEXT DEFAULT NULL,
    image_path TEXT NOT NULL,
    face_encoding BLOB NOT NULL,
    status TEXT NOT NULL DEFAULT 'ACTIVE' CHECK(status IN ('ACTIVE', 'INACTIVE')),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 3. Entry Logs Table
CREATE TABLE IF NOT EXISTS entry_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    resident_id INTEGER DEFAULT NULL,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    match_distance REAL NOT NULL,
    decision TEXT NOT NULL CHECK(decision IN ('ENTRY_ALLOWED', 'ENTRY_REJECTED', 'VERIFICATION_REQUIRED')),
    reason TEXT NOT NULL,
    snapshot_path TEXT DEFAULT NULL,
    FOREIGN KEY (resident_id) REFERENCES residents(resident_id) ON DELETE SET NULL
);

-- 4. Runtime Configuration Table
CREATE TABLE IF NOT EXISTS system_config (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    description TEXT,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for Fast Lookups and High-Performance Live Video Querying
CREATE INDEX IF NOT EXISTS idx_residents_status ON residents(status);
CREATE INDEX IF NOT EXISTS idx_residents_flat ON residents(flat_number);
CREATE INDEX IF NOT EXISTS idx_entry_logs_timestamp ON entry_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_entry_logs_resident_id ON entry_logs(resident_id);
CREATE INDEX IF NOT EXISTS idx_entry_logs_decision ON entry_logs(decision);

-- Trigger: Automatically update residents.updated_at timestamp upon modification
CREATE TRIGGER IF NOT EXISTS trg_residents_updated_at
AFTER UPDATE ON residents
FOR EACH ROW
BEGIN
    UPDATE residents SET updated_at = CURRENT_TIMESTAMP WHERE resident_id = OLD.resident_id;
END;

