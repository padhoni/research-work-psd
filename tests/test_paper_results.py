import hashlib
import json
import unittest
from pathlib import Path
from docx import Document
from analysis import analyze, simulate, DEMO
from publication.build import ROOT, suggested_sections

class PublicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.results=json.loads((ROOT/'publication/results.json').read_text())
    def test_results_match_application(self):
        a=analyze(DEMO)
        b=analyze((ROOT/'examples/documentation.csv').read_text())
        for key,actual in [('original_example',a),('large_example',b)]:
            for metric in ['n','pre','post','difference','reduction','t','p','ci','dz']:
                self.assertEqual(self.results[key][metric],actual[metric])
        self.assertEqual(self.results['cds'],simulate())
    def test_document_results_are_synchronized(self):
        proof=Document(ROOT/'Proof of Concept.docx')
        suggestions=Document(ROOT/'publication/Suggested_Results.docx')
        proof_text='\n'.join(p.text for p in proof.paragraphs)
        suggestion_text='\n'.join(p.text for p in suggestions.paragraphs)
        markdown=(ROOT/'publication/Suggested_Results.md').read_text()
        for heading,paragraph in suggested_sections(self.results):
            for text in [proof_text,suggestion_text,markdown]:
                self.assertIn(heading,text)
                self.assertIn(paragraph,text)
        self.assertEqual(len(proof.inline_shapes),3)
        self.assertEqual(len(suggestions.inline_shapes),3)
        self.assertEqual(len(proof.tables),1)
        self.assertEqual(len(proof.tables[0].rows),6)
    def test_data_hashes(self):
        for name,expected in self.results['data_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),expected)
    def test_publication_manifest(self):
        manifest=json.loads((ROOT/'publication/manifest.json').read_text())
        for name,expected in manifest['sha256'].items():
            with self.subTest(name=name):
                self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),expected)
    def test_original_backed_up(self):
        original=ROOT/'archive/pre_sync/Proof of Concept.docx'
        self.assertTrue(original.exists())
        self.assertNotEqual(original.read_bytes(),(ROOT/'Proof of Concept.docx').read_bytes())
    def test_no_screenshot_claims_in_canonical_results(self):
        text=(ROOT/'publication/Suggested_Results.md').read_text()
        for unsupported in ['72%', 'F1 = 0.71','54.9%', '461.3']:
            self.assertNotIn(unsupported,text)
