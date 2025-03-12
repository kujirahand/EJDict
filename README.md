# English-Japanese Dictionary "ejdict-hand"

- This is the English-Japanese Dictionary data (Public Domain / No Copyright).
- これはパブリックドメインの英和辞書データです。

## 辞書データのダウンロード

以下、くじらはんどのWebサイトにてテキスト形式、SQLite形式のデータをダウンロードできます。

- [URL] http://kujirahand.com/web-tools/EJDictFreeDL.php

## 辞書データのテスト

以下のWebサイトで辞書データをテストできます。

 - [URL] https://kujirahand.com/web-tools/EJDict.php

## 間違いを見つけたら？

- 気軽にプルリクエストください。あるいは、メールにて修正点をお伝えください。
- よく分からなくても間違いを見つけたら、気軽にメールにてお知らせください。宛先は、クジラ飛行机( web@kujirahand.com )まで。その際には、複数の変更がある場合、基本となる辞書のバージョンやダウンロード日時などをお知らせください。

## フォーマット

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
````

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
- `《米》`は、アメリカ英語を意味します。
- `《英》`は、イギリス英語を意味します。

## License

- [Public Domain CC0](https://creativecommons.org/publicdomain/zero/1.0/)
- [パブリックドメイン CC0](https://creativecommons.org/publicdomain/zero/1.0/deed.ja)
