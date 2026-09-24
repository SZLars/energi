# 20555 – Ingestion, kontrakt, enheder og tid – miniopgaver

> **Revision:** 1.2 · 21. september 2026  
> **Status:** ARBEJDSDOKUMENT  
> **Eksempeldata:** Konstrueret Sensorlab; Energinet er den separate hovedcase

## Indhold

1. [M02.1 – Flyt data](#aktivitet-1)
2. [M02.2 – Kontraktbrud](#aktivitet-2)
3. [M02.3 – Mængde og dækning](#aktivitet-3)
4. [M02.4 – Beskrivelse og versionsspor](#aktivitet-4)

Tiderne er planlægningsestimater. Arbejd i din egen Sensorlab-kopi. Gem korte svar som arbejdsnoter; hovedcasens afleveringskrav ejes af starterprojektets `OPGAVE.md`.

<a id="aktivitet-1"></a>
## M02.1 – Flyt data

**Arbejdsform:** Par, 15 minutter.

Tegn to Sensorlab-flow: periodisk HTTPS-hentning og publicering gennem en broker. Markér producer, transport, raw, processor og planlægning. Forklar en fejl og et genforsøg i hvert flow.

**Forventet output:** To små diagrammer med ansvar og dubletrisiko.

**Opsamling:** Sammenlign fremgangsmåde og begrundelse med en makker og derefter holdet. Underviseren viser svarankre efter arbejdet.

<a id="aktivitet-2"></a>
## M02.2 – Kontraktbrud

**Arbejdsform:** Individuelt, 25 minutter.

Implementér validate i exercises.py. Afprøv en kopi med dubletrække, en ugyldig timestamp og en manglende flowværdi. Begrund forskellen på fejlstop og bevaret kvalitetsproblem.

**Forventet output:** Kode og tre dokumenterede resultater.

**Opsamling:** Sammenlign fremgangsmåde og begrundelse med en makker og derefter holdet. Underviseren viser svarankre efter arbejdet.

<a id="aktivitet-3"></a>
## M02.3 – Mængde og dækning

**Arbejdsform:** Individuelt, 40 minutter.

Implementér aggregate. Kontroller først en enkelt måling i hånden. Beregn både antal rækker og antal gyldige værdier; markér complete. Forklar hvorfor alle-null ikke må give nul. Brug derefter pandas.date_range til UTC-timer mellem 2026-03-28T23:00Z og 2026-03-29T22:00Z, slut eksklusiv, og vis dem i Europe/Copenhagen.

**Forventet output:** Tabel for A/B samt kontrol af lokalt sommertidsdøgn.

**Opsamling:** Sammenlign fremgangsmåde og begrundelse med en makker og derefter holdet. Underviseren viser svarankre efter arbejdet.

<a id="aktivitet-4"></a>
## M02.4 – Beskrivelse og versionsspor

**Arbejdsform:** Par, 20 minutter.

Læs plan.json. Tegn dependencies og forklar, hvilket trin der ikke må starte ved valideringsfejl. Lav i din egen Sensorlab-kopi et Git-commit af kode/plan, ændr én begrundet regel og vis diff. Ingen credentials eller rådatasletning.

**Forventet output:** Dependency-skitse og et forklaret versionsspor.

**Opsamling:** Sammenlign fremgangsmåde og begrundelse med en makker og derefter holdet. Underviseren viser svarankre efter arbejdet.

## Videre til casen

Starterprojektets `OPGAVE.md`, Modul02 og `pipeline.py` TODO 1–3. Verificér de givne primærnøgler, join keys, intervaller og outputfelter mod metadata og kontrakten. Implementér selv transformationerne, kontrollér dækning og DST, og begrund resultater og metodeforbehold. Undersøgelsesspørgsmål, analysescope og supplerende kontroller er dine valg inden for starterprojektets `OPGAVE.md`.

## Revisionshistorik

| Revision | Dato | Ændring |
|---|---|---|
| 1.2 | 21. september 2026 | Præciserer case-navigation og/eller fagterminologi efter stateful learner-journey-review; ingen nye krav. |
| 1.1 | 21. september 2026 | QA-006. |
