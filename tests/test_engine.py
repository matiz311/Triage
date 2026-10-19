import unittest
from datetime import datetime, timezone
from triage.engine import analyze, batch
NOW = datetime(2026, 10, 19, 10, tzinfo=timezone.utc)
def ticket(**kw):
    return dict(id='D1', subject='VPN', description='Verifica', priority='Media', status='Assegnato', **kw)
class EngineTests(unittest.TestCase):
    def test_sla_breach(self):
        self.assertIn('sla_breached', analyze(ticket(sla_due_at='2026-10-19T09:00:00Z'), NOW)['flags'])
    def test_unknown_sla_not_inferred(self):
        self.assertTrue(any('scadenza SLA' in q for q in analyze(ticket(sla_code='8X5XNBD'), NOW)['questions']))
    def test_waiting_still_breaches(self):
        t=ticket(sla_due_at='2026-10-19T09:00:00Z');t['status']='Sospeso in Attesa Fornitore'
        r=analyze(t,NOW);self.assertEqual(r['lane'],'waiting');self.assertIn('sla_breached',r['flags'])
    def test_duplicate_id(self):
        with self.assertRaises(ValueError): batch([ticket(),ticket()],NOW)
    def test_invalid_date(self):
        with self.assertRaises(ValueError): analyze(ticket(sla_due_at='2026-10-19'),NOW)
    def test_route_ambiguity(self):
        t=ticket();t['description']='VPN e DNS';self.assertIn('ambiguous_route',analyze(t,NOW)['flags'])
    def test_reactivation(self):
        self.assertEqual(analyze(ticket(reactivation_at='2026-10-18T10:00:00Z'),NOW)['lane'],'follow_up')
    def test_missing_not_invented(self):
        r=analyze({'id':'x'},NOW);self.assertEqual(r['completeness'],0)
    def test_closed(self):
        t=ticket();t['status']='Chiuso';self.assertEqual(analyze(t,NOW)['score'],0)
    def test_bad_type(self):
        with self.assertRaises(ValueError): analyze(ticket(sla_due_at=42),NOW)
