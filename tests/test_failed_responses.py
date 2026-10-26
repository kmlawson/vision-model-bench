import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).parents[1]
spec = importlib.util.spec_from_file_location('failed_response_builder', ROOT/'results/build-index.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)
INPUTS = ['1931-table-english', 'difficult-table', 'english-page', 'itinerary',
          'population-stats-japanese', 'sideways-table', 'text-two-columns-plus-tables', 'wide-table']


class FailedResponseTests(unittest.TestCase):
    def collect_task(self, raw, status='completed', name='example'):
        with tempfile.TemporaryDirectory() as directory:
            results = Path(directory)
            run_dir = results/name/'2026-10-26'
            run_dir.mkdir(parents=True)
            (run_dir/'response.json').write_text(json.dumps(raw))
            tasks = [{'task': i, 'input': f'{name}.png', 'status': 'failed',
                      'error': 'Provider incomplete'} for i, name in enumerate(INPUTS, 1)]
            tasks[0].update(status=status, raw_stdout='response.json')
            (run_dir/'run.json').write_text(json.dumps({'status': 'incomplete', 'tasks': tasks}))
            with patch.object(builder, 'HERE', results):
                task = builder.collect()['runs'][0]['tasks'][0]
            self.assertEqual(json.loads((run_dir/'response.json').read_text()), raw)
            return task

    def test_failed_raw_text_receives_zero_but_keeps_usage_and_error(self):
        # Even a failed response that matches the reference must not earn credit.
        raw = {'response': (ROOT/'corrected'/f'{INPUTS[0]}.md').read_text(),
               'input_tokens': 12, 'output_tokens': 34,
               'response_json': {'status': 'incomplete', 'usage': {'total_tokens': 46, 'cost': .01}}}
        task = self.collect_task(raw, status='failed')
        self.assertIsNone(task['output'])
        self.assertEqual(task['evaluation']['content']['f1'], 0)
        self.assertEqual(task['evaluation']['numbers']['f1'], 0)
        self.assertEqual(task['total_tokens'], 46)
        self.assertEqual(task['reported_cost_usd'], .01)
        self.assertEqual(task['error'], 'Provider incomplete')

    def test_native_gemini_thought_tokens_are_not_counted_twice(self):
        raw = {'response': 'A table', 'input_tokens': 112, 'output_tokens': 135,
               'token_details': json.dumps({'candidatesTokenCount': 35, 'thoughtsTokenCount': 100,
                                            'cachedContentTokenCount': 12}),
               'response_json': {'modelVersion': 'gemini-4-argon',
                                 'candidates': [{'finishReason': 'STOP'}]}}
        task = self.collect_task(raw, name='gemini-4-argon')
        self.assertEqual(task['input_tokens'], 112)
        self.assertEqual(task['output_tokens'], 135)
        self.assertEqual(task['thinking_tokens'], 100)
        self.assertEqual(task['cached_input_tokens'], 12)
        self.assertEqual(task['total_tokens'], 247)
        self.assertIsNone(task['reported_cost_usd'])

    def test_native_mistral_completion_details_are_captured(self):
        usage = {'prompt_tokens': 2276, 'completion_tokens': 5430, 'total_tokens': 7706,
                 'prompt_tokens_details': {'cached_tokens': 0},
                 'completion_tokens_details': {'reasoning_tokens': 4702}}
        raw = {'response': 'A table', 'input_tokens': 2276, 'output_tokens': 5430,
               'response_json': {'model': 'mistral-large-4', 'usage': usage}}
        task = self.collect_task(raw, name='mistral-large-4')
        self.assertEqual(task['thinking_tokens'], 4702)
        self.assertEqual(task['cached_input_tokens'], 0)
        self.assertEqual(task['total_tokens'], 7706)
        self.assertEqual(task['output_tokens'], 5430)
        self.assertIsNone(task['reported_cost_usd'])
