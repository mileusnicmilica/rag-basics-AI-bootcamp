# Plan rada — domaći zadatak, 6. nedelja (RAG)

**Status:** plan potvrđen; tehnička implementacija je završena, a Milica je 12. oktobra 2026. potvrdila završni pregled za sebe i Nemanju.

**Polazni materijal:** `Week 6 RAG Homework Starter (1).pdf`, `README.md`, sav kod u `src/`, svi postojeći testovi u `tests/`, `scripts/run_tests.sh` i `docs/homework-checklist.md`.

## 1. Cilj i granice zadatka

Uraditi pet obaveznih ishoda iz PDF-a: (1) uporediti uticaj dva podešavanja segmentacije na pretragu, (2) pokazati ispravno rangiranu `top-k` pretragu, (3) vratiti odgovor sa proverljivim citatima, (4) odbiti pitanje koje korpus ne podržava i (5) priložiti ponovljive dokaze za podržan i nepodržan slučaj. Završni paket prati `docs/homework-checklist.md`. Predloženo poboljšanje leksičkog rangiranja pokriva i opciono proširenje iz odeljka H, uz najmanje tri relevantna testa.

Uputstva iz PDF-a tretiraju se kao zahtevi domaćeg zadatka. Podela posla, obostrani pregled, vođenje evidencije i obavezno čekanje potvrde ovog plana potiču iz korisničkog zahteva. Plan ne beleži budući ili nepotvrđeni rad kao već obavljen.

## 2. Nalaz početnog pregleda

| Deo | Trenutno stanje | Šta proveriti/uraditi |
| --- | --- | --- |
| `src/corpus.py` | Dva mala, statička profila (`default`, `training-rag`) sa naslovom i ID-jem dokumenta. | Zadržati proverljivo poreklo svakog segmenta; izabrati pitanja koja korpus stvarno podržava. |
| `src/chunking.py` | Seče normalizovan tekst po broju karaktera; preklop je ispravno ograničen, ali rez može prekinuti reč i tvrdnju. | Uporediti dve konfiguracije na istom pitanju; po potrebi poboljšati granice bez gubitka izvornog teksta i ID-ja. |
| `src/retrieval.py` | Broji pojave bilo kog tokena pitanja u segmentu i deli dužinom segmenta; sortira opadajuće i vraća najviše `k`. | Smanjiti lažno pozitivne rezultate zbog čestih reči, proveriti deterministički redosled i prikazati ocenu svakog rezultata. |
| `src/rag.py` | Prazan rezultat se odbija; svaki pronađeni segment iznad niskog praga postaje deo odgovora. | Uvesti konzervativnu proveru relevantnosti pre odgovora i razlikovati tekst odgovora od liste referenci. |
| `src/cli.py` | Prima pitanje, profil, veličinu segmenta, preklop i `top-k`; ispisuje odgovor i ID-jeve citata, ali ne ispisuje pronađene segmente ni ocene. | Ispisati čitljiv trag pretrage potreban za dokaz; koristiti iste rezultate za odgovor i prikaz. |
| `tests/` | Devet početnih testova proverava osnovne putanje, ali ne traženi primer nepodržanog pitanja ni potpun trag citata. | Dodati usmerene testove za uočene rizike i CLI/evidence ponašanje. |
| Okruženje | Zatečeni `.venv` je napravljen na macOS-u; na ovom Windows računaru `python -m pytest -q` ne radi jer `pytest` nije instaliran. | Posle potvrde plana pripremiti lokalno Windows okruženje i zabeležiti tačnu komandu i rezultat testova. |

**Potvrđen početni propust:** `python -m src.cli --question "Who won the world cup in 1958?"` trenutno vraća `Refused: False` i citira nepovezane RAG segmente. To mora postati odbijanje u završnom dokazu. Drugi početni problem je da podrazumevana segmentacija može prekinuti rečenicu usred reči.

## 3. Predložena podela i pravilo obostranog pregleda

„Nosilac“ je osoba odgovorna za razumevanje, odluku i proveru koraka. AI pomoć pri pisanju koda ili dokumentacije upisuje se u stvarnu evidenciju; sama oznaka nosioca nije dokaz da je osoba ručno napisala izmenu. Obe osobe čitaju **ceo** `src/`, postojeće i nove testove, `evidence.md`, izlaze CLI-ja i kontrolnu listu pre završne predaje. Nijedan pregled ili doprinos neće biti označen kao obavljen bez stvarne potvrde osobe.

