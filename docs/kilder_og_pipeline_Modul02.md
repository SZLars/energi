# Kilder og pipeline – Modul01 og Modul02

> Denne dokumentation samler checkpoint-arbejdet for Modul01 og Modul02 i Energinet-casen.
> Resultaterne i Modul02-afsnittet er kontrolleret på den udleverede projektkopi med den implementerede `src/pipeline.py`.

# Modul01 – Kilder, grain og rådata

## Kilder

| Kilde og snapshot | Formål | Grain / primærnøgle | Enhed / tid | Kendte begrænsninger |
|---|---|---|---|---|
| Realtime – `realtime_2026-01.json` / `ElectricityProdex5MinRealtime` | Hurtige operationelle data om produktion og eludveksling | Én værdi ved et 5-minutters tidspunkt i ét prisområde. Sammensat primærnøgle: `(Minutes5UTC, PriceArea)` | Primært effekt i MW. `Minutes5UTC` er teknisk UTC-tid, `Minutes5DK` er dansk lokaltid. Prisområder i casen: DK1 og DK2. | Data bygger på opskalerede realtime/SCADA-målinger. Fejl kan forekomme og bliver generelt ikke rettet. Nogle udvekslingsfelter er strukturelt null i et prisområde. |
| Afregning – `settlement_2026-01.json` / `ProductionConsumptionSettlement` | Senere afregnings- og statistikdata til sammenligning med realtime | Én time i ét prisområde. Sammensat primærnøgle: `(HourUTC, PriceArea)` | Energi i MWh. `HourUTC` er UTC-time, `HourDK` er dansk lokaltid. Prisområder: DK1 og DK2. | Data kommer senere end realtime og kan efteropdateres. Nogle null/0-værdier kræver fortolkning. |

## Observation af de to snapshots

### Realtime – januar

- Fil: `data/raw/realtime_2026-01.json`
- Antal rækker: **17.850**
- Prisområder: **DK1, DK2**
- Tidskolonner: `Minutes5UTC`, `Minutes5DK`
- Primærnøgle: `(Minutes5UTC, PriceArea)`
- Eksempel på målefelter: `OffshoreWindPower`, `OnshoreWindPower`, `SolarPower`, `ExchangeGermany`, `ExchangeGreatBelt`.
- Flere forbindelseskolonner indeholder null-værdier, fordi ikke alle forbindelser findes i begge prisområder.

### Afregning – januar

- Fil: `data/raw/settlement_2026-01.json`
- Antal rækker: **1.488**
- Prisområder: **DK1, DK2**
- Tidskolonner: `HourUTC`, `HourDK`
- Primærnøgle: `(HourUTC, PriceArea)`
- Eksempel på felter: vindproduktion, solproduktion, udveksling og `GrossConsumptionMWh`.

## Grain og senere join key

Realtime-data har finere grain end afregningsdata:

```text
Realtime:
5-minutters tidspunkt + prisområde
        ↓ aggregation
UTC-time + prisområde

Afregning:
UTC-time + prisområde
```

Efter realtime er aggregeret til timer, skal begge kilder have samme grain:

```text
(hour_utc, price_area)
```

Det bliver den senere **join key** mellem realtime og afregning.

## Planlagt pipeline

```text
RAW JSON
│
├── realtime JSON
│      │
│      ▼
│   indlæsning
│      │
│      ▼
│   validering
│   - datasætnavn
│   - obligatoriske kolonner
│   - PriceArea = DK1/DK2
│   - primærnøgle unik
│   - timestamps kan parses
│      │
│      ▼
│   MW × 5/60 → MWh
│      │
│      ▼
│   aggregation
│   5 min → UTC-time + prisområde
│   + antal intervaller pr. time
│      │
│      └──────────────────────┐
│                             │
└── afregnings JSON           │
       │                      │
       ▼                      │
    indlæsning                │
       │                      │
       ▼                      │
    validering                │
       │                      │
       ▼                      │
    sammenlignelige felter    │
       │                      │
       └──────────────┐       │
                      ▼       ▼
                 one-to-one outer join
                 på (hour_utc, price_area)
                         │
                         ▼
                    kvalitetsflag
                         │
                         ▼
                analyseklart CSV-output
                         +
                  kvalitetsrapport
```

## Tre foreløbige undersøgelsesspørgsmål

1. **Er realtime-data lige anvendelige i vinter og sommer?**
2. **Er forskellen mellem realtime og afregning den samme i DK1 og DK2?**
3. **Hvad sker der med analysen, hvis ufuldstændige timer behandles som normale timer?**

## Modul01-checkpoint

- [x] `check_setup.py` giver `SETUP PASS`.
- [x] Ét realtime-snapshot er undersøgt.
- [x] Ét afregningssnapshot er undersøgt.
- [x] Grain, primærnøgler, tid, enheder og prisområder er identificeret.
- [x] Senere join key er identificeret som `(hour_utc, price_area)`.
- [x] Metadata og centrale advarsler er gennemgået.
- [x] Pipeline fra raw til analyseklart output er skitseret.
- [x] Tre foreløbige undersøgelsesspørgsmål er valgt.

