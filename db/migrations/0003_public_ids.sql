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
