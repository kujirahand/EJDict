# English-Japanese Dictionary "ejdic-hand"

- これはパブリックドメインの英和辞書データです。
- This is the English-Japanese Dictionary data (Public Domain).

## 間違いを見つけたら？

- 気軽にプルリクエストください。あるいは、メールにて修正点をお伝えください。
- よく分からなくても、間違いを見つけたら、気軽に、メールにて、クジラ飛行机<web@kujirahnad.com> までお知らせください。

## ダウンロード

以下、くじらはんどのWebサイトにてテキスト形式、SQLite形式のデータをダウンロードできます。

- http://kujirahand.com/web-tools/EJDictFreeDL.php

## フォーマット

- src ディレクトリに、アルファベットフォトのテキストデータがあります。
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
