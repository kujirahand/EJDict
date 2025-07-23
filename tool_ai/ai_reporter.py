# AIを利用して辞書の誤字脱字を検出するツール

# 使い方:
# ! pip install ollama
# ! pip install kudb
# ! pip install demjson3
# ! python tools/ai_reporter.py

import json
from glob import glob
import ollama
import os
import random
import kudb
import time
import demjson3

script_dir = os.path.dirname(__file__)
config_file = os.path.join(script_dir, "config.json")
db_file = os.path.join(script_dir, "ai_reporter.db")
# ---
OLLAMA_HOST = "http://localhost:11434"
TEMPERATURE = 0.3  # 温度設定
# model
#model1 = "qwen3:14b"
#model2 = "gemma3n:e4b"
#model3 = "qwen3:8b"

model1 = "qwen3:8b"
model2 = "gemma3n:e4b"
model3 = "qwen3:14b"


# ---
IS_DEBUG = True
CHECK_TIMES = 5  # チェックの最大回数
# ----

# 明らかな間違いがある場合のみ、明確な理由を付けて指摘してください。

PROMPT = """
### System:
あなたは辞書の校正者です。与えられた単語と意味をチェックし、誤りがあれば修正案を提案します。
/no_think

### Instruction:
Inputを読み、校正の例を参考にして、**JSONだけ**を出力してください。
誤字脱字や明確な間違いがあると分かった場合のみ、結果に「error」を指定して、修正案を出力してください。

### 備考:
- 英単語の表記にはcedillaを含めません。
- `A / B / C`は、列挙で単語にAとBとCの意味があることを示します。
- `A, B, C`は、Aの言い換えがBやCであることを示します。
- `A; B`は、同じ単語の異なる意味があることを示します。
- `A(B)`は、Aの補足Bを示しています。
- `=A / B`は、Aと同じ意味であり、Bの別の意味も持つことを示します。
- `〈C〉` は、countableの略で「可算名詞（数えられる名詞）」を意味します。例えば、"an apple"。`〈C〉リンゴ`のように指定
- `〈U〉` は、uncountableの略で「不可算名詞（数えられない名詞）」を意味します。例えば、"water"。`〈U〉水`のように指定
- 英単語に`B.P.`のような省略形が与えられた時は`bills payable / blood pressure`などの完全系を出力します。

### Input:
```json
{{"英単語": "{word}", "意味": "{mean}"}}
```

### Output:
JSON形式の次のような形式で出力してください。

```json
{{
    "結果": "ok または error",
    "理由": "理由",
    "修正後の英単語": "正しい単語の綴り",
    "修正後の意味": "正しい意味"
}}
```

### 校正の例1:
Input: {{"英単語": "cat", "意味": "猫"}}
Output:
```json
{{
    "結果": "ok",
    "理由": "問題ない",
    "修正後の英単語": "cat",
    "修正後の意味": "猫"
}}
```

### 校正の例2:
Input: {{"英単語": "cot", "意味": "猫"}}
Output:
```json
{{
    "結果": "error",
    "理由": "英単語の綴りミス",
    "修正後の英単語": "cat",
    "修正後の意味": "猫"
}}
```

### 校正の例3:
Input: {{"英単語": "Alpaca", "意味": "アルパカ(日本産のロバ)"}}
Output:
```json
{{
    "結果": "error",
    "理由": "意味の間違い→アルパカはロバではなく、南米の動物です。",
    "修正後の英単語": "Alpaca",
    "修正後の意味": "アルパカ(南米の動物)"
}}
```

### 校正の例4:
Input: {{"英単語": "apple", "意味": "リソゴ"}}
Output:
```json
{{
    "結果": "error",
    "理由": "意味に誤字脱字があった",
    "修正後の英単語": "apple",
    "修正後の意味": "リンゴ"
}}
```
"""

kudb.connect(db_file)

def load_config():
    """Load configuration from config.json."""
    global OLLAMA_HOST
    if os.path.exists(config_file):
        with open(config_file, "r", encoding="utf-8") as fp:
            j = json.load(fp)
            if "host" in j:
                OLLAMA_HOST = j["host"]
    return OLLAMA_HOST

load_config()
time_adv = -1
llm_count = 0
print("===", "Ollama host:", OLLAMA_HOST)


def generate(prompt, model=model1, temperature=TEMPERATURE, host=OLLAMA_HOST):
    """Generate text using the Ollama client."""
    global time_adv, llm_count
    start_time = time.time()
    # create client
    client = ollama.Client(host=host)
    response = client.generate(
        model=model,
        prompt=prompt,
        options={
            "temperature": temperature,
        },
    )
    res = response["response"]
    if "</think>" in res:
        res = res.split("</think>")[-1].strip()
    end_time = time.time()
    ellipsised_time = end_time - start_time
    if time_adv < 0:
        time_adv = ellipsised_time
    else:
        time_adv = (time_adv + ellipsised_time) / 2
    llm_count += 1
    if llm_count % 10 == 0:
        print(f"[INFO] LLM count: {llm_count}, Average time: {time_adv:.2f} seconds")
    return res

