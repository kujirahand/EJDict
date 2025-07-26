import os
import kudb

SCRIPT_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
SRC_DIR = os.path.join(ROOT_DIR, "src")
CONFIG_FILE = os.path.join(SCRIPT_DIR, "config.json")
DB_FILE = os.path.join(SCRIPT_DIR, "ai_reporter.db")

# データベース接続
res = {"fix": 0, "pass": 0}
kudb.connect(DB_FILE)
for row in kudb.get_all():
    if "fix2" not in row:
        continue
    word1 = row["英単語"]
    id = row["id"]
    fix2 = row.get("fix2", "")
    res[fix2] += 1
    print(row)
print(res)


