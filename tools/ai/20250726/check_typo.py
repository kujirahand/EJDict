# typo checker
import os
import glob
import ollama
import json

DIR_SCRIPT = os.path.dirname(__file__)
DIR_AI = os.path.dirname(DIR_SCRIPT)
DIR_TOOLS = os.path.dirname(DIR_AI)
DIR_ROOT = os.path.dirname(DIR_TOOLS)
DIR_SRC = os.path.join(DIR_ROOT, "src")

# MODEL = "gemma3n:e4b"
MODEL = "qwen3:14b"
TEMPLATE = """\
### 指示:
あなたは、与えられたテキストの誤字脱字をチェックし、修正案を提案するAIアシスタントです。
入力するデータは、英和辞書です。
JSON形式で誤字脱字の修正案を出力してください。

### 入力形式:
各辞書のデータは、タブ区切りのCSVで、次のような形式になっています。

```tsv
行番号1	英単語1	意味1
行番号2	英単語2	意味2
行番号3	英単語3	意味3
行番号4	英単語4a, 英単語4b	意味4
```

### 辞書の記号の意味

- `A / B / C`は、列挙で単語にAとBとCの意味があることを示します。
- `A, B, C`は、Aの言い換えがBやCであることを示します。
- `A; B`は、同じ単語の異なる意味があることを示します。
- `A(B)`は、Aの補足Bを示しています。
- `=A / B`は、Aと同じ意味であり、Bの別の意味も持つことを示します。
- `〈C〉` は、countableの略で「可算名詞（数えられる名詞）」を意味します。例えば、"an apple"。
- `〈U〉` は、uncountableの略で「不可算名詞（数えられない名詞）」を意味します。例えば、"water"。
- `{{形}}`は 「形容詞（adjective）」 を意味します。
- `{{副}}`は、副詞（adverb）を意味します。
- `{{動}}`は、動詞（verb）を意味します。
- `《米》`は、アメリカ英語を意味します。
- `《英》`は、イギリス英語を意味します。
- `《俗》`は、俗語を意味します。
- `《口》`は、口語を意味します。
- `《差別的表現》`は、差別的な表現を含むことを示します。利用を避けてください。

### 出力:
出力は、次のようなJSON形式で、誤字脱字の修正案を提案してください。

```json
[
    {{"行番号": (番号), "誤字": "(誤字)", "修正案": "修正案"}},
    {{"行番号": (番号), "誤字": "(誤字)", "修正案": "修正案"}},
    {{"行番号": (番号), "誤字": "(誤字)", "修正案": "修正案"}},
    …
]
```

### 出力例

```json
[
    {{"行番号": (番号), "誤字": "catt", "修正案": "cat"}},
    {{"行番号": (番号), "誤字": "笑の顔", "修正案": "笑顔"}},
    …
]
```

### 入力:
```tsv
{INPUT}
```
"""
# clinet = ollama.Client(host="http://localhost:11434")
clinet = ollama.Client(host="http://192.168.1.23:11435")

def generate(prompt, model=MODEL):
    """ Generate text using the Ollama client."""
    try:
        response = clinet.chat(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            options={
                "temperature": 0.5
            }
        )
        return response['message']['content']
    except Exception as e:
        print(f"Error generating text: {e}")
        return None

def text_to_json(text):
    """テキスト内にあるJSONを抽出してオブジェクトに変換する"""
    if "```json" in text:
        try:
            start = text.index("```json") + len("```json")
            end = text.index("```", start)
            json_text = text[start:end].strip()
            return json.loads(json_text)
        except ValueError as e:
            print(f"Error parsing JSON: {e}")
    elif "```" in text:
        try:
            start = text.index("```") + len("```")
            end = text.index("```", start)
            json_text = text[start:end].strip()
            return json.loads(json_text)
        except ValueError as e:
            print(f"Error parsing JSON: {e}")
    return []

def typo_check(file_path):
    """ ファイルを読んで、LLMに送信して誤字脱字をチェックする """
    print("[CHEKING]", file_path)
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    # テキストの一行毎に行番号を付与
    lines = text.splitlines()
    numbered_lines = "\n".join(f"{i+1}\t{line}" for i, line in enumerate(lines))

    # LLMに送信して誤字脱字をチェック
    prompt = TEMPLATE.format(INPUT=numbered_lines)
    print("[PROMPT]", prompt)
    response = generate(prompt)
    print("=" * 50)
    print("[RESPONSE]", response)
    print("=" * 50)

    if response:
        # レスポンスからJSONを抽出
        corrections = text_to_json(response)
        if corrections:
            print(f"Corrections for {file_path}:")
            for correction in corrections:
                print(correction)
        else:
            print(f"No corrections found for {file_path}.")
    else:
        print(f"Failed to get a response for {file_path}.")

def check_typo_allfiles():
    # Get all text files in the src directory
    files = glob.glob(os.path.join(DIR_SRC, '**', '*.txt'), recursive=True)
    for file_path in sorted(files, reverse=True):
        typo_check(file_path)

if __name__ == "__main__":
    check_typo_allfiles()