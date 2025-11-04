# English-Japanese Dictionary "ejdict-hand"

- This is the English-Japanese Dictionary data (Public Domain / No Copyright).
- This is public domain English-Japanese dictionary data.

## Download Dictionary Data

You can download the data in text format or SQLite format from the Kujirahand website below:

- [Download Dictionary Data](http://kujirahand.com/web-tools/EJDictFreeDL.php)

## Test the Dictionary Data

You can test the dictionary data on the following website:

- [Test the Dictionary Data](https://kujirahand.com/web-tools/EJDict.php)

## Found a Mistake?

- Feel free to submit a pull request or send corrections via email.

## Data Format

- In the `src` directory, there are text data files organized by alphabet.
- The files in the `release` directory are combined and sorted versions of the files in the `src` directory.

Each dictionary entry is formatted as follows:

```plaintext
word1 \t meaning1
word2 \t meaning2
word3 \t meaning3
...
```

If words have the same meaning but slightly different spellings, they are listed separated by commas:

```plaintext
word1, word2, word3 \t meaning
```

## Tools

```sh
# Combine dictionary data split by alphabet into one file
$ php tools/join-files.php

# Convert dictionary data into SQLite format
$ php tools/tosqlite.php
```

## Meaning of Dictionary Symbols

- `A / B / C` indicates that the word has meanings A, B, and C.
- `A, B, C` indicates that B and C are synonyms or alternative expressions for A.
- `A; B` indicates that the word has different meanings A and B.
- `A(B)` provides additional information B about A.
- `=A / B` indicates that it has the same meaning as A and also has another meaning B.
- `〈C〉` stands for "countable noun," meaning a noun that can be counted, e.g., "an apple."
- `〈U〉` stands for "uncountable noun," meaning a noun that cannot be counted, e.g., "water."
- `{形}` means "adjective."
- `{副}` means "adverb."
- `{動}` means "verb."
- `《米》` indicates American English.
- `《英》` indicates British English.
- `《俗》` indicates slang.
- `《口》` indicates colloquial expressions.
- `《差別的表現》` indicates discriminatory expressions. Please avoid using them.
- `《まれ》` indicates rarely used expressions.
- `《法》` indicates legal terms.

## License

- [Public Domain CC0](https://creativecommons.org/publicdomain/zero/1.0/)
- [Public Domain CC0 (Japanese)](https://creativecommons.org/publicdomain/zero/1.0/deed.ja)