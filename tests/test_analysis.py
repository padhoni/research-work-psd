import unittest
from analysis import analyze, simulate, DEMO

class AnalysisTests(unittest.TestCase):
    def test_document_values(self):
        r = analyze(DEMO)
        self.assertAlmostEqual(r['pre'], 5.11)
        self.assertAlmostEqual(r['post'], 4.16)
        self.assertAlmostEqual(r['reduction'], 18.590998043)
        self.assertAlmostEqual(r['t'], 42.48529157)
        self.assertAlmostEqual(r['sd'], .05)
        self.assertLess(r['p'], .0001)
        self.assertAlmostEqual(r['ci'][0], .8879168001)
        self.assertAlmostEqual(r['ci'][1], 1.0120831999)
        self.assertIn('Simulated', r['report'])
    def test_bad_pairs(self):
        for text in ['clinician_id,pre,post\na,1,2', 'clinician_id,pre,post\na,1,2\na,3,4', 'clinician_id,pre,post\na,nan,2\nb,3,4', 'clinician_id,pre,post\na,1,\nb,3,4','clinician_id,pre,post\na,-1,2\nb,3,4']:
            with self.subTest(text=text), self.assertRaises(ValueError): analyze(text)
    def test_degenerate(self):
        r=analyze('clinician_id,pre,post\na,0,1\nb,0,1')
        self.assertIsNone(r['t'])
        self.assertIsNone(r['ci'])
        self.assertIsNone(r['reduction'])
    def test_workload_scale(self):
        with self.assertRaises(ValueError): analyze('clinician_id,pre,post\na,461,25\nb,430,24', 'workload')
    def test_increase_and_null(self):
        r=analyze('clinician_id,pre,post\na,1,2\nb,2,4\nc,3,4')
        self.assertLess(r['difference'],0)
        self.assertLess(r['t'],0)
        r=analyze('clinician_id,pre,post\na,1,2\nb,2,1')
        self.assertEqual(r['p'],1)
    def test_seed_and_bounds(self):
        self.assertEqual(simulate(),simulate())
        r=simulate(1,10,0,1)
        self.assertEqual(r['groups'][0]['overrides'],0)
        self.assertEqual(r['groups'][1]['overrides'],10)
        with self.assertRaises(ValueError): simulate(n=0)

if __name__ == '__main__': unittest.main()
