# Simulazione Attacchi nel CAN bus

Questo progetto è stato realizzato per la relazione "Il CAN Bus: funzionamento, vulnerabilità di
sicurezza e attacchi" a compimento del mio percorso di laurea triennale in Ingegneria Informatica presso l'Università
La Sapienza, sotto la supervisione del prof. Emilio Coppa.

Si tratta di una simulazione di un'automobile all'interno della quale è presente un CAN bus. Sono presenti varie ECUs
(implementate nella directory `ecus`) che gestiscono le principali funzionalità di un'automobile e comunicano tra loro.
Tutte interagiscono con l'auto e con l'ambiente esterno attraverso dei sensori (simulati dalla classe `Car`).

È possibile simulare il comportamento reale di un'auto in determintate condizioni, come quella di un impatto con un
ostacolo, l'accelerazione o l'attivazione/disattivazione dei sistemi di sicurezza tramite il telecomando.
In queste situazioni è necessaria una particolare efficienza nella comunicazione tra le ECUs attraverso il CAN bus.
<br> Per dimostrare quanto sia importante curare l'aspetto della sicurezza in un'automobile, vengono simulati tre tipi
di attacchi al CAN bus, che ne impediscono il normale funzionamento proprio nelle situazioni critiche descritte in
precedenza. Una ECU intrusa nel sistema (implementata in `ecus/attacker.py`) esegue degli attacchi di tipo Replay, DoS e Freeze Doom Loop.

Un'analisi più dettagliata della simulazione, insieme alla discussione sulle conseguenze degli attacchi effettuati,
è disponibile nella relazione.

### Come eseguire la simulazione
Si può scegliere quale attacco simulare passando l'argomento appropriato da linea di comando.

Per simulare l'attacco DoS:
`python3 main.py dos true|false`

Per simulare l'attacco Replay:
`python3 main.py replay true|false`

Per simulare l'attacco Freeze Doom Loop:
`python3 main.py fdm true|false`

L'ultimo argomento indica se stampare o meno l'output su file. Se non specificato o se impostato a `true` lo `stdout`
sarà un file diverso per ogni tipo di attacco, altrimenti sarà la console. 

<br>Alternativamente, è possibile eseguire la simulazione all'interno di un'immagine Docker, con i seguenti comandi.

Creare l'immagine con:<br>
`docker build --tag thesis-simulation .`

Eseguire l'immagine, specificando il tipo di attacco da eseguire da `false` per avere l'output su console:<br>
`docker run --rm thesis-simulation [tipo-attacco] false`
