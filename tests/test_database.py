import asyncio
import tempfile
import unittest
from pathlib import Path

from utils.database import Database


class DatabaseTests(unittest.TestCase):
    def test_config_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Database(Path(tmp) / "test.db")
            db.set_config(123, prefix="!", ai_enabled=True, ai_model="gpt-5.6-luna")
            cfg = db.get_config(123)
            self.assertEqual(cfg["prefix"], "!")
            self.assertTrue(cfg["ai_enabled"])
            self.assertEqual(cfg["ai_model"], "gpt-5.6-luna")

    def test_usage(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Database(Path(tmp) / "test.db")
            db.record_usage(123, 456, "ask")
            stats = db.get_usage(123, 456)
            self.assertEqual(stats["ask"], 1)


if __name__ == "__main__":
    unittest.main()
