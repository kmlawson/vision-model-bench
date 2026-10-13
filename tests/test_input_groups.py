import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('builder', Path(__file__).parents[1]/'results/build-index.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class InputGroupTests(unittest.TestCase):
    def test_group_membership_and_overlap(self):
        self.assertEqual([g['tasks'] for g in builder.INPUT_GROUPS],
                         [[1,3,6,8],[1,2,3,6,8],[4,5,7]])

    def test_equal_weights_and_failure_zero(self):
        tasks = [{'task':i,'evaluation':{'content':{'f1':0 if i==2 else 1},
                                        'numbers':{'f1':0 if i==2 else .5}}}
                 for i in range(1,9)]
        result = builder.input_group_scores(tasks)
        self.assertEqual(result['english'],{'content':1,'number':.5,'overall':.75})
        self.assertEqual(result['english_asian'],{'content':.8,'number':.4,'overall':(.8+.4)/2})
        self.assertEqual(result['japanese'],{'content':1,'number':.5,'overall':.75})
