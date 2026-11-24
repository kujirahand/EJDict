"""Check source ordering and meaning formatting without changing dictionary data."""

from pathlib import Path
import re
import sys


def check_lines(lines):
    """Yield (line number, message) for each quality issue in TSV lines."""
    previous = None
    for lineno, line in enumerate(lines, 1):
        cells = line.rstrip("\r\n").split("\t")
        if len(cells) != 2:
            # check_data.php is responsible for malformed TSV lines.
            continue
        word, meaning = cells
        key = word.encode("utf-8")
        if previous is not None and previous > key:
            yield lineno, f"headword out of UTF-8 byte order: {word}"
        previous = key

        segments = [segment.strip() for segment in meaning.split(" / ")]
        if any(a == b for a, b in zip(segments, segments[1:])):
            yield lineno, f"consecutive duplicate meanings: {word}"
        if meaning.rstrip().endswith(","):
            yield lineno, f"trailing comma in meaning: {word}"
        if re.search(r" {2,}", meaning):
            yield lineno, f"repeated spaces in meaning: {word}"
        # A slash with a space on only one side is a malformed separator.
        # Unspaced slashes also occur in fractions, abbreviations and examples;
        # their role cannot be decided from whitespace alone.
        for index, char in enumerate(meaning):
            if char != "/":
                continue
            left = index > 0 and meaning[index - 1] == " "
            right = index + 1 < len(meaning) and meaning[index + 1] == " "
            if left != right:
                yield lineno, f"inconsistent spaces around meaning separator: {word}"
                break


def main():
    errors = 0
    src = Path(__file__).resolve().parent.parent / "src"
    for path in sorted(src.glob("?.txt")):
        with path.open(encoding="utf-8") as source:
            for lineno, message in check_lines(source):
                print(f"{path.name}:{lineno}: {message}")
                errors += 1
    if errors:
        print(f"Total quality issues: {errors}")
        return 1
    print("No quality issues found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
