BEGIN;

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS names (
    id INTEGER PRIMARY KEY,
    raw_name TEXT NOT NULL,
    normalized_name TEXT NOT NULL,
    note TEXT,
    icon_path TEXT,
    deleted_at TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_names_normalized_active
ON names(normalized_name)
WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS titles (
    id INTEGER PRIMARY KEY,
    title_name TEXT NOT NULL,
    note TEXT,
    icon_path TEXT,
    deleted_at TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS subtitles (
    id INTEGER PRIMARY KEY,
    title_id INTEGER NOT NULL,
    subtitle_code TEXT NOT NULL,
    subtitle_name TEXT NOT NULL,
    sort_order INTEGER NOT NULL DEFAULT 0,
    note TEXT,
    icon_path TEXT,
    deleted_at TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (title_id) REFERENCES titles(id)
        ON UPDATE RESTRICT
        ON DELETE RESTRICT
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_subtitles_title_code_active
ON subtitles(title_id, subtitle_code)
WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS name_subtitle_links (
    id INTEGER PRIMARY KEY,
    name_id INTEGER NOT NULL,
    subtitle_id INTEGER NOT NULL,
    relation_type TEXT NOT NULL,
    deleted_at TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (name_id) REFERENCES names(id)
        ON UPDATE RESTRICT
        ON DELETE RESTRICT,
    FOREIGN KEY (subtitle_id) REFERENCES subtitles(id)
        ON UPDATE RESTRICT
        ON DELETE RESTRICT
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_name_subtitle_links_active
ON name_subtitle_links(name_id, subtitle_id)
WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS change_logs (
    id INTEGER PRIMARY KEY,
    entity_type TEXT NOT NULL,
    entity_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    operator_id TEXT NOT NULL,
    before_json TEXT,
    after_json TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_change_logs_entity
ON change_logs(entity_type, entity_id, created_at);

COMMIT;
