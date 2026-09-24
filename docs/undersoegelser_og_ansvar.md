# Undersøgelser og ansvar – Modul04 og Modul05

Denne fil samler de resterende dokumentationskrav fra `OPGAVE.md` på baggrund af projektets egne genererede outputs.

## Analysemetode

De tre valgte spørgsmål er nr. **1, 3 og 5** fra spørgsmålsbanken.

Til de samlede sammenligninger bruges primært **middel absolut afvigelse (MAE)**:

```text
MAE = gennemsnittet af |realtime - afregning|
```

For spørgsmål 1 og 3 bruges rækker, hvor realtime og afregning er matchet, og hvor realtime-timen er komplet med 12 femminuttersintervaller. Negative produktionsværdier slettes ikke; de bevares som kvalitetsflag og tælles særskilt.

Resultaterne beskriver de udleverede snapshots. De kan ikke alene bruges til at konkludere, at alle vinter- eller sommerperioder opfører sig på samme måde.

---

# Undersøgelse 1

## Er realtime-data lige anvendelige i vinter og sommer?

### Hvorfor spørgsmålet er relevant

Realtime-data skal kunne bruges hurtigt, men kvaliteten kan variere mellem perioder. Derfor sammenlignes januar og juni for at se, om afvigelsen fra den senere afregning og antallet af kvalitetsproblemer er omtrent det samme.

### Periode, område, måling og kvalitetsfilter

- Perioder: januar 2026 og juni 2026.
- Områder: DK1 og DK2 samlet.
- Kvalitetsfilter for MAE: `quality_join_matched == True` og `quality_rt_complete_hour == True`.
- Negative produktionsintervaller bevares som kvalitetsfund.
- Datakilder:
  - `output/analysis_ready_january.csv`
  - `output/analysis_ready_june.csv`
  - `output/quality_january.json`
  - `output/quality_june.json`

### Samlede målinger

| Sammenligningsfelt | Januar MAE (MWh) | Juni MAE (MWh) |
|---|---:|---:|
| Offshore vind | 14,81 | 31,87 |
| Onshore vind | 59,68 | 46,95 |
| Sol til net | 4,40 | 90,44 |
| Udenlandsk udveksling | 17,57 | 32,86 |
| Load/balance | 46,99 | 207,85 |

Kvalitetsfund:

| Periode | Ufuldstændige rækker | Rækker med negativ realtime-produktion |
|---|---:|---:|
| Januar | 2 | 4 |
| Juni | 6 | 37 |

### Konkrete timer som evidens

**Januar:** `2026-01-13 09:00 UTC`, DK2:

```text
diff_load_mwh = -284,40 MWh
quality_issue_codes = OK
```

**Juni:** `2026-06-22 08:00 UTC`, DK1:

```text
diff_load_mwh = -1809,34 MWh
diff_solar_grid_mwh = -1299,25 MWh
quality_issue_codes = OK
```

### Observation

I de udleverede snapshots er realtime-data **ikke lige anvendelige i januar og juni efter den valgte målemetode**. Juni har større absolutte afvigelser for offshore vind, sol, udenlandsk udveksling og load/balance. Onshore vind er en undtagelse, hvor januar har større MAE.

Juni har også flere ufuldstændige timer og flere rækker med negativ realtime-produktion.

### Mulig forklaring og begrænsning

Resultatet viser en forskel mellem netop januar- og juni-snapshottet, men dokumenterer ikke alene årsagen. Forskellen kan hænge sammen med produktionens sammensætning, solproduktion, kildeforskelle, kendte metadataforhold eller andre driftsforhold. To udleverede perioder er ikke tilstrækkelige til at generalisere om alle vintre og somre.

---

# Undersøgelse 2

## Er forskellen mellem realtime og afregning den samme i DK1 og DK2?

### Hvorfor spørgsmålet er relevant

Hvis afvigelsen er forskellig mellem prisområderne, bør DK1 og DK2 ikke behandles som om realtime-kvaliteten nødvendigvis er ens.

### Periode, område, måling og kvalitetsfilter

- Perioder: januar og juni 2026.
- Områder: DK1 sammenlignes med DK2.
- Kvalitetsfilter: matchede rækker med komplette realtime-timer.
- Mål: MAE for de vigtigste sammenligningsfelter.

### Januar – MAE pr. prisområde

