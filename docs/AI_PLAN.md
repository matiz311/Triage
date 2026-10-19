# AI: utilità, integrazione e decisioni da prendere

L'AI non è necessaria per ordinare per scadenza, controllare completezza, seguire stati e riattivazioni o applicare una matrice approvata. È utile per interpretare richieste ambigue, riassumere lunghe conversazioni, distinguere richieste da risposte, estrarre flussi tecnici e proporre domande pertinenti. Non risolve dati mancanti o SLA sconosciuti.

## Tre livelli proposti

| Livello | Strumenti | Vantaggio / limite |
|---|---|---|
| Base presente | Regole Python | Ripetibile e offline; comprensione semantica limitata |
| Retrieval futuro | Ricerca full-text, poi embeddings se misurati utili | Recupera ticket e runbook; richiede corpus e controllo accessi |
| Assistente futuro | LLM dietro provider adapter | Sintesi, classificazione e bozze; costo, errori e valutazione da governare |

Scelta da concordare: modello locale (infrastruttura e prestazioni da dimensionare) oppure API esterna (provider, regione, retention e budget da definire prima dell'invio). Non sono stati attivati provider né trasmessi ticket all'esterno. Nessun prezzo o modello specifico viene presunto attuale.

## Contratto del futuro provider

`analyze(redacted_ticket, permitted_evidence) -> {summary, classification_candidates, missing_information, suggested_next_action, evidence_refs, uncertainty, model_version}`.

Validare output con schema rigido, enum di catalogo e riferimenti realmente presenti. Budget token, timeout, retry limitato, caching per hash contenuto+versione e circuit breaker. Fallimento provider → regole locali. La confidenza autodichiarata del modello non è una probabilità calibrata.

Testi e allegati sono dati non attendibili: istruzioni contenute in email non possono cambiare prompt, richiamare strumenti o approvare scritture. Il modello non riceve cookie, password o strumenti di amministrazione. Retrieval filtrato per cliente e permessi prima della selezione; riduzione dati con allowlist, poi redazione di contatti, segreti e indirizzi dove non necessari. Rilevamento segreti mediante sola regex non è sufficiente.

## Valutazione prima dell'attivazione

Costruire un set anonimizzato con incident/service request, negazioni, richieste pianificate, sicurezza, attese, SLA, ticket multi-tecnologia, firme lunghe e notifiche duplicate. Separare training/tuning e holdout per cliente e tempo. Confrontare baseline e AI con precision/recall per classe e costo per caso; misurare errori pericolosi e citazioni inventate. Prima shadow mode, poi proposte approvate da operatore. Non consentire all'AI di abbassare unilateralmente priorità o chiudere ticket.

## Decisioni aperte

API del portale ed export; ambiente di esecuzione e accesso rete; volumi e frequenza; cataloghi e policy; disponibilità knowledge base; AI locale o cloud; budget; quali suggerimenti potranno diventare azioni automatiche. Questi punti non impediscono lo sviluppo del core, ma bloccano la certificazione di un'integrazione operativa completa.
