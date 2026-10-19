# Ricognizione del portale — 19 ottobre 2026

## Fonte e perimetro

Fonte primaria: sessione autenticata del [portale](https://ticket.lantechlongwave.it/HDAPortal/), pagina dettaglio ticket selezionata dall'utente, scheda Ticket e scheda Storico. Rilevati contenuto della pagina e DOM tramite Browser. Nessuna modifica, invio, presa in carico o cambio stato effettuato. Nessuna API chiamata o autenticazione esportata. Il repository di destinazione era vuoto ed è pubblico: qui sono conservate solo osservazioni strutturali senza dettagli del cliente.

Questa ricognizione NON certifica di aver esaminato l'intero tenant: allegati, cataloghi completi, autorizzazioni, regole SLA, API, Security Incidents e transizioni non sono stati verificati. Titolo osservato: Helpdesk Advanced. Produttore/versione esatta non accertati.

## Superfici osservate

Navigazione: Ticket, Security Incidents, Problem, Change, Interventi, Siti e Utenti, Asset, LL_Contratti, Attività, Le tue attività.

Elenco ticket (presente nel contesto estratto, anche se non attivo): filtri date, stato, priorità, sito, ubicazione, tipo, categoria, servizio, assegnazione, gruppo owner, utente owner, nickname, tags. Colonne ID, creazione, sito, classificazione, tipo, priorità, stato, assegnazione, oggetto, prossima/ultima scadenza, monte ore, SLA, ID sito, agente. Paginazione e righe per pagina. Non assumere che una singola pagina rappresenti tutta la coda.

Scheda dettaglio: Ticket, Storico, Storico Email, Soluzioni parziali, Allegati, Altri Ticket Sito/Ubicazione, Altri Interventi/Change Sito, Attività, Oggetti Correlati. Contatori possono mostrare 99+ pur esponendo quantità superiori: non usare il badge come totale preciso.

Comandi osservati: Salva, Salva ed Esci, Cambia Tipo, Inoltra, Prendi in carico, SLA 1/2, Cambia stato, Report, Altri Comandi. Sono capacità esposte, non un contratto di API o una prova dei permessi effettivi.

## Dizionario del modello normalizzato

| Campo UI | Campo applicazione | Osservazione |
|---|---|---|
| ID | id | Identificatore stringa stabile, separare entity da classificazione |
| Data creazione | created_at | Data italiana e ora separate; timezone da esplicitare |
| Sito / Ubicazione / Utente | site_id / location_id / contact_id | Conservare ID e label separati |
| Tipo | classification / type_id | Tipo gerarchico; l'entity nella URL non determina Incident vs Service Request |
| Stato | status_id / status | Conservare raw ID e normalizzazione |
| Servizio / Categoria | service_id / category_id | Possono essere vuoti |
| Service AS400 / Contratto | support_service / contract_id | Arricchimento contrattuale, non inferire copertura |
| Codice SLA | sla_code | Non basta per calcolare calendario e scadenze |
| SLA 1 / SLA 2, prossima/ultima scadenza | sla_milestones | Semantica e pause da acquisire |
| Asset | asset_id | ID e descrizione separati |
| Impatto / Urgenza / Priorità | impact / urgency / priority | Matrice tenant non rilevata |
| Oggetto / Richiesta / Soluzione | subject / description / solution | Rich text in iframe, non semplice testo input |
| Tags | tags | Multivalore |
| Gruppo / Risorsa / Owner | assigned_group / assigned_to / owner | Ruoli distinti; possono apparire non coerenti tra storico e scheda |
| Riattivazione / Inizio previsto | reactivation_at / planned_start_at | Non confondere con SLA |
| Sorgente / RemoteID / Ticket Cliente | source / remote_id / customer_ticket | Correlazione e origine |
| Case fornitore / Seriali / Sostituto | vendor_case / serials / replacement | Dati di contesto manutenzione |
| Allegati privati | attachments.visibility | Separare visibilità e permessi |
| Attività fatturabili/validate/verificate | activity_accounting | Non usare come priorità tecnica |
| Evasione / Upgrade priorità / Attenzionato | resolved_at / priority_upgrade / watched | Da conservare senza deduzioni automatiche |

La scheda segnala 40 stati e 4 valori per priorità/impatto/urgenza; l'elenco indicava 3 priorità. Non è stato enumerato il catalogo. Un click sul campo Impatto non ha aperto una lista completa: nessun valore è stato selezionato. I conteggi non dimostrano un insieme universale.

Stati visibili nel filtro: Aperto, Assegnato a Gruppo, Evaso da Compilare, Sospeso in Attesa Fornitore, Sospeso in Attesa Commerciale, Risposta da Commerciale, Richiesta Chiusura da Cliente, Appuntamento Programmato, Intervento Iniziato, Sospeso in Attesa Riscontro Cliente, Azione Parziale, Assegnato, Accettazione cliente, Non accettato, Pre Apertura. Elenco parziale, non una macchina a stati completa.

## Storico verificato

Eventi distinti: creazione da email, modifica, cambio stato (con ID prima/dopo), cambio gruppo, inoltro a risorsa, cambio tipo, cambio sito/contatto, modifica asset, note/soluzione parziale, email spedita e bozza, allegati EML/PDF. Presenti notifiche automatiche ripetute con placeholder non risolti. Il timestamp “Ultimo aggiornamento” del pannello può riferirsi al refresh UI e NON prova attività umana sul ticket.

Serve Event: id, ticket_id, occurred_at, author_id, actor_kind (human/system/unknown), event_type, body, before/after, attachment_refs, visibility, source_version. Conservare deduplica per ID evento; hash come ripiego con provenance. Non eliminare eventi solo perché il testo coincide.

## Rischi di estrazione accertati

- Il contesto testuale include elementi nascosti, pulsanti di dialoghi non aperti e campi hidden: non interpretare presenza come stato attivo.
- Non salvare l'HTML completo: può contenere token e dati estranei al dettaglio.
- ID DOM del form generati: evitare selettori con ID completo; usare sezione e label, verificando unicità.
- Iframe Rich Text e più form conviventi: leggere soltanto richiesta/soluzione del ticket attivo.
- Le firme email e i disclaimer gonfiano il testo. Separare testo originale, pulito e metadati.
- SOC in Tipo non equivale necessariamente al gruppo che ha attualmente il ticket.

## Informazioni ancora da ottenere

1. Documentazione API/esportazione ufficiale, autenticazione service account e scope sola lettura.
2. Cataloghi ID/label di stati, gruppi, classificazioni, impatto/urgenza/priorità; regole di transizione.
3. Matrice di priorità, SLA 1/2, fuso, festività, orari lavorativi, pause ed eccezioni contrattuali.
4. Paginazione, delta sync, timestamp/versione record e limiti del servizio.
5. Visibilità note/allegati e separazione clienti; rappresentazione ticket padre/figlio e correlazioni.
6. Campione diversificato anonimizzato e decisioni di triage convalidate da operatori.

Non sono stati dedotti endpoint da nomi di script o dalla URL SPA. L'integrazione verrà implementata su contratto documentato, oppure con adapter DOM locale esplicito se non esiste API.
