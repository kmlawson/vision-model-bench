import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('runner', Path(__file__).parents[1] / 'run-cli-benchmark.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class CodexResponseTests(unittest.TestCase):
    def test_preserves_final_text_and_reported_usage(self):
        usage = {'input_tokens': 120, 'cached_input_tokens': 100,
                 'output_tokens': 40, 'reasoning_output_tokens': 12}
        events = [{'type': 'item.completed', 'item': {'type': 'agent_message', 'text': '正文'}},
                  {'type': 'turn.completed', 'usage': usage}]
        with tempfile.TemporaryDirectory() as directory:
            final = Path(directory) / 'final.md'
            final.write_text('正文\n| A | 12 |\n')
            result = runner.codex_response('\n'.join(map(json.dumps, events)), final)
            self.assertEqual(result['response'], final.read_text())
            self.assertEqual(result['usage'], usage)
            self.assertEqual(result['tool_items'], [])

    def test_failed_turn_cannot_be_scored_as_success(self):
        with tempfile.TemporaryDirectory() as directory:
            final = Path(directory) / 'final.md'
            final.write_text('partial response')
            with self.assertRaises(ValueError):
                runner.codex_response('{"type":"turn.failed","error":"failed"}', final)

    def test_missing_final_text_cannot_be_scored_as_success(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                runner.codex_response('{"type":"turn.completed","usage":{}}', Path(directory) / 'missing.md')
