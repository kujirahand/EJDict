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

kudb.connect(db_file)

for row in kudb.get_all():
    print("----------")
    # print('get_all >', row) # all
    status = row["Status"]
    if status == "ok":
        continue
    if "データ修正済" in row:
        print("skip", row["修正後"]["word"])
        continue
    fix = row["修正後"]
    word = fix["word"]
    mean1 = row["org_mean"]
    mean2 = fix["mean"]
    reason = row["Reason"]
    print(f"* [{word}]")
    print("ORG:", mean1)
    print("FIX:", mean2)
    print("Reason:", reason)
    prompt = f""""

-----------------------
### 背景:
以下の入力は、AIによる英和辞書の単語『{word}』の日本語訳の修正例です。

### 指示:
1.『{word}』の意味が修正前よりも修正後が相応しいか判定してください。
2.次に、修正後の単語を洗練させて出力してください。

### 入力:
- 英単語: {word}
- 修正前: {mean1}
- 修正後: {mean2}
- 修正理由: {reason}

### 出力例:

- 英単語: {word}
- 結論: (修正後|修正後)の方が正しいです。
- 理由: xxx
- さらに洗練させた表現に直すと次のようになります。

```json
{{
    "word": "{word}",
    "mean": "{mean2}"
}}
```
-----------------------
"""
    print(prompt)
    print("------------------")
    print("<result>")
    print(ai_reporter.generate(prompt, ai_reporter.model3))
    print("</result>")

    # --- check user input ---
    for _ in range(10):
        i = input("remove this line press [k] >>> ")
        if len(i) >= 2:
            continue
        break
    if i == "k":
        row["データ修正済"] = True
        kudb.update_by_tag(word, row)
        print("--- marked ---")
    else:
        print("--- next ---")
