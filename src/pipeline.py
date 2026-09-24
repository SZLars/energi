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
    """Modul02: implementér den fatale datakontrakt.

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
    """Modul02: beregn MWh som MW × interval_minutes/60.

    Caseantagelse: MW repræsenterer det efterfølgende interval; se DATAORDLISTE.md.
    Resultatet er et tilnærmet sammenligningsgrundlag, ikke officiel afregning.
    """
    if interval_minutes <= 0:
        raise ValueError("interval_minutes skal være større end 0.")
    numeric = pd.to_numeric(values, errors="raise")
    return numeric * (interval_minutes / 60.0)


def prepare_realtime(frame: pd.DataFrame) -> pd.DataFrame:
    """Modul02: skab én realtime-række pr. UTC-time og prisområde.

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
    """Modul03: skab sammenlignelige felter i afregningsdata.

    Outputtet har samme grain som realtime-aggregatet: én UTC-time pr.
    prisområde. Storebælt holdes ude af udenlandsk udveksling, fordi
    forbindelsen flytter energi mellem DK1 og DK2. Strukturelle nulls i
    udenlandske forbindelser behandles som 0, mens øvrige måle-nullværdier
    bevares.
    """
    required = set(SETTLEMENT_REQUIRED_COLUMNS)
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"afregning: mangler kolonner til transformation: {missing}")

    work = frame.copy()
    if not isinstance(work["HourUTC"].dtype, pd.DatetimeTZDtype):
        work["HourUTC"] = pd.to_datetime(work["HourUTC"], errors="raise", utc=True)
    work["HourDK"] = pd.to_datetime(work["HourDK"], errors="raise")

    offshore_columns = [
        "OffshoreWindLt100MW_MWh",
        "OffshoreWindGe100MW_MWh",
    ]
    onshore_columns = [
        "OnshoreWindLt50kW_MWh",
        "OnshoreWindGe50kW_MWh",
    ]
    solar_grid_columns = [
        "SolarPowerLt10kW_MWh",
        "SolarPowerGe10Lt40kW_MWh",
        "SolarPowerGe40kW_MWh",
    ]
    exchange_columns = [
        "ExchangeNO_MWh",
        "ExchangeSE_MWh",
        "ExchangeGE_MWh",
        "ExchangeNL_MWh",
        "ExchangeGB_MWh",
    ]

    offshore = work[offshore_columns].apply(pd.to_numeric, errors="raise")
    onshore = work[onshore_columns].apply(pd.to_numeric, errors="raise")
    solar_grid = work[solar_grid_columns].apply(pd.to_numeric, errors="raise")

    # Null i en forbindelse, der fysisk ikke findes i prisområdet, er
    # strukturel. Storebælt er bevidst ikke med i denne sum.
    exchange = work[exchange_columns].apply(pd.to_numeric, errors="raise").fillna(0.0)

    result = pd.DataFrame({
        "hour_utc": work["HourUTC"],
        "hour_dk": work["HourDK"],
        "price_area": work["PriceArea"],
        "st_offshore_wind_mwh": offshore.sum(
            axis=1, min_count=len(offshore_columns)
        ),
        "st_onshore_wind_mwh": onshore.sum(
            axis=1, min_count=len(onshore_columns)
        ),
        "st_solar_grid_mwh": solar_grid.sum(
            axis=1, min_count=len(solar_grid_columns)
        ),
        "st_external_exchange_mwh": exchange.sum(axis=1),
        "st_gross_consumption_mwh": pd.to_numeric(
            work["GrossConsumptionMWh"], errors="raise"
        ),
    })

    solar_self = pd.to_numeric(work["SolarPowerSelfConMWh"], errors="raise")
    result["st_solar_all_mwh"] = result["st_solar_grid_mwh"] + solar_self

    duplicate = result.duplicated(subset=["hour_utc", "price_area"], keep=False)
    if duplicate.any():
        bad = result.loc[duplicate, ["hour_utc", "price_area"]]
        raise ValueError(
            "afregning: dublet efter transformation på (hour_utc, price_area):\n"
            + bad.to_string(index=False)
        )

    return result.sort_values(["hour_utc", "price_area"]).reset_index(drop=True)


