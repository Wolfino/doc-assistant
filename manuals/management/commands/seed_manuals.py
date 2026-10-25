from django.core.management.base import BaseCommand
from django.db import transaction

from manuals.models import Manual, Section

MANUALS = [
    {
        "title": "Stampante 3D Forma One - Guida rapida",
        "description": "Manuale d'uso della stampante 3D Forma One.",
        "sections": [
            ("Installazione", "Posiziona la stampante su una superficie piana e stabile, lontano da correnti d'aria. Collega l'alimentatore da 24 V e accendi l'interruttore sul retro. Al primo avvio la stampante esegue una calibrazione automatica del piano che dura circa 3 minuti."),
            ("Caricamento del filamento", "La Forma One supporta filamenti PLA e PETG da 1,75 mm. Riscalda l'ugello a 210 gradi per il PLA o 240 gradi per il PETG, poi inserisci il filamento nell'estrusore finché non esce dall'ugello. Non usare filamenti ABS: la stampante non ha una camera chiusa."),
            ("Prima stampa", "Carica il file G-code su una scheda microSD e inseriscila nello slot frontale. Dal menu seleziona Stampa e scegli il file. Per i pezzi di prova si consiglia un'altezza di strato di 0,2 mm."),
            ("Risoluzione dei problemi", "Se il pezzo non aderisce al piano, pulisci il piano con alcol isopropilico e ripeti la calibrazione. Se l'ugello si ostruisce, riscaldalo a 250 gradi ed esegui la procedura di pulizia dal menu Manutenzione. Il codice errore E04 indica un sensore di temperatura scollegato."),
        ],
    },
    {
        "title": "Router NetBox X2 - Manuale utente",
        "description": "Configurazione e uso del router Wi-Fi NetBox X2.",
        "sections": [
            ("Primo accesso", "Collega il PC al router con un cavo di rete o alla rete Wi-Fi NetBox-X2. Apri il browser all'indirizzo 192.168.50.1. Le credenziali predefinite sono admin / netbox2024 e vanno cambiate al primo accesso."),
            ("Configurazione Wi-Fi", "Il router trasmette su 2,4 GHz e 5 GHz. Dal menu Wireless puoi cambiare il nome della rete e la password. Si consiglia la protezione WPA3; per dispositivi più vecchi è disponibile la modalità mista WPA2/WPA3."),
            ("Rete ospiti", "La rete ospiti permette di dare accesso a Internet ai visitatori senza esporre i dispositivi della rete principale. Si attiva dal menu Wireless > Ospiti e può essere limitata a una durata da 1 a 24 ore."),
            ("Ripristino di fabbrica", "Per riportare il router alle impostazioni di fabbrica, tieni premuto il tasto Reset sul retro per 10 secondi finché le spie non lampeggiano. Tutte le configurazioni verranno cancellate."),
        ],
    },
    {
        "title": "TurniPro - Guida per gli amministratori",
        "description": "Gestione dei turni di lavoro con l'applicazione TurniPro.",
        "sections": [
            ("Creare un reparto", "Dal menu Impostazioni > Reparti clicca Nuovo reparto, inserisci il nome e il responsabile. Ogni dipendente può appartenere a un solo reparto alla volta."),
            ("Pianificare i turni", "Nella vista Calendario trascina un dipendente sulla fascia oraria desiderata. TurniPro segnala in rosso i turni che superano le 10 ore giornaliere o che non rispettano le 11 ore di riposo tra un turno e l'altro."),
            ("Richieste di ferie", "I dipendenti inviano le richieste di ferie dall'app mobile. L'amministratore riceve una notifica e può approvarle o rifiutarle dalla sezione Richieste. Le ferie approvate vengono bloccate automaticamente nel calendario."),
            ("Esportazione dei dati", "Dalla sezione Report puoi esportare le ore lavorate in formato CSV o Excel, filtrando per reparto e periodo. L'esportazione è disponibile solo per gli utenti con ruolo Amministratore."),
        ],
    },
]


class Command(BaseCommand):
    help = "Crea manuali di esempio con sezioni per lo sviluppo."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Cancella tutti i manuali esistenti prima di crearne di nuovi.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["reset"]:
            deleted, _ = Manual.objects.all().delete()
            self.stdout.write(f"Cancellati {deleted} oggetti esistenti.")

        for data in MANUALS:
            manual, created = Manual.objects.get_or_create(
                title=data["title"],
                defaults={"description": data["description"]},
            )
            if not created:
                self.stdout.write(f"Già presente, salto: {manual.title}")
                continue

            for order, (title, content) in enumerate(data["sections"], start=1):
                Section.objects.create(manual=manual, title=title, content=content, order=order)

            self.stdout.write(self.style.SUCCESS(f"Creato: {manual.title}"))