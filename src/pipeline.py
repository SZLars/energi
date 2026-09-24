from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from contracts import (
    EXPECTED_INTERVALS_PER_HOUR,
    EXPECTED_PRICE_AREAS,
    MINIMUM_ANALYSIS_COLUMNS,
    PERIODS,
    REALTIME_REQUIRED_COLUMNS,
    SETTLEMENT_REQUIRED_COLUMNS,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_DIR = PROJECT_ROOT / "output"


class NextTodo(NotImplementedError):
    """Markér et endnu ikke implementeret trin uden at styre modulrækkefølgen."""


def load_records(path: Path, expected_dataset: str) -> pd.DataFrame:
    """Indlæser records og udfører de første kontroller af JSON-konvolutten."""
    if not path.exists():
        raise FileNotFoundError(f"Råfilen findes ikke: {path}")
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if payload.get("dataset") != expected_dataset:
        raise ValueError(
            f"{path.name} angiver {payload.get('dataset')!r}; "
            f"forventede {expected_dataset!r}."
        )
    records = payload.get("records")
    if not isinstance(records, list):
        raise ValueError(f"{path.name} mangler en liste med records.")
    if payload.get("total") is not None and int(payload["total"]) != len(records):
        raise ValueError(f"{path.name}: total matcher ikke antallet af records.")
    return pd.DataFrame(records)


def validate_snapshot(
    frame: pd.DataFrame,
    required_columns: list[str],
    timestamp_column: str,
    label: str,
) -> pd.DataFrame:
    """TODO 1: Implementér den fatale datakontrakt.

    Minimum:
    - kontrollér obligatoriske kolonner;
    - konvertér timestampkolonnen og fejl tydeligt på ugyldige værdier;
    - kontrollér DK1/DK2;
    - kontrollér dubletter på den sammensatte primærnøgle: timestamp + PriceArea;
    - returnér en kopi med den konverterede timestampkolonne.
    """
    missing = sorted(set(required_columns) - set(frame.columns))
    if missing:
        raise ValueError(f"{label}: mangler obligatoriske kolonner: {missing}")

    result = frame.copy()

    try:
        result[timestamp_column] = pd.to_datetime(
            result[timestamp_column],
            errors="raise",
            utc=True,
        )
    except (ValueError, TypeError) as exc:
        raise ValueError(
            f"{label}: ugyldig timestamp i {timestamp_column}."
        ) from exc

    if result[timestamp_column].isna().any():
        raise ValueError(f"{label}: {timestamp_column} indeholder manglende timestamps.")

    if "PriceArea" not in result.columns:
        raise ValueError(f"{label}: PriceArea mangler.")

    invalid_area = result["PriceArea"].isna() | ~result["PriceArea"].isin(EXPECTED_PRICE_AREAS)
    if invalid_area.any():
        values = sorted(result.loc[invalid_area, "PriceArea"].astype(str).unique().tolist())
        raise ValueError(
            f"{label}: uventede PriceArea-værdier: {values}; "
            f"forventede {sorted(EXPECTED_PRICE_AREAS)}."
        )

    duplicate = result.duplicated(
        subset=[timestamp_column, "PriceArea"],
        keep=False,
    )
    if duplicate.any():
        bad = result.loc[duplicate, [timestamp_column, "PriceArea"]]
        raise ValueError(
            f"{label}: dublet på sammensat primærnøgle "
            f"({timestamp_column}, PriceArea):\n{bad.to_string(index=False)}"
        )

    return result


def mw_to_mwh(values: pd.Series, interval_minutes: int = 5) -> pd.Series:
    """TODO 2: Beregn MWh som MW × interval_minutes/60.

    Caseantagelse: MW repræsenterer det efterfølgende interval; se DATAORDLISTE.md.
    Resultatet er et tilnærmet sammenligningsgrundlag, ikke officiel afregning.
    """
    if interval_minutes <= 0:
        raise ValueError("interval_minutes skal være større end 0.")
    numeric = pd.to_numeric(values, errors="raise")
    return numeric * (interval_minutes / 60.0)


def prepare_realtime(frame: pd.DataFrame) -> pd.DataFrame:
    """TODO 3: Skab én realtime-række pr. UTC-time og prisområde.

    Outputtet skal mindst indeholde:
    - hour_utc, price_area og rt_interval_count;
    - offshore, onshore og sol i MWh;
    - udenlandsk udveksling uden Storebælt;
    - en prisområdebalance, hvor Storebælt er med;
    - antal negative produktionsintervaller.

    Husk at omregne hvert interval før summering.
    """
    required = set(REALTIME_REQUIRED_COLUMNS)
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"realtime: mangler kolonner til aggregation: {missing}")

    work = frame.copy()
    if not isinstance(work["Minutes5UTC"].dtype, pd.DatetimeTZDtype):
        work["Minutes5UTC"] = pd.to_datetime(
            work["Minutes5UTC"], errors="raise", utc=True
        )

    # De tre produktionstyper, der sammenlignes direkte med afregningsdata.
    work["_offshore_mwh"] = mw_to_mwh(work["OffshoreWindPower"])
    work["_onshore_mwh"] = mw_to_mwh(work["OnshoreWindPower"])
    work["_solar_mwh"] = mw_to_mwh(work["SolarPower"])

    # Null i en fysisk ikke-eksisterende udvekslingsforbindelse er strukturel.
    # Derfor behandles null som 0 kun i disse udvekslingskolonner.
    exchange_columns = [
        "ExchangeGermany",
        "ExchangeNetherlands",
        "ExchangeGreatBritain",
        "ExchangeNorway",
        "ExchangeSweden",
    ]
    exchange_mw = work[exchange_columns].apply(pd.to_numeric, errors="raise").fillna(0.0)
    work["_external_exchange_mwh"] = mw_to_mwh(exchange_mw.sum(axis=1))

    # Prisområdebalancen inkluderer Storebælt, fordi forbindelsen flytter energi
    # mellem DK1 og DK2. BornholmSE4 lægges ikke til separat, da metadata siger,
    # at den allerede indgår i ExchangeSweden.
    production_columns = [
        "ProductionLt100MW",
        "ProductionGe100MW",
        "OffshoreWindPower",
        "OnshoreWindPower",
        "SolarPower",
    ]
    production_mw = work[production_columns].apply(pd.to_numeric, errors="raise")
    production_total_mw = production_mw.sum(axis=1, min_count=len(production_columns))
    great_belt_mw = pd.to_numeric(work["ExchangeGreatBelt"], errors="raise")
    work["_load_balance_mwh"] = mw_to_mwh(
        production_total_mw + exchange_mw.sum(axis=1) + great_belt_mw
    )

    # Antal femminuttersrækker, hvor mindst én produktionsværdi er negativ.
    work["_negative_production_interval"] = production_mw.lt(0).any(axis=1).astype(int)
    work["hour_utc"] = work["Minutes5UTC"].dt.floor("h")
    work["price_area"] = work["PriceArea"]

    grouped = work.groupby(["hour_utc", "price_area"], as_index=False, sort=True)

    totals = grouped[[
        "_offshore_mwh",
        "_onshore_mwh",
        "_solar_mwh",
        "_external_exchange_mwh",
        "_load_balance_mwh",
        "_negative_production_interval",
    ]].sum(min_count=1)

    counts = grouped.size().rename(columns={"size": "rt_interval_count"})
    result = totals.merge(counts, on=["hour_utc", "price_area"], validate="1:1")

    result = result.rename(columns={
        "_offshore_mwh": "rt_offshore_wind_mwh",
        "_onshore_mwh": "rt_onshore_wind_mwh",
        "_solar_mwh": "rt_solar_mwh",
        "_external_exchange_mwh": "rt_external_exchange_mwh",
        "_load_balance_mwh": "rt_load_balance_mwh",
        "_negative_production_interval": "rt_negative_production_intervals",
    })

    return result[[
        "hour_utc",
        "price_area",
        "rt_interval_count",
        "rt_offshore_wind_mwh",
        "rt_onshore_wind_mwh",
        "rt_solar_mwh",
        "rt_external_exchange_mwh",
        "rt_load_balance_mwh",
        "rt_negative_production_intervals",
    ]]


