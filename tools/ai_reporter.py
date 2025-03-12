# AIを利用して辞書の誤字脱字を検出するツール

# 使い方:
# ! pip install ollama
# ! pip install kudb
# ! python tools/ai_reporter.py
# ! python tools/ai_reporter_fix.py

import json
from glob import glob
import ollama
import os
import random
import kudb

script_dir = os.path.dirname(__file__)
config_file = os.path.join(script_dir, "config.json")
db_file = os.path.join(script_dir, "ai_reporter.db")
# ---
ollama_host = "http://localhost:11434"
# model
# model = "Maoyue/mistral-nemo-instruct-2407:latest" # 12.2b → JSON生成ミスが多くて使えなかった
# model1 = "phi4:14b"
# model2 = "lucas2024/llama-3-elyza-jp-8b:q5_k_m"
# model3 = "lucas2024/llama-3-elyza-jp-8b:q5_k_m"
model1 = "phi4:14b"
model2 = model1
model3 = model1

# ----
kudb.connect(db_file)
if os.path.exists(config_file):
    with open(config_file, "r", encoding="utf-8") as fp:
        j = json.load(fp)
        if "host" in j:
            ollama_host = j["host"]
# create client
client = ollama.Client(host=ollama_host)


def generate(prompt, model):
    response = client.generate(
        model=model1,
        system="あなたは優秀な文章校正AIです。これから英和辞書の誤字脱字を指摘します。",
        prompt=prompt,
        options={"temperature": 0.7, "seed": random.randint(1, 100000)},
    )
    return response["response"]


def check_raw(word, mean, model):
    prompt = """
### Instruction:
Inputを読み、Outputの例を参考にして、**JSONだけ**を出力してください。
明らかな間違いがある場合のみ、明確な理由を付けて指摘してください。

### 備考:
- `A / B / C`は、列挙で単語にAとBとCの意味があることを示します。
- `A, B, C`は、Aの言い換えがBやCであることを示します。
- `A; B`は、同じ単語の異なる意味があることを示します。
- `A(B)`は、Aの補足Bを示しています。
- `=A / B`は、Aと同じ意味であり、Bの別の意味も持つことを示します。
- `〈C〉` は、countableの略で「可算名詞（数えられる名詞）」を意味します。例えば、"an apple"。
- `〈U〉` は、uncountableの略で「不可算名詞（数えられない名詞）」を意味します。例えば、"water"。

### Input:
```json
{{"word": "{word}", "mean": "{mean}"}}
```

### Output example:
```json
{{"Status": "ok"}}
```
または
```json
{{"Status": "error", "Reason": "説明が間違っていた", "修正後": {{"word": "face", "mean": "魚"}}}}
```
または
```json
{{"Status": "error", "Reason": "誤字があった", "修正後": {{"word": "abalone", "mean": "〈C〉アワビ;〈U〉アワビの身"}}}}
```
または
```json
{{"Status": "error", "Reason": "カッコが対応していない", "修正後": {{"word": "Aaron", "mean": "アロン(モーセの兄;ヘブライ人最初の大祭司とされる)"}}}}
```
""".format(
        word=word, mean=mean
    )
    return generate(prompt, model)


def check_json(word, mean, model, times=0):
    if times > 10:
        print("[ERROR] faild 10 times")
        raise ValueError("faild 10 times")
    # プロンプトを実行してJSONを取得
    text = check_raw(word, mean, model)
    if "```" not in text:
        # 直接JSONが出力された？
        text = "```json\n" + text + "\n```\n"
    blocks = text.split("```")
    if len(blocks) < 3:
        print("[ERROR] broken json: ", word, ":", text)
        check_json(word, mean, model, times + 1)
        return
    json_str = blocks[1].strip()
    if json_str[0:4] == "json":
        json_str = json_str[4:]
    try:
        obj = json.loads(json_str)
    except Exception:
        print("[ERROR] JSON parse error: ", word)
        return check_json(word, mean, model, times + 1)
    # Statusがあるか？
    if "Status" not in obj:
        # print("[ERROR] Status not found: ", word, obj)
        return check_json(word, mean, model, times + 1)
    status = obj["Status"]
    if status == "ok":
        return obj
    if status == "error":
        return obj
    print("[ERROR] Status unknown: ", word, obj)
    return check_json(word, mean, model, times + 1)