| Korak | Predloženi nosilac | Obavezni pregled druge osobe | Rezultat |
| --- | --- | --- | --- |
| 0. Okruženje, početni testovi, pregled korpusa i ograničenja | Milica | Nemanja proverava komande, korpus i zapis početnog stanja | Ponovljive komande i početni nalaz |
| 1. Segmentacija i eksperiment sa dve konfiguracije | Milica | Nemanja pregleda kod, iste upite, rangiranje i tumačenje razlike | Testovi i Outcome 1 u `evidence.md` |
| 2. Leksičko rangiranje i `top-k` | Nemanja | Milica pregleda formulu, pragove, poredak i izlaze za `k=2` i `k=3` | Kod, testovi i Outcome 2 |
| 3. Utemeljen odgovor, citati i odbijanje | Nemanja | Milica proverava svaku tvrdnju prema tekstu citiranog segmenta i slučajeve odbijanja | Kod, testovi i Outcomes 3–4 |
| 4. CLI trag pretrage i ponovljivi primeri | Milica | Nemanja izvršava iste komande i proverava prikazane ID-jeve, ocene i tekst | CLI i Outcome 5 |
| 5. Završna dokumentacija, testovi i predaja | Zajedno | Svako samostalno pregleda sve fajlove, pokreće testove i upisuje svoj nalaz | `evidence.md`, izveštaj o doprinosu, ček-lista |

**Demo lead:** Milica, prema njenoj potvrdi tokom rada. Ako stvarna podela rada odstupi od predloga, evidentirati stvarni doprinos i razlog. `docs/pair-report.md` beleži prijavljene doprinose, AI pomoć i zasebne završne provere; potvrde ljudi ostaju prazne dok ih sami ne daju.

## 4. Redosled rada i kriterijumi prihvatanja

### Korak 0 — uspostavljanje ponovljivog polaznog stanja

1. Pripremiti Windows Python okruženje odvojeno od zatečenog macOS `.venv` i instalirati tačno ono što je navedeno u `requirements.txt`; dokumentovati Windows i, gde je korisno, Unix komande u `README.md`.
2. Pokrenuti devet postojećih testova i zabeležiti rezultat. Pokrenuti podržano i nepodržano pitanje iz `README.md`; početni propust ostaje zabeležen kao motivacija, ne kao završni dokaz.
3. Proveriti da svi primeri koriste isti izabrani profil korpusa ili jasno navesti promenu profila. Ne dodavati izmišljene izvore, odgovore ni ljudske doprinose.

**Gotovo kada:** čisto okruženje pokreće testove i CLI sa proizvoljnim pitanjem; početni nalaz i komande su zapisani.

### Korak 1 — segmentacija i uticaj na pretragu

1. Pregledati da li su granice karaktera prihvatljive za čitljiv i dokaziv segment; sačuvati stabilne ID-jeve i vezu sa dokumentom.
2. Pokrenuti najmanje konfiguracije A `chunk_size=140, overlap=30` i B sa bitno drugačijom veličinom/preklopom za **isto** pitanje i isti profil korpusa.
3. U `evidence.md` upisati obe komande, sve relevantne ID-jeve, ocene i tekst pronađenih segmenata, pa kratko objasniti konkretnu promenu kvaliteta (npr. da li je potrebna tvrdnja potpuna ili presečena). Ako prva dva podešavanja ne daju poučnu razliku, izabrati drugo B i navesti zašto.
4. Dodati test za svojstvo segmentacije koje je zaista važno za taj nalaz.

**Gotovo kada:** razlika je zasnovana na vidljivim rezultatima istog upita, a ne na pretpostavci o kvalitetu.

### Korak 2 — `top-k` i rangiranje

1. Popraviti leksičko ocenjivanje tako da samo česte reči ili slučajni kratak pogodak ne izgledaju kao podrška; definisati formulu, filtriranje i prag u dokumentaciji. Ponašanje na praznom upitu, nevažećem `k`, izjednačenim ocenama i upitu bez informativnih poklapanja mora biti određeno.
2. Proveriti da rezultat sadrži najviše `k` segmenata, sortiranih opadajuće po oceni, sa stabilnim redosledom pri jednakim ocenama.
3. Za isto pitanje prikazati `top_k=2` i `top_k=3` sa ID-jevima, ocenama i tekstom; obrazložiti poredak na osnovu stvarnih poklapanja.
4. Pošto je bolje leksičko rangiranje i opciono proširenje, dodati najmanje tri smislena testa za njega (npr. ignorisanje čestih reči, poredak relevantnih segmenata, stabilnost/ograničenje `k`).

**Gotovo kada:** testovi i primeri potvrđuju poredak, a način računanja ocene je objašnjen u `evidence.md`.

