import os
import kudb
import ai_reporter
import time

# --------------------------
# ai_reporter.db に fix2=pass/fixを設定します。
# --------------------------
script_dir = os.path.dirname(__file__)
config_file = os.path.join(script_dir, "config.json")
db_file = os.path.join(script_dir, "ai_reporter.db")
# --------------------------
# FIX_MODEL = "gemma3n:e4b"
FIX_MODEL = "qwen3:8b"
# OLLAMA_HOST = "http://localhost:11434"
# print("===", "Ollama host:", OLLAMA_HOST)
OLLAMA_HOST = ai_reporter.load_config()
TEMPLATE = """
### 指示:
あなたは優秀な英和辞書です。
与えられた英単語の意味として、候補AとBのどちらが相応しいかを判定して、結果として`A`または`B`を出力してください。
もし、AもBも相応しくない場合は、結果に`C`と相応しい意味を出力してください。
ただし、`C`を出力するのは、明らかな間違いがある場合のみです。

### 備考:
- 英単語の表記にはcedillaを含めません。
- `A / B / C`は、列挙で単語にAとBとCの意味があることを示します。
- `A, B, C`は、Aの言い換えがBやCであることを示します。
- `A; B`は、同じ単語の異なる意味があることを示します。
- `A(B)`は、Aの補足Bを示しています。
- `=A / B`は、Aと同じ意味であり、Bの別の意味も持つことを示します。
- `〈C〉` は、countableの略で「可算名詞（数えられる名詞）」を意味します。例えば、"an apple"。`〈C〉リンゴ`のように指定
- `〈U〉` は、uncountableの略で「不可算名詞（数えられない名詞）」を意味します。例えば、"water"。`〈U〉水`のように指定

### 入力:
```json
{{
    "英単語": "{word}",
    "A": "{mean1}",
    "B": "{mean3}"
}}
```

### 出力:
以下のJSONフォーマットで出力してください。
結果は、`A`、`B`、または`C`のいずれか1文字を指定してください。
```json
{{
    "結果": "(A|B|C)",
    "意味": "(英単語の意味)",
}}
```

### 出力例:
入力: {{"英単語": "cat", "A": "猫", "B": "犬"}}
出力:
```json
{{
    "結果": "A",
    "意味": "猫"
}}
```
"""

kudb.connect(db_file)

for i, row in enumerate(kudb.get_all()):    
    status = row["結果"]
    if status == "ok":
        continue
    word1= row["英単語"]
    mean1 = row["意味"]
    word2 = row["修正後の英単語"]
    mean2 = row["修正後の意味"]
    mean3 = row.get("校正後の意味", mean2)
    reason = row["理由"]
    place = row["修正点"] if "修正点" in row else "意味"
    if place == "英単語":
        continue  # 今回英単語の修正はしない
    if "校正結果" not in row:
        continue
    if "fix2" in row:
        continue # ai_fixer2ですでに修正済み
    fix = row["校正結果"]
    if fix == "pass":
        continue
    # 自動修正が可能な場合がある
    if mean1 == mean3:
        print(f"自動修正可能: {word1} の意味は修正前と一緒")
        row["fix2"] = "pass"
        row["校正結果"] = "pass"
        row["備考"] = "自動修正可能"
        kudb.update(id=row["id"], tag=word1, new_value=row)
        continue
    # 自動修正
    mean3 = row["校正後の意味"] = mean3.replace("、", ",")
    # AIで優れた意味を確認
    flag_ok = False
    print("===")
    print("# [英単語]", word1)
    prompt = TEMPLATE.format(word=word1, mean1=mean1, mean3=mean3)
    # print(prompt)
    for i in range(3):
        obj = ai_reporter.generate_json(prompt, FIX_MODEL, host=OLLAMA_HOST)
        if obj is None or "結果" not in obj:
            print("[ERROR] 結果がありません:", word1)
            obj = ai_reporter.generate_json(prompt, FIX_MODEL, host=OLLAMA_HOST)
            if obj is None or "結果" not in obj:
                print("[ERROR] 結果がありません2:", word1)
                continue
        flag_ok = True
        break
    if not flag_ok:
        print("[ERROR] AIの結果が得られません:", word1)
        continue
    flag_changed = False
    if obj["結果"] == "A":
        print(f"[OK] {word1} の意味は A ({mean1})")
        row["fix2"] = "pass"
        row["校正結果"] = "pass"
        row["備考"] = "fix2でAIが修正不要と判断(A)"
        flag_changed = True
    if obj["結果"] == "B":
        print(f"[OK] {word1} の意味は B ({mean3})")
        row["fix2"] = "fix"
        row["校正結果"] = "fix"
        row["備考"] = "fix2でAIが修正必要と判断(B)"
        flag_changed = True
    if obj["結果"] == "C":
        print(f"[OK] {word1} の意味は C ({obj['意味']})")
        row["fix2"] = "fix"
        row["校正結果"] = "fix"
        row["校正後の意味"] = obj["意味"]
        row["備考"] = "fix2でAIが再修正必要(C)と判断"
        flag_changed = True
    if not flag_changed:
        print(f"[ERROR] {word1} の意味は不明: {obj}")
    # save
    kudb.update(id=row["id"], tag=word1, new_value=row)
    time.sleep(3) # 少し待つ
    continue
    # ここまで自動修正できない場合は、手動で確認
    # 手間がかかるので止める
    # エントリを表示
    print("=" * 60)
    print("# [英単語]", word1)
    print("- [意味]", mean3)
    print("- [修正前の意味]", mean1)
    print(json.dumps(row, indent=2, ensure_ascii=False))
    # シンプルに英語の意味を生成
    mean4 = obj["意味"]
    print("[AI4]", mean4)
    print("選択肢:")
    print("[p] 修正不要: 校正結果を pass に戻して備考を入力")
    print("[y] 校正結果は正しい")
    print("[a] AI4の意味を採用して修正")
    print("[o] 手動で修正")
    print("[n] 今回は触らず再度検討する")
    choice = "y"
    while True:
        choice = input("選択肢を入力してください: ").strip().lower()
        if choice in ['p', 'y', 'a', 'o', 'n']:
            break
        print("無効な選択肢です。もう一度入力してください。")
    if choice == "p":
        # 校正結果を pass に戻す
        row["fix2"] = "pass"
        row["校正結果"] = "pass"
        row["校正理由"] = "人間が修正を確認(fix2)"
        print("校正結果を pass に変更しました。")
    elif choice == "y":
        # 校正結果は正しいので、修正する
        row["fix2"] = "fix"
    elif choice == "a":
        # 第三者の意見を採用
        row["fix2"] = "fix"
        row["校正後の意味"] = mean4
    elif choice == "n":
        # 今回は見送り
        continue
    elif choice == "o":
        # 入力
        while True:
            user = input("修正後の意味を入力してください: ").strip()
            print("入力された修正後の意味:", user)
            yn = input("この修正を採用しますか？ (y/N): ").strip().lower()
            if yn != 'y':
                continue
            break
        row["fix2"] = "fix"
        row["校正後の意味"] = user
    user = input("備考があれば記入(省略可):")
    row["備考"] = user.strip()
    # DBに更新を記録
    kudb.update_by_id(row["id"], row)
