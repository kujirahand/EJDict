# EJDict 開発者・AIエージェント向けガイド (AGENTS.md)

このドキュメントは、英和辞書データ『ejdict-hand』プロジェクトのフォルダ構造、データ形式、および `tools/` ディレクトリに配置されている各種開発ツールについて解説します。

---

## 1. プロジェクトのフォルダ構造

```text
EJDict/
├── src/                    # 辞書データのソースファイル群
│   ├── a.txt               # アルファベット「a」で始まる単語の辞書データ
│   ├── b.txt               # アルファベット「b」で始まる単語の辞書データ
│   └── ... (z.txtまで)
├── release/                # ビルドされたリリース用ファイル（ビルド実行時に生成される）
│   ├── ejdict-hand-utf8.txt  # すべてのデータを結合したUTF-8テキストファイル
│   ├── ejdict.json         # JSON形式に変換した辞書データ
│   └── ejdict.sqlite3      # SQLite3形式のデータベースファイル
├── tools/                  # データ処理、ビルド、検証用スクリプト群
│   ├── schema.sql          # SQLite3データベースのテーブルスキーマ
│   ├── level.txt           # 単語の重要度レベルデータ（SQLiteビルド時に参照）
│   └── (各種PHP/Pythonスクリプト - 後述)
├── justfile                # タスクランナー just の設定ファイル
├── README.md               # プロジェクトの概要説明（日本語）
└── README-en.md            # プロジェクトの概要説明（英語）
```

---

## 2. 辞書データの形式

### ソースファイル (`src/*.txt`)
- ファイル名は `a.txt` から `z.txt` までのアルファベット小文字1文字。
- 各行は、**`単語` と `意味（訳語）` がタブ文字 (`\t`) で区切られた**テキストデータです。
  ```text
  apple\tリンゴ、林檎
  book\t本、書籍
  ```
- 1つのキーに複数のスペルバリエーションがある場合は、カンマ（`,`）で区切られて登録されていることがあります。
- 意味の部分には、必要に応じて括弧 `(...)` や `[...]`、日本語の説明が含まれます。

---

## 3. ツール一覧と役割

`tools/` ディレクトリ配下にあるスクリプトの役割と使用方法のまとめです。

### A. ビルド & パッケージング

| スクリプト名 | 言語 | 役割 |
| :--- | :--- | :--- |
| [join-files.php](tools/join-files.php) | PHP | `src/*.txt` のすべてのファイルを結合し、`release/ejdict-hand-utf8.txt` を出力します。 |
| [tojson.php](tools/tojson.php) | PHP | `src/*.txt` から `release/ejdict.json` を生成します。同音異義語は ` / ` で結合されます。 |
| [tosqlite.php](tools/tosqlite.php) | PHP | `release/ejdict.json` および `tools/level.txt` から SQLite データベース `release/ejdict.sqlite3` を構築します。 |
| [makezip.php](tools/makezip.php) | PHP | リリース用ファイル（txt, json, sqlite3）と `tools/README.md` をそれぞれ ZIP 圧縮してルートに配置します。 |
| [clean.php](tools/clean.php) | PHP | `release/` ディレクトリ内の生成物およびルートの `.zip` ファイルを削除します。 |
| [z-release.php](tools/z-release.php) | PHP | 結合・SQLiteビルド・ZIP圧縮を順番に実行する一括スクリプトです（JSONビルドが含まれていないため、Makefile/justfile側のタスク実行が推奨されます）。 |

### B. バリデーション & 整合性チェック

| スクリプト名 | 言語 | 役割 |
| :--- | :--- | :--- |
| [check_data.php](tools/check_data.php) | PHP | `src/` 配下に `a.txt` から `z.txt` までが正しく存在するか、また各行が正常に「タブ区切り」になっているか（2カラム構成か）を検証します。 |
| [check_brackets.py](tools/check_brackets.py) | Python | 訳語部分のカッコ（丸カッコ、角カッコ、全角カッコなど）の対応が崩れている（閉じカッコが無いなど）箇所を検出して報告します。 |

### C. データ自動修正・整形

| スクリプト名 | 言語 | 役割 |
| :--- | :--- | :--- |
| [fix_brackets.py](tools/fix_brackets.py) | Python | `check_brackets.py` で検出されるような、カッコの対応崩れを自動で補正・修復します。 |
| [fix_zen_han.py](tools/fix_zen_han.py) | Python | 全角のスペース、カッコ、コロン、ピリオドなどを半角に一括置換して統一します。 |
| [normalize.php](tools/normalize.php) | PHP | 訳語に含まれる表記のブレを修正したり、特定の全角記号を半角に揃える標準化処理を実行します。 |

### D. 分割 & 統合の特殊ツール

| スクリプト名 | 言語 | 役割 |
| :--- | :--- | :--- |
| [split-text.php](tools/split-text.php) | PHP | 統合されたテキストファイル（`release/ejdict-hand-utf8.txt`）から頭文字（a-z）ごとに分割して `src/*.txt` を再配置します。 |
| [cli_split_text.php](tools/cli_split_text.php) | PHP | コマンドライン引数で渡されたテキストファイルから頭文字ごとに分割して `src/*.txt` を構築します。 |
| [split100-1-split.py](tools/split100-1-split.py) | Python | LLM等での翻訳・校正処理を容易にするため、`src/*.txt` を100行ずつに分割してサブフォルダ（例: `src/a/a001.txt`）に出力します。 |
| [split100-2-join.py](tools/split100-2-join.py) | Python | 100行ずつに分割されたファイルを元の `src/*.txt` に結合し直し、辞書順に再ソートします。 |
| [split100-3-remove.py](tools/split100-3-remove.py) | Python | 分割用サブフォルダ内のファイルを削除してクリーンアップします。 |

---

## 4. `just` を使った作業手順

プロジェクトルートに用意されている `justfile` を使うことで、複雑な引数や各スクリプトの言語の違いを意識することなく、統一されたコマンドで作業を行うことができます。

主要なコマンドの例：
- リリースパッケージを一括作成する: `just build-all`
- データの不整合をチェックする: `just check`
- 自動修正を行う: `just fix`
- AI等での処理用に100行に分割する: `just split-100`

詳細は `just --list` または [justfile](justfile) を確認してください。
