# 02_document_priority_order.md

## 1. 目的
複数文書間に矛盾がある場合、どの文書を正とするかを明確にします。

## 2. 優先順位
1. `docs/00_repository_master_spec.md`
2. `docs/10_requirements_definition.md`
3. `docs/11_acceptance_criteria.md`
4. `docs/12_basic_design.md`
5. `docs/13_detailed_technical_design.md`
6. `docs/50_operations_design.md`
7. `docs/31_branch_and_pr_policy.md`
8. `docs/40_test_strategy.md`
9. `README.md`
10. `prompts/*`
11. その他の補助文書

## 3. 原則
- 下位文書は上位文書に反してはならない
- 矛盾が見つかったら下位文書を修正する
- 実装が文書に反している場合、原則として実装が誤り
- ただし設計不備が明らかな場合は、設計修正 PR を先に行う

## 4. 仕様不整合時の対応
1. 不整合箇所を特定
2. 影響文書を洗い出す
3. `docs/98_decision_log.md` に記録
4. 上位文書から順に修正
5. 実装に反映
6. 最終レビューで再確認

## 5. AI 向けルール
- Codex は必ず本書を最初に読む
- 解釈に迷う場合、下位文書ではなく上位文書を優先する
