# Kilder og pipeline – Modul01

## Kilder

| Kilde og snapshot | Formål | Grain / primærnøgle | Enhed / tid | Kendte begrænsninger |
|---|---|---|---|---|
| Realtime – `realtime_2026-01.json` / `ElectricityProdex5MinRealtime` | Hurtige operationelle data om produktion og eludveksling | Én værdi ved et 5-minutters tidspunkt i ét prisområde. Sammensat primærnøgle: `(Minutes5UTC, PriceArea)` | Primært effekt i MW. `Minutes5UTC` er teknisk UTC-tid, `Minutes5DK` er dansk lokaltid. Prisområder i casen: DK1 og DK2. | Data bygger på opskalerede realtime/SCADA-målinger. Fejl kan forekomme og bliver generelt ikke rettet. Metadata advarer også om kendte fejl omkring DST 29. marts 2026 og `ProductionLt100MW` 30. marts 2026. Nogle udvekslingsfelter er strukturelt null i et prisområde. |
| Afregning – `settlement_2026-01.json` / `ProductionConsumptionSettlement` | Senere afregnings- og statistikdata til sammenligning med realtime | Én time i ét prisområde. Sammensat primærnøgle: `(HourUTC, PriceArea)` | Energi i MWh. `HourUTC` er UTC-time, `HourDK` er dansk lokaltid. Prisområder: DK1 og DK2. | Data kommer med ca. 9–15 dages forsinkelse og kan efteropdateres. Metadata beskriver historiske ændringer i felter og at nogle null/0-værdier kræver fortolkning. |

## Observation af de to snapshots

### Realtime – januar

- Fil: `data/raw/realtime_2026-01.json`
- Antal rækker: **17.850**
- Prisområder: **DK1, DK2**
- Tidskolonner: `Minutes5UTC`, `Minutes5DK`
- Primærnøgle: `(Minutes5UTC, PriceArea)`
- Ingen dubletter fundet på denne nøgle i snapshot'et.
- Eksempel på målefelter: `OffshoreWindPower`, `OnshoreWindPower`, `SolarPower`, `ExchangeGermany`, `ExchangeGreatBelt`.
- Flere forbindelseskolonner indeholder null-værdier, fordi ikke alle forbindelser findes i begge prisområder.

### Afregning – januar

- Fil: `data/raw/settlement_2026-01.json`
- Antal rækker: **1.488**
- Prisområder: **DK1, DK2**
- Tidskolonner: `HourUTC`, `HourDK`
- Primærnøgle: `(HourUTC, PriceArea)`
- Ingen dubletter fundet på denne nøgle i snapshot'et.
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

### Dependencies og fejlstop

Hvis indlæsning eller validering fejler, må senere transformationer ikke fortsætte. Realtime-data skal først omregnes og aggregeres, før de kan sammenlignes med afregningsdata, fordi de to kilder ellers ikke har samme grain eller enhed.

## Metadata og forventede problemer

### Realtime

Metadata beskriver realtime-kilden som femminutters produktions- og udvekslingsdata. Data er baseret på opskalerede realtime-målinger fra SCADA-systemet. Metadata siger direkte, at fejl kan forekomme og normalt ikke bliver rettet.

Vigtige forhold:

- opløsning: 5 minutter;
- primærnøgle: `(Minutes5UTC, PriceArea)`;
- teknisk tid bør håndteres i UTC;
- DST kan skabe problemer ved fortolkning af dansk lokaltid;
- kendte fejl findes i DST-perioden;
- strukturelle null-værdier må ikke automatisk behandles som ukendte målinger;
- Storebælt er intern udveksling mellem DK1 og DK2 og skal derfor behandles anderledes end udenlandsk udveksling.

### Afregning

Afregningsdata er timebaserede og kommer senere end realtime-data. Metadata oplyser, at data normalt er ca. 99 % korrekte efter 15 dage og gradvist forbedres. Historiske værdier kan blive opdateret.

Vigtige forhold:

- opløsning: 1 time;
- primærnøgle: `(HourUTC, PriceArea)`;
- hovedenheden er MWh;
- data kan blive revideret;
- nogle historiske 0/null-værdier kræver domænefortolkning;
- felter med lignende navne i realtime og afregning er ikke nødvendigvis defineret identisk.

## Tre foreløbige undersøgelsesspørgsmål

Jeg vælger foreløbigt disse tre fra spørgsmålsbanken:

1. **Er realtime-data lige anvendelige i vinter og sommer?**
2. **Er forskellen mellem realtime og afregning den samme i DK1 og DK2?**
3. **Hvad sker der med analysen, hvis ufuldstændige timer behandles som normale timer?**

De tre spørgsmål giver mulighed for at undersøge både periodeforskelle, prisområder og betydningen af datakvalitet.

## Modul01-checkpoint

- [x] `check_setup.py` giver `SETUP PASS`.
- [x] Ét realtime-snapshot er undersøgt.
- [x] Ét afregningssnapshot er undersøgt.
- [x] Grain, primærnøgler, tid, enheder og prisområder er identificeret.
- [x] Senere join key er identificeret som `(hour_utc, price_area)`.
- [x] Metadata og centrale advarsler er gennemgået.
- [x] Pipeline fra raw til analyseklart output er skitseret.
- [x] Tre foreløbige undersøgelsesspørgsmål er valgt.
