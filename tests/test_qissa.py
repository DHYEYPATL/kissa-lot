import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from qissa.catalog import bucket_bar
from qissa.craft import showrun
from qissa.eval_harness import run_eval
from qissa.pipeline import human_gate, run_desk
from qissa.sessions import get_session, save_session
from qissa.state import Character, Episode, SeriesState
from web.app import app


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
        self.assertEqual(state.canary.vs_catalog, "blocked")
        
        # Applying a direction still keeps canary blocked
        state = human_gate(state, "direct", "Give Meena more lines.")
        self.assertFalse(state.canary.ran)
        self.assertEqual(state.status, "review")
        
        # Approve unlocks canary
        state = human_gate(state, "approve", "Ship the tape scene.")
        self.assertTrue(state.canary.ran)
        self.assertTrue(state.canary.opted_in)
        self.assertIn(state.status, {"graduate", "archive"})

    def test_iteration_cap(self):
        state = run_desk("Kitchen secret.")
        state.cycle = 4
        state = human_gate(state, "direct", "darker")
        self.assertEqual(state.status, "archive")
        self.assertIn("iteration cap", state.verdict)

    def test_hit_bar_ignores_flops(self):
        bar = bucket_bar("campus dark romance")
        self.assertGreaterEqual(bar["completion_bar"], 0.60)

    def test_human_direction_changes_script(self):
        state = run_desk("A Surat cook hides a notebook.")
        before = state.episodes[0].script
        state = human_gate(state, "direct", "Give her more agency in scene 3 before minute 4")
        self.assertNotEqual(state.episodes[0].script, before)
        self.assertTrue(state.before_after)
        self.assertEqual(state.cycle, 1)

    def test_owned_fact_and_booth(self):
        state = run_desk("A Surat cook hides a notebook.", owned_fact="asafetida on the tape")
        self.assertEqual(state.owned_fact, "asafetida on the tape")
        self.assertTrue(state.refused_instinct)
        self.assertTrue(state.booth.get("audio_only"))
        self.assertIn("none", state.provenance.get("picture_track", ""))

    def test_showrun_does_not_clobber_family_drama(self):
        """Verifies that live Gemini generation in regional family drama is NEVER overwritten by hardcoded Surat scene."""
        mock_data = {
            "title": "Lineman and the Ghost Radio",
            "logline": "A retired telegraph lineman in Pune hears Morse code in an unplugged valve set.",
            "bible": "The telegraph line was cut in August 1947. The signals are still arriving.",
            "characters": [{"name": "Kashinath", "wound": "He sent the final evacuation dispatch"}],
            "spine": ["Ep1: Valve set hums", "Ep2: The missing name", "Ep3: Cut line", "Ep4: The reply"],
            "episode1_script": "KASHINATH: The line has been dead for fifty years.\nSFX: valve hum.\n",
            "cliffhanger": "The callsign belongs to his brother.",
            "first_turn_minute": 4.5,
            "exposition_minutes": 1.0,
        }
        with patch("qissa.llm.generate_json", return_value=mock_data), patch("qissa.llm.is_live_gemini", return_value=True):
            state = SeriesState(
                title="Lineman and the Ghost Radio",
                genre="regional family drama",
                seed="A retired telegraph lineman hears Morse code.",
                owned_fact="The solder flux smells like pine resin.",
            )
            state = showrun(state)
            self.assertEqual(state.title, "Lineman and the Ghost Radio")
            self.assertEqual(state.logline, mock_data["logline"])
            self.assertEqual(state.bible, mock_data["bible"])
            self.assertIn("KASHINATH", state.episodes[0].script)
            self.assertEqual(state.episodes[0].cliffhanger, mock_data["cliffhanger"])
            self.assertTrue(state.branches)

    def test_canon_guard_execution(self):
        """Verifies that canon guard executes in the diagnostic scan."""
        from qissa.bench import canon_guard
        state = SeriesState(
            title="Ghost Tale",
            characters=[Character(name="Vikram", goal="Survive", wound="Survivor guilt after flood")],
            episodes=[Episode(number=1, title="Ep 1", script="VIKRAM: I am still here.")],
        )
        state.memory.events = ["Vikram dies in hospital before episode 1"]
        diagnoses = canon_guard(state)
        issues = [d.issue for d in diagnoses]
        self.assertIn("canon drift", issues)

    def test_session_isolation(self):
        """Verifies that web/app.py maintains separate state and rejects unknown sessions."""
        client = TestClient(app)

        # User A opens a lot
        res_a = client.post("/api/open", data={"seed": "A telegraph lineman in Pune", "genre": "mythic thriller", "session_id": "user-a"})
        self.assertEqual(res_a.status_code, 200)
        self.assertEqual(res_a.json()["genre"], "mythic thriller")
        self.assertEqual(res_a.json()["session_id"], "user-a")

        # User B opens a lot
        res_b = client.post("/api/open", data={"seed": "A campus rumor in Bangalore", "genre": "campus dark romance", "session_id": "user-b"})
        self.assertEqual(res_b.status_code, 200)
        self.assertEqual(res_b.json()["genre"], "campus dark romance")
        self.assertEqual(res_b.json()["session_id"], "user-b")

        # Verify state in session store is distinct
        state_a = get_session("user-a")
        state_b = get_session("user-b")
        self.assertIsNotNone(state_a)
        self.assertIsNotNone(state_b)
        self.assertEqual(state_a.genre, "mythic thriller")
        self.assertEqual(state_b.genre, "campus dark romance")

        # User A directs rewrite on their own story
        res_gate = client.post("/api/gate", data={"action": "direct", "note": "Make it darker", "session_id": "user-a"})
        self.assertEqual(res_gate.status_code, 200)
        self.assertEqual(res_gate.json()["session_id"], "user-a")
        
        # User B unaffected
        self.assertEqual(get_session("user-b").cycle, 0)

        # Unknown session ID must return 404 error, NEVER leak User A's or User B's state
        res_unknown = client.post("/api/gate", data={"action": "approve", "session_id": "nonexistent-session"})
        self.assertEqual(res_unknown.status_code, 404)
        self.assertIn("not found or expired", res_unknown.json()["error"])


if __name__ == "__main__":
    unittest.main()
