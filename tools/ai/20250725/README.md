# 構成手順

1. ai_reporter.py を実行して、校正を実行。
2. ai_fixer.py を実行して、AIの校正結果を確認(1回目)
3. ai_fixer2.py を実行して、AIの校正結果を確認(2回目)
4. fix_db.py 実行して、DBにtagを追加
5. fix_src_data.py 実行して、ソースデータを修正
