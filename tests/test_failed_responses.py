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


class FailedResponseTests(unittest.TestCase):
    def test_failed_raw_text_receives_zero_but_keeps_usage_and_error(self):
        names = ['1931-table-english', 'difficult-table', 'english-page', 'itinerary',
                 'population-stats-japanese', 'sideways-table', 'text-two-columns-plus-tables', 'wide-table']
        with tempfile.TemporaryDirectory() as directory:
            results = Path(directory)
            run_dir = results/'example'/'2026-10-26'
            run_dir.mkdir(parents=True)
            # Even a failed response that matches the reference must not earn credit.
            raw = {'response': (ROOT/'corrected'/f'{names[0]}.md').read_text(),
                   'input_tokens': 12, 'output_tokens': 34,
                   'response_json': {'status': 'incomplete', 'usage': {'total_tokens': 46, 'cost': .01}}}
            (run_dir/'failed.json').write_text(json.dumps(raw))
            tasks = [{'task': i, 'input': f'{name}.png', 'status': 'failed',
                      'error': 'Provider incomplete'} for i, name in enumerate(names, 1)]
            tasks[0]['raw_stdout'] = 'failed.json'
            (run_dir/'run.json').write_text(json.dumps({'status': 'incomplete', 'tasks': tasks}))
            with patch.object(builder, 'HERE', results):
                run = builder.collect()['runs'][0]
            task = run['tasks'][0]
            self.assertIsNone(task['output'])
            self.assertEqual(task['evaluation']['content']['f1'], 0)
            self.assertEqual(task['evaluation']['numbers']['f1'], 0)
            self.assertEqual(task['total_tokens'], 46)
            self.assertEqual(task['reported_cost_usd'], .01)
            self.assertEqual(task['error'], 'Provider incomplete')
            self.assertEqual(json.loads((run_dir/'failed.json').read_text()), raw)
