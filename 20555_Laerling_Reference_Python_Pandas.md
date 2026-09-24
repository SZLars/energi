# 20555 – Python/pandas-reference

> **Revision:** 1.1 · 21. september 2026  
> **Status:** ARBEJDSDOKUMENT

## Indhold

1. [Python-indgang](#python-indgang)
2. [Tabelarbejde](#tabelarbejde)
3. [Fejlfinding](#fejlfinding)

## Python-indgang

Funktioner skrives med `def`; indrykning afgrænser blokke. `return` afleverer en værdi. En liste har rækkefølge, og en `dict`/dictionary består af key/value-par. `None` betyder ingen værdi. Importér biblioteker én gang øverst og læs en traceback fra fejltype tilbage til din egen kode.

```python
def difference(measured, reference):
    return measured - reference

record = {"device": "A", "value": 10}
print(difference(record["value"], 8))
```

Installation og kørsel skal bruge samme Python-miljø: `python -m pip --version` og `python --version`. Ingen generel omskrivning af hele projektet er nødvendig for en importfejl.

## Tabelarbejde

Illustrative mønstre; vælg selv de rigtige felter i hovedcasen.

| Kendt idé | pandas-mønster |
|---|---|
| SELECT kolonner | `df[["device", "value"]]` |
| WHERE | `df.loc[df["value"] > 0]` |
| Afledt kolonne | `df["double"] = df["value"] * 2` |
| GROUP BY | `df.groupby("device")["value"].sum(min_count=1)` |
| Nullkontrol | `df["value"].isna()` |
| Dubletkontrol | `df.duplicated(["time", "device"])` |
| Datatype | `pd.to_numeric(df["value"], errors="raise")` |
| UTC-tid | `pd.to_datetime(df["time"], utc=True, errors="raise")` |
| Timebucket | `df["time"].dt.floor("h")` |
| Outer join | `left.merge(right, on=["time", "device"], how="outer", validate="one_to_one", indicator=True)` |
| CSV-output | `df.to_csv("result.csv", index=False)` |

Afvis manglende værdier i join keys før sammenkobling. `size` og `count` er ikke samme kontrol. `sum(min_count=1)` undgår at en gruppe med kun manglende værdier automatisk bliver til nul. Tjek dtypes efter læsning og efter join. Et DataFrame-indeks er ikke automatisk en business key eller primærnøgle i dine data.

## Fejlfinding

1. Vis `shape`, `columns`, `dtypes` og et lille udsnit.
2. Kontroller én forventet række i hånden.
3. Find første trin, hvor resultatet afviger.
4. Skeln manglende fil, forkert kolonne, forkert type og forkert betydning.
5. Genkør efter ændringen og kontroller både normal- og fejltilfældet.

Brug `20555_Laerling_Kilder.md` til dokumentationen og `demo_read.py` som første kørbare eksempel.

## Revisionshistorik

| Revision | Dato | Ændring |
|---|---|---|
| 1.1 | 21. september 2026 | Præciserer case-navigation og/eller fagterminologi efter stateful learner-journey-review; ingen nye krav. |
| 1.0 | 20. september 2026 | Første version. |