---

# Modul02 – Validering, MW→MWh og timer

## Implementerede trin

I `src/pipeline.py` er Modul02 afgrænset til **TODO 1–3**.

### TODO 1 – `validate_snapshot()`

Valideringen kontrollerer den fatale datakontrakt før transformationen fortsætter:

- obligatoriske kolonner skal findes;
- timestampkolonnen skal kunne konverteres til UTC;
- manglende timestamps afvises;
- `PriceArea` skal være DK1 eller DK2;
- den sammensatte primærnøgle `(timestamp, PriceArea)` skal være unik;
- kontraktbrud giver en tydelig fejl og stopper senere trin.

For realtime svarer primærnøglen til:

```text
(Minutes5UTC, PriceArea)
```

Det betyder, at samme femminutters tidspunkt ikke må forekomme mere end én gang for samme prisområde.

## MW til MWh – metodeantagelse

Realtime-kilden indeholder primært effekt i **MW**, mens sammenligningen senere skal ske på energi i **MWh**.

Casens beregningsregel er:

```text
MWh = MW × 5/60
```

Et eksempel med 120 MW:

```text
120 MW × 5/60 = 10 MWh
```

Omregningen foretages på **hvert femminuttersinterval før summering til time**.

### Metodeforbehold

I denne case behandles værdien ved `Minutes5UTC = t` som repræsentativ effekt for det efterfølgende interval:

```text
[t, t + 5 minutter)
```

Den beregnede realtime-MWh er derfor et **tilnærmet sammenligningsgrundlag**. Den skal ikke beskrives som Energinets officielle afregningsværdi.

## TODO 3 – timeaggregation

Realtime-data grupperes efter:

```text
hour_utc + price_area
```

`hour_utc` dannes ved at runde `Minutes5UTC` ned til UTC-timen.

Outputtet har én række pr. UTC-time og prisområde og indeholder:

```text
hour_utc
price_area
rt_interval_count
rt_offshore_wind_mwh
rt_onshore_wind_mwh
rt_solar_mwh
rt_external_exchange_mwh
rt_load_balance_mwh
rt_negative_production_intervals
```

En normal komplet UTC-time forventes at have:

```text
60 / 5 = 12 intervaller
```

Derfor bevares `rt_interval_count`, så ufuldstændige timer kan opdages i stedet for at blive skjult.

## Storebælt og strukturelle null-værdier

Storebæltsforbindelsen flytter energi mellem DK1 og DK2. Den behandles derfor forskelligt afhængigt af beregningen:

- `ExchangeGreatBelt` regnes **ikke** som udenlandsk udveksling for Danmark;
- `ExchangeGreatBelt` indgår i prisområdebalancen, fordi forbindelsen flytter energi mellem DK1 og DK2.

For visse udenlandske forbindelser kan en null-værdi være **strukturel**, fordi forbindelsen fysisk ikke findes i det pågældende prisområde. I realtime-afledningen behandles sådanne null-værdier som 0 kun i de relevante udvekslingskolonner. En strukturel null må ikke generelt tolkes som en ukendt måling.

## Testkommandoer

Modul02 testes først på den lille sommertidsperiode:

```powershell
python run_pipeline.py --period dst --stage realtime
```

Derefter januar:

```powershell
python run_pipeline.py --period january --stage realtime
```

De relevante mellemoutputs er:

```text
output/realtime_hourly_dst.csv
output/realtime_hourly_january.csv
```

## Kontrol 1 – grain i realtime-output

Det genererede output har én række pr.:

```text
(hour_utc, price_area)
```

DST-outputtet indeholder:

- **71 unikke UTC-timer**;
- **2 prisområder**: DK1 og DK2;
- **142 rækker i alt**.

Det passer med:

```text
71 timer × 2 prisområder = 142 rækker
```

Der blev ikke fundet ufuldstændige UTC-timer i DST-outputtet; alle rækker havde `rt_interval_count = 12`.

## Kontrol 2 – sommertid

UTC bruges som teknisk tidsnøgle. Når DST-outputtet konverteres til `Europe/Copenhagen`, bliver antallet af lokale timer:

| Lokal dato | DK1 | DK2 |
|---|---:|---:|
| 2026-03-28 | 24 | 24 |
| **2026-03-29** | **23** | **23** |
| 2026-03-30 | 24 | 24 |

Sommertid starter **29. marts 2026**. Den lokale tid springer fra 01:59 til 03:00, så klokken 02 findes ikke som lokal time den dag.

Eksempel fra DK1:

```text
UTC 2026-03-29 00:00 → dansk tid 2026-03-29 01:00 +01:00
UTC 2026-03-29 01:00 → dansk tid 2026-03-29 03:00 +02:00
```

