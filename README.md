# English-Japanese Dictionary "ejdict-hand"

- This is the English-Japanese Dictionary data (Public Domain / No Copyright).
- これはパブリックドメインの英和辞書データです。

## 間違いを見つけたら？

- 気軽にプルリクエストください。あるいは、メールにて修正点をお伝えください。
- よく分からなくても間違いを見つけたら、気軽にメールにてお知らせください。宛先は、クジラ飛行机( web@kujirahand.com )まで。
- その際、複数の変更がある場合、基本となる辞書のバージョンやダウンロード日時などをお知らせください。

## 辞書データのダウンロード

以下、くじらはんどのWebサイトにてテキスト形式、SQLite形式のデータをダウンロードできます。

- [URL] http://kujirahand.com/web-tools/EJDictFreeDL.php

## 辞書データのテスト

以下のWebサイトで辞書データをテストできます。

 - [URL] https://kujirahand.com/web-tools/EJDict.php

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

## License

- [Public Domain CC0](https://creativecommons.org/publicdomain/zero/1.0/)
- [パブリックドメイン CC0](https://creativecommons.org/publicdomain/zero/1.0/deed.ja)
