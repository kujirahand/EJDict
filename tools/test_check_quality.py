"""Regression coverage for Issue #73 checks and legitimate dictionary notation."""

import unittest

from check_quality import check_lines


class QualityCheckTest(unittest.TestCase):
    def test_detects_issue_73_patterns(self):
        cases = [
            (["A,a,an\t冠詞", "A level\t試験"], "byte order"),
            (["overeat\t食べ過ぎる / 食べ過ぎる"], "duplicate"),
            (["instructive\t『ためになる』,"], "trailing comma"),
            (["chap\tやつ /  {名}ひび"], "repeated spaces"),
            (["deli\t惣菜店/ 惣菜"], "separator"),
            (["hassle\t苦心 /面倒"], "separator"),
        ]
        for lines, message in cases:
            with self.subTest(lines=lines):
                self.assertTrue(any(message in text for _, text in check_lines(lines)))

    def test_preserves_legitimate_notation(self):
        lines = [
            "A level\t試験\n",
            "A,a,an\t冠詞\n",
            "cable\t〈C〉〈U〉 / 太綱 / 〈C〉〈U〉 / ケーブル線\n",
            "centavo\t1/100ペソ / A/V / And/Or / 斜線(/)\n",
            "landholder\t地主(＝landowner) / 【用例】～ / ￡\n",
            "mercuric\t{形}水銀の / 水銀を含む\n",
        ]
        self.assertEqual(list(check_lines(lines)), [])

    def test_reports_source_line(self):
        self.assertEqual(
            list(check_lines(["apple\tリンゴ\n", "book\t本,\n"])),
            [(2, "trailing comma in meaning: book")],
        )


if __name__ == "__main__":
    unittest.main()
