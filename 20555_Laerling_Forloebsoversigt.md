# 20555 – Big Data begreber, teknikker og processer
## Forløbsoversigt for lærlinge

**Revision 1.5 · 22. september 2026**

> **Status:** ARBEJDSDOKUMENT  
> **Afprøvning:** Planlagt til første gennemførelse; tid og støtte afprøves med holdet  
> **Niveau:** Rutineret  
> **Målgruppe:** H4, datatekniker med speciale i programmering

## Indhold

1. [Forløbet i overblik](#1-forløbet-i-overblik)
2. [Modul01](#2-modul01)
3. [Modul02](#3-modul02)
4. [Modul03](#4-modul03)
5. [Modul04](#5-modul04)
6. [Modul05](#6-modul05)
7. [Hvis du bliver bagud](#7-hvis-du-bliver-bagud)
8. [Materialer og links](#8-materialer-og-links)

---

# 1. Forløbet i overblik

Du arbejder gennem forløbet på **én sammenhængende datapipeline med danske Energinet-data**. Casen hedder **Kan vi stole på live-eldata?**

Operationelle data kan bruges hurtigt, men deres definitioner og kvalitet kan afvige fra senere afregningsdata. Du undersøger forskellene og gør behandlingen gennemsigtig, så andre kan vurdere, hvad resultaterne kan bruges til.

```text
datakilde → rå snapshot → validering → transformation
→ sammenkobling → kvalitetsflag → analyseklart output → faglig forklaring
```

| Modul | Placering i forløbet | Fokus | Resultat at arbejde hen imod |
|---|---|---|---|
| Modul01 | Første del | Kilder, dataformer, formater og spørgsmål | Kildeskema og plan for dataflowet |
| Modul02 | Efter kildeundersøgelsen | Ingestion, kontrakt, enheder og tid | Kontrollerede realtime-data på timeniveau |
| Modul03 | Efter første transformation | Sammenlignelighed, join og datakvalitet | Analyseklart output med synlige kvalitetsproblemer |
| Modul04 | Før afslutningen | Undersøgelser, platform og ansvar | Begrundede svar og dokumenterede valg |
| Modul05 | Afslutningen; fredag i denne gennemførelse | Færdiggørelse, aflevering og fremlæggelse | Genkørbar løsning og individuel faglig forklaring |

Modulerne viser den faglige rækkefølge. Det konkrete skema og antallet af lektioner meddeles særskilt. Et modul kan fordeles over flere undervisningspas.

Du bruger Python og pandas til databehandling, JSON som rådata, CSV til analyseklart output, JSON til kvalitetsrapport og Git til versionsstyring. Du arbejder med faste snapshots og behøver ikke API-adgang. Et muligt fremtidigt API indgår som arkitekturperspektiv.

Denne forløbsoversigt er din indgang til hele fagets progression. Når du arbejder i hovedcasen, ejer starterprojektets `OPGAVE.md` rækkefølgen, kravene og checkpoints; `pipeline.py` ejer de konkrete kode-TODO'er, når starterprojektets `OPGAVE.md` sender dig dertil.

### Det bygger vi videre på

Du bruger din erfaring med programmering, databaser, fejlfinding og test fra uddannelsen. Der forudsættes ikke et omfattende kendskab til Python eller pandas. Du får en målrettet introduktion til den syntaks og de arbejdsformer, forløbet kræver.

På dette hold har alle netop gennemført 20556. Derfor genaktiverer vi blandt andet grain, raw og afledte data, joins, pipeline og genkørsel gennem korte opgaver. Begreberne forklares også her og bruges med et nyt fokus: datakilders betydning, behandling og kvalitet. Tidligere gennemførelse af 20556 er ikke en generel forudsætning for faget; uden den erfaring skal introduktion og øvetid tilpasses.

### Sådan arbejder vi

På almindelige undervisningsdage bruges de første op til tre lektioner til faglige oplæg, korte demonstrationer og **miniopgaver på separate eksempeldata**. Du forudsiger resultater, afprøver kode, finder fejl og forklarer dine valg. Derefter overfører du principperne til Energinet-casen.

Miniopgaverne giver ikke en færdig løsning på hovedcasen. Primærnøgler, tidsregler, join keys og centrale outputfelter er givet i casekontrakten. Du verificerer dem mod metadata, implementerer og kontrollerer selv transformationerne og begrunder deres betydning. Du vælger undersøgelsesspørgsmål, analysescope og supplerende kontroller inden for opgaven. Fredag bruges primært til afslutning, aflevering og fremlæggelse.

Hvert modul har et checkpoint. Når du har nået det, arbejder du med faglig fordybelse. Hvis du mangler et tidligere led, bruger du støttevejen under det relevante modul.

### Faglige ressourcer er støtte – ikke nye krav

Start med modulets undervisning, miniopgaver og caseopgave. Brug dataordlisten, metadata og biblioteksdokumentation til opslag og genlæsning. Ressourcerne tilføjer ikke ekstra afleveringer.

---

# 2. Modul01

**Placering:** Forløbets begyndelse

## Hvad arbejder vi med?

Du undersøger, hvad kilderne beskriver, før du beslutter, hvordan de skal behandles. Den fælles undervisning har fire læringsblokke:

1. **Fra kilde til anvendelige data:** Operationelle og analytiske behov, raw og afledte data samt Big Data-karakteristika. Vi skelner mellem et undervisningsudsnit og det løbende system bag det.
2. **Dataformer og filformater:** Vi sammenligner tabulære data, JSON og ustruktureret indhold, herunder tekst, billede, lyd og video. Du undersøger forskellen på format, schema og indhold.
3. **Python/pandas til kendte opgaver:** På små separate data læser, filtrerer og grupperer du data og sammenholder arbejdet med kendte databaseoperationer.
4. **Kildens betydning:** Du finder grain, identifikatorer/keys, enheder og metadata i et separat eksempel og forklarer, hvilke oplysninger der mangler for at kunne bruge data sikkert.

I hovedcasen følger du derefter starterens `README.md` til setup og fortsætter efter `SETUP PASS` i Modul01 i `OPGAVE.md`. Du undersøger realtime- og afregningssnapshots, vælger foreløbigt tre undersøgelsesspørgsmål, tegner din planlagte pipeline og begynder kildebeskrivelsen. `kilder_og_pipeline.md` i docs-mappen er frivillig støtte til dokumentationen. TODO 1–3 implementeres først i Modul02.

## Modulets checkpoint

Du kan vise et fungerende setup, et kildeskema og en pipelineskitse. Du kan forklare:

- hvad én række betyder i hver kilde;
- hvilke primærnøgler, join keys, tidskolonner og enheder du skal være opmærksom på;
- hvorfor felter med lignende navne ikke nødvendigvis betyder det samme;
- hvilke spørgsmål du vil undersøge, og hvilke data de kræver.

Det konkrete checkpoint ejes af Modul01-afsnittet i starterprojektets `OPGAVE.md`.

## Hvis du har mere tid

Sammenlign, hvordan samme lille eksempel repræsenteres i JSON og CSV. Forklar, hvilke typer eller strukturer der kræver særlig håndtering ved konvertering. Undersøg alternativt en metadataadvarsel og dens mulige betydning for et af dine spørgsmål.

## Hvis du var syg / arbejder videre hjemme

```text
Sensorlabs README.md: kopi og Python/pandas-setup → Modul01-noter og miniopgaver
→ starterprojektets README.md og check_setup.py → OPGAVE.md, Modul01
→ DATAORDLISTE.md og kildemetadata efter behov
→ kildeskema og pipelineskitse → checkpoint
```

Hvis pandas er nyt, begynd med læsning, kolonnevalg, filtrering og en lille gruppering på eksempeldata, før du arbejder med de større snapshots.

## Ressourcer ved behov

- `README.md` i Sensorlab under Faelles: kopi, Python/pandas-setup og første demo.
- `README.md` i starterprojektet: efter miniopgaverne, opsætning og startkontrol af Energinet.
- `DATAORDLISTE.md`: begreber, felter og enheder i casen.
- De medfølgende metadata: kildeformål, definitioner og advarsler. Læs især felterne, som dine spørgsmål afhænger af.

---

# 3. Modul02

**Placering:** Efter kildeundersøgelsen

## Hvad arbejder vi med?

Du bygger det første kontrollerede behandlingstrin. Et program, der kan køre, er ikke i sig selv bevis for, at enheder og tid er behandlet korrekt. Den fælles undervisning har fire læringsblokke:

1. **Transport og ingestion:** Vi følger data fra afsender til modtager og sammenligner fil/snapshot, request/response og eventbaseret transport. API-kald, polling og adgang forklares med et separat eksempel uden krav om ekstern adgang.
2. **Datakontrakt og fejlstop:** Du afprøver manglende felter, forkerte typer og dubletter på den forventede key/identifikator i små eksempeldata og vælger, hvornår behandlingen skal stoppe.
3. **Enheder og tid:** Du undersøger på separate målinger forskellen på en hastighed og en samlet mængde, tidsintervaller, UTC og lokaltid samt ufuldstændige grupper.
4. **Pipeline og versionsspor:** Vi beskriver trin og dependencies, skelner mellem deklarativ beskrivelse og udførende kode og bruger Git til at følge ændringer. Genkørsel trænes fra begyndelsen.

I Energinet-casen implementerer du derefter `TODO 1–3` i `pipeline.py`: validering, MW→MWh og timeaggregation. Indlæsningen er leveret i starteren. Før TODO 3 slår du Storebælt og strukturelle null-værdier op i `DATAORDLISTE.md` og metadata; de er relevante allerede for realtime-afledningerne. Omregningen følger casens eksplicitte metodeantagelse, ikke en officiel afregningsberegning.

Start med sommertidsperioden og brug derefter januar. Følg Modul02-kørslen med `--stage realtime` i starterens `README.md` og `OPGAVE.md`: den gemmer mellemoutput uden at kræve TODO 4–6.

## Modulets checkpoint

Du kan vise en realtime-tabel med én række pr. UTC-time og prisområde og forklare:

- hvordan en kontraktfejl bliver synlig;
- hvorfor omregningen kræver et tidsinterval;
- hvordan du opdager ufuldstændige timer;
- hvordan din kontrol håndterer sommertid;
- hvordan du kan gentage behandlingen fra samme rådata.

Det konkrete checkpoint ejes af Modul02-afsnittet i starterprojektets `OPGAVE.md`.

## Hvis du har mere tid

Afprøv et ekstra fejlscenarie i en kopi af eksempeldata. Undersøg, hvordan en ændring af måleinterval eller schema påvirker kontrakten og beregningen. Bevar casens rå snapshots uændrede.

## Hvis du var syg / arbejder videre hjemme

```text
genfind Modul01-checkpoint → Modul02-miniopgaver om kontrakt, enhed og tid
→ starterprojektets OPGAVE.md, Modul02 → pipeline.py, TODO 1–3
→ realtime-checkpoint med --stage realtime: lille periode → januar → checkpoint
```

Kontrollér først inputkolonner og datatyper, derefter én omregning, og til sidst én samlet time. Brug fejlmeddelelsen til at finde det første fejlende trin.

## Ressourcer ved behov

- starterprojektets `OPGAVE.md`: behandlingsrækkefølge og checkpoint.
- `pipeline.py`: nummererede TODO'er i starterprojektet.
- `contracts.py`: de kolonner og navne, starterprojektet stiller til rådighed.
- `DATAORDLISTE.md` og metadata: enheder, tidsantagelse, Storebælt og strukturelle null-værdier. Brug pandas-dokumentationen til den konkrete syntaks, du mangler.

---

# 4. Modul03

**Placering:** Efter realtime-behandlingen

## Hvad arbejder vi med?

Du gør de to kilder sammenlignelige og bevarer spor af deres kvalitetsproblemer. Den fælles undervisning har tre læringsblokke:

1. **Betydning før sammenkobling:** På et separat eksempel undersøger du, om to opgørelser bruger samme enhed, tidsgrundlag og definition. Du begrunder, hvad der kan sammenlignes.
2. **Join og kvalitetsflag:** Du afprøver manglende matches og dubletter i små tabeller. Du undersøger rækkeantal før/efter join og markerer problemer frem for at skjule dem.
3. **Sikkerhed og databeskyttelse:** Vi følger et separat dataflow og vurderer adgang, transport og personoplysninger. En kort kontrastopgave viser, hvorfor fjernelse af et navn ikke automatisk gør data anonyme.

I Energinet-casen implementerer du derefter `TODO 4–6`, danner sammenlignelige afregningsfelter og sammenkobler kilderne. Du bygger videre på realtime-afledningerne fra Modul02 og kontrollerer Storebælt-logik, kvalitetsflag og output for januar, juni og sommertidsperioden.

## Modulets checkpoint

Du kan vise analyseklart output og en kvalitetsrapport og forklare:

- hvorfor din join key og den forventede kardinalitet passer til det valgte grain;
- hvilke rækker der ikke matcher eller har ufuldstændige intervaller;
- hvad de valgte kvalitetsflag betyder for anvendelsen;
- hvorfor Storebælt skal behandles efter den konkrete opgørelses definition.

Det konkrete checkpoint ejes af Modul03-afsnittet i starterprojektets `OPGAVE.md`. Sikkerheds- og persondataøvelsen forbereder den vurdering, du samler i Modul04.

## Hvis du har mere tid

Undersøg et kvalitetsproblem, som en simpel kolonne- eller typekontrol ikke finder. Sammenlign, hvad en regel kan opdage alene, og hvad der kræver metadata eller domæneviden.

## Hvis du var syg / arbejder videre hjemme

```text
kontrollér realtime-mellemoutput → Modul03-miniopgaver
→ afregningsmetadata og DATAORDLISTE.md → starterprojektets OPGAVE.md, Modul03
→ pipeline.py, TODO 4–6 → tre periodeoutputs → checkpoint
```

Hvis rækkeantallet ændrer sig uventet, undersøg join keys, primærnøgler og dubletter før nye beregninger. Hvis felter afviger, kontrollér definitioner og enheder før en konklusion om datakvalitet.

## Ressourcer ved behov

- `DATAORDLISTE.md`: udveksling, prisområdebalance og sammenligningsfelter.
- Metadata for begge kilder: definitioner og kendte begrænsninger.
- starterprojektets `OPGAVE.md` og `pipeline.py`: join, flag og output.

---

# 5. Modul04

**Placering:** Før afslutningsmodulet

## Hvad arbejder vi med?

Du bruger dit output til at besvare spørgsmål og vurderer, hvordan løsningen kan drives og forvaltes. Den fælles undervisning har fire læringsblokke:

1. **Fra resultat til begrundet svar:** På separate eksempeldata sammenholder du absolutte og relative forskelle, samlede mål og enkelttilfælde. Du skelner mellem observation, mulig forklaring og dokumenteret konklusion.
2. **Big Data i sammenhæng:** Du genbruger karakteristika fra Modul01 og vurderer forskellen mellem et lille udsnit og et løbende produktionssystem.
3. **Software og platform:** I M04.3 sammenligner du lokal Python/pandas, en fælles PostgreSQL-løsning og ét cloudalternativ, BigQuery eller Redshift. Du undersøger komponenternes roller og trade-offs ved ændrede behov for fælles adgang og opdatering. Ingen konto eller deployment kræves.
4. **Governance og ansvar:** Et separat eksempel med et enhedsregister og en beskrevet registerkonflikt bruges til at diskutere fælles identiteter, MDM, definitioner, domæneejerskab, historik og rettelser. Du skal ikke fremskaffe et ekstra register.

I hovedcasen besvarer du mindst tre spørgsmål og samler Big Data-, platform-, ansvars- og sikkerhedsvurderingen efter starterprojektets `OPGAVE.md`. Her finder du også kravet om at sammenligne mindst to perioder eller prisområder. Undersøgelserne skal bygge på dit output og vise relevante begrænsninger. Du afprøver en samlet genkørsel inden afslutningsmodulet, så større fejl opdages i tide.

## Modulets checkpoint

Du kan vise tre foreløbige svar med tabeller eller figurer, din Big Data-vurdering og et begrundet platform- og ansvarsvalg. Du kan forklare:

- hvilke perioder, områder og kvalitetsflag svaret bygger på;
- hvordan konkrete timer understøtter eller nuancerer det samlede resultat;
- hvad data ikke dokumenterer;
- hvem der skal reagere på fejl, ændrede definitioner og adgangsbehov.

Det konkrete checkpoint ejes af Modul04-afsnittet i starterprojektets `OPGAVE.md`.

## Hvis du har mere tid

Undersøg, om en konklusion ændrer sig ved et andet velbegrundet kvalitetsfilter. Beskriv alternativt, hvad en central løsning skal gøre, hvis samme data modtages igen, eller en kilde efterfølgende retter historiske værdier.

## Hvis du var syg / arbejder videre hjemme

```text
kontrollér output og kvalitetsrapport → Modul04-eksempler
→ spørgsmålsbanken i starterprojektets OPGAVE.md → tre svar med evidens
→ Big Data- og platformopgaver → prøvegenkørsel → checkpoint
```

Start med ét afgrænset spørgsmål. Angiv først periode, område, måling og kvalitetsafgrænsning. Brug den samme arbejdsform på de øvrige spørgsmål.

## Ressourcer ved behov

- starterprojektets `OPGAVE.md`: spørgsmålsbank og caseopgaver om Big Data samt platform, ansvar og sikkerhed.
- Dine periodeoutputs og kvalitetsrapporter: evidens for svarene.
- Kildemetadata: støtte til at vurdere mulige forklaringer og begrænsninger.

---

# 6. Modul05

**Aktuel placering:** Fredag; afsluttende del af forløbet

## Hvad arbejder vi med?

Du færdiggør, afleverer og demonstrerer din samlede løsning. Der planlægges ikke nyt centralt kernestof eller nye værktøjer. Den fælles tid bruges til kort opsamling, spørgsmål og målrettet hjælp.

### Modulets arbejdsflow

```text
færdiggør løsningen → genkør fra rådata → kontrollér output
→ brugbart demonstrationsgrundlag → M05.1: prøveforklaring
→ aflever → demonstrér og begrund → M05.2: forløbsfeedback
```

Du følger afslutningsafsnittet i starterprojektets `OPGAVE.md` og forbereder en individuel forklaring af en transformation og et kvalitetsfund. Brug M05.1 i `20555_Laerling_Miniopgaver_Modul05.md`, når demonstrationsgrundlaget er brugbart. Efter aflevering og demonstration giver du forløbsfeedback gennem M05.2; den er adskilt fra den faglige feedback, du modtager på arbejdet. Den konkrete afleveringsfrist, kanal og tidsramme for fremlæggelse meddeles særskilt.

## Modulets checkpoint

Du kan demonstrere sammenhængen:

```text
kilde → rådata → validering → transformation → join → kvalitet → anvendeligt output
```

Du kan forklare dine antagelser, begrænsninger og tre undersøgelsessvar med dokumenteret evidens. Kode, output og forklaring skal hænge sammen. Den samlede afleveringsliste ejes af starterprojektets `OPGAVE.md`.

## Hvis du bliver færdig tidligt

Kontrollér først, om en anden kan forstå startvejledningen og følge et resultat tilbage til kilden. Øv derefter din forklaring og gør usikkerheder tydelige. Prioritér en gennemskuelig aflevering frem for en ny stor funktion.

## Hvis du var syg / arbejder videre hjemme

Følg samme rækkefølge: `OPGAVE.md`, Modul05 → færdiggørelse/genkørsel/kontrol → M05.1 → aftalt aflevering og demonstration → M05.2. Ved fravær til selve afslutningen aftaler du aflevering og individuel demonstration med underviseren; en genkørsel alene erstatter ikke forklaringen.

## Ressourcer ved behov

- starterprojektets `OPGAVE.md`: afslutningsopgaver, minimumsevidens og kvalitetskriterier.
- starterprojektets `README.md`: teknisk opstart og kørsel.
- Din egen kode, dokumentation, output og kvalitetsrapporter: grundlag for demonstrationen.
- `20555_Laerling_Afleveringsvejledning.md` og `20555_Laerling_Miniopgaver_Modul05.md`: praktisk afslutning, prøveforklaring og forløbsfeedback.

---

# 7. Hvis du bliver bagud

Find det første checkpoint, du ikke kan dokumentere:

```text
1. Kan jeg starte projektet og forklare kilderne?
2. Kan jeg kontrollere og aggregere realtime-data korrekt?
3. Kan jeg sammenkoble kilderne og synliggøre problemer?
4. Kan jeg besvare spørgsmål og begrunde anvendelsen?
5. Kan jeg genkøre, aflevere og forklare løsningen?
```

Arbejd på det første manglende led. Brug den lille sommertidsperiode til at undersøge tekniske fejl og kontrollér derefter de øvrige perioder som angivet i opgaven.

Ved behov for hjælp: vis kommandoen, fejlmeddelelsen, det første fejlende trin og det, du forventede. Skeln mellem manglende kendskab til Python/pandas, en programmeringsfejl og et problem med dataenes betydning. De kræver forskellig hjælp.

Hvis et fælles begreb er nyt for dig, genfind modulets forklaring og separate miniopgave. Du behøver ikke materialer fra 20556 for at finde opgaven i dette fag.

---

# 8. Materialer og links

Denne forløbsoversigt er indgangen til hele faget. Når du arbejder i hovedcasen, er starterprojektets `OPGAVE.md` den styrende fil for casearbejdet. Underviseren udleverer de separate miniopgaver og undervisningsmaterialer til det relevante modul. Når slides er udleveret i LMS, bruges de til genlæsning sammen med miniopgaverne.

Hvert modul har nu `20555_Laerling_Laeringsnoter_ModulNN.md` og `20555_Laerling_Miniopgaver_ModulNN.md`, hvor NN er 01–05. Brug læringsnoterne til forklaringer og miniopgavefilen til aktiviteterne. De fælles eksempeldata ligger i Sensorlab; de er konstruerede og adskilt fra Energinets virkelige snapshots. Modul05-aktiviteterne er prøveforklaring og feedback, ikke nyt stof.

Fælles støtte: `20555_Laerling_Reference_Python_Pandas.md`, `20555_Laerling_Kilder.md`, `20555_Laerling_Afleveringsvejledning.md` og `20555_Laerling_Feedback.md`. Starterprojektets docs-mappe indeholder skabeloner til eksisterende dokumentationskrav. Efter TODO 1–3 kan `run_pipeline.py` køres med `--stage realtime` for at gemme Modul02-mellemoutput.

## Materialer til Modul01

Start med Sensorlabs `README.md` under Faelles til kopi og Python/pandas-setup. Følg derefter Modul01-noter og miniopgaver. Fortsæt så med starterprojektets `README.md`, `check_setup.py` og Modul01 i `OPGAVE.md`. Brug `DATAORDLISTE.md`, de medfølgende metadata og `snapshot_manifest.json` til at undersøge kilder og datagrundlag. Miniopgaverne introducerer den nødvendige Python/pandas-arbejdsform og forskellige dataformer.

## Materialer til Modul02

Brug `pipeline.py`, `contracts.py`, `run_pipeline.py` og Modul02-afsnittet i starterprojektets `OPGAVE.md`. Miniopgaverne træner transport, kontrakt, transformation, tid og versionsspor på separate data. Brug dataordlisten og metadata ved realtime-afledningerne og starterens README til realtime-checkpointet. De rå snapshots skal bevares uændrede.

## Materialer til Modul03

Brug `pipeline.py`, `DATAORDLISTE.md`, afregningsmetadata og Modul03-afsnittet i starterprojektets `OPGAVE.md`. Genfind miniopgaverne om join, kvalitet og databeskyttelse før selvstændig anvendelse. M03.2 beskriver dit lokale testkald til Sensorlabs `combine`; standardkørslen af `exercises.py` viser kun Modul02-output.

## Materialer til Modul04

Brug starterprojektets `OPGAVE.md`, dine egne outputs, kvalitetsrapporter og dokumentation. Genfind metadata, når en afvigelse kræver en præcis kildeforklaring. Brug blok C i `20555_Laerling_Laeringsnoter_Modul04.md` til M04.3’s konkrete platformsammenligning.

## Materialer til Modul05

Start med starterprojektets `OPGAVE.md`, Modul05, og `20555_Laerling_Afleveringsvejledning.md`. Brug læringsnoterne til repetition, M05.1 i miniopgavefilen til prøveforklaring og til sidst M05.2 samt `20555_Laerling_Feedback.md` til forløbsfeedback. Egne outputs og dokumentation er demonstrationsgrundlaget.

---

## Revisionshistorik

| Version | Dato | Hovedændring |
|---|---|---|
| 1.5 | 22. september 2026 | Afstemt med aktuelle casekrav og modulaktiviteter: præcist TODO-/realtime-forløb, opslag før realtime-afledninger, konkrete platformalternativer, sammenligning på tværs, afslutningsrækkefølge og kronologisk materialerute. Ingen nye lærlingekrav. |
| 1.4 | 21. september 2026 | Registrerer ændret Modul01-startvej: Sensorlab-setup før miniopgaver og derefter Energinet-setup. NAV-008: revisionsmetadata afstemt; ingen yderligere faglige ændringer. |
| 1.3 | 21. september 2026 | Præciserer den kanoniske arbejdsrute mellem forløbsoversigt, starter-README og OPGAVE samt fagterminologi for primærnøgle/join key; ingen nye krav. |
| 1.2 | 21. september 2026 | QA-006. |
| 1.1 | 20. september 2026 | Henviser til de konkrete modulnoter, miniopgaver, Sensorlab, fælles støtte og runnerens Modul02-checkpoint. |
| 0.1 | Før 20. september 2026 | Foreløbig navigation med fem moduler og henvisning til Energinet-pilotopgaven. |
| 1.0 | 20. september 2026 | Udbygget efter 20556-forløbsoversigtens hovedstruktur med læringsblokke, checkpoints, fordybelse, fraværsveje og materialer. Første gennemførelse bruger holdets erfaring fra 20556; Python/pandas introduceres særskilt. Separate miniopgaver før transfer, offline-case og afslutning uden nyt kernestof er gjort eksplicitte. |