def join_and_flag(realtime: pd.DataFrame, settlement: pd.DataFrame) -> pd.DataFrame:
    """Modul03: outer join kilderne og bevar synlige kvalitetsflag.

    Joinet valideres som one-to-one på ``hour_utc + price_area``. Rækker
    slettes ikke, når der findes problemer; i stedet registreres joinstatus,
    intervaldækning, negative realtime-produktionsværdier og læsbare
    issue-koder.
    """
    join_key = ["hour_utc", "price_area"]

    for label, frame in (("realtime", realtime), ("afregning", settlement)):
        missing = sorted(set(join_key) - set(frame.columns))
        if missing:
            raise ValueError(f"{label}: mangler join-kolonner: {missing}")
        if frame[join_key].isna().any().any():
            raise ValueError(f"{label}: join key indeholder manglende værdier.")
        duplicate = frame.duplicated(subset=join_key, keep=False)
        if duplicate.any():
            bad = frame.loc[duplicate, join_key]
            raise ValueError(
                f"{label}: join key er ikke entydig:\n{bad.to_string(index=False)}"
            )

    result = realtime.merge(
        settlement,
        on=join_key,
        how="outer",
        validate="one_to_one",
        indicator=True,
        sort=True,
    )

    join_status = result["_merge"].map({
        "both": "matched",
        "left_only": "realtime_only",
        "right_only": "settlement_only",
    })
    # map() på en kategorisk merge-indikator kan bevare kategorisk dtype;
    # string gør outputtet enklere at skrive og tælle.
    result["quality_join_status"] = join_status.astype("string")
    result["quality_join_matched"] = result["_merge"].eq("both")

    realtime_present = result["_merge"].ne("right_only")
    result["quality_rt_complete_hour"] = (
        realtime_present
        & result["rt_interval_count"].eq(EXPECTED_INTERVALS_PER_HOUR)
    )
    result["quality_rt_negative_production"] = (
        result["rt_negative_production_intervals"].fillna(0).gt(0)
    )

    # Hvis en række kun findes i realtime, kan dansk lokaltid stadig afledes
    # entydigt fra UTC. Det gør outer-join-rækker lettere at undersøge.
    if "hour_dk" in result.columns:
        missing_hour_dk = result["hour_dk"].isna() & result["hour_utc"].notna()
        if missing_hour_dk.any():
            local_time = (
                result.loc[missing_hour_dk, "hour_utc"]
                .dt.tz_convert("Europe/Copenhagen")
                .dt.tz_localize(None)
            )
            result.loc[missing_hour_dk, "hour_dk"] = local_time

    def issue_codes(row: pd.Series) -> str:
        issues: list[str] = []
        status = row["quality_join_status"]
        if status == "realtime_only":
            issues.append("MISSING_SETTLEMENT")
        elif status == "settlement_only":
            issues.append("MISSING_REALTIME")

        if status != "settlement_only" and not bool(row["quality_rt_complete_hour"]):
            issues.append("RT_INCOMPLETE_HOUR")
        if bool(row["quality_rt_negative_production"]):
            issues.append("RT_NEGATIVE_PRODUCTION")
        return ";".join(issues) if issues else "OK"

    result["quality_issue_codes"] = result.apply(issue_codes, axis=1)

    # Direkte differencer gør de centrale sammenligninger analyseklare.
    comparison_pairs = {
        "diff_offshore_wind_mwh": ("rt_offshore_wind_mwh", "st_offshore_wind_mwh"),
        "diff_onshore_wind_mwh": ("rt_onshore_wind_mwh", "st_onshore_wind_mwh"),
        "diff_solar_grid_mwh": ("rt_solar_mwh", "st_solar_grid_mwh"),
        "diff_solar_all_mwh": ("rt_solar_mwh", "st_solar_all_mwh"),
        "diff_external_exchange_mwh": ("rt_external_exchange_mwh", "st_external_exchange_mwh"),
        "diff_load_mwh": ("rt_load_balance_mwh", "st_gross_consumption_mwh"),
    }
    for output_column, (rt_column, st_column) in comparison_pairs.items():
        result[output_column] = result[rt_column] - result[st_column]

    result = result.drop(columns=["_merge"])
    return result.sort_values(join_key).reset_index(drop=True)


def create_quality_summary(analysis_ready: pd.DataFrame) -> dict:
    """Modul03: lav en maskinlæsbar kvalitetsrapport med tællinger."""
    required = {
        "quality_join_status",
        "quality_join_matched",
        "quality_rt_complete_hour",
        "quality_rt_negative_production",
        "quality_issue_codes",
        "rt_interval_count",
    }
    missing = sorted(required - set(analysis_ready.columns))
    if missing:
        raise ValueError(f"Kvalitetsrapport mangler kolonner: {missing}")

    join_counts = analysis_ready["quality_join_status"].value_counts(dropna=False)
    realtime_present = analysis_ready["quality_join_status"].ne("settlement_only")
    complete = realtime_present & analysis_ready["quality_rt_complete_hour"]
    incomplete = realtime_present & ~analysis_ready["quality_rt_complete_hour"]

    issue_count: dict[str, int] = {}
    for value in analysis_ready["quality_issue_codes"].fillna(""):
        for code in str(value).split(";"):
            code = code.strip()
            if not code or code == "OK":
                continue
            issue_count[code] = issue_count.get(code, 0) + 1

    return {
        "total_rows": int(len(analysis_ready)),
        "join_status_counts": {
            "matched": int(join_counts.get("matched", 0)),
            "realtime_only": int(join_counts.get("realtime_only", 0)),
            "settlement_only": int(join_counts.get("settlement_only", 0)),
        },
        "realtime_hours": {
            "complete": int(complete.sum()),
            "incomplete": int(incomplete.sum()),
            "missing_from_realtime": int((~realtime_present).sum()),
            "expected_intervals_per_hour": int(EXPECTED_INTERVALS_PER_HOUR),
        },
        "quality_flag_counts": {
            "join_unmatched": int((~analysis_ready["quality_join_matched"]).sum()),
            "rt_incomplete_hour": int(incomplete.sum()),
            "rt_negative_production": int(
                analysis_ready["quality_rt_negative_production"].sum()
            ),
        },
        "issue_code_counts": dict(sorted(issue_count.items())),
    }


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
