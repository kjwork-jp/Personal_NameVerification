# 15_data_design.md

## 1. 主要エンティティ
- names
- titles
- subtitles
- name_subtitle_links
- change_logs

## 2. names
### 目的
照合対象となる名前を管理する。

### 主項目
- id
- raw_name
- normalized_name
- note
- icon_path
- deleted_at
- created_at
- updated_at

### 制約
- normalized_name は削除未済範囲で一意

## 3. titles
### 主項目
- id
- title_name
- note
- icon_path
- deleted_at
- created_at
- updated_at

## 4. subtitles
### 主項目
- id
- title_id
- subtitle_code
- subtitle_name
- sort_order
- note
- icon_path
- deleted_at
- created_at
- updated_at

### 制約
- title_id + subtitle_code は削除未済範囲で一意

## 5. name_subtitle_links
### 主項目
- id
- name_id
- subtitle_id
- relation_type
- deleted_at
- created_at
- updated_at

### 制約
- 同一 name_id + subtitle_id の重複禁止

## 6. change_logs
### 主項目
- id
- entity_type
- entity_id
- action
- operator_id
- before_json
- after_json
- created_at

## 7. 共通設計
- 日時は UTC ISO8601 を原則
- 物理削除は限定用途のみ
- 外部キー整合性を維持する
