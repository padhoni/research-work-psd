import json
import unittest
from analysis import analyze, simulate

class RegressionTests(unittest.TestCase):
    def test_tiny_nonconstant_differences(self):
        r=analyze('clinician_id,pre,post\na,2e-16,1e-16\nb,4e-16,1e-16')
        self.assertAlmostEqual(r['t'],2.0)

    def test_extreme_numbers_rejected_clearly(self):
        with self.assertRaisesRegex(ValueError, 'numeric range'):
            analyze('clinician_id,pre,post\na,1e308,1\nb,1e307,2')

    def test_p_underflow_is_not_reported_as_exact_zero(self):
        r=analyze('clinician_id,pre,post\n'+'\n'.join(f'{i},{100+i%2*.001},1' for i in range(1000)))
        self.assertEqual(r['p'],0)
        self.assertNotIn('p = 0;',r['report'])
        self.assertIn('below numerical precision',r['report'])

    def test_fractional_seed_and_count_rejected(self):
        for kwargs in [{'seed':1.5},{'n':10.5},{'seed':True}]:
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError): simulate(**kwargs)

    def test_bom_quoted_ids_and_observed_provenance(self):
        r=analyze('\ufeffclinician_id,pre,post\n"C,1",5,4\nC2,7,3',source='observed')
        self.assertEqual(r['rows'][0]['clinician_id'],'C,1')
        self.assertIn('User-supplied observational',r['report'])
        json.dumps(r,allow_nan=False)

    def test_row_limit(self):
        with self.assertRaisesRegex(ValueError,'10,000'):
            analyze('clinician_id,pre,post\n'+'\n'.join(f'{i},2,1' for i in range(10001)))

    def test_workload_boundaries(self):
        r=analyze('clinician_id,pre,post\na,0,100\nb,100,0','workload')
        self.assertEqual(r['p'],1)