Der er derfor **23 lokale timer** på sommertidsdøgnet, ikke 24 eller 25. Samtidig bevares UTC-grain stabilt, og der bliver ikke skabt en kunstig ekstra time.

### Konklusion på DST-kontrollen

```text
Sommertidsdøgnet håndteres korrekt.
29. marts 2026 har 23 lokale timer pr. prisområde.
Der er ingen kunstigt oprettet ekstra UTC-time.
Alle eksisterende UTC-timer har 12 femminuttersintervaller.
```

## Kontrol 3 – ufuldstændige timer i januar

Januar-outputtet indeholder:

- **744 unikke UTC-timer**;
- **2 prisområder**;
- **1.488 rækker i alt**.

Der findes præcis **to ufuldstændige rækker**:

| `hour_utc` | `price_area` | `rt_interval_count` | Mangler ift. 12 |
|---|---|---:|---:|
| 2026-01-06 22:00:00+00:00 | DK1 | 9 | 3 |
| 2026-01-06 22:00:00+00:00 | DK2 | 9 | 3 |

De to rækker bevares i outputtet. De slettes ikke, fordi intervaltællingen skal gøre kvalitetsproblemet synligt.

## Kontroller og genkørsel

| Kontrol | Forventning | Observeret resultat | Konsekvens |
|---|---|---|---|
| Primærnøgle/datakontrakt | Obligatoriske felter findes, DK1/DK2 er gyldige, og `(timestamp, PriceArea)` er unik | Valideringen er implementeret i `validate_snapshot()` og stopper på kontraktbrud | Dårligt input fortsætter ikke til aggregation |
| MW→MWh | Hvert 5-minutters MW-interval omregnes med `MW × 5/60` | Implementeret i `mw_to_mwh()` | Realtime-data kan summeres til et sammenligningsgrundlag i MWh |
| Timegrain | Én række pr. `(hour_utc, price_area)` | DST: 142 rækker = 71 timer × 2 områder | Grain er klar til senere one-to-one join |
| Dækning | Komplet time har præcis 12 intervaller | DST: alle 12. Januar: to rækker med 9 | Ufuldstændige timer kan findes uden at slette dem |
| DST | Teknisk UTC må ikke skabe en kunstig ekstra time | 29-03-2026 har 23 lokale timer i både DK1 og DK2 | Sommertid håndteres stabilt med UTC |
| Genkørsel | Samme rådata og kode skal kunne skabe samme mellemoutput igen | `run_pipeline.py --period ... --stage realtime` kan genkøres | Modul02-resultatet er reproducerbart fra rådata |

## Antagelser og fravalg

### 1. Femminuttersværdi som efterfølgende interval

**Regel:** `MW × 5/60`.

**Begrundelse:** Casen kræver en eksplicit metode til at danne energi fra femminutters effektværdier.

**Konsekvens:** Resultatet er et sammenligningsgrundlag og ikke officiel afregning.

### 2. UTC som teknisk tidsnøgle

**Regel:** Aggregation udføres på `hour_utc`.

**Begrundelse:** UTC er stabil hen over skift mellem normal- og sommertid.

**Konsekvens:** Lokal dansk tid kan have 23 eller 25 timer i et døgn uden at den tekniske nøgle bliver tvetydig.

### 3. Storebælt

**Regel:** Storebælt udelades fra udenlandsk udveksling, men indgår i prisområdebalancen.

**Begrundelse:** Forbindelsen er intern mellem DK1 og DK2.

### 4. Strukturelle null-værdier

**Regel:** Null behandles kun som 0, når feltets betydning viser, at forbindelsen ikke findes i det pågældende prisområde.

**Konsekvens:** Vi undgår at gøre almindelige manglende målinger til falske nuller.

## Modul02-checkpoint

- [x] TODO 1 – `validate_snapshot()` er implementeret.
- [x] TODO 2 – `mw_to_mwh()` er implementeret.
- [x] TODO 3 – `prepare_realtime()` er implementeret.
- [x] Dubletter på den sammensatte primærnøgle afvises tydeligt.
- [x] Obligatoriske kolonnebrud afvises tydeligt.
- [x] Femminutters MW omregnes med `MW × 5/60` før timeaggregation.
- [x] Realtime-data aggregeres til én række pr. UTC-time og prisområde.
- [x] Antal femminuttersintervaller bevares i `rt_interval_count`.
- [x] DST-perioden er kørt med `--stage realtime`.
- [x] Januar er kørt med `--stage realtime`.
- [x] DST-kontrollen viser 23 lokale timer den 29. marts 2026 og ingen kunstig ekstra time.
- [x] Ufuldstændige timer er identificeret: DK1 og DK2 kl. 2026-01-06 22:00 UTC har hver 9 intervaller.
- [x] Metodeforbeholdet for MW→MWh er dokumenteret.

## Status efter Modul02

Modul01- og Modul02-checkpoints er dokumenteret. Næste kodearbejde i casen er **Modul03 / TODO 4–6**, men de er ikke en del af denne dokumentation.
