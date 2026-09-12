import unittest
from cogs.ai import clean_secret, safe_path


class SecurityTests(unittest.TestCase):
    def test_secret_redaction(self):
        text = "OPENAI_API_KEY=sk-test-example-value"
        self.assertNotIn("sk-test-example-value", clean_secret(text))

    def test_safe_path_blocks_traversal(self):
        self.assertIsNone(safe_path("../secret.txt"))
        self.assertIsNone(safe_path("/etc/passwd"))
        self.assertEqual(safe_path("src/main.py"), "src/main.py")


if __name__ == "__main__":
    unittest.main()
