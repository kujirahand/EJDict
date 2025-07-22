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

FIX_MODEL = "qwen3:8b"
TEMPLATE = """
### システム:
あなたは優秀な英語の先生です。英和辞書の校正をしてください。

### 指示:
1. 与えられた入力を確認してください。
2. もし修正すべきであれば校正結果に「fix」を、修正すべきでなければ「pass」を指定してください。
3. より良い修正案を考えて、修正後の英単語と意味を出力してください。

### 入力:
```json
{{
    "修正前の英単語": "{word1}",
    "修正前の意味": "{mean1}",
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
    "校正後の意味": "(校正後の意味)",
}}
```

### 出力例1:
入力:
```json
    "修正前の英単語": "cot",
    "修正前の意味": "猫"
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
    "修正前の英単語": "cat",
    "修正前の意味": "猫"
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
    if "校正結果" in row:
        print("[SKIP] すでに校正済み:", row["英単語"])
        continue
    word1= row["英単語"]
    mean1 = row["意味"]
    word2 = row["修正後の英単語"]
    mean2 = row["修正後の意味"]
    reason = row["理由"]
    #print(f"### [{word1}]")
    #print(f"  - {reason}")
    #print(f"  - [x] {mean1}", )
    #print(f"  - [o] {mean2}")
    prompt = TEMPLATE.format(
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
        # 結果を出力
        result = row["校正結果"]
        word3 = row["校正後の英単語"]
        mean3 = row["校正後の意味"]
        reason3 = row["校正理由"]
        print(f"### [{word1}]の校正結果:", result)
        print(f"- 理由: {reason3}")
        print(f"- 単語: {word3}")
        print(f"- 意味: {mean3}")
        kudb.update_by_id(row["id"], row)
        if result == "fix":
            print(f"  - 元の情報")
            print(f"    - [x]: {mean1}")
            print(f"    - [o]: {mean2}")
