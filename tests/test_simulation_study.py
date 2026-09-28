import unittest
import numpy as np
from scipy import stats
from analysis import analyze
from simulation_study import run_study

class SimulationStudyTests(unittest.TestCase):
    def test_reproducible_design_and_ranges(self):
        a=run_study(repetitions=100)
        self.assertEqual(a,run_study(repetitions=100))
        self.assertEqual(a['scenario_count'],24)
        self.assertEqual({s['true_difference'] for s in a['scenarios']},{-.5,0,.5,.95})
        for s in a['scenarios']:
            self.assertTrue(0<=s['coverage']<=1)
            self.assertTrue(0<=s['rejection_rate']<=1)
            self.assertGreaterEqual(s['coverage_mcse'],0)
            self.assertEqual(s['rejection_interpretation'],'Type I error' if s['true_difference']==0 else 'Power')
    def test_difference_test_matches_app(self):
        d=np.array([1.1,-.5,.25,.8,1.3])
        csv='clinician_id,pre,post\n'+'\n'.join(f'C{i},10,{10-x}' for i,x in enumerate(d))
        app=analyze(csv);test=stats.ttest_1samp(d,0)
        self.assertAlmostEqual(app['t'],test.statistic)
        self.assertAlmostEqual(app['p'],test.pvalue)
        self.assertAlmostEqual(app['ci'][0],test.confidence_interval().low)
    def test_invalid_repetition_count(self):
        for value in [0,1,True,2.5]:
            with self.assertRaises(ValueError):run_study(repetitions=value)
