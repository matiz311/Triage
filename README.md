# Triage

Assistente locale per il triage del service desk, derivato dall'analisi del portale Helpdesk Advanced. Prima versione **advisory**, eseguibile senza AI e senza dipendenze Python esterne. Non è ancora un connettore al portale né un sistema pronto per produzione.

## Avvio (Python 3.12)

```sh
python -m triage.server
# Aprire http://127.0.0.1:8765
python -m triage examples/tickets.json
python -m unittest discover -s tests -v
```

La UI accetta una lista JSON normalizzata e presenta punteggio, coda operativa, motivazioni, campi mancanti, candidati di instradamento ed export JSON. Non conserva i ticket e non chiama servizi esterni. Il server ascolta soltanto su loopback; autenticazione, TLS, database e multiutenza non sono implementati.

## Cosa funziona

- Ordinamento deterministico e motivazioni versionate.
- Scadenze SLA esplicite, rischio entro 120 minuti di calendario, riattivazioni.
- Separazione ticket attivi, attese, follow-up e stati terminali provvisori.
- Controllo completezza, assenza assegnatario, inattività umana oltre 7 giorni.
- Candidati SOC/NOC per parole chiave, ambiguità esplicita; nessuna assegnazione automatica.
- Domande diagnostiche per pagamenti e segnalazioni di sicurezza.
- Validazione input, limite batch, test e workflow GitHub Actions.

**Le soglie e i gruppi sono ipotesi dimostrative**, non policy aziendali ricavate dal portale. Il punteggio indica ordine di revisione, non una nuova priorità contrattuale. Le keyword possono comparire in frasi negate: non provano un incidente né autorizzano escalation.

## Input

Vedere `examples/tickets.json`. Campi opzionali: `sla_due_at`, `reactivation_at`, `last_human_update_at`, in ISO 8601 con timezone. `last_human_update_at` deve essere fornito da un adapter che distingua attività umane da notifiche; il motore non estrae ancora lo storico. Campi assenti restano sconosciuti. Un codice SLA non viene convertito arbitrariamente in scadenza.

## Analisi e sviluppo

- [Rilevazione portale e dizionario dati](docs/PORTAL_DISCOVERY.md)
- [Architettura, backlog e criteri di accettazione](docs/ARCHITECTURE.md)
- [Incorporare AI e retrieval](docs/AI_PLAN.md)

Il repository contiene soltanto codice, metadati strutturali e casi sintetici. Non inserirvi esportazioni clienti, indirizzi di gestione, credenziali, cookie o dump HTML.
