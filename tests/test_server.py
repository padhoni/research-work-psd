import http.client
import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from server import Handler
from analysis import DEMO

class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True)
        cls.thread.start()
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()
    def request(self,path,body=None,headers=None):
        conn=http.client.HTTPConnection('127.0.0.1',self.server.server_port,timeout=5)
        conn.request('POST' if body is not None else 'GET',path,body=body,headers=headers or {})
        response=conn.getresponse()
        status,data=response.status,response.read()
        conn.close()
        return status,data
    def test_pages_and_missing_routes(self):
        for path in ['/','/paper','/app.js','/style.css','/api/demo']:
            with self.subTest(path=path): self.assertEqual(self.request(path)[0],200)
        self.assertEqual(self.request('/../analysis.py')[0],404)
    def test_valid_analysis(self):
        status,data=self.request('/api/analyze',json.dumps({'csv':DEMO}))
        self.assertEqual(status,200)
        self.assertAlmostEqual(json.loads(data)['pre'],5.11)
    def test_malformed_requests(self):
        for body in ['{','[]','null','{}',json.dumps({'csv':None}),json.dumps({'csv':'bad'})]:
            with self.subTest(body=body):
                status,data=self.request('/api/analyze',body)
                self.assertEqual(status,400)
                self.assertIn('error',json.loads(data))
    def test_simulation_rejects_fractional_and_nonfinite_values(self):
        for field,value in [('seed',1.5),('n',10.5),('seed',float('inf')),('n',True),('ai',101)]:
            payload={'seed':42,'n':100,'legacy':89,'ai':34,field:value}
            with self.subTest(payload=payload): self.assertEqual(self.request('/api/simulate',json.dumps(payload))[0],400)
    def test_simulation_reproducible(self):
        body=json.dumps({'seed':'42','n':'10000','legacy':'89','ai':'34'})
        first=self.request('/api/simulate',body)
        self.assertEqual(first[0],200)
        self.assertEqual(first,self.request('/api/simulate',body))
    def test_cross_origin_rejected(self):
        self.assertEqual(self.request('/api/analyze',json.dumps({'csv':DEMO}),{'Origin':'https://example.com'})[0],403)
    def test_body_limit(self):
        # Oversize bodies are rejected from their headers before uploading bytes.
        self.assertEqual(self.request('/api/analyze','',{'Content-Length':'2000001'})[0],400)
    def test_extreme_values_give_validation_response(self):
        status,data=self.request('/api/analyze',json.dumps({'csv':'clinician_id,pre,post\na,1e308,1\nb,1e307,2'}))
        self.assertEqual(status,400)
        self.assertIn('numeric range',json.loads(data)['error'])
