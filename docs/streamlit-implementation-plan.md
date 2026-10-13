# Plan implementacije: Streamlit interfejs za lokalni RAG

**Status:** odobreno i implementirano 13. oktobra 2026.

## Cilj

Omogućiti postavljanje pitanja kroz lokalnu stranicu u browseru. Aplikacija treba da prikaže odgovor ili odbijanje, citat i segmente na kojima je rezultat zasnovan, koristeći postojeću logiku iz `src/`. Pokretanje aplikacije i dalje zahteva jednu komandu u terminalu; za svako naredno pitanje terminal nije potreban.

## Opseg i ponašanje

- Jedna Streamlit stranica sa poljem za pitanje (`st.chat_input`) i prikazom pitanja i odgovora (`st.chat_message`). Svako pitanje se obrađuje nezavisno; istorija služi samo za prikaz i ne šalje se kao dodatni kontekst RAG funkciji.
- Bočna traka za izbor profila korpusa (`default` ili `training-rag`) i podešavanje `chunk_size` (140), `overlap` (30) i `top_k` (2). Podrazumevane vrednosti su iste kao u CLI-ju.
- Za svaki upit prikazati odgovor, status odbijanja, citirane ID-jeve i listu pronađenih segmenata sa redosledom, ocenom, naslovom, ID-jem i punim tekstom. Ako pretraga ne vrati segmente, prikazati jasnu poruku. Detalji pretrage mogu biti u proširivom delu ispod odgovora.
- Sačuvati istoriju tokom otvorene browser sesije pomoću `st.session_state`. Uz svaki odgovor sačuvati podešavanja koja su važila za to pitanje, tako da promena kontrola ne promeni značenje već prikazanih rezultata. Obezbediti dugme za brisanje istorije.
- Prazno pitanje se ne obrađuje. Podešavanja moraju poštovati postojeća pravila: `chunk_size > 0`, `0 <= overlap < chunk_size`, `top_k > 0`. Nevažeće vrednosti se zaustavljaju uz čitljivu poruku u interfejsu.
- Interfejs treba jasno da kaže da projekat trenutno radi nad malim ugrađenim engleskim korpusom i da koristi leksičku pretragu i izdvajanje rečenice, bez LLM-a.

## Koraci implementacije

1. **Zavisnost i ulazna tačka.** Dodati proverenu verziju `streamlit` u `requirements.txt` i novi korenski fajl `app.py`. Aplikaciju pokretati iz korena repozitorijuma komandnom linijom `python -m streamlit run app.py`. Ne menjati CLI način rada.
2. **Povezivanje sa RAG tokom.** U `app.py` direktno pozvati `load_corpus(profile)`, `build_chunks(documents, chunk_size, overlap)` i `build_grounded_answer(question, chunks, top_k)`. Ne pozivati CLI kao podproces i ne duplicirati rangiranje ili pravila odbijanja.
3. **Interfejs i stanje.** Napraviti kontrole, prikaz rezultata i istoriju opisanu gore. Za svaki poslati upit sačuvati pitanje, izabrana podešavanja i `RagAnswer`; podaci ne moraju trajati posle zatvaranja sesije.
4. **Uputstvo.** Dopuniti `README.md` instalacijom i komandom za Streamlit, lokalnom adresom koju ispisuje Streamlit i kratkim opisom kontrola. Navesti da se ugrađeni korpus i dalje menja u `src/corpus.py`.
5. **Provera.** Pokrenuti postojeći `pytest` skup. Dodati integracione testove interfejsa pomoću Streamlit `AppTest`: podržano pitanje uz promenjen profil prikazuje odgovor i odgovarajući citirani segment; nepodržano pitanje prikazuje odbijanje bez citata; nevažeći preklop sprečava unos; istorija čuva izvorna podešavanja i može da se obriše. Pokrenuti lokalni server i proveriti njegov odgovor.

## Kriterijumi prihvatanja

- Posle jednokratnog pokretanja Streamlit-a, pitanja se postavljaju u browseru bez ponovnog kucanja CLI komandi.
- Odgovor i lista pronađenih segmenata potiču iz istog poziva postojeće RAG logike; svaki prikazani citat odgovara prikazanom segmentu.
- Podržano pitanje `Why are citations important in RAG?` uz profil `training-rag` daje citirani odgovor; nepodržano pitanje `Who won the world cup in 1958?` uz `default` daje odbijanje bez citata.
- Postojeći CLI i svi raniji testovi nastavljaju da rade. Novi testovi i ručna provera prolaze.
- Implementacija ne uvodi LLM, vektorsku bazu, upload dokumenata, prijavljivanje korisnika ni javni hosting.

## Provera implementacije

Korisnik je odobrio implementaciju. Dodati su `app.py`, zavisnost Streamlit, uputstvo u `README.md` i četiri testa u `tests/test_app.py`. Test komanda `.\.venv-win\Scripts\python.exe -m pytest -q` završena je sa `25 passed`. Lokalni Streamlit server pokrenut je na `http://localhost:8501`; zdravstvena provera `/_stcore/health` vratila je HTTP 200. Interakcije na stranici proverene su pomoću Streamlit `AppTest` simulacije.

## Relevantna Streamlit dokumentacija

- [Elementi za razgovor](https://docs.streamlit.io/develop/api-reference/chat)
- [Session State](https://docs.streamlit.io/develop/concepts/architecture/session-state)
- [AppTest](https://docs.streamlit.io/develop/concepts/app-testing/get-started)
