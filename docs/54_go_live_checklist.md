# 54_go_live_checklist.md

## 運用開始前チェック
- [ ] リリース対象 Git SHA 確定（配布物と一致確認）
- [ ] PR #47 相当（blocker 修正）が main へ反映済み
- [ ] UI 日本語化確認（主要タブ/ボタン/ラベル）
- [ ] ID 手入力不要確認（新規作成は自動採番前提）
- [ ] 名前↔タイトル直接リンク確認（多対多）
- [ ] タイトル作成時の名前複数紐づけ確認
- [ ] `name_title_links` の export/import 対象化確認
- [ ] role 別 title-name link 操作確認（editor: link可 / admin: unlink・復元・完全削除可）
- [ ] 運用操作 ログビューア確認（source/filter/regex/paging/表示件数）
- [ ] UAT 完了
- [ ] 主要バグ解消
- [ ] バックアップ実行確認
- [ ] 復旧確認
- [ ] ロール確認
- [ ] Runbook 確認
- [ ] 配布物確認
- [ ] 最終見直しレビュー完了


補助: Day 1 実施テンプレートは `docs/58_operations_handoff_runbook_and_day1_checklist.md` を参照。
