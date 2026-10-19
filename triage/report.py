"""Deterministic technical report. Only curated templates and explicit evidence."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).with_name('playbooks')
PLAYBOOKS = {p.stem: json.loads(p.read_text()) for p in sorted(ROOT.glob('*.json'))}
GENERIC = dict(id='generic', version='1.0', title='Analisi iniziale',
               fields={'impact':'Quale impatto operativo?', 'expected':'Quale comportamento atteso?',
                       'test_case':'Passi riproducibili, ambiente/versione, orario ed errore esatto?'},
               checks=[], acceptance='Definire ed eseguire un test di accettazione con il referente.', sources=[])


def clean(value, limit=240):
    """Plain-text, one-line display; preserve structured full data elsewhere."""
    value = ' '.join(str(value or '').split())
    return value if len(value) <= limit else value[:limit-1] + '…'


def evidence_record(value, label):
    if not isinstance(value, dict):
        raise ValueError(f'{label}: atteso oggetto con value, source, kind')
    if set(value) - {'value', 'source', 'kind'}:
        raise ValueError(f'{label}: chiavi non supportate')
    for key in ('value', 'source'):
        if not isinstance(value.get(key), str) or not value[key].strip():
            raise ValueError(f'{label}.{key}: stringa obbligatoria')
        if len(value[key]) > 2000:
            raise ValueError(f'{label}.{key}: massimo 2000 caratteri')
    if value.get('kind') not in ('reported', 'verified'):
        raise ValueError(f'{label}.kind: reported oppure verified')


def validate_technical(ticket):
    data = ticket.get('technical', {})
    if not isinstance(data, dict):
        raise ValueError('technical: atteso oggetto')
    if set(data) - {'playbook_id', 'facts', 'checks', 'evidence'}:
        raise ValueError('technical: chiavi non supportate')
    selected = data.get('playbook_id', 'generic')
    if not isinstance(selected, str) or selected not in {'generic', *PLAYBOOKS}:
        raise ValueError('playbook_id sconosciuto')
    book = PLAYBOOKS.get(selected, GENERIC)
    facts, checks, evidence = data.get('facts', {}), data.get('checks', {}), data.get('evidence', [])
    if not isinstance(facts, dict) or not isinstance(checks, dict) or not isinstance(evidence, list):
        raise ValueError('facts/checks devono essere oggetti; evidence una lista')
    allowed_facts = {'problem', 'impact', 'expected', 'classification', *book['fields']}
    if set(facts) - allowed_facts:
        raise ValueError('Campo tecnico non previsto dalla procedura')
    for key, value in facts.items():
        evidence_record(value, 'facts.' + key)
    if len(evidence) > 20:
        raise ValueError('Massimo 20 evidenze')
    for value in evidence:
        evidence_record(value, 'evidence')
    definitions = {c['id']: c for c in book['checks']}
    if set(checks) - set(definitions):
        raise ValueError('Controllo non previsto dalla procedura')
    for key, value in checks.items():
        if not isinstance(value, dict) or set(value) - {'status', 'evidence'}:
            raise ValueError(f'checks.{key}: formato non valido')
        status = value.get('status')
        if status not in ('pass', 'fail', 'unknown', 'not_applicable'):
            raise ValueError(f'checks.{key}: esito non valido')
        proof = value.get('evidence')
        if proof is not None:
            evidence_record(proof, 'checks.' + key + '.evidence')
        if status != 'unknown' and (not proof or proof['kind'] != 'verified'):
            raise ValueError(f'checks.{key}: esito richiede prova o motivazione verificata')
        if key in ('application_test', 'regression') and status == 'not_applicable':
            raise ValueError(f'checks.{key}: test di accettazione non escludibile')
    return data, book


def candidates(ticket):
    # Keywords suggest a procedure, never prove a problem or auto-select a diagnosis.
    text = (ticket.get('subject') or '') + '\n' + (ticket.get('description') or '')
    return [{'id': b['id'], 'title': b['title'], 'matches': sorted(set(
                m.group(0).lower() for p in b['patterns'] for m in re.finditer(p, text, re.I)))}
            for b in PLAYBOOKS.values() if any(re.search(p, text, re.I) for p in b['patterns'])]


def build_report(ticket):
    data, book = validate_technical(ticket)
    facts, checks = data.get('facts', {}), data.get('checks', {})
    evidence = data.get('evidence', [])
    questions = [{'field': k, 'question': v} for k, v in book['fields'].items() if k not in facts]
    verified, failed, pending, excluded = [], [], [], []
    actions, findings = [], []
    for definition in book['checks']:
        key = definition['id']
        check = checks.get(key, {'status':'unknown'})
        status = check['status']
        item = {'id':key, 'label':definition['label'], 'status':status}
        if check.get('evidence'):
            item['evidence'] = check['evidence']
        if status == 'unknown':
            item['question'] = definition['question']
            pending.append(item)
        elif status == 'fail':
            failed.append(item)
            findings.append({'rule_id': book['id'] + '.' + key + '.fail',
                             'finding': definition['label'] + ': esito negativo documentato',
                             'evidence': check['evidence']})
            actions.append(definition['on_fail'])
        elif status == 'pass':
            verified.append(item)
        else:
            excluded.append(item)
    if questions:
        phase = 'Informazioni da acquisire'  # never implies a message was sent
    elif failed:
        phase = 'Anomalia rilevata'
    elif pending or not book['checks']:
        phase = 'Verifiche da eseguire'
    else:
        phase = 'Verifiche completate — revisione operatore'
    def fact(key, fallback):
        value = facts.get(key)
        if value is None:
            return fallback
        return clean(value['value']) + ' [' + ('verificato' if value['kind']=='verified' else 'dichiarato') + '; ' + clean(value['source'], 100) + ']'
    rows = [f"TRIAGE | {clean(ticket['id'],80)} | {book['title']}",
            f"Stato triage: {phase}",
            f"Stato ticket: {clean(ticket.get('status')) or 'non disponibile'} | Priorità portale: {clean(ticket.get('priority')) or 'non disponibile'}",
            'Problema: ' + fact('problem', clean(ticket.get('subject')) or 'da definire'),
            'Impatto: ' + fact('impact', 'da acquisire'),
            'Categoria: ' + fact('classification', 'da validare'), '', 'EVIDENZE']
    rows += ['- ' + clean(e['value']) + ' [' + ('verificato' if e['kind']=='verified' else 'dichiarato') + '; ' + clean(e['source'],100) + ']' for e in evidence]
    if not evidence:
        rows.append('- Nessuna evidenza tecnica allegata al report.')
    rows += ['', 'DIAGNOSI']
    rows += ['- ' + f['finding'] + ' [' + clean(f['evidence']['source'],100) + ']' for f in findings]
    if not findings:
        rows.append('- Causa non determinata; nessuna anomalia dedotta dalle sole parole chiave.')
    if verified:
        rows.append('- Controlli positivi: ' + '; '.join(c['label'] for c in verified) + '.')
    if excluded:
        rows.append('- Non applicabili (motivazione registrata): ' + '; '.join(c['label'] for c in excluded) + '.')
    rows += ['', 'DATI MANCANTI'] + ['- ' + q['question'] for q in questions]
    if not questions:
        rows.append('- Campi obbligatori della procedura compilati.')
    rows += ['', 'PROSSIME VERIFICHE'] + ['- ' + c['question'] for c in pending]
    if not pending:
        rows.append('- Revisione operatore dei risultati disponibili.')
    rows += ['', 'INTERVENTO PROPOSTO'] + ['- ' + a for a in actions]
    if not actions:
        rows.append('- Nessuna modifica individuata prima delle verifiche.')
    next_step = questions[0]['question'] if questions else (actions[0] if actions else (pending[0]['question'] if pending else 'Revisionare evidenze e risultato.'))
    rows += ['', 'Accettazione: ' + book['acceptance'],
             'Responsabile: ' + (clean(ticket.get('assigned_to')) or 'da assegnare'),
             'Prossimo passo: ' + next_step,
             'Limiti: risultati riferiti ai casi documentati; nessun cambio stato o invio al cliente eseguito.',
             f"Procedura: {book['id']} v{book['version']} | Nota interna"]
    return dict(phase=phase, playbook_id=book['id'], playbook_version=book['version'],
                procedure_candidates=candidates(ticket), facts=facts, evidence=evidence,
                findings=findings, missing_information=questions, pending_checks=pending,
                passed_checks=verified, failed_checks=failed, excluded_checks=excluded,
                proposed_actions=actions, next_step=next_step, acceptance=book['acceptance'],
                sources=book['sources'], note_text='\n'.join(rows),
                publication={'destination':'partial_solution', 'visible_to_account':False,
                             'copy_to_final_solution':False, 'status':'draft'})
