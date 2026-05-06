PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS names (
    id INTEGER PRIMARY KEY,
    public_id TEXT,
    raw_name TEXT NOT NULL,
    normalized_name TEXT NOT NULL,
    note TEXT,
    icon_path TEXT,
    deleted_at TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_names_public_id
ON names(public_id)
WHERE public_id IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS uq_names_normalized_active
ON names(normalized_name)
WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS titles (
    id INTEGER PRIMARY KEY,
    public_id TEXT,
    title_name TEXT NOT NULL,
    note TEXT,
    icon_path TEXT,
    deleted_at TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_titles_public_id
ON titles(public_id)
WHERE public_id IS NOT NULL;

CREATE TABLE IF NOT EXISTS subtitles (
    id INTEGER PRIMARY KEY,
    public_id TEXT,
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

CREATE UNIQUE INDEX IF NOT EXISTS uq_subtitles_public_id
ON subtitles(public_id)
WHERE public_id IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS uq_subtitles_title_code_active
ON subtitles(title_id, subtitle_code)
WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS name_subtitle_links (
    id INTEGER PRIMARY KEY,
    public_id TEXT,
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

CREATE UNIQUE INDEX IF NOT EXISTS uq_name_subtitle_links_public_id
ON name_subtitle_links(public_id)
WHERE public_id IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS uq_name_subtitle_links_active
ON name_subtitle_links(name_id, subtitle_id)
WHERE deleted_at IS NULL;


CREATE TABLE IF NOT EXISTS name_title_links (
    id INTEGER PRIMARY KEY,
    public_id TEXT,
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

CREATE UNIQUE INDEX IF NOT EXISTS uq_name_title_links_public_id
ON name_title_links(public_id)
WHERE public_id IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS uq_name_title_links_active
ON name_title_links(name_id, title_id)
WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS change_logs (
    id INTEGER PRIMARY KEY,
    public_id TEXT,
    entity_type TEXT NOT NULL,
    entity_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    operator_id TEXT NOT NULL,
    before_json TEXT,
    after_json TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_change_logs_public_id
ON change_logs(public_id)
WHERE public_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_change_logs_entity
ON change_logs(entity_type, entity_id, created_at);

CREATE TRIGGER IF NOT EXISTS trg_names_public_id_after_insert
AFTER INSERT ON names
FOR EACH ROW
WHEN NEW.public_id IS NULL
BEGIN
    UPDATE names SET public_id = lower(hex(randomblob(4)) || '-' || hex(randomblob(2)) || '-4' || substr(hex(randomblob(2)), 2) || '-' || substr('89ab', 1 + abs(random()) % 4, 1) || substr(hex(randomblob(2)), 2) || '-' || hex(randomblob(6))) WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS trg_titles_public_id_after_insert
AFTER INSERT ON titles
FOR EACH ROW
WHEN NEW.public_id IS NULL
BEGIN
    UPDATE titles SET public_id = lower(hex(randomblob(4)) || '-' || hex(randomblob(2)) || '-4' || substr(hex(randomblob(2)), 2) || '-' || substr('89ab', 1 + abs(random()) % 4, 1) || substr(hex(randomblob(2)), 2) || '-' || hex(randomblob(6))) WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS trg_subtitles_public_id_after_insert
AFTER INSERT ON subtitles
FOR EACH ROW
WHEN NEW.public_id IS NULL
BEGIN
    UPDATE subtitles SET public_id = lower(hex(randomblob(4)) || '-' || hex(randomblob(2)) || '-4' || substr(hex(randomblob(2)), 2) || '-' || substr('89ab', 1 + abs(random()) % 4, 1) || substr(hex(randomblob(2)), 2) || '-' || hex(randomblob(6))) WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS trg_name_subtitle_links_public_id_after_insert
AFTER INSERT ON name_subtitle_links
FOR EACH ROW
WHEN NEW.public_id IS NULL
BEGIN
    UPDATE name_subtitle_links SET public_id = lower(hex(randomblob(4)) || '-' || hex(randomblob(2)) || '-4' || substr(hex(randomblob(2)), 2) || '-' || substr('89ab', 1 + abs(random()) % 4, 1) || substr(hex(randomblob(2)), 2) || '-' || hex(randomblob(6))) WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS trg_name_title_links_public_id_after_insert
AFTER INSERT ON name_title_links
FOR EACH ROW
WHEN NEW.public_id IS NULL
BEGIN
    UPDATE name_title_links SET public_id = lower(hex(randomblob(4)) || '-' || hex(randomblob(2)) || '-4' || substr(hex(randomblob(2)), 2) || '-' || substr('89ab', 1 + abs(random()) % 4, 1) || substr(hex(randomblob(2)), 2) || '-' || hex(randomblob(6))) WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS trg_change_logs_public_id_after_insert
AFTER INSERT ON change_logs
FOR EACH ROW
WHEN NEW.public_id IS NULL
BEGIN
    UPDATE change_logs SET public_id = lower(hex(randomblob(4)) || '-' || hex(randomblob(2)) || '-4' || substr(hex(randomblob(2)), 2) || '-' || substr('89ab', 1 + abs(random()) % 4, 1) || substr(hex(randomblob(2)), 2) || '-' || hex(randomblob(6))) WHERE id = NEW.id;
END;