def check(word, mean, model):
    last_obj = {}
    for i in range(10):
        obj = check_json(word, mean, model)
        status = obj["Status"]
        if status == "ok":
            # print("[OK] ", word, mean)
            return obj
        # JSONが正しくない?
        if "修正後" not in obj:
            print("[ERROR] Fix not found: ", word, obj)
            continue
        fix = obj["修正後"]
        if fix is None:
            print("[ERROR] Fix not found: ", word, obj)
            continue
        if "word" not in fix:
            print("[ERROR] Fix.word not found: ", word, obj)
            continue
        if "mean" not in fix:
            print("[ERROR] Fix.mean not found: ", word, obj)
            continue
        last_obj = obj
        # word2 = obj["修正後"]["word"]
        # if word != word2:
        #    print(f"[ERROR] Fix.word broken: {word}!={word2}", obj)
        #    continue
        # print(f"[{word}]=", json.dumps(obj, ensure_ascii=False))
        return obj
    print("[ERROR] faild 10 times")
    return last_obj


def file_check(fname):
    infile = fname
    outfile = fname.replace(".txt", "_fix.json")
    # check double
    # if os.path.exists(outfile):
    #     return
    # load data
    with open(infile, "rt", encoding="utf-8") as fp:
        text = fp.read()
    lines = text.split("\n")
    fix_list = []
    for line in lines:
        if "\t" not in line:
            continue
        word, mean = line.split("\t", 2)
        if "," in word:
            words = word.split(",")
        else:
            words = [word]
        print("")
        print("###", word)
        for w in words:
            # check db
            a = kudb.get(tag=w)
            if a and len(a) > 0:
                print(f"  - already : {w}")
                continue
            flag_ok = False
            flag_no_problem = False
            for retry in range(1, 5 + 1):
                obj = check(w, mean, model1)
                if obj["Status"] == "ok":
                    flag_no_problem = True
                    print(f"  - ok : {w} = {mean}")
                    break
                obj["org_mean"] = mean
                # 1次チェックが完了
                print(f"  - ORG: {mean}")
                print(f"  - FIX: {obj['修正後']['mean']}")
                # 2次チェック
                word2 = w
                mean2 = obj["修正後"]["mean"]
                obj2 = check(word2, mean2, model2)
                if obj2["Status"] == "ok":
                    flag_ok = True
                    break
                print(f"  - [?] {retry}回目: 2次チェックに失敗:やり直します: {obj2}")
            if flag_no_problem:
                kudb.insert(obj, tag=w)
                continue
            if not flag_ok:
                print(f"  - [ERROR] 5回やり直しても失敗: {w} {mean}")
            else:
                fix_list.append(obj)
                kudb.insert(obj, tag=w)
                print("  - SUCCESS!!")

    with open(outfile, "wt", encoding="utf-8") as fp:
        json.dump(fix_list, fp, ensure_ascii=False, indent=2)


def all_files_check():
    tools_dir = os.path.dirname(__file__)
    root = os.path.dirname(tools_dir)
    for code in range(ord("a"), ord("z") + 1):
        ch = chr(code)
        full = os.path.join(root, "src", f"{ch}.txt")
        file_check(full)


def remove_fix_json():
    tools_dir = os.path.dirname(__file__)
    root = os.path.dirname(tools_dir)
    files = glob(f"{root}/src/*_fix.json")
    for f in files:
        print(f)
        os.remove(f)


if __name__ == "__main__":
    # check("Alpaca", "アルパカ(日本産のロバ)")
    # check("animal", "動物")
    # check("sleep", "眠る")
    # check("Apple", "ゴリラ")
    # file_check("src/c.txt")
    all_files_check()
