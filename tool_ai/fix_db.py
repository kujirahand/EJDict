import os
import kudb

SCRIPT_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
SRC_DIR = os.path.join(ROOT_DIR, "src")
CONFIG_FILE = os.path.join(SCRIPT_DIR, "config.json")
DB_FILE = os.path.join(SCRIPT_DIR, "ai_reporter.db")

# データベース接続
kudb.connect(DB_FILE)
for row in kudb.get_all():
    if "fix2" not in row:
        continue
    word1 = row["英単語"]
    id = row["id"]
    kudb.update(id=id, tag=word1, new_value=row)
    print(id ,word1)
