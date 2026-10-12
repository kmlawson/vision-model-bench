import random
import unittest
from evaluate import edit_distance, normalize, score

class EvaluationTests(unittest.TestCase):
    def test_presentation_does_not_change_content(self):
        a = '# Total\n| Item | Value |\n|---|---:|\n| Foo | 1,234.00 |'
        b = '<h1>TOTAL</h1>\nItem\tValue\nFoo\t1234'
        self.assertEqual(score(a,b)['content']['f1'],1)
        self.assertEqual(score(a,b)['numbers']['f1'],1)

    def test_layout_reordering_not_penalized_by_headline(self):
        result=score('alpha 12 beta 23','beta 23 alpha 12')
        self.assertEqual(result['content']['f1'],1)
        self.assertGreater(result['cer'],0)

    def test_incorrect_digits_and_extra_text_are_penalized(self):
        result=score('人口 1234','人口 1235 invented')
        self.assertLess(result['content']['f1'],1)
        self.assertEqual(result['numbers']['f1'],0)
        self.assertTrue(result['content']['missing'])
        self.assertTrue(result['content']['extra'])

    def test_multilingual_numeric_aliases_and_proper_names(self):
        a='第三案 二萬以上 三笠山村 船中二泊'
        b='第3案 20,000以上 三笠山村 船中2泊'
        self.assertEqual(score(a,b)['content']['f1'],1)
        self.assertNotIn('n:3',normalize('三笠山村')['tokens'])
        self.assertEqual(score('明治元年','明治1年')['content']['f1'],1)

    def test_clock_and_superscript_styles(self):
        self.assertEqual(score('05・23 204','5:23 ２０４','itinerary.png')['content']['f1'],1)
        self.assertEqual(score('Australia¹ 25.9ᵃ','Australia [1] 25.90[a]')['content']['f1'],1)

    def test_unknowns_are_errors_and_failures_score_zero(self):
        self.assertLess(score('人口 1234','人口 [?]')['content']['f1'],1)
        self.assertEqual(score('人口 1234',None)['content']['f1'],0)
        self.assertEqual(score('人口 1234',None)['cer'],1)

    def test_genuine_spelling_and_glyph_errors_remain(self):
        self.assertLess(score('transferred 國','transfered 国')['content']['f1'],1)

    def test_exact_distance_against_independent_dynamic_program(self):
        def slow(a,b):
            row=list(range(len(b)+1))
            for i,x in enumerate(a,1):
                new=[i]
                for j,y in enumerate(b,1):new.append(min(new[-1]+1,row[j]+1,row[j-1]+(x!=y)))
                row=new
            return row[-1]
        random.seed(13)
        for _ in range(150):
            a=''.join(random.choices('abc人口',k=random.randrange(20)))
            b=''.join(random.choices('abc人口',k=random.randrange(20)))
            self.assertEqual(edit_distance(a,b),slow(a,b))

if __name__ == '__main__': unittest.main()