def generate_json(prompt, model=model1, temperature=TEMPERATURE, host=OLLAMA_HOST):
    """Generate JSON using the Ollama client."""
    for i in range(CHECK_TIMES):
        if i > 3:
            if model == model2:
                model = model3
            else:
                model = model2
        try:
            res = generate(prompt, model, temperature=temperature, host=host)
        except Exception as e:
            print(f"[ERROR] generate_json failed ({i}times): {e}")
            continue
        if "```" not in res:
            # 直接JSONが出力された？
            res = "```json\n" + res + "\n```\n"
        blocks = res.split("```")
        if len(blocks) < 3:
            print("[ERROR] broken json: ", res)
            continue
        json_str = blocks[1].strip()
        if json_str[0:4] == "json":
            json_str = json_str[4:]
        try:
            obj = demjson3.decode(json_str)
            return obj
        except Exception as e:
            print(f"[ERROR] JSON parse error: ```\n{json_str}\n```: {e}")
            continue
    print(f"[ERROR] generate_json :", prompt)
    raise ValueError("failed to generate valid JSON after multiple attempts")

def check_raw(word, mean, model):
    """Check the word and meaning using the Ollama model."""
    prompt = PROMPT.format(
        word=word,
        mean=mean
    )
    return generate(prompt, model)


def check_json(word, mean, model, times=0):
    if times > CHECK_TIMES:
        print(f"[ERROR] failed {CHECK_TIMES} times: check_json : {word}:{mean}")
        raise ValueError("failed 10 times")
    if times > 2:
        model = model2  # 3回目以降は別のモデルを使用
    # プロンプトを実行してJSONを取得
    text = check_raw(word, mean, model)
    if "```" not in text:
        # 直接JSONが出力された？
        text = "```json\n" + text + "\n```\n"
    blocks = text.split("```")
    if len(blocks) < 3:
        print("[ERROR] broken json: ", word, ":", text)
        return check_json(word, mean, model, times + 1)
    json_str = blocks[1].strip()
    if json_str[0:4] == "json":
        json_str = json_str[4:]
    try:
        obj = demjson3.decode(json_str)
        return obj
    except Exception:
        print(f"[ERROR] JSON parse error: ```\n{json_str}\n```")
        return check_json(word, mean, model, times + 1)


def check(word, mean, model=model1):
    for _ in range(CHECK_TIMES):
        obj = check_json(word, mean, model)
        # objがNoneの場合はスキップ
        if obj is None:
            print(f"[ERROR] check_json returned None for: {word}")
            continue
        # JSONが正しくない?
        if "結果" not in obj:
            print("[ERROR] 「結果」がない: ", word, obj)
            continue
        if "理由" not in obj:
            print("[ERROR] 「理由」がない: ", word, obj)
            continue
        if "修正後の英単語" not in obj:
            print("[ERROR] 「修正後の英単語」がない: ", word, obj)
            continue
        if "修正後の意味" not in obj:
            print("[ERROR] 「修正後の意味」がない: ", word, obj)
            continue
        # 結果を確認
        status = obj["結果"]
        if status == "ok":
            return obj
        # 正しく結果が出力された場合
        return obj
    print(f"[ERROR] 正しいJSONの取得に{CHECK_TIMES}回失敗しました: ", word)
    return {"結果": "ok"}

def check_word(word, mean, fix_list):
    """Check a single word and meaning."""
    word = word.strip()
    mean = mean.strip()
    # 既に確認済みか？
    if kudb.get(tag=word):
        print(f"- [OK] {word} - 確認済み")
        return
    # チェック実行
    result = check(word, mean)
    result["英単語"] = word
    result["意味"] = mean
    if result["結果"] == "ok":
        print(f"- [OK] {word}")
        kudb.insert(tag=word, value=result)
        return
    # 信頼性の確認
    fix_word = result["修正後の英単語"]
    fix_mean = result["修正後の意味"]
    if word == fix_word and mean == fix_mean:
        print(f"- [OK] {word} (修正なし)")
        kudb.insert(tag=word, value=result)
        return
    if word == fix_word:
        result["修正点"] = "意味"
    else:
        result["修正点"] = "英単語"
    # 結果を保存
    fix_list.append(result)
    kudb.insert(tag=word, value=result)
    
    print("+ [NG]", result["修正点"], word)
    print(f"  - 理由:{result['理由']}")
    if result["修正点"] == "意味":
        print(f"  - [x]: {mean}")
        print(f"  - [o]: {fix_mean}")
    else:
        print(f"  - [x] 英単語: {word}")
        print(f"  - [o] 英単語: {fix_word}")

def file_check(fname):
    infile = fname
    outfile = fname.replace(".txt", "_fix.json")
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
        for word1 in words:
            check_word(word1, mean, fix_list)

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
    if False:
        check("Alpaca", "アルパカ(日本産のロバ)")
        check("animal", "動物")
        check("sleep", "眠る")
        check("Apple", "ゴリラ")
    # file_check("../src/z.txt")
    all_files_check()
