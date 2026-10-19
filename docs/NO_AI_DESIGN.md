# Progettazione senza AI

## Vincolo

Il prodotto usa regole deterministiche, procedure curate e dati strutturati. Nessun LLM, embedding, modello locale, API AI o chiave provider. Il motore opera offline. A parità di input, versioni delle regole e istante di valutazione restituisce lo stesso risultato.

## Implementato

- `engine.py`: ordinamento operativo e controlli di completezza.
- `report.py`: validazione delle evidenze, selezione esplicita della procedura, domande mancanti, risultati e nota schematica.
- `playbooks/*.json`: campi, controlli, interventi per esito negativo e criteri di accettazione versionati.
- Procedura generica e procedura `network-flow`: applicazione configurazione, ingresso, policy, NAT, ritorno, selettori VPN se pertinenti, test applicativo e regressione.
- UI e CLI: anteprima ed esportazione della bozza interna. Nessuna scrittura automatica nel portale.

Le keyword suggeriscono soltanto procedure candidate. Non confermano categoria, guasto, causa o urgenza. L'operatore sceglie la procedura e compila i dati nel JSON; un modulo guidato è ancora da realizzare.

## Contratto delle evidenze

Ogni fatto ha `value`, `source`, `kind` (`reported` oppure `verified`). Un controllo ha `status` (`pass`, `fail`, `unknown`, `not_applicable`) e un'evidenza. Gli esiti diversi da `unknown` richiedono `kind=verified`; la non applicabilità richiede una motivazione. Test applicativo e regressione non sono escludibili.

La validazione controlla struttura e coerenza, non autentica la fonte: `verified` è una dichiarazione dell'operatore o dell'adapter. In produzione serviranno riferimenti a log, orari, identificativi e revisore. Un controllo negativo attiva un intervento predefinito e identificabile tramite `rule_id`; non prova da solo la causa radice.

## Limiti intenzionali

Il motore non comprende liberamente conversazioni ambigue, non legge allegati, non interroga firewall e non esegue verifiche tecniche reali. Se mancano dati produce domande; se il caso non è coperto usa la procedura generica e richiede revisione. Non simula comprensione semantica tramite keyword.

## Sviluppi successivi

1. Moduli guidati per famiglia tecnica, cataloghi validati e scelta della procedura.
2. Adapter ufficiale del portale e normalizzazione con provenienza dei campi.
3. Parser deterministici per IP, porte, codici errore e formati log conosciuti, sempre con contesto originale e conferma.
4. Nuove procedure curate e ricerca full-text tradizionale nella knowledge base con filtri di autorizzazione.
5. Scrittura idempotente della sola nota approvata in Soluzioni parziali: `Visibile all'Account=No`, `Copia in soluzione finale=No`, verifica rilettura e audit.

Il contenuto dei ticket è un dato: non può introdurre regole, selezionare comandi eseguibili o autorizzare pubblicazioni.