def prepare_settlement(frame: pd.DataFrame) -> pd.DataFrame:
    """TODO 4: Skab sammenligningsfelter i afregningsdata.

    Outputtet skal mindst indeholde:
    - hour_utc, hour_dk og price_area;
    - samlet offshore og onshore;
    - sol både uden og med self-consumption;
    - udenlandsk udveksling uden Storebælt;
    - gross consumption.
    """
    raise NextTodo("TODO 4 er ikke implementeret: prepare_settlement() Følg det aktuelle modul i OPGAVE.md.")


def join_and_flag(realtime: pd.DataFrame, settlement: pd.DataFrame) -> pd.DataFrame:
    """TODO 5: Udfør outer join og tilføj kvalitetsflag.

    Brug hour_utc + price_area som join key, og validér én-til-én-kardinalitet.
    Bevar mindst flag for joinstatus og præcis 12 realtime-intervaller.
    Tilføj gerne negative værdier, frosne tilstande og metadataadvarsler.
    """
    raise NextTodo("TODO 5 er ikke implementeret: join_and_flag() Følg det aktuelle modul i OPGAVE.md.")


def create_quality_summary(analysis_ready: pd.DataFrame) -> dict:
    """TODO 6: Lav en lille maskinlæsbar rapport med tællinger.

    Medtag mindst samlet rækkeantal, joinstatus, fulde/ufuldstændige timer
    og antal rækker med hvert kvalitetsflag.
    """
    raise NextTodo("TODO 6 er ikke implementeret: create_quality_summary() Følg det aktuelle modul i OPGAVE.md.")


