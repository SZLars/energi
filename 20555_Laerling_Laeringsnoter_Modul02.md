# 20555 – Modul02 – Ingestion, kontrakt, enheder og tid

> **Revision:** 1.3 · 21. september 2026  
> **Status:** ARBEJDSDOKUMENT  
> **Rolle:** Delbar forklaring til undervisning, repetition og fravær

## Indhold

1. [A – Transport](#a--transport)
2. [B – Kontrakt](#b--kontrakt)
3. [C – Enheder og tid](#c--enheder-og-tid)
4. [D – Pipeline og Git](#d--pipeline-og-git)

## A – Transport
Et lokalt snapshot er en gemt kildeversion. Ingestion er indlæsningen i vores system; transport beskriver, hvordan data flyttes. HTTP request/response kan hente data ved behov eller polling. REST er en arkitekturstil, ikke et filformat. MQTT er en publish/subscribe-protokol; en eventlog kan bevare hændelser til genafspilning. En broker formidler meddelelser mellem afsendere og modtagere; en processor bearbejder data; en orchestrator styrer, hvornår afhængige trin køres.
Ved netværksindsamling skal man forholde sig til kildeopdatering, fejl, dubletter, adgang og gentagne kald. Offlinearbejdet undgår adgangsafhængigheden, men principperne kan stadig forklares.

## B – Kontrakt
En datakontrakt beskriver forventede felter, typer, identifikatorer/keys og betydning. En manglende eller dubleret key kan gøre en transformation tvetydig og bør give en tydelig fejl. En manglende måleværdi kan i stedet bevares og markeres. Beslutningen afhænger af anvendelsen.
Validering er mere end at programmet ikke kaster en fejl: undersøg forventninger, grænsetilfælde og forretningsregler.

## C – Enheder og tid
I Sensorlab er flow en middelhastighed over ti minutter: liter/minut × minutter = liter. Summering af hastigheder uden tidsinterval giver ikke en mængde. Sensorlabs `complete` kræver seks unikke tidspositioner på ti-minuttersgridet OG seks gyldige flowværdier. Seks rækker er ikke nok, hvis en position er gentaget eller en måling mangler.
I Energinet bruger vi `MW × 5/60` som en eksplicit caseantagelse om det efterfølgende interval, ikke som dokumenteret intervalmiddel eller officiel afregning. Se `DATAORDLISTE.md`.
Gem og gruppér teknisk tid i UTC; konvertér til lokaltid til visning. Et lokalt døgn kan have 23 eller 25 timer ved skift af sommertid. I Energinet er fuld tidsdækning tolv unikke femminuttersintervaller i timen efter casens kontrakt. Tidsdækning er ikke det samme som gyldige måleværdier; vurder manglende værdier og kvalitetsflag særskilt efter `OPGAVE.md` og kodekontrakten. Sensorlabs seks-plus-seks-regel er ikke et ekstra Energinet-krav.

## D – Pipeline og Git
En deklarativ beskrivelse angiver ønskede trin og afhængigheder, eksempelvis plan.json. Den imperative kode beskriver udførelsen. En liste med dependencies udfører ikke sig selv; en runner eller orchestrator skal fortolke den.
Git versionsstyrer kode, konfiguration og dokumentation. Store snapshots skal identificeres med kilde, periode og checksum; secrets må ikke lægges i historikken. Genkørsel med samme input og kode skal kunne genskabe de faglige resultater.

## Selvkontrol og videre arbejde

Realtime-timetabel, ufuldstændige timer og dokumenteret DST-kontrol; genkørsel og fejlstop kan forklares.

Gennemfør `20555_Laerling_Miniopgaver_Modul02.md`, og følg derefter starterprojektets `OPGAVE.md`. Ved fravær: læs én blok, løs den tilhørende aktivitet og forklar resultatet før næste blok. Brug `20555_Laerling_Reference_Python_Pandas.md` ved syntaksproblemer og `20555_Laerling_Kilder.md` til originale kilder. Læringsnoterne supplerer den undervisning, der vises i slides.

## Revisionshistorik

| Revision | Dato | Ændring |
|---|---|---|
| 1.3 | 21. september 2026 | Præciserer arbejdsrute og forklaringer uden nye casekrav. |
| 1.2 | 21. september 2026 | Præciserer case-navigation og/eller fagterminologi efter stateful learner-journey-review; ingen nye krav. |
| 1.1 | 21. september 2026 | QA-001. |
