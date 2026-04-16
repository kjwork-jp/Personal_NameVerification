# 33_directory_structure_policy.md

## 1. 目的
ディレクトリ構成の一貫性を保つ。

## 2. 方針
- UI, Application, Domain, Infrastructure を分ける
- test は対象層に対応させる
- scripts は CLI / 運用系に限定する
- docs と prompts はコードから独立させる

## 3. 実装開始後の標準
```text
app/
  ui/
  application/
  domain/
  infrastructure/
tests/
scripts/
db/
assets/
docs/
prompts/
```

## 4. 禁止事項
- app 直下への雑多なファイル増殖
- 層責務をまたぐ混在配置
