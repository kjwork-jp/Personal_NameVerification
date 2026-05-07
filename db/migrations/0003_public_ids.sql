ALTER TABLE names ADD COLUMN public_id TEXT;
ALTER TABLE titles ADD COLUMN public_id TEXT;
ALTER TABLE subtitles ADD COLUMN public_id TEXT;
ALTER TABLE name_subtitle_links ADD COLUMN public_id TEXT;
ALTER TABLE name_title_links ADD COLUMN public_id TEXT;
ALTER TABLE change_logs ADD COLUMN public_id TEXT;

CREATE UNIQUE INDEX IF NOT EXISTS uq_names_public_id ON names(public_id) WHERE public_id IS NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS uq_titles_public_id ON titles(public_id) WHERE public_id IS NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS uq_subtitles_public_id ON subtitles(public_id) WHERE public_id IS NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS uq_name_subtitle_links_public_id ON name_subtitle_links(public_id) WHERE public_id IS NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS uq_name_title_links_public_id ON name_title_links(public_id) WHERE public_id IS NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS uq_change_logs_public_id ON change_logs(public_id) WHERE public_id IS NOT NULL;

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
