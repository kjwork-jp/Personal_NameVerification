CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    public_id TEXT,
    operator_id TEXT NOT NULL UNIQUE,
    display_name TEXT,
    role TEXT NOT NULL CHECK(role IN ('viewer', 'editor', 'admin')),
    password_hash TEXT NOT NULL,
    password_salt TEXT NOT NULL,
    password_algorithm TEXT NOT NULL DEFAULT 'pbkdf2_sha256',
    password_iterations INTEGER NOT NULL,
    password_updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    disabled_at TEXT,
    failed_login_count INTEGER NOT NULL DEFAULT 0,
    locked_until TEXT,
    last_login_at TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_users_public_id
ON users(public_id)
WHERE public_id IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS uq_users_operator_id
ON users(operator_id);

CREATE TRIGGER IF NOT EXISTS trg_users_public_id_after_insert
AFTER INSERT ON users
FOR EACH ROW
WHEN NEW.public_id IS NULL
BEGIN
    UPDATE users SET public_id = lower(hex(randomblob(4)) || '-' || hex(randomblob(2)) || '-4' || substr(hex(randomblob(2)), 2) || '-' || substr('89ab', 1 + abs(random()) % 4, 1) || substr(hex(randomblob(2)), 2) || '-' || hex(randomblob(6))) WHERE id = NEW.id;
END;

CREATE TABLE IF NOT EXISTS user_audit_logs (
    id INTEGER PRIMARY KEY,
    actor_operator_id TEXT NOT NULL,
    target_operator_id TEXT,
    action TEXT NOT NULL,
    before_json TEXT,
    after_json TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_user_audit_logs_actor
ON user_audit_logs(actor_operator_id, created_at);

CREATE INDEX IF NOT EXISTS idx_user_audit_logs_target
ON user_audit_logs(target_operator_id, created_at);

CREATE TABLE IF NOT EXISTS app_settings (
    key TEXT PRIMARY KEY,
    value_json TEXT NOT NULL,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