def write_outputs(
    period: str,
    analysis_ready: pd.DataFrame,
    quality_summary: dict,
) -> tuple[Path, Path]:
    missing = sorted(set(MINIMUM_ANALYSIS_COLUMNS) - set(analysis_ready.columns))
    if missing:
        raise ValueError(f"Analyseoutputtet mangler obligatoriske kolonner: {missing}")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = OUTPUT_DIR / f"analysis_ready_{period}.csv"
    quality_path = OUTPUT_DIR / f"quality_{period}.json"
    analysis_ready.to_csv(csv_path, index=False)
    with quality_path.open("w", encoding="utf-8") as handle:
        json.dump(quality_summary, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    return csv_path, quality_path


def build_realtime_period(period: str) -> tuple[pd.DataFrame, Path]:
    """Kør kun det færdige Modul02-spor og gem mellemoutput."""
    if period not in PERIODS:
        raise ValueError(f"Ukendt periode: {period}")
    realtime_name, _ = PERIODS[period]
    realtime_raw = load_records(
        RAW_DIR / realtime_name, "ElectricityProdex5MinRealtime"
    )
    realtime_valid = validate_snapshot(
        realtime_raw,
        REALTIME_REQUIRED_COLUMNS,
        "Minutes5UTC",
        "realtime",
    )
    realtime_hourly = prepare_realtime(realtime_valid)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / f"realtime_hourly_{period}.csv"
    realtime_hourly.to_csv(path, index=False)
    return realtime_hourly, path


def run_period(period: str) -> tuple[Path, Path]:
    realtime_hourly, _ = build_realtime_period(period)
    _, settlement_name = PERIODS[period]
    settlement_raw = load_records(
        RAW_DIR / settlement_name, "ProductionConsumptionSettlement"
    )
    settlement_valid = validate_snapshot(
        settlement_raw,
        SETTLEMENT_REQUIRED_COLUMNS,
        "HourUTC",
        "afregning",
    )
    settlement_hourly = prepare_settlement(settlement_valid)
    analysis_ready = join_and_flag(realtime_hourly, settlement_hourly)
    quality_summary = create_quality_summary(analysis_ready)
    return write_outputs(period, analysis_ready, quality_summary)
