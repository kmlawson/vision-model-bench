import unittest
from review import annotate


class ReviewTests(unittest.TestCase):
    def test_wrong_number_hover_and_original_text_preserved(self):
        text = '| 人口 | 1235 |\n'
        chunks = annotate('| 人口 | 1,234 |\n', text)
        self.assertEqual(''.join(c['text'] for c in chunks), text)
        wrong = [c for c in chunks if c['kind']=='incorrect']
        self.assertEqual(len(wrong),1)
        self.assertEqual(wrong[0]['text'],'1235')
        self.assertIn('1234',wrong[0]['hint'])

    def test_reordered_content_is_not_marked_wrong(self):
        chunks=annotate('alpha 12 beta 23','beta 23 alpha 12')
        self.assertFalse(any(c['kind']=='incorrect' for c in chunks))

    def test_width_proper_names_and_hyphenation(self):
        text='三笠山 １２３ trans-\nferred'
        chunks=annotate('三笠山 123 transferred',text)
        self.assertEqual(''.join(c['text'] for c in chunks),text)
        self.assertFalse(any(c['kind']=='incorrect' for c in chunks))

    def test_unknown_has_ground_truth_hover(self):
        wrong=[c for c in annotate('人口 1234','人口 [?]') if c['kind']=='incorrect']
        self.assertEqual(wrong[0]['text'],'[?]')
        self.assertIn('1234',wrong[0]['hint'])
