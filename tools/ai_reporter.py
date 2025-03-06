# ! pip install ollama
import json
from glob import glob
import ollama
import os
import random

ollama_host = "http://localhost:11434"
client = ollama.Client(host=ollama_host)
# model = "codellama"
# model = "lucas2024/llama-3-elyza-jp-8b:q5_k_m"
model = "phi4"


def generate(prompt):
    response = client.generate(
        model=model,
        system="あなたは優秀な文章校正者です。これから英和辞典の誤字脱字を調査します。",
        prompt=prompt,
        options={"temperature": 0.7, "seed": random.randint(1, 100000)},
    )
    return response["response"]


def check_raw(word, mean):
    prompt = """
### Instruction:
Inputを確認して、Outputの例を参考にして、**JSONだけ**を出力してください。

### Input:
```json
{{"word": "{word}", "mean": "{mean}"}}
```

### Output:
```json
{{"Status": "error", "Reason": "意味が間違っている", "Fix": {{"word": "fish", "mean": "魚"}}}}
```
OR
```json
{{"Status": "error", "Reason": "誤字がある", "Fix": {{"word": "animal", "mean": "動物"}}}}
```
OR
```json
{{"Status": "ok"}}
```
""".format(
        word=word, mean=mean
    )
    return generate(prompt)


def check(word, mean):
    last_obj = {}
    for i in range(5):
        text = check_raw(word, mean)
        if "```" not in text:
            # 直接JSONが出力された？
            text = "```json\n" + text + "\n```\n"
        blocks = text.split("```")
        if len(blocks) < 3:
            print("[ERROR] broken json: ", word, ":", text)
            continue
        json_str = blocks[1].strip()
        if json_str[0:4] == "json":
            json_str = json_str[4:]
        try:
            obj = json.loads(json_str)
        except Exception:
            print("[ERROR] JSON parse error: ", word)
            continue
        if "Status" not in obj:
            print("[ERROR] Status not found: ", word, obj)
            continue
        status = obj["Status"]
        if status == "ok":
            return obj
        if "Fix" not in obj:
            print("[ERROR] Fix not found: ", word, obj)
            continue
        fix = obj["Fix"]
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
        word2 = obj["Fix"]["word"]
        if word != word2:
            print(f"[ERROR] Fix.word broken: {word}!={word2}", obj)
            continue
        print(f"[{word}]=", json.dumps(obj, ensure_ascii=False))
        return obj
    print("[ERROR] faild 5 times")
    return last_obj


def file_check(fname):
    infile = fname
    outfile = fname.replace(".txt", "_fix.json")
    # check double
    if os.path.exists(outfile):
        return
    # load data
    with open(infile, "rt", encoding="utf-8") as fp:
        text = fp.read()
    lines = text.split("\n")
    fix_list = []
    for line in lines:
        if "\t" not in line:
            continue
        word, mean = line.split("\t")
        if len(mean) > 2 and mean[0] == "=":
            continue
        if "," in word:
            words = word.split(",")
        else:
            words = [word]
        for w in words:
            print("-----", w, "-----", mean, "-----")
            obj = check(w, mean)
            if obj["Status"] == "ok":
                continue
            obj["org_mean"] = mean
            fix_list.append(obj)
    with open(outfile, "wt", encoding="utf-8") as fp:
        json.dump(fix_list, fp, ensure_ascii=False)


def all_files_check():
    tools_dir = os.path.dirname(__file__)
    root = os.path.dirname(tools_dir)
    files = glob(f"{root}/src/*.txt")
    for f in files:
        file_check(f)


def remove_fix_json():
    tools_dir = os.path.dirname(__file__)
    root = os.path.dirname(tools_dir)
    files = glob(f"{root}/src/*_fix.json")
    for f in files:
        print(f)
        os.remove(f)


if __name__ == "__main__":
    check("Alpaca", "アルパカ(日本産のロバ)")
    file_check("src/a.txt")
    all_files_check()
    # check("animal", "動物")
    # check("sleep", "眠る")
