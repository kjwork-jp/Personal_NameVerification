PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS name_title_links (
    id INTEGER PRIMARY KEY,
    name_id INTEGER NOT NULL,
    title_id INTEGER NOT NULL,
    relation_type TEXT NOT NULL DEFAULT 'primary',
    deleted_at TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (name_id) REFERENCES names(id)
        ON UPDATE RESTRICT
        ON DELETE RESTRICT,
    FOREIGN KEY (title_id) REFERENCES titles(id)
        ON UPDATE RESTRICT
        ON DELETE RESTRICT
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_name_title_links_active
ON name_title_links(name_id, title_id)
WHERE deleted_at IS NULL;
