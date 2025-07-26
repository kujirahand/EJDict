import os
import kudb
import ai_reporter
import glob

# --------------------------------------
# ai_reporter.db に fix_src=1を設定します。
# --------------------------------------

SCRIPT_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
SRC_DIR = os.path.join(ROOT_DIR, "src")
CONFIG_FILE = os.path.join(SCRIPT_DIR, "config.json")
DB_FILE = os.path.join(SCRIPT_DIR, "ai_reporter.db")

# データベース接続
kudb.connect(DB_FILE)

def fix_file(file_path):
    """指定されたファイルの内容を修正"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    # ここでファイルの内容を修正する処理を追加
    flag_change_file = False
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        # タブ区切りで分割
        it = line.split("\t")
        words, mean = it[0], it[1]
        org_mean = mean
        word_list = words.split(",")
        for word in word_list:
            id = 0
            rr = kudb.get_by_tag(word)
            if not rr:
                continue
            r = rr[0]
            id = r["id"]
            # if "fix_src" in r: # fix_srcがあれば修正済み
            #    continue
            if "fix2" not in r:
                continue
            if r["fix2"] == "pass":
                continue
            mean3 = r.get("校正後の意味", "")
            if mean3 == "":
                continue
            mean = mean3 # update
            r["fix_src"] = 1
            kudb.update(id=id, tag=word, new_value=r)
            flag_change_file = True
            break
        if mean != org_mean:
            print(f"### 修正({id}): {words} の意味")
            print(f"- [x] {org_mean}")
            print(f"- [o] {mean}")
        lines[i] = f"{words}\t{mean}"
    if flag_change_file:
        with open(file_path, 'w', encoding='utf-8') as f:
            content = '\n'.join(lines)
            f.write(content)
        print(f"File processed: {file_path}")

def fix_all_files():
    files = glob.glob(os.path.join(SRC_DIR, "*.txt"))
    for file in sorted(files):
        print(f"Processing file: {file}")
        fix_file(file)

def main():
    """メイン処理"""
    fix_all_files()

# --------------------------
if __name__ == "__main__":
    main()    
