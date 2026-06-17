# default task: list all available recipes
default:
    @just --list

# Remove build outputs and temporary zip packages
clean:
    php tools/clean.php

# Build release files (join text files, convert to json, and build sqlite3)
build:
    php tools/join-files.php
    php tools/tojson.php
    php tools/tosqlite.php

# Package build output files into zip files at repository root
makezip:
    php tools/makezip.php

# Clean, rebuild all artifacts, and make zip packages
build-all: clean build makezip

# Validate format of src/*.txt files and check brackets balance
check:
    php tools/check_data.php
    python3 tools/check_brackets.py

# Automatically fix mismatched brackets in dictionary text
fix-brackets:
    python3 tools/fix_brackets.py

# Convert full-width characters (spaces, brackets, commas, colons, etc) to half-width
fix-zen-han:
    python3 tools/fix_zen_han.py

# Normalize Japanese meanings (kana normalization, space formatting)
normalize:
    php tools/normalize.php

# Run all formatting and normalization tasks (fix-zen-han, fix-brackets, normalize)
fix-all: fix-zen-han fix-brackets normalize

# Split merged ejdict-hand-utf8.txt back into src/*.txt by letter
split-all:
    php tools/split-text.php

# Split custom text file into src/*.txt by letter
cli-split input_file:
    php tools/cli_split_text.php {{input_file}}

# Split src/*.txt files into 100-line chunk files for LLM/AI editing
split-100:
    python3 tools/split100-1-split.py

# Join 100-line chunk files back to src/*.txt files and sort them
join-100:
    python3 tools/split100-2-join.py

# Remove 100-line chunk files and directories (requires confirmation)
remove-100:
    python3 tools/split100-3-remove.py
