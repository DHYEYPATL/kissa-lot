import unittest
from pathlib import Path

from kissa_lot.tools.complexity import score_complexity
from kissa_lot.tools.script_parse import parse_screenplay


class ParserTests(unittest.TestCase):
    def test_night_kitchen(self):
        raw = (Path(__file__).resolve().parents[1] / "examples" / "night_kitchen.fountain").read_text()
        breakdown = parse_screenplay(raw, title_hint="Night Kitchen")
        self.assertEqual(breakdown.title, "Night Kitchen")
        self.assertIn("Surat Dhaba Kitchen", breakdown.locations)
        self.assertGreaterEqual(breakdown.night_scenes, 2)
        self.assertTrue(any("Meena" in c for c in breakdown.characters))
        report = score_complexity(breakdown)
        self.assertGreaterEqual(report.score, 20)
        self.assertTrue(report.shooting_groups)

    def test_logline_only(self):
        breakdown = parse_screenplay("A grandmother in Pune hides a Partition letter inside a radio.")
        self.assertEqual(len(breakdown.scenes), 1)
        self.assertGreaterEqual(score_complexity(breakdown).score, 1)


if __name__ == "__main__":
    unittest.main()
