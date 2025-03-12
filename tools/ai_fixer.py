import json
from glob import glob
import ollama
import os
import random
import kudb

ollama_host = "http://localhost:11434"
client = ollama.Client(host=ollama_host)
# model = "codellama"
# model = "lucas2024/llama-3-elyza-jp-8b:q5_k_m"
model = "phi4:14b"
kudb.connect("ai_reporter.db")
### kudb.clear() # 必要に応じて

for row in kudb.get_all():
    print("----------")
    # print('get_all >', row) # all
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
    print(f""""
-----------------------
### Instruction:
英和辞書の単語『{word}』の日本語訳として相応しいのはどちらでしょうか？
- 修正前: {mean1}
- 修正後: {mean2}
- 修正理由: {reason}
-----------------------
""")
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