| Felt | DK1 (MWh) | DK2 (MWh) |
|---|---:|---:|
| Offshore vind | 23,80 | 5,82 |
| Onshore vind | 108,03 | 11,33 |
| Sol til net | 6,76 | 2,04 |
| Udenlandsk udveksling | 20,10 | 15,05 |
| Load/balance | 41,79 | 52,18 |

### Juni – MAE pr. prisområde

| Felt | DK1 (MWh) | DK2 (MWh) |
|---|---:|---:|
| Offshore vind | 58,43 | 5,31 |
| Onshore vind | 86,60 | 7,29 |
| Sol til net | 135,06 | 45,82 |
| Udenlandsk udveksling | 45,78 | 19,94 |
| Load/balance | 294,66 | 121,04 |

### Konkrete timer som evidens

Ved `2026-06-22 08:00 UTC` er begge rækker markeret `OK`, men forskellen i load/balance er:

```text
DK1: -1809,34 MWh
DK2:  -397,30 MWh
```

Ved `2026-01-13 09:00 UTC` er forskellen i load/balance:

```text
DK1:  -23,86 MWh
DK2: -284,40 MWh
```

### Observation

Forskellen mellem realtime og afregning er **ikke den samme i DK1 og DK2**.

I både januar og juni er vindafvigelserne betydeligt større i DK1 end i DK2. I juni er også sol, udveksling og load/balance klart større i DK1. Januar viser dog, at mønsteret ikke er identisk for alle felter: load/balance har en lidt større gennemsnitlig absolut afvigelse i DK2 end i DK1.

### Mulig forklaring og begrænsning

Prisområderne har forskellige produktions- og udvekslingsmønstre. Resultatet viser, at kvalitet eller sammenlignelighed bør vurderes pr. område og pr. målefelt. Det dokumenterer ikke i sig selv, hvorfor forskellene opstår.

---

# Undersøgelse 3

## Hvad sker der med analysen, hvis ufuldstændige timer behandles som normale timer?

### Hvorfor spørgsmålet er relevant

En time med færre end 12 femminuttersintervaller indeholder mindre realtime-data end forventet. Hvis den behandles som en almindelig komplet time, kan forskellen mod afregningsdata se kunstigt stor ud.

### Januar

Der er præcis to ufuldstændige rækker:

| UTC-time | Område | Intervaller | Load-difference |
|---|---|---:|---:|
| 2026-01-06 22:00 | DK1 | 9 | -861,08 MWh |
| 2026-01-06 22:00 | DK2 | 9 | -479,52 MWh |

For load/balance:

```text
MAE for ufuldstændige timer: 670,30 MWh
MAE for komplette timer:      46,99 MWh
```

Hvis alle timer behandles som normale, bliver den månedlige load-MAE:

```text
47,82 MWh
```

Hvis de ufuldstændige timer filtreres fra:

```text
46,99 MWh
```

Det er ca. **1,8 %** forskel på den månedlige MAE, selv om de enkelte ufuldstændige timer er meget mere afvigende.

### Juni

Der findes seks ufuldstændige rækker. Den mest markante UTC-time er `2026-06-13 11:00`:

```text
DK1: 3 intervaller, diff_load_mwh = -2723,12 MWh
DK2: 3 intervaller, diff_load_mwh = -1462,80 MWh
```

For load/balance:

```text
MAE for ufuldstændige timer: 788,46 MWh
MAE for komplette timer:     207,85 MWh
```

Hvis alle timer behandles som normale:

```text
210,27 MWh
```

Hvis de ufuldstændige timer filtreres fra:

```text
207,85 MWh
```

Det er ca. **1,2 %** forskel på den månedlige MAE.

### Observation

Ufuldstændige timer kan være **meget misvisende på timeniveau**. De har langt større load-afvigelser end komplette timer i både januar og juni.

Fordi de udgør få rækker i de udleverede måneder, ændrer de den samlede månedlige MAE relativt lidt. Men de kan ændre maksimumværdier, konkrete hændelsesvurderinger og beslutninger, der bygger på enkelte timer.

### Konklusion

Ufuldstændige timer bør ikke behandles som normale timer uden et kvalitetsflag. Projektets løsning er derfor at **bevare dem og markere dem med `RT_INCOMPLETE_HOUR`** i stedet for at slette eller skjule dem.

---

# Big Data-vurdering

Casen kan vurderes med flere Big Data-karakteristika. Det er vigtigt at skelne mellem de relativt små undervisningssnapshots og det løbende produktionssystem, som de repræsenterer.

## Volume

De udleverede snapshots er håndterbare lokalt. Januar har eksempelvis 17.850 realtime-rækker og 1.488 afregningsrækker.

