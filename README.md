# English-Japanese Dictionary "ejdict-hand"

- This is the English-Japanese Dictionary data (Public Domain / No Copyright). [→English](README-en.md)
- これはパブリックドメインの英和辞書データです。

## 辞書データのダウンロード

以下、くじらはんどのWebサイトにてテキスト形式、SQLite形式のデータをダウンロードできます。

- [URL] http://kujirahand.com/web-tools/EJDictFreeDL.php

## 辞書データのテスト

以下のWebサイトで辞書データをテストできます。

- [URL] https://kujirahand.com/web-tools/EJDict.php

## 間違いを見つけたら？

- 気軽にプルリクエストください。あるいは、メールにて修正点をお伝えください。

## データフォーマット

- src ディレクトリに、アルファベットごとのテキストデータがあります。
- release ディレクトリのものは、srcディレクトリのファイルを結合しソートしたものです。

各辞書のデータは、次のような形式になっています。

```
英単語1 \t 意味1
英単語2 \t 意味2
英単語3 \t 意味3
...
```

ただし、意味が同じで綴りが少し異なるだけの単語は、カンマで区切って列挙されます。

```
英単語, 英単語, 英単語 \t 意味
```

## ツール

```sh
# アルファベットごとに分割された辞書データを一つにまとめる
$ php tools/join-files.php

# 辞書データをSQLite形式のDBに変換する
$ php tools/tosqlite.php
```

## 辞書の記号の意味

- `A / B / C`は、列挙で単語にAとBとCの意味があることを示します。
- `A, B, C`は、Aの言い換えがBやCであることを示します。
- `A; B`は、同じ単語の異なる意味があることを示します。
- `A(B)`は、Aの補足Bを示しています。
- `=A / B`は、Aと同じ意味であり、Bの別の意味も持つことを示します。
- `〈C〉` は、countableの略で「可算名詞（数えられる名詞）」を意味します。例えば、"an apple"。
- `〈U〉` は、uncountableの略で「不可算名詞（数えられない名詞）」を意味します。例えば、"water"。
- `{形}`は 「形容詞（adjective）」 を意味します。
- `{副}`は、副詞（adverb）を意味します。
- `{動}`は、動詞（verb）を意味します。
- `《米》`は、アメリカ英語を意味します。
- `《英》`は、イギリス英語を意味します。
- `《俗》`は、俗語を意味します。
- `《口》`は、口語を意味します。
- `《差別的表現》`は、差別的な表現を含むことを示します。利用を避けてください。
- `《まれ》`は、まれに使われる表現を意味します。
- `《法》`は、法律用語を意味します。

## 改変履歴

- 2025/11/04 生成AI(GitHub Copilot{Claude Sonnet 4.5})を利用した自動校正を実施。軽微な誤字脱字を多数修正。
- 2025/07/25 生成AI(Ollama{qwen3:14b, gemma3n:e4b})を利用した大々的な自動校正を実施(GPUを3日間回しっぱなし)
- それ以前、人力での誤字脱字修正や加筆修正を随時実施した。

## License

- [Public Domain CC0](https://creativecommons.org/publicdomain/zero/1.0/)
- [パブリックドメイン CC0](https://creativecommons.org/publicdomain/zero/1.0/deed.ja)
