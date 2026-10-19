# Architettura e percorso verso produzione

## Decisione iniziale

Core Python indipendente dal portale, input JSON normalizzato, regole motivate e UI locale. Tutte le decisioni sono proposte: nessuna chiamata di modifica al sistema sorgente. Nessun requisito aziendale è inventato a partire da un singolo caso.

## Obiettivo completo (non ancora implementato)

Adapter ufficiale read-only → validazione e normalizzazione → PostgreSQL (ticket/eventi/versioni) → coda lavori → motore regole + procedure curate → API e dashboard. Un componente di scrittura separato applicherà soltanto proposte approvate. Frontend con code per azione, attesa, follow-up, assegnazione mancante, rischio SLA; filtri, ricerca, vista cronologica e spiegazioni con collegamento all'evidenza.

Per il deployment proporre FastAPI, PostgreSQL, worker e Docker Compose, reverse proxy TLS e SSO. Sono scelte proposte, non dipendenze già adottate. Per piccoli volumi basta un worker con job idempotenti su database; valutare un orchestratore durevole soltanto per workflow lunghi, retry e timer effettivamente necessari.

## Backlog ordinato

| Fase | Attività | Accettazione |
|---|---|---|
| 0 (presente) | JSON, regole, procedure tecniche, nota schematica, demo UI, test | Funzionamento offline con casi sintetici |
| 1 | Contratto API, cataloghi, mapping e sync delta | Confronto campo per campo; pagine complete; retry/backoff; nessuna scrittura |
| 2 | Policy configurabili e SLA con calendari | Casi reali convalidati; festività, weekend, DST, sospensioni e riaperture |
| 3 | Timeline, deduplica notifiche, arricchimento asset/contratti | Provenance di ogni dato; attività umana distinta da eventi sistema |
| 4 | Dashboard operativa e persistenza | SSO, ruoli, separazione tenant, audit append-only, backup/ripristino |
| 5 | Ricerca full-text e procedure tecniche | Precisione misurata; filtro cliente/permessi prima della ricerca |
| 6 | Moduli guidati e parser deterministici | Estrazione verificabile; casi sconosciuti demandati all’operatore |
| 7 | Approvazione e write-back | Confronto versione record, idempotency key, anteprima diff, audit e rollback quando disponibile |

## Normalizzazione e scheduling

Conservare ID sorgente, entity, versione, rilevato_at, raw label e campo normalizzato. Separare created_at, modified_at, last_human_update_at e observed_at. Tutti gli istanti timezone-aware; rendering Europe/Rome. Nessuna conversione 8x5 → ore solari. Lo SLA autorevole del portale ha precedenza sulle stime; mostrare stime come tali. Stato in attesa non implica automaticamente timer fermo.

Non confondere un disservizio con una richiesta pianificata solo perché cita pagamenti o firewall. Priorità ufficiale e punteggio operativo devono rimanere separati. Mapping gruppi e competenze richiede validazione, turni, reperibilità e capacità: una keyword non sceglie una persona.

## Qualità e sicurezza operative

Test: contratti adapter, fixture anonimizzate, paginazione/delta, dati mancanti, cambi catalogo, DST, pause SLA, concorrenza, retry, testo non attendibile e provenienza delle evidenze. Metriche: precisione instradamento, recall casi urgenti, falsi allarmi, tempo risparmiato, override operatori, costo/latency per ticket. Registrare versione regole e procedure per ogni proposta; nessun body cliente nei log applicativi.

La demo non implementa persistenza, parser HTML/EML/PDF, deduplica, autenticazione, calcolo SLA lavorativo o adapter live. Non esporre il server demo su Internet. Allegati futuri: limite dimensione, sandbox, niente macro/esecuzione; ACL applicata prima di estrarre contenuti.

## Vincolo di progetto

Sviluppo senza AI: vedere [NO_AI_DESIGN.md](NO_AI_DESIGN.md). Stato triage e stato del ticket restano indipendenti. La nota segue [TRIAGE_FORMAT.md](TRIAGE_FORMAT.md).