I et løbende system kommer femminuttersdata kontinuerligt, for flere målefelter og over længere historik. Datamængden vokser derfor løbende og stiller større krav til lagring, indeksering, backup og historik end undervisningsudsnittet gør.

## Velocity

Realtime-kilden arbejder med femminuttersintervaller. Et produktionssystem skal derfor kunne modtage, validere og lagre nye data regelmæssigt.

Afregningsdata kommer senere og kan blive opdateret. Systemet skal derfor kunne håndtere både hurtige foreløbige data og senere mere modne værdier.

## Variety

Projektet arbejder med to kilder, som ikke har samme grain, enhed eller betydning:

```text
realtime: 5 minutter, primært MW
afregning: 1 time, MWh
```

Derudover bruges JSON som råformat, CSV som analyseklart output og JSON som kvalitetsrapport. Felter med lignende navne kan have forskellige definitioner.

## Veracity

Datakvalitet er et centralt problem i casen. Projektet finder blandt andet:

- ufuldstændige realtime-timer;
- negative produktionsværdier;
- strukturelle null-værdier;
- forskelle mellem realtime og afregning;
- metadataadvarsler og mulige senere revisioner.

Det er derfor ikke nok, at data kan læses teknisk. Betydning, kvalitet og kontrakter skal også kontrolleres.

## Value

Realtime-data har værdi, fordi de er hurtigt tilgængelige. Afregningsdata har værdi, fordi de er senere og mere modne.

Projektets værdi ligger i at gøre forskellen synlig, så brugeren kan vurdere, om realtime-data er gode nok til den konkrete anvendelse.

## Historik og revisioner

Afregningsdata kan ændre sig senere. Et produktionssystem bør derfor kunne dokumentere, hvilken version af kilden der blev brugt, og kunne genkøre beregninger fra kendte snapshots.

### Samlet vurdering

Det udleverede undervisningsdatasæt er ikke stort nok til, at størrelse alene gør det til et Big Data-problem. Casen har alligevel relevante Big Data-egenskaber, især **velocity, variety, veracity, value og historik/revisioner**, når den ses som udsnit af et løbende produktionssystem.

---

# Platform, ansvar og sikkerhed

## Lokal offline-løsning

Den nuværende løsning kører lokalt med Python/pandas og faste JSON-snapshots.

### Fordele

- nem at reproducere;
- kræver ikke ekstern API-adgang;
- samme input kan bruges igen;
- enkel fejlsøgning;
- rådata kan holdes uændrede.

### Begrænsninger

- data opdateres ikke automatisk;
- samarbejde og fælles adgang er begrænset;
- lokal maskine er et enkelt fejlpunkt;
- adgangskontrol og central logning er begrænset;
- historik og nye versioner skal håndteres manuelt.

## Tænkt central løsning

En central løsning kan bestå af:

```text
Energinet / kilde
      ↓
indsamler
      ↓
raw-lager
      ↓
validering / transformation
      ↓
database
      ↓
internt API
      ↓
brugere / analyse
```

Den kan automatisere indsamling og give flere brugere adgang til samme version af data.

## Ansvar

Et muligt ansvarsskema er:

| Område | Ansvar |
|---|---|
| Indsamling | Den komponent/person der driver ingestion skal sikre hentning, tidspunkt, kilde og fejl/genforsøg |
| Validering | Pipeline-/dataansvarlig skal vedligeholde kontrakter og reagere på schema- og nøglebrud |
| Adgang | Systemejer skal styre hvem der må læse, ændre og administrere løsningen |
| Rettelser | Dataansvarlig skal beslutte hvordan nye kildeversioner og korrektioner indlæses uden at skjule historikken |
| Analyse | Analytiker/udvikler skal dokumentere filtre, antagelser og begrænsninger |

## Hvad bør logges?

Et centralt system bør som minimum kunne dokumentere:

- hvornår data blev hentet;
- hvilken kilde og periode der blev hentet;
- fil/version/checksum;
- rækkeantal;
- valideringsfejl;
- schemaændringer;
- genforsøg og fejl;
- hvilken kode-/pipelineversion der producerede output;
- hvem eller hvilken service der udførte administrative handlinger.

## API-nøgler og forbindelsesoplysninger

Secrets bør ikke ligge direkte i Python-koden, committed `.env`-filer eller Git-historikken.

De bør opbevares i en egnet secret-/miljøkonfiguration med adgang begrænset til de services og personer, der har behov for dem. Secrets bør heller ikke skrives ud i logs.

