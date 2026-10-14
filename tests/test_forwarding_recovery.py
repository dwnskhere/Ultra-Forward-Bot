"""Regression tests for forwarding checkpoints and recovery helpers."""

import json
import os
import unittest
from pathlib import Path
from types import SimpleNamespace

# Make imports deterministic without needing live production secrets or MongoDB.
os.environ.setdefault("DB_URL", "mongodb://localhost:27017")
os.environ.setdefault("DB_NAME", "ultra_forward_test")
os.environ.setdefault("API_ID", "12345")
os.environ.setdefault("API_HASH", "test-api-hash")
os.environ.setdefault("BOT_TOKEN", "12345:test-token")

from plugins.recovery import final_task_status, next_source_message_id, retry_delay_seconds
from plugins.test import start_clone_bot


ROOT = Path(__file__).resolve().parents[1]


class RecoveryHelperTests(unittest.TestCase):
    def test_resume_offset_is_exclusive(self):
        self.assertEqual(next_source_message_id(250000), 250000)
        self.assertEqual(next_source_message_id(None), 0)
        self.assertEqual(next_source_message_id(-4), 0)

    def test_final_status_distinguishes_delivery_errors(self):
        self.assertEqual(final_task_status({"failed": 0}), "completed")
        self.assertEqual(final_task_status({"failed": 2}), "completed_with_errors")
        self.assertEqual(final_task_status({}), "completed")

    def test_recovery_retry_delay_is_bounded(self):
        self.assertEqual(retry_delay_seconds(1), 5)
        self.assertEqual(retry_delay_seconds(2), 10)
        self.assertEqual(retry_delay_seconds(99), 300)

    def test_app_manifest_is_valid_json(self):
        with (ROOT / "app.json").open(encoding="utf-8") as manifest_file:
            manifest = json.load(manifest_file)
        self.assertEqual(manifest["repository"], "https://github.com/dwnskhere/Ultra-Forward-Bot")
        self.assertIn("DB_URL", manifest["env"])
        self.assertIn("DB_NAME", manifest["env"])
        self.assertEqual(manifest["stack"], "container")
        self.assertEqual(manifest["formation"]["worker"]["quantity"], 1)
        self.assertEqual(manifest["formation"]["worker"]["size"], "basic")

    def test_heroku_manifest_declares_worker_command(self):
        heroku_manifest = (ROOT / "heroku.yml").read_text(encoding="utf-8")
        self.assertIn("worker: Dockerfile", heroku_manifest)
        self.assertIn("worker: python main.py", heroku_manifest)
        self.assertIn("Deploy to Heroku", (ROOT / "README.md").read_text(encoding="utf-8"))


class SourceIteratorTests(unittest.IsolatedAsyncioTestCase):
    async def test_iterator_does_not_repeat_inclusive_boundary(self):
        class FakeNode:
            def __init__(self):
                self.requested = []

            async def start(self):
                return None

            async def get_messages(self, chat_id, message_ids):
                self.requested.append(list(message_ids))
                return [SimpleNamespace(id=message_id) for message_id in reversed(message_ids)]

        node = FakeNode()
        await start_clone_bot(node)
        actual = []
        async for item in node.iter_messages(node, chat_id=-100123, limit=201, offset=0):
            actual.append(item.id)

        self.assertEqual(actual, list(range(1, 202)))
        self.assertEqual(node.requested[0], list(range(1, 201)))
        self.assertEqual(node.requested[1], [201])
        self.assertEqual(len(actual), len(set(actual)))

    async def test_restart_resumes_after_saved_source_message_id(self):
        class FakeNode:
            async def start(self):
                return None

            async def get_messages(self, chat_id, message_ids):
                return [SimpleNamespace(id=message_id) for message_id in message_ids]

        node = FakeNode()
        await start_clone_bot(node)
        actual = []
        async for item in node.iter_messages(
            node, chat_id=-100123, limit=250005, offset=250000
        ):
            actual.append(item.id)

        self.assertEqual(actual, [250001, 250002, 250003, 250004, 250005])


if __name__ == "__main__":
    unittest.main()