### Korak 3 — odgovori, citati i odbijanje

1. Koristiti iste rezultate pretrage za proveru podrške, odgovor i CLI trag, kako bi citati u odgovoru odgovarali prikazanim segmentima.
2. Za podržano pitanje vratiti sažet odgovor ograničen na tvrdnje koje su prisutne u citiranim segmentima; u izlazu odvojiti telo odgovora od `References`/citata sa ID-jevima segmenata.
3. Za nepodržano pitanje vratiti doslednu poruku odbijanja bez izmišljene tvrdnje i bez lažnih citata. Obavezni regresioni primer je pitanje o Svetskom prvenstvu 1958; dodati i test za mešanje opštih RAG reči sa nepodržanom činjenicom ako je potrebno da se pokaže ograničenje pravila.
4. U `evidence.md` kratko objasniti zašto pronađeni segmenti ne podržavaju odgovor. Leksička heuristika nije garancija semantičke istinitosti; proveriti sve završne primere ručno prema korpusu.

**Gotovo kada:** podržan odgovor ima samo citate prisutne u prikazu pretrage, a nepodržan primer pouzdano odbija odgovor.

### Korak 4 — CLI i dokazi

1. CLI treba jasno da pokaže pitanje, profil, parametre segmentacije i `top-k`, listu pronađenih segmenata sa ocenom/tekstom, zatim odgovor, status odbijanja i reference.
2. Napraviti `evidence.md` po redosledu i nazivima pet odeljaka iz PDF-a: *Chunking impact*, *Top-k retrieval*, *Citation quality*, *Refusal behavior*, *Final evidence pair*. Uključiti doslovne komande i stvarne izlaze ili dovoljno precizne izvatke da se mogu ponoviti.
3. U završnom paru dati jedan podržan i jedan nepodržan upit sa pitanjem, pronađenim segmentima (ili jasnim praznim skupom), odgovorom/statusom i citatima kada postoje.
4. Zabeležiti snimak izlaza testova i verziju okruženja. Ne predstavljati početni CLI izlaz kao završni rezultat.

**Gotovo kada:** druga osoba može ponoviti oba slučaja iz navedenih komandi i dobiti iste logičke rezultate.

### Korak 5 — zajednički pregled i zaključavanje kontrolne liste

1. Pokrenuti sve testove, `top_k=2`, `top_k=3`, obe konfiguracije segmentacije, podržano i nepodržano pitanje. Pregledati `README.md`, sve iz `src/`, sve testove i svaki primer iz `evidence.md`.
2. U `docs/homework-checklist.md` označiti `[x]` **tek** pošto postoji odgovarajući kod, test, komanda ili dokaz. Ostaviti `[ ]` za sve što još nije završeno ili ljudski potvrđeno; opcione stavke označiti samo ako su zaista urađene.
3. U `docs/pair-report.md` upisati stvarni doprinos i demo lead. Milica i Nemanja zasebno potvrđuju da su pregledali ceo projekat; bez tih potvrda stavke G i povezane stavke predaje ostaju otvorene.

**Gotovo kada:** svaka označena stavka ima proverljiv trag, a izveštaj razlikuje planirane zadatke, stvarne doprinose i završni pregled obe osobe.

## 5. Veza sa kontrolnom listom

| Odeljak liste | Planirani dokaz |
| --- | --- |
| A — Baseline setup | Korak 0: instalacija, testovi, CLI primer i pregled koda. |
| B — Chunking | Korak 1: dve konfiguracije, isti upit, razlika u rezultatima i objašnjenje. |
| C — Top-k | Korak 2: sortirani rezultati, primeri za `k=2/3`, objašnjenje ocene. |
| D — Citations | Korak 3: telo odgovora i reference; provereni ID-jevi u CLI tragu. |
| E — Refusal | Korak 3: jasna poruka odbijanja i objašnjenje nedovoljne evidencije. |
| F — Evidence | Korak 4: potpuni podržan i nepodržan primer sa komandama. |
| G — Pair accountability | Korak 5: stvarni doprinosi, dva odvojena pregleda, dogovoren demo lead. |
| H — Optional extension | Korak 2: bolje leksičko ocenjivanje i najmanje tri testa za njega. |
| I — Submission bundle | Koraci 4–5: `evidence.md`, CLI komande i izlaz testova. |

**Stanje pri pisanju plana:** pregled fajlova i PDF-a bio je obavljen, ali nijedna stavka postojeće kontrolne liste tada nije imala sav traženi dokaz. Kasnije oznake u listi prate stvarno završene korake.
