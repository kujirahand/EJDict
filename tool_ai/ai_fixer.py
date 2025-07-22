import json
from glob import glob
import ollama
import os
import random
import kudb
import ai_reporter

script_dir = os.path.dirname(__file__)
config_file = os.path.join(script_dir, "config.json")
db_file = os.path.join(script_dir, "ai_reporter.db")
# --------------------------
# FIX_MODEL = "gemma3n:e4b"
FIX_MODEL = "qwen3:8b"
TEMPLATE = """
### システム:
あなたは優秀な英語校正の専門家です。英和辞書の校正をしてください。
入力は、AIが修正したものなので、信頼性を確認する必要があります。

### 指示:
与えられた入力を確認して、校正作業が必要か判断してください。
もし修正を確認して妥当であれば、校正結果を「fix」として、修正すべきでなければ「pass」を指定してください。
「fix」の場合は、より良い修正案を考えて、修正後の英単語と、修正後の意味を考えてください。

### 備考:
- 英単語の表記にはcedillaを含めません。
- できるだけ「pass」を、必要がある際に「fix」を使用してください。
- `A / B / C`は、列挙で単語にAとBとCの意味があることを示します。
- `A, B, C`は、Aの言い換えがBやCであることを示します。
- `A; B`は、同じ単語の異なる意味があることを示します。
- `A(B)`は、Aの補足Bを示しています。
- `=A / B`は、Aと同じ意味であり、Bの別の意味も持つことを示します。
- `〈C〉` は、countableの略で「可算名詞（数えられる名詞）」を意味します。例えば、"an apple"。
- `〈U〉` は、uncountableの略で「不可算名詞（数えられない名詞）」を意味します。例えば、"water"。

### 入力:
```json
{{
    "英単語": "{word1}",
    "意味": "{mean1}",
    "修正箇所": "{place}",
    "修正理由": "{reason}",
    "修正後の英単語": "{word2}",
    "修正後の意味": "{mean2}"
}}
```

### 出力:
以下のJSONフォーマットで出力してください。
```json
{{
    "校正結果": "pass または fix",
    "校正理由": "校正が必要な理由",
    "校正後の英単語": "(校正後の英単語)",
    "校正後の意味": "(校正後の英単語の意味)",
}}
```

### 出力例1:
入力:
```json
    "英単語": "cot",
    "意味": "猫"
    "修正理由": "英単語のスペルミス",
    "修正後の英単語": "cat",
    "修正後の意味": "猫"
```
出力:
```json
{{
    "校正結果": "fix",
    "校正理由": "英単語のスペルミス",
    "校正後の英単語": "cat",
    "校正後の意味": "猫",
}}
```

### 出力例2:
入力:
```json
    "英単語": "cat",
    "意味": "猫"
    "修正理由": "意味が間違っている",
    "修正後の英単語": "cat",
    "修正後の意味": "犬"
```
出力:
```json
{{
    "校正結果": "pass",
    "校正理由": "修正ミスのため",
    "校正後の英単語": "cat",
    "校正後の意味": "猫",
}}
```
"""
# --------------------------
v2_json_format = """
{
    "結果": "error",
    "理由": "意味に誤字脱字があった",
    "修正後の英単語": "apple",
    "修正後の意味": "リンゴ"
}
"""

kudb.connect(db_file)

for row in kudb.get_all():
    status = row["結果"]
    if status == "ok":
        continue
    word1= row["英単語"]
    mean1 = row["意味"]
    word2 = row["修正後の英単語"]
    mean2 = row["修正後の意味"]
    reason = row["理由"]
    place = row["修正点"] if "修正点" in row else "意味"
    if "校正結果" in row:
        print("[SKIP] すでに校正済み:", row["英単語"])
        continue
    prompt = TEMPLATE.format(
        place=place,
        word1=word1,
        mean1=mean1,
        word2=word2,
        mean2=mean2,
        reason=reason)
    flag_check = False
    for _ in range(10):
        try:
            obj = ai_reporter.generate_json(prompt, FIX_MODEL)
        except Exception as e:
            print("[ERROR] JSONの取得に失敗:", e)
            continue
        if "校正結果" not in obj:
            print("[ERROR] 校正結果がありません:", word1)
            continue
        if "校正理由" not in obj:
            print("[ERROR] 校正理由がありません:", word1)
            continue
        if "校正後の英単語" not in obj:
            print("[ERROR] 校正後の英単語がありません:", word1)
            continue
        if "校正後の意味" not in obj:
            print("[ERROR] 校正後の意味がありません:", word1)
            continue
        flag_check = True
        for k, v in obj.items():
            row[k] = v
        break
    if flag_check:
        kudb.update_by_id(row["id"], row)
        # 結果を出力
        result = row["校正結果"]
        word3 = row["校正後の英単語"]
        mean3 = row["校正後の意味"]
        reason3 = row["校正理由"]        
        print(f"### [{word1}]の校正結果:", result)
        if result == "pass":
            continue
        print(f"- 理由3: {reason3}")
        print(f"  - 単語3: {word3}")
        print(f"  - 意味3: {mean3}")
        print(f"- 理由2: ({place}) {reason}")
        print(f"  - 単語1: {word1}")
        print(f"  - 意味1: {mean1}")
        print(f"  - 単語2: {word2}")
        print(f"  - 意味2: {mean2}")
