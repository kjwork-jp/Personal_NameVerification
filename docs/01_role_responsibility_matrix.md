# 01_role_responsibility_matrix.md

## 1. 目的
本書は ChatGPT、Codex、人間オーナーの責任分界を定義します。

## 2. RACI 的整理
- R = Responsible: 実施責任
- A = Accountable: 最終責任
- C = Consulted: 相談先
- I = Informed: 情報共有先

## 3. 役割表
| 項目 | ChatGPT | Codex | Human Owner |
|---|---|---|---|
| リポジトリ構想整理 | R | I | A |
| 要件定義 | R | I | A |
| 基本設計 | R | I | A |
| 技術詳細設計レビュー | R | C | A |
| 実装 | C | R | A |
| 単体テスト初期 | C | R | A |
| 結合テスト初期 | C | R | A |
| 総合レビュー | R | C | A |
| UAT 観点整理 | R | C | A |
| 運用開始前判定 | R | I | A |
| PR 作成 | C | R | A |
| マージ判断 | C | I | A |
| 障害時判断 | C | I | A |

## 4. 明確な責任境界
### ChatGPT が担当するもの
- 要件定義の固定
- 基本設計の固定
- 品質基準・受入条件・運用条件の定義
- 後期レビュー
- 運用開始前の最終整理

### Codex が担当するもの
- 実装
- 小さなタスク分割
- 単体 / 初期結合テスト
- コード差分作成
- PR 作成

### Human Owner が担当するもの
- 最終意思決定
- ブランチ / PR の承認
- 実運用可否判定
- 例外的判断
- 機密情報の管理

## 5. 禁止境界
- Codex は設計承認前に仕様を拡張しない
- ChatGPT は設計未確定で実装要件を確定したことにしない
- Human Owner は文書未確認で main へ直接変更しない

## 6. エスカレーション
- 仕様不明点: ChatGPT → Human Owner
- 実装判断に迷う: Codex → 文書参照 → Human Owner
- 運用影響がある変更: Human Owner が最終判断
