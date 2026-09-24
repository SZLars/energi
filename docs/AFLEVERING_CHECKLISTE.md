# Afleveringscheckliste – Energinet-casen

Brug denne som sidste kontrol før aflevering.

## Modul01

- [x] `check_setup.py` giver `SETUP PASS`
- [x] Kilde- og grainskema
- [x] Primærnøgler, tid, enheder og prisområder
- [x] Pipeline-skitse
- [x] Tre spørgsmål valgt

## Modul02

- [x] TODO 1–3 implementeret
- [x] MW → MWh dokumenteret
- [x] UTC-timeaggregation
- [x] Intervaltælling
- [x] DST-kontrol
- [x] Ufuldstændige januar-timer dokumenteret
- [x] Realtime-mellemoutput

## Modul03

- [x] TODO 4–6 implementeret
- [x] Afregningsfelter gjort sammenlignelige
- [x] One-to-one outer join
- [x] Kvalitetsflag
- [x] Storebælt-logik
- [x] Analyseoutput for januar, juni og DST
- [x] Kvalitetsrapport for januar, juni og DST

## Modul04

- [x] Spørgsmål 1 besvaret
- [x] Spørgsmål 3 besvaret
- [x] Spørgsmål 5 besvaret
- [x] Mindst to perioder/prisområder sammenlignet
- [x] Samlede mål og konkrete timer brugt som evidens
- [x] Big Data-vurdering
- [x] Platform-, ansvar- og sikkerhedsvurdering

## Modul05

- [x] Pipeline kan genkøres fra rådata
- [x] README/driftsvejledning findes
- [x] Antagelser og begrænsninger dokumenteret
- [x] Demonstrationsrute for transformation og kvalitetsfund forberedt
- [ ] Udfyld personligt hvad du selv har lavet, og hvilken hjælp du har fået
- [ ] Gennemfør den faktiske individuelle demonstration/præsentation efter underviserens krav

## Kommandoer til sidste kontrol

Fra `energi`:

```powershell
python check_setup.py
python -m pytest

Remove-Item .\output\* -Force
python run_pipeline.py --period dst --stage all
python run_pipeline.py --period january --stage all
python run_pipeline.py --period june --stage all

Get-ChildItem .\output\
```

Forventede centrale filer:

```text
analysis_ready_dst.csv
analysis_ready_january.csv
analysis_ready_june.csv

quality_dst.json
quality_january.json
quality_june.json
```

> Bemærk: `Remove-Item .\output\* -Force` fjerner også `.gitkeep`, hvis PowerShell inkluderer skjulte filer via en anden kommando. Det påvirker ikke selve pipeline-testen, men `.gitkeep` kan genskabes bagefter hvis ønsket.
