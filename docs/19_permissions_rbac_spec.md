# 19_permissions_rbac_spec.md

## 1. 目的
本書は、NameVerification v3 の権限制御（RBAC）を定義する。  
**本版は、現行実装（`app/application/authorization.py` と `app/application/query_services.py`）に整合する最小方針**を固定する。

## 2. ロール
- viewer
- editor
- admin

## 3. 操作区分
- **read-only**: 検索/参照/一覧表示/監査ログ閲覧など、データ永続状態を変更しない操作
- **write**: 作成/更新/リンク作成・解除など、永続状態を変更するが destructive ではない操作
- **destructive**: 論理削除/復元/完全削除など、運用上の破壊的影響を持つ操作

## 4. 現行実装に合わせた最小 RBAC 方針
### 4.1 read-only
現時点では、**valid role（viewer/editor/admin）であれば read-only 操作を許可**する。

### 4.2 write
write 操作は **editor/admin のみ許可**する。

### 4.3 destructive
destructive 操作は **admin のみ許可**する。

## 5. 権限マトリクス（現行）
| 操作 | 区分 | viewer | editor | admin |
|---|---|---:|---:|---:|
| 検索（名前検索） | read-only | ○ | ○ | ○ |
| 詳細参照（名前/タイトル/サブタイトル） | read-only | ○ | ○ | ○ |
| タイトル一覧/サブタイトル一覧参照 | read-only | ○ | ○ | ○ |
| 既存リンク参照 | read-only | ○ | ○ | ○ |
| ゴミ箱/削除済み一覧参照（names/titles/subtitles/links） | read-only | ○ | ○ | ○ |
| 監査ログ参照（change_logs） | read-only | ○ | ○ | ○ |
| 名前作成/更新 | write | × | ○ | ○ |
| タイトル/サブタイトル作成/更新 | write | × | ○ | ○ |
| リンク作成/解除 | write | × | ○ | ○ |
| 論理削除（名前/タイトル/サブタイトル/リンク） | destructive | × | × | ○ |
| 復元（名前/タイトル/サブタイトル/リンク） | destructive | × | × | ○ |
| 完全削除（名前/タイトル/サブタイトル/リンク） | destructive | × | × | ○ |
| Import/Restore 等の管理系操作 | destructive | × | × | ○ |

## 6. ゴミ箱・削除済み・監査ログの扱い
- `list_deleted_*` / `search_names(include_deleted=True)` / `list_change_logs` 等の**閲覧系 read-only 操作**は valid role で許可する。
- ただし、ゴミ箱対象への **復元/完全削除などの操作は admin のみ**とする。
- 監査ログは「見られること」と「状態変更できること」を分離し、後者は存在しない（参照専用）前提とする。

## 7. 実装原則
- UI 制御だけでなくアプリ層でも制御する。
- ロール判定失敗時は明示的に拒否する。
- read-only の valid role 共通化は、現行 `require_known_role` ベースの実装と整合させる。
- 将来、viewer/editor/admin 間で read 差分を導入する場合は、要件・受入基準・UI 表示仕様を同時に更新する。

## 8. 将来拡張（本PRの対象外）
- read-only の粒度をロールごとに分離（例: viewer は監査ログ不可、deleted 一覧不可 など）
- フィールド単位のマスキング
- 監査ログのロール別フィルタ制御
