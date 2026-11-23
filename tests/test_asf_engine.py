import tempfile
import unittest
from pathlib import Path
from asf_engine import CandidateStore, Profile, Criteria, classify, load_fixture


class ASFTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = CandidateStore(Path(self.temp.name) / "test.sqlite")

    def tearDown(self):
        self.store.close()
        self.temp.cleanup()

    def test_classify_is_conservative(self):
        self.assertEqual(classify(Profile("a", 4000, "creator"))[0], "candidate")
        self.assertEqual(classify(Profile("b", 800, "creator"))[0], "excluded")
        self.assertEqual(classify(Profile("c", 4000, "official company"))[0], "excluded")
        self.assertEqual(classify(Profile("d", 4000, "some topic"))[0], "review")

    def test_idempotent_reimport_and_update(self):
        batch = [Profile("a", 2000, "review"), Profile("b", 100, "creator")]
        self.assertEqual(self.store.upsert(batch)["inserted"], 2)
        self.assertEqual(self.store.upsert(batch)["unchanged"], 2)
        self.assertEqual(len(self.store.list()), 2)
        self.assertEqual(self.store.upsert([Profile("b", 3000, "creator")])["changed"], 1)
        self.assertEqual(len(self.store.list("candidate")), 2)

    def test_invalid_does_not_enter_store(self):
        self.assertEqual(
            self.store.upsert([Profile("", 2000, "creator"), Profile("bad", -1, "review")])["invalid"], 2
        )
        self.assertEqual(self.store.list(), [])

    def test_export_and_reopen(self):
        self.store.upsert([Profile("x", 2000, "creator")])
        output = Path(self.temp.name) / "candidates.csv"
        self.assertEqual(self.store.export_csv(output), 1)
        self.assertIn("x", output.read_text(encoding="utf-8"))
        self.assertIn("creator", output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
