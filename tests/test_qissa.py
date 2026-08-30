import unittest

from qissa.catalog import bucket_bar
from qissa.eval_harness import run_eval
from qissa.pipeline import human_gate, run_desk
from qissa.state import SeriesState


class QissaTests(unittest.TestCase):
    def test_eval_catches_bad_story(self):
        result = run_eval()
        self.assertTrue(result["bad_flagged_exposition"])
        self.assertTrue(result["clone_caught"])
        self.assertTrue(result["twins_rank_good_above_bad"])
        self.assertTrue(result["pass"])

    def test_pipeline_offline(self):
        state = run_desk("A Surat cook hides a notebook.")
        self.assertIsInstance(state, SeriesState)
        self.assertEqual(len(state.twin_scores), 7)
        self.assertTrue(state.episodes)
        self.assertEqual(state.status, "review")
        self.assertFalse(state.canary.ran)
        self.assertTrue(state.ledger.promises or state.memory.open_threads)
        state = human_gate(state, "reject", "Too much producer.")
        self.assertEqual(state.status, "archive")
        self.assertTrue(state.rework_brief)

    def test_canary_waits_for_human(self):
        state = run_desk("Kitchen secret.")
        self.assertFalse(state.canary.ran)
        state = human_gate(state, "approve", "Ship the tape scene.")
        self.assertTrue(state.canary.ran)
        self.assertTrue(state.canary.opted_in)
        self.assertIn(state.status, {"graduate", "review", "iterate"})

    def test_iteration_cap(self):
        state = run_desk("Kitchen secret.")
        state.cycle = 4
        state = human_gate(state, "direct", "darker")
        self.assertEqual(state.status, "archive")

    def test_hit_bar_ignores_flops(self):
        bar = bucket_bar("campus dark romance")
        self.assertGreaterEqual(bar["completion_bar"], 0.60)

    def test_human_direction_changes_script(self):
        state = run_desk("A Surat cook hides a notebook.")
        before = state.episodes[0].script
        state = human_gate(state, "direct", "Give her more agency in scene 3")
        self.assertNotEqual(state.episodes[0].script, before)
        self.assertTrue(state.before_after)
        self.assertEqual(state.cycle, 1)


if __name__ == "__main__":
    unittest.main()