## Persondata og GDPR

Hoveddataene i casen beskriver elproduktion, udveksling og prisområder og indeholder ikke i sig selv åbenlyse personoplysninger om private personer.

GDPR bør stadig vurderes i en rigtig central løsning, fordi omkringliggende systemdata kan indeholde eksempelvis:

- brugeridentiteter;
- adgangslogs;
- IP-adresser;
- kontaktoplysninger;
- andre fremtidige datakilder.

Konklusionen bør derfor dokumenteres i stedet for blot at antage, at GDPR aldrig er relevant.

## Platformvalg

Til undervisningscasen er den lokale offline-løsning tilstrækkelig, fordi datasættene er faste og genkørbare.

Hvis løsningen skulle indsamle femminuttersdata løbende og deles mellem flere brugere, ville en central database med automatiseret ingestion, adgangskontrol, overvågning og et internt API være mere egnet.

---

# Antagelser og kendte begrænsninger

1. Realtime-værdier i MW behandles efter caseantagelsen som repræsentative for det efterfølgende femminuttersinterval.
2. `MW × 5/60` giver et beregnet sammenligningsgrundlag i MWh og er ikke beskrevet som officiel afregning.
3. UTC bruges som teknisk tid til grouping og join; dansk tid bevares til fortolkning.
4. En komplet realtime-time forventes at have præcis 12 femminuttersintervaller.
5. Ufuldstændige timer slettes eller udfyldes ikke automatisk; de bevares og flagges.
6. Strukturelle null-værdier behandles kun som 0 i de udvekslingsfelter, hvor projektets metadata giver grundlag for det.
7. Storebælt regnes ikke som udenlandsk udveksling, men indgår i prisområdebalancen.
8. Afregningsdata bruges som senere og mere modnede sammenligningsdata, ikke som en absolut og ufejlbarlig sandhed.
9. Undersøgelserne bygger på de udleverede januar-, juni- og DST-snapshots. Resultaterne kan ikke uden videre generaliseres til andre år eller perioder.
10. MAE er valgt som hovedmål i de tre undersøgelser. Andre mål, fx relative fejl, median, korrelation eller percentiler, kan give yderligere perspektiver.
11. Kvalitetsflag gør problemer synlige, men forklarer ikke automatisk årsagen til dem.

---

# Demonstrationsrute

En kort demonstration kan gennemføres sådan:

## 1. Vis setup

```powershell
python check_setup.py
```

Forklar at `SETUP PASS` kontrollerer miljø og råfiler.

## 2. Vis Modul02 separat

```powershell
python run_pipeline.py --period dst --stage realtime
```

Vis:

```text
output/realtime_hourly_dst.csv
```

Forklar:

```text
MW × 5/60 → MWh
5-minuttersdata → UTC-time + prisområde
12 intervaller = komplet time
```

## 3. Vis hele pipelinen

```powershell
python run_pipeline.py --period january --stage all
```

Vis:

```text
output/analysis_ready_january.csv
output/quality_january.json
```

## 4. Forklar én transformation

Brug eksempelvis `mw_to_mwh()`:

```text
120 MW × 5/60 = 10 MWh
```

Forklar at hvert femminuttersinterval konverteres før timeaggregation.

## 5. Forklar ét kvalitetsfund

Brug januar `2026-01-06 22:00 UTC`:

```text
DK1: 9 intervaller
DK2: 9 intervaller
```

Begge timer bevares, men markeres `RT_INCOMPLETE_HOUR`.

Alternativt kan juni `2026-06-13 11:00 UTC` vises, hvor begge områder kun har 3 intervaller.

## 6. Vis at problemer ikke skjules

Vis kolonnerne:

```text
quality_join_status
quality_rt_complete_hour
quality_rt_negative_production
quality_issue_codes
```

Forklar at problemrækker bevares i outputtet.

## 7. Opsummer de tre analyser

- Januar og juni har ikke samme afvigelsesprofil.
- DK1 og DK2 har ikke samme afvigelsesprofil.
- Ufuldstændige timer kan være meget misvisende på timeniveau.

## 8. Forklar eget arbejde og anvendt hjælp

Denne del skal udfyldes personligt og ærligt før aflevering/demonstration:

```text
Jeg har selv lavet/forstået:
[udfyld]

Jeg har fået hjælp til:
[udfyld]

Værktøjer/kilder jeg har brugt:
[udfyld]
```

Det er vigtigt, at denne del afspejler det arbejde og den hjælp, der faktisk er anvendt.
