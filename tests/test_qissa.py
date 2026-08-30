import unittest

from qissa.eval_harness import run_eval
from qissa.pipeline import human_gate, run_desk
from qissa.state import SeriesState


class QissaTests(unittest.TestCase):
    def test_eval_catches_bad_story(self):
        result = run_eval()
        self.assertTrue(result["bad_flagged_exposition"])
        self.assertTrue(result["clone_caught"])
        self.assertTrue(result["pass"])

    def test_pipeline_offline(self):
        state = run_desk("A Surat cook hides a notebook.")
        self.assertIsInstance(state, SeriesState)
        self.assertEqual(len(state.twin_scores), 6)
        self.assertTrue(state.episodes)
        self.assertEqual(state.status, "review")
        state = human_gate(state, "reject", "Too much producer.")
        self.assertEqual(state.status, "archive")
        self.assertTrue(state.rework_brief)

    def test_iteration_cap(self):
        state = run_desk("Kitchen secret.")
        state.cycle = 4
        state = human_gate(state, "direct", "darker")
        self.assertEqual(state.status, "archive")


if __name__ == "__main__":
    unittest.main()
