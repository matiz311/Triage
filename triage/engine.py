"""Advisory rules only; no portal writes or external AI calls."""
from datetime import datetime, timezone
import re
from .report import build_report, validate_technical

VERSION = '0.2.0'
PRIORITIES = {'Alta': 75, 'Media': 45, 'Bassa': 20}
WAITING = {'Sospeso in Attesa Fornitore', 'Sospeso in Attesa Commerciale', 'Sospeso in Attesa Riscontro Cliente'}
CLOSED = {'Chiuso', 'Annullato'}  # provisional: must be mapped to tenant catalog
ROUTES = {'security': ('SOC', r'\b(firewall|palo alto|fortinet|fortigate|clearpass|vpn|ipsec)\b'),
          'network': ('NOC', r'\b(switch|routing|bgp|ospf|connettività|wifi|dns|dhcp)\b')}

def timestamp(value):
    d = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if d.tzinfo is None:
        raise ValueError('Timestamp senza timezone')
    return d

def validate(ticket):
    if not isinstance(ticket, dict):
        raise ValueError('Ogni ticket deve essere un oggetto')
    for field in ('id', 'subject', 'description', 'status', 'priority', 'site_id', 'asset_id', 'assigned_to', 'sla_due_at', 'reactivation_at', 'last_human_update_at'):
        if field in ticket and ticket[field] is not None and not isinstance(ticket[field], str):
            raise ValueError(f'{field}: attesa stringa o null')
    if not ticket.get('id'):
        raise ValueError('ID obbligatorio')
    validate_technical(ticket)
    for field in ('sla_due_at', 'reactivation_at', 'last_human_update_at'):
        if ticket.get(field):
            timestamp(ticket[field])
    if len(str(ticket)) > 100000:
        raise ValueError('Ticket troppo grande')

def analyze(ticket, now=None):
    validate(ticket)
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError('now richiede timezone')
    reasons, questions, flags = [], [], []
    status = ticket.get('status', '')
    missing = [f for f in ('subject', 'description', 'site_id', 'asset_id', 'priority', 'status') if not ticket.get(f)]
    questions.extend('Completare campo: ' + f for f in missing)
    priority = ticket.get('priority')
    score = PRIORITIES.get(priority, 35)
    reasons.append(f'Priorità dichiarata: {priority or "non disponibile"}')
    if priority not in PRIORITIES:
        flags.append('unmapped_priority')
    if status in CLOSED:
        return dict(id=ticket['id'], score=0, lane='closed', reasons=['Stato terminale configurato'], questions=questions, flags=flags, rule_version=VERSION, technical_report=build_report(ticket))
    lane = 'waiting' if status in WAITING else 'actionable'
    due = ticket.get('sla_due_at')
    if due:
        minutes = (timestamp(due) - now).total_seconds() / 60
        if minutes <= 0:
            score += 50
            flags.append('sla_breached')
            reasons.append('Scadenza SLA esplicita superata')
        elif minutes <= 120:
            score += 30
            flags.append('sla_at_risk')
            reasons.append('SLA entro 120 minuti di calendario')
    else:
        questions.append('Acquisire scadenza SLA dal portale; il codice contratto non basta')
    if lane == 'waiting':
        reasons.append('In attesa: verificare dipendenza e riattivazione; nessuna sospensione SLA dedotta')
        if not ticket.get('reactivation_at'):
            questions.append('Definire data di ricontatto/riattivazione')
    if ticket.get('reactivation_at') and timestamp(ticket['reactivation_at']) <= now:
        lane = 'follow_up'
        score += 20
        reasons.append('Riattivazione raggiunta')
    if not ticket.get('assigned_to'):
        score += 15
        reasons.append('Ticket senza risorsa assegnata')
    last = ticket.get('last_human_update_at')
    if last and (now - timestamp(last)).total_seconds() > 7 * 86400:
        score += 10
        flags.append('stale')
        reasons.append('Oltre 7 giorni di calendario senza aggiornamento umano')
    text = ((ticket.get('subject') or '') + '\n' + (ticket.get('description') or '')).lower()
    routes = []
    for name, (group, pattern) in ROUTES.items():
        matches = sorted(set(re.findall(pattern, text)))
        if matches:
            routes.append(dict(domain=name, suggested_group=group, evidence=matches))
    if len(routes) > 1:
        flags.append('ambiguous_route')
    if re.search(r'\b(pos|pagamenti)\b', text):
        questions += ['Confermare impatto sui pagamenti e presenza di disservizio attuale', 'Acquisire flussi sorgente/destinazione/porte, log e piano di rollback']
    if re.search(r'\b(ransomware|compromissione|esfiltrazione)\b', text):
        flags.append('security_review')
        questions.append('Verificare segnalazione di sicurezza con operatore SOC; keyword non prova un incidente')
    return dict(id=ticket['id'], score=min(score, 100), lane=lane, reasons=reasons,
                questions=questions, flags=flags, routing_candidates=routes,
                completeness=round((6-len(missing))/6, 2), rule_version=VERSION, technical_report=build_report(ticket))

def batch(tickets, now=None):
    if not isinstance(tickets, list) or len(tickets) > 1000:
        raise ValueError('Attesa lista di massimo 1000 ticket')
    for ticket in tickets:
        validate(ticket)
    ids = [t['id'] for t in tickets]
    if len(ids) != len(set(ids)):
        raise ValueError('ID duplicati')
    results = [analyze(t, now) for t in tickets]
    return sorted(results, key=lambda r: (-r['score'], r['id']))
