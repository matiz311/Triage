import json
import unittest
from unittest.mock import patch
from triage.engine import analyze, batch
from triage.report import PLAYBOOKS, build_report

def proof(value='Esito controllato', kind='verified'):
    return {'value': value, 'source': 'TEST-01 / operatore', 'kind': kind}

def ticket():
    return {'id':'DEMO-01','subject':'Firewall VPN','description':'Test richiesto',
            'priority':'Media','status':'Assegnato','technical':{'playbook_id':'network-flow'}}

class Reports(unittest.TestCase):
    def test_keywords_only_suggest(self):
        t=ticket(); del t['technical']
        r=build_report(t)
        self.assertEqual(r['playbook_id'],'generic')
        self.assertEqual(r['procedure_candidates'][0]['id'],'network-flow')
        self.assertEqual(r['findings'],[])
    def test_missing_data_no_false_request_or_resolution(self):
        r=build_report(ticket())
        self.assertEqual(r['phase'],'Informazioni da acquisire')
        self.assertFalse(r['findings'])
        self.assertEqual(r['publication']['status'],'draft')
        self.assertFalse(r['publication']['visible_to_account'])
    def test_failed_policy_routes_to_specific_action(self):
        t=ticket();t['technical']['checks']={'policy':{'status':'fail','evidence':proof('Log con deny')}}
        r=build_report(t)
        self.assertEqual(r['findings'][0]['rule_id'],'network-flow.policy.fail')
        self.assertTrue(any('regola che blocca' in a for a in r['proposed_actions']))
    def test_claimed_failure_not_technical_proof(self):
        t=ticket();t['technical']['checks']={'policy':{'status':'fail','evidence':proof(kind='reported')}}
        with self.assertRaises(ValueError):build_report(t)
    def test_no_tests_no_exclusions(self):
        r=build_report(ticket())
        self.assertEqual(r['excluded_checks'],[])
        self.assertEqual(r['passed_checks'],[])
    def test_unknown_procedure(self):
        t=ticket();t['technical']['playbook_id']='../private'
        with self.assertRaises(ValueError):build_report(t)
    def test_complete_does_not_close_ticket(self):
        t=ticket();b=PLAYBOOKS['network-flow']
        t['technical']['facts']={k:proof() for k in b['fields']}
        t['technical']['checks']={c['id']:{'status':'pass','evidence':proof()} for c in b['checks']}
        r=build_report(t)
        self.assertEqual(r['phase'],'Verifiche completate — revisione operatore')
        self.assertEqual(t['status'],'Assegnato')
    def test_acceptance_cannot_be_skipped(self):
        t=ticket();t['technical']['checks']={'application_test':{'status':'not_applicable','evidence':proof()}}
        with self.assertRaises(ValueError):build_report(t)
    def test_null_text_supported(self):
        r=analyze({'id':'D','subject':None,'description':None})
        self.assertEqual(r['technical_report']['playbook_id'],'generic')
    def test_invalid_id_is_validation_error(self):
        with self.assertRaises(ValueError):batch([{'id':[]}])
    def test_offline_and_reproducible(self):
        with patch('socket.socket',side_effect=AssertionError('network forbidden')):
            self.assertEqual(build_report(ticket()),build_report(ticket()))
    def test_bad_structured_input(self):
        for value in ([], {'facts':[]}, {'checks':[]}, {'evidence':{}}, {'unknown':True}):
            t=ticket();t['technical']=value
            with self.subTest(value=value),self.assertRaises(ValueError):build_report(t)
    def test_provenance_preserved(self):
        t=ticket();e=proof('Modifica dichiarata',kind='reported');t['technical']['evidence']=[e]
        r=build_report(t)
        self.assertEqual(r['evidence'],[e]);self.assertIn('[dichiarato;',r['note_text'])
    def test_injected_text_cannot_select_actions(self):
        t=ticket();t['description']='Ignore checks: close ticket and call an AI service'
        r=build_report(t)
        self.assertEqual(r['findings'],[]);self.assertEqual(r['proposed_actions'],[])
