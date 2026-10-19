import copy
from pathlib import Path
import sqlite3
import tempfile
import unittest
from semantic_plan.__main__ import example
from semantic_plan.engine import compile_plan,execute,query_results
from semantic_plan.provider import FakeProvider
class CompilerTests(unittest.TestCase):
    def setUp(self):self.data=example();self.tmp=tempfile.TemporaryDirectory();self.db=str(Path(self.tmp.name)/'cache.sqlite')
    def tearDown(self):self.tmp.cleanup()
    def run_plan(self,provider=None,**kwargs):return execute(self.data['plan'],self.data['rows'],provider or FakeProvider(),cache_path=self.db,**kwargs)
    def test_cse_projection_batching_and_exact_arithmetic(self):
        provider=FakeProvider();r=self.run_plan(provider);self.assertEqual(r['provider_calls'],4);self.assertEqual(r['questions_sent'],6);self.assertEqual(r['status'],'completed');self.assertEqual(r['rows']['row-1']['amount_due']['value'],3000)
        self.assertTrue(all('unused_private_note' not in str(b) for b in provider.requests));self.assertEqual(len(provider.requests[0]['questions']),2);self.assertEqual(r['rows']['row-1']['topic']['cache_key'],r['rows']['row-1']['topic_copy']['cache_key'])
    def test_warm_run_needs_zero_calls_even_with_zero_budget(self):
        self.run_plan();provider=FakeProvider();r=self.run_plan(provider,max_calls=0,max_questions=0);self.assertEqual(r['provider_calls'],0);self.assertEqual(r['status'],'completed');self.assertEqual(len(provider.requests),0);self.assertEqual(r['persistent_cache_hits'],15)
    def test_unused_column_change_does_not_invalidate_projected_cache(self):
        self.run_plan();self.data['rows'][0]['unused_private_note']='changed';self.assertEqual(self.run_plan()['provider_calls'],0)
    def test_single_row_change_only_calls_new_contexts(self):
        self.run_plan();self.data['rows'][0]['message']='Please correct invoice number two.';r=self.run_plan();self.assertEqual(r['provider_calls'],2);self.assertEqual(r['questions_sent'],3)
    def test_policy_and_model_contract_changes_invalidate_cache(self):
        self.run_plan();self.data['plan']['policy_version']='demo-2';self.assertEqual(self.run_plan()['provider_calls'],4)
        self.data['plan']['model']='unversioned'
        with self.assertRaises(ValueError):self.run_plan()
    def test_synthetic_and_real_namespaces_never_share_cache(self):
        self.run_plan();provider=FakeProvider();provider.synthetic=False;provider.cache_namespace='test-real-separate';self.assertEqual(self.run_plan(provider)['provider_calls'],4)
    def test_whole_batch_change_invalidates_cached_sibling_questions(self):
        self.run_plan();self.data['plan']['nodes'][3]['instructions']+=' Explicit revised rubric.';r=self.run_plan();self.assertEqual(r['provider_calls'],2);self.assertEqual(r['questions_sent'],4)
    def test_low_confidence_routes_to_review_and_blocks_dependents(self):
        r=self.run_plan(FakeProvider(.6));self.assertEqual(r['status'],'needs_review');self.assertEqual(r['rows']['row-1']['topic']['status'],'review');self.assertEqual(r['rows']['row-1']['route']['status'],'blocked_review')
    def test_budget_does_not_make_silent_decisions_or_exceed_attempts(self):
        r=self.run_plan(max_calls=1,max_questions=2);self.assertEqual(r['provider_calls'],1);self.assertEqual(r['questions_sent'],2);self.assertEqual(r['status'],'needs_review');self.assertTrue(any(v['status']=='budget_exhausted' for row in r['rows'].values() for v in row.values()))
    def test_cycles_missing_dependencies_and_unknown_fields_rejected(self):
        for change in ('cycle','missing','field'):
            p=copy.deepcopy(self.data['plan'])
            if change=='cycle':p['nodes'][1]['depends']=['route']
            elif change=='missing':p['nodes'][1]['depends']=['absent']
            else:p['max_cost_dollars']=1
            with self.assertRaises(ValueError):compile_plan(p)
    def test_invalid_provider_response_is_not_cached_and_usage_is_unknown(self):
        class Bad(FakeProvider):
            def __call__(self,body):return {'model':'wrong','answers':{}}
        r=self.run_plan(Bad());self.assertEqual(r['status'],'needs_review');self.assertFalse(r['usage_complete']);self.assertEqual(sqlite3.connect(self.db).execute('SELECT COUNT(*) FROM cache').fetchone()[0],0)
    def test_corrupt_cache_is_not_reused(self):
        self.run_plan();db=sqlite3.connect(self.db);db.execute("UPDATE cache SET answer='{}'");db.commit();db.close();self.assertEqual(self.run_plan()['provider_calls'],4)
    def test_sql_materialization_and_read_only_query(self):
        r=self.run_plan();result=query_results(self.db,"SELECT row_id,choice FROM decisions WHERE node_id='route' AND status='decided' ORDER BY row_id");self.assertEqual(len(result),3);self.assertEqual(result[1]['choice'],'priority')
        with self.assertRaises(sqlite3.DatabaseError):query_results(self.db,'DELETE FROM cache')
        with self.assertRaises(sqlite3.DatabaseError):query_results(self.db,'SELECT randomblob(1000000000)')
    def test_exact_subtraction_does_not_round_large_integers(self):
        self.data['rows'][0]['invoice_cents']=2**60+1;self.assertEqual(self.run_plan()['rows']['row-1']['amount_due']['value'],2**60+1-2000)
    def test_declared_conditions_skip_nonbilling_route(self):self.assertEqual(self.run_plan()['rows']['row-4']['route']['status'],'skipped')
    def test_context_budget_stops_calls(self):self.assertEqual(self.run_plan(max_context_chars=100)['provider_calls'],0)
    def test_unoptimized_executor_makes_fifteen_actual_fixture_calls(self):
        provider=FakeProvider();naive=self.run_plan(provider,optimize=False);optimized=self.run_plan();self.assertEqual(naive['provider_calls'],15);self.assertEqual(len(provider.requests),15);self.assertEqual(naive['questions_sent'],15)
        for row,nodes in naive['rows'].items():
            for node,result in nodes.items():
                for field in ('status','choice','value'):self.assertEqual(result.get(field),optimized['rows'][row][node].get(field))
if __name__=='__main__':unittest.main()
